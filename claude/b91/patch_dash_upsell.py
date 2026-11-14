# ב91: לשונית "אפסייל" בדשבורד הראשי. קריאה בלבד (ב30). דף האפסייל לא משתנה.
# מקורות:
#  - קודים (הונפקו / נוצלו / נדחו / פגו / בתוקף): API הדשבורד action=upsell - נתיב חדש ב-7843392 שקורא את 251557
#    בלי קוד, שם, מייל, טלפון ו-sid (make_route_upsell.json). עד שהנתיב קיים: "מקור הקודים עוד לא מחובר".
#  - רכישות, הכנסה ועמלות: שורות upsell_purchase בגיליון האירועים (אותן שורות כמו בבקרה הכספית, finUps), פעם אחת לעסקה.
# שימוש: python3 patch_dash_upsell.py <dashboard.html> <out> "<YYYY-MM-DD>" "<HH:MM>"   (לשורת היומן)
import sys
src, out, day, hm = sys.argv[1:5]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)

# CSS: בורר תקופה משלה, כמו בבקרה הכספית
rep('''body[data-scr="fin"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}''',
    '''body[data-scr="fin"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}
/* ב91 אפסייל: שלוש תקופות זו לצד זו, בלי הסינונים הכלליים */
body[data-scr="up"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}
#upTable td,#upTable th,#upAff td,#upAff th{white-space:nowrap}''')

rep('''    <button role="tab" data-s="fin"><b>11</b>בקרה כספית</button>''',
    '''    <button role="tab" data-s="fin"><b>11</b>בקרה כספית</button>
    <button role="tab" data-s="up"><b>12</b>אפסייל</button>''')

rep('''  <!-- 10 (ב71): השוואת קהלים - P25.''',
    '''  <!-- 12 (ב91): אפסייל 97 ₪. קריאה בלבד. קודים מ-251557 (דרך API הדשבורד, בלי פרטים אישיים), רכישות מהגיליון -->
  <section class="screen" id="s-up">
    <div class="banner" id="upSrc" hidden></div>
    <div class="panel"><div class="panel-h"><h2>אפסייל 97 ₪ - קודים ורכישות</h2><span class="note" id="upNote"></span></div><div class="tw"><table id="upTable"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>עמלות אפסייל לפי משווק</h2><span class="note" id="upAffNote"></span></div><div class="tw"><table id="upAff"></table></div></div>
  </section>

  <!-- 10 (ב71): השוואת קהלים - P25.''')

