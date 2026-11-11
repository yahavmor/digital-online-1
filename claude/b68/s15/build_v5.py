# ב83 (בקשת בן 11.11, ראשי): דף בדיקה a5v5 מתוך סקריפט הבנייה של a5v4. a5v4 לא משתנה.
# המפרט: claude/sales-page-plan-1111.md (סעיפים 3-6).
#   3 סדר: פתיחה (לולאת וידאו מוכהה + "צפו בסרטון עם קול") / מה אם + h2 / השינוי האמיתי, ההפסקה, אתה כבר יודע + know /
#     מה באמת השתנה אצלם / ככה מרגיש יום רגיל / מה יש בפנים / בונוסים / #offer / "עוד כמה דקות עם בן" (רצועת 5) /
#     למה בניתי / למי מתאימה / מה ישתנה + cta2 / איך מתחילים + cta3 / שאלות / אחריות + final.
#   4 סרטונים מ-slots_v5.json (קוד, קובץ, פוסטר) - מחליפים סדר בלי שינוי קוד. preload=none, רק אחד מתנגן, נעצר מחוץ למסך,
#     אירוע video_play עם הקוד (v5_<code>). אין <video> ב-HTML - נוצרים ב-JS, כך שמספרי הסרטונים הקיימים במדידה לא זזים.
#   5 אנימציות: transform/opacity בלבד, לא במסך הראשון ולא על ה-LCP, כבויות בהפחתת תנועה, התוכן גלוי בלי JS.
# בלי טקסט חדש ובלי שינוי מחיר, חוץ מ"עוד כמה דקות עם בן" ו"צפו בסרטון עם קול". noindex, לא ב-go.html ולא בניסוי.
# הרצה: python3 claude/b68/s15/build_v5.py <שורש ריפו של main> <תיקיית יעד> [--noindex] [--v5slots=קובץ] [--suffix=s]
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_v4 as B4  # אותו argv: SRC, OUT, --noindex, --slots, --suffix, --preview

V5 = json.load(open(B4.ARG.get("v5slots", os.path.join(HERE, "slots_v5.json")), encoding="utf8"))
STRIP_TITLE = "עוד כמה דקות עם בן"
SOUND_LABEL = "צפו בסרטון עם קול"
PLAY = B4.PLAY

ORDER = ["מה אם", "מה אומרים", "@cta1", "רגע לפני", "לדעת או להטמיע", "תוצאות אמיתיות", "איך נראית המציאות",
         "מה יש בפנים", "בונוסים", "ההצעה", "@strip", "למה בניתי", "למי מתאים", "עם מה תצא", "@cta2",
         "איך מתחילים", "@cta3", "שאלות", "@final"]

def vid_html(item, cls="v5-vid"):
    # פוסטר + כפתור הפעלה; הסרטון נוצר רק בלחיצה (preload=none בפועל)
    return ('<figure class="%s" data-v5code="%s"><button type="button" class="v5-box" style="aspect-ratio:%d/%d" aria-label="הפעלת הסרטון" data-v5src="%s">'
            '<img src="%s" alt="" loading="lazy" decoding="async" width="%d" height="%d"><span class="v4-pi">%s</span></button></figure>'
            % (cls, item["code"], item["w"], item["h"], item["src"], item["poster"], item["w"], item["h"], PLAY))

def has(item): return bool(item and item.get("src"))

def blocks(p):
    # הבלוקים העליונים בין הפתיחה לפוטר: סקשנים לפי data-name, כפתורי ביניים (ctab) וסקשן האחריות
    a = p.index("</header>") + len("</header>")
    first = p.index("<section", a); end = p.index("<footer", first)
    out = {}; i = first
    for m in re.finditer(r'<section\b[^>]*>', p[first:end]):
        s = first + m.start()
        if s < i: continue
        e = p.index("</section>", s) + len("</section>")
        tag = m.group(0); body = p[s:e]
        n = re.search(r'data-name="([^"]*)"', tag)
        if n: key = n.group(1)
        elif 'class="guar"' in tag: key = "@final"
        else:
            c = re.search(r'data-cta="(cta\d)"', body); assert c, tag; key = "@" + c.group(1)
        assert key not in out, key
        out[key] = body; i = e
    rest = re.sub(r'<section\b.*?</section>', "", p[first:end], flags=re.S)
    assert not rest.strip(), rest[:200]
    return first, end, out

