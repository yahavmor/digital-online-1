# ב68, תוכנית ראשון 15.11: v4 = v3 (סדר ומהירות) + הרשימה של בן:
#   כפתורים בולטים ומודרניים, מנעול ו"תשלום מאובטח" ליד המחיר וההצעה, סקשנים שנכנסים בעדינות בגלילה,
#   צללים ורקעים יוקרתיים, גלילה ומעברים חלקים. ובנוסף מקומות מוכנים לשלושה נכסים (slots.json).
# תנאים: המסך הראשון בלי אנימציה, אנימציות רק ב-CSS עם IntersectionObserver, כיבוי בהפחתת תנועה,
#   בלי קפיצות בפריסה, LCP במובייל עד 1.5 ש'. אותו קופי ואותה מדידה כמו v3 (ובלי טקסט חדש, חוץ מ"תשלום מאובטח").
# הרצה: python3 claude/b68/s15/build_v4.py <שורש ריפו של main> <תיקיית יעד> [--preview] [--noindex] [--slots=קובץ] [--suffix=s]
#   --preview: מסמן את המקומות הריקים במסגרת עם שם (רק למעבדה ולצילומי המסך). בלי הדגל, מקום בלי קובץ לא נכנס לדף.
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_v3

SRC = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; PREVIEW = "--preview" in sys.argv
NOINDEX = "--noindex" in sys.argv  # דפי בדיקה לבן לפני ראשון (מאשר ב68 - דפי בדיקה): noindex, לא מחוברים ל-go.html
build_v3.ROOT = SRC
ARG = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--") and "=" in a)
SLOTS = json.load(open(ARG.get("slots", os.path.join(HERE, "slots.json")), encoding="utf8"))
SUFFIX = ARG.get("suffix", "")
FONT_DISPLAY = ARG.get("font", "optional")  # optional: אם הגופן לא הגיע לפני הציור הראשון, נשארים בגופן הגיבוי - בלי קפיצה  # לבדיקות: שם קובץ אחר (למשל a5v4s.html), אותו data-variant

LOCK = '<svg class="v4-li" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.4-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>'

