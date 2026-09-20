# -*- coding: utf-8 -*-
"""
בודק אם Meta חושפת את מדד "Instagram Follows" (עוקבים חדשים שנוצרו ממודעה) דרך
ה-Insights API הציבורי - Meta הוסיפה את המדד הזה ל-Ads Manager (UI) אבל לא ברור
אם/איך הוא זמין ב-API. במקום לנחש שם שדה, מנסה כמה מועמדים סבירים ישירות מול
החשבון האמיתי - שגיאת API על שדה לא-קיים תגיד לנו בדיוק מה לא תקין, ותשובה
תקינה תגיד לנו בדיוק מה השם הנכון.

הרצה:
    python debug_check_follows_metric.py
"""

import json

import requests

import config
import insights

# מועמדים סבירים לשם השדה/action_type - top-level fields וגם action_types בתוך actions.
CANDIDATE_TOP_LEVEL_FIELDS = [
    "instagram_follows",
    "estimated_ad_recallers",  # שדה ידוע אחר, בשביל להשוות איך שגיאת "שדה לא קיים" נראית
]

CANDIDATE_ACTION_TYPES = [
    "onsite_conversion.follow",
    "follow",
    "ig_follow",
    "instagram_profile_follow",
    "onsite_conversion.ig_follow",
]


def main():
    campaign = insights.find_campaign()
    if not campaign:
        print(f"לא נמצא קמפיין בשם '{config.CAMPAIGN_NAME}'.")
        return
    print(f"קמפיין: {campaign['id']} ({campaign['name']})\n")

    print("=== שלב 1: מנסה לבקש שדות top-level מועמדים ===\n")
    for field in CANDIDATE_TOP_LEVEL_FIELDS:
        url = f"{config.GRAPH_URL}/{campaign['id']}/insights"
        resp = requests.get(url, params={
            "level": "ad",
            "date_preset": config.DATE_PRESET,
            "fields": f"ad_name,{field}",
            "access_token": config.ACCESS_TOKEN,
            "limit": 5,
        }, timeout=30)
        data = resp.json()
        print(f"--- שדה: {field} ---")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])
        print()

    print("\n=== שלב 2: בודק אם action_type כלשהו מהמועמדים מופיע ב-actions בפועל ===\n")
    url = f"{config.GRAPH_URL}/{campaign['id']}/insights"
    resp = requests.get(url, params={
        "level": "ad",
        "date_preset": config.DATE_PRESET,
        "fields": "ad_name,actions",
        "access_token": config.ACCESS_TOKEN,
        "limit": 200,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        print(f"שגיאה: {data['error']}")
        return

    found_any = False
    all_action_types = set()
    for row in data.get("data", []):
        for a in row.get("actions", []):
            all_action_types.add(a.get("action_type"))
            if a.get("action_type") in CANDIDATE_ACTION_TYPES:
                found_any = True
                print(f"נמצא! {row.get('ad_name')}: {a}")

    if not found_any:
        print("לא נמצא אף action_type מהמועמדים בפועל.")
    print(f"\nכל ה-action_type הייחודיים שכן הופיעו בפועל ({len(all_action_types)}):")
    print(json.dumps(sorted(t for t in all_action_types if t), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
