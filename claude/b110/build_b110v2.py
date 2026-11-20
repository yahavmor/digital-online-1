# ב110 v2 (ראשי 20.11): זרימת הרכישה במבנה של המתחרה - טיוטה בלבד. בן הקפיא את ב110 ב-19.11; העלייה לאוויר רק אחרי החלטה של יהב ובן ו"מאשר" נפרד.
# בונה קובץ אחד, draft/a5s_b110v2.html, מתוך nlp/a5s.html של main. לא מקושר מאף דף, noindex, ונשמר רק בענף העבודה.
#  - כל כפתורי הקנייה גוללים לטופס הקרוב (במקום לפתוח את checkout.html).
#  - טופס בכרטיס ההצעה מתחת למחיר, וטופס שני בסוף הדף אחרי השאלות הנפוצות: שם מלא, מייל, תיבה (לא מסומנת), כפתור.
#  - בשליחה: checkout_details (אותו אירוע ואותו hook כמו בסליקה -> 7798267 -> 210989 + נטישה 7847510 -> nlp_rec1-3 למי שסימן),
#    Lead + InitiateCheckout ל-Meta, ואז קריאה לאותו hook שהסליקה קוראת לו (7827398, יוצר דף Low Profile) ומעבר ישר לדף התשלום של קארדקום.
#    הטלפון לא נשלח: קארדקום מציג שדה נייד חובה בדף התשלום עצמו (נבדק 20.11 בדף שנוצר בלי טלפון).
#    אם יצירת דף התשלום נכשלת - מעבר ל-checkout.html עם הפרטים ממולאים (גיבוי).
#  - aff ו-UTM: נשלחים ל-7827398 בדיוק כמו מהסליקה (utm_*, aff מ-NLP_OWNER, v, sid, fbp/fbc/ua).
#  - נוסחים שמחכים לבן מסומנים בסוגריים מרובעים. שורת 3 התשלומים היא הנוסח שכבר באוויר בסליקה.
# הרצה: python3 build_b110v2.py <שורש main> <תיקיית יעד>
import sys, os, re
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
s = open(os.path.join(SRC, "nlp", "a5s.html"), encoding="utf8").read()
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:90], s.count(a)); return s.replace(a, b)

s = rep(s, 'data-variant="a5s"', 'data-variant="a5s_f"')  # בטיוטה: גרסה נפרדת, כדי שלא תתערבב בנתונים של a5s
assert "noindex" in s

PH_LINE = "[שורת הסבר מעל הטופס - מחכה לבן]"
PH_BOX = "[נוסח ההסכמה לדיוור - מחכה לבן]"
PH_BTN = "[כפתור בגוף ראשון, פונה לבן - מחכה לבן]"
TERMS = 'מדיניות ביטול לעסקה זו הינה לפי חוק שירותי תשלום בישראל. מאשר אני כי הנני מכיר את <a href="terms.html" target="_blank" rel="noopener">תנאי ופרטי העסקה</a> ואת <a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a>.'
LOCK = '<svg class="v4-li" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'

def form(n):
    return ('<form class="lpf" id="lpForm%d" data-form="%d" novalidate>' % (n, n) +
            '<p class="lpf-how">' + PH_LINE + '</p>'
            '<label class="lpf-f"><b>שם מלא</b><input id="lfName%d" name="name" autocomplete="name" maxlength="50" required></label>' % n +
            '<label class="lpf-f"><b>מייל</b><input id="lfEmail%d" name="email" type="email" inputmode="email" autocomplete="email" dir="ltr" required></label>' % n +
            '<input class="lpf-hp" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<label class="lpf-c" data-box="one"><input type="checkbox" id="lfBox%d" name="box" value="1"><span>' % n + PH_BOX + ' ' + TERMS + '</span></label>'
            '<label class="lpf-c" data-box="news" hidden><input type="checkbox" id="lfNews%d" name="news" value="1"><span>' % n + PH_BOX + '</span></label>'
            '<p class="lpf-err" id="lfErr%d" role="alert"></p>' % n +
            '<button class="cta" type="submit" data-cta="form%d"><span class="ct-t">' % n + PH_BTN + '</span> <span>←</span><span class="v4-pay">' + LOCK + 'תשלום מאובטח</span></button>'
            '</form>')

