# ב107 (בקשת בן 18.11): "שורה לבן" לסיכום היומי - תנועה מיום ליום בשפה פשוטה.
# אתמול מול שלשום ומול ממוצע 7 ימים (אתמול ו-6 הימים שלפניו): אנשים שנכנסו לדף (המודעות של בן / משווקים / חינם),
# הגיעו לדף התשלום, השאירו פרטים (checkout_details או שלב התשלום או רכישה), רכישות מאומתות.
# אותם כללים כמו daily_0811.py: אנשים = מכשירים (vid), בלי בדיקות פנימיות (int=1, claude/test/nocache, עסקאות הבדיקה), בלי סריקות של Meta.
# יום = יום תחילת הביקור (שעון ישראל, כמו בגיליון). אותה הגדרה כמו הטבלה "תנועה מיום ליום" בדשבורד.
# שימוש: python3 ben_line.py <json של הגיליון> "<עכשיו YYYY-MM-DD HH:MM>"
import json, base64, re, sys, urllib.parse as up
from datetime import datetime, timedelta
from collections import defaultdict
o = json.load(open(sys.argv[1])); c = o["content"]
try: t = base64.b64decode(c).decode()
except Exception: t = c
t = t.replace("\r", "")
NOW = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M")
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
        or bool(re.search("בדיקה|בדיקת", r["name"] or "")) or r["sid"] == "6ac363a1-80a1-4715-9964-0a72520b66fb" or any(d in (r["qs"] or "") for d in TEST_DEALS)
TV = {r["vid"] for r in R if r["vid"] and isTest(r)} | {"77438727"}
def group(p, x):
    s = (p.get("utm_source") or [""])[0].lower(); m = (p.get("utm_medium") or [""])[0].lower()
    if p.get("aff") or m == "affiliate" or "aff=" in (x or ""): return "aff"
    if re.search("meta|facebook|fb|ig|instagram", s) and re.search("paid|cpc|ads?$|social_paid|paid_social", m): return "ben"
    return "free"
A = (NOW - timedelta(days=8)).replace(hour=0, minute=0, second=0)
S = {}
for r in R:
    if r["t"] < A or not r["sid"] or r["ev"].startswith("meta_scan") or isTest(r) or r["vid"] in TV: continue
    s = S.get(r["sid"])
    if not s:
        s = S[r["sid"]] = {"t": r["t"], "vid": r["vid"], "g": None, "chk": 0, "lead": 0}
    s["t"] = min(s["t"], r["t"]); s["vid"] = s["vid"] or r["vid"]
    if s["g"] is None and r["ev"] == "view": s["g"] = group(up.parse_qs(r["qs"]), r["x"])
    e = r["ev"]
    if e.startswith("checkout_"): s["chk"] = 1
    if e in ("checkout_details", "checkout_payment_viewed"): s["lead"] = 1
for s in S.values():
    if s["g"] is None: s["g"] = "free"
# רכישות מאומתות (כמו daily_0811.py): עסקה אחת פעם אחת, בלי עסקאות בדיקה
seen = set(); BUY = []
for r in R:
    if r["ev"] == "purchase" and r["cta"] in ("cardcom_webhook", "cardcom_page_webhook", "manual_bank_transfer") and r["t"] >= A:
        if re.search(r"(^|;)int=1(;|$)", r["x"] or ""): continue
        m = re.search(r"ref\s+([^\s|]+)", r["qs"]) if r["cta"] == "manual_bank_transfer" else re.search(r"deal\s+(\S+)", r["qs"])
        d = (("bank_" if r["cta"] == "manual_bank_transfer" else "") + m.group(1)) if m else r["sid"]
        if d in seen or d in TEST_DEALS: continue
        seen.add(d); BUY.append(r)
        if r["sid"] in S: S[r["sid"]]["lead"] = 1
def day(d):
    k = d.date(); P = defaultdict(set); chk = set(); lead = set()
    for s in S.values():
        if s["t"].date() != k: continue
        w = s["vid"] or s["t"].isoformat(); P[s["g"]].add(w); P["all"].add(w)
        if s["chk"]: chk.add(w)
        if s["lead"]: lead.add(w)
    return {"ben": len(P["ben"]), "aff": len(P["aff"]), "free": len(P["free"]), "all": len(P["all"]), "chk": len(chk), "lead": len(lead),
            "buy": sum(1 for r in BUY if r["t"].date() == k)}
Y = NOW - timedelta(days=1); y = day(Y); y2 = day(NOW - timedelta(days=2))
W = [day(NOW - timedelta(days=i)) for i in range(1, 8)]; avg = {k: sum(w[k] for w in W) / 7 for k in y}
f1 = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
def cmp(v, ref):
    w = ("יותר אנשים" if v else "אותו מספר אנשים") if not ref else "יותר אנשים" if v / ref >= 1.15 else "פחות אנשים" if v / ref <= 0.85 else "בערך אותו מספר אנשים"
    return "אתמול נכנסו " + w + "."
print("b107 line for Ben (by device):")
print("אתמול (%s): %d אנשים נכנסו לדף (%d מהמודעות של בן, %d דרך משווקים, %d בחינם), %d הגיעו לדף התשלום, %d השאירו פרטים, %d רכישות."
      % (Y.strftime("%d.%m"), y["all"], y["ben"], y["aff"], y["free"], y["chk"], y["lead"], y["buy"]))
print("שלשום: %d אנשים, %d לדף התשלום, %d השאירו פרטים, %d רכישות. %s" % (y2["all"], y2["chk"], y2["lead"], y2["buy"], cmp(y["all"], y2["all"])))
print("ממוצע 7 ימים: %s אנשים ביום, %s לדף התשלום, %s השאירו פרטים, %s רכישות. %s"
      % (f1(avg["all"]), f1(avg["chk"]), f1(avg["lead"]), f1(avg["buy"]), cmp(y["all"], avg["all"])))
