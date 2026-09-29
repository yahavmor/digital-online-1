# -*- coding: utf-8 -*-
"""
performance_dashboard.html - דשבורד קריאה-בלבד לקמפיין "מעורבות לאינסטגרם - ben_nahum_1".

עדכון (ספטמבר 2026): הדשבורד כבר לא מדרג לפי CTR. הקמפיין ממוטב ל"ביקורים בפרופיל",
והמטרה העסקית היא עוקבים - ומודעה יכולה להביא הרבה ביקורים זולים ואפס עוקבים. לכן:
- מוצגים ביקורים בפרופיל, עוקבים, אחוז המרה ועלות לעוקב לכל מודעה.
- הדירוג הוא לפי "עוקבים לכל ₪100" (על כל תקופת הקמפיין - יותר נתונים, פחות רעש).
- מודעות עם הרבה ביקורים ו-0 עוקבים מסומנות באזהרה.
- התקציב היומי מוצג כסכום של קבוצות המודעות הפעילות (לא "לכל מודעה").

לא מבצע שום פעולה על החשבון - קורא נתונים בלבד ובונה קובץ HTML סטטי.
הרצה: python dashboard.py
"""

from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import config
import insights

STATUS_LABELS = {
    "ACTIVE": "פעילה",
    "PAUSED": "מושהית",
    "PENDING_REVIEW": "בבדיקה",
    "IN_PROCESS": "בעיבוד",
    "DISAPPROVED": "נדחתה",
    "ARCHIVED": "בארכיון",
    "ADSET_PAUSED": "מושהית (סט)",
    "CAMPAIGN_PAUSED": "מושהית (קמפיין)",
    "WITH_ISSUES": "יש בעיה",
    "UNKNOWN": "-",
}

DATE_PRESET_LABELS = {
    "today": "היום",
    "yesterday": "אתמול",
    "last_7d": "7 הימים האחרונים",
    "last_14d": "14 הימים האחרונים",
    "last_28d": "28 הימים האחרונים",
    "last_30d": "30 הימים האחרונים",
    "last_90d": "90 הימים האחרונים",
    "this_month": "החודש הנוכחי",
    "last_month": "החודש הקודם",
    "maximum": "מאז תחילת הקמפיין",
}

# ספים לסימון - ניתן לכוונן
ZERO_FOLLOW_WARN_VISITS = 150   # 0 עוקבים אחרי לפחות כמה ביקורים = אזהרה
SMALL_SAMPLE_FOLLOWS = 3        # פחות עוקבים מזה = "מדגם קטן"
MIN_SPEND_TO_SHOW = 1.0         # מודעות שהוציאו פחות מזה לא מוצגות

RLM_LRM_CHARS = "‎‏"
NAME_SUFFIXES = (" - עותק", " - Ad", " - מאוחד")


def _display_name(ad_name: str) -> str:
    """
    מנקה שם מודעה לתצוגה: תווי RLM/LRM, סיומות שכפול ("- עותק"), " - Ad", " - מאוחד"
    וסיומת קובץ וידאו - כדי שאותו תוכן (למשל מודעה בקבוצה הישנה ובקבוצה המאוחדת)
    יתמזג לשורה אחת.
    """
    ad_name = ad_name.strip(RLM_LRM_CHARS).strip()
    changed = True
    while changed:
        changed = False
        for suffix in NAME_SUFFIXES:
            stripped = ad_name.removesuffix(suffix).strip(RLM_LRM_CHARS).strip()
            if stripped != ad_name:
                ad_name = stripped
                changed = True
        for ext in (".mov", ".mp4", ".MOV", ".MP4"):
            if ad_name.endswith(ext):
                ad_name = ad_name[: -len(ext)]
                changed = True
    return ad_name


STATUS_PRIORITY = ["ACTIVE", "PENDING_REVIEW", "IN_PROCESS", "WITH_ISSUES", "DISAPPROVED",
                   "PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED", "ARCHIVED"]