# 1. טופס בכרטיס ההצעה, מתחת למחיר (במקום כפתור ההצעה). שורת 3 התשלומים - הנוסח שכבר באוויר בסליקה
m = re.search(r'<a class="cta" data-cta="offer" data-checkout href="#">.*?</a>', s, re.S); assert m
s = s[:m.start()] + '<p class="lpf-pay3">או 3 תשלומים של 99 ₪</p>' + form(1) + s[m.end():]
# 2. טופס בסוף הדף, אחרי השאלות הנפוצות (במקום הכפתור האחרון)
m = re.search(r'<a class="cta" data-cta="final" data-checkout href="#">.*?</a>', s, re.S); assert m
pl = re.search(r'<div class="paylogos" data-paylogos="offer">.*?</div>', s, re.S).group(0).replace('data-paylogos="offer"', 'data-paylogos="final"')
s = s[:m.start()] + '<p class="v4-ko-now lpf-price"><span>מחיר השקה לזמן מוגבל</span> <b>297 ₪</b></p><p class="lpf-pay3">או 3 תשלומים של 99 ₪</p>' + form(2) + pl + s[m.end():]
# 3. כפתורי הקנייה שנשארו (פתיחה, אחריות, להטמיע, הצצה, דביק, סיפורים): גלילה לטופס הקרוב במקום מעבר לסליקה
s = rep(s, 'a.addEventListener("click",()=>{ try{localStorage.setItem("nlp_lc"',
           'a.addEventListener("click",(ev)=>{ if(window.__lpFormGo){ window.__lpFormGo(a,ev); return; } try{localStorage.setItem("nlp_lc"')
s = rep(s, 'window.__lpSend = send; send("view");', 'window.__lpSend = send; window.__lpSid = sid; send("view");')

