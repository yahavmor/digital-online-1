# -*- coding: utf-8 -*-
"""
משווה בין insights ברמת קמפיין לבין insights ברמת מודעה (מה ש-dashboard.py מבקש
בפועל) - כדי להבדיל בין "השהיה כללית בצנרת ה-Insights של Meta" (שתי הרמות יראו
אפס) לבין "בעיה ספציפית בשאילתת רמת-המודעה" (קמפיין יראה נתונים, מודעה לא).

הרצה:
    python debug_check_insights_levels.py
"""

import json

import requests

import config
import insights


def main():
    campaign = insights.find_campaign()
    if not campaign:
        print("לא נמצא קמפיין.")
        return
    campaign_id = campaign["id"]
    print(f"קמפיין: {campaign_id}\n")

    for level in ("campaign", "adset", "ad"):
        print(f"=== insights ברמת {level} (date_preset={config.DATE_PRESET}) ===")
        url = f"{config.GRAPH_URL}/{campaign_id}/insights"
        resp = requests.get(url, params={
            "level": level,
            "date_preset": config.DATE_PRESET,
            "fields": "spend,impressions,clicks,actions",
            "access_token": config.ACCESS_TOKEN,
        }, timeout=30)
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print()


if __name__ == "__main__":
    main()
