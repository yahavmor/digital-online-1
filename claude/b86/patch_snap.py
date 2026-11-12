# ב86 (בן 12.11): דשבורד פשוט - מסך ראשי חדש "תמונת מצב". הלשוניות הקיימות עוברות ל"מתקדם" בלי מחיקה.
# שימוש: python3 patch_snap.py <dashboard.html> <out>     (מילון המודעות: ads_dict.json לידו - תמונה מהלשונית Ads, מ36)
# קריאה בלבד. רק רכישות מאומתות (כרטיס והעברה בנקאית, ב64). אנשים = מזהה מבקר (עמודה Q). בלי ביקורים פנימיים ובלי מזהי הבדיקה שלנו.
import sys, os, json
src, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
ADS = json.load(open(os.path.join(HERE, "ads_dict.json"), encoding="utf8"))
s = open(src, encoding="utf8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)


# 1. ניווט: "תמונת מצב" ראשון, ו"מתקדם" פותח את הלשוניות הקיימות
rep('''  <nav class="tabs" role="tablist" aria-label="מסכים">
''', '''  <nav class="tabs" role="tablist" aria-label="מסכים" id="tabsNav">
    <button role="tab" data-s="snap" class="snap-t"><b>◎</b>תמונת מצב</button>
    <button type="button" class="adv-t" id="advT" aria-expanded="false">מתקדם <span aria-hidden="true">▾</span></button>
''')

# 2. המסך
rep('''  <!-- 🧪 lab (ב43):''', '''  <!-- ◎ תמונת מצב (ב86): מסך ראשי פשוט. רק רכישות מאומתות, אנשים לפי מזהה מבקר, בלי ביקורים פנימיים -->
  <section class="screen" id="s-snap">
    <div class="snap-h"><h2>תמונת מצב</h2>
      <div class="seg" role="group" aria-label="תקופה" id="snapPer"><button data-p="week">השבוע</button><button data-p="today">היום</button><button data-p="7">7 ימים</button><button data-p="30">30 ימים</button><button data-p="launch">מההשקה</button></div>
      <span class="note" id="snapRange"></span></div>
    <div class="tiles snap-tiles" id="snapKpi"></div>
    <div class="panel"><div class="panel-h"><h2>מה עובד ומה לא</h2><span class="note">המלצה בלבד, לפי כללי מ35. ההחלטות פעם בשבוע (הראשונה 16.11), ו-72 שעות בלי לגעת אחרי שינוי</span></div><div id="snapLines" class="snap-lines"></div></div>
    <div class="panel"><div class="panel-h"><h2>מודעות</h2><span class="note">הקוד מופיע כשמעבירים את העכבר על השם</span></div><div class="tw"><table id="snapAds"></table></div><p class="note" id="snapAdsNote"></p></div>
    <div class="panel"><div class="panel-h"><h2>דפי מכירה</h2><span class="note">אנשים, ומתוכם כמה הגיעו לכל שלב</span><label class="chk"><input type="checkbox" id="snapGo"> רק תנועת הניסוי (go.html)</label></div><div class="tw"><table id="snapPages"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>דפי תשלום</h2><span class="note">מתוך מי שהגיע לדף התשלום</span></div><div class="tw"><table id="snapCo"></table></div></div>
    <p class="note" id="snapNote"></p>
  </section>

  <!-- 🧪 lab (ב43):''')

# 3. CSS
rep('''.tw{overflow-x:auto}''', '''.tw{overflow-x:auto}
/* ב86 תמונת מצב */
nav.tabs:not(.open) button[data-s]:not([data-s="snap"]){display:none}
nav.tabs .adv-t{flex:none;border:0;background:transparent;color:var(--muted);font:600 14px var(--f-body);padding:10px 12px;cursor:pointer;white-space:nowrap}
nav.tabs.open .adv-t{color:var(--ink)}
body[data-scr="snap"] :is(#range,#customBox,#fSrc,#fOwn,#fDev,.controls .chk){display:none!important}
.snap-h{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:4px 0 12px}
.snap-h h2{margin:0;font-size:22px}
.snap-tiles{grid-template-columns:repeat(5,minmax(0,1fr))}
.snap-lines{display:grid;gap:8px}
.snap-line{display:flex;gap:10px;align-items:flex-start;border-radius:12px;padding:10px 14px;font-size:15px;line-height:1.5}
.snap-line i{flex:none;width:12px;height:12px;border-radius:50%;margin-top:6px}
.snap-line.g{background:var(--good-bg)} .snap-line.g i{background:var(--good)}
.snap-line.y{background:var(--warn-bg)} .snap-line.y i{background:var(--warn)}
.snap-line.r{background:var(--crit-bg)} .snap-line.r i{background:var(--crit)}
#snapAds td,#snapAds th,#snapPages td,#snapPages th,#snapCo td,#snapCo th{white-space:nowrap}
#snapAds td.nm{white-space:normal;min-width:150px;max-width:220px}
#snapAds td.nm small.ty{display:block;color:var(--muted);font-weight:400}
@media (max-width:760px){.snap-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.snap-tiles .tile:last-child{grid-column:1/-1}}''')

# 4. ברירת המחדל: תמונת מצב (רק #hash פותח לשונית אחרת)
rep('''screen="op"''', '''screen="snap"''')
rep('''const sc=(location.hash||"").slice(1)||(st()&&st().getItem("nlpdash_screen"));''', '''const sc=(location.hash||"").slice(1); /* ב86: בלי #, נפתח תמיד במסך "תמונת מצב" */''')
rep('''function setScreen(s){screen=s;''', '''function setScreen(s){screen=s;document.body.dataset.scr=s;if(s!=="snap"&&$("tabsNav"))$("tabsNav").classList.add("open");''')
rep('''({lab:()=>renderLab(M,B),''', '''({snap:()=>renderSnap(),lab:()=>renderLab(M,B),''')
rep('''document.querySelectorAll("nav.tabs button").forEach(b=>b.onclick=()=>setScreen(b.dataset.s));''',
    '''document.querySelectorAll("nav.tabs button[data-s]").forEach(b=>b.onclick=()=>setScreen(b.dataset.s));
 $("advT").onclick=()=>{const n=$("tabsNav"),o=n.classList.toggle("open");$("advT").setAttribute("aria-expanded",String(o));if(!o&&screen!=="snap")setScreen("snap");};
 document.querySelectorAll("#snapPer button").forEach(x=>x.onclick=()=>{snapPer=x.dataset.p;render()});$("snapGo").onchange=e=>{snapGo=e.target.checked;render()};snapAds();''')

JS = r'''/* ================= ◎ תמונת מצב (ב86) =================
   רק רכישות מאומתות (כרטיס והעברה בנקאית, ב64). אנשים = מזהה מבקר (עמודה Q). בלי ביקורים פנימיים ובלי מזהי מבקר שהופיעו בבדיקות שלנו.
   שם וסוג לכל מודעה: "מילון המודעות" (לשונית Ads בגיליון, מ36). קוד בלי שם - "לא מזוהה".
   הוצאה לכל מודעה: אותו טופס הוצאה, מפתח "YYYY-MM-DD|utm_content" (הפורמט שהממומן מזין במ36 סעיף 3). הוצאה כללית שלנו: מפתח "YYYY-MM-DD".
   כללי מ35: עד 245 ₪ לרכישה אצלנו ועד 220 ₪ אצל משווק; כל עוד יש מעט רכישות - עד 35 ₪ למעבר לתשלום; 250 ₪ בלי מעבר לתשלום,
   או 500 ₪ בלי רכישה (משווק 440 ₪) - עצירה. המלצה בלבד: החלטות פעם בשבוע (הראשונה 16.11), 72 שעות בלי לגעת אחרי שינוי. */
const SNAP_LAUNCH=new Date("2026-10-20T00:00"), SNAP_TEST_VIDS=["77438727","fead4466"];
const SNAP_PAGES={a5v6:"דף A החדש (a5v6)",pr2:"דף הפרימיום (pr2)",a5:"דף A הקודם (a5)",a:"דף A המקורי (a)",a5v4:"דף בדיקה a5v4",a5v5:"דף בדיקה a5v5"};
const SNAP_CO={a:"דף תשלום 1 - שני שלבים (A)",b:"דף תשלום 2 - מסך אחד (B)"};
const M35={cpa:245,cpaAff:220,perChk:35,noChk:250,noBuy:500,noBuyAff:440,few:3};
let snapPer="week", snapGo=false, SNAP_TV=null, SNAP_FIRST=null, SNAP_TV_N=-1;
let ADS=Object.fromEntries(__ADS__.map(r=>[r[0].toLowerCase(),{name:r[1],type:r[2],camp:r[3],aud:r[4],status:r[5]}])), ADS_SRC="תמונה של הלשונית Ads (12.11)";
/* מילון חי מה-API (פעולה ads ב-7843392), אם קיימת; אחרת נשארת התמונה */
function snapAds(){fetch(API+"ads",{cache:"no-store"}).then(r=>r.ok?r.text():"").then(t=>{if(!/^ads\n/.test(t))return;const m={};t.split("\n").slice(1).forEach(l=>{const a=l.split("\t");if(a[0]&&a[0].trim())m[a[0].trim().toLowerCase()]={name:(a[1]||"").trim(),type:(a[2]||"").trim(),camp:(a[3]||"").trim(),aud:(a[4]||"").trim(),status:(a[5]||"").trim()}});
 if(Object.keys(m).length){ADS=m;ADS_SRC="הלשונית Ads (חי)";if(screen==="snap")render();}}).catch(()=>{})}
function snapBounds(){const n=new Date(),sod=new Date(n.getFullYear(),n.getMonth(),n.getDate()),b=new Date(+sod+864e5);let a;
 if(snapPer==="today")a=sod;else if(snapPer==="week")a=new Date(n.getFullYear(),n.getMonth(),n.getDate()-n.getDay());else if(snapPer==="launch")a=SNAP_LAUNCH;else a=new Date(n.getFullYear(),n.getMonth(),n.getDate()-(+snapPer-1));
 return {a,b}}
function snapTV(){if(SNAP_TV&&SNAP_TV_N===rows.length)return SNAP_TV;SNAP_TV=new Set(rows.filter(isTest).map(r=>r.vid).filter(Boolean));
 SNAP_FIRST=new Map();rows.forEach(r=>{if(r.sid&&!isNaN(r.t)&&!SNAP_FIRST.has(r.sid))SNAP_FIRST.set(r.sid,r.t)}); /* השורות ממוינות לפי זמן: הראשונה = תחילת הביקור */
 SNAP_TV_N=rows.length;return SNAP_TV}
function snapCode(s){return ((s.p&&s.p.get("utm_content"))||"").trim()}
function renderSnap(){
 const B=snapBounds(),keep=[fSrc,fDev,fOwn,showTests];fSrc="";fDev="";fOwn="";showTests=false;let M;try{M=build(B.a,B.b)}finally{[fSrc,fDev,fOwn,showTests]=keep}
 document.querySelectorAll("#snapPer button").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.p===snapPer)));
 $("snapRange").textContent=B.a.toLocaleDateString("he-IL",{day:"2-digit",month:"2-digit"})+" עד היום";
 const TV=snapTV(),internal=s=>TV.has(s.vid)||SNAP_TEST_VIDS.some(p=>(s.vid||"").indexOf(p)===0);
 const S=M.sess.filter(s=>!internal(s)&&!(SNAP_FIRST.get(s.sid)<B.a)) /* ביקור נספר לפי שעת ההתחלה שלו: אירוע מאוחר (יציאה, שגיאה) של ביקור שהתחיל לפני התקופה לא נספר */,who=s=>s.vid||s.sid,uniq=a=>new Set(a.map(who)).size;
 const buys=M.buys.filter(b=>!(b.s&&internal(b.s))),bySid=new Map();buys.forEach(b=>{if(b.sid)bySid.set(b.sid,b)});
 const bought=s=>bySid.has(s.sid),na='<span class="na">-</span>',pc=(k,n)=>n?' <small>'+pf(pct(k,n))+'</small>':'';
 /* --- למעלה --- */
 const spLast=Object.keys(spend).filter(k=>{const d=new Date(k+"T12:00");return d>=B.a&&d<B.b}).sort().pop()||"";
 const sp=spendIn(B.a,B.b),ours=buys.filter(b=>!b.aff),rev=buys.reduce((x,b)=>x+b.amt,0),ourRev=ours.reduce((x,b)=>x+b.amt,0),cpa=sp!=null&&ours.length?sp/ours.length:null;
 $("snapKpi").innerHTML=[
  tile("הוצאה על מודעות",sp==null?na:ils(sp),"החשבון של בן"+(spLast&&spLast<dayKey(new Date(+B.b-2*864e5))?" · מוזן עד "+spLast.split("-").reverse().slice(0,2).join("."):""),""),
  tile("הכנסות",ils(rev),"מרכישות מאומתות, כולל מע\"מ",""),
  tile("רכישות",fmt(buys.length),buys.length?fmt(buys.filter(b=>b.bank).length)+" בהעברה בנקאית · "+fmt(buys.length-ours.length)+" דרך משווקים":"מאומתות בלבד",""),
  tile("עלות לרכישה",cpa==null?na:ils(cpa),cpa==null?(sp?"אין עדיין רכישות מהמודעות של בן":""):'<span class="pill '+(cpa<=M35.cpa?"good":"crit")+'">'+(cpa<=M35.cpa?"עד ":"מעל ")+ils(M35.cpa)+'</span>',"הוצאה ÷ רכישות שלא דרך משווק"),
  tile("ROAS",sp?(ourRev/sp).toFixed(2):na,sp?"כל 1 ₪ על מודעות החזיר "+(ourRev/sp).toFixed(2)+" ₪":"","הכנסה שלא דרך משווק ÷ הוצאה")].join("");
 /* --- מודעות --- */
 const spC={},spD={};for(const k in cspend){const [d,c]=k.split("|");if(!c||/^aff_/.test(c))continue;const dt=new Date(d+"T12:00");if(dt>=B.a&&dt<B.b){const kk=c.toLowerCase();spC[kk]=(spC[kk]||0)+cspend[k];(spD[kk]=spD[kk]||new Set()).add(d)}}
 const G={};S.forEach(s=>{const c=snapCode(s).toLowerCase();(G[c]=G[c]||[]).push(s)});
 const A=Object.keys(G).map(c=>{const ss=G[c],d=ADS[c],chk=uniq(ss.filter(s=>s.chk)),b=ss.filter(bought).length,spend=spC[c]!=null?spC[c]:null,aff=d&&/משווק/.test(d.aud)&&!/קר|חם/.test(d.aud);
   /* עלות לרכישה וההמלצות: רק על הימים שיש להם הוצאה למודעה הזו - כדי לא לחלק הוצאה של יום אחד ברכישות של חודש */
   const sd=spD[c],ds=sd?ss.filter(s=>sd.has(dayKey(SNAP_FIRST.get(s.sid)||s.t))):[],schk=uniq(ds.filter(s=>s.chk)),sb=ds.filter(bought).length;
   return {c,d,ppl:uniq(ss),chk:schk,b:sb,tchk:chk,tb:b,spend,aff,cpa:spend!=null&&sb?spend/sb:null,partial:!!sd&&sd.size<Math.round((Math.min(B.b,new Date())-B.a)/864e5)}}).sort((x,y)=>y.ppl-x.ppl);
 const nm=r=>!r.c?'<b>בלי קוד מודעה</b> <small>כניסה ישירה או אורגנית</small>':r.d?'<b title="קוד: '+esc(r.c)+'">'+esc(r.d.name)+'</b>':'<b title="קוד: '+esc(r.c)+'">לא מזוהה</b>';
 const SHOW=25,typ=r=>r.d&&r.d.type?'<small class="ty">'+esc(r.d.type)+'</small>':'';
 const rowsA=A.slice(0,SHOW).map(r=>'<tr><td class="nm">'+nm(r)+typ(r)+'</td><td class="num">'+fmt(r.ppl)+'</td><td class="num">'+fmt(r.tchk)+pc(r.tchk,r.ppl)+'</td><td class="num">'+fmt(r.tb)+'</td><td>'+(r.spend==null?na:ils(r.spend)+(r.partial?' <small>'+(spD[r.c].size===1?'יום אחד':fmt(spD[r.c].size)+' ימים')+'</small>':''))+'</td><td>'+(r.cpa!=null?ils(r.cpa):r.spend?'<small>אין רכישות בימים האלה</small>':na)+'</td><td>'+(r.d&&r.d.aud?esc(r.d.aud):na)+'</td><td><small>'+(r.d&&r.d.camp?esc(r.d.camp):"")+'</small></td></tr>');
 table($("snapAds"),["מודעה","אנשים","הגיעו לסליקה","רכישות","הוצאה","עלות לרכישה","קהל","קמפיין"],rowsA,"אין כניסות בתקופה");
 const unk=A.filter(r=>r.c&&!r.d);
 $("snapAdsNote").textContent=(A.length>SHOW?"מוצגות "+SHOW+" המודעות עם הכי הרבה אנשים מתוך "+A.length+". ":"")+(unk.length?"לא מזוהים ("+unk.length+"): צריך להוסיף אותם למילון המודעות. ":"")+"השמות מ"+ADS_SRC+". הוצאה לכל מודעה - מהטופס, כשהממומן מזין אותה (מ36). עלות לרכישה - רק על הימים שהוזנה להם הוצאה למודעה.";
 /* --- דפי מכירה ודפי תשלום --- */
 const pageRow=(lab,ss)=>{const n=uniq(ss),c=uniq(ss.filter(s=>s.chk)),st=uniq(ss.filter(s=>s.cstart)),py=uniq(ss.filter(s=>s.pay)),b=uniq(ss.filter(bought));
  return '<tr><td><b>'+esc(lab)+'</b></td><td class="num">'+fmt(n)+'</td><td class="num">'+fmt(c)+pc(c,n)+'</td><td class="num">'+fmt(st)+pc(st,n)+'</td><td class="num">'+fmt(py)+pc(py,n)+'</td><td class="num">'+fmt(b)+pc(b,n)+'</td></tr>'};
 const SP=snapGo?S.filter(s=>s.go):S,byV={};SP.forEach(s=>{(byV[s.v]=byV[s.v]||[]).push(s)});const V=Object.keys(byV).sort((x,y)=>uniq(byV[y])-uniq(byV[x]));
 table($("snapPages"),["דף","אנשים","הגיעו לסליקה","התחילו להזין פרטים","שלב התשלום","רכישות"],V.map(v=>pageRow(SNAP_PAGES[v]||VLBL[v]||v,byV[v])),"אין כניסות בתקופה");
 const byC={};SP.filter(s=>s.chk).forEach(s=>{const c=s.co==="a"||s.co==="b"?s.co:"?";(byC[c]=byC[c]||[]).push(s)});
 const coRow=(lab,ss)=>{const n=uniq(ss),st=uniq(ss.filter(s=>s.cstart)),py=uniq(ss.filter(s=>s.pay)),b=uniq(ss.filter(bought));return '<tr><td><b>'+esc(lab)+'</b></td><td class="num">'+fmt(n)+'</td><td class="num">'+fmt(st)+pc(st,n)+'</td><td class="num">'+fmt(py)+pc(py,n)+'</td><td class="num">'+fmt(b)+pc(b,n)+'</td></tr>'};
 table($("snapCo"),["דף תשלום","הגיעו","התחילו להזין פרטים","שלב התשלום","רכישות"],Object.keys(byC).sort().map(c=>coRow(SNAP_CO[c]||"לא ידוע",byC[c])),"אף אחד לא הגיע לדף התשלום בתקופה");
 /* --- מה עובד ומה לא (מ35) --- */
 const W=A.filter(r=>r.c&&r.spend>0),L=[];const nmT=r=>r.d?r.d.name:"מודעה לא מזוהה ("+r.c+")";
 const tgt=r=>r.aff?M35.cpaAff:M35.cpa,perC=r=>r.chk?r.spend/r.chk:null;
 const isRed=r=>r.spend>=M35.noChk&&!r.chk||r.spend>=(r.aff?M35.noBuyAff:M35.noBuy)&&!r.b;
 const isGreen=r=>!isRed(r)&&(r.b&&r.cpa<=tgt(r)||r.chk&&perC(r)<=M35.perChk&&r.b<M35.few);
 const red=W.filter(isRed).sort((x,y)=>y.spend-x.spend)[0];
 const green=W.filter(isGreen).sort((x,y)=>(x.b&&x.cpa<=tgt(x)?x.cpa/tgt(x):1+perC(x)/M35.perChk)-(y.b&&y.cpa<=tgt(y)?y.cpa/tgt(y):1+perC(y)/M35.perChk))[0];
 const yellow=W.filter(r=>!isRed(r)&&!isGreen(r)).sort((x,y)=>y.spend-x.spend)[0];
 if(!W.length){L.push(["y","עוד אין הוצאה לפי מודעה בטופס ההוצאה, ולכן אי אפשר לדעת איזו מודעה משתלמת. כשהממומן יזין אותה (מ36), כאן יופיעו ההמלצות."]);
  const bestPage=V.filter(v=>uniq(byV[v])>=50).map(v=>({v,r:uniq(byV[v].filter(s=>s.chk))/uniq(byV[v])})).sort((x,y)=>y.r-x.r)[0];
  L.unshift(["g",buys.length?fmt(buys.length)+" רכישות מאומתות בתקופה"+(bestPage?". הכי הרבה הגעה לסליקה: "+(SNAP_PAGES[bestPage.v]||bestPage.v)+" ("+pf(bestPage.r*100)+")":"")+".":"עוד אין רכישות מאומתות בתקופה."]);
  L.push(["r","אין מודעה שעברה את סף העצירה (אין נתוני הוצאה לפי מודעה)."]);}
 else{
  L.push(green?["g",nmT(green)+": "+(green.b&&green.cpa<=tgt(green)?"עלות לרכישה "+ils(green.cpa)+" (היעד עד "+ils(tgt(green))+"). לפי הכללים: אפשר להגדיל ב-20% תקציב, כל 3 ימים.":ils(perC(green))+" לכל מי שהגיע לסליקה (היעד עד 35 ₪ כל עוד יש מעט רכישות). ממשיכים.")]:["g","עוד אין מודעה שעומדת ביעד (עד "+ils(M35.cpa)+" לרכישה, או עד 35 ₪ לכל מי שמגיע לסליקה)."]);
  L.push(yellow?["y",nmT(yellow)+": "+(yellow.b&&yellow.cpa>tgt(yellow)?"עלות לרכישה "+ils(yellow.cpa)+", מעל היעד ("+ils(tgt(yellow))+"). לעקוב.":yellow.chk?ils(perC(yellow))+" לכל מי שהגיע לסליקה, מעל 35 ₪. לעקוב עוד כמה ימים.":"הוציאה "+ils(yellow.spend)+" ועוד אף אחד לא הגיע לסליקה (העצירה ב-250 ₪).")]:["y","אין מודעה באמצע - כל המודעות עם הוצאה כבר ביעד או מעבר לסף."]);
  L.push(red?["r",nmT(red)+": הוציאה "+ils(red.spend)+" "+(!red.chk?"בלי אף אחד שהגיע לסליקה":"בלי רכישה")+". לפי הכללים: לעצור."]:["r","אין מודעה שעברה את סף העצירה (250 ₪ בלי הגעה לסליקה, או "+ils(M35.noBuy)+" בלי רכישה)."]);}
 $("snapLines").innerHTML=L.slice(0,3).map(l=>'<div class="snap-line '+l[0]+'"><i aria-hidden="true"></i><span>'+esc(l[1])+'</span></div>').join("");
 $("snapNote").textContent="רק רכישות מאומתות (כרטיס והעברה בנקאית). אנשים = מבקר ייחודי לפי מזהה הדפדפן. בלי ביקורים פנימיים ובלי מבקרים שהופיעו בבדיקות שלנו, ובלי סריקות של Meta. הוצאה ועלות לרכישה - מטופס ההוצאה. הלשוניות המפורטות - בכפתור \"מתקדם\".";
}
/* ================= 🧪 lab (ב43) ================= */'''
rep('''/* ================= 🧪 lab (ב43) ================= */''', JS.replace("__ADS__", json.dumps(ADS, ensure_ascii=False, separators=(",", ":"))))
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
