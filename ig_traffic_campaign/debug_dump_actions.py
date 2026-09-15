# -*- coding: utf-8 -*-
"""
מדפיס את מערך ה-actions הגולמי מה-Insights API עבור קמפיין נתון, ברמת מודעה -
כדי למצוא את ה-action_type המדויק של "ביקורים בפרופיל אינסטגרם" (מה שרואים ב-
Ads Manager בפועל), כי extract_link_clicks() ב-insights.py מחפש רק link_click.

הרצה ראשונה (ללא action_attribution_windows) הראתה link_click נמוך בהרבה ממה
שה-UI של Ads Manager מציג באותה מודעה בדיוק (למשל "שיחת מכירה זה לא חוקר ונחקר":
0 link_click כאן מול 2 "ביקורים בפרופיל" ו-₪4.86 הוצאה ב-UI). זה עלול להיות
חלון-ייחוס (attribution window) שונה בין ברירת המחדל של ה-API לזה שה-UI מציג -
לכן משווים כאן שתי שאילתות: אחת בלי action_attribution_windows (ברירת מחדל),
ואחת עם 7d_click,1d_view (ברירת המחדל הנפוצה של Ads Manager עצמו).

הרצה:
    python debug_dump_actions.py
"""

import json

import requests

import config
import insights


def fetch_with_attribution(campaign_id: str, attribution_windows: str | None) -> list[dict]:
    url = f"{config.GRAPH_URL}/{campaign_id}/insights"
    params = {
        "level": "ad",
        "date_preset": config.DATE_PRESET,
        "fields": "ad_id,ad_name,adset_id,spend,impressions,actions",
        "access_token": config.ACCESS_TOKEN,
        "limit": 200,
    }
    if attribution_windows:
        params["action_attribution_windows"] = attribution_windows

    results = []
    while url:
        resp = requests.get(url, params=params, timeout=30)
        params = None
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"נכשל בשליפת insights: {data['error']}")
        results.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
    return results


def print_rows(title: str, rows: list[dict]) -> None:
    print(f"=== {title} ({len(rows)} שורות) ===\n")
    for row in rows:
        print(f"--- {row.get('ad_name')} (spend={row.get('spend')}) ---")
        print(json.dumps(row.get("actions", []), ensure_ascii=False, indent=2))
        print()


def main():
    campaign = insights.find_campaign()
    if not campaign:
        print(f"לא נמצא קמפיין בשם '{config.CAMPAIGN_NAME}'.")
        return
    print(f"קמפיין: {campaign['id']} ({campaign['name']})\n")

    default_rows = fetch_with_attribution(campaign["id"], None)
    print_rows("ברירת מחדל (בלי action_attribution_windows)", default_rows)

    wide_rows = fetch_with_attribution(campaign["id"], "7d_click,1d_view")
    print_rows("עם 7d_click,1d_view (ברירת המחדל של Ads Manager)", wide_rows)


if __name__ == "__main__":
    main()
