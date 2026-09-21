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
    url = f"{config.GRAPH_URL}/{config.IG_ACTOR_ID}"
    resp = requests.get(url, params={
        "fields": "followers_count,username",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    print(json.dumps(redact(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
