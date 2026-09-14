# -*- coding: utf-8 -*-
"""
בודק מה בדיוק יש בתוך הקריאטיב שמחובר למודעה נתונה (object_story_spec המלא) -
כדי להבין למה זה "נראה ריק" ב-Ads Manager למרות שה-API מדווח שיש creative מחובר.

הרצה:
    python debug_inspect_creative.py <ad_id>
"""

import json
import sys

import requests

import config


def main():
    if len(sys.argv) < 2:
        print("שימוש: python debug_inspect_creative.py <ad_id>")
        return

    ad_id = sys.argv[1]
    url = f"{config.GRAPH_URL}/{ad_id}"
    resp = requests.get(url, params={
        "fields": "name,status,effective_status,creative{id,name,object_story_spec,"
                  "object_type,status,video_id,image_url,thumbnail_url,body,title}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