CSS = """<style>/* ב110 v2 (טיוטה): טופס שם + מייל בכרטיס ההצעה ובסוף הדף */
.lpf{display:grid;gap:10px;margin:12px 0 4px;text-align:right;scroll-margin-top:90px}
.lpf-how{margin:0 0 2px;font-size:14.5px;line-height:1.5;color:var(--ink2,#ccc);text-align:center}
.lpf-f{display:grid;gap:4px;font-size:15px}.lpf-f b{font-weight:700}
.lpf-f input{font:inherit;font-size:16px;min-height:48px;padding:8px 14px;border-radius:12px;border:1.5px solid var(--gold-a,#8a7340);background:var(--card,#16161a);color:var(--ink,#fff)}
.lpf-f input:focus{outline:2px solid var(--gold2,#fecf00);outline-offset:1px}
.lpf-f input.bad{border-color:#e5484d}
.lpf-hp{position:absolute!important;left:-9999px!important;width:1px;height:1px;opacity:0}
.lpf-c[hidden]{display:none}.lpf-c{display:flex;gap:9px;align-items:flex-start;font-size:13px;line-height:1.55;color:var(--ink2,#ccc)}.lpf-c input{width:20px;height:20px;margin-top:2px;flex:none}
.lpf-c a{color:inherit;text-decoration:underline}.lpf-c.need{outline:2px solid #e5484d;outline-offset:4px;border-radius:6px}
.lpf-err{min-height:1em;margin:0;color:#e5484d;font-size:14px}
.lpf .cta{width:100%;border:0;cursor:pointer;font:inherit}.lpf .cta[disabled]{opacity:.7;cursor:wait}
.lpf-pay3{margin:-2px 0 0;text-align:center;font-size:14.5px;font-weight:700;color:var(--ink2,#ccc)}
.lpf-price{text-align:center}
html.lpf-in #sticky{opacity:0!important;pointer-events:none!important;transform:translateY(120%)!important} /* הכפתור הדביק לא מכסה טופס פתוח */
.lpf.hl{animation:lpfHl 1.2s ease-out 1}@keyframes lpfHl{0%{box-shadow:0 0 0 0 rgba(254,207,0,.55)}100%{box-shadow:0 0 0 18px rgba(254,207,0,0)}}
</style>
"""
JS = """<script>/* ב110 v2 (טיוטה): כפתורי הקנייה גוללים לטופס הקרוב; שליחת הטופס שומרת ליד ועוברת ישר לדף התשלום של קארדקום */
(function(){
 var BOX_MODE="one_required"; /* one_required: תיבה אחת חובה (תנאי העסקה של קארדקום + פרטיות + דיוור) - הדיוור נעשה תנאי, החלטה של בן.
                                 two: תיבת תנאים חובה + תיבת דיוור רשות. one_optional: תיבה אחת רשות - רק אם קארדקום מאשרים בלי תיבת תנאים */
 var CHECKOUT_ENDPOINT="https://hook.eu1.make.com/9yp88pz9bfvxbr7w6xkb4ckun82ote6a"; /* אותו hook של הסליקה (7827398) - יוצר דף Low Profile ומחזיר {url} */
 var F=[].slice.call(document.querySelectorAll("form.lpf"));if(!F.length)return;
 var S=function(ev,ex){try{(window.__lpSend||function(){})(ev,ex||{})}catch(e){}};
 var qs=new URLSearchParams(location.search),INT=false;try{INT=localStorage.getItem("nlp_int")==="1"}catch(e){}
 if(BOX_MODE==="two")F.forEach(function(f){f.querySelector('[data-box="news"]').hidden=false;var o=f.querySelector('[data-box="one"] span');o.innerHTML=o.innerHTML.replace(/^\\[[^\\]]*\\]\\s*/,"")});
 /* פתיחת טופס: פעם אחת לכל טופס כשהוא נראה (60%), וגם התחלת מילוי */
 var seen={},started={};
 var inV={};
 if("IntersectionObserver" in window){new IntersectionObserver(function(es){es.forEach(function(e){inV[e.target.dataset.form]=e.isIntersecting});document.documentElement.classList.toggle("lpf-in",Object.keys(inV).some(function(k){return inV[k]}))},{threshold:[0]}).observe(F[0]);
  if(F[1])new IntersectionObserver(function(es){es.forEach(function(e){inV[e.target.dataset.form]=e.isIntersecting});document.documentElement.classList.toggle("lpf-in",Object.keys(inV).some(function(k){return inV[k]}))},{threshold:[0]}).observe(F[1])}
 if("IntersectionObserver" in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){var n=e.target.dataset.form;if(e.isIntersecting&&e.intersectionRatio>=.6&&!seen[n]){seen[n]=1;S("form_open",{name:"form"+n,x:"form="+n})}})},{threshold:[.6]});F.forEach(function(f){io.observe(f)})}
 F.forEach(function(f){f.addEventListener("focusin",function(){var n=f.dataset.form;if(!started[n]){started[n]=1;S("form_start",{name:"form"+n,x:"form="+n})}})});
 /* כפתור קנייה: גלילה לטופס הקרוב (לפי המרחק בדף), בלי מעבר דף */
 window.__lpFormGo=function(a,ev){if(ev)ev.preventDefault();var m=document.getElementById("spModal");if(m&&!m.hidden){var x=m.querySelector(".sp-x");if(x)x.click()}
  var y=a.getBoundingClientRect().top+scrollY,best=F[0],bd=1e12;if(a.dataset.cta==="sticky"){y=scrollY+innerHeight/2}
  F.forEach(function(f){var d=Math.abs(f.getBoundingClientRect().top+scrollY-y);if(d<bd){bd=d;best=f}});
  var sec=a.closest("[data-sec]");S("cta_click",{cta:a.dataset.cta||"",at_section:sec?+sec.dataset.sec:0,x:"to=form"+best.dataset.form});
  try{best.scrollIntoView({behavior:"smooth",block:"center"})}catch(e){best.scrollIntoView()}
  best.classList.remove("hl");void best.offsetWidth;best.classList.add("hl")}; /* בלי פוקוס אוטומטי: גלילה בלבד, כמו אצל המתחרה (פוקוס בנייד פותח מקלדת שמכסה את הטופס) */
 function $(f,k){return f.querySelector('[name="'+k+'"]')}
 function chk(f){var n=$(f,"name").value.replace(/["\\\\<>{}]/g,"").trim().replace(/\\s+/g," "),e=$(f,"email").value.trim(),bad=[];
  var nok=n.length>=2&&/\\s/.test(n),eok=/^[^\\s@"'\\\\<>{}]+@[^\\s@"'\\\\<>{}]+\\.[^\\s@"'\\\\<>{}]{2,}$/.test(e);
  $(f,"name").classList.toggle("bad",!nok);$(f,"email").classList.toggle("bad",!eok);if(!nok)bad.push("שם מלא (שם פרטי ומשפחה)");if(!eok)bad.push("מייל תקין");
  var bx=$(f,"box"),boxReq=BOX_MODE!=="one_optional",bw=bx.closest(".lpf-c");bw.classList.toggle("need",boxReq&&!bx.checked);if(boxReq&&!bx.checked)bad.push("סימון התיבה");
  f.querySelector(".lpf-err").textContent=bad.length?"חסר: "+bad.join(", "):"";
  return bad.length?null:{name:n,email:e,phone:""}}
 function ck(n){var m=document.cookie.match(new RegExp("(?:^|; )"+n+"=([^;]*)"));return m?decodeURIComponent(m[1]):""}
 F.forEach(function(f){f.addEventListener("submit",function(ev){ev.preventDefault();var fn=f.dataset.form,btn=f.querySelector("button");if(btn.disabled)return;
  if($(f,"company").value){S("form_bot",{x:"form="+fn});return}
  var d=chk(f);if(!d){S("form_error",{name:["name","email","box"].filter(function(k){var el=$(f,k);return k==="box"?el.closest(".lpf-c").classList.contains("need"):el.classList.contains("bad")}).join(","),x:"form="+fn});return}
  var cn=BOX_MODE==="two"?($(f,"news").checked?"1":"0"):($(f,"box").checked?"1":"0"),V=document.documentElement.dataset.variant,sid=window.__lpSid||"";
  try{sessionStorage.setItem("cc_det",JSON.stringify(d));sessionStorage.setItem("cc_cons",cn);sessionStorage.setItem("cc_from_lp","1")}catch(e){}
  try{localStorage.setItem("nlp_lc",JSON.stringify({v:V,sid:sid,qs:location.search.slice(1),cta:"form"+fn,ts:Date.now()}))}catch(e){}
  S("form_submit",{name:"form"+fn,cta:"form"+fn,checkout_started:1,x:"form="+fn+";cons="+cn});
  S("checkout_details",{lead_name:d.name,lead_email:d.email,lead_phone:"",lead_consent:cn,x:"cons="+cn+";form=lp"+fn}); /* אותו אירוע ואותו hook כמו בסליקה -> 7798267 -> 210989 ונטישה */
  try{if(window.fbq&&!window.__noPix){var w=d.name.toLowerCase().split(/\\s+/),ud={em:d.email.toLowerCase()};if(w[0])ud.fn=w[0];if(w.length>1)ud.ln=w[w.length-1];
   fbq("init","1278104408729813",ud);fbq("init","1651086743466533",ud);fbq("track","Lead",{content_name:"lpform",value:297,currency:"ILS"});
   if(!window.__ic){var dn=false;try{dn=sessionStorage.getItem("nlp_ic")==="1";sessionStorage.setItem("nlp_ic","1")}catch(e){}window.__ic=1;if(!dn)fbq("track","InitiateCheckout",{value:297,currency:"ILS"})}}}catch(e){}
  btn.disabled=true;var bt=btn.querySelector(".ct-t"),old=bt.textContent;bt.textContent="מעבירים לתשלום מאובטח...";
  var U=function(k){return qs.get(k)||""},utmC=U("utm_content")||("lp_"+V);
  var body=new URLSearchParams({variant:V,sid:sid,name:d.name,email:d.email,phone:"",utm_source:U("utm_source"),utm_medium:U("utm_medium"),utm_campaign:U("utm_campaign"),utm_content:utmC,co:"b"});
  var ow=window.NLP_OWNER?NLP_OWNER():"";if(ow)body.set("aff",ow);if(INT)body.set("test","1");
  try{var fbp=ck("_fbp"),fbc=ck("_fbc"),fc=qs.get("fbclid");if(!fbc&&fc)fbc="fb.1."+Date.now()+"."+fc;if(navigator.userAgent)body.set("ua",navigator.userAgent);if(fbp)body.set("fbp",fbp);if(fbc)body.set("fbc",fbc)}catch(e){}
  var fallback=function(code){S("checkout_load_error",{code:String(code||""),x:"form="+fn});var q=new URLSearchParams(location.search);if(!q.has("utm_content"))q.set("utm_content","lp_"+V);q.set("v",V);q.set("sid",sid);location.href="checkout.html?"+q.toString()};
  var ctl=("AbortController" in self)?new AbortController():null,t0=Date.now(),to=setTimeout(function(){ctl&&ctl.abort()},15000);
  fetch(CHECKOUT_ENDPOINT,{method:"POST",body:body,signal:ctl?ctl.signal:undefined}).then(function(r){return r.json()}).then(function(r){clearTimeout(to);
   if(!r||!r.url||!/^https:\\/\\/[^\\/]*cardcom\\.solutions\\//i.test(r.url)||(r.code&&String(r.code)!=="0"))return fallback(r&&r.code);
   try{if(r.lp)sessionStorage.setItem("cc_lp",r.lp)}catch(e){}
   S("checkout_pay_redirect",{x:"form="+fn+";pay_load_ms="+(Date.now()-t0)});
   setTimeout(function(){location.href=r.url},250)}).catch(function(){clearTimeout(to);btn.disabled=false;bt.textContent=old;fallback()})})});
})();
</script>
"""
s = rep(s, "</head>", CSS + "</head>"); s = rep(s, "</body>", JS + "</body>")
assert 'data-cta="offer"' not in s and 'data-cta="final"' not in s and s.count('class="lpf"') == 2
open(os.path.join(OUT, "a5s_b110v2.html"), "w", encoding="utf8").write(s)
print("ok", len(s))
