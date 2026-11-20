# פ3 (20.11): שורת אפסייל לסיכום היומי. האפסייל ב-97 ₪ באוויר מ-14.11 19:02 (ב74).
# רכישות: שורות ev=upsell_purchase, cta=cardcom_upsell_webhook בגיליון האירועים (8463714), עסקה אחת פעם אחת, בלי בדיקות.
# קודים: API של הדשבורד action=upsell (251557, בלי הקוד עצמו): הונפקו, נוצלו, נדחו, פגו, בתוקף. בלי קודי בדיקה.
# בלי פרטים אישיים ובלי מספרי עסקה בפלט.
# שימוש: python3 upsell_line.py <json של הגיליון> <upsell.tsv או -> "<עכשיו YYYY-MM-DD HH:MM>"
import json, base64, re, sys
from datetime import datetime, timedelta
LAUNCH = datetime(2026, 11, 14, 19, 2)
TEST_DEALS = ("267429750", "270060105", "265594626")
o = json.load(open(sys.argv[1])); c = o["content"]
try: t = base64.b64decode(c).decode()
except Exception: t = c
NOW = datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M"); Y = (NOW - timedelta(days=1)).date()
COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
def is_test_text(s): return bool(re.search(r"test|claude|e2e|nocache|בדיקה|בדיקת", s or "", re.I))
buys = {}
for l in t.replace("\r", "").split("\n")[1:]:
    a = l.split("\t")
    if len(a) < 5: continue
    r = dict(zip(COLS, a + [""] * 21))
    if r["ev"] != "upsell_purchase" or r["cta"] != "cardcom_upsell_webhook": continue
    try: ts = datetime.strptime(r["ts"], "%Y-%m-%d %H:%M:%S")
    except Exception: continue
    if is_test_text(r["qs"]) or is_test_text(r["name"]) or re.search(r"(^|;)int=1(;|$)", r["x"]) or any(d in r["qs"] for d in TEST_DEALS): continue
    m = re.search(r"\|\s*deal\s+(\S+)", r["qs"]); d = m.group(1) if m else r["sid"]
    if d not in buys: buys[d] = {"t": ts, "aff": "aff=" in r["x"]}
yb = [b for b in buys.values() if b["t"].date() == Y]
tot = len(buys)
line1 = "אפסייל 97 ₪ (מ-14.11): אתמול %d רכישות (%d ₪), מצטבר %d רכישות (%d ₪)%s." % (len(yb), 97 * len(yb), tot, 97 * tot,
        ("; מתוכן %d עם משווק" % sum(1 for b in buys.values() if b["aff"])) if tot else "")
print(line1)
if sys.argv[2] != "-":
    L = open(sys.argv[2], encoding="utf-8").read().replace("\r", "").split("\n")
    h = [x.strip().lower() for x in (L[0].split("\t") if L else [])]
    if h and h[0] == "upsell":
        h = h[1:]; st = {"issued": 0, "used": 0, "declined": 0, "expired": 0, "open": 0}; sty = dict(st)
        for l in L[1:]:
            if not l.strip(): continue
            r = dict(zip(h, l.split("\t")))
            if r.get("test", "").lower() == "true" or is_test_text(r.get("deal", "")) or r.get("deal", "") in TEST_DEALS: continue
            try: cr = datetime.strptime(r.get("created", "")[:19], "%Y-%m-%d %H:%M:%S"); ex = datetime.strptime(r.get("expires", "")[:19], "%Y-%m-%d %H:%M:%S")
            except Exception: continue
            k = "used" if r.get("used", "").lower() == "true" else "declined" if r.get("declined", "").lower() == "true" else "expired" if ex < NOW else "open"
            for S, ok in ((st, cr >= LAUNCH), (sty, cr.date() == Y)):
                if ok: S["issued"] += 1; S[k] += 1
        f = lambda S: "הונפקו %d, נוצלו %d, נדחו %d, פגו בלי החלטה %d, בתוקף %d" % (S["issued"], S["used"], S["declined"], S["expired"], S["open"])
        print("קודים: אתמול - %s. מצטבר - %s." % (f(sty), f(st)))
    else:
        print("קודים: לא נקראו (הקובץ לא בפורמט של action=upsell).")
