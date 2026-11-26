# ב116 (22.11): שורה לסיכום היומי - הדף הקצר a5s לפי מקור, מאז הטופס של ב110 (22.11 10:32).
# מקורות: "קר" = תנועה קרה של בן דרך go.html (exp=cold_2211, מ-22.11 15:53), "נשים" = lenatzeach_w40 (ישר לדף),
# "משווקים" = aff, ומ-ב125 (26.11 10:28, כל הנתב ל-a5s) גם "חם" (הקרוסלה), "מיילים" ו"אינסטגרם"; "אחר" = כל השאר. לכל מקור, אתמול ומצטבר מ-22.11 10:32: מבקרים (מכשירים), ראו טופס (form_open),
# שלחו טופס (form_submit), עברו לתשלום (checkout_pay_redirect), רכישות מאומתות.
# ובנוסף: lenatzeach_w40 לפני הטופס (19.11 - 22.11 10:32) מול אחרי, באותם מדדים (לפני הטופס: "עברו לתשלום" = הגיעו לסליקה).
# אותם כללים כמו daily_0811.py: בלי בדיקות פנימיות, בלי סריקות של Meta, עסקה אחת פעם אחת.
# שימוש: python3 a5s_line.py <json של הגיליון> "<עכשיו YYYY-MM-DD HH:MM>"
import json, base64, re, sys, urllib.parse as up
from datetime import datetime, timedelta
from collections import defaultdict
FORM, W40 = datetime(2026, 11, 22, 10, 32), datetime(2026, 11, 19)
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
def src(p):
    med = (p.get("utm_medium") or [""])[0].lower(); camp = (p.get("utm_campaign") or [""])[0].lower().strip(); srcq = (p.get("utm_source") or [""])[0].lower()
    cont = (p.get("utm_content") or [""])[0].lower(); exp = (p.get("exp") or [""])[0]; route = (p.get("route") or [""])[0]
    if (p.get("aff") or [""])[0] or med == "affiliate": return "משווקים"
    if exp == "cold_2211" or camp == "lenatzeach_cold" or re.match(r"nlp\s*\|\s*cold\b", camp): return "קר"
    if camp == "lenatzeach_w40": return "נשים"
    # ב125 (מ-26.11 10:28 כל הנתב מגיע ל-a5s): חם = הקרוסלה (lenatzeach_lab / car4_warm_a); מיילים = utm_medium=responder/email או utm_source=email; אינסטגרם = ביו/ManyChat (route=ig_org)
    if camp == "lenatzeach_lab" or cont.startswith("car4_warm"): return "חם"
    if med in ("responder", "email") or srcq == "email": return "מיילים"
    if route == "ig_org" or (srcq in ("instagram", "ig") and med in ("bio", "dm")): return "אינסטגרם"
    return "אחר"
S = {}
for r in R:
    if r["t"] < W40 or not r["sid"] or r["ev"].startswith("meta_scan") or isTest(r) or r["vid"] in TV: continue
    s = S.get(r["sid"])
    if s is None:
        if r["ev"] != "view": continue
        if r["variant"] != "a5s": S[r["sid"]] = False; continue
        p = up.parse_qs(r["qs"])
        s = S[r["sid"]] = {"t": r["t"], "vid": r["vid"] or r["sid"], "src": src(p), "open": 0, "sub": 0, "pay": 0, "chk": 0, "buy": 0}
    if s is False: continue
    e = r["ev"]
    if e == "form_open": s["open"] = 1
    if e == "form_submit": s["sub"] = 1
    if e == "checkout_pay_redirect": s["pay"] = 1
    if e.startswith("checkout_"): s["chk"] = 1
S = {k: v for k, v in S.items() if v}
seen = set()
for r in R:
    if r["ev"] == "purchase" and r["cta"] in ("cardcom_webhook", "cardcom_page_webhook", "manual_bank_transfer") and r["sid"] in S:
        if re.search(r"(^|;)int=1(;|$)", r["x"] or ""): continue
        m = re.search(r"deal\s+(\S+)", r["qs"]); d = m.group(1) if m else r["sid"]
        if d in seen or d in TEST_DEALS: continue
        seen.add(d); S[r["sid"]]["buy"] = 1
def agg(sel):
    P = defaultdict(lambda: defaultdict(int))
    for s in S.values():
        if not sel(s): continue
        for f in ("open", "sub", "pay", "chk", "buy"): P[s["vid"]][f] |= s[f]
    return len(P), *(sum(o[f] for o in P.values()) for f in ("open", "sub", "pay", "chk", "buy"))
def line(lab, a): return "%s: מבקרים %d, ראו טופס %d, שלחו טופס %d, עברו לתשלום %d, רכישות %d" % (lab, a[0], a[1], a[2], a[3], a[5])
print("b116 a5s by source (by device), form since 22.11 10:32; cold via go.html since 22.11 15:53")
for lab, only_y in (("אתמול (%s)" % Y.strftime("%d.%m"), True), ("מצטבר מ-22.11 10:32", False)):
    for sname in ("קר", "נשים", "משווקים", "חם", "מיילים", "אינסטגרם", "אחר"):
        print(line("%s %s" % (sname, lab), agg(lambda s: s["t"] >= FORM and s["src"] == sname and (not only_y or s["t"].date() == Y))))
b = agg(lambda s: s["t"] < FORM and s["src"] == "נשים"); a = agg(lambda s: s["t"] >= FORM and s["src"] == "נשים")
print("נשים (lenatzeach_w40) לפני הטופס (19.11 - 22.11 10:32): מבקרים %d, הגיעו לסליקה %d, רכישות %d" % (b[0], b[4], b[5]))
print(line("נשים (lenatzeach_w40) אחרי הטופס (מ-22.11 10:32)", a))
