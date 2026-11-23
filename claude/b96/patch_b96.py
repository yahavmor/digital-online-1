# ב96 ("מאשר ב96" מיהב, 15.11): שדה השם חוזר למסך הראשון בדף התשלום. פריסה בלבד, בלי טקסט חדש.
# 1. #wallTop (Apple Pay / Google Pay, או הרמז בדפדפן פנימי) עובר מראש הדף אל מתחת לטופס הפרטים - ב-B וב-B2.
# 2. B2: עוגן המחיר ושורת האחריות נשארים, בעיצוב צמוד יותר.
# 3. cx חדש co_b2_1511 - הספירה של B מול B2 מתחילה מחדש (בדף התשלום, בדשבורד ובסיכום היומי).
# שימוש: python3 patch_b96.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os, re
root, day, hm = sys.argv[1:4]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
p = os.path.join(root, "nlp/checkout.html"); s = open(p, encoding="utf8").read()
m = re.search(r'<div class="walltop" id="wallTop">.*?<p class="wt-h" id="wtH" hidden></p></div>\n', s, re.S)
assert m and s.count('id="wallTop"') == 1
wall = m.group(0); s = s.replace(wall, "", 1)
old = '''</form>
</section>

<section class="pay" id="paySec"'''
assert s.count(old) == 1
s = s.replace(old, '''</form>
''' + wall.replace('<div class="walltop" id="wallTop">', '<div class="walltop wt-below" id="wallTop"><!-- ב96: מתחת לטופס (היה בראש הדף) -->') + '''</section>

<section class="pay" id="paySec"''', 1)
open(p, "w", encoding="utf8").write(s)
patch("nlp/checkout.html", [
 ('''.b2-step{color:var(--gold)}''', '''.b2-step{color:var(--gold)}
/* ב96: B2 צמוד יותר - העוגן ושורת האחריות נשארים, כדי ששדה השם ייכנס למסך הראשון */
html[data-co2="1"] .top{padding:14px 0 2px}
html[data-co2="1"] .order{position:relative;margin-top:22px;padding:14px 16px 8px}
html[data-co2="1"] .b2-launch{position:absolute;top:-11px;left:50%;transform:translateX(-50%);margin:0;padding:1px 10px;font-size:12.5px;line-height:1.5;background:var(--soft);white-space:nowrap}
html[data-co2="1"] .order .price{margin:4px 0 0}
html[data-co2="1"] .price s.was{font-size:18px}
html[data-co2="1"] .b2-guar{margin:6px auto 0;max-width:none;padding:4px 10px;font-size:13px;line-height:1.35;border-radius:10px}
html[data-co2="1"] .once,html[data-co2="1"] .nosub{display:inline-block;margin:6px 5px 0;vertical-align:baseline}
html[data-co2="1"] .incl{margin:8px 0 0;padding:6px 0 0;gap:4px}
html[data-co2="1"] .why{margin-top:12px;padding-top:10px}
/* ב96: Apple Pay / Google Pay מתחת לטופס */
.walltop.wt-below{margin:14px auto 0}'''),
 ('''const CO_EXP = "co_b2_1311";''', '''const CO_EXP = "co_b2_1511"; /* ב96 (%s %s): הספירה של B מול B2 מתחילה מחדש - שתי הגרסאות השתנו (Apple Pay/Google Pay מתחת לטופס, B2 צמוד יותר). היה co_b2_1311 */''' % (day[8:10] + "." + day[5:7], hm)),
])
patch("nlp/dashboard.html", [
 ('''S=M.sess.filter(s=>(s.co==="b"||s.co==="b2")&&s.ev.some(r=>parseX(r.x).cx==="co_b2_1311"));''', '''S=M.sess.filter(s=>(s.co==="b"||s.co==="b2")&&s.ev.some(r=>parseX(r.x).cx==="co_b2_1511")); /* ב96: מתחיל מחדש (היה co_b2_1311) */'''),
 ('''קבועה למכשיר (cx=co_b2_1311). ''', '''קבועה למכשיר (cx=co_b2_1511, מ-%s %s - הספירה התחילה מחדש ב-ב96). ''' % (day[8:10] + "." + day[5:7], hm)),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב96 (\\"מאשר ב96\\" מיהב): שדה השם חוזר למסך הראשון בדף התשלום - השורה על Apple Pay / Google Pay (או הרמז בדפדפן של פייסבוק ואינסטגרם) עברה מראש הדף אל מתחת לטופס, ב-B וב-B2; ב-B2 עוגן המחיר ושורת האחריות בעיצוב צמוד יותר. בלי טקסט חדש. הספירה של B מול B2 מתחילה מחדש (cx=co_b2_1511)."],
''' % (day, hm)),
])
patch("claude/daily/daily_0811.py", [
 ('''s["cx"]=="co_b2_1311" and''', '''s["cx"]=="co_b2_1511" and'''),
 ('''s["cx"] not in("co_b_0811","co_b2_1311")''', '''s["cx"] not in("co_b_0811","co_b2_1311","co_b2_1511")'''),
])
print("ok")
