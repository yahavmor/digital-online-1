# -*- coding: utf-8 -*-
"""
העלאת קובץ תמונה מקומי ל-Meta (POST /act_<id>/adimages) - בקשה אחת (לא Resumable
כמו וידאו, Meta לא דורשת את זה לתמונות), מחזירה image_hash לשימוש בקריאטיב.
"""

import json
from pathlib import Path

import requests

import config

CACHE_FILE = Path("./logs/image_upload_cache.json")


def _load_upload_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_upload_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_image(local_path: Path, name: str) -> str:
    """מעלה קובץ תמונה ומחזיר image_hash."""
    if config.DRY_RUN:
        return f"DRY_RUN_IMAGE_HASH_{name}"

    url = f"{config.GRAPH_URL}/act_{config.AD_ACCOUNT_ID}/adimages"
    with open(local_path, "rb") as f:
        resp = requests.post(url, data={
            "access_token": config.ACCESS_TOKEN,
        }, files={local_path.name: f}, timeout=120)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בהעלאת תמונה '{name}': {data['error']}")

    images = data.get("images", {})
    if not images:
        raise RuntimeError(f"תשובה לא צפויה מהעלאת תמונה '{name}': {data}")
    image_info = next(iter(images.values()))
    return image_info["hash"]


def upload_and_prepare(local_path: Path, name: str) -> dict:
    """
    זרימה מלאה: העלאה (עם מטמון לפי שם, כמו video_upload.upload_and_prepare - כדי
    שלא להעלות שוב תמונה שכבר הועלתה בהרצה קודמת שנכשלה בשלב מאוחר יותר).
    מחזיר {'image_hash'}.
    """
    if config.DRY_RUN:
        return {"image_hash": upload_image(local_path, name)}

    cache = _load_upload_cache()
    cached = cache.get(name)
    if cached:
        print(f"  '{name}' כבר הועלתה בהרצה קודמת (image_hash={cached['image_hash']}) - מדלג על העלאה חוזרת.")
        return cached

    result = {"image_hash": upload_image(local_path, name)}
    cache[name] = result
    _save_upload_cache(cache)
    return result