# ---------- CSS משותף. צבעים לפי הדף: a5 כהה וזהב, pr2 ירוק על לבן וכחול לילה ----------
CSS_COMMON = """
/* ===== ב68 v4: שכבת פרימיום (CSS בלבד; המסך הראשון בלי אנימציה) ===== */
html{scroll-padding-top:12px}
[data-sec]{scroll-margin-top:12px}
.cta{position:relative;isolation:isolate;overflow:hidden;min-height:64px;border-radius:16px;letter-spacing:-.005em;
  transition:transform .25s var(--ease),box-shadow .25s var(--ease),filter .25s var(--ease),background-color .25s var(--ease)}
.cta::before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:-1;
  background:linear-gradient(180deg,rgba(255,255,255,.26),rgba(255,255,255,0) 55%)}
.cta::after{content:"";position:absolute;top:0;bottom:0;inset-inline-start:0;width:42%;border-radius:inherit;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.5),transparent);opacity:0}
.cta.v4-shine::after{animation:v4shine 1.15s var(--ease) .15s 1 backwards}
@keyframes v4shine{0%{opacity:0;transform:translateX(130%) skewX(-18deg)}20%{opacity:1}100%{opacity:0;transform:translateX(-260%) skewX(-18deg)}}
.cta > span:last-child,.cta .ar{transition:transform .25s var(--ease)}
.cta:hover > span:last-child,.cta:focus-visible > span:last-child,.cta:hover .ar,.cta:focus-visible .ar{transform:translateX(-5px)}
.cta:active{transform:translateY(1px) scale(.99)}
.v4-lock{display:inline-flex;align-items:center;gap:5px;font-weight:700;white-space:nowrap}
.v4-li{width:15px;height:15px;flex:none;fill:none;stroke:var(--v4-ok);stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round;vertical-align:-2px}
.secure .v4-li,.secure li svg{stroke:var(--v4-ok)}
.v4-sec{display:flex;justify-content:center;margin:12px auto 0;font-size:14px;line-height:1.4}
.v4-sec .v4-lock{padding:6px 13px;border-radius:999px;border:1px solid var(--v4-okb);background:var(--v4-okbg);color:var(--v4-okt)}
.sticky .cta{min-height:56px}
/* מקומות לנכסים: גודל קבוע מראש (aspect-ratio) - אין קפיצה כשהתמונה נטענת */
.v4-slot{margin:26px auto 0;max-width:300px;width:100%}
.v4-slot-h{margin:0 0 14px;text-align:center;font-weight:800;font-size:20px;line-height:1.4;text-wrap:balance}
@media (min-width:960px){.v4-slot{max-width:340px}}
.v4-slot.v4-img{max-width:440px}
.v4-slot .v4-box{position:relative;display:block;width:100%;padding:0;border:0;border-radius:20px;overflow:hidden;background:var(--v4-slotbg);
  box-shadow:var(--v4-card);cursor:pointer;-webkit-tap-highlight-color:transparent}
.v4-slot img,.v4-slot video{display:block;width:100%;height:100%;object-fit:cover}
.v4-slot .v4-pi{position:absolute;inset:0;margin:auto;width:68px;height:68px;border-radius:50%;display:grid;place-items:center;
  background:rgba(255,255,255,.92);box-shadow:0 10px 30px rgba(0,0,0,.35);transition:transform .25s var(--ease)}
.v4-slot .v4-pi svg{width:30px;height:30px;fill:#111;margin-inline-start:4px}
.v4-slot .v4-box:hover .v4-pi,.v4-slot .v4-box:focus-visible .v4-pi{transform:scale(1.06)}
.v4-slot .v4-box:focus-visible{outline:3px solid var(--v4-ok);outline-offset:3px}
.v4-ph{position:absolute;inset:0;display:grid;place-items:center;padding:18px;text-align:center;font:700 15px/1.5 var(--font,Heebo,sans-serif);
  color:var(--v4-okt);border:2px dashed var(--v4-okb);border-radius:20px}
/* כניסה עדינה בגלילה: רק מה שמתחת למסך הראשון, רק עם IntersectionObserver, ולא בהפחתת תנועה */
html.v4rv .v4r:not(.in){opacity:0;transform:translate3d(0,22px,0)}
html.v4rv .v4r{transition:opacity .6s var(--ease),transform .7s var(--ease)}
@media (prefers-reduced-motion:reduce){
  html.v4rv .v4r:not(.in){opacity:1;transform:none}
  html.v4rv .v4r,.cta,.cta > span:last-child,.cta .ar{transition:none}
  .cta.v4-shine::after{animation:none}
}
"""

