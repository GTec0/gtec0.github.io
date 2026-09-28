"""Platform-tailored captions with link + hashtags. All free, no AI needed."""
from __future__ import annotations


def _tags(tags: list[str], extra: list[str], n=6) -> str:
    base = [f"#{t.lower().replace(' ', '').replace('.', '').replace('+', 'plus')}" for t in tags]
    out = []
    for h in base + extra:
        if h not in out:
            out.append(h)
    return " ".join(out[:n])


def facebook_caption(title: str, excerpt: str, url: str, tags: list[str], cfg: dict) -> str:
    h = _tags(tags, cfg["social"]["hashtags"])
    return (f"🚀 New tutorial: {title}\n\n{excerpt}\n\n"
            f"👉 Read it here: {url}\n\n{h}"[: cfg["social"]["fb_max"]])


def instagram_caption(title: str, excerpt: str, url: str, tags: list[str], cfg: dict) -> str:
    # IG captions aren't clickable — push link-in-bio + blog URL visibly
    h = _tags(tags, cfg["social"]["hashtags"])
    return (f"✨ {title}\n\n{excerpt}\n\n🔗 Link in bio / {url}\n.\n.\n.\n{h}"[: cfg["social"]["ig_max"]])


def threads_caption(title: str, url: str, tags: list[str], cfg: dict) -> str:
    h = _tags(tags, cfg["social"]["hashtags"], n=3)
    txt = f"New on GTec: {title} 👇\n{url}\n{h}"
    return txt[: cfg["social"]["threads_max"]]
