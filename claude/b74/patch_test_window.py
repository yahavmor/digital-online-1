# ב74 - הכנת חלון הבדיקה ("מאשר ב74 - הפעלה לבדיקה", ראשי 14.11):
#  1. כתובת השרת (hook 4068821, תרחיש 8463689) במקום %UPSELL_API% בשלושת דפי האפסייל.
#  2. צילומי האפליקציה שבן אישר (upsell-assets.zip מצ'אט האפליקציה, 11.11) ב-CONFIG.screenshots: home, plan, sos.
#     הקבצים נכנסים ל-nlp/assets/upsell/ (780x1604, אותו יחס כמו מסגרת הטלפון בדף).
# שימוש: python3 patch_test_window.py <nlp dir>   (משנה במקום)
import sys, os, shutil
D = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://hook.eu1.make.com/afnx34prmqo6zjf7b8zoqe7fvvy6q97b"
def rep(f, old, new):
    p = os.path.join(D, f); s = open(p, encoding="utf8").read()
    assert s.count(old) == 1, (f, old[:60], s.count(old)); open(p, "w", encoding="utf8").write(s.replace(old, new, 1))
rep("upsell-97.html", "upsellApi: '%UPSELL_API%', // תרחיש Make של האפסייל (טיוטה, לא קיים עדיין). עד שמוזן - אין פנייה לשרת",
    "upsellApi: '" + API + "', // ב74: תרחיש 8463689 (hook 4068821). פעיל רק בחלון בדיקה או אחרי ההשקה; כבוי = אין הצעה")
rep("upsell-97.html", "screenshots: { home: null, plan: null, sos: null },",
    "screenshots: { home: 'assets/upsell/app-home.jpg', plan: 'assets/upsell/app-plan.jpg', sos: 'assets/upsell/app-sos.jpg' }, // בן אישר 14.11")
rep("checkout97.html", 'const UPSELL_API = "%UPSELL_API%";', 'const UPSELL_API = "' + API + '";')
rep("upsell-thanks.html", 'const UPSELL_API = "%UPSELL_API%";', 'const UPSELL_API = "' + API + '";')
os.makedirs(os.path.join(D, "assets", "upsell"), exist_ok=True)
for k in ("home", "plan", "sos"):
    shutil.copy(os.path.join(HERE, "upsell_assets", "app-%s.jpg" % k), os.path.join(D, "assets", "upsell", "app-%s.jpg" % k))
print("ok")
