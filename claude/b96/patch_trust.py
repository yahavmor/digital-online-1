# ב96 המשך ("מאשר ב96" מיהב, בן אישר את שורת האמון, 15.11): שורת אמון קומפקטית בדף התשלום, בלי טקסט חדש.
# תמונה עגולה קטנה של בן (assets/ben-avatar.webp, 96x96, חיתוך של ben-m.webp) + "90 שיעורים קצרים + 5 בונוסים" + "7 ימי אחריות עם החזר מלא".
# B2: שורת האחריות הנפרדת בכרטיס ההזמנה (.b2-guar) מוסתרת - האחריות נמצאת בשורת האמון, בלי כפילות. עוגן המחיר נשאר.
# מיקום: POS=above (מעל השדות) או below_name (מיד מתחת לשדה השם). cx חדש co_b2_1511t.
# שימוש: python3 patch_trust.py <repo root> "<YYYY-MM-DD>" "<HH:MM>" <above|below_name>
import sys, os, shutil
root, day, hm, pos = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(here, "ben-avatar.webp"), os.path.join(root, "nlp/assets/ben-avatar.webp"))
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
TR = '<div class="trust" id="coTrust"><img src="assets/ben-avatar.webp" alt="בן נחום" width="34" height="34" decoding="async"><p><span>90 שיעורים קצרים + 5 בונוסים</span><span>7 ימי אחריות עם החזר מלא</span></p></div>'
D = day[8:10] + "." + day[5:7]
pairs = [
 ('''/* ב96: Apple Pay / Google Pay מתחת לטופס */''', '''/* ב96 המשך: שורת אמון */
.trust{display:flex;align-items:center;gap:10px;margin:0 0 10px;padding:6px 10px;border-radius:12px;background:var(--soft);text-align:right}
.trust img{width:34px;height:34px;border-radius:50%;flex:none;object-fit:cover}
.trust p{margin:0;font-size:13.5px;line-height:1.35;font-weight:600;color:var(--ink2)}
.trust p{min-width:0}
.trust p span{display:inline-block;max-width:100%}
.trust p span+span::before{content:" · ";color:var(--muted);font-weight:400}
.fld+.trust{margin:-2px 0 12px}
html[data-co2="1"] .b2-guar{display:none} /* ב-B2 האחריות בשורת האמון */
/* ב96: Apple Pay / Google Pay מתחת לטופס */'''),
 ('''const CO_EXP = "co_b2_1511";''', '''const CO_EXP = "co_b2_1511t"; /* ב96 המשך (%s %s): שורת אמון - הספירה מתחילה מחדש */''' % (D, hm)),
]
if pos == "above":
    pairs.append(('''<form id="det" novalidate data-clarity-mask="True">
''', '''<form id="det" novalidate data-clarity-mask="True">
''' + TR + '''
'''))
else:
    pairs.append(('''<span>החשבונית תופק על השם הזה</span></label>
''', '''<span>החשבונית תופק על השם הזה</span></label>
''' + TR + '''
'''))
patch("nlp/checkout.html", pairs)
patch("nlp/dashboard.html", [
 ('''parseX(r.x).cx==="co_b2_1511")''', '''parseX(r.x).cx==="co_b2_1511t")'''),
 ('''(cx=co_b2_1511, מ-''', '''(cx=co_b2_1511t, מ-%s %s, אחרי שורת האמון; קודם co_b2_1511 מ-''' % (D, hm)),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב96 המשך (\\"מאשר ב96\\" מיהב, בן אישר): שורת אמון בדף התשלום %s - תמונה עגולה של בן, \\"90 שיעורים קצרים + 5 בונוסים\\" ו\\"7 ימי אחריות עם החזר מלא\\", בלי טקסט חדש. ב-B2 שורת האחריות הנפרדת אוחדה לתוך שורת האמון. הספירה של B מול B2 מתחילה מחדש (cx=co_b2_1511t)."],
''' % (day, hm, "מעל השדות" if pos == "above" else "מיד מתחת לשדה השם")),
])
patch("claude/daily/daily_0811.py", [
 ('''s["cx"]=="co_b2_1511" and''', '''s["cx"]=="co_b2_1511t" and'''),
 ('''"co_b2_1311","co_b2_1511")''', '''"co_b2_1311","co_b2_1511","co_b2_1511t")'''),
])
print("ok", pos)