def strip_section():
    items = [x for x in V5.get("strip", []) if has(x)]
    if not items: return ""
    figs = "".join(vid_html(x, "v5-vid v5-sv") for x in items)
    btn = ('<div class="v4-ctab"><a class="cta" data-cta="strip" data-checkout href="#"><span class="ct-t">כן, אני רוצה להתחיל עכשיו <span class="pgrp">ב-<s class="was">1,290</s> 297 ₪</span></span> <span>←</span>'
           '<span class="v4-pay">%sתשלום מאובטח</span></a><p class="cta-micro"><b class="launch">מחיר השקה לזמן מוגבל</b> · גישה מיידית לקורס ולבונוסים · החזר מלא תוך 7 ימים</p></div>') % B4.LOCK
    return ('<section data-num="00" class="alt v5-strip-sec" data-sec="0" data-name="%s"><div class="wrap stack">\n<h2>%s</h2>\n'
            '<div class="v5-strip" tabindex="0">%s</div>\n%s\n</div></section>') % (STRIP_TITLE, STRIP_TITLE, figs, btn)

def hero(p):
    h = V5.get("hero", {})
    loop, full = h.get("loop"), h.get("full")
    add = ""
    if has(loop):
        add += '<div class="v5-loop" data-v5loop="%s" aria-hidden="true"></div>' % loop["src"]
    if has(full):
        add += ('<button type="button" class="v5-sound" data-v5full="%s" data-v5poster="%s" data-v5code="%s" data-v5w="%d" data-v5h="%d">'
                '<span class="v5-sound-i">%s</span>%s</button>') % (full["src"], full["poster"], h["code"], full["w"], full["h"], PLAY, SOUND_LABEL)
    if not add: return p
    i = p.index('<figure class="portrait">'); j = p.index("</figure>", i)
    return p[:j] + add + p[j:]

def belief(p):
    b = V5.get("belief")
    if not has(b): return p
    a, z = B4.sec_bounds(p, "מה אם")
    k = p.rindex("</div>", a, z)  # סוף ה-wrap של הסקשן
    return p[:k] + vid_html(b) + "\n" + p[k:]

def reorder(p):
    first, end, B = blocks(p)
    keep_cta1 = V5.get("keep_cta1", True)
    parts = []
    for k in ORDER:
        if k == "@strip":
            s = strip_section()
            if s: parts.append(s)
            continue
        if k == "@cta1" and not keep_cta1:
            B.pop(k); continue
        parts.append(B.pop(k))
    assert not B, list(B)
    p = p[:first] + "\n\n".join(parts) + "\n\n" + p[end:]
    n = iter(range(1, 999)); p = re.sub(r'(<(?:header|section)\b[^>]*?)data-sec="\d+"', lambda m: m.group(1) + 'data-sec="%d"' % next(n), p)
    k = iter(range(1, 99)); p = re.sub(r'data-num="\d+"', lambda m: 'data-num="%02d"' % next(k), p)
    return p

