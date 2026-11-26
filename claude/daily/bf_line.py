# ב127.2 (26.11): שורה לסיכום היומי - בלאק פריידיי. כניסות (מכשירים) ורכישות עם utm_campaign=bf_2611 (מיילים וסטוריז), אתמול ומצטבר מ-26.11,
# וכל הרכישות האמיתיות בתקופה 26.11 00:00 - 30.11 23:59 (שעון ישראל), לפי דף ומקור. בלי פרטים אישיים ובלי מספרי עסקה.
# שימוש: python3 bf_line.py <ev.json> "<עכשיו YYYY-MM-DD HH:MM>"
import json, re, sys, collections
from datetime import datetime, timedelta
from urllib.parse import parse_qs
T = json.load(open(sys.argv[1], encoding="utf8"))["content"].split("\n")
NOW = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M"); Y = (NOW - timedelta(days=1)).date()
START, END = datetime(2026, 11, 26, 0, 0), datetime(2026, 11, 30, 23, 59, 59)
H = T[0].split("\t"); ix = {h: i for i, h in enumerate(H)}
def g(r, k):
    i = ix.get(k); return r[i] if i is not None and len(r) > i else ""
TEST_DEALS = ("267429750", "270060105", "265594626")
def is_test(r):
    q = g(r, "qs").lower(); x = g(r, "x") or ""
    return bool(re.search(r"claude|test|nocache", q)) or bool(re.search(r"(^|;)int=1(;|$)", x)) or "בדיקה" in (g(r, "name") or "") or any(d in q for d in TEST_DEALS)
rows = []
for line in T[1:]:
    if not line: continue
    r = line.split("\t")
    try: t = datetime.strptime(g(r, "ts")[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError: continue
    if t < START or t > END or g(r, "ev").startswith("meta_scan") or is_test(r): continue
    rows.append((t, r))
def camp(r): return (parse_qs(g(r, "qs")).get("utm_campaign") or [""])[0].lower().strip()
bf = [(t, r) for t, r in rows if camp(r) == "bf_2611"]
def dev(items, only_y=False):
    return len({g(r, "vid") or g(r, "sid") for t, r in items if g(r, "ev") == "view" and (not only_y or t.date() == Y)})
PUR = ("cardcom_webhook", "cardcom_page_webhook", "manual_bank_transfer")
def buys(items, only_y=False):
    return [(t, r) for t, r in items if g(r, "ev") == "purchase" and g(r, "cta") in PUR and (not only_y or t.date() == Y)]
# רכישות בתקופה: גם אם שורת ה-purchase בלי utm (ב-purchase ה-qs הוא של קארדקום) - משייכים לפי sid לכניסה עם bf_2611
bf_sids = {g(r, "sid") for t, r in bf if g(r, "sid")}
all_buys = buys(rows); bf_buys = [(t, r) for t, r in all_buys if g(r, "sid") in bf_sids or camp(r) == "bf_2611"]
print("בלאק פריידיי (bf_2611, 26.11 - 30.11 23:59), לפי מכשיר")
print("bf_2611 אתמול (%s): כניסות %d, רכישות %d" % (Y.strftime("%d.%m"), dev(bf, True), len([1 for t, r in bf_buys if t.date() == Y])))
print("bf_2611 מצטבר מ-26.11: כניסות %d, רכישות %d" % (dev(bf), len(bf_buys)))
by = collections.Counter((g(r, "variant") or "-") for t, r in all_buys)
src = collections.Counter()
for t, r in all_buys:
    q = g(r, "qs").lower(); a = re.search(r"\baff\s+([a-z0-9_-]+)", q)
    src["משווק " + a.group(1)] += 1 if a else 0
    if not a: src["בן / אחר"] += 1
print("כל הרכישות האמיתיות בתקופה: %d%s%s" % (len(all_buys), (" | לפי דף: " + ", ".join("%s %d" % kv for kv in by.most_common())) if all_buys else "", (" | לפי מקור: " + ", ".join("%s %d" % kv for kv in src.most_common() if kv[1])) if all_buys else ""))
