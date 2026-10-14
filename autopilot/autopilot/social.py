"""Meta Social Automation (FB, IG, Threads)."""
from __future__ import annotations
import requests
import logging
import os

logger = logging.getLogger("autopilot.social")

def _meta_post(endpoint: str, params: dict, token: str) -> dict:
    params["access_token"] = token
    try:
        r = requests.post(f"https://graph.facebook.com/v20.0/{endpoint}", data=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Meta API error ({endpoint}): {e}")
        return {}

def post_to_facebook(cfg: dict, caption: str, url: str, banner_abs: str) -> bool:
    """Posts to FB Page feed."""
    page_id = os.environ.get("FB_PAGE_ID") or cfg.get("social", {}).get("fb_page_id")
    token = os.environ.get("FB_TOKEN") or cfg.get("social", {}).get("fb_token")
    if not page_id or not token:
        return False

    params = {
        "message": caption,
        "link": url,
    }
    res = _meta_post(f"{page_id}/feed", params, token)
    return "id" in res

def post_to_instagram(cfg: dict, caption: str, url: str, banner_url: str) -> bool:
    """Posts to IG Business Account."""
    ig_id = os.environ.get("IG_USER_ID") or cfg.get("social", {}).get("ig_user_id")
    token = os.environ.get("IG_TOKEN") or cfg.get("social", {}).get("ig_token")
    if not ig_id or not token:
        return False

    container_params = {
        "image_url": banner_url,
        "caption": caption,
    }
    res = _meta_post(f"{ig_id}/media", container_params, token)
    creation_id = res.get("id")
    if not creation_id:
        return False

    publish_params = {"creation_id": creation_id}
    res = _meta_post(f"{ig_id}/media_publish", publish_params, token)
    return "id" in res

def post_to_threads(cfg: dict, caption: str, url: str, banner_url: str) -> bool:
    """Posts to Threads account."""
    threads_id = os.environ.get("THREADS_USER_ID") or cfg.get("social", {}).get("threads_user_id")
    token = os.environ.get("THREADS_TOKEN") or cfg.get("social", {}).get("threads_token")
    if not threads_id or not token:
        return False

    container_params = {
        "media_type": "IMAGE",
        "image_url": banner_url,
        "text": caption,
    }
    res = _meta_post(f"{threads_id}/threads", container_params, token)
    creation_id = res.get("id")
    if not creation_id:
        return False

    publish_params = {"creation_id": creation_id}
    res = _meta_post(f"{threads_id}/threads_publish", publish_params, token)
    return "id" in res

def share_all(cfg: dict, title: str, excerpt: str, url: str, tags: list[str], banner_abs: str) -> dict:
    """Orchestrates sharing across all enabled platforms."""
    from . import captions as C
    
    banner_rel = str(banner_abs).split("banners/")[-1]
    banner_url = f"{cfg['blog']['url'].rstrip('/')}/assets/images/banners/{banner_rel}"
    
    results = {}
    
    fb_cap = C.facebook_caption(title, excerpt, url, tags, cfg)
    results["facebook"] = post_to_facebook(cfg, fb_cap, url, banner_abs)
    
    ig_cap = C.instagram_caption(title, excerpt, url, tags, cfg)
    results["instagram"] = post_to_instagram(cfg, ig_cap, url, banner_url)
    
    th_cap = C.threads_caption(title, url, tags, cfg)
    results["threads"] = post_to_threads(cfg, th_cap, url, banner_url)
    
    return results