def _better_status(a: str, b: str) -> str:
    """מחזיר את הסטטוס ה"חי" יותר מבין השניים (פעילה > בבדיקה > ... > מושהית)."""
    rank = lambda s: STATUS_PRIORITY.index(s) if s in STATUS_PRIORITY else len(STATUS_PRIORITY)
    return a if rank(a) <= rank(b) else b


def status_by_name(ads: list[dict]) -> dict:
    """
    {שם תצוגה: סטטוס}. אותו סרטון יכול להופיע כמה פעמים (בקבוצה הישנה ובקבוצה המאוחדת) -
    אם אחד העותקים פעיל, השורה מוצגת כ"פעילה", גם אם לעותק הפעיל עוד אין נתונים.
    """
    out: dict[str, str] = {}
    for ad in ads:
        name = _display_name(ad.get("name", ad["id"]))
        st = ad.get("effective_status", "UNKNOWN")
        out[name] = _better_status(st, out[name]) if name in out else st
    return out


def _merge_rows(insight_rows: list[dict], statuses: dict) -> list[dict]:
    """statuses = {שם תצוגה: סטטוס} (מ-status_by_name)."""
    merged: dict[str, dict] = {}
    for r in insight_rows:
        name = _display_name(r.get("ad_name", r["ad_id"]))
        status = statuses.get(name, "UNKNOWN")
        m = merged.setdefault(name, {
            "ad_name": name, "status": status, "spend": 0.0, "impressions": 0,
            "clicks": 0, "visits": 0, "follows": 0, "saves": 0, "messages": 0,
        })
        m["spend"] += float(r.get("spend", 0) or 0)
        m["impressions"] += int(float(r.get("impressions", 0) or 0))
        m["clicks"] += insights.extract_link_clicks(r)
        m["visits"] += insights.extract_profile_visits(r)
        m["follows"] += insights.extract_follows(r)
        m["saves"] += insights.extract_saves(r)
        m["messages"] += insights.extract_messages(r)

    rows = []
    for m in merged.values():
        if m["spend"] < MIN_SPEND_TO_SHOW:
            continue
        m["cpv"] = m["spend"] / m["visits"] if m["visits"] else None
        m["follow_rate"] = m["follows"] / m["visits"] * 100 if m["visits"] else 0.0
        m["cpf"] = m["spend"] / m["follows"] if m["follows"] else None
        m["follows_per_100"] = m["follows"] / m["spend"] * 100 if m["spend"] else 0.0
        m["status_label"] = STATUS_LABELS.get(m["status"], m["status"])
        rows.append(m)

    # דירוג: קודם מודעות עם מספיק עוקבים (לפחות SMALL_SAMPLE_FOLLOWS) לפי עלות לעוקב, אחריהן
    # מודעות עם 1-2 עוקבים (מדגם קטן - לא מספיק כדי להכריז על מנצחת), ובסוף מודעות בלי עוקבים
    # לפי הוצאה (הכי "שורפות" קודם).
    solid = sorted((r for r in rows if r["follows"] >= SMALL_SAMPLE_FOLLOWS), key=lambda r: r["cpf"])
    small = sorted((r for r in rows if 0 < r["follows"] < SMALL_SAMPLE_FOLLOWS), key=lambda r: r["cpf"])
    zero = sorted((r for r in rows if not r["follows"]), key=lambda r: r["spend"], reverse=True)
    rows = solid + small + zero

    for i, r in enumerate(rows):
        badges = []
        if i == 0 and r["follows"] >= SMALL_SAMPLE_FOLLOWS:
            badges.append(("🏆 הכי זולה לעוקב", "st-win"))
        if not r["follows"] and r["visits"] >= ZERO_FOLLOW_WARN_VISITS:
            badges.append((f"⚠️ 0 עוקבים מתוך {r['visits']:,} ביקורים", "st-lose"))
        elif 0 < r["follows"] < SMALL_SAMPLE_FOLLOWS:
            badges.append(("מדגם קטן", "st-other"))
        r["badges"] = badges
    return rows


