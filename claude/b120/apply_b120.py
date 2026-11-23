# ב120 (23.11): checkout.html - (1) B2 בנייד: מעל הטופס שורה אחת במקום הכותרת וכרטיס ההזמנה, כדי שהתיבה והטופס יעלו;
# (2) "עוד לא בטוח?" - מוכן ומכובה (SOFT_ON=false) עד שבן קובע את התוכן. שימוש: python3 apply_b120.py <nlp/checkout.html>
import sys, hashlib
P = sys.argv[1]; s = open(P, encoding="utf-8").read()
h = hashlib.sha256(s.encode()).hexdigest()[:16]
assert h == "a6df8bce9bbe9c3f", "checkout.html changed since ב120 was prepared: " + h
SOFT_HOOK = "https://hook.eu1.make.com/39kj2y452zq059jpdcneylg155umd3to"
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)

CSS = """/* ב120: B2 בנייד - מעל הטופס רק שורה אחת (מחיר, 3 תשלומים, החזר, בלי מנוי), כדי שהתיבה והטופס יעלו במסך הראשון בדפדפן של פייסבוק */
.one2{display:none}
@media (max-width:600px){
html[data-co2="1"] .wrap{padding-top:8px}
html[data-co2="1"] .brand{display:none}
html[data-co2="1"] .top{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
html[data-co2="1"] .order{margin:0;padding:8px 6px}
html[data-co2="1"] .order .one1{display:none!important}
html[data-co2="1"] .order .one2{display:block!important;margin:0;text-align:center;font-size:clamp(12.5px,3.65vw,15.5px);font-weight:800;line-height:1.35;color:var(--ink)}
html[data-co2="1"] .why{margin-top:8px;padding-top:10px}
}
/* ב120: "עוד לא בטוח?" - קישור קטן מתחת לטופס, ומייל עם תוכן חינמי. מוצג רק כש-SOFT_ON=true */
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.soft{margin:14px 0 0;text-align:center}.soft[hidden],.softbox[hidden]{display:none}
.softlink{font:inherit;font-size:14.5px;color:var(--muted);background:none;border:0;padding:6px 4px;text-decoration:underline;cursor:pointer}
.softbox{margin:8px 0 0;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--soft);text-align:right}
.softbox p{margin:0 0 8px;font-size:14.5px;line-height:1.45;color:var(--ink2)}
.softbox input[type=email]{display:block;width:100%;font:inherit;font-size:16px;padding:10px 12px;border:1px solid #D9D4C9;border-radius:10px;background:#fff;text-align:right}
.softbox .cons{margin:8px 0 8px}
.softgo{width:100%;min-height:44px;border:1px solid var(--gold2);border-radius:10px;background:#fff;color:var(--ink);font:inherit;font-weight:700;font-size:15.5px;cursor:pointer}
.softerr{color:var(--err);font-size:13.5px;font-weight:600;margin:6px 0 0}
</style>
</head>"""
rep("</style>\n</head>", CSS)
rep('<!-- ב99: שורה אחת במובייל בלבד -->', '<!-- ב99: שורה אחת במובייל בלבד -->\n<p class="one2">297 ₪ או 3 תשלומים של 99 ₪ · 7 ימי החזר · בלי מנוי</p><!-- ב120: B2 בנייד, במקום הכותרת והשורה של ב99. מהנוסח הקיים -->')
SOFT_HTML = """<p class="wt-h" id="wtH" hidden></p></div>
<div class="soft" id="softWrap" hidden><!-- ב120: "עוד לא בטוח?" - כבוי עד שבן קובע את התוכן -->
<button type="button" class="softlink" id="softBtn" aria-expanded="false" aria-controls="softBox"></button>
<form class="softbox" id="softBox" hidden novalidate data-clarity-mask="True">
<p id="softIntro"></p>
<label class="sr" for="softEmail">מייל</label><input id="softEmail" type="email" inputmode="email" autocomplete="email" dir="ltr" required>
<label class="cons"><input type="checkbox" id="softConsent" value="1"><span>אשמח לקבל מבן נחום עדכונים והצעות במייל ובוואטסאפ. אפשר להסיר בכל רגע. <a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a></span></label>
<button type="submit" class="softgo" id="softGo"></button>
<p class="softerr" id="softErr" role="alert"></p>
</form>
<p class="softok" id="softOk" role="status" hidden></p>
</div>"""
rep('<p class="wt-h" id="wtH" hidden></p></div>', SOFT_HTML)
rep('window.NLP_CO_TRACK=track;', 'window.NLP_CO_TRACK=track; window.NLP_CO_CTX={sid:sid,variant:variant,U:U}; /* ב120: ל"עוד לא בטוח?" */')
SOFT_JS = """<script>/* ב120: "עוד לא בטוח?" - שומר את המייל עם המשווק (aff) והמקור, כדי שמכירה מאוחרת מהמייל תיזקף למשווק (הקישור במייל נושא aff=).
   כבוי (SOFT_ON=false) עד שבן קובע את התוכן ואת הנוסח. הנוסחים כאן הם מקום שמור בלבד, לא נוסח מאושר. */
(function(){var SOFT_ON=false, HOOK="__HOOK__",
 COPY={link:"עוד לא בטוח?", intro:"[נוסח של בן: מה נשלח למייל, למשל שיעור או מדריך חינמי]", btn:"[נוסח של בן: שלחו לי]", ok:"[נוסח של בן: נשלח, תבדקו את המייל]", err:"צריך מייל תקין"};
 var on=SOFT_ON||window.NLP_SOFT_PREVIEW===true; var W=document.getElementById("softWrap"); if(!on||!W)return;
 var $=function(i){return document.getElementById(i)}, B=$("softBtn"), X=$("softBox"), E=$("softEmail"), tr=function(ev,x){try{if(window.NLP_CO_TRACK)NLP_CO_TRACK(ev,x?{x:x}:undefined)}catch(e){}};
 B.textContent=COPY.link; $("softIntro").textContent=COPY.intro; $("softGo").textContent=COPY.btn; $("softOk").textContent=COPY.ok; W.hidden=false;
 B.addEventListener("click",function(){var o=X.hidden; X.hidden=!o; B.setAttribute("aria-expanded",String(o)); if(o){var m=($("fEmail")||{}).value||""; if(m&&!E.value)E.value=m.trim(); tr("soft_open"); setTimeout(function(){try{E.focus()}catch(e){}},50)}});
 X.addEventListener("submit",function(ev){ev.preventDefault(); var m=(E.value||"").trim(); if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(m)){$("softErr").textContent=COPY.err; return} $("softErr").textContent="";
  var C=window.NLP_CO_CTX||{}, U=C.U||function(){return ""}, q=new URLSearchParams(location.search), ow=""; try{ow=window.NLP_OWNER?NLP_OWNER():""}catch(e){}
  var f=new URLSearchParams({email:m, name:(($("fName")||{}).value||"").trim().slice(0,50), aff:ow, utm_source:U("utm_source"), utm_medium:U("utm_medium"), utm_campaign:U("utm_campaign"), utm_content:U("utm_content"), variant:C.variant||"", exp:q.get("exp")||"", page:location.pathname, sid:C.sid||"", consent:$("softConsent").checked?"1":"0"});
  try{ if(!(navigator.sendBeacon&&navigator.sendBeacon(HOOK,f))) fetch(HOOK,{method:"POST",body:f,mode:"no-cors",keepalive:true}); }catch(e){}
  tr("soft_submit", "consent="+($("softConsent").checked?1:0)); X.hidden=true; B.hidden=true; $("softOk").hidden=false; });
})();</script>
</body>""".replace("__HOOK__", SOFT_HOOK)
rep("</body>", SOFT_JS)
open(P, "w", encoding="utf-8").write(s)
print("ok", hashlib.sha256(s.encode()).hexdigest()[:16])
