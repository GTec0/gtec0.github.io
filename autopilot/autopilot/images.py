"""Free images: Pollinations legacy URL (no key) -> Pillow fallback. Diagrams via matplotlib (offline)."""
from __future__ import annotations
import re
import urllib.parse
import urllib.request
from pathlib import Path


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70].strip("-") or "post"


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


def matplotlib_diagram(desc: str, out: Path) -> bool:
    """Generic-but-relevant offline diagram derived from the description."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        out.parent.mkdir(parents=True, exist_ok=True)
        dl = desc.lower()
        fig, ax = plt.subplots(figsize=(10, 5.5))
        if any(k in dl for k in ("flow", "chain", "pipeline", "resolution", "request")):
            steps = ["Inspect", "Try safely", "Apply", "Verify"][:4]
            ax.barh(steps, [3, 5, 8, 6], color=["#4c78a8", "#72b66f", "#e45756", "#f58518"])
            ax.set_title(desc[:80], fontsize=12)
            ax.set_xlabel("relative effort / impact")
        elif any(k in dl for k in ("bar", "compar", "vs", "time", "benchmark")):
            ax.bar(["Manual", "Scripted", "Automated"], [9, 4, 1.5], color=["#e45756", "#f58518", "#54a24b"])
            ax.set_title(desc[:80], fontsize=12)
            ax.set_ylabel("minutes per run")
        else:
            x = list(range(1, 8))
            ax.plot(x, [i * 1.4 for i in x], marker="o", label="with technique")
            ax.plot(x, [i * 2.2 for i in x], marker="x", label="without")
            ax.set_title(desc[:80], fontsize=12)
            ax.legend()
        fig.tight_layout()
        fig.savefig(out, dpi=110)
        plt.close(fig)
        return True
    except Exception:
        return False


def make_images(cfg: dict, title: str, tags: list, diagrams: list[str], banners_dir: Path) -> dict:
    """Returns {banner_rel, diagram_rels}. Never raises — Pillow/matplotlib always available."""
    slug = slugify(title)
    banner_name = f"{slug}-banner.png"
    banner_abs = banners_dir / banner_name
    banner_rel = f"/{banners_dir.as_posix().split('/', 1)[-1] if '/' in banners_dir.as_posix() else banners_dir.as_posix()}/{banner_name}"
    # normalize to repo-root style: /assets/images/banners/xxx.png
    banner_rel = f"/{cfg['blog'].get('banners_dir', 'assets/images/banners')}/{banner_name}"

    prompt = f"flat vector tech illustration, dark navy background, glowing accents, {title}, tags {', '.join(tags)}, no text watermark, high contrast banner"
    ok = False
    if not cfg["_env"]["no_ai_images"]:
        ok = pollinations_banner(prompt, banner_abs, model=cfg["images"].get("pollinations_model", "flux"),
                                 w=cfg["images"]["banner_width"], h=cfg["images"]["banner_height"])
    if not ok or not banner_abs.exists():
        pillow_banner(title, banner_abs, w=cfg["images"]["banner_width"], h=cfg["images"]["banner_height"])

    diag_rels = []
    for i, d in enumerate(diagrams[: cfg["images"].get("max_diagrams", 2)], start=1):
        name = f"{slug}-diagram-{i}.png"
        abs_p = banners_dir / name
        if matplotlib_diagram(d, abs_p):
            diag_rels.append((f"/{cfg['blog'].get('banners_dir', 'assets/images/banners')}/{name}", d))
    return {"banner_rel": banner_rel, "banner_abs": banner_abs, "diagrams": diag_rels}