def build_rows(campaign_id: str, date_preset: str, statuses: dict) -> list[dict]:
    return _merge_rows(insights.fetch_ad_insights(campaign_id, date_preset), statuses)


def _totals(rows: list[dict]) -> dict:
    t = {k: sum(r[k] for r in rows) for k in ("spend", "impressions", "visits", "follows", "messages")}
    t["cpv"] = t["spend"] / t["visits"] if t["visits"] else None
    t["cpf"] = t["spend"] / t["follows"] if t["follows"] else None
    t["follow_rate"] = t["follows"] / t["visits"] * 100 if t["visits"] else 0.0
    return t


def _money(v) -> str:
    return "-" if v is None else f"₪{v:,.2f}"


def _badges_html(r: dict) -> str:
    return "".join(f'<span class="badge {c}">{escape(t)}</span>' for t, c in r["badges"])


def _table(rows: list[dict]) -> str:
    if not rows:
        return '<tr><td colspan="9" class="empty">אין נתונים לתקופה הזאת</td></tr>'
    return "\n".join(f"""
        <tr>
          <td><div class="nm">{escape(r['ad_name'])}</div><div class="bdg">{_badges_html(r)}</div></td>
          <td><span class="badge st-{'ACTIVE' if r['status'] == 'ACTIVE' else 'other'}">{escape(r['status_label'])}</span></td>
          <td>₪{r['spend']:,.2f}</td>
          <td>{r['visits']:,}</td>
          <td>{_money(r['cpv'])}</td>
          <td class="strong">{r['follows']:,}</td>
          <td>{r['follow_rate']:.1f}%</td>
          <td class="strong">{_money(r['cpf'])}</td>
          <td>{r['messages']:,}</td>
        </tr>""" for r in rows)


