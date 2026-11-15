# ב99 (ראשי, 15.11): במובייל בלבד, ב-B וב-B2, הטופס בדף התשלום עולה למסך הראשון.
# 1. כרטיס ההזמנה בשורה אחת: "הקורס המלא + 5 בונוסים · 297 ₪ חד-פעמי" (הנוסח מבקשת ב99). רשימת ה-✓ עוברת לסוף הדף (עותק זהה, רק במובייל).
# 2. המשפט מתחת ל"השלמת הרכישה" - במובייל רק "עוד רגע זה שלך." (החלק השני מוסתר, בלי טקסט חדש).
# 3. מחשב (מעל 600px) - בלי שינוי. לא נוגעים בטקסטים המחייבים, בצ'קבוקסים, באירועים ובחיבור לקארדקום. cx חדש co_b2_1511m.
# שימוש: python3 patch_b99.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
D = day[8:10] + "." + day[5:7]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
INCL = '''<li>קורס הליבה: 90 שיעורים קצרים ומעשיים</li>
<li>תרגולים מעשיים ליישום ביום-יום</li>
<li>5 בונוסים בשווי 1,121 ₪: 2 קורסים מוקלטים + 3 ערכות עבודה</li>
<li>גישה מיידית, מהטלפון או מהמחשב</li>'''
patch("nlp/checkout.html", [
 ('''<p class="what">עוד רגע זה שלך. לאחר אישור התשלום תקבל גישה מיידית לקורס ולכל הבונוסים.</p>''',
  '''<p class="what">עוד רגע זה שלך.<span class="what2"> לאחר אישור התשלום תקבל גישה מיידית לקורס ולכל הבונוסים.</span></p>'''),
 ('''<section class="order" aria-label="ההזמנה שלך">
''', '''<section class="order" aria-label="ההזמנה שלך">
<p class="one1">הקורס המלא + 5 בונוסים · <span class="pgrp">297 ₪</span> חד-פעמי</p><!-- ב99: שורה אחת במובייל בלבד -->
'''),
 ('''<a class="back" href="./" id="back">חזרה לדף</a>''', '''<section class="incl-end" aria-label="מה מקבלים"><ul class="incl">
''' + INCL + '''
</ul></section><!-- ב99: במובייל רשימת ה-✓ כאן, בסוף הדף -->
<a class="back" href="./" id="back">חזרה לדף</a>'''),
 ('''/* ב96: Apple Pay / Google Pay מתחת לטופס */''', '''/* ב99: במובייל הטופס במסך הראשון - כרטיס הזמנה בשורה אחת, ✓ בסוף הדף */
.one1,.incl-end{display:none}
@media (max-width:600px){
.wrap{padding-top:10px}
.brand{padding:2px 0 8px}
.top,html[data-co2="1"] .top{padding:10px 0 0}
.top h1{font-size:26px;margin:0 0 2px}
.top .what{font-size:15.5px}
.top .what2{display:none}
.order,html[data-co2="1"] .order{margin:10px 0 0;padding:9px 12px}
.order>*:not(.one1){display:none!important}
.order .one1{display:block;margin:0;text-align:center;font-size:16px;font-weight:800;line-height:1.35}
.why,html[data-co2="1"] .why{margin-top:10px;padding-top:10px}
.why h2{margin:0 0 6px}
.incl-end{display:block;margin:16px 0 0;padding:14px 16px;border:1px solid var(--line);border-radius:var(--r);background:var(--soft)}
.incl-end .incl{margin:0;padding:0;border:0}
}
/* ב96: Apple Pay / Google Pay מתחת לטופס */'''),
 ('''const CO_EXP = "co_b2_1511t";''', '''const CO_EXP = "co_b2_1511m"; /* ב99 (%s %s): במובייל הטופס במסך הראשון - הספירה מתחילה מחדש */''' % (D, hm)),
])
patch("nlp/dashboard.html", [
 ('''parseX(r.x).cx==="co_b2_1511t")''', '''parseX(r.x).cx==="co_b2_1511m")'''),
 ('''(cx=co_b2_1511t, מ-''', '''(cx=co_b2_1511m, מ-%s %s, אחרי ב99 - הטופס במסך הראשון במובייל; קודם co_b2_1511t מ-''' % (D, hm)),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב99 (ראשי, \\"מאשר\\" מיהב): במובייל בלבד, ב-B וב-B2, הטופס בדף התשלום עולה למסך הראשון. כרטיס ההזמנה בשורה אחת (\\"הקורס המלא + 5 בונוסים · 297 ₪ חד-פעמי\\"), רשימת ה-✓ עברה לסוף הדף, ומתחת לכותרת רק \\"עוד רגע זה שלך.\\". במחשב אין שינוי. הספירה של B מול B2 מתחילה מחדש (cx=co_b2_1511m)."],
''' % (day, hm)),
])
patch("claude/daily/daily_0811.py", [
 ('''s["cx"]=="co_b2_1511t" and''', '''s["cx"]=="co_b2_1511m" and'''),
 ('''"co_b2_1511","co_b2_1511t")''', '''"co_b2_1511","co_b2_1511t","co_b2_1511m")'''),
])
print("ok")
