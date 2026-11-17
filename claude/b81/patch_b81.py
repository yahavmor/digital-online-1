# ב81 (ראשי 11.11, יהב אישר לבנות 17.11): שתי שאלות בדף התודה + לשונית "פרופיל רוכשים" בדשבורד.
# השאלות מופיעות רק אחרי אימות התשלום מול השרת, מתחת לכפתור הכניסה לקורס ולקבוצת הוואטסאפ, לא חובה, לחיצה אחת.
# לא נוגעים בהפניה לאפסייל, ב-Purchase, בדפים שבניסוי ובסליקה. נוסח השאלות לאישור בן.
# שימוש: python3 patch_b81.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:90], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)

CSS = '''/* ב81: שתי שאלות אחרי התשלום - לא חובה, לחיצה אחת */
.srv{margin:22px 0 0;padding:16px 14px 14px;border:1px solid var(--line);border-radius:16px;text-align:right}
.srv h2{font-size:16px;font-weight:800;margin:0 0 2px}
.srv .sub{font-size:13.5px;color:var(--muted);margin:0 0 10px}
.srv fieldset{border:0;margin:0;padding:0}.srv fieldset+fieldset{margin-top:14px}
.srv legend{font-size:15.5px;font-weight:700;padding:0;margin:0 0 8px;color:var(--ink)}
.srv .ch{display:flex;flex-wrap:wrap;gap:7px}
.srv .ch button{font:inherit;font-size:14.5px;min-height:40px;padding:6px 13px;border-radius:999px;border:1.5px solid var(--line);background:#fff;color:var(--ink);cursor:pointer}
.srv .ch button:focus-visible{outline:3px solid var(--gold2);outline-offset:2px}
.srv .ch button[aria-pressed="true"]{border-color:var(--gold);background:#FBF5E8;font-weight:700}
.srv .oth{display:flex;gap:7px;margin-top:8px}
.srv .oth input{flex:1;min-width:0;font:inherit;font-size:15px;min-height:42px;padding:6px 12px;border:1.5px solid var(--line);border-radius:12px}
.srv .oth button{font:inherit;font-weight:700;min-height:42px;padding:0 16px;border:0;border-radius:12px;background:var(--ink);color:#fff;cursor:pointer}
.srv .ty{font-size:14.5px;color:var(--ok);font-weight:700;margin:6px 0 0}
</style>'''

HTML = '''<p class="sent2">3 ערכות העבודה מחכות בשיעור הפתיחה של הקורס, בלשונית "קבצים מצורפים".</p>
<!-- ב81: שתי שאלות קצרות, רק אחרי אימות התשלום. לא חובה. התשובה נשמרת בגיליון האירועים עם מספר העסקה בלבד. הנוסח לאישור בן -->
<section class="srv" id="srv" aria-labelledby="srvH" hidden>
 <h2 id="srvH">2 שאלות קצרות, לא חובה</h2>
 <p class="sub">לחיצה אחת בכל שאלה. זה עוזר לבן להבין מה באמת עובד.</p>
 <fieldset id="srvQ1"><legend>מה הכי שכנע אותך להצטרף?</legend><div class="ch">
  <button type="button" data-a="video">סרטון של בן</button><button type="button" data-a="testimonials">ההמלצות בדף</button><button type="button" data-a="method">ההסבר על השיטה</button><button type="button" data-a="price_bonus">המחיר והבונוסים</button><button type="button" data-a="refund7">7 ימים להחזר</button><button type="button" data-a="referral">המלצה של מישהו</button><button type="button" data-a="other">אחר</button></div>
  <div class="oth" id="srvOth" hidden><input id="srvTxt" type="text" maxlength="60" placeholder="במילה או שתיים" aria-label="מה עוד שכנע אותך" data-clarity-mask="True"><button type="button" id="srvSend">שליחה</button></div>
 </fieldset>
 <fieldset id="srvQ2"><legend>איפה שמעת על בן לראשונה?</legend><div class="ch">
  <button type="button" data-a="facebook">פייסבוק</button><button type="button" data-a="instagram">אינסטגרם</button><button type="button" data-a="friend_aff">חבר או משווק</button><button type="button" data-a="youtube_google">יוטיוב או גוגל</button><button type="button" data-a="other">אחר</button></div>
 </fieldset>
 <p class="ty" id="srvTy" role="status" hidden>תודה!</p>
</section>'''