CSS = """
/* ===== ב83 a5v5 ===== */
/* פתיחה: לולאת וידאו מוכהה מעל תמונת הפתיחה (התמונה נשארת ה-LCP; הלולאה נטענת אחרי שהיא צוירה) */
.hero9 .portrait .v5-loop{position:absolute;inset:0;z-index:0;pointer-events:none}
.hero9 .portrait .v5-loop video{width:100%;height:100%;object-fit:cover;object-position:center 12%;display:block;filter:brightness(.55) contrast(1.05) saturate(.9);opacity:0}
.hero9 .portrait .v5-loop video.on{opacity:1}
.hero9 .portrait::after{z-index:1}
.v5-sound{position:absolute;z-index:3;top:calc(56px + env(safe-area-inset-top,0px));inset-inline-end:16px;display:inline-flex;align-items:center;gap:8px;
  padding:8px 14px 8px 12px;border-radius:999px;border:1px solid rgba(254,207,0,.55);background:rgba(14,14,16,.6);color:#FFFFFF;font:700 14px/1 var(--font,Heebo,sans-serif);
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);cursor:pointer}
.v5-sound-i{display:grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#FECF00}
.v5-sound-i svg{width:12px;height:12px;fill:#000;margin-inline-start:2px}
.v5-modal{position:fixed;inset:0;z-index:60;display:grid;place-items:center;background:rgba(0,0,0,.86);padding:16px}
.v5-modal[hidden]{display:none}
.v5-modal video{width:min(100%,420px);max-height:86vh;border-radius:16px;background:#000}
.v5-modal .v5-x{position:absolute;top:calc(12px + env(safe-area-inset-top,0px));inset-inline-start:12px;width:44px;height:44px;border-radius:50%;border:0;background:rgba(255,255,255,.14);color:#fff;font-size:26px;cursor:pointer}
/* סרטונים (אמונה, רצועה) */
.v5-vid{margin:22px auto 0;width:100%;max-width:360px}
.v5-vid .v5-box{position:relative;display:block;width:100%;padding:0;border:0;border-radius:18px;overflow:hidden;background:#151518;cursor:pointer;
  box-shadow:0 24px 50px -30px rgba(0,0,0,.9);border:1px solid rgba(254,207,0,.28)}
.v5-vid img,.v5-vid video{display:block;width:100%;height:100%;object-fit:cover}
.v5-vid video{border-radius:18px;background:#000;height:auto}
.v5-vid .v4-pi{position:absolute;inset:0;margin:auto;width:68px;height:68px;border-radius:50%;display:grid;place-items:center;background:#FECF00;box-shadow:0 0 0 10px rgba(254,207,0,.18)}
.v5-vid .v4-pi svg{width:30px;height:30px;fill:#000;margin-inline-start:4px}
.v5-strip{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 2px 12px;margin:6px -20px 0;padding-inline:20px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.v5-strip::-webkit-scrollbar{display:none}
.v5-strip .v5-vid{flex:0 0 72%;max-width:300px;margin:0;scroll-snap-align:center}
/* ===== סעיף 5: אנימציות. רק כש-JS הוסיף html.v5a (לא בהפחתת תנועה, יש IntersectionObserver), ורק למה שמתחת למסך הראשון ===== */
.rv{transform:translateY(16px);transition:opacity .45s var(--ease) var(--d,0ms),transform .45s var(--ease) var(--d,0ms)}
.rv.in{opacity:1;transform:none}
html.v4rv .v4r:not(.in){transform:translate3d(0,16px,0)}
html.v4rv .v4r{transition:opacity .45s var(--ease),transform .45s var(--ease)}
html.v5a .v5s:not(.in){opacity:0;transform:translate3d(0,16px,0)}
html.v5a .v5s{transition:opacity .45s var(--ease) var(--v5d,0ms),transform .45s var(--ease) var(--v5d,0ms)}
html.v5a .v5z:not(.in){opacity:0;transform:scale(.96)}
html.v5a .v5z{transition:opacity .5s var(--ease),transform .6s var(--ease)}
html.v5a .v5o{transform:scale(1.06);transition:transform 1.2s var(--ease)}
html.v5a .v5o.in{transform:none}
html.v5a .v5-box img{transition:transform 8s linear}
html.v5a .v5-box.kb img,html.v5a .v4-box.kb img{transform:scale(1.05)}
html.v5a .v4-box img{transition:transform 8s linear}
.v4-ko-reg s{position:relative;text-decoration:none}
.v4-ko-reg s::after{content:"";position:absolute;inset-inline:-2px;top:52%;height:1.5px;background:currentColor;transform-origin:right center}
html.v5a .v4-ko-reg:not(.in) s::after{transform:scaleX(0)}
html.v5a .v4-ko-reg s::after{transition:transform .5s var(--ease) .15s}
html.v5a .v4-ko-now b:not(.in){opacity:0;transform:scale(1.08)}
html.v5a .v4-ko-now b{transition:opacity .45s var(--ease),transform .5s var(--ease)}
@media (prefers-reduced-motion:reduce){
  html.v5a .v5s,html.v5a .v5z,html.v5a .v5o,html.v5a .v4-ko-now b{opacity:1!important;transform:none!important;transition:none!important}
  .v5-box img,.v4-box img{transform:none!important;transition:none!important}
  .v4-ko-reg s::after{transform:none!important;transition:none!important}
  .rv{transition:none}
}
"""