CSS_PAGE = {
"a5": """
:root{--v4-ok:#43C08A;--v4-okb:rgba(67,192,138,.38);--v4-okbg:rgba(67,192,138,.08);--v4-okt:#CDEFDF;--v4-slotbg:#111319;
  --v4-card:0 0 0 1px rgba(211,183,122,.22),0 30px 70px -30px rgba(0,0,0,.85)}
.cta{background:linear-gradient(180deg,#F0E2BE 0%,#D9BE83 48%,#C6A266 100%);
  box-shadow:0 1px 0 rgba(255,255,255,.55) inset,0 -2px 0 rgba(120,90,40,.25) inset,0 0 0 1px rgba(234,219,181,.4),0 16px 36px -14px rgba(211,183,122,.75),0 4px 10px rgba(0,0,0,.35)}
.cta:hover{filter:brightness(1.05);box-shadow:0 1px 0 rgba(255,255,255,.55) inset,0 -2px 0 rgba(120,90,40,.25) inset,0 0 0 1px rgba(234,219,181,.55),0 22px 46px -14px rgba(211,183,122,.9),0 6px 14px rgba(0,0,0,.4)}
.pcard{border-radius:28px;border-color:rgba(211,183,122,.42);
  background:radial-gradient(120% 60% at 50% 0%,rgba(211,183,122,.12),transparent 60%),linear-gradient(180deg,rgba(211,183,122,.07),rgba(255,255,255,.015));
  box-shadow:0 0 0 1px rgba(234,219,181,.08) inset,0 1px 0 rgba(255,255,255,.08) inset,0 70px 130px -50px rgba(0,0,0,.95),0 0 80px -30px rgba(211,183,122,.25)}
section[data-sec]+section[data-sec]{box-shadow:0 1px 0 rgba(211,183,122,.07) inset}
section.alt{background-image:radial-gradient(700px circle at 88% 0%,rgba(201,169,110,.07),transparent 60%),radial-gradient(640px circle at 12% 100%,rgba(201,169,110,.05),transparent 62%)}
.sticky{-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
/* המסך הראשון מוצג מיד: בלי אנימציית הכניסה של הפתיחה (בדף החי הכותרת, הכפתור והתמונה נכנסים בהדרגה) */
.hero8 .copy>*,.hero8 .visual,.hero9 .copy>*{animation:none}
#offer .secure{margin-top:14px}
""",
"pr2": """
:root{--v4-ok:#1F9A68;--v4-okb:rgba(24,132,90,.30);--v4-okbg:rgba(24,132,90,.07);--v4-okt:#17694A;--v4-slotbg:#EEF0EC;
  --v4-card:0 1px 2px rgba(16,24,39,.06),0 12px 28px rgba(16,24,39,.10),0 34px 70px -20px rgba(16,24,39,.22)}
.dark{--v4-ok:#43C08A;--v4-okb:rgba(67,192,138,.38);--v4-okbg:rgba(67,192,138,.08);--v4-okt:#CDEFDF;--v4-slotbg:#172235}
.cta{background:linear-gradient(180deg,#22A570 0%,#18845A 55%,#136B49 100%);
  box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.14) inset,0 14px 30px -12px rgba(24,132,90,.65),0 3px 8px rgba(16,24,39,.16)}
.cta:hover{background:linear-gradient(180deg,#25B07A 0%,#1A8E61 55%,#147350 100%);box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.14) inset,0 20px 40px -12px rgba(24,132,90,.75),0 5px 12px rgba(16,24,39,.2)}
.dark .cta{box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.18) inset,0 0 0 1px rgba(67,192,138,.35),0 18px 40px -12px rgba(31,154,104,.6)}
.offer .pricebox{border-top-color:rgba(216,166,78,.28)}
.white{background:radial-gradient(900px 420px at 100% 0%,rgba(216,166,78,.06),transparent 60%),var(--paper)}
main > section:not(.white):not(.dark){background-image:radial-gradient(800px 380px at 0% 0%,rgba(16,24,39,.035),transparent 60%)}
""",
}

