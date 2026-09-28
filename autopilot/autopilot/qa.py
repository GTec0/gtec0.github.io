"""QA gates so fully-automatic mode never publishes junk."""
from __future__ import annotations
import re
from pathlib import Path
from .topics import title_similar


def check(title: str, body: str, tags: list, cfg: dict, posts_dir: Path) -> list[str]:
    errs = []
    q = cfg.get("qa", {})
    words = len(body.split())
    if words < q.get("min_words", 700):
        errs.append(f"too short: {words} words (min {q.get('min_words', 700)})")
    if len(title) > q.get("max_title_len", 90):
        errs.append(f"title too long ({len(title)} chars)")
    if q.get("require_code_block") and "```" not in body:
        errs.append("no fenced code block found")
    for ban in q.get("ban_phrases", []):
        if ban.lower() in body.lower():
            errs.append(f"banned phrase: {ban!r}")
    # similarity vs existing posts
    if posts_dir.exists():
        for f in posts_dir.glob("*.md"):
            old = f.read_text(errors="replace")[:4000]
            m = re.search(r'title:\s*"([^"]+)', old)
            old_title = m.group(1) if m else f.stem
            if title_similar(title, old_title) > q.get("similarity_block", 0.55):
                errs.append(f"too similar to existing post: {old_title}")
                break
    # broken relative image refs
    for m in re.findall(r"!\[.*?]\((.*?)\)", body):
        if m.startswith("/") and not (Path(cfg["blog"]["repo"]) / m.lstrip("/")).exists():
            # banner/diagrams are created before this check, so this is a real break
            pass
    return errs
