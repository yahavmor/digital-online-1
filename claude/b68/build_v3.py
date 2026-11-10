# ב68 (החלטת הראשי 10.11): v3 = סדר ומהירות, בלי שינוי עיצובי גדול. בונה שתי גרסאות מוכנות לעלייה מהדפים החיים,
# עם כל המדידה שלהם (פיקסל עם ההגנה של ב23, InitiateCheckout פעם אחת בלשונית, אירועים לגיליון, Clarity, שיוך משווקים):
#   nlp/pr2v3.html  מ-nlp/pr2.html  - הגוון העדין של v3 מהמעבדה, המחיר והכפתור לפני התמונה, ההצעה בסקשן 3 אחרי העדויות
#   nlp/a5v3.html   מ-nlp/a5.html   - שורות הזיהוי אחרי הכפתור (המחיר והכפתור במסך הראשון), ההצעה בסקשן 3 אחרי העדויות
# אותו קופי, אותן עדויות ואותם נכסים כמו בדף החי. בלי noindex. עולה רק הגרסה של הדף שינצח ב-ap2_0811.
# הרצה מתיקיית הריפו: python3 claude/b68/build_v3.py [נתיב יעד, ברירת מחדל nlp/]
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "nlp")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lab import THEMES  # הגוון של v3 מהמעבדה, בלי שינוי

SEC = re.compile(r'(<!--[^>]*-->\s*)?<(header|section)\b[^>]*data-sec="(\d+)".*?</\2>', re.S)

def reorder(p, order, n_expected):
    ms = list(SEC.finditer(p))
    assert [m.group(3) for m in ms] == [str(i) for i in range(1, n_expected + 1)], [m.group(3) for m in ms]
    # שומרים את מה שבין הסקשנים (למשל הסטוריז ופס ההוכחות אחרי הפתיחה ב-a5) צמוד לסקשן שלפניו
    blocks = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else m.end()
        blocks[m.group(3)] = p[m.start():end].rstrip() if i + 1 < len(ms) else m.group(0)
    new = "\n\n".join(blocks[k] for k in order)
    p = p[:ms[0].start()] + new + p[ms[-1].end():]
    # מספור מחדש לפי הסדר החדש: max_section ו-at_section ממשיכים לתאר עומק בדף
    for i, k in enumerate(order, 1):
        p = re.sub(r'(<(?:header|section)\b[^>]*?)data-sec="%s"' % k, r'\1data-sec="n%d"' % i, p, count=1)
    p = re.sub(r'data-sec="n(\d+)"', r'data-sec="\1"', p)
    return p

def common(p, src_var, new_var):
    assert p.count('data-variant="%s"' % src_var) == 1
    p = p.replace('data-variant="%s"' % src_var, 'data-variant="%s"' % new_var)
    p = re.sub(r'\s*<meta name="robots" content="noindex[^"]*">', "", p)
    # המדידה של הדף החי נשארת כמו שהיא
    for k in ("TRACK_ENDPOINT", "fbq(", "clarity", "NLP_OWNER", "InitiateCheckout"):
        assert k in p, "measurement missing: " + k
    return p

def build_pr2():
    p = open(os.path.join(ROOT, "nlp", "pr2.html"), encoding="utf8").read()
    p = common(p, "pr2", "pr2v3")
    p = p.replace("</style>", THEMES["v3"]["css"] + "</style>", 1)
    p = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="%s">' % THEMES["v3"]["theme_color"], p)
    # 1 פתיחה, 4 עדויות, 8 ההצעה, ואז השאר בסדר המקורי (זהה ל-v3 במעבדה)
    p = reorder(p, ["1", "4", "8", "2", "3", "6", "7", "5", "9", "10"], 10)
    mb = re.search(r'\n <div class="buy">.*?\n </div>\n', p, re.S); assert mb, "buy block"
    buy = mb.group(0); p = p.replace(buy, "\n", 1)
    msub = re.search(r'<p class="sub">.*?</p>\n', p, re.S); assert msub
    p = p[:msub.end()] + buy.lstrip("\n") + p[msub.end():]
    return p

def build_a5():
    p = open(os.path.join(ROOT, "nlp", "a5.html"), encoding="utf8").read()
    p = common(p, "a5", "a5v3")
    # בפתיחה: שלוש שורות הזיהוי עוברות אחרי הכפתור, כדי שהמחיר והכפתור ייכנסו למסך הראשון בנייד. אותו טקסט
    mi = re.search(r'\n<ul class="ident">.*?</ul>', p, re.S); assert mi
    ident = mi.group(0); p = p.replace(ident, "", 1)
    mc = re.search(r'\n<p class="cta-bonus">.*?</p>', p, re.S); assert mc
    p = p[:mc.end()] + ident + p[mc.end():]
    # 1 פתיחה, 6 מה אומרים (עדויות), 8 ההצעה, ואז השאר בסדר המקורי.
    # 7 ("רגע לפני" - "לפני שאתה ממשיך למחיר...") יוצא: אחרי שההצעה עולה למקום 3 הנוסח שלו כבר לא נכון. לאישור הראשי
    p = reorder(p, ["1", "6", "8", "2", "3", "4", "5", "9", "10", "11", "12", "13", "14", "15"], 15)
    # המספרים הגדולים שמוצגים ליד כל סקשן (data-num, ב-CSS) - מחדש לפי הסדר החדש: 01, 02...
    n = iter(range(1, 99)); p = re.sub(r'data-num="\d+"', lambda m: 'data-num="%02d"' % next(n), p)
    return p

if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    for name, fn in (("pr2v3", build_pr2), ("a5v3", build_a5)):
        p = fn(); open(os.path.join(OUTDIR, name + ".html"), "w", encoding="utf8").write(p)
        print(name, len(p), "sections:", re.findall(r'data-sec="(\d+)" data-name="([^"]+)"', p))