# ---------- JS: כניסה עדינה לסקשנים שאין בהם עדיין אנימציה, ברק אחד על כפתור כשהוא נכנס למסך, וטעינת משקלי הגופן מראש ----------
JS = """<script>/* ב68 v4: (1) כניסה עדינה בגלילה למה שמתחת למסך הראשון ועוד לא מונפש בדף - רק IntersectionObserver ו-CSS, לא בהפחתת תנועה.
   מה שכבר במסך בטעינה לא מוסתר בכלל. (2) ברק אחד על כפתור כשהוא נכנס במלואו למסך (CSS). (3) המקומות לסרטונים: הסרטון נטען רק בלחיצה. */
(function(){var RM=matchMedia("(prefers-reduced-motion: reduce)").matches,IO="IntersectionObserver" in window,root=document.documentElement;
 if(IO&&!RM){var vh=innerHeight,els=[];
  document.querySelectorAll("[data-sec]").forEach(function(s){if(s.dataset.sec==="1")return;
   [].forEach.call(s.querySelectorAll(":scope > .wrap > *, :scope > div > .wrap > *, :scope > .wrap > .stack > *"),function(e){
    if(e.closest(".rv,.v4r")||e.querySelector(".rv,.in")||/^(SCRIPT|STYLE)$/.test(e.tagName)||e.classList.contains("rv"))return;
    if(e.getBoundingClientRect().top<vh*0.98)return; e.classList.add("v4r");els.push(e);});});
  root.classList.add("v4rv");
  var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting||x.boundingClientRect.top<0){x.target.classList.add("in");io.unobserve(x.target);}});},{rootMargin:"0px 0px -6% 0px"});
  els.forEach(function(e){io.observe(e);});
  /* גלילה מהירה או קפיצה לעוגן (#offer): מה שכבר מעל תחתית המסך נחשף, כדי ששום דבר לא יישאר מוסתר */
  /* חל גם על אנימציות הכניסה שכבר קיימות בדף (.rv, נחשפות עם אותו קלאס in) */
  var pend=false;addEventListener("scroll",function(){if(pend)return;pend=true;requestAnimationFrame(function(){pend=false;var h=innerHeight;
   [].forEach.call(document.querySelectorAll(".v4r:not(.in),.rv:not(.in)"),function(e){if(e.getBoundingClientRect().top<h){e.classList.add("in");io.unobserve(e);}});});},{passive:true});
  var io2=new IntersectionObserver(function(es){es.forEach(function(x){if(x.intersectionRatio>=.95){x.target.classList.add("v4-shine");io2.unobserve(x.target);}});},{threshold:[.95]});
  document.querySelectorAll("a.cta").forEach(function(b){if(b.dataset.cta!=="sticky")io2.observe(b);});}
 /* תמונות שמחכות לתמונה הראשית (data-v4src על img) */
 (function(){var done=false;function rel(){if(done)return;done=true;[].forEach.call(document.querySelectorAll("img[data-v4src]"),function(i){i.src=i.dataset.v4src;i.removeAttribute("data-v4src");});}
  var h=document.querySelector('[data-sec="1"] img[fetchpriority="high"]');
  if(!h||h.complete)rel();else{h.addEventListener("load",rel);h.addEventListener("error",rel);}
  addEventListener("scroll",rel,{once:true,passive:true});addEventListener("touchstart",rel,{once:true,passive:true});setTimeout(rel,4000);})();
 document.querySelectorAll(".v4-slot [data-v4src]").forEach(function(b){b.addEventListener("click",function(){
  var v=document.createElement("video");v.src=b.dataset.v4src;v.controls=true;v.playsInline=true;v.setAttribute("playsinline","");v.poster=b.dataset.v4poster||"";
  var k=b.closest(".v4-slot").dataset.slot;v.style.aspectRatio=b.style.aspectRatio;b.replaceWith(v);v.play().catch(function(){});
  try{window.__lpSend&&window.__lpSend("video_play",{video:"slot_"+k});}catch(e){}});});
})();</script>
"""


# ---------- הגופן: Heebo מהאתר עצמו (עברית ולטינית, גופן משתנה), עם preload, במקום ה-CSS של Google שחוסם את הציור ----------
# בלי זה הכותרת הראשית קופצת פעמיים כשהגופן מגיע (פעם לעברית ופעם לפיסוק), ובדף החי זה מוסתר רק בזכות אנימציית הכניסה של הפתיחה
# שני קבצים מ-Heebo המלא (גופן משתנה, מצומצם למשקלים 400-900 שבשימוש), לפי טווח ולא לפי התווים שבדף היום,
# כדי ששינויי קופי לא יציגו תו בגופן אחר: "he" = כל האותיות העבריות, ספרות, פיסוק ו-₪ (10KB, עם preload);
# "la" = אותיות לטיניות (NLP, WhatsApp...; 12KB, בלי preload). ראו fonts/README.md
FONT_RANGES = {"he": "U+0020-0040, U+005B-0060, U+007B-007E, U+00A0, U+00A9, U+00AB, U+00B0, U+00B7, U+00BB, U+00D7, U+05BE, U+05C0, U+05C3, U+05C6, U+05D0-05EA, U+05F0-05F4, U+200C-200F, U+2010-2014, U+2018-201E, U+2022, U+2026, U+2030, U+2039-203A, U+20AA",
               "la": "U+0041-005A, U+0061-007A, U+00C0-00D6, U+00D8-00F6, U+00F8-017F"}
