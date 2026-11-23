# ב109 (ראשי 18.11 15:27, בקשת בן): הדף הקצר a5s.html בלבד. נבנה מעל a5s.html של main (ב107).
#  (1) בלוק חדש בין סוף הפתיחה (אחרי "מה בדיוק מקבלים?") ל-#offer, עם הפסקה של בן מילה במילה.
#      הנוסח בקובץ ben_paragraph.txt (שורה = שורה בדף). מקף ארוך (—, –) מוחלף במקף קצר (-). בלי הקובץ - הבנייה נעצרת,
#      חוץ מ-placeholder=1 לצילומי מבנה בלבד.
#  (2) שני קיפולי ההוכחות עולים למעלה, מיד אחרי האחריות ופס המספרים ולפני "עצור רגע":
#      קודם הסרטון ("תוצאות אמיתיות") בכותרת "מה אנשים שעברו את התהליך שלנו מספרים",
#      ואחריו צילומי הוואטסאפ ("מה אומרים") בכותרת "אנשים מספרים בתוך הקהילה הפרטית שלנו".
#      עיצוב מודגש שמזמין לפתוח. התוכן בפנים לא משתנה (הכותרת הקודמת של הסקשן נשארת ראשונה בתוך הקיפול).
#  לא נוגעים בדפים אחרים, ב-go.html, בניסוי on_1711 ובסליקה.
# הרצה: python3 build_b109.py <שורש ריפו של main> <קובץ יעד> [placeholder=1]
import sys, os, re, html
SRC, OUT = sys.argv[1], sys.argv[2]; PH = "placeholder=1" in sys.argv[3:]
HERE = os.path.dirname(os.path.abspath(__file__)); PF = os.path.join(HERE, "ben_paragraph.txt")
s = open(os.path.join(SRC, "nlp/a5s.html"), encoding="utf8").read()
assert s.count('data-variant="a5s"') == 1
def end_of(t, i):
    tag = re.match(r"<(\w+)", t[i:]).group(1); depth = 0
    for m in re.finditer(r"<(/?)%s\b[^>]*>" % tag, t[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return i + m.end()
    raise ValueError(i)
def section_of(name):
    i = s.index('<details class="fold" data-fold="%s">' % name); a = s.rindex("<section", 0, i); return a, end_of(s, a)
# (1) הפסקה של בן
if os.path.exists(PF):
    lines = [l.strip() for l in open(PF, encoding="utf8").read().replace("\r", "").split("\n")]
    while lines and not lines[-1]: lines.pop()
    while lines and not lines[0]: lines.pop(0)
    lines = [re.sub(r"\s*[—–]\s*", " - ", l) for l in lines]
    body = "\n".join('<p>%s</p>' % html.escape(l, quote=False) if l else '<p class="gap" aria-hidden="true"></p>' for l in lines)
    placeholder = False
else:
    assert PH, "חסר ben_paragraph.txt - הנוסח של בן"
    body = '<p class="ph">[הפסקה של בן - 13 שורות - ממתין לנוסח]</p>' * 1; placeholder = True
BLOCK = '<section class="bennote" data-sec="1" data-name="מילים של בן" data-stage="pain"%s><div class="wrap stack"><div class="bn-in">\n%s\n</div></div></section>\n' % (' data-placeholder="1"' if placeholder else "", body)
h = s.index('<header class="hero9"'); he = end_of(s, h)
assert 'data-cta="hero_shortcut"' in s[h:he] and s[he:].lstrip().startswith('<section id="offer"'), "המקום שבן סימן: בין הפתיחה ל-#offer"
s = s[:he] + "\n" + BLOCK + s[he:].lstrip("\n")
# (2) הקיפולים של ההוכחות
TITLES = {"תוצאות אמיתיות": "מה אנשים שעברו את התהליך שלנו מספרים", "מה אומרים": "אנשים מספרים בתוך הקהילה הפרטית שלנו"}
moved = []
for name in ["תוצאות אמיתיות", "מה אומרים"]:
    a, e = section_of(name); sec = s[a:e]; s = s[:a] + s[e:].lstrip("\n")
    m = re.search(r'<details class="fold" data-fold="%s"><summary>(.*?)</summary><div class="fold-b">' % name, sec, re.S)
    old_head = m.group(1)
    sec = sec[:m.start()] + '<details class="fold hot" data-fold="%s"><summary><h2>%s</h2></summary><div class="fold-b">%s' % (name, TITLES[name], old_head) + sec[m.end():]
    moved.append(sec)
a, _ = section_of("רגע לפני")
s = s[:a] + "\n".join(moved) + "\n" + s[a:]
# מספור data-sec ו-data-num מחדש לפי הסדר החדש
# רק בגוף הדף (מהפתיחה ועד ה-footer): הסקריפטים מפנים ל-[data-sec="1"] = הפתיחה
A_, Z_ = s.index('<header class="hero9"'), s.index("<footer"); mid = s[A_:Z_]
n = [0]; mid = re.sub(r'data-sec="\d+"', lambda m: (n.__setitem__(0, n[0] + 1), 'data-sec="%d"' % n[0])[1], mid)
k = [0]; mid = re.sub(r'data-num="\d+"', lambda m: (k.__setitem__(0, k[0] + 1), 'data-num="%02d"' % k[0])[1], mid)
s = s[:A_] + mid + s[Z_:]; assert 'data-sec="1"' in s[A_:A_ + 200]
CSS = """<style>/* ב109: הפסקה של בן, וקיפולי ההוכחות המודגשים */
.bennote{padding-block:30px 6px}
.bennote .bn-in{max-width:var(--text,640px);margin:0 auto;display:grid;gap:2px;font-size:18px;line-height:1.75;color:var(--ink2,#ddd);text-align:center}
.bennote .bn-in p{margin:0}.bennote .bn-in p.gap{height:12px}
.bennote .bn-in p.ph{color:#e5b84b;border:1px dashed #e5b84b;padding:14px;border-radius:12px}
section:has(>.wrap>.fold.hot){padding-block:14px}
.fold.hot{background:linear-gradient(180deg,rgba(212,175,55,.16),rgba(212,175,55,.06));border:1.5px solid var(--gold,#b8892f);border-radius:18px;padding:16px 16px 16px 14px;box-shadow:0 8px 28px rgba(0,0,0,.35)}
.fold.hot>summary{padding-left:52px}
.fold.hot>summary h2{font-size:clamp(20px,5.2vw,27px);line-height:1.35;color:var(--ink,#fff)}
.fold.hot>summary::before{content:"";position:absolute;left:0;top:50%;width:40px;height:40px;margin-top:-20px;border-radius:50%;background:var(--gold,#b8892f);box-shadow:0 0 0 6px rgba(212,175,55,.18)}
.fold.hot>summary::after{left:15px;border-color:#111;border-right-color:#111;border-bottom-color:#111;z-index:1}
.fold.hot:not([open])>summary::before{animation:hotpulse 2.4s ease-in-out infinite}
@keyframes hotpulse{0%,100%{box-shadow:0 0 0 6px rgba(212,175,55,.18)}50%{box-shadow:0 0 0 11px rgba(212,175,55,.06)}}
@media (prefers-reduced-motion:reduce){.fold.hot:not([open])>summary::before{animation:none}}
</style>
"""
s = s.replace("</head>", CSS + "</head>", 1)
assert s.count('class="fold hot"') == 2 and s.count('<section class="bennote"') == 1
open(OUT, "w", encoding="utf8").write(s)
print(OUT, len(s), "sections:", n[0], "placeholder" if placeholder else "ben text: %d lines" % len([l for l in lines if l]))
