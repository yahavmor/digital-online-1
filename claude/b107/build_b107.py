# ב107 (ראשי 18.11, בקשת בן): דף בדיקה קצר "הצעה קודם" מ-a5v7, באותו עיצוב ובאותם רכיבים, בלי ניסוח חדש.
# לפי תוכנית העבודה של הראשי (17.11, סעיף 1): ההצעה מיד אחרי המסך הראשון, והעומק מקופל.
#   סדר: פתיחה (בלי שינוי) → ההצעה → האחריות → תלמידים מספרים ופס המספרים
#        → מקופלים, כל אחד בכותרת שלו (פתיחה בלחיצה): רגע לפני, מה אם, לדעת או להטמיע, איך נראית המציאות, עם מה תצא,
#          מה יש בפנים, בונוסים, מה אומרים, תוצאות אמיתיות, למי מתאים, איך מתחילים, שאלות נפוצות
#        → כפתור הסיום (final). הכפתור הצף נשאר. כפתורי הביניים cta2 ו-cta1 יוצאים (הם היו בין סקשנים שעכשיו מקופלים).
#   הטקסטים לא משתנים: כותרת הקיפול היא הכותרת הקיימת של הסקשן (ב"רגע לפני", שאין לו כותרת, השאלה הראשונה שלו).
#   מדידה: variant a5s, noindex, אותם קישורי סליקה ותגיות. אירוע חדש fold_open (name = שם הסקשן) בפתיחה הראשונה של קיפול.
#   לא ב-go.html ולא בניסוי. לא נוגעים ב-a.html, ב-a5v7.html, ב-go.html ובסליקה.
# הרצה: python3 build_b107.py <שורש ריפו של main> <תיקיית יעד> [--name=a5s]
import sys, os, re
SRC, OUT = sys.argv[1], sys.argv[2]
ARG = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--") and "=" in a); NAME = ARG.get("name", "a5s")
s = open(os.path.join(SRC, "nlp/a5v7.html"), encoding="utf8").read()
assert s.count('data-variant="a5v7"') == 1; s = s.replace('data-variant="a5v7"', 'data-variant="%s"' % NAME)
def end_of(t, i):
    tag = re.match(r"<(\w+)", t[i:]).group(1); depth = 0
    for m in re.finditer(r"<(/?)%s\b[^>]*>" % tag, t[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return i + m.end()
    raise ValueError(i)
a = s.index('<header class="hero9" data-sec="1"'); z = s.index("<footer")
blocks, i = [], a
while True:
    j = s.find("<", i)
    if j >= z: break
    assert not s[i:j].strip(), s[i:j][:80]; e = end_of(s, j); blocks.append(s[j:e]); i = e
def key(b):
    if b.startswith("<header"): return "hero"
    if 'class="sp-stories"' in b[:200]: return "stories"
    if 'class="proofbar"' in b[:200]: return "proofbar"
    if b.startswith('<section class="guar"'): return "guar"
    if 'class="ctab' in b[:60]: return re.search(r'data-cta="([^"]+)"', b).group(1)
    return re.search(r'data-name="([^"]+)"', b[:400]).group(1)
B = {key(b): b for b in blocks}; assert len(B) == len(blocks), [key(b) for b in blocks]
FOLD = ["רגע לפני", "מה אם", "לדעת או להטמיע", "איך נראית המציאות", "עם מה תצא", "מה יש בפנים", "בונוסים",
        "מה אומרים", "תוצאות אמיתיות", "למי מתאים", "איך מתחילים", "שאלות"]
ORDER = ["hero", "ההצעה", "guar", "stories", "proofbar"] + FOLD + ["final"]
assert set(B) - set(ORDER) == {"cta1", "cta2"}, set(B) ^ set(ORDER)
def fold(name, b):
    w = b.index('<div class="wrap stack">'); we = end_of(b, w); inner = b[w + len('<div class="wrap stack">'): we - len("</div>")]
    m = re.search(r"<h2\b[^>]*>.*?</h2>", inner, re.S) or re.search(r"<h3\b[^>]*>.*?</h3>", inner, re.S) or re.search(r'<p class="q">.*?</p>', inner, re.S)
    head = m.group(0); rest = inner[:m.start()] + inner[m.end():]
    return b[:w] + '<div class="wrap stack"><details class="fold" data-fold="%s"><summary>%s</summary><div class="fold-b">%s</div></details></div>' % (name, head, rest) + b[we:]
for k in FOLD: B[k] = fold(k, B[k])
body = "\n".join(B[k] for k in ORDER)
n = [0]; body = re.sub(r'data-sec="\d+"', lambda m: (n.__setitem__(0, n[0] + 1), 'data-sec="%d"' % n[0])[1], body)
k = [0]; body = re.sub(r'data-num="\d+"', lambda m: (k.__setitem__(0, k[0] + 1), 'data-num="%02d"' % k[0])[1], body)
CSS = """<style>/* ב107: קיפול העומק */
section:has(>.wrap>.fold){padding-block:26px}
.fold{width:100%}
.fold>summary{list-style:none;cursor:pointer;position:relative;padding-left:40px;border-radius:12px}
.fold>summary::-webkit-details-marker{display:none}
.fold>summary>*{margin:0}
.fold>summary::after{content:"";position:absolute;left:10px;right:auto;top:50%;width:10px;height:10px;border:0;border-radius:0;border-right:2.5px solid var(--gold,#b8892f);border-bottom:2.5px solid var(--gold,#b8892f);background:none;transform:translateY(-70%) rotate(45deg);transition:transform .2s}
.fold[open]>summary::after{transform:translateY(-25%) rotate(-135deg)}
.fold>summary h2{font-size:clamp(21px,5.6vw,30px);line-height:1.3}
.fold>summary:focus-visible{outline:3px solid var(--gold,#b8892f);outline-offset:4px}
.faq details.fold{border:0;background:none;padding:0;box-shadow:none;border-radius:0}
.faq details.fold>summary{padding:0 0 0 40px;background:none;min-height:0}
.fold>.fold-b{display:grid;gap:inherit;margin-top:18px}
</style>
"""
JS = """<script>/* ב107: אירוע fold_open בפתיחה הראשונה של כל קיפול */
document.querySelectorAll("details.fold").forEach(function(d){d.addEventListener("toggle",function(){if(d.open&&!d.dataset.o){d.dataset.o="1";try{window.__lpSend&&window.__lpSend("fold_open",{name:d.dataset.fold})}catch(e){}}})});
</script>
"""
out = s[:a] + body + "\n" + s[z:]
out = out.replace("</head>", CSS + "</head>", 1).replace("</body>", JS + "</body>", 1)
assert out.count('<details class="fold"') == len(FOLD) and out.count('data-cta="hero_main"') == s.count('data-cta="hero_main"') and 'data-cta="final"' in out
os.makedirs(OUT, exist_ok=True); fn = os.path.join(OUT, NAME + ".html"); open(fn, "w", encoding="utf8").write(out)
print(fn, len(out), "sections:", n[0], "ctas:", re.findall(r'<a class="cta" data-cta="([^"]+)"', out))
