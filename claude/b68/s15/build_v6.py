# ב85 (בן 12.11, אישור בצילום 09:49 - גובר על הגרסה הקודמת של ההנחיות): a5v6 = a5v4 כמו שהוא, עם 2 שינויים בלבד:
#   1. ע21 (סרטון הסיור) בדיוק בין "👇 תגלול ותראה בעצמך מה מחכה לך בפנים." לבין "הצצה פנימה" - המקום של inside_tour
#      שכבר קיים ב-a5v4 (slot t21 ב-slots.json, או --t21=קובץ:פוסטר:רוחב:גובה). בלי קובץ - לא מוצג, כמו ב-a5v4.
#   2. כל כפתורי ההצטרפות, כולל הכפתור הצמוד, ירוקים כמו ב-pr2 (#18845A), רטט חזק כל 2.5 ש' (keyframes shk של pr2) וברק שמופיע ונעלם
#      כל כמה שניות (הברק של a5v4, עכשיו גם בכפתור הצמוד). הכפתור הצמוד נשאר מוצג לאורך כל הגלילה אחרי כפתור הפתיחה.
#      שורת "תשלום מאובטח" עם המנעול נשארת בתוך הכפתור כמו ב-a5v4. רק transform/opacity (בלי ה-ring של pr2, שמנפיש צל). כבוי בהפחתת תנועה.
#   אזור הקורס והבונוסים - בלי שינוי. a5v4 ו-a5v5 לא משתנים.
# הרצה: python3 build_v6.py <שורש ריפו של main> <תיקיית יעד> [--noindex] [--suffix=s] [--t21=src:poster:w:h]
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_v4 as B4
import stages as STG

CSS = """
/* ב85: כפתורי ההצטרפות ירוקים כמו ב-pr2. הצורה, השורה "תשלום מאובטח" והברק - של a5v4 */
body a.cta{background:#18845A;background-image:none;color:#fff;filter:none;
  box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18)}
body a.cta:hover,body a.cta:focus-visible{background:#136B49;filter:none;box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18)}
body a.cta .ct-t,body a.cta .st-txt,body a.cta > span{color:#fff}
body a.cta s.was{color:rgba(255,255,255,.72);text-decoration-color:rgba(255,255,255,.72)}
body a.cta .v4-pay{color:rgba(255,255,255,.9)}
/* overflow:clip ולא hidden: עם hidden הברק (::after שזז מחוץ לכפתור) יוצר גלילה פנימית בכפתור הצמוד, והתוכן קפץ הצידה (CLS 0.015-0.024) */
body a.cta{overflow:hidden;overflow:clip}
html .sticky a.cta{background:#18845A;box-shadow:0 10px 26px rgba(24,132,90,.34),inset 0 1px 0 rgba(255,255,255,.18)}
/* רטט חזק (ה-keyframes של pr2, transform בלבד) */
@keyframes v6shk{0%,100%{transform:translate3d(0,0,0)}10%{transform:translate3d(-7px,0,0) rotate(-1.6deg)}20%{transform:translate3d(7px,0,0) rotate(1.6deg)}30%{transform:translate3d(-6px,0,0) rotate(-1.2deg)}40%{transform:translate3d(6px,0,0) rotate(1.2deg)}50%{transform:translate3d(-3px,0,0)}60%{transform:translate3d(3px,0,0)}70%{transform:translate3d(0,0,0)}}
body a.cta.v6shk{animation:v6shk .72s cubic-bezier(.36,.07,.19,.97) 1}
@media (prefers-reduced-motion:reduce){body a.cta.v6shk{animation:none}}
"""

JS = r"""<script>/* ב85: רטט חזק כל 2.5 ש' - הכפתור הבולט במסך (90%+) והכפתור הצמוד; ברק גם בכפתור הצמוד; הכפתור הצמוד נשאר אחרי כפתור הפתיחה. כבוי בהפחתת תנועה / ?shake=0 */
(function(){var q=new URLSearchParams(location.search),RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
 var st=document.getElementById("sticky"),sa=st&&st.querySelector("a.cta"),sp=document.getElementById("spModal"),hc=document.querySelector('[data-sec="1"] [data-cta="hero_main"]');
 /* הכפתור הצמוד: מוצג מרגע שכפתור הפתיחה יצא מהמסך, ולא נעלם באזורי הקנייה */
 if(st&&hc){var keep=function(){if(hc.getBoundingClientRect().bottom<0&&!st.classList.contains("on")){st.classList.add("on");st.setAttribute("aria-hidden","false");}};
  new MutationObserver(keep).observe(st,{attributes:true,attributeFilter:["class"]});addEventListener("scroll",keep,{passive:true});keep();}
 if(RM)return;
 if(sa)sa.classList.add("v4-shine");
 if(!("IntersectionObserver" in window)||q.get("shake")==="0")return;
 var inPage=[].slice.call(document.querySelectorAll("a.cta")).filter(function(b){return !b.closest(".sticky,.sp-modal");}),vis=new Map();
 var sio=new IntersectionObserver(function(es){es.forEach(function(x){vis.set(x.target,x.intersectionRatio);});},{threshold:[0,.5,.9,1]});
 inPage.forEach(function(b){sio.observe(b);});
 function shake(b){b.classList.remove("v6shk");void b.offsetWidth;b.classList.add("v6shk");b.addEventListener("animationend",function e(ev){if(ev.animationName==="v6shk"){b.classList.remove("v6shk");b.removeEventListener("animationend",e);}});}
 setInterval(function(){if(document.visibilityState!=="visible"||(sp&&!sp.hidden))return;
  var best=null,br=.9;inPage.forEach(function(b){var r=vis.get(b)||0;if(r>=br){br=r;best=b;}});
  if(best)shake(best);
  if(st&&sa&&st.classList.contains("on"))shake(sa);},2500);
})();</script>"""

def green(p):
    p = p.replace("</head>", "<style>" + CSS + "</style>\n</head>", 1)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    return p

def t21():
    a = B4.ARG.get("t21")
    if not a: return
    src, poster, w, h = a.split(":")
    B4.SLOTS["t21"].update(src=src, poster=poster, w=int(w), h=int(h))

def build():
    t21()
    p = B4.v4(B4.build_v3.build_a5(), "a5", "a5v3", "a5v6")
    p = STG.tag_a5v4(p)
    p = green(p)
    assert p.count('data-variant="a5v6"') == 1
    return p

if __name__ == "__main__":
    os.makedirs(B4.OUT, exist_ok=True)
    p = build()
    open(os.path.join(B4.OUT, "a5v6" + B4.SUFFIX + ".html"), "w", encoding="utf8").write(p)
    print("a5v6", len(p), "ctas:", len(re.findall(r'<a class="cta"[^>]*data-cta=', p)), "tour:", 'data-v4tour' in p)
