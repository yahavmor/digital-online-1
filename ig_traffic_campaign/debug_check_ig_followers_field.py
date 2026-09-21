# -*- coding: utf-8 -*-
"""
בודק אם אפשר למשוך את מספר העוקבים הכולל של הפרופיל (config.IG_ACTOR_ID) דרך
Instagram Graph API הרגיל (לא Ads Insights) - עם אותו טוקן (System User) שכבר
בשימוש. זה שדה ברמת החשבון/פרופיל, לא ברמת מודעה - לא "כמה עוקבים הביאה כל
מודעה" (זה כבר נבדק ואומת כלא-אפשרי), אלא סך העוקבים הנוכחי, שניתן לרשום
לאורך זמן ולראות מגמה כללית.

הרצה:
    python debug_check_ig_followers_field.py
"""

import json

import requests

import config
from redact import redact


def main():
    print("--- ניסיון 1: ישירות מול IG_ACTOR_ID ---")
    url = f"{config.GRAPH_URL}/{config.IG_ACTOR_ID}"
    resp = requests.get(url, params={
        "fields": "followers_count,username",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    print(json.dumps(redact(resp.json()), ensure_ascii=False, indent=2))

    print("\n--- ניסיון 2: דרך PAGE_ID -> instagram_business_account ---")
    url2 = f"{config.GRAPH_URL}/{config.PAGE_ID}"
    resp2 = requests.get(url2, params={
        "fields": "instagram_business_account{followers_count,username}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    print(json.dumps(redact(resp2.json()), ensure_ascii=False, indent=2))

    # ben_nahum_1 מוקצה ישירות ל-Business Portfolio בלי דף פייסבוק מקושר קלאסי
    # (ראו ההערה ב-config.py) - אז הדרך הנכונה היא דרך owned_instagram_accounts
    # של ה-Business עצמו, לא דרך Page. קודם מאתרים את ה-Business ID/ים שהטוקן רואה.
    print("\n--- ניסיון 3: /me/businesses (מאתר Business IDs נגישים לטוקן) ---")
    url3 = f"{config.GRAPH_URL}/me/businesses"
    resp3 = requests.get(url3, params={
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    businesses_data = resp3.json()
    print(json.dumps(redact(businesses_data), ensure_ascii=False, indent=2))

    print("\n--- ניסיון 4: owned_instagram_accounts לכל Business שנמצא ---")
    for biz in businesses_data.get("data", []):
        biz_id = biz.get("id")
        url4 = f"{config.GRAPH_URL}/{biz_id}/owned_instagram_accounts"
        resp4 = requests.get(url4, params={
            "fields": "id,username,followers_count",
            "access_token": config.ACCESS_TOKEN,
        }, timeout=30)
        print(f"Business {biz_id}:")
        print(json.dumps(redact(resp4.json()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