JS_DONE_OLD = '''      upsell(0);
      if(d.email && window.__showTo) __showTo(d.email);'''
JS_DONE_NEW = '''      upsell(0);
      survey(d);
      if(d.email && window.__showTo) __showTo(d.email);'''

JS_FN_OLD = '''    /* ב74: הצעת האפסייל. ההמתנה של 1.5 שניות נותנת ל-Purchase ולאירועי הדף להישלח לפני המעבר */'''
JS_FN_NEW = '''    /* ב81: שתי שאלות אחרי תשלום מאומת בלבד (גם בחזרה מדף האפסייל, ups=1). לחיצה אחת שולחת אירוע buyer_survey לגיליון:
       cta = q1 (מה שכנע) או q2 (איפה שמע), name = קוד התשובה (או other:טקסט קצר בלי מספרים ובלי מייל), x = deal=<מספר העסקה>.
       תשובה שכבר נשלחה מאותו דפדפן לא מוצגת שוב. לא חוסם ולא משנה את ההפניה לאפסייל */
    function survey(d){
      if(framed || TRACK_ENDPOINT[0] === "%") return;
      const deal = d && /^\\d+$/.test(String(d.deal || "")) ? String(d.deal) : ""; if(!deal) return;
      const box = el("srv"); if(!box || box.dataset.on) return; box.dataset.on = "1";
      const K = q => "srv_" + deal + "_" + q, done = q => { try{ return !!localStorage.getItem(K(q)); }catch(e){ return false; } };
      const send = (q, a) => { try{ localStorage.setItem(K(q), "1"); }catch(e){}
        try{ let lc = {}; try{ lc = JSON.parse(localStorage.getItem("nlp_lc") || "{}"); }catch(e){}
          const f = new URLSearchParams({ev:"buyer_survey", variant:lc.v || qs.get("v") || "", sid:lc.sid || qs.get("sid") || "", cta:q, name:a, x:"deal=" + deal});
          try{ if(localStorage.getItem("nlp_int") === "1") f.set("x", f.get("x") + ";int=1"); }catch(e){}
          try{ const ow = window.NLP_OWNER ? NLP_OWNER() : ""; if(ow) f.set("x", f.get("x") + ";aff=" + ow); }catch(e){}
          if(!(navigator.sendBeacon && navigator.sendBeacon(TRACK_ENDPOINT, f))) fetch(TRACK_ENDPOINT, {method:"POST", body:f, mode:"no-cors"}); }catch(e){} };
      const fin = () => { if(done("q1") && done("q2")) el("srvTy").hidden = false; };
      [["q1", "srvQ1"], ["q2", "srvQ2"]].forEach(([q, id]) => { const fs = el(id); if(done(q)){ fs.hidden = true; return; }
        fs.querySelectorAll(".ch button").forEach(b => b.addEventListener("click", () => { if(done(q)) return;
          fs.querySelectorAll(".ch button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
          if(q === "q1" && b.dataset.a === "other"){ el("srvOth").hidden = false; el("srvTxt").focus(); return; }
          send(q, b.dataset.a); fs.hidden = true; fin(); })); });
      el("srvSend").addEventListener("click", () => { if(done("q1")) return;
        const t = String(el("srvTxt").value || "").replace(/\\S+@\\S+/g, "").replace(/[\\d+()\\-]{5,}/g, "").replace(/[\\t\\r\\n;|]+/g, " ").trim().slice(0, 60);
        send("q1", t ? "other:" + t : "other"); el("srvQ1").hidden = true; fin(); });
      if(done("q1") && done("q2")) return; box.hidden = false;
    }
    /* ב74: הצעת האפסייל. ההמתנה של 1.5 שניות נותנת ל-Purchase ולאירועי הדף להישלח לפני המעבר */'''

patch("nlp/thanks.html", [
 ('''@keyframes sp{to{transform:rotate(360deg)}}
</style>''', '''@keyframes sp{to{transform:rotate(360deg)}}
''' + CSS),
 ('''<p class="sent2">3 ערכות העבודה מחכות בשיעור הפתיחה של הקורס, בלשונית "קבצים מצורפים".</p>''', HTML),
 (JS_DONE_OLD, JS_DONE_NEW),
 (JS_FN_OLD, JS_FN_NEW),
])