def generate_dashboard() -> str:
    campaign = insights.find_campaign()
    now_str = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m/%Y %H:%M")
    recent_preset = config.DATE_PRESET
    recent_label = DATE_PRESET_LABELS.get(recent_preset, recent_preset)

    if campaign:
        statuses = status_by_name(insights.get_ads(campaign["id"]))
        recent = build_rows(campaign["id"], recent_preset, statuses)
        lifetime = build_rows(campaign["id"], "maximum", statuses)
        adsets = insights.get_adsets(campaign["id"])
    else:
        recent, lifetime, adsets = [], [], []

    shown = {r["ad_name"] for r in recent}
    waiting = sorted(n for n, st in statuses.items()
                     if st in ("ACTIVE", "PENDING_REVIEW", "IN_PROCESS") and n not in shown) if campaign else []
    waiting_html = (
        '<p class="hint">מודעות פעילות שעוד אין להן נתונים בתקופה הזאת: '
        + " · ".join(escape(n) for n in waiting) + "</p>"
    ) if waiting else ""

    t = _totals(recent)
    active_sets = [a for a in adsets if a.get("effective_status") == "ACTIVE"]
    daily_budget = sum(int(a.get("daily_budget") or 0) for a in active_sets) / 100
    budget_note = "<br>".join(
        f"{escape(a['name'].removesuffix(' - Ad Set'))}: ₪{int(a.get('daily_budget') or 0) / 100:,.0f}"
        for a in active_sets) or "אין קבוצות פעילות"

    chart_rows = [r for r in lifetime if r["visits"]]
    # קנה המידה נקבע רק לפי מודעות עם מדגם מספיק - אחרת מודעה של ₪5 ועוקב אחד "מנפחת" את הגרף
    max_f = max((r["follows_per_100"] for r in chart_rows if r["follows"] >= SMALL_SAMPLE_FOLLOWS),
                default=0) or max((r["follows_per_100"] for r in chart_rows), default=0) or 1

    def _bar_text(r: dict) -> str:
        if not r["follows"]:
            return f"0 עוקבים על ₪{r['spend']:,.0f} ({r['visits']:,} ביקורים)"
        return f"{r['follows_per_100']:.1f} עוקבים ל-₪100 · עלות לעוקב {_money(r['cpf'])}"
    bars_html = "\n".join(f"""
      <div class="bar-row">
        <div class="bar-label"><span class="bar-name">{escape(r['ad_name'])}</span>{_badges_html(r)}</div>
        <div class="bar-track" title="{r['follows']} עוקבים על ₪{r['spend']:,.0f} ({r['visits']:,} ביקורים)">
          <div class="bar-fill {'zero' if not r['follows'] else ('small' if r['follows'] < SMALL_SAMPLE_FOLLOWS else '')}" style="width:{min(max(r['follows_per_100'] / max_f * 100, 2), 100):.1f}%"></div>
          <span class="bar-value">{_bar_text(r)}</span>
        </div>
      </div>""" for r in chart_rows)

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ביצועי קמפיין Instagram - עוקבים</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0e1016; --card: #171a23; --ink: #e9ebf1; --muted: #8c93a4; --border: #262b38;
    --brand: #6366f1; --brand-2: #22d3ee; --green: #34d399; --green-soft: #113328;
    --red: #f87171; --red-soft: #3a1818; --radius: 16px;
    --shadow: 0 1px 2px rgba(0,0,0,.3), 0 8px 24px -12px rgba(0,0,0,.55);
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: 'Heebo', 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--ink);
         padding: 28px clamp(16px, 4vw, 48px) 60px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  .sub {{ color: var(--muted); font-size: 13px; margin: 0 0 24px; line-height: 1.6; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin-bottom: 26px; }}
  .kpi {{ background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow); padding: 16px 18px; }}
  .kpi .value {{ font-size: 22px; font-weight: 800; font-variant-numeric: tabular-nums; }}
  .kpi .label {{ font-size: 12px; color: var(--muted); margin-top: 4px; line-height: 1.5; }}
  .kpi.hl .value {{ color: var(--green); }}
  .card {{ background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow); padding: 20px 22px; margin-bottom: 22px; }}
  .card h2 {{ font-size: 15px; margin: 0 0 6px; }}
  .card .hint {{ color: var(--muted); font-size: 12.5px; margin: 0 0 16px; line-height: 1.6; }}
  .bar-row {{ margin-bottom: 14px; }}
  .bar-label {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 5px; font-size: 13px; }}
  .bar-name {{ font-weight: 600; }}
  .bar-track {{ position: relative; height: 24px; background: #1b1f29; border-radius: 6px; }}
  .bar-fill {{ height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--brand), var(--brand-2)); }}
  .bar-fill.zero {{ background: var(--red-soft); }}
  .bar-fill.small {{ opacity: .45; }}
  .bar-value {{ position: absolute; top: 50%; transform: translateY(-50%); left: 8px; font-size: 11.5px; font-weight: 700; white-space: nowrap; }}
  .badge {{ font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }}
  .badge.st-win, .badge.st-ACTIVE {{ background: var(--green-soft); color: var(--green); }}
  .badge.st-lose {{ background: var(--red-soft); color: var(--red); }}
  .badge.st-other {{ background: #262b38; color: var(--muted); }}
  .tw {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; min-width: 760px; }}
  thead th {{ text-align: right; padding: 10px 8px; background: #1b1f29; color: var(--muted); font-weight: 600; font-size: 12px; border-bottom: 1px solid var(--border); }}
  tbody td {{ padding: 10px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tbody tr:hover {{ background: rgba(255,255,255,.03); }}
  td .nm {{ font-weight: 600; }} td .bdg {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }}
  td.strong {{ font-weight: 800; }}
  .empty {{ color: var(--muted); text-align: center; padding: 30px; }}
  footer {{ margin-top: 20px; font-size: 12px; color: var(--muted); line-height: 1.7; }}
</style>
</head>
<body>

<h1>ביצועי קמפיין Instagram - עוקבים</h1>
<p class="sub">עודכן לאחרונה: {now_str} · קמפיין: {escape(config.CAMPAIGN_NAME.strip(RLM_LRM_CHARS))} · יעד: {config.DESTINATION_URL}</p>

<div class="kpis">
  <div class="kpi"><div class="value">₪{t['spend']:,.0f}</div><div class="label">הוצאה · {recent_label}</div></div>
  <div class="kpi"><div class="value">{t['visits']:,}</div><div class="label">ביקורים בפרופיל · {recent_label}</div></div>
  <div class="kpi hl"><div class="value">{t['follows']:,}</div><div class="label">עוקבים · {recent_label}</div></div>
  <div class="kpi"><div class="value">₪{daily_budget:,.0f}</div><div class="label">תקציב יומי כולל של כל הקבוצות הפעילות (לא לכל מודעה)<br>{budget_note}</div></div>
</div>

<div class="card">
  <h2>איזו מודעה מביאה הכי הרבה עוקבים לכל שקל</h2>
  <p class="hint">מאז תחילת הקמפיין (יותר נתונים, פחות רעש). פס ארוך יותר = יותר עוקבים לכל ₪100. פס אדום = מודעה שהוציאה כסף ולא הביאה אף עוקב. פס חיוור = פחות מ-{SMALL_SAMPLE_FOLLOWS} עוקבים, מוקדם מדי לשפוט.</p>
  {bars_html if chart_rows else '<div class="empty">אין עדיין נתונים.</div>'}
</div>

<div class="card">
  <h2>טבלה · {recent_label}</h2>
  <p class="hint">מדורג לפי עלות לעוקב (זול למעלה). מודעה עם הרבה ביקורים ואפס עוקבים מביאה תנועה שלא ממירה.</p>
  <div class="tw"><table>
    <thead><tr><th>מודעה</th><th>סטטוס</th><th>הוצאה</th><th>ביקורים בפרופיל</th><th>עלות לביקור</th><th>עוקבים</th><th>% המרה לעוקב</th><th>עלות לעוקב</th><th>הודעות בפרטי</th></tr></thead>
    <tbody>{_table(recent)}</tbody>
  </table></div>
  {waiting_html}
</div>

<div class="card">
  <h2>טבלה · מאז תחילת הקמפיין</h2>
  <div class="tw"><table>
    <thead><tr><th>מודעה</th><th>סטטוס</th><th>הוצאה</th><th>ביקורים בפרופיל</th><th>עלות לביקור</th><th>עוקבים</th><th>% המרה לעוקב</th><th>עלות לעוקב</th><th>הודעות בפרטי</th></tr></thead>
    <tbody>{_table(lifetime)}</tbody>
  </table></div>
</div>

<footer>
  "עוקבים" = המדד "Follows or likes" של Meta. "ביקורים בפרופיל" = התוצאה שהקמפיין ממוטב אליה.
  מודעות שמופיעות גם בקבוצה הישנה וגם בקבוצה המאוחדת מאוחדות לשורה אחת. קידומים שנעשו מכפתור "קידום"
  באפליקציית אינסטגרם לא כלולים. נוצר אוטומטית ע"י ig_traffic_campaign/dashboard.py - קריאה בלבד, לא נוגע בשום מודעה.
</footer>

</body>
</html>"""

    Path(config.PERFORMANCE_DASHBOARD_FILE).write_text(html, encoding="utf-8")
    return config.PERFORMANCE_DASHBOARD_FILE


if __name__ == "__main__":
    path = generate_dashboard()
    print(f"performance_dashboard.html נוצר: {path}")
