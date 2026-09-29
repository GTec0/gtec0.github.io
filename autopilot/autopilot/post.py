"""Build a beautiful-jekyll post file (front matter matches your existing posts)."""
from __future__ import annotations
import datetime as dt
import re
from pathlib import Path
from .images import slugify


def build_filename(title: str, date: dt.date) -> str:
    return f"{date.isoformat()}-{slugify(title)}.md"


def render_front_matter(title: str, subtitle: str, tags: list[str], banner_rel: str, author: str, date: dt.date) -> str:
    tag_list = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    safe_title = title.replace('"', "'")
    lines = [
        "---",
        "layout: post",
        f'title: "{safe_title}"',
    ]
    if subtitle:
        lines.append(f'subtitle: "{subtitle.replace(chr(34), chr(39))}"')
    lines += [
        f"date: {date.isoformat()}",
        "categories: []",
        f"tags: {tag_list}",
        f"thumbnail-img: {banner_rel}",
        f"share-img: {banner_rel}",
        f"author: {author}",
        "---",
        "",
    ]
    return "\n".join(lines)


def write_post(cfg: dict, title: str, subtitle: str, tags: list[str], body: str,
               banner_rel: str, date: dt.date | None = None) -> Path:
    root = Path(cfg["blog"]["repo"])
    posts_dir = root / cfg["blog"].get("posts_dir", "_posts")
    posts_dir.mkdir(parents=True, exist_ok=True)
    date = date or dt.date.today()
    md = render_front_matter(title, subtitle, tags, banner_rel, cfg["blog"]["author"], date)
    md += body
    path = posts_dir / build_filename(title, date)
    i = 2
    while path.exists():  # fully-automatic must never overwrite
        path = posts_dir / build_filename(f"{title} {i}", date)
        i += 1
    path.write_text(md)
    return path


def post_url(cfg: dict, post_path: Path) -> str:
    stem = post_path.stem  # YYYY-MM-DD-slug
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.*)", stem)
    slug = m.group(2) if m else stem
    date = m.group(1) if m else ""
    base = cfg["blog"]["url"].rstrip("/")
    # beautiful-jekyll default permalink: /YYYY-MM-DD-slug/ (matches your live site)
    return f"{base}/{date}-{slug}/" if date else f"{base}/{slug}/"
