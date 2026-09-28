#!/usr/bin/env python3
"""GTec autopilot — free AI blog post generator (post ONLY, no social automation).

You share manually: every run prints ready-to-paste FB/IG/Threads captions and
saves them to SHARE.txt (latest run) for easy copy-paste.

Usage:
  python main.py --dry-run            # generate to ./preview/ (POST.md + SHARE.txt + banners)
  python main.py --topic "Your title" # force a topic
  python main.py                       # fully-automatic: pick topic -> generate -> QA -> write files
                                 # (aborts with exit 4 if all AI providers fail — no filler ever published)
"""
from __future__ import annotations
import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from autopilot.config import load_config
from autopilot import topics as T
from autopilot import llm, images as IMG, post as P, captions as C, qa as QA, state as ST

ROOT = Path(__file__).resolve().parent


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--topic", default=None)
    ap.add_argument("--allow-template", action="store_true",
                    help="permit the offline template fallback (local testing only). "
                         "--dry-run implies this; real runs fail instead of publishing filler.")
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    return ap.parse_args()


def front_matter_of(path: Path) -> dict:
    txt = path.read_text(errors="replace")
    m = re.search(r"^---\n(.*?)\n---\n", txt, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    fm["_body"] = txt[m.end():] if m else txt
    return fm


def share_text(cfg, title, excerpt, url, tags, banner_abs: Path) -> str:
    return (
        f"MANUAL SHARE KIT — {title}\n"
        f"Link: {url}\n"
        f"Banner to upload: {banner_abs}\n"
        f"(Post the banner + caption on IG/FB/Threads yourself.)\n"
        f"\n{'=' * 20} FACEBOOK (paste + link attaches preview) {'=' * 20}\n"
        f"{C.facebook_caption(title, excerpt, url, tags, cfg)}\n"
        f"\n{'=' * 20} INSTAGRAM (link NOT clickable — put URL in bio/stories) {'=' * 20}\n"
        f"{C.instagram_caption(title, excerpt, url, tags, cfg)}\n"
        f"\n{'=' * 20} THREADS (<=500 chars) {'=' * 20}\n"
        f"{C.threads_caption(title, url, tags, cfg)}\n"
    )


def main() -> int:
    a = parse_args()
    cfg = load_config(a.config)
    root = Path(cfg["blog"]["repo"]).resolve()
    posts_dir = root / cfg["blog"].get("posts_dir", "_posts")
    banners_dir = root / cfg["blog"].get("banners_dir", "assets/images/banners")
    state_path = ROOT / "state.json" if Path(cfg["blog"]["repo"]).as_posix() == "." else root / "autopilot-state.json"

    # ── 1. topic ──
    topic = T.pick_topic(cfg, state_path, force_topic=a.topic)
    print(f"[topic:{topic['source']}] {topic['topic']}")

    # ── 2. text ──
    body_raw, provider = llm.generate_post(cfg, topic,
                                           allow_template=a.allow_template or a.dry_run)
    if body_raw is None:
        # ALL providers failed: publish NOTHING. Non-zero exit turns the
        # Actions run red — owner notices the missing post and reads the log.
        print(f"[llm] FATAL: {provider} — no post written, nothing committed. "
              f"Check the [llm:*] FAILED lines above (keys? quota? model retired?).")
        return 4
    excerpt, diagrams, body = llm.extract_excerpt_and_diagrams(body_raw)
    print(f"[llm] provider={provider} words={len(body.split())} diagrams={len(diagrams)}")

    title = topic["topic"].strip().rstrip(".")
    if len(title) > 88:
        title = title[:85].rsplit(" ", 1)[0]
    tags = topic.get("tags", ["Programming"])[:5]

    if a.dry_run:
        prev = ROOT / "preview"
        shutil.rmtree(prev, ignore_errors=True)
        (prev / "banners").mkdir(parents=True)
        imgs = IMG.make_images(cfg, title, tags, diagrams, prev / "banners")
        (prev / "POST.md").write_text(P.render_front_matter(title, excerpt, tags, imgs["banner_rel"], cfg["blog"]["author"], dt.date.today()) + body)
        (prev / "SHARE.txt").write_text(share_text(cfg, title, excerpt, "https://gtec0.github.io/<slug>/", tags, imgs["banner_abs"]))
        print("[dry-run] wrote preview/POST.md + preview/SHARE.txt + banners. Nothing else touched.")
        return 0

    # ── 3. images ──
    imgs = IMG.make_images(cfg, title, tags, diagrams, banners_dir)
    print(f"[img] banner={imgs['banner_rel']} diagrams={len(imgs['diagrams'])}")

    # ── 4. QA (blocks junk even in fully-automatic mode) ──
    errs = QA.check(title, body, tags, cfg, posts_dir)
    if errs:
        print("[qa] BLOCKED:", "; ".join(errs))
        return 2

    # ── 5. write post ──
    path = P.write_post(cfg, title, excerpt, tags, body, imgs["banner_rel"],
                        imgs["diagrams"])
    url = P.post_url(cfg, path)
    print(f"[post] {path} -> {url}")

    ST.record(state_path, {"topic": topic["topic"], "file": path.name, "url": url,
                           "provider": provider, "source": topic["source"]})

    # ── 6. share kit (manual — you post it yourself) ──
    kit = share_text(cfg, title, excerpt, url, tags, imgs["banner_abs"])
    (ROOT / "SHARE.txt").write_text(kit)  # latest run only, overwritten each time
    print(kit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