JS = r"""<script>/* ב83 a5v5: סרטונים (לולאת פתיחה, הסרטון המלא, אמונה, רצועה) ואנימציות סעיף 5 */
(function(){var RM=matchMedia("(prefers-reduced-motion: reduce)").matches,IO="IntersectionObserver" in window,root=document.documentElement;
 function send(code){try{window.__lpSend&&window.__lpSend("video_play",{video:"v5_"+code});}catch(e){}}
 /* רק סרטון אחד מתנגן; סרטון שיוצא מהמסך נעצר */
 var seen=new WeakSet(),vis=IO?new IntersectionObserver(function(es){es.forEach(function(x){var v=x.target;if(x.intersectionRatio<.2&&!v.paused&&!v.closest(".v5-modal"))v.pause();});},{threshold:[0,.2]}):null;
 function watch(v){if(seen.has(v))return;seen.add(v);if(vis)vis.observe(v);}
 document.addEventListener("play",function(e){var v=e.target;if(!v||v.tagName!=="VIDEO")return;watch(v);if(v.dataset.v5bg)return;
  [].forEach.call(document.querySelectorAll("video"),function(o){if(o!==v&&!o.paused)o.pause();});},true);
 function mk(src,poster,ratio,code,auto){var v=document.createElement("video");v.src=src;if(poster)v.poster=poster;v.playsInline=true;v.setAttribute("playsinline","");v.preload="auto";
  if(ratio)v.style.aspectRatio=ratio;if(auto){v.muted=true;v.setAttribute("muted","");v.loop=true;v.dataset.v5bg="1";}else{v.controls=true;var sent=false;v.addEventListener("play",function(){if(!sent){sent=true;send(code);}});}
  return v;}
 /* סרטוני אמונה ורצועה: נוצרים בלחיצה */
 document.querySelectorAll("[data-v5src]").forEach(function(b){b.addEventListener("click",function(){var f=b.closest("[data-v5code]");var v=mk(b.dataset.v5src,(b.querySelector("img")||{}).src,b.style.aspectRatio,f.dataset.v5code,false);b.replaceWith(v);v.play().catch(function(){});});});
 /* הסרטון המלא עם קול */
 var sb=document.querySelector(".v5-sound");
 if(sb)sb.addEventListener("click",function(){var m=document.createElement("div");m.className="v5-modal";m.setAttribute("role","dialog");m.setAttribute("aria-modal","true");
  var x=document.createElement("button");x.type="button";x.className="v5-x";x.setAttribute("aria-label","סגירה");x.textContent="×";
  var v=mk(sb.dataset.v5full,sb.dataset.v5poster,sb.dataset.v5w+"/"+sb.dataset.v5h,sb.dataset.v5code,false);
  function close(){v.pause();m.remove();root.style.overflow="";}
  x.addEventListener("click",close);m.addEventListener("click",function(e){if(e.target===m)close();});
  m.appendChild(x);m.appendChild(v);document.body.appendChild(m);root.style.overflow="hidden";v.play().catch(function(){});});
 /* לולאת הפתיחה: אחרי שתמונת הפתיחה (LCP) צוירה, בלי קול, רק כשהיא במסך ורק כשאין סרטון אחר שמתנגן. לא בהפחתת תנועה */
 var lp=document.querySelector("[data-v5loop]");
 if(lp&&!RM){var start=function(){if(lp.firstChild)return;var v=mk(lp.dataset.v5loop,"",null,"",true);v.addEventListener("playing",function(){v.classList.add("on");},{once:true});lp.appendChild(v);
   var busy=function(){return [].some.call(document.querySelectorAll("video"),function(o){return o!==v&&!o.paused;});};
   if(IO)new IntersectionObserver(function(es){if(es[0].intersectionRatio>=.25){if(!busy())v.play().catch(function(){});}else v.pause();},{threshold:[0,.25]}).observe(lp);else v.play().catch(function(){});};
  var img=document.querySelector('[data-sec="1"] img[fetchpriority="high"]'),go=function(){setTimeout(start,350);};
  if(document.readyState==="complete")go();else addEventListener("load",go,{once:true});}
 /* אנימציות - רק למה שמתחת למסך הראשון */
 if(RM||!IO)return;
 var vh=innerHeight,below=function(e){return e.getBoundingClientRect().top>=vh*0.98;};root.classList.add("v5a");
 var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting||x.boundingClientRect.top<0){on(x.target);io.unobserve(x.target);}});},{rootMargin:"0px 0px -8% 0px"});
 function on(e){e.classList.add("in");if(e.__kids)e.__kids.forEach(function(k){k.classList.add("in");});if(e.__fn)e.__fn();}
 function stagger(sel,kidSel){document.querySelectorAll(sel).forEach(function(c){if(!below(c))return;var kids=[].slice.call(c.querySelectorAll(kidSel));
  kids.forEach(function(k,i){k.classList.add("v5s");k.style.setProperty("--v5d",(i*70)+"ms");});c.__kids=kids;io.observe(c);});}
 stagger(".bx2-list","article.bx2");stagger(".v4-ko-list","li");
 var ko=document.querySelector(".v4-ko");
 if(ko&&below(ko)){ko.classList.add("v5z");io.observe(ko);
  /* רגע המחיר: השורות אחת אחרי השנייה, 2,411 נספר, קו המחיקה נמתח, 297 מופיע */
  var tot=ko.querySelector(".v4-ko-tot b"),reg=ko.querySelector(".v4-ko-reg"),now=ko.querySelector(".v4-ko-now b");
  var tw=ko.querySelector(".v4-ko-tot");
  if(tot){var T=tot.textContent,N=parseInt(T.replace(/\D/g,""),10)||0;
   tw.__fn=function(){var t0=null,d=900;function f(ts){if(t0===null)t0=ts;var k=Math.min(1,(ts-t0)/d),val=Math.round(N*(1-Math.pow(1-k,3)));
     tot.textContent=T.replace(/[\d,]+/,val.toLocaleString("en-US"));if(k<1)requestAnimationFrame(f);else{tot.textContent=T;setTimeout(function(){if(reg)reg.classList.add("in");setTimeout(function(){if(now)now.classList.add("in");},350);},150);}}
     requestAnimationFrame(f);};io.observe(tw);}}
 document.querySelectorAll(".bio img").forEach(function(i){if(below(i)){i.classList.add("v5o");io.observe(i);}});
 /* פוסטרים של סרטונים: הגדלה איטית כשהם במסך */
 var kb=new IntersectionObserver(function(es){es.forEach(function(x){x.target.classList.toggle("kb",x.isIntersecting);});},{threshold:.3});
 document.querySelectorAll(".v5-box,.v4-slot .v4-box").forEach(function(b){kb.observe(b);});
})();</script>"""

def v5_layer(p):
    p = hero(p)
    p = belief(p)
    p = reorder(p)
    p = p.replace("</head>", "<style>" + CSS + "</style>\n</head>", 1)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    p = B4.ben_colors(p)
    return p

def build():
    p = B4.v4(B4.build_v3.build_a5(), "a5", "a5v3", "a5v5")
    p = v5_layer(p)
    assert p.count('data-variant="a5v5"') == 1
    return p

if __name__ == "__main__":
    os.makedirs(B4.OUT, exist_ok=True)
    p = build()
    open(os.path.join(B4.OUT, "a5v5" + B4.SUFFIX + ".html"), "w", encoding="utf8").write(p)
    print("a5v5", len(p), "sections:", re.findall(r'data-name="([^"]*)"', p))
