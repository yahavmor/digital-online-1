# ב112 (19.11): שורה לסיכום היומי - הקמפיין החדש של בן לדף הקצר (utm_campaign=lenatzeach_w40, בלי aff, a5s).
# לכל מודעה (w1_ben, w2_ben, ומודעה חדשה אם תופיע) ובסה"כ: אתמול ומצטבר מ-19.11.
# הוצאה (מטופס ההוצאה, מפתח <תאריך>|<utm_content>), אנשים (מכשירים), הגיעו לסליקה, רכישות מאומתות,
# עלות להגעה לסליקה ועלות למכירה מול היעד של בן (עד 450 ₪ למכירה, עד סוף דצמבר; "יציב" = בערך מכירה בשבוע).
# אותם כללים כמו daily_0811.py ו-ben_line.py: בלי בדיקות פנימיות, בלי סריקות של Meta, עסקה אחת פעם אחת.
# שימוש: python3 w40_line.py <json של הגיליון> <spend.tsv> "<עכשיו YYYY-MM-DD HH:MM>"
import json, base64, re, sys, urllib.parse as up
from datetime import datetime, timedelta
from collections import defaultdict
CAMP, START, TARGET = "lenatzeach_w40", datetime(2026, 11, 19), 450
o = json.load(open(sys.argv[1])); c = o["content"]
try: t = base64.b64decode(c).decode()
except Exception: t = c
t = t.replace("\r", "")
NOW = datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M"); Y = (NOW - timedelta(days=1)).date()
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
# ביקורים: כל sid שהאירוע הראשון שלו (לא סריקה) הוא view של הקמפיין, בלי aff
S = {}
for r in R:
    if r["t"] < START or not r["sid"] or r["ev"].startswith("meta_scan") or isTest(r) or r["vid"] in TV: continue
    s = S.get(r["sid"])
    if s is None:
        if r["ev"] != "view": continue
        p = up.parse_qs(r["qs"]); camp = (p.get("utm_campaign") or [""])[0]
        aff = (p.get("aff") or [""])[0] or ("aff=" in (r["x"] or "")) or (p.get("utm_medium") or [""])[0].lower() == "affiliate"
        if camp != CAMP or aff: S[r["sid"]] = False; continue
        s = S[r["sid"]] = {"t": r["t"], "vid": r["vid"], "uc": (p.get("utm_content") or ["-"])[0] or "-", "v": r["variant"], "chk": 0, "co": "", "buy": 0}
    if s is False: continue
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
# הוצאה מטופס ההוצאה: <תאריך>|<utm_content>
SP = defaultdict(float)
for l in open(sys.argv[2], encoding="utf-8").read().split("\n")[1:]:
    a = l.split("\t")
    if len(a) < 2 or "|" not in a[0]: continue
    d, k = a[0].split("|", 1)
    try: dd = datetime.strptime(d, "%Y-%m-%d").date(); amt = float(a[1])
    except Exception: continue
    if dd >= START.date(): SP[(dd, k)] += amt
ads = sorted({s["uc"] for s in S.values()} | {k for (_, k) in SP if re.match(r"w\d+_ben$", k)})
def agg(uc, only_y):
    ss = [s for s in S.values() if (uc is None or s["uc"] == uc) and (not only_y or s["t"].date() == Y)]
    ppl = len({s["vid"] or s["t"].isoformat() for s in ss}); chk = len({s["vid"] or s["t"].isoformat() for s in ss if s["chk"]})
    buys = sum(1 for s in S.values() if s["buy"] and (uc is None or s["uc"] == uc) and (not only_y or s.get("buyday") == Y))
    sp = sum(v for (d, k), v in SP.items() if (k == uc if uc else k in ads) and (not only_y or d == Y))
    has_sp = any((k == uc if uc else k in ads) and (not only_y or d == Y) for (d, k) in SP)
    return ppl, chk, buys, (sp if has_sp else None)
f = lambda v: "%.0f ₪" % v
def line(lab, a):
    ppl, chk, buys, sp = a
    cpc = (f(sp / chk) if chk else "אין הגעות") if sp is not None else "-"
    cps = (f(sp / buys) + (" (עד היעד)" if sp / buys <= TARGET else " (מעל היעד)") if buys else ("אין מכירה" + (", הוצאה עד עכשיו %s מתוך %d" % (f(sp), TARGET) if sp else ""))) if sp is not None else "-"
    return "%s: הוצאה %s, אנשים %d, הגיעו לסליקה %d, רכישות %d, עלות להגעה לסליקה %s, עלות למכירה %s" % (lab, f(sp) if sp is not None else "אין במאגר", ppl, chk, buys, cpc, cps)
print("b112 lenatzeach_w40 (Ben -> a5s), by device; target: sale up to %d ILS" % TARGET)
if not S and not any(k in ads for (_, k) in SP):
    print("עוד אין כניסות ואין הוצאה מהקמפיין (מאז 19.11).")
for uc in ads:
    print(line(uc + " אתמול (%s)" % Y.strftime("%d.%m"), agg(uc, True)))
    print(line(uc + " מצטבר מ-19.11", agg(uc, False)))
if ads:
    print(line("סה\"כ אתמול", agg(None, True))); print(line("סה\"כ מצטבר מ-19.11", agg(None, False)))
co = defaultdict(int)
for s in S.values():
    if s["chk"]: co[s["co"] or "?"] += 1
if co: print("checkout version (expected b2):", dict(co))
