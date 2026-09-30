"""Load config.yaml + env overrides."""
from __future__ import annotations
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent

try:  # optional: load .env next to config so `cp .env.example .env` just works
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path) if path else ROOT / "config.yaml"
    cfg = yaml.safe_load(path.read_text())
    blog = cfg.get("blog", {})
    # env overrides (GitHub Secrets friendly)
    blog["url"] = os.getenv("BLOG_URL", blog.get("url", "https://gtec0.github.io"))
    # Autodetect repo root: works both standalone (./_posts) and nested
    # inside the blog repo as autopilot/ (../_posts).
    env_repo = os.getenv("BLOG_REPO")
    if env_repo:
        blog["repo"] = env_repo
    else:
        here = Path(__file__).resolve().parent.parent
        if not (here / blog.get("posts_dir", "_posts")).exists() and (here.parent / blog.get("posts_dir", "_posts")).exists():
            blog["repo"] = str(here.parent)
        else:
            blog["repo"] = str(here) if (here / blog.get("posts_dir", "_posts")).exists() else "."
    cfg["blog"] = blog
    cfg["_env"] = {
        "gemini_key": os.getenv("GEMINI_API_KEY", ""),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "groq_key": os.getenv("GROQ_API_KEY", ""),
        "groq_model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        "ollama_host": os.getenv("OLLAMA_HOST", ""),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.1"),
        "no_ai_images": os.getenv("NO_AI_IMAGES", "0") == "1",
        "hf_token": os.getenv("HF_TOKEN", ""),
    }
    return cfg
