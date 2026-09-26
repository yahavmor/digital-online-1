# -*- coding: utf-8 -*-
"""
מעלה מראש ל-Meta את כל סרטון/תמונה מ-config.VIDEOS שעדיין אין לו מטמון העלאה
(video_upload_cache.json / image_upload_cache.json) - בלי ליצור קמפיין/Ad Set/מודעה.

למה זה נפרד מ-campaign_launch.py: campaign_launch.py גם יוצר Ad Set בעצמו, עם
optimization_goal=LINK_CLICKS (config.OPTIMIZATION_GOAL) - זה לא מתאים לקמפיין
"מעורבות" הפעיל כרגע (OUTCOME_ENGAGEMENT, Ad Set-ים נוצרים רק ע"י שכפול ידני
ב-Ads Manager). הסקריפט הזה עושה רק את שלב ההעלאה (המורכב/האיטי) מראש, כדי
שכשתשכפלו ידנית את 10 סטי המודעות החדשים ב-Ads Manager, fill_engagement_creatives.py
ימצא את המטמון כבר מוכן ויוכל לצרף קריאטיב מיד בלי להעלות שוב.

הרצה:
    python upload_new_media.py
"""

import json
import sys

import config
import drive_videos
import image_upload
import video_upload


def load_cache(module) -> dict:
    if not module.CACHE_FILE.exists():
        return {}
    try:
        return json.loads(module.CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def main():
    if config.ACCESS_TOKEN in ("PASTE_YOUR_TOKEN_HERE", "", None):
        print("שגיאה: לא הוגדר META_ACCESS_TOKEN.")
        sys.exit(1)

    video_cache = load_cache(video_upload)
    image_cache = load_cache(image_upload)

    pending = [v for v in config.VIDEOS
               if v["ad_set_name"] not in (image_cache if v.get("media_type") == "image" else video_cache)]

    if not pending:
        print("כל הסרטונים/תמונות ב-config.VIDEOS כבר הועלו בעבר (יש מטמון לכולם). אין מה להעלות.")
        return

    print(f"נמצאו {len(pending)} פריטים שעדיין לא הועלו ל-Meta:")
    for v in pending:
        print(f"  - {v['ad_set_name']} ({v.get('media_type', 'video')})")
    print()

    print("--- הורדת קבצים מ-Google Drive (מדלג על מה שכבר הורד בעבר) ---")
    videos_data = drive_videos.ensure_videos_downloaded()

    print("\n--- העלאה ל-Meta ---")
    for v in pending:
        name = v["ad_set_name"]
        media_type = v.get("media_type", "video")
        local_path = videos_data[name]["path"]

        print(f"\n[{name}] ({media_type})")
        if media_type == "image":
            result = image_upload.upload_and_prepare(local_path, name=name)
            print(f"  הועלה. image_hash={result['image_hash']}")
        else:
            result = video_upload.upload_and_prepare(local_path, name=name)
            print(f"  הועלה. video_id={result['video_id']}")

    print("\n=== סיום ===")
    print("כל הפריטים החדשים הועלו ל-Meta והמטמון עודכן. עכשיו אפשר לשכפל ב-Ads Manager "
          "את סטי המודעות (renaming לפי ad_set_name), ואז להריץ python fill_engagement_creatives.py "
          "כדי לצרף להם את הקריאטיב האמיתי בלי המתנה נוספת.")


if __name__ == "__main__":
    main()