FONT_PRELOAD = ("he",)
def self_font(p):
    n0 = len(p)
    p = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"(?: crossorigin)?>', "", p)
    m = re.search(r'\s*<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Heebo[^"]*">', p); assert m, "heebo link"
    # preload רק לעברית (10KB), כדי שעם font-display optional היא תגיע לפני הציור הראשון אצל רוב הגולשים
    pre = "".join('\n<link rel="preload" as="font" type="font/woff2" href="assets/fonts/heebo-%s.woff2" crossorigin>' % k for k in FONT_PRELOAD)
    ff = "".join('@font-face{font-family:"Heebo";font-style:normal;font-weight:400 900;font-display:%s;src:url(assets/fonts/heebo-%s.woff2) format("woff2");unicode-range:%s}' % (FONT_DISPLAY, k, r) for k, r in FONT_RANGES.items())
    p = p[:m.start()] + pre + "\n<style>" + ff + "</style>" + p[m.end():]
    assert "fonts.googleapis" not in p and len(p) != n0
    return p

# ---------- תמונות מתחת לפתיחה מחכות לתמונה הראשית ----------
# ב-v3 צילומי הוואטסאפ עלו לסקשן 2, צמוד לפתיחה, והדפדפן מוריד אותם מיד (גם עם loading=lazy) במקביל לתמונה הראשית.
# ב-3G זה דוחה את התמונה הראשית (LCP) בשנייה. לכן תמונה עצלה עם רוחב וגובה אחרי סקשן 1 מקבלת data-v4src במקום src,
# ונטענת אחרי שהתמונה הראשית נטענה, בגלילה הראשונה, או אחרי 4 שניות. הגודל קבוע מראש (width/height) - אין קפיצה.
def defer_imgs(p):
    m = re.search(r'<(header|section)\b[^>]*data-sec="1"', p); assert m
    end = p.index("</%s>" % m.group(1), m.end())
    head, tail = p[:end], p[end:]
    n = [0]
    def f(mm):
        t = mm.group(0)
        if 'loading="lazy"' not in t or ' width="' not in t or ' height="' not in t or ' src="' not in t: return t
        n[0] += 1; return t.replace(' src="', ' data-v4src="', 1)
    tail = re.sub(r"<img\b[^>]*>", f, tail)
    return head + tail, n[0]

def sec_bounds(p, name):
    m = re.search(r'<(header|section)\b[^>]*data-name="%s"[^>]*>' % re.escape(name), p); assert m, name
    end = p.index("</%s>" % m.group(1), m.end())
    return m.end(), end

def slot_html(key, cfg):
    has = bool(cfg.get("src"))
    if not has and not PREVIEW: return ""
    ar = "%d/%d" % (cfg["w"], cfg["h"])
    poster = cfg.get("poster") or ""
    if cfg["kind"] == "video":
        inner = ('<img src="%s" alt="" loading="lazy" decoding="async" width="%d" height="%d">' % (poster, cfg["w"], cfg["h"]) if poster else "")
        inner += '<span class="v4-pi">%s</span>' % PLAY if has else '<span class="v4-ph">%s</span>' % cfg["label"]
        attrs = ' data-v4src="%s" data-v4poster="%s"' % (cfg["src"], poster) if has else ""
        box = '<button type="button" class="v4-box" style="aspect-ratio:%s" aria-label="%s"%s>%s</button>' % (ar, cfg.get("aria", "הפעלת הסרטון"), attrs, inner)
    else:
        inner = ('<img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">' % (cfg["src"], cfg.get("alt", ""), cfg["w"], cfg["h"])) if has else '<span class="v4-ph">%s</span>' % cfg["label"]
        box = '<div class="v4-box" style="aspect-ratio:%s;cursor:auto">%s</div>' % (ar, inner)
    # כותרת מעל הנכס (למשל סרטון ההמלצות, בנוסח של בן), רק כשהנכס עצמו בדף
    head = '<p class="v4-slot-h">%s</p>' % cfg["title"] if cfg.get("title") else ""
    return '<figure class="v4-slot%s" data-slot="%s">%s%s</figure>' % (" v4-img" if cfg["kind"] == "image" else "", key, head, box)

def place_slots(p, page):
    for key, cfg in SLOTS.items():
        if key.startswith("_"): continue
        where = cfg["where"][page]; h = slot_html(key, cfg)
        if not h: continue
        a, b = sec_bounds(p, where["section"])
        if where["at"] == "after_h2":
            m = re.compile(r"</h2>").search(p, a, b); assert m, (key, page)
            # אחרי הכותרת ואחרי פסקת הפתיחה שצמודה לה, אם יש
            m2 = re.compile(r"\s*<p class=\"(?:lead|sub|offer-lead)\">.*?</p>", re.S).match(p, m.end())
            at = m2.end() if m2 else m.end()
        elif where["at"] == "end":
            at = p.rfind("</div>", a, b); assert at > a
        p = p[:at] + "\n" + h + p[at:]
    return p

