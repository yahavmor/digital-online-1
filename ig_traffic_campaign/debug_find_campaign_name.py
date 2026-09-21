# -*- coding: utf-8 -*-
"""
מוצא את שם הקמפיין המדויק (ומזהה הקמפיין) לפי מזהה Ad Set ידוע - כדי לוודא את הערך
המדויק שצריך ב-config.CAMPAIGN_NAME, בלי לנחש (רווחים/ניסוח עלולים להיות שונים
ממה שרואים ב-UI).

הרצה:
    python debug_find_campaign_name.py <adset_id>
"""

import json
import sys

import requests

import config
from redact import redact


def main():
    if len(sys.argv) < 2:
        print("שימוש: python debug_find_campaign_name.py <adset_id>")
        return

    adset_id = sys.argv[1]
    url = f"{config.GRAPH_URL}/{adset_id}"
    resp = requests.get(url, params={
        "fields": "name,campaign{id,name,objective,effective_status}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    print(json.dumps(redact(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
