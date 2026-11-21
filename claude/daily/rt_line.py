# ב115 (21.11): שורה לסיכום היומי - הניתוב החדש של go.html, rt_2111 (80% a5v6, 20% a5v7, מ-21.11 12:34).
# לכל דף ובסה"כ, אתמול ומצטבר מ-21.11 12:34: מבקרים (מכשירים), לחיצות קנייה (מבקרים שלחצו), הגיעו לסליקה, רכישות מאומתות.
# וגם: גרסת הסליקה (צפוי b2), וחלק התנועה של a5v6 (צפוי בערך 80%).
# אותם כללים כמו daily_0811.py ו-w40_line.py: בלי בדיקות פנימיות, בלי סריקות של Meta, עסקה אחת פעם אחת.
# ("מאשר לתזמן" + בקשת יהב 21.11): חלק מהסיכום היומי מ-22.11.
# שימוש: python3 rt_line.py <json של הגיליון> "<עכשיו YYYY-MM-DD HH:MM>"
import json, base64, re, sys, urllib.parse as up
from datetime import datetime, timedelta
from collections import defaultdict
EXP, START, ARMS = "rt_2111", datetime(2026, 11, 21, 12, 34), ("a5v6", "a5v7")
o = json.load(open(sys.argv[1])); c = o["content"]
try: t = base64.b64decode(c).decode()
except Exception: t = c
t = t.replace("\r", "")
NOW = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M"); Y = (NOW - timedelta(days=1)).date()
COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R = []
for l in t.split("\n")[1:]:
    a = l.split("\t")
    if len(a) < 5: continue
    r = dict(zip(COLS, a + [""] * (21 - len(a))))
    try: r["t"] = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
    except Exception: continue
    R.append(r)
TEST_DEALS = ("267429750", "270060105", "265594626")
def isTest(r):
    q = (r["qs"] or "").lower()
    return bool(re.search("claude|test|nocache", q)) or bool(re.search(r"(^|;)int=1(;|$)", r["x"] or "")) or r["variant"] == "test" \
        or bool(re.search("בדיקה|בדיקת", r["name"] or "")) or any(d in (r["qs"] or "") for d in TEST_DEALS)
TV = {r["vid"] for r in R if r["vid"] and isTest(r)} | {"77438727"}
# ביקורים: כל sid שהאירוע הראשון שלו (לא סריקה) הוא view של a5v6/a5v7 עם exp=rt_2111
S = {}
for r in R:
    if r["t"] < START or not r["sid"] or r["ev"].startswith("meta_scan") or isTest(r) or r["vid"] in TV: continue
    s = S.get(r["sid"])
    if s is None:
        if r["ev"] != "view": continue
        p = up.parse_qs(r["qs"])
        if (p.get("exp") or [""])[0] != EXP or r["variant"] not in ARMS: S[r["sid"]] = False; continue
        s = S[r["sid"]] = {"t": r["t"], "vid": r["vid"] or r["sid"], "v": r["variant"], "cta": 0, "chk": 0, "co": "", "buy": 0}
    if s is False: continue
    if r["ev"] == "cta_click": s["cta"] = 1
    if r["ev"].startswith("checkout_"):
        s["chk"] = 1; x = dict(kv.split("=", 1) for kv in (r["x"] or "").split(";") if "=" in kv); s["co"] = s["co"] or x.get("co", "")
S = {k: v for k, v in S.items() if v}
seen = set()
for r in R:
    if r["ev"] == "purchase" and r["cta"] in ("cardcom_webhook", "cardcom_page_webhook", "manual_bank_transfer") and r["t"] >= START and r["sid"] in S:
        if re.search(r"(^|;)int=1(;|$)", r["x"] or ""): continue
        m = re.search(r"deal\s+(\S+)", r["qs"]); d = m.group(1) if m else r["sid"]
        if d in seen or d in TEST_DEALS: continue
        seen.add(d); S[r["sid"]]["buy"] = 1; S[r["sid"]]["buyday"] = r["t"].date()
def agg(v, only_y):
    P = defaultdict(lambda: {"cta": 0, "chk": 0})
    for s in S.values():
        if (v and s["v"] != v) or (only_y and s["t"].date() != Y): continue
        P[s["vid"]]["cta"] |= s["cta"]; P[s["vid"]]["chk"] |= s["chk"]
    buys = sum(1 for s in S.values() if s["buy"] and (not v or s["v"] == v) and (not only_y or s.get("buyday") == Y))
    return len(P), sum(o["cta"] for o in P.values()), sum(o["chk"] for o in P.values()), buys
def line(lab, a): return "%s: מבקרים %d, לחצו על קנייה %d, הגיעו לסליקה %d, רכישות %d" % ((lab,) + a)
print("b115 rt_2111 (go.html 80%% a5v6 / 20%% a5v7, from 21.11 12:34), by device")
for lab, only_y in (("אתמול (%s)" % Y.strftime("%d.%m"), True), ("מצטבר מ-21.11 12:34", False)):
    for v in ARMS: print(line(v + " " + lab, agg(v, only_y)))
    print(line("סה\"כ " + lab, agg(None, only_y)))
n6, n7 = agg("a5v6", False)[0], agg("a5v7", False)[0]
if n6 + n7: print("חלק a5v6 מהמבקרים: %.0f%% (צפוי בערך 80%%)" % (100.0 * n6 / (n6 + n7)))
co = defaultdict(int)
for s in S.values():
    if s["chk"]: co[(s["v"], s["co"] or "?")] += 1
if co: print("checkout version (expected b2):", {"%s->%s" % k: n for k, n in co.items()})
