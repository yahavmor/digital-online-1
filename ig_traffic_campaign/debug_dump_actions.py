# -*- coding: utf-8 -*-
"""
מדפיס את מערך ה-actions הגולמי מה-Insights API עבור קמפיין נתון, ברמת מודעה -
כדי למצוא את ה-action_type המדויק של "ביקורים בפרופיל אינסטגרם" (מה שרואים ב-
Ads Manager בפועל), כי extract_link_clicks() ב-insights.py מחפש רק link_click,
וזה כנראה לא המדד הנכון לקמפיין ה"מעורבות" (Instagram Profile Visits).

הרצה:
    python debug_dump_actions.py
"""

import json

import config
import insights


def main():
    campaign = insights.find_campaign()
    if not campaign:
        print(f"לא נמצא קמפיין בשם '{config.CAMPAIGN_NAME}'.")
        return
    print(f"קמפיין: {campaign['id']} ({campaign['name']})\n")

    rows = insights.fetch_ad_insights(campaign["id"])
    print(f"נמצאו {len(rows)} שורות insights ברמת מודעה (date_preset={config.DATE_PRESET}).\n")

    for row in rows:
        spend = row.get("spend")
        if spend in (None, "0", "0.0", 0):
            continue
        print(f"--- {row.get('ad_name')} (spend={spend}) ---")
        print(json.dumps(row.get("actions", []), ensure_ascii=False, indent=2))
        print()


if __name__ == "__main__":
    main()