rep('''/* ================= 🧪 lab (ב43) ================= */''',
    '''/* ================= 12 אפסייל (ב91) ================= */
/* קודים: API action=upsell (נתיב ב-7843392 שקורא את 251557). כותרת לפי שמות, כך ששדות שיתווספו (opened, declined_at) ייקלטו בלי שינוי כאן.
   רשומות סימון (mailed:/alerted:) לא מגיעות - הנתיב מחזיר רק רשומות עם token. בדיקות: test=true או עסקה ב-TEST_DEALS (אלא אם "כולל בדיקות") */
let UPS=null, UPS_ST="idle";
function upsParse(t){const L=t.replace(/\\r/g,"").split("\\n"),h=(L[0]||"").split("\\t").map(x=>x.trim().toLowerCase());if(h[0]!=="upsell")return null;
 const D=v=>{v=(v||"").trim();if(!v)return null;const d=new Date(v.replace(" ","T"));return isNaN(d)?null:d},T=v=>/^true$/i.test((v||"").trim());
 return {cols:h,rows:L.slice(1).filter(l=>l.trim()).map(l=>{const a=l.split("\\t"),o={};h.forEach((k,i)=>{if(i)o[k]=(a[i-1]||"").trim()});
  return {created:D(o.created),expires:D(o.expires),paid:D(o.paid_at),used:T(o.used),declined:T(o.declined),test:T(o.test),aff:(o.aff||"").toLowerCase(),deal:o.deal||"",up:o.up_deal||"",
   opened:"opened" in o?D(o.opened):undefined}}).filter(r=>r.created)}}
function upsLoad(){UPS_ST="loading";fetch(API+"upsell",{cache:"no-store"}).then(r=>r.ok?r.text():"").then(t=>{UPS=upsParse(t);UPS_ST=UPS?"ok":"none"}).catch(()=>{UPS=null;UPS_ST="err"}).finally(()=>{if(screen==="up")render()})}
function upsTestDeal(d){return !!d&&TEST_DEALS.includes(d)}
function renderUpsell(){
 if(UPS_ST==="idle")upsLoad();
 const n=new Date(),sod=new Date(n.getFullYear(),n.getMonth(),n.getDate()),end=new Date(+sod+864e5);
 const PER=[["today","היום",sod],["7","7 ימים",new Date(+sod-6*864e5)],["mtd","מתחילת החודש",new Date(n.getFullYear(),n.getMonth(),1)]];
 const keep=[fSrc,fDev,fOwn];fSrc="";fDev="";fOwn="";let ALL;try{ALL=build(new Date(0),end)}finally{[fSrc,fDev,fOwn]=keep}
 /* רכישות מהגיליון: finUps (פעם אחת לעסקה), בלי עסקאות בדיקה - של האפסייל או של הקורס שממנו הונפק הקוד */
 const cdeal=r=>{const m=(r.qs||"").match(/course_deal\\s+(\\S+)/);return m?m[1]:""},CD={};ALL.R.forEach(r=>{if(r.ev==="upsell_purchase"){const d=(r.qs||"").match(/\\|\\s*deal\\s+(\\d+)/);if(d)CD[d[1]]=cdeal(r)}});
 const BUY=finUps(ALL).filter(x=>showTests||!(upsTestDeal(x.deal)||upsTestDeal(CD[x.deal]))),live=x=>affState(x)!=="refund";
 const C=UPS?UPS.rows.filter(r=>showTests||!(r.test||upsTestDeal(r.deal)||upsTestDeal(r.up))):[],hasOpen=!!UPS&&UPS.cols.includes("opened");
 const inP=(t,a)=>t&&t>=a&&t<end,MISS='<span class="na">חסר נתון</span>',WAIT='<span class="na">…</span>';
 const rowsT=[],head=["לפי מועד הנפקת הקוד"].concat(PER.map(p=>p[1]));
 const codeRow=(label,f,showPct)=>{rowsT.push('<tr><td>'+label+'</td>'+PER.map(([,,a])=>{if(!UPS)return '<td class="num">'+(UPS_ST==="loading"||UPS_ST==="idle"?WAIT:MISS)+'</td>';const I=C.filter(r=>inP(r.created,a)),v=I.filter(f).length;return '<td class="num">'+fmt(v)+(showPct?'<small>'+pf(pct(v,I.length))+'</small>':'')+'</td>'}).join("")+'</tr>')};
 codeRow("קודים שהונפקו <small>רוכשי קורס שקיבלו הצעה</small>",()=>true,false);
 codeRow("נוצלו <small>= רכישות אפסייל</small>",r=>r.used,true);
 codeRow("נדחו <small>\\"לא תודה\\"</small>",r=>r.declined&&!r.used,true);
 codeRow("לא נפתחו",r=>hasOpen?!r.opened&&!r.used&&!r.declined:false,true);
 if(!hasOpen)rowsT[rowsT.length-1]=rowsT[rowsT.length-1].replace(/<td class="num">[^]*?<\\/td>/g,'<td class="num">'+MISS+'</td>');
 codeRow("פגו בלי החלטה <small>לא נוצלו ולא נדחו"+(hasOpen?"":", כולל מי שלא פתח")+"</small>",r=>!r.used&&!r.declined&&r.expires&&r.expires<=n,true);
 codeRow("עדיין בתוקף <small>30 דקות מרכישת הקורס</small>",r=>!r.used&&!r.declined&&r.expires&&r.expires>n,true);
 rowsT.push('<tr><td><b>אחוז המרה</b> <small>רכישות אפסייל מתוך קודים שהונפקו</small></td>'+PER.map(([,,a])=>{if(!UPS)return '<td class="num">'+(UPS_ST==="loading"||UPS_ST==="idle"?WAIT:MISS)+'</td>';const I=C.filter(r=>inP(r.created,a));return '<td class="num"><b>'+pf(pct(I.filter(r=>r.used).length,I.length))+'</b></td>'}).join("")+'</tr>');
 rowsT.push('<tr><td colspan="'+(PER.length+1)+'" class="note">לפי מועד הרכישה (גיליון האירועים)</td></tr>');
 const buyRow=(label,g)=>rowsT.push('<tr><td>'+label+'</td>'+PER.map(([,,a])=>'<td class="num">'+g(BUY.filter(x=>inP(x.t,a)))+'</td>').join("")+'</tr>');
 buyRow("רכישות אפסייל",P=>fmt(P.filter(live).length)+(P.some(x=>!live(x))?' <small>'+fmt(P.filter(x=>!live(x)).length)+' הוחזרו</small>':''));
 buyRow("<b>הכנסה מאפסייל</b> <small>כולל מע\\"מ, בלי החזרים</small>",P=>'<b>'+ils(P.filter(live).reduce((s,x)=>s+x.amt,0))+'</b>');
 buyRow("עמלות אפסייל <small>"+FIN_UP_FEE+" ₪ לרכישה דרך משווק</small>",P=>ils(P.filter(x=>live(x)&&finCode(x)).reduce((s,x)=>s+FIN_UP_FEE,0)));
 table($("upTable"),head,rowsT);
 /* עמלות לפי משווק */
 const codes=[...new Set(BUY.map(finCode).filter(Boolean))].sort((x,y)=>((AFF[x]||{}).name||x).localeCompare((AFF[y]||{}).name||y,"he"));
 const affRows=codes.map(c=>'<tr><td><b>'+esc((AFF[c]||{}).name||c)+'</b>'+(AFF[c]?'':' <small>לא ברשימה</small>')+'</td>'+PER.map(([,,a])=>{const P=BUY.filter(x=>finCode(x)===c&&inP(x.t,a)),L=P.filter(live);return '<td class="num">'+ils(L.length*FIN_UP_FEE)+' <small>'+fmt(L.length)+' רכישות'+(P.length>L.length?' · '+fmt(P.length-L.length)+' הוחזרו':'')+'</small></td>'}).join("")+'</tr>');
 if(codes.length)affRows.push('<tr><td>בלי משווק <small>בלי עמלה</small></td>'+PER.map(([,,a])=>'<td class="num">'+fmt(BUY.filter(x=>!finCode(x)&&live(x)&&inP(x.t,a)).length)+' <small>רכישות</small></td>').join("")+'</tr>');
 table($("upAff"),["משווק"].concat(PER.map(p=>p[1])),affRows,"עוד אין רכישות אפסייל דרך משווקים");
 $("upAffNote").textContent="המשווק של רכישת הקורס. "+FIN_UP_FEE+" ₪ קבוע לכל רכישת אפסייל, גם למשווק באחוזים; החזר מבטל. סטטוס התשלום (ממתינה / לתשלום / שולמה) - בלשונית 11.";
 const u=$("upSrc");
 if(UPS_ST==="none"||UPS_ST==="err"){u.className="banner warn";u.textContent="מקור הקודים (251557) עוד לא מחובר ל-API של הדשבורד, ולכן אין כאן קודים שהונפקו, נדחו ואחוז המרה. הרכישות, ההכנסה והעמלות כבר מוצגות מהגיליון.";u.hidden=false}
 else if(UPS&&!hasOpen){u.className="banner";u.textContent="\\"לא נפתחו\\": חסר נתון - מאגר הקודים לא שומר אם ומתי הקוד נפתח. עד שיתווסף שדה כזה, מי שלא פתח נספר ב\\"פגו בלי החלטה\\".";u.hidden=false}
 else u.hidden=true;
 $("upNote").textContent="קריאה בלבד. קוד אחד לכל רכישת קורס מאומתת, בתוקף 30 דקות. הקודים נספרים לפי מועד ההנפקה, כך שאחוז ההמרה הוא מתוך אותם קודים. בלי עסקאות בדיקה"+(showTests?" (עכשיו: כולל בדיקות)":"")+". אחוזים מתוך הקודים שהונפקו באותה תקופה.";
}
/* ================= 🧪 lab (ב43) ================= */''')

rep('''fin:()=>renderFinance()})[screen]()''', '''fin:()=>renderFinance(),up:()=>renderUpsell()})[screen]()''')
# רענון: לטעון שוב גם את הקודים
rep('''async function load(){if(busy)return;busy=true;$("refresh").disabled=true;''',
    '''async function load(){if(busy)return;busy=true;$("refresh").disabled=true;if(UPS_ST!=="loading")UPS_ST="idle";''')

rep('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב91: לשונית 12 \\"אפסייל\\" (קריאה בלבד). היום / 7 ימים / מתחילת החודש: קודים שהונפקו, נוצלו, נדחו, פגו בלי החלטה ובתוקף (מ-251557, דרך action=upsell, בלי פרטים אישיים), אחוז המרה מתוך הקודים, רכישות והכנסה מאפסייל ועמלות אפסייל לפי משווק (72 ₪, מהגיליון). בלי עסקאות בדיקה. \\"לא נפתחו\\" - חסר נתון עד שהמאגר ישמור פתיחה."],
''' % (day, hm))
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
