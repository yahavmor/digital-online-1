# ב74 (החלטת בן 10.11): 97 ₪ הצעה חד-פעמית - כשהדף נסגר אי אפשר לקבל אותה יותר. מסלול ה-147 (ב38) והמייל למי שוויתר מבוטלים.
# מוריד כל אזכור של 147 מדף האפסייל ומדף התשלום, ומחליף את הנוסחים לנוסח החד-פעמי. רץ על nlp/ של main:
#   python3 claude/b74/once/patch_once.py <nlp dir>
import sys, os, re
D = sys.argv[1]
def sub1(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a)); return s.replace(a, b)
# ---------- upsell-97.html ----------
p = os.path.join(D, "upsell-97.html"); s = open(p, encoding="utf8").read()
a = s.index("  // הצעה חוזרת למי שוויתר"); b = s.index("/* ===== פס בדיקה") if False else s.index("if (_q === 'b') CONFIG.reoffer"); b = s.index("\n", b) + 1
s = s[:a] + '''  // ב74 (החלטת בן 10.11): 97 ₪ הצעה חד-פעמית. כשהדף נסגר או בוויתור אי אפשר לקבל אותה יותר; אין מחיר אחר בהמשך ואין מייל חוזר (המסלול של ב38 בוטל)
  reoffer: { mode: 'once' }
};
''' + s[b:]
s = sub1(s, "const P = CONFIG.reoffer.laterPrice;\n", "")
a = s.index("const COPY = {"); b = s.index("}[CONFIG.reoffer.mode || 'null'];"); b = s.index("\n", b) + 1
s = s[:a] + '''const COPY = {
  once: { heroTag: 'הצעה חד-פעמית • לרוכשי הקורס', offerTag: 'הצעה חד-פעמית, רק במסך הזה',
          urgent: '<b>שימו לב:</b> זו הצעה חד-פעמית. 97&nbsp;₪ רק במסך הזה, וכשתמשיך מהדף הזה היא לא תחזור.',
          modal: 'אין בעיה. הגישה שלך לקורס כבר מובטחת. רק חשוב לדעת: זו הצעה חד-פעמית שלא תחזור.',
          faq: 'הקורס שרכשת נשאר שלך. ההצעה להוסיף את האפליקציה ב-97&nbsp;₪ היא חד-פעמית, רק במסך הזה, והיא לא תחזור.' }
}.once;
''' + s[b:]
s = sub1(s, "   (!CONFIG.reoffer.mode && 'הצעה חוזרת: מתי ובאיזה מחיר (ממתין לבן)')].filter(Boolean)", "   ].filter(Boolean)")
# ערכי ברירת המחדל בתוך התגיות (מוצגים לפני שהסקריפט רץ) - אותו נוסח חד-פעמי
s = sub1(s, '<span class="tag" data-copy="heroTag">הצעה מיוחדת • לרוכשי הקורס</span>', '<span class="tag" data-copy="heroTag">הצעה חד-פעמית • לרוכשי הקורס</span>')
s = sub1(s, '<span class="tag" data-copy="offerTag">הצעה מיוחדת לרוכשי הקורס</span>', '<span class="tag" data-copy="offerTag">הצעה חד-פעמית, רק במסך הזה</span>')
s = sub1(s, '<p class="urgent" data-copy="urgent"><b>מחיר מיוחד לרוכשים חדשים:</b> 97&nbsp;₪ בתשלום חד-פעמי.</p>', '<p class="urgent" data-copy="urgent"><b>שימו לב:</b> זו הצעה חד-פעמית. 97&nbsp;₪ רק במסך הזה, וכשתמשיך מהדף הזה היא לא תחזור.</p>')
s = sub1(s, '<p data-copy="modal">אין בעיה. הגישה שלך לקורס כבר מובטחת. אפשר יהיה להוסיף את האפליקציה גם בהמשך.</p>', '<p data-copy="modal">אין בעיה. הגישה שלך לקורס כבר מובטחת. רק חשוב לדעת: זו הצעה חד-פעמית שלא תחזור.</p>')
assert "147" not in s and "laterPrice" not in s, "leftover"
open(p, "w", encoding="utf8").write(s)
# ---------- checkout97.html ----------
p = os.path.join(D, "checkout97.html"); s = open(p, encoding="utf8").read()
s = sub1(s, "ההצעה ב-97 ₪ פוקעת 30 דקות מרכישת הקורס או בוויתור; המוצר עצמו נשאר זמין ב-147 ₪ באזור הקורס", "ההצעה ב-97 ₪ חד-פעמית: פוקעת 30 דקות מרכישת הקורס או בוויתור, ולא חוזרת (ב74, בן 10.11; המסלול של ב38 בוטל)")
s = sub1(s, "<p>המאמן האישי זמין באזור הקורס ב-147 ₪.</p>", "<p>זו הייתה הצעה חד-פעמית, והיא לא חוזרת.</p>")
assert "147" not in s
open(p, "w", encoding="utf8").write(s)
print("ok")