TAB_HTML = '''  <!-- 14 (ב81): פרופיל רוכשים - שורה לכל רכישה מאומתת. בלי שמות, טלפונים, מיילים ומספרי עסקה. קריאה בלבד -->
  <section class="screen" id="s-pr">
    <div class="panel"><div class="panel-h"><h2>פרופיל רוכשים</h2><span class="note" id="prNote"></span></div><div class="tw"><table id="prTable"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>תשובות בדף התודה</h2><span class="note">מ-buyer_survey (ב81). לא חובה, לכן לא לכל רכישה יש תשובה</span></div><div class="tw"><table id="prAns"></table></div></div>
  </section>

  <!-- 13 (ב93): מה מוכר - לפי מודעה, קמפיין ומשווק. קריאה בלבד -->'''

RENDER = '''/* ================= 14 פרופיל רוכשים (ב81) =================
   שורה לכל רכישה מאומתת (כרטיס והעברה בנקאית), מכל הזמן, בלי עסקאות בדיקה. מקור/קמפיין/מודעה/דף מהביקור שבו נקנה;
   זמן מהביקור הראשון ומספר ביקורים - לפי מזהה המבקר (vid), עד רגע הרכישה. תשובות: אירוע buyer_survey מדף התודה, לפי deal=. */
const PR_Q1={video:"סרטון של בן",testimonials:"ההמלצות בדף",method:"ההסבר על השיטה",price_bonus:"המחיר והבונוסים",refund7:"7 ימים להחזר",referral:"המלצה של מישהו",other:"אחר"},
 PR_Q2={facebook:"פייסבוק",instagram:"אינסטגרם",friend_aff:"חבר או משווק",youtube_google:"יוטיוב או גוגל",other:"אחר"},
 PR_DV={m:"נייד",d:"מחשב",t:"טאבלט"},PR_APP={fb:"אפליקציית פייסבוק",ig:"אפליקציית אינסטגרם",web:"דפדפן"};
function prDur(ms){if(ms==null||!isFinite(ms))return "-";const h=ms/36e5;return h<1?"פחות משעה":h<24?Math.round(h)+" שעות":(Math.round(h/24*10)/10)+" ימים"}
function prAns(a,M){if(!a)return '<span class="na">-</span>';const o=/^other:/.test(a)?"אחר: "+a.slice(6):(M[a]||a);return esc(o)}
function renderPr(){
 const now=new Date(),keep=[fSrc,fDev,fOwn];fSrc="";fDev="";fOwn="";let M;try{M=build(new Date(0),new Date(+now+864e5))}finally{[fSrc,fDev,fOwn]=keep}
 const ANS={},SANS={};M.R.forEach(r=>{if(r.ev!=="buyer_survey"||!/^q[12]$/.test(r.cta||""))return;const x=parseX(r.x),d=x.deal||"";const o=d?(ANS[d]=ANS[d]||{}):(SANS[r.sid]=SANS[r.sid]||{});if(!o[r.cta])o[r.cta]=String(r.name||"")});
 const byV={};M.sess.forEach(s=>{if(s.vid)(byV[s.vid]=byV[s.vid]||[]).push(s)});
 const B=M.allBuys.slice().sort((x,y)=>y.t-x.t),na='<span class="na">-</span>';
 const body=B.map(b=>{const s=b.s,an=ANS[b.deal]||(b.sid&&SANS[b.sid])||{};
  const V=s&&s.vid&&byV[s.vid]?byV[s.vid].filter(x=>x.t<=b.t):(s?[s]:[]),first=V.length?Math.min(...V.map(x=>+x.t)):null;
  const p=s&&s.p,aff=b.aff||(s&&s.aff)||(p&&p.get("aff"))||"",inf=aff&&AFF&&AFF[aff];
  const plat=s?[s.os&&s.os!=="?"?s.os:"",PR_APP[s.app]||(s.app&&s.app!=="?"?s.app:"")].filter(Boolean).join(" · "):"";
  return '<tr><td>'+hm2(b.t)+(b.bank?' <small>העברה בנקאית</small>':'')+'</td><td>'+(s?esc(s.v):na)+'</td><td>'+(s?esc(s.src):na)+'</td><td>'+(p&&p.get("utm_campaign")?esc(p.get("utm_campaign")):na)+'</td><td>'+(s&&s.cr&&s.cr!=="(ללא קריאייטיב)"?esc(s.cr):na)+'</td><td>'+(s?esc(PR_DV[s.dv]||s.dv):na)+'</td><td>'+(plat?esc(plat):na)+'</td><td class="num">'+(first!=null?prDur(+b.t-first):na)+'</td><td class="num">'+(V.length?fmt(V.length):na)+'</td><td>'+(aff?esc(inf?inf.name:aff)+' <small>'+esc(aff)+'</small>':'בן')+'</td><td>'+prAns(an.q1,PR_Q1)+'</td><td>'+prAns(an.q2,PR_Q2)+'</td></tr>'});
 table($("prTable"),["תאריך","דף","מקור","קמפיין","מודעה","מכשיר","פלטפורמה","מהביקור הראשון לרכישה","ביקורים עד הרכישה","משווק","מה שכנע","איפה שמע"],body,"אין עדיין רכישות מאומתות");
 const noS=B.filter(b=>!b.s).length;
 $("prNote").textContent=B.length+" רכישות מאומתות מכל הזמן, בלי עסקאות בדיקה. ביקורים וזמן - לפי מזהה המבקר (מכשיר), עד הרכישה."+(noS?" "+noS+" רכישות בלי ביקור מזוהה (למשל העברה בנקאית) - בלי מקור ובלי מכשיר.":"")+" שאלות דף התודה נוספו ב-ב81, ולרכישות מלפני כן אין תשובות.";
 const cnt=(q,MAP)=>{const C={};B.forEach(b=>{const a=(ANS[b.deal]||(b.sid&&SANS[b.sid])||{})[q];if(a){const k=/^other:/.test(a)?"other":a;C[k]=(C[k]||0)+1}});return Object.keys(MAP).map(k=>[MAP[k],C[k]||0])};
 const c1=cnt("q1",PR_Q1),c2=cnt("q2",PR_Q2),n1=c1.reduce((x,y)=>x+y[1],0),n2=c2.reduce((x,y)=>x+y[1],0),rows2=[];
 for(let i=0;i<Math.max(c1.length,c2.length);i++){const a=c1[i],b=c2[i];rows2.push('<tr><td>'+(a?esc(a[0]):"")+'</td><td class="num">'+(a?fmt(a[1])+(n1?'<small>'+pf(pct(a[1],n1))+'</small>':''):"")+'</td><td>'+(b?esc(b[0]):"")+'</td><td class="num">'+(b?fmt(b[1])+(n2?'<small>'+pf(pct(b[1],n2))+'</small>':''):"")+'</td></tr>')}
 table($("prAns"),["מה שכנע ("+n1+" ענו)","רוכשים","איפה שמע לראשונה ("+n2+" ענו)","רוכשים"],n1||n2?rows2:[],"עוד אין תשובות");
}
/* סינון לפי משווק (בקשת יהב 09.11): אמיר, שחר, גל ורחל ראשונים, ואחריהם שאר המשווקים הפעילים */'''

