# ב85 (בן 12.11): a5v5 "נהרס מבחינת המבנה והעיצוב" - חוזרים לגרסה הקודמת. דף בדיקה a5v6 מתוך סקריפט הבנייה של a5v4:
#   אותו סדר, קופי ועיצוב כמו a5v4 (כולל תגיות המדידה section_view). בלי 13 השלבים, משפטי המעבר, לולאת הפתיחה והרצועה.
#   אזור הקורס וההצעה כבר בסדר של בן ב-a5v4 (נבדק ב-t_v6.js): מה יש בפנים, 👇, ע21 (כשיגיע), ע20, "וזה עוד לפני שדיברנו...",
#   הבונוסים עם התכנים והערכים, וסיכום ההצעה (שווי, מחיר מחוק, 297, כפתור).
#   השינוי היחיד: כל כפתורי ההצטרפות כמו הכפתורים הירוקים של pr2, אחד לאחד - #18845A, רטט + ring באותו מחזור (shk, ring, כל ~4 ש'),
#   ו"🔒 תשלום מאובטח" מתחת לכפתור (ב-pr2 אין שורה כזו בכפתור הצמוד, ולכן גם כאן לא). data-cta והקישורים לסליקה בלי שינוי.
# a5v4 ו-a5v5 לא משתנים. הרצה: python3 build_v6.py <שורש ריפו של main> <תיקיית יעד> [--noindex] [--suffix=s]
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_v4 as B4
import stages as STG

PAY = re.compile(r'<span class="v4-pay"><svg class="v4-li"[^>]*>.*?</svg>תשלום מאובטח</span>', re.S)
LOCK = '<p class="v6-lock">🔒 תשלום מאובטח</p>'

CSS = """
/* ב85: כפתורי ההצטרפות כמו ב-pr2, אחד לאחד */
body a.cta{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:nowrap;width:100%;max-width:470px;min-height:60px;margin-inline:auto;
  padding:14px 22px;border:0;border-radius:14px;background:#18845A;background-image:none;color:#fff;font-weight:800;font-size:18px;line-height:1.3;
  text-align:center;text-decoration:none;text-shadow:none;letter-spacing:normal;filter:none;overflow:visible;
  box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18);transition:background-color .2s,transform .2s;-webkit-tap-highlight-color:transparent}
body a.cta:hover{background:#136B49;transform:none;filter:none;box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18)}
body a.cta:active{transform:translateY(1px)}
body a.cta::before,body a.cta::after{display:none;content:none;animation:none}
body a.cta.pulse1{animation:none}
body a.cta,body a.cta *{color:#fff}
body a.cta .ct-t,body a.cta .st-txt{color:#fff;font-weight:800}
body a.cta s.was{color:rgba(255,255,255,.72);text-decoration-color:rgba(255,255,255,.72)}
html .sticky a.cta{min-height:54px;font-size:18px;max-width:420px;margin-inline:auto;border-radius:14px;padding:12px 18px;box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18)}
@keyframes shk{0%,100%{transform:translate3d(0,0,0)}10%{transform:translate3d(-7px,0,0) rotate(-1.6deg)}20%{transform:translate3d(7px,0,0) rotate(1.6deg)}30%{transform:translate3d(-6px,0,0) rotate(-1.2deg)}40%{transform:translate3d(6px,0,0) rotate(1.2deg)}50%{transform:translate3d(-3px,0,0)}60%{transform:translate3d(3px,0,0)}70%{transform:translate3d(0,0,0)}}
@keyframes ring{0%{box-shadow:0 10px 26px rgba(24,132,90,.34),0 0 0 0 rgba(233,196,126,.75)}100%{box-shadow:0 10px 26px rgba(24,132,90,.34),0 0 0 16px rgba(233,196,126,0)}}
body a.cta.shk{animation:shk .72s cubic-bezier(.36,.07,.19,.97) 1,ring .9s ease-out 1}
@media (prefers-reduced-motion:reduce){body a.cta.shk{animation:none}}
html body p.v6-lock{margin:8px auto 0;font-size:14px;line-height:1.4;font-weight:400;color:var(--muted,#B8B8B8);text-align:center;max-width:none}
"""

JS = r"""<script>/* ב85: רטט כמו ב-pr2 - כל ~4 ש', הכפתור הבולט במסך (90%+) והכפתור הצמוד כשהוא מוצג. ויזואלי בלבד. כבוי בהפחתת תנועה / ?shake=0 */
(function(){var q=new URLSearchParams(location.search),RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
 if(!("IntersectionObserver" in window)||RM||q.get("shake")==="0")return;
 var st=document.getElementById("sticky"),sa=st&&st.querySelector("a.cta"),sp=document.getElementById("spModal");
 var inPage=[].slice.call(document.querySelectorAll("a.cta")).filter(function(b){return !b.closest(".sticky,.sp-modal");}),vis=new Map();
 var sio=new IntersectionObserver(function(es){es.forEach(function(x){vis.set(x.target,x.intersectionRatio);});},{threshold:[0,.5,.9,1]});
 inPage.forEach(function(b){sio.observe(b);});
 function shake(b){b.classList.remove("shk");void b.offsetWidth;b.classList.add("shk");b.addEventListener("animationend",function e(ev){if(ev.animationName==="ring"){b.classList.remove("shk");b.removeEventListener("animationend",e);}});}
 setInterval(function(){if(document.visibilityState!=="visible"||(sp&&!sp.hidden))return;
  var best=null,br=.9;inPage.forEach(function(b){var r=vis.get(b)||0;if(r>=br){br=r;best=b;}});
  if(best)shake(best);
  if(st&&sa&&st.classList.contains("on"))shake(sa);},4000);
})();</script>"""

def green(p):
    n = len(re.findall(r'<a class="cta"[^>]*data-cta=', p))
    p, k = PAY.subn("", p)
    assert k == n, (k, n)  # כל כפתור הצטרפות הכיל "תשלום מאובטח" בתוכו - עובר אל מתחת לכפתור
    out, i, added = [], 0, 0
    for m in re.finditer(r'<a class="cta"[^>]*data-cta="([^"]+)"[^>]*>.*?</a>', p, re.S):
        out.append(p[i:m.end()]); i = m.end()
        before = p[max(0, m.start() - 300):m.start()]
        if m.group(1) == "sticky": continue
        out.append(LOCK); added += 1
    out.append(p[i:]); p = "".join(out)
    assert added == n - 1, (added, n)
    p = p.replace("</head>", "<style>" + CSS + "</style>\n</head>", 1)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    return p

def build():
    p = B4.v4(B4.build_v3.build_a5(), "a5", "a5v3", "a5v6")
    p = STG.tag_a5v4(p)
    p = green(p)
    assert p.count('data-variant="a5v6"') == 1
    return p

if __name__ == "__main__":
    os.makedirs(B4.OUT, exist_ok=True)
    p = build()
    open(os.path.join(B4.OUT, "a5v6" + B4.SUFFIX + ".html"), "w", encoding="utf8").write(p)
    print("a5v6", len(p), "ctas:", re.findall(r'<a class="cta"[^>]*data-cta="([^"]+)"', p), "locks:", p.count('class="v6-lock"'))
