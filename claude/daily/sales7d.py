# "מה מוכר" (ראשי 14.11): רכישות מאומתות ב-7 הימים האחרונים לפי קמפיין ולפי מודעה, לפי הכניסה הראשונה של אותו sid,
# עם ההוצאה לפי מודעה מהמאגר (210972) כשיש.
# שימוש: python3 sales7d.py <json מ-download_file_content> "<עד YYYY-MM-DD HH:MM>" [spend.tsv]
#  - spend.tsv: הפלט של API הדשבורד action=spend (שורה ראשונה "spend", ואחריה key<TAB>amount). בלי הקובץ - "לא נטען".
#  - רכישה מאומתת: ev=purchase עם cta cardcom_webhook / cardcom_page_webhook / manual_bank_transfer, פעם אחת לכל עסקה,
#    בלי עסקאות הבדיקה (267429750, 270060105) ובלי שורות בדיקה (int=1, claude/test/nocache ב-qs).
#  - שיוך: הכניסה הראשונה (האירוע המוקדם ביותר) של ה-sid של שורת הרכישה. ממנה utm_campaign, utm_content ו-aff.
#    אם ל-sid אין אירועים (למשל העברה בנקאית) - "לא ידוע".
#  - הוצאה למודעה: סכום המפתחות "תאריך|<utm_content>" בחלון של 7 הימים (הוצאה לפי מודעה של בן ושל יוסף).
#    למשווקים בלי הוצאה לפי מודעה - ההוצאה של המשווק בחלון (aff_<קוד> ו-aff_<קוד>_*), בשורה נפרדת. בלי הוצאה לקמפיין (אין במאגר).
import json, base64, re, sys, urllib.parse as up
from datetime import datetime, timedelta
from collections import defaultdict
o = json.load(open(sys.argv[1])); c = o["content"]
try: t = base64.b64decode(c).decode()
except Exception: t = c
END = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M"); START = END - timedelta(days=7)
SPF = sys.argv[3] if len(sys.argv) > 3 else None
TEST_DEALS = ("267429750", "270060105")
COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
def is_test(r):
    return bool(re.search("claude|test|nocache", (r["qs"] or "").lower())) or bool(re.search(r"(^|;)int=1(;|$)", r["x"] or "")) or r["variant"] == "test"
first = {}; buys = []; seen = set()
for l in t.replace("\r", "").split("\n")[1:]:
    a = l.split("\t")
    if len(a) < 9: continue
    r = dict(zip(COLS, a + [""] * (21 - len(a))))
    try: r["t"] = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
    except Exception: continue
    if r["ev"] == "purchase":
        if r["cta"] not in ("cardcom_webhook", "cardcom_page_webhook", "manual_bank_transfer") or not (START <= r["t"] < END): continue
        if r["cta"] == "manual_bank_transfer":
            m = re.search(r"ref\s+([^\s|]+)", r["qs"]); d = "bank_" + m.group(1) if m else r["sid"]
        else:
            m = re.search(r"deal\s+(\S+)", r["qs"]); d = m.group(1) if m else r["sid"]
        if d in seen or d in TEST_DEALS: continue
        seen.add(d); am = re.search(r"(\d+(?:\.\d+)?)\s*ILS", r["qs"])
        buys.append({"t": r["t"], "sid": r["sid"], "amt": float(am.group(1)) if am else 0.0, "bank": r["cta"] == "manual_bank_transfer"})
        continue
    if not r["sid"] or r["ev"].startswith("meta_scan") or is_test(r): continue
    f = first.get(r["sid"])
    if f is None or r["t"] < f["t"]: first[r["sid"]] = r
def q(qs, k):
    m = re.search(r"(?:^|[?&])" + k + r"=([^&]*)", qs or ""); return up.unquote_plus(m.group(1)) if m else ""
for b in buys:
    f = first.get(b["sid"])
    if not f: b.update(camp="לא ידוע", ad="לא ידוע", aff="", page="", src=""); continue
    x = f["x"] or ""; m = re.search(r"(?:^|;)aff=([a-z0-9_-]+)", x)
    b.update(camp=(q(f["qs"], "utm_campaign") or "(בלי קמפיין)").replace("|", "/"), ad=(q(f["qs"], "utm_content") or "(בלי מודעה)").lower(),
             aff=(m.group(1) if m else q(f["qs"], "aff")), page=f["variant"], src=q(f["qs"], "utm_source"), first=f["t"])
