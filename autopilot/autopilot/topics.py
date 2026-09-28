"""Topic picker: trending (free, no keys) + evergreen backlog + dedup vs _posts + state."""
from __future__ import annotations
import json
import re
from pathlib import Path
import urllib.request
import yaml


def _get_json(url: str, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "gtec-autopilot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _get_text(url: str, timeout=15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "gtec-autopilot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def trending_candidates(limit=15) -> list[str]:
    out: list[str] = []
    # HackerNews top stories
    try:
        ids = _get_json("https://hacker-news.firebaseio.com/v0/topstories.json")[:20]
        for i in ids[:10]:
            try:
                it = _get_json(f"https://hacker-news.firebaseio.com/v0/item/{i}.json")
                t = (it or {}).get("title", "")
                if t and len(t) > 20:
                    out.append(t)
            except Exception:
                continue
    except Exception:
        pass
    # dev.to latest practical articles
    try:
        arts = _get_json("https://dev.to/api/articles?per_page=20&state=rising")
        for a in arts if isinstance(arts, list) else []:
            t = a.get("title", "")
            if t:
                out.append(t)
    except Exception:
        pass
    # GitHub trending repos -> convert to tutorial angle
    try:
        html = _get_text("https://github.com/trending?since=daily")
        repos = re.findall(r'href="(/[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)"', html)
        seen = set()
        for r in repos:
            if r in seen or r.startswith("/trending"):
                continue
            seen.add(r)
            out.append(f"Getting started with {r.strip('/')} — what it is and a hands-on demo")
            if len(out) >= limit + 10:
                break
    except Exception:
        pass
    # de-dupe, keep order
    uniq, seen = [], set()
    for t in out:
        k = t.lower().strip()
        if k and k not in seen:
            seen.add(k)
            uniq.append(t)
    return uniq[:limit]


def existing_slugs(posts_dir: Path) -> set[str]:
    slugs = set()
    if not posts_dir.exists():
        return slugs
    for f in posts_dir.glob("*.md"):
        text = f.read_text(errors="replace")[:2000].lower()
        m = re.search(r"title:\s*\"?([^\"\n]+)", text)
        if m:
            slugs.add(m.group(1).strip().lower())
        slugs.add(f.stem.lower())
    return slugs


def title_similar(a: str, b: str) -> float:
    wa, wb = set(re.findall(r"[a-z0-9]+", a.lower())), set(re.findall(r"[a-z0-9]+", b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(len(wa), len(wb))


# Varied framings for trending headlines. The wrapper is picked deterministically
# (md5 of the title) so the same headline always maps to the same post title,
# but different headlines get different framings — no more identical
# "— explained with a hands-on example" suffix on every post.
_TRENDING_WRAPPERS = [
    "{t} — a hands-on walkthrough",
    "{t}: a practical beginner's guide",
    "{t}: what it is and how to use it",
    "Getting started with {t}",
    "{t} explained with runnable examples",
    "{t}",
]


def to_tutorial_title(t: str) -> str:
    """Turn a raw headline into a tutorial title without repetitive slop."""
    import hashlib
    s = re.sub(r"^(show|ask|tell|launch) hn:\s*", "", t.strip(), flags=re.I).rstrip(".")
    if len(s) > 110:
        s = s[:107].rsplit(" ", 1)[0]
    low = s.lower()
    if low.startswith(("how to", "how ", "getting started", "build ", "learn ",
                       "try ", "trying ", "10 ", "5 ")):
        return s  # already tutorial-shaped — leave it alone
    i = hashlib.md5(s.encode()).digest()[0] % len(_TRENDING_WRAPPERS)
    return _TRENDING_WRAPPERS[i].format(t=s)


def pick_topic(cfg: dict, state_path: Path, force_topic: str | None = None) -> dict:
    """Returns {topic, tags, angle, source}."""
    root = Path(cfg["blog"]["repo"])
    posts_dir = root / cfg["blog"].get("posts_dir", "_posts")
    existing = existing_slugs(posts_dir)
    state = json.loads(state_path.read_text()) if state_path.exists() else {"done": []}
    done_titles = [d.get("topic", "") for d in state.get("done", [])]

    def is_dup(title: str) -> bool:
        tl = title.lower()
        for e in list(existing) + [d.lower() for d in done_titles]:
            if title_similar(tl, e) > 0.6 or tl == e:
                return True
        return False

    if force_topic:
        return {"topic": force_topic, "tags": ["Programming", "Developer Tips"],
                "angle": "Hands-on tutorial for beginners", "source": "manual"}

    # 1) trending, mapped to tutorial angle
    if cfg.get("topics", {}).get("trending", {}).get("enabled", True):
        try:
            for t in trending_candidates(cfg["topics"]["trending"].get("max_candidates", 15)):
                if t.strip().endswith("?"):
                    continue  # question threads make poor tutorials — skip
                tutorial = to_tutorial_title(t)
                if not is_dup(tutorial):
                    return {"topic": tutorial, "tags": ["Programming", "Developer Tips"],
                            "angle": "News-pegged explainer: what happened + hands-on tutorial", "source": "trending"}
        except Exception:
            pass

    # 2) evergreen round-robin
    ev_path = Path(cfg["topics"].get("evergreen_file", "topics.yaml"))
    if not ev_path.is_absolute():
        ev_path = Path(__file__).resolve().parent.parent / ev_path
    items = yaml.safe_load(ev_path.read_text()).get("evergreen", [])
    for item in items:
        if not is_dup(item["topic"]):
            return {"topic": item["topic"], "tags": item.get("tags", ["Programming"]),
                    "angle": item.get("angle", ""), "source": "evergreen"}
    # fallback: should never happen, but guarantees fully-automatic never stalls
    return {"topic": "Linux pipes and redirection: 10 examples that click",
            "tags": ["Linux", "Bash", "Beginner"], "angle": "Hands-on", "source": "fallback"}
