# -*- coding: utf-8 -*-
"""
מחליף את הקריאטיב הריק שה-UI של Ads Manager בנה אוטומטית לכל מודעה בקמפיין החדש
(config.CAMPAIGN_NAME - קמפיין "מעורבות", Instagram Profile Visits) בקריאטיב אמיתי
עם הווידאו/תמונה/טקסט של אותו סרטון מ-config.VIDEOS.

אומת בפועל (14/9/2026, debug_inspect_creative.py) שכשמגדירים Conversion location=
Instagram Profile ב-UI, Meta בונה אוטומטית קריאטיב placeholder גנרי: object_type=
SHARE, בלי video/image בכלל, רק link_data.link לכתובת הפרופיל וכפתור
VIEW_INSTAGRAM_PROFILE - זה מה ש"נראה ריק". השדות האמיתיים שנדרשים (מתוך אותו
placeholder עצמו, לא ניחוש): instagram_user_id (לא instagram_actor_id!),
call_to_action.type=VIEW_INSTAGRAM_PROFILE עם value.app_link (כולל
config.IG_NUMERIC_USER_ID) ו-value.link.

משתמש בקבצי המטמון הקיימים (video_upload_cache.json / image_upload_cache.json)
כדי לא להעלות מחדש קבצים שכבר קיימים אצל Meta מהריצה המקורית של campaign_launch.py -
צריך להריץ את זה מאותה תיקייה/מחשב שבו רץ campaign_launch.py בעבר.

שים לב: חלק מהמודעות בקמפיין הזה כבר ACTIVE (רצות בפועל) - זה מחליף את הקריאטיב
שלהן ישירות, בלי לעצור אותן קודם.

הרצה:
    python fill_engagement_creatives.py
"""

import json
from pathlib import Path

import requests

import config
import image_upload
import insights
import video_upload


def load_cache(path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def get_adsets_with_ads(campaign_id: str) -> list:
    url = f"{config.GRAPH_URL}/{campaign_id}"
    resp = requests.get(url, params={
        "fields": "adsets.limit(200){name,ads{id,name,creative{object_type,video_id,"
                  "object_story_spec}}}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בשליפת סטים/מודעות עבור קמפיין {campaign_id}: {data['error']}")
    return data.get("adsets", {}).get("data", [])


def is_placeholder_creative(creative: dict | None) -> bool:
    """
    מזהה את הקריאטיב הגנרי שה-UI בונה אוטומטית (object_type=SHARE, בלי video_id,
    בלי image_hash ב-object_story_spec.link_data) - כדי להחליף רק אותו, ולדלג על
    קריאטיב שכבר תוקן. link_data/video_data הם שדות בתוך object_story_spec,
    לא שדות ישירים על ה-creative עצמו.
    """
    if not creative:
        return True
    if creative.get("video_id"):
        return False
    story_spec = creative.get("object_story_spec") or {}
    if story_spec.get("video_data"):
        return False
    link_data = story_spec.get("link_data") or {}
    if link_data.get("image_hash"):
        return False
    return True


def find_video_by_ad_set_name(name: str) -> dict | None:
    return next((v for v in config.VIDEOS if v["ad_set_name"] == name), None)


def build_call_to_action() -> dict:
    return {
        "type": "VIEW_INSTAGRAM_PROFILE",
        "value": {
            "app_link": f"instagram://user?username={config.IG_USERNAME}&userid={config.IG_NUMERIC_USER_ID}",
            "link": f"http://instagram.com/{config.IG_USERNAME}",
        },
    }


def build_object_story_spec(video: dict, cached_upload: dict) -> dict:
    media_type = video.get("media_type", "video")
    message = video["message"]
    title = video.get("title", "")
    description = video.get("description", "")
    call_to_action = build_call_to_action()

    if media_type == "image":
        link_data = {
            "image_hash": cached_upload["image_hash"],
            "message": message,
            "link": f"http://instagram.com/{config.IG_USERNAME}",
            "call_to_action": call_to_action,
        }
        if title:
            link_data["name"] = title
        if description:
            link_data["description"] = description
        return {
            "page_id": config.PAGE_ID,
            "instagram_user_id": config.IG_ACTOR_ID,
            "link_data": link_data,
        }

    video_data = {
        "video_id": cached_upload["video_id"],
        "image_url": cached_upload["thumbnail_url"],
        "message": message,
        "call_to_action": call_to_action,
    }
    if title:
        video_data["title"] = title
    if description:
        video_data["link_description"] = description
    return {
        "page_id": config.PAGE_ID,
        "instagram_user_id": config.IG_ACTOR_ID,
        "video_data": video_data,
    }


def create_creative(name: str, object_story_spec: dict) -> str:
    url = f"{config.GRAPH_URL}/act_{config.AD_ACCOUNT_ID}/adcreatives"
    resp = requests.post(url, data={
        "name": name,
        "object_story_spec": json.dumps(object_story_spec),
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל ביצירת קריאטיב '{name}': {data['error']}")
    return data["id"]


def attach_creative(ad_id: str, creative_id: str) -> None:
    url = f"{config.GRAPH_URL}/{ad_id}"
    resp = requests.post(url, data={
        "creative": json.dumps({"creative_id": creative_id}),
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בעדכון מודעה {ad_id} עם קריאטיב {creative_id}: {data['error']}")


def main():
    campaign = insights.find_campaign()
    if not campaign:
        print(f"לא נמצא קמפיין בשם '{config.CAMPAIGN_NAME}'.")
        return
    print(f"קמפיין: {campaign['id']} ({campaign['name']})\n")

    video_cache = load_cache(video_upload.CACHE_FILE)
    image_cache = load_cache(image_upload.CACHE_FILE)

    adsets = get_adsets_with_ads(campaign["id"])
    print(f"נמצאו {len(adsets)} סטים.\n")

    for adset in adsets:
        name = adset["name"].removesuffix(" - Ad Set")
        ads = adset.get("ads", {}).get("data", [])

        if not ads:
            print(f"[{name}] - אין שום מודעה בסט הזה, מדלג (בדוק ידנית).")
            continue

        ad = ads[0]
        if not is_placeholder_creative(ad.get("creative")):
            print(f"[{name}] - כבר יש קריאטיב אמיתי (עם וידאו/תמונה) למודעה, מדלג.")
            continue

        video = find_video_by_ad_set_name(name)
        if not video:
            print(f"[{name}] - לא נמצא ב-config.VIDEOS לפי שם, מדלג (שם לא תואם?).")
            continue

        media_type = video.get("media_type", "video")
        cache = image_cache if media_type == "image" else video_cache
        cached_upload = cache.get(name)
        if not cached_upload:
            print(f"[{name}] - אין מטמון העלאה קיים לשם הזה (video_upload_cache.json / "
                  f"image_upload_cache.json) - מדלג. ודא שאתה מריץ מאותה תיקייה שבה רץ "
                  f"campaign_launch.py בעבר.")
            continue

        print(f"[{name}] - יוצר קריאטיב חדש (media_type={media_type})...")
        object_story_spec = build_object_story_spec(video, cached_upload)
        creative_id = create_creative(name, object_story_spec)
        print(f"  creative_id={creative_id} - מצרף למודעה {ad['id']}...")
        attach_creative(ad["id"], creative_id)
        print("  הצליח.")

    print("\nסיום. עברו על כל המודעות ב-Ads Manager (תצוגה מקדימה של הקריאטיב) לפני הפעלה.")


if __name__ == "__main__":
    main()
