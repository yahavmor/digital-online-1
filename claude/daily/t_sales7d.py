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
 row("2026-11-12 13:00:00", "view", "a5v6", "s6", "utm_content=p25&claude=1"),
 row("2026-11-12 16:26:30", "view", "a5v6", "s10", "utm_campaign=x&utm_content=p25&fbclid=IwAR1tnpw6glbrf"),   # utm_campaign=x - בדיקה
 row("2026-11-12 16:30:00", "view", "a5v6", "s11", "utm_campaign=xmas&utm_content=car4"),                          # לא x בדיוק - נספר
 row("2026-11-09 08:00:00", "view", "a5", "s7", "utm_campaign=ic_camp&utm_content=p25"),
 row("2026-11-09 08:10:00", "purchase", "a5", "s7", "cardcom | 297 ILS | deal 1007 | src ", cta="cardcom_webhook"),       # לפני נתוני ההוצאה
 row("2026-11-12 14:00:00", "purchase", "a5v6", "s1", "cardcom | 297 ILS | deal 1008 | src ", x="int=1", cta="cardcom_webhook"),  # בדיקה (b88)
 row("2026-11-12 15:00:00", "view", "a5v6", "s9", "utm_campaign=lenatzeach_lab&utm_content=car4"),
 row("2026-11-12 15:20:00", "purchase", "a5v6", "s9", "cardcom | 297 ILS | deal 1009 | src ", cta="cardcom_webhook"),      # אין רכישה בימי ההוצאה
                                         # בדיקה - לא נספר כראשונה
]
json.dump({"content": "\n".join(R)}, open(d + "/ev.json", "w"))
open(d + "/sp.tsv", "w").write("spend\n2026-11-10|p25\t10\n2026-11-11|p25\t20\n2026-11-11|p25_brain_c2\t50\n2026-11-11|aff_amir_ic\t30\n2026-11-12|aff_amir_ic\t40\n2026-11-12|p25_yosef\t7\n2026-11-13|car4\t9\n2026-11-12|aff_yosef\t5\n2026-11-13|aff_yosef\t4\n2026-11-01|p25\t999\n")
out = subprocess.run([sys.executable, "-I", sys.argv[1], d + "/ev.json", "2026-11-14 10:00", d + "/sp.tsv"], capture_output=True, text=True).stdout
print(out)
n = f = 0
def ok(m, c):
    global n, f; n += 1
    if not c: f += 1; print("FAIL", m)
ok("6 purchases (dedupe, test deal, int=1 and out-of-window excluded)", "verified purchases 6," in out)
ok("first entry wins (s1 -> lenatzeach_cold), p25 has 2 purchases", "ad | p25 | purchases 2" in out and "OTHER" not in out)
ok("p25 spend in window only (30, 2/8 days), shared by 2 campaigns", "spend 7d 30 (2/8 ימים עם הוצאה; משותפת ל-2 קמפיינים: ic_camp 1, lenatzeach_cold 1 ביקורים)" in out)
ok("cpa = 30 / 1 purchase on spend days, 1 before spend data", "cost/purchase 30; 1 לפני נתוני ההוצאה" in out)
ok("ad with spend but no purchase on spend days", "ad | car4 | purchases 1" in out and "אין רכישות בימי ההוצאה; 1 לפני נתוני ההוצאה" in out)
ok("utm_campaign=x not counted; xmas is (car4 shared by 2)", "x 1" not in out and "משותפת ל-2 קמפיינים: ic_camp 1, lenatzeach_cold 1 ביקורים" in out and "spend 7d 9 (1/8 ימים עם הוצאה; משותפת ל-2 קמפיינים: lenatzeach_lab 1, xmas 1 ביקורים)" in out)
ok("amir shared ad -> spend at affiliate", "p25_brain_c2 · aff amir" in out and "אצל המשווק" in out and "aff | amir | purchases 1 | spend 7d 70 (2/8" in out)
ok("campaign decoded, pipe replaced", "camp | NLP / Aff amir |" in out)
ok("yosef own ad uses per-ad spend 7", "p25_yosef · aff yosef | purchases 1 | revenue 297 | spend 7d 7 (1/8" in out)
ok("bank without events -> unknown", "לא ידוע" in out and "| bank |" in out)
ok("yosef total = per-ad on 12.11 (7, not +5) + aff_yosef on 13.11 (4) = 11", "aff | yosef | purchases 1 | spend 7d 11 (2/8" in out)
ok("no personal data columns", "deal" not in out.split("-- רכישות")[1])
print("%d/%d" % (n - f, n)); sys.exit(1 if f else 0)
