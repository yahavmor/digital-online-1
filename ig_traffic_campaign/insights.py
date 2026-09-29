# -*- coding: utf-8 -*-
"""
משיכת נתוני ביצועים (Insights) מ-Meta Marketing API ברמת המודעה, מסונן לקמפיין הזה בלבד
(config.CAMPAIGN_NAME) - לא כל מודעה אחרת שכבר קיימת בחשבון act_330184635273905.
מקביל בכוונה ל-tiktok_ads_automation/insights.py.

עדכון: הקמפיין הפעיל ממוטב ל"ביקורים בפרופיל" (results = profile_visit_view), והמטרה
העסקית היא עוקבים - לכן נוספו כאן גם ביקורים בפרופיל, עוקבים (המדד "Follows or likes"
של Meta = action_type "like"), שמירות והודעות, ותקציב יומי כולל של הקבוצות הפעילות.
"""

import requests

import config


def find_campaign() -> dict | None:
    """מחפש את הקמפיין לפי שם (config.CAMPAIGN_NAME) בחשבון. מחזיר {'id','name','objective'} או None."""
    url = f"{config.GRAPH_URL}/act_{config.AD_ACCOUNT_ID}"
    resp = requests.get(url, params={
        "fields": "campaigns.limit(200){id,name,objective}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בשליפת קמפיינים עבור act_{config.AD_ACCOUNT_ID}: {data['error']}")

    campaigns = data.get("campaigns", {}).get("data", [])
    return next((c for c in campaigns if c.get("name") == config.CAMPAIGN_NAME), None)


def fetch_ad_insights(campaign_id: str, date_preset: str | None = None) -> list[dict]:
    """מושך ביצועים ברמת מודעה עבור קמפיין נתון בלבד. date_preset ברירת מחדל: config.DATE_PRESET."""
    url = f"{config.GRAPH_URL}/{campaign_id}/insights"
    params = {
        "level": "ad",
        "date_preset": date_preset or config.DATE_PRESET,
        "fields": "ad_id,ad_name,adset_id,spend,impressions,inline_link_clicks,actions,results",
        "access_token": config.ACCESS_TOKEN,
        "limit": 200,
    }

    results = []
    while url:
        resp = requests.get(url, params=params, timeout=30)
        params = None  # paging url כבר כולל פרמטרים
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"נכשל בשליפת insights עבור קמפיין {campaign_id}: {data['error']}")
        results.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")

    return results


def extract_action(insight_row: dict, action_type: str) -> int:
    """מחזיר את הערך של action_type מסוים מתוך actions (0 אם לא קיים)."""
    for a in insight_row.get("actions") or []:
        if a.get("action_type") == action_type:
            return int(float(a.get("value", 0)))
    return 0


def extract_link_clicks(insight_row: dict) -> int:
    """סופר קליקים על הלינק (link_click) מתוך actions."""
    return extract_action(insight_row, "link_click")


def extract_profile_visits(insight_row: dict) -> int:
    """
    ביקורים בפרופיל = ה-"results" של הקמפיין (indicator = profile_visit_view).
    כשאין תוצאות, Meta מחזירה את ה-indicator בלי values - ואז מחזירים 0.
    """
    for r in insight_row.get("results") or []:
        if "profile_visit" in (r.get("indicator") or ""):
            values = r.get("values") or []
            if values:
                return int(float(values[0].get("value", 0)))
    return 0


def extract_follows(insight_row: dict) -> int:
    """עוקבים = המדד "Follows or likes" של Meta (action_type 'like')."""
    return extract_action(insight_row, "like")


def extract_saves(insight_row: dict) -> int:
    return extract_action(insight_row, "onsite_conversion.post_net_save")


def extract_messages(insight_row: dict) -> int:
    return extract_action(insight_row, "onsite_conversion.messaging_conversation_started_7d")


def get_ads_status(campaign_id: str) -> dict:
    """מחזיר {ad_id: effective_status} לכל המודעות בקמפיין, בקריאה אחת."""
    url = f"{config.GRAPH_URL}/{campaign_id}"
    resp = requests.get(url, params={
        "fields": "ads.limit(200){id,effective_status}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בשליפת סטטוס מודעות לקמפיין {campaign_id}: {data['error']}")
    return {ad["id"]: ad.get("effective_status", "UNKNOWN") for ad in data.get("ads", {}).get("data", [])}


def get_ads(campaign_id: str) -> list[dict]:
    """מחזיר את כל המודעות בקמפיין (id, name, effective_status) - כולל מודעות חדשות שעוד אין להן נתונים."""
    url = f"{config.GRAPH_URL}/{campaign_id}"
    resp = requests.get(url, params={
        "fields": "ads.limit(200){id,name,effective_status}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בשליפת מודעות לקמפיין {campaign_id}: {data['error']}")
    return data.get("ads", {}).get("data", [])


def get_adsets(campaign_id: str) -> list[dict]:
    """מחזיר את קבוצות המודעות בקמפיין עם סטטוס ותקציב יומי (באגורות)."""
    url = f"{config.GRAPH_URL}/{campaign_id}"
    resp = requests.get(url, params={
        "fields": "adsets.limit(200){id,name,effective_status,daily_budget}",
        "access_token": config.ACCESS_TOKEN,
    }, timeout=30)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"נכשל בשליפת קבוצות מודעות לקמפיין {campaign_id}: {data['error']}")
    return data.get("adsets", {}).get("data", [])
