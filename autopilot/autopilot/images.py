"""Free banner image chain: HuggingFace (free token) -> Pollinations (no key) -> Pillow (offline)."""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70].strip("-") or "post"


def banner_prompt(title: str, tags: list) -> str:
    # Specific, minimalist, and explicit "no text": garbled AI lettering is the
    # #1 source of nonsense-banner blends, so forbid text outright.
    kw = ", ".join(tags[:3])
    return (f"minimalist flat vector banner illustration about {title} ({kw}), "
            f"simple geometric shapes, dark navy background with teal and indigo gradients, "
            f"clean tech aesthetic, generous empty space, absolutely no text, no letters, "
            f"no words, no watermark, no logo, wide 1200x630 composition")


def huggingface_banner(prompt: str, out: Path, token: str, model: str,
                       w=1200, h=630, timeout=180) -> bool:
    """Hugging Face Inference Providers text-to-image (free tier, needs free HF_TOKEN).

    One-time setup for the token owner: create a free token at
    huggingface.co/settings/tokens and open the model page once to accept
    its license if gated. Returns False on ANY failure (caller falls through).
    """
    try:
        import urllib.error
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        payload = {"inputs": prompt[:600],
                   "parameters": {"width": w, "height": h, "num_inference_steps": 8}}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "gtec-autopilot/1.0",
            "Accept": "image/png",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            body = r.read()
        if "image" not in ctype or len(body) < 20_000:
            print(f"[img:huggingface] rejected ({ctype[:60]}), trying next...", flush=True)
            return False
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        return True
    except Exception as e:
        try:
            detail = ""
            if isinstance(e, urllib.error.HTTPError):
                detail = e.read().decode("utf-8", "replace")[:200]
            print(f"[img:huggingface] FAILED: {type(e).__name__}: {str(e)[:120]} {detail[:120]}",
                  flush=True)
        except Exception:
            pass
        return False


def pollinations_banner(prompt: str, out: Path, model="flux", w=1200, h=630, timeout=120) -> bool:
    try:
        q = urllib.parse.quote(prompt[:400])
        url = f"https://image.pollinations.ai/prompt/{q}?model={model}&width={w}&height={h}&nologo=true&seed=7"
        req = urllib.request.Request(url, headers={"User-Agent": "gtec-autopilot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        if len(data) < 20_000:  # probably an error payload, not an image
            return False
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        return True
    except Exception:
        return False


def pillow_banner(title: str, out: Path, w=1200, h=630) -> Path:
    """Always-works offline banner: dark gradient + title + site tag."""
    from PIL import Image, ImageDraw, ImageFont
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (w, h), (13, 17, 23))
    px = img.load()
    for y in range(h):
        f = y / h
        r, g, b = int(13 + 40 * f), int(17 + 60 * f), int(23 + 90 * f)
        for x in range(w):
            ff = x / w * 0.15
            px[x, y] = (min(255, int(r + 60 * ff)), min(255, int(g + 80 * ff)), min(255, int(b + 110 * ff)))
    d = ImageDraw.Draw(img)
    d.rectangle([30, 30, w - 30, h - 30], outline=(88, 101, 242), width=4)
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 36)
    except Exception:
        font_big = font_small = ImageFont.load_default()
    words, lines, cur = title.split(), [], ""
    for wd in words:
        if len(cur + " " + wd) > 28:
            lines.append(cur.strip())
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur.strip())
    lines = lines[:3]
    y = h // 2 - len(lines) * 45
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=font_big)
        d.text(((w - (bb[2] - bb[0])) / 2, y), ln, font=font_big, fill=(255, 255, 255))
        y += 85
    tag = "gtec0.github.io  •  Code easier!"
    bb = d.textbbox((0, 0), tag, font=font_small)
    d.text(((w - (bb[2] - bb[0])) / 2, h - 120), tag, font=font_small, fill=(150, 180, 255))
    img.save(out)
    return out


def make_images(cfg: dict, title: str, tags: list, banners_dir: Path) -> dict:
    """Returns {banner_rel, banner_abs, provider}. Never raises — Pillow always works."""
    slug = slugify(title)
    banner_name = f"{slug}-banner.png"
    banner_abs = banners_dir / banner_name
    # normalize to repo-root style: /assets/images/banners/xxx.png
    banner_rel = f"/{cfg['blog'].get('banners_dir', 'assets/images/banners')}/{banner_name}"
    w, h = cfg["images"]["banner_width"], cfg["images"]["banner_height"]
    prompt = banner_prompt(title, tags)
    env = cfg["_env"]

    if not env.get("no_ai_images"):
        if env.get("hf_token"):
            if huggingface_banner(prompt, banner_abs, env["hf_token"],
                                  cfg["images"].get("hf_model", "black-forest-labs/FLUX.1-schnell"),
                                  w=w, h=h):
                return {"banner_rel": banner_rel, "banner_abs": banner_abs, "provider": "huggingface"}
            print("[img] huggingface failed, falling back to Pollinations...", flush=True)
        else:
            print("[img] no HF_TOKEN — skipping HuggingFace, trying Pollinations...", flush=True)
        if pollinations_banner(prompt, banner_abs, model=cfg["images"].get("pollinations_model", "flux"), w=w, h=h):
            return {"banner_rel": banner_rel, "banner_abs": banner_abs, "provider": "pollinations"}
        print("[img] Pollinations failed, using offline Pillow banner.", flush=True)
    pillow_banner(title, banner_abs, w=w, h=h)
    return {"banner_rel": banner_rel, "banner_abs": banner_abs, "provider": "pillow"}