patch("nlp/dashboard.html", [
 ('''    <button role="tab" data-s="ws"><b>13</b>מה מוכר</button>''', '''    <button role="tab" data-s="ws"><b>13</b>מה מוכר</button>
    <button role="tab" data-s="pr"><b>14</b>פרופיל רוכשים</button>'''),
 ('''body[data-scr="ws"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}''', '''body[data-scr="ws"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}
body[data-scr="pr"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}'''),
 ('''  <!-- 13 (ב93): מה מוכר - לפי מודעה, קמפיין ומשווק. קריאה בלבד -->''', TAB_HTML),
 ('''ws:()=>renderWs()})[screen]()''', '''ws:()=>renderWs(),pr:()=>renderPr()})[screen]()'''),
 ('''/* סינון לפי משווק (בקשת יהב 09.11): אמיר, שחר, גל ורחל ראשונים, ואחריהם שאר המשווקים הפעילים */''', RENDER),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב81 (יהב אישר לבנות 17.11): לשונית 14 \\"פרופיל רוכשים\\" - שורה לכל רכישה מאומתת: דף, מקור, קמפיין, מודעה, מכשיר, פלטפורמה, זמן מהביקור הראשון, מספר ביקורים עד הרכישה, משווק, ותשובות שתי השאלות בדף התודה (buyer_survey). בלי שמות, טלפונים, מיילים ומספרי עסקה."],
''' % (day, hm)),
])
print("ok")
