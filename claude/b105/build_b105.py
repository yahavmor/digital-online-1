# ב105 (ראשי 17.11 11:44 - בקשת בן ו"בצע" של יהב): דף בדיקה חדש a5v7 מ-a5v6, באותו עיצוב ובאותם רכיבים.
# מזיזים סקשנים שלמים (הלקח מ-a5v5), בלי לשנות את הטקסט שלהם. השינויים:
#   1. יוצא: "למה בניתי את השיטה?" (data-name="למה בניתי").
#   2. מסך ראשון: הוק חדש - כותרת (h1) ושורת המשך (.sub). השאלה שמעל הכותרת ("למה המוח מחפש חסרונות?") יוצאת.
#      שלוש אפשרויות: --hook=a (ברירת מחדל), b, c. כל השאר במסך הראשון בלי שינוי.
#   3. סדר: פתיחה → רגע לפני (הכאב) → מה אם → לדעת או להטמיע → איך נראית המציאות → עם מה תצא (+כפתור cta2)
#      → מה יש בפנים → בונוסים → ההצעה → האחריות (+כפתור, id: guar) → תלמידים מספרים (סטוריז) ופס המספרים → מה אומרים (+כפתור cta1)
#      → תוצאות אמיתיות → למי מתאים → איך מתחילים → שאלות נפוצות → כפתור הסיום (id: final). הכפתור הצף נשאר.
#   4. variant a5v7, noindex (כמו a5v6), אותם קישורי סליקה ותגיות מדידה. data-sec ממוספר מחדש לפי הסדר החדש
#      (אירוע section ופס ההתקדמות מניחים מספרים עולים), section_view לפי data-stage כמו ב-a5v6.
# לא נוגעים ב-a.html, ב-a5v6.html, ב-go.html ובסליקה.
# הרצה: python3 build_b105.py <שורש ריפו של main> <תיקיית יעד> [--hook=a|b|c] [--name=a5v7]
import sys, os, re
SRC, OUT = sys.argv[1], sys.argv[2]
ARG = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--") and "=" in a)
HOOK = ARG.get("hook", "a"); NAME = ARG.get("name", "a5v7")
HOOKS = {  # כותרת (החלק השני מודגש כמו ב-a5v6) ושורת המשך
 "a": ("שוב הלכת לישון עם ההבטחה שמחר תתחיל.", "ושוב התעוררת לאותם ההרגלים.", "אבל למה זה ממשיך לקרות לך, גם כשאתה מבין בדיוק מה אתה צריך לשנות?"),
 "b": ("קראת ספרים. עשית קורסים.", "ועדיין באותו מקום?", "הבעיה היא לא שחסר לך ידע. הבעיה היא מה שקורה אחרי שאתה יודע."),
 "c": ("המוח שלך מחפש קודם מה לא בסדר.", "בך, בחיים שלך, במה שעוד לא עשית.", "ומה שהכי מעניין? יכול להיות שאתה אפילו לא שם לב כמה זה מנהל אותך במהלך היום."),
}
s = open(os.path.join(SRC, "nlp/a5v6.html"), encoding="utf8").read()
assert s.count('data-variant="a5v6"') == 1
s = s.replace('data-variant="a5v6"', 'data-variant="%s"' % NAME)

def end_of(i):
    tag = re.match(r"<(\w+)", s[i:]).group(1); depth = 0
    for m in re.finditer(r"<(/?)%s\b[^>]*>" % tag, s[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return i + m.end()
    raise ValueError(i)

# הבלוקים העליונים מהפתיחה ועד סוף סקשן האחריות
a = s.index('<header class="hero9" data-sec="1"'); g = s.index('<section class="guar"'); z = end_of(g)
blocks, i = [], a
while i < z:
    j = s.index("<", i); assert not s[i:j].strip(), s[i:j][:80]
    e = end_of(j); blocks.append(s[j:e]); i = e
def key(b):
    m = re.search(r'data-name="([^"]+)"', b[:400])
    if b.startswith('<header'): return "hero"
    if 'class="sp-stories"' in b[:200]: return "stories"
    if 'class="proofbar"' in b[:200]: return "proofbar"
    if b.startswith('<section class="guar"'): return "guar"
    if 'class="ctab' in b[:60]: return re.search(r'data-cta="([^"]+)"', b).group(1)
    return m.group(1)
B = {key(b): b for b in blocks}; assert len(B) == len(blocks), [key(b) for b in blocks]
ORDER = ["hero", "רגע לפני", "מה אם", "לדעת או להטמיע", "איך נראית המציאות", "עם מה תצא", "cta2",
         "מה יש בפנים", "בונוסים", "ההצעה", "guar", "stories", "proofbar", "מה אומרים", "cta1", "תוצאות אמיתיות", "למי מתאים",
         "איך מתחילים", "שאלות", "cta3"]
assert set(B) - set(ORDER) == {"למה בניתי"}, set(B) ^ set(ORDER)
B["guar"] = B["guar"].replace('data-cta="final"', 'data-cta="guar"', 1)      # כפתור האחריות, עכשיו מיד אחרי ההצעה
B["cta3"] = B["cta3"].replace('data-cta="cta3"', 'data-cta="final"', 1)      # כפתור הסיום, אחרי השאלות הנפוצות
# ההוק
h1a, h1b, sub = HOOKS[HOOK]; hero = B["hero"]
hero, n1 = re.subn(r'<p class="eyebrow">[^<]*</p>\s*', "", hero, 1)
hero, n2 = re.subn(r'<h1 class="promise">.*?</h1>', '<h1 class="promise">%s <mark>%s</mark></h1>' % (h1a, h1b), hero, 1, flags=re.S)
hero, n3 = re.subn(r'<p class="sub">.*?</p>', '<p class="sub">%s</p>' % sub, hero, 1, flags=re.S)
assert (n1, n2, n3) == (1, 1, 1); B["hero"] = hero
body = "\n".join(B[k] for k in ORDER)
# מספור data-sec ו-data-num מחדש לפי הסדר החדש
n = [0]; body = re.sub(r'data-sec="\d+"', lambda m: (n.__setitem__(0, n[0] + 1), 'data-sec="%d"' % n[0])[1], body)
k = [0]; body = re.sub(r'data-num="\d+"', lambda m: (k.__setitem__(0, k[0] + 1), 'data-num="%02d"' % k[0])[1], body)
out = s[:a] + body + s[z:]
assert out.count('data-cta="hero_main"') == s.count('data-cta="hero_main"') and "למה בניתי את השיטה" not in out
os.makedirs(OUT, exist_ok=True)
fn = os.path.join(OUT, NAME + ("" if HOOK == "a" else "_hook" + HOOK) + ".html")
open(fn, "w", encoding="utf8").write(out)
print(fn, len(out), "sections:", n[0], "ctas:", re.findall(r'<a class="cta" data-cta="([^"]+)"', out))