# הוצאה
SP = None; SPD = defaultdict(set); SPDAY = defaultdict(float); NDAYS = (END.date() - START.date()).days + 1
if SPF:
    SP = defaultdict(float)
    for l in open(SPF, encoding="utf8").read().replace("\r", "").split("\n")[1:]:
        a = l.split("\t")
        if len(a) < 2 or "|" not in a[0]: continue
        dd, code = a[0].strip().split("|", 1)
        try: dt = datetime.strptime(dd, "%Y-%m-%d")
        except Exception: continue
        if START.date() <= dt.date() < END.date() + timedelta(days=1):
            try: SP[code.strip().lower()] += float(a[1]); SPD[code.strip().lower()].add(dd); SPDAY[(dd, code.strip().lower())] += float(a[1])
            except Exception: pass
def fmt(v): return ("%.0f" % v) if v is not None else "-"
print("sales7d window %s - %s (Israel time), verified purchases %d, revenue %s ILS" % (START.strftime("%d.%m %H:%M"), END.strftime("%d.%m %H:%M"), len(buys), fmt(sum(b["amt"] for b in buys))))
if not buys: print("sales7d: אין רכישות מאומתות בחלון"); sys.exit(0)
print("\n-- לפי קמפיין (הכניסה הראשונה של ה-sid) --")
C = defaultdict(list)
for b in buys: C[b["camp"]].append(b)
for k, L in sorted(C.items(), key=lambda kv: -len(kv[1])):
    print("camp | %s | purchases %d | revenue %s" % (k, len(L), fmt(sum(b["amt"] for b in L))))
print("\n-- לפי מודעה (utm_content) --")
# מודעה של משווק נספרת בנפרד מאותה מודעה אצל בן: ההוצאה לפי מודעה במאגר היא של בן (או של משווק כשהקוד שלו בשם, כמו p25_yosef),
# ולמשווק שהמודעה לא שלו בשם - ההוצאה רק ברמת המשווק (בטבלה הבאה)
A = defaultdict(list)
for b in buys: A[(b["ad"], b["aff"])].append(b)
for (k, af), L in sorted(A.items(), key=lambda kv: -len(kv[1])):
    own = (not af) or (af in k)
    sp = SP.get(k) if (SP is not None and own and k in SP) else None
    if SP is None: spt = "לא נטען"
    elif not own: spt = "אצל המשווק (למטה)"
    elif sp is None: spt = "אין במאגר"
    else: spt = "%s (%d/%d ימים עם הוצאה)" % (fmt(sp), len(SPD[k]), NDAYS)
    cpa = fmt(sp / len(L)) if sp is not None else "-"
    camps = sorted({b["camp"] for b in L})
    print("ad | %s%s | purchases %d | revenue %s | spend 7d %s | cost/purchase %s | campaigns %s" % (k, (" · aff " + af) if af else "", len(L), fmt(sum(b["amt"] for b in L)), spt, cpa, ",".join(camps)))
AF = sorted({b["aff"] for b in buys if b["aff"]})
if AF:
    print("\n-- משווקים (הוצאה כוללת בחלון, כשאין לפי מודעה) --")
    for a in AF:
        L = [b for b in buys if b["aff"] == a]
        if SP is None: print("aff | %s | purchases %d | spend 7d לא נטען" % (a, len(L))); continue
        # כמו בדשבורד (ב86): ביום עם הוצאה לפי מודעה של המשווק (קוד שמכיל את שמו, כמו p25_yosef) - סכום המודעות; אחרת aff_<קוד>*
        days = {dd for (dd, k) in SPDAY}; tot = 0.0; nd = 0
        for dd in days:
            ad = sum(v for (d2, k), v in SPDAY.items() if d2 == dd and a in k and not k.startswith("aff_"))
            af = sum(v for (d2, k), v in SPDAY.items() if d2 == dd and (k == "aff_" + a or k.startswith("aff_" + a + "_")))
            has = any(d2 == dd and a in k for (d2, k) in SPDAY)
            v = ad if any(d2 == dd and a in k and not k.startswith("aff_") for (d2, k) in SPDAY) else af
            if has: nd += 1
            tot += v
        print("aff | %s | purchases %d | spend 7d %s (%d/%d ימים)" % (a, len(L), fmt(tot), nd, NDAYS))
print("\n-- רכישות (בלי פרטים אישיים) --")
for b in sorted(buys, key=lambda b: b["t"]):
    print("buy | %s | %s | page %s | camp %s | ad %s%s" % (b["t"].strftime("%d.%m %H:%M"), "bank" if b["bank"] else "card", b.get("page") or "-", b["camp"], b["ad"], (" | aff " + b["aff"]) if b["aff"] else ""))
