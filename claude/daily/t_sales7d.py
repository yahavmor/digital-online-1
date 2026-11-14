# בדיקה ל-sales7d.py על נתונים מדומים: שיוך לפי הכניסה הראשונה, עסקת בדיקה, כפילות עסקה, העברה בנקאית בלי אירועים,
# מודעה של משווק בשמו (p25_yosef) מול מודעה משותפת (p25_brain_c2 אצל אמיר), ומחוץ לחלון.
# שימוש: python3 t_sales7d.py <sales7d.py>
import json, subprocess, sys, tempfile, os
d = tempfile.mkdtemp()
def row(t, ev, v, sid, qs="", x="", cta=""):
    a = [""] * 21; a[0] = t; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[13] = cta; a[20] = x; return "\t".join(a)
R = ["header",
 row("2026-11-10 09:00:00", "view", "a5v6", "s1", "utm_campaign=lenatzeach_cold&utm_content=P25"),
 row("2026-11-10 09:05:00", "view", "a5v6", "s1", "utm_campaign=OTHER&utm_content=other"),   # לא הראשונה
 row("2026-11-10 09:10:00", "purchase", "a5v6", "s1", "cardcom | 297 ILS | deal 1001 | src ", cta="cardcom_webhook"),
 row("2026-11-10 09:11:00", "purchase", "a5v6", "s1", "cardcom | 297 ILS | deal 1001 | src ", cta="cardcom_page_webhook"),  # כפילות
 row("2026-11-11 10:00:00", "view", "pr2", "s2", "utm_campaign=NLP+%7C+Aff+amir&utm_content=p25_brain_c2&aff=amir", x="aff=amir"),
 row("2026-11-11 10:20:00", "purchase", "pr2", "s2", "cardcom | 297 ILS | deal 1002 | src ", cta="cardcom_webhook"),
 row("2026-11-12 10:00:00", "view", "a5v6", "s3", "utm_campaign=yosef_c&utm_content=p25_yosef&aff=yosef", x="aff=yosef"),
 row("2026-11-12 10:20:00", "purchase", "a5v6", "s3", "cardcom | 297 ILS | deal 1003 | src ", cta="cardcom_webhook"),
 row("2026-11-12 11:00:00", "purchase", "a", "s4", "cardcom | 297 ILS | deal 270060105 | src ", cta="cardcom_webhook"),  # בדיקה
 row("2026-11-12 12:00:00", "purchase", "a", "bank_x", "bank | 297 ILS | ref R1", cta="manual_bank_transfer"),          # בלי אירועים
 row("2026-11-01 10:00:00", "purchase", "a", "s5", "cardcom | 297 ILS | deal 999 | src ", cta="cardcom_webhook"),       # מחוץ לחלון
 row("2026-11-12 13:00:00", "view", "a5v6", "s6", "utm_content=p25&claude=1"),                                         # בדיקה - לא נספר כראשונה
]
json.dump({"content": "\n".join(R)}, open(d + "/ev.json", "w"))
open(d + "/sp.tsv", "w").write("spend\n2026-11-10|p25\t10\n2026-11-11|p25\t20\n2026-11-11|p25_brain_c2\t50\n2026-11-11|aff_amir_ic\t30\n2026-11-12|aff_amir_ic\t40\n2026-11-12|p25_yosef\t7\n2026-11-12|aff_yosef\t5\n2026-11-13|aff_yosef\t4\n2026-11-01|p25\t999\n")
out = subprocess.run([sys.executable, "-I", sys.argv[1], d + "/ev.json", "2026-11-14 10:00", d + "/sp.tsv"], capture_output=True, text=True).stdout
print(out)
n = f = 0
def ok(m, c):
    global n, f; n += 1
    if not c: f += 1; print("FAIL", m)
ok("4 purchases (dedupe, test deal and out-of-window excluded)", "verified purchases 4," in out)
ok("first entry wins: lenatzeach_cold / p25", "ad | p25 | purchases 1" in out and "OTHER" not in out)
ok("p25 spend in window only (30, 2/8 days)", "spend 7d 30 (2/8" in out)
ok("amir shared ad -> spend at affiliate", "p25_brain_c2 · aff amir" in out and "אצל המשווק" in out and "aff | amir | purchases 1 | spend 7d 70 (2/8" in out)
ok("campaign decoded, pipe replaced", "camp | NLP / Aff amir |" in out)
ok("yosef own ad uses per-ad spend 7", "p25_yosef · aff yosef | purchases 1 | revenue 297 | spend 7d 7 (1/8" in out)
ok("bank without events -> unknown", "לא ידוע" in out and "| bank |" in out)
ok("yosef total = per-ad on 12.11 (7, not +5) + aff_yosef on 13.11 (4) = 11", "aff | yosef | purchases 1 | spend 7d 11 (2/8" in out)
ok("no personal data columns", "deal" not in out.split("-- רכישות")[1])
print("%d/%d" % (n - f, n)); sys.exit(1 if f else 0)
