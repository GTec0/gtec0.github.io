"""state.json — what was published/posted, so reruns never duplicate."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path


def load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"done": []}


def record(path: Path, entry: dict) -> dict:
    st = load(path)
    entry["at"] = dt.datetime.utcnow().isoformat() + "Z"
    st["done"].append(entry)
    path.write_text(json.dumps(st, indent=2))
    return st
