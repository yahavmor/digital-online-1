# -*- coding: utf-8 -*-
"""
בודק אם יש יותר מקמפיין אחד בשם config.CAMPAIGN_NAME בחשבון (יש קמפיין ריק ישן
משלב ניפוי מוקדם, עם objective שגוי, שעדיין לא נמחק) - וכדי לוודא בוודאות שדווקא
insights.find_campaign() (ולכן גם dashboard.py) מחזירה את הקמפיין האמיתי/הפעיל,
לא את הישן/הריק, במקרה ש-Meta מחזירה אותם בסדר לא-צפוי.

הרצה:
    python debug_check_campaign_dupes.py
"""

import json

import requests

import config
import insights


def main():
    url = f"{config.GRAPH_URL}/act_{config.AD_ACCOUNT_ID}"
    resp = requests.get(url, params={
        "fields": "campaigns.limit(200){id,name,objective,status,created_time}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        print(f"שגיאה: {data['error']}")
        return

    matches = [c for c in data.get("campaigns", {}).get("data", [])
               if c.get("name") == config.CAMPAIGN_NAME]
    print(f"נמצאו {len(matches)} קמפיינים בשם '{config.CAMPAIGN_NAME}':")
    print(json.dumps(matches, ensure_ascii=False, indent=2))

    found = insights.find_campaign()
    print(f"\ninsights.find_campaign() (מה ש-dashboard.py משתמש בו בפועל) מחזיר:")
    print(json.dumps(found, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