def lock_everywhere(p):
    # "תשלום מאובטח" עם מנעול אחיד (SVG במקום אימוג'י), בכל מקום שהוא כבר מופיע ליד כפתור או מחיר
    p = p.replace("🔒 תשלום מאובטח", '<span class="v4-lock">%sתשלום מאובטח</span>' % LOCK)
    p = re.sub(r'(?<![>"])(?<!</svg>)תשלום מאובטח(?![^<]*</span>)', '<span class="v4-lock">%sתשלום מאובטח</span>' % LOCK, p)
    # כפתור (חוץ מהדביק) שאין אחריו "תשלום מאובטח" קרוב: מוסיפים שורה קטנה עם מנעול מתחת לכפתור
    out, last = [], 0
    for m in re.finditer(r'<a class="cta[^"]*" data-cta="([a-z_0-9]+)"[^>]*>.*?</a>', p, re.S):
        if m.group(1) == "sticky": continue
        near = p[m.end():m.end() + 900]
        near = near[:near.find("<a class=\"cta")] if "<a class=\"cta" in near else near
        if "תשלום מאובטח" in near: continue
        out.append(p[last:m.end()]); out.append('\n<p class="v4-sec"><span class="v4-lock">%sתשלום מאובטח</span></p>' % LOCK); last = m.end()
    out.append(p[last:]); return "".join(out)

def v4(p, page, old, new):
    assert p.count('data-variant="%s"' % old) == 1
    p = p.replace('data-variant="%s"' % old, 'data-variant="%s"' % new)
    if page == "a5":
        # בהצעה: רשימת "תשלום מאובטח / גישה מיידית" עוברת אל מתחת לכפתור, לפני הקישור לוואטסאפ (אותו טקסט)
        ms = re.search(r'\s*<ul class="secure">.*?</ul>', p, re.S); assert ms
        sec = ms.group(0); p = p.replace(sec, "", 1)
        a, b = sec_bounds(p, "ההצעה")
        mc = re.compile(r'<a class="cta"[^>]*data-cta="offer"[^>]*>.*?</a>', re.S).search(p, a, b); assert mc
        p = p[:mc.end()] + sec + p[mc.end():]
    p = self_font(p)
    p = lock_everywhere(p)
    p = place_slots(p, page)
    p, nd = defer_imgs(p); assert nd >= 3, nd
    # בלוק נפרד בסוף ה-head, אחרי ה-CSS של הדף, כדי שהשכבה של v4 תגבר עליו
    assert p.count("</head>") == 1
    p = p.replace("</head>", "<style>" + CSS_COMMON + CSS_PAGE[page] + "</style>\n</head>", 1)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    if NOINDEX:
        assert 'name="robots"' not in p
        p = p.replace('<meta name="viewport"', '<meta name="robots" content="noindex,nofollow"><meta name="viewport"', 1); assert 'name="robots"' in p
    for k in ("TRACK_ENDPOINT", "fbq(", "clarity", "NLP_OWNER", "InitiateCheckout"):
        assert k in p, "measurement missing: " + k
    return p

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    import shutil; os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    for k in FONT_RANGES: shutil.copy(os.path.join(HERE, "fonts", "heebo-%s.woff2" % k), os.path.join(OUT, "assets", "fonts"))
    for page, fn, old in (("pr2", build_v3.build_pr2, "pr2v3"), ("a5", build_v3.build_a5, "a5v3")):
        new = page + "v4"; p = v4(fn(), page, old, new)
        open(os.path.join(OUT, new + SUFFIX + ".html"), "w", encoding="utf8").write(p)
        print(new, len(p), "slots:", re.findall(r'data-slot="(\w+)"', p), "locks:", p.count('class="v4-lock"'), "added lines:", p.count('class="v4-sec"'))
