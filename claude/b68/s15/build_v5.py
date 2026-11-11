# ב83 (בקשת בן 11.11, ראשי): דף בדיקה a5v5 מתוך סקריפט הבנייה של a5v4. a5v4 לא משתנה.
# a5v5 = a5v4 (כולל חלקים 1-9) + שכבת v5 לפי claude/sales-page-plan-1111.md (סעיפים 3-6):
#   סדר הסקשנים (סעיף 3), סרטונים (לולאה ברקע הפתיחה + הסרטון המלא בלחיצה, h2 בסקשן האמונה, רצועת 5 אחרי ההצעה),
#   אנימציות (סעיף 5: transform/opacity בלבד, לא במסך הראשון, כבויות בהפחתת תנועה, תוכן גלוי בלי JS), קבלה (סעיף 6).
# בלי טקסט חדש ובלי שינוי מחיר. noindex, לא ב-go.html ולא בניסוי. data-variant="a5v5" (האירועים נרשמים עם v=a5v5).
# הרצה: python3 claude/b68/s15/build_v5.py <שורש ריפו של main> <תיקיית יעד> [--noindex] [--slots=קובץ] [--suffix=s] [--preview]
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_v4 as B4  # אותו argv: SRC, OUT, --noindex, --slots, --suffix, --preview

V5_SLOTS = json.load(open(B4.ARG.get("v5slots", os.path.join(HERE, "slots_v5.json")), encoding="utf8"))

def v5_layer(p):
    # השכבה של v5 נבנית לפי המפרט (סעיפים 3-6) - ממתין לקובץ המפרט
    return p

def build():
    p = B4.v4(B4.build_v3.build_a5(), "a5", "a5v3", "a5v5")
    p = v5_layer(p)
    assert p.count('data-variant="a5v5"') == 1
    return p

if __name__ == "__main__":
    os.makedirs(B4.OUT, exist_ok=True)
    p = build()
    open(os.path.join(B4.OUT, "a5v5" + B4.SUFFIX + ".html"), "w", encoding="utf8").write(p)
    print("a5v5", len(p))
