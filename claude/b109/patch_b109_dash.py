# ב109: הדשבורד לא הכיר את a5s (לא ב-ALLV), ולכן כניסות לדף הקצר - גם עם aff - לא נספרו בכלל (רק הרכישה, מה-webhook).
# מוסיף את a5s לרשימת הדפים, לשם, לצבע ולשמות של "תמונת מצב". campaign.html נבנה מחדש מהדשבורד (ALLV בתוך הבלוק המשותף).
# שימוש: python3 patch_b109_dash.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
p = os.path.join(root, "nlp/dashboard.html"); s = open(p, encoding="utf-8").read()
for a, b in [
 ('"a5v6","a5v7","pr","pr2"], VLBL={', '"a5v6","a5v7","a5s","pr","pr2"], VLBL={a5s:"a5s - הדף הקצר: ההצעה קודם, העומק מקופל (ב107, ב109)",'),
 ('a5v6:"var(--s4)",pr:"var(--s7)"', 'a5v6:"var(--s4)",a5s:"var(--s1)",pr:"var(--s7)"'),
 ('SNAP_PAGES={a5v6:"דף A החדש (a5v6)",', 'SNAP_PAGES={a5s:"הדף הקצר (a5s)",a5v6:"דף A החדש (a5v6)",'),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב109: הדף הקצר a5s נוסף לרשימת הדפים בדשבורד (ALLV). עד עכשיו כניסות ל-a5s לא נספרו בשום לשונית, גם לא אצל משווק; רק רכישה נספרה. הדף עצמו: הפסקה של בן בין הפתיחה להצעה, ושני קיפולי ההוכחות (סרטון וצילומי וואטסאפ) עלו מיד אחרי האחריות."],\n' % (day, hm)),
]:
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s); print("ok")
