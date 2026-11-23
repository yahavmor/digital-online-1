# ב84 (בן 11.11 דרך הראשי): לשונית 11 "בקרה כספית" בדשבורד. קריאה בלבד (ב30).
# שימוש: python3 patch_fin.py <dashboard.html בכניסה> <קובץ יציאה>
# לא נוגע בשום לשונית קיימת. מוסיף: כפתור לשונית, מסך s-fin, שתי שורות טעינה (תקציב ותאריך תשלום, אם השדות קיימים), renderFinance.
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)


# 1. כפתור הלשונית
rep('''    <button role="tab" data-s="aud"><b>10</b>השוואת קהלים - P25</button>
''', '''    <button role="tab" data-s="aud"><b>10</b>השוואת קהלים - P25</button>
    <button role="tab" data-s="fin"><b>11</b>בקרה כספית</button>
''')

# 2. המסך
rep('''  <!-- 10 (ב71):''', '''  <!-- 11 (ב84): בקרה כספית. קריאה בלבד - בלי פעולות כתיבה (ב30). סימון "שולם" והחזרים: אצל הראשי ב-Make -->
  <section class="screen" id="s-fin">
    <div class="panel"><div class="panel-h"><h2>בקרה כספית</h2>
      <div class="seg" role="group" aria-label="תקופה" id="finPer"><button data-p="today">היום</button><button data-p="7">7 ימים</button><button data-p="mtd">מתחילת החודש</button><button data-p="all">הכול</button></div></div>
      <p class="note" id="finNote"></p></div>
    <div class="panel"><div class="panel-h"><h2>התראות</h2></div><div id="finAlerts" class="fin-al"></div></div>
    <div class="panel"><div class="panel-h"><h2>אצלנו</h2><span class="note" id="finUsNote"></span></div><div class="tiles" id="finUs"></div></div>
    <div class="panel"><div class="panel-h"><h2>לפי משווק</h2><span class="note">כניסות והגעות לסליקה = אנשים, בלי סריקות. עמלות לפי רכישות התקופה; יתרה לתשלום - מכל הזמן</span></div><div class="tw"><table id="finAff"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>פירוט למשווק</h2>
      <div class="fin-det-h"><select id="finAffSel" aria-label="משווק"></select><button type="button" id="finCopy" class="fin-copy">העתקה</button></div></div>
      <div class="tw"><table id="finDet"></table></div><p class="note" id="finDetNote"></p></div>
  </section>

  <!-- 10 (ב71):''')

# 3. CSS
rep('''.tw{overflow-x:auto}''', '''.tw{overflow-x:auto}
/* ב84 בקרה כספית */
.fin-al{display:grid;gap:8px}
.fin-al .banner{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.fin-det-h{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.fin-copy{font:600 14px var(--f-body);padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
#finAff td,#finAff th{white-space:nowrap}
/* בלשונית הזו יש בורר תקופה משלה, והסינונים הכלליים לא חלים עליה - מוסתרים כדי שלא יבלבלו */
body[data-scr="fin"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}''')

# 4. טעינה: תקציב (עמודת budget, כשתתווסף ב-237596) ותאריך/אסמכתא לעמלות ששולמו (אם קיימים ב-237837)
rep('''fee:+fe||0}});ownOpts()}}''', '''fee:+fe||0}});finBudgets(tc);ownOpts()}}''')
rep('''if(/^paid/.test(te))PAID=new Set(te.split("\\n").slice(1).map(l=>(l.split("\\t")[0]||"").trim()).filter(Boolean))}''',
    '''if(/^paid/.test(te)){PAID=new Set(te.split("\\n").slice(1).map(l=>(l.split("\\t")[0]||"").trim()).filter(Boolean));PAIDAT=finPaidAt(te)}}''')

# 5. ניתוב (והסתרת הסינונים הכלליים בלשונית הזו)
rep('''function render(){if(!rows)return;''', '''function render(){document.body.dataset.scr=screen;if(!rows)return;''')
rep('''af:()=>renderAffiliates(),aud:()=>renderAud()''', '''af:()=>renderAffiliates(),aud:()=>renderAud(),fin:()=>renderFinance()''')

# 6. הקוד
JS = r'''/* ================= 11 בקרה כספית (ב84) =================
   קריאה בלבד (ב30). עמלה: fee מרשימת המשווקים (220 ₪) לרכישת קורס, 72 ₪ לאפסייל. ממתינה 7 ימים ואז "לתשלום". החזר מבטל.
   תקציב יומי: עמודת budget ב-237596 - תתווסף ב-Make רק אחרי "מאשר ב84"; עד אז "חסר נתון". עמלות סליקה: לפי השיעור שבן ימסור (FIN_PROC_RATE).
   בפירוט למשווק: בלי שמות, טלפונים ומיילים של רוכשים, ומספר עסקה מוצג רק בשלוש הספרות האחרונות ("מסתיים ב-123") */
const FIN_FEE=220, FIN_UP_FEE=72, FIN_OUR_CPA=245, FIN_PROC_RATE=null, FIN_DUE_DAYS=3, FIN_OVER=1.2;
let finPer="7", finAff="", PAIDAT={};
function finBudgets(tc){const L=tc.split("\n"),h=L[0].split("\t").map(x=>x.trim().toLowerCase()),i=h.indexOf("budget");if(i<0)return;
 L.slice(1).forEach(l=>{const a=l.split("\t"),c=(a[0]||"").trim().toLowerCase();if(c&&AFF[c]){const v=+(a[i]||"").trim();AFF[c].budget=v>0?v:null}})}
function finPaidAt(te){const L=te.split("\n"),h=L[0].split("\t").map(x=>x.trim().toLowerCase()),ia=["at","date","paid_at"].map(k=>h.indexOf(k)).find(i=>i>0),ir=["ref","reference"].map(k=>h.indexOf(k)).find(i=>i>0),o={};
 L.slice(1).forEach(l=>{const a=l.split("\t"),d=(a[0]||"").trim();if(d)o[d]={at:ia?(a[ia]||"").trim():"",ref:ir?(a[ir]||"").trim():""}});return o}
function finBounds(){const n=new Date(),sod=new Date(n.getFullYear(),n.getMonth(),n.getDate()),b=new Date(+sod+864e5);
 return {sod,b,a:finPer==="today"?sod:finPer==="7"?new Date(+sod-6*864e5):finPer==="mtd"?new Date(n.getFullYear(),n.getMonth(),1):new Date(0)}}
/* אפסייל: מ-build אחרי ב74; עד אז קריאה ישירה של אותן שורות (upsell_purchase מ-cardcom_upsell_webhook), פעם אחת לכל עסקה */
function finUps(M){if(M.allUps)return M.allUps;const seen=new Set(),o=[];M.R.forEach(r=>{if(!(r.ev==="upsell_purchase"&&r.cta==="cardcom_upsell_webhook"))return;
 const d=(r.qs||"").match(/\|\s*deal\s+(\d+)/),m=(r.qs||"").match(/(\d+(?:\.\d+)?)\s*ILS/),deal=d?d[1]:"";if(!deal||seen.has(deal))return;seen.add(deal);
 o.push({t:r.t,day:dayKey(r.t),amt:m?+m[1]:97,deal,sid:r.sid||"",aff:(parseX(r.x).aff||"").toLowerCase(),up:true})});return o}
const finCode=b=>(b.aff||"").toLowerCase();
function finFee(b){if(!finCode(b))return 0;if(b.up)return FIN_UP_FEE;const inf=AFF[finCode(b)];return inf&&inf.fee>0?inf.fee:FIN_FEE}
function finDueSince(b){return +b.t+PAY_DAYS*864e5}
function finMask(b){const d=b.bank?b.deal.slice(5):(b.deal||"");return (b.bank?"העברה, ":"")+(d?"מסתיים ב-"+d.slice(-3):"-")}
function finDate(x){const d=x instanceof Date?x:new Date(x);return isNaN(d)?String(x||""):d.toLocaleDateString("he-IL",{day:"2-digit",month:"2-digit",year:"numeric"})}
function finAffSpend(a,b,code){const x=spendIn(a,b,"aff_"+code),y=spendIn(a,b,"aff_"+code+"_ic");return x==null&&y==null?null:(x||0)+(y||0)}
function finNextSunday(sod){return new Date(+sod+((7-sod.getDay())%7)*864e5)}
function renderFinance(){
 const B=finBounds(),now=new Date(),keep=[fSrc,fDev,fOwn];fSrc="";fDev="";fOwn="";let M,ALL;
 try{ALL=build(new Date(0),B.b);M=finPer==="all"?ALL:build(B.a,B.b)}finally{[fSrc,fDev,fOwn]=keep}
 document.querySelectorAll("#finPer button").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.p===finPer)));
 const MISS='<span class="na">חסר נתון</span>',na='<span class="na">-</span>',LAB={pending:"ממתינה",due:"לתשלום",paid:"שולמה",refund:"בוטלה (החזר)"},PILL={pending:"warn",due:"good",paid:"off",refund:"crit"};
 const items=X=>X.allBuys.concat(finUps(X)),PI=items(M),AI=items(ALL),live=x=>affState(x)!=="refund";
 const days=Math.max(1,Math.round((B.b-Math.max(+B.a,(()=>{const k=Object.keys(cspend).concat(Object.keys(spend)).map(k=>k.split("|")[0]).sort()[0];return k?+new Date(k+"T00:00"):+B.sod})()))/864e5));
 /* --- אצלנו --- */
 const ours=PI.filter(x=>!finCode(x)),inc=PI.filter(live).reduce((s,x)=>s+x.amt,0),refd=PI.filter(x=>!live(x)),vat=inc-inc/(1+VAT),comm=PI.filter(x=>finCode(x)&&live(x)).reduce((s,x)=>s+finFee(x),0),
  sp=spendIn(B.a,B.b),proc=FIN_PROC_RATE!=null?inc*FIN_PROC_RATE:null,net=inc/(1+VAT)-(sp||0)-comm-(proc||0),ourBuys=ours.filter(x=>!x.up&&live(x)).length,ourRev=ours.filter(live).reduce((s,x)=>s+x.amt,0),
  cpa=sp!=null&&ourBuys?sp/ourBuys:null;
 $("finUs").innerHTML=[
  tile("הוצאה (החשבון שלנו)",sp==null?MISS:ils(sp),"","210972 · לפי מנהל המודעות"),
  tile("הכנסה מאומתת",ils(inc),fmt(PI.filter(x=>!x.up&&live(x)).length)+" קורס · "+fmt(PI.filter(x=>x.up&&live(x)).length)+" אפסייל","כרטיס והעברה בנקאית, כולל מע\"מ, בלי החזרים"),
  tile("מע\"מ 18%",ils(vat),"","מתוך ההכנסה"),
  tile("עמלות סליקה",proc==null?MISS:ils(proc),proc==null?"לפי השיעור שבן ימסור":"","קארדקום"),
  tile("עמלות משווקים",ils(comm),"220 ₪ לרכישה · 72 ₪ לאפסייל","כל המצבים חוץ מהחזר"),
  tile("נטו לפני מס",ils(net),(sp==null?"בלי הוצאה (חסר נתון) · ":"")+(proc==null?"בלי עמלות סליקה":""),"הכנסה בלי מע\"מ פחות הוצאה ועמלות",true),
  tile("עלות לרכישה",cpa==null?na:ils(cpa),cpa==null?"":'<span class="pill '+(cpa<=FIN_OUR_CPA?"good":"crit")+'">'+(cpa<=FIN_OUR_CPA?"עד ":"מעל ")+ils(FIN_OUR_CPA)+'</span>',"הוצאה שלנו ÷ רכישות קורס שלא דרך משווק"),
  tile("ROAS",sp?(ourRev/sp).toFixed(2):na,"","הכנסה שלא דרך משווק ÷ הוצאה שלנו"),
  tile("רכישות שלנו",fmt(ourBuys),fmt(PI.filter(x=>finCode(x)&&!x.up&&live(x)).length)+" דרך משווקים",""),
  tile("החזרים",fmt(refd.length),refd.length?ils(refd.reduce((s,x)=>s+x.amt,0)):"","לפי 237694")].join("");
 $("finUsNote").textContent={today:"היום",7:"7 הימים האחרונים כולל היום",mtd:"מתחילת החודש",all:"כל הזמן"}[finPer];
 /* --- לפי משווק --- */
 const codes=[...new Set(Object.keys(AFF).filter(k=>AFF[k].active&&!/^claude/.test(k)).concat(AI.map(finCode).filter(Boolean)))].sort((x,y)=>{const i=AFF_FIRST.indexOf(x),j=AFF_FIRST.indexOf(y);return (i<0?99:i)-(j<0?99:j)||((AFF[x]||{}).name||x).localeCompare((AFF[y]||{}).name||y,"he")});
 const nextPay=finNextSunday(B.sod),sum=(X,st)=>X.filter(x=>affState(x)===st).reduce((s,x)=>s+finFee(x),0);
 const rowsA=codes.map(code=>{const inf=AFF[code],bud=inf&&inf.budget?inf.budget:null,spP=finAffSpend(B.a,B.b,code),spA=finAffSpend(new Date(0),B.b,code),
   S=M.sess.filter(s=>(s.aff||"").toLowerCase()===code),ppl=new Set(S.map(s=>s.vid||s.sid)),chk=new Set(S.filter(s=>s.chk).map(s=>s.vid||s.sid)),
   P=PI.filter(x=>finCode(x)===code),A=AI.filter(x=>finCode(x)===code),C=P.filter(x=>!x.up&&live(x)),U=P.filter(x=>x.up&&live(x)),cp=spP!=null&&C.length?spP/C.length:null,bal=sum(A,"due");
   return '<tr><td><b>'+esc(inf?inf.name:code)+'</b>'+(inf?"":' <small>לא ברשימה</small>')+'</td><td>'+(bud?ils(bud):MISS)+'</td><td>'+(spP==null?na:ils(spP))+'</td><td>'+(spA==null?na:ils(spA))+'</td><td>'+(bud&&spP!=null?pf(spP/(bud*days)*100):MISS)+'</td>'+
    '<td class="num">'+fmt(ppl.size)+'</td><td class="num">'+fmt(chk.size)+'</td><td class="num">'+fmt(C.length)+' <small>'+fmt(C.filter(x=>!x.bank).length)+' כרטיס · '+fmt(C.filter(x=>x.bank).length)+' העברה</small></td>'+
    '<td>'+ils(C.reduce((s,x)=>s+x.amt,0))+'</td><td>'+ils(U.reduce((s,x)=>s+x.amt,0))+' <small>'+fmt(U.length)+'</small></td>'+
    '<td>'+ils(sum(P,"pending"))+'</td><td>'+ils(sum(P,"due"))+'</td><td>'+ils(sum(P,"paid"))+'</td><td class="num">'+fmt(P.filter(x=>!live(x)).length)+'</td><td><b>'+ils(bal)+'</b></td><td>'+(bal?finDate(nextPay):na)+'</td>'+
    '<td>'+(cp==null?na:ils(cp)+' <span class="pill '+(cp<=FIN_FEE?"good":"crit")+'">'+(cp<=FIN_FEE?"עד ":"מעל ")+ils(FIN_FEE)+'</span>')+'</td></tr>'});
 table($("finAff"),["משווק","תקציב יומי","הוצאה בתקופה","הוצאה מצטברת","מהתקציב","כניסות","הגיעו לסליקה","רכישות קורס","הכנסה 297","הכנסה 97","עמלה ממתינה","עמלה לתשלום","עמלה ששולמה","הוחזרו","יתרה לתשלום","תשלום הבא","עלות לרכישה (מול 220 ₪)"],rowsA,"אין משווקים פעילים ברשימה");
 /* --- התראות --- */
 const al=[];
 codes.forEach(code=>{const late=AI.filter(x=>finCode(x)===code&&affState(x)==="due"&&now-finDueSince(x)>FIN_DUE_DAYS*864e5);if(late.length){const old=Math.floor((now-Math.min(...late.map(finDueSince)))/864e5);
  al.push(['crit','עמלה ב"לתשלום" יותר מ-'+FIN_DUE_DAYS+' ימים',esc((AFF[code]||{}).name||code)+': '+late.length+' עמלות, '+ils(late.reduce((s,x)=>s+finFee(x),0))+', הוותיקה - '+old+' ימים'])}});
 const first=Object.keys(spend).sort()[0];if(first){const miss=[];const yday=new Date(B.sod.getFullYear(),B.sod.getMonth(),B.sod.getDate()-1),f0=new Date(first+"T00:00"),st0=finPer==="today"?yday:new Date(Math.max(+B.a,+f0));for(let d=new Date(st0.getFullYear(),st0.getMonth(),st0.getDate());d<B.sod;d.setDate(d.getDate()+1)){if(d<f0)continue;if(spend[dayKey(d)]==null)miss.push(dayKey(d))}
  if(miss.length)al.push(['warn','יום בלי הזנת הוצאה לחשבון שלנו',miss.slice(-10).map(k=>k.slice(8,10)+"."+k.slice(5,7)).join(", ")+(miss.length>10?" (ועוד "+(miss.length-10)+")":"")])}
 else al.push(['warn','יום בלי הזנת הוצאה לחשבון שלנו','לא נטענה הוצאה בכלל']);
 const noBud=[];codes.forEach(code=>{const inf=AFF[code];if(!inf||!inf.budget){noBud.push(code);return}const over={};for(const k in cspend){const [d,c]=k.split("|");if(c!=="aff_"+code&&c!=="aff_"+code+"_ic")continue;const dt=new Date(d+"T12:00");if(dt<B.a||dt>=B.b)continue;over[d]=(over[d]||0)+cspend[k]}
  const bad=Object.keys(over).filter(d=>over[d]>inf.budget*FIN_OVER).sort();if(bad.length)al.push(['crit','הוצאה מעל '+Math.round(FIN_OVER*100)+'% מהתקציב',esc(inf.name)+': '+bad.map(d=>d.slice(8,10)+"."+d.slice(5,7)+" "+ils(over[d])).join(", ")+' (תקציב '+ils(inf.budget)+')'])});
 if(noBud.length)al.push(['','בדיקת '+Math.round(FIN_OVER*100)+'% מהתקציב לא פעילה','חסר תקציב יומי ל-'+noBud.length+' משווקים (שדה budget ב-Make, אחרי "מאשר ב84")']);
 $("finAlerts").innerHTML=al.map(a=>'<div class="banner '+a[0]+'"><b>'+a[1]+'</b><span>'+a[2]+'</span></div>').join("")||'<div class="banner">אין התראות</div>';
 /* --- פירוט למשווק --- */
 const sel=$("finAffSel");if(!codes.includes(finAff))finAff=codes.find(c=>AI.some(x=>finCode(x)===c))||codes[0]||""; /* ברירת מחדל: המשווק הראשון שיש לו רכישות */const opts=codes.map(c=>'<option value="'+esc(c)+'"'+(c===finAff?" selected":"")+'>'+esc((AFF[c]||{}).name||c)+'</option>').join("");if(sel.innerHTML!==opts)sel.innerHTML=opts;
 const D=PI.filter(x=>finCode(x)===finAff).sort((x,y)=>x.t-y.t),stTxt=x=>{const st=affState(x),pa=PAIDAT[x.deal];return LAB[st]+(st==="pending"?" · לתשלום מ-"+finDate(new Date(finDueSince(x))):"")+(st==="paid"?" · "+(pa&&pa.at?finDate(pa.at):"תאריך חסר")+" · אסמכתא "+(pa&&pa.ref?pa.ref:"חסר נתון"):"")};
 table($("finDet"),["תאריך","מוצר","עסקה","עמלה","סטטוס"],D.map(x=>'<tr><td>'+finDate(x.t)+'</td><td>'+(x.up?"אפסייל 97 ₪":"קורס 297 ₪")+(x.bank?" <small>העברה בנקאית</small>":"")+'</td><td class="num">'+esc(finMask(x))+'</td><td>'+(live(x)?ils(finFee(x)):'<s>'+ils(finFee(x))+'</s>')+'</td><td><span class="pill '+PILL[affState(x)]+'">'+esc(stTxt(x))+'</span></td></tr>'),"אין רכישות למשווק הזה בתקופה");
 const tot={pending:sum(D,"pending"),due:sum(D,"due"),paid:sum(D,"paid")};
 $("finDetNote").textContent=D.length?"סה\"כ בתקופה: ממתינה "+ils(tot.pending)+" · לתשלום "+ils(tot.due)+" · שולמה "+ils(tot.paid)+". תשלום הבא: יום ראשון "+finDate(nextPay)+".":"";
 $("finCopy").onclick=()=>{const name=(AFF[finAff]||{}).name||finAff,txt=["פירוט עמלות - "+name+" ("+$("finUsNote").textContent+")","תאריך\tמוצר\tעסקה\tעמלה\tסטטוס"].concat(D.map(x=>[finDate(x.t),x.up?"אפסייל 97 ₪":"קורס 297 ₪",finMask(x),live(x)?Math.round(finFee(x))+" ₪":"0 ₪",stTxt(x)].join("\t"))).concat([$("finDetNote").textContent]).join("\n");
  const done=()=>{$("finCopy").textContent="הועתק";setTimeout(()=>$("finCopy").textContent="העתקה",1500)};
  try{navigator.clipboard.writeText(txt).then(done,()=>{window.prompt("להעתקה:",txt)})}catch(e){window.prompt("להעתקה:",txt)}};
 $("finNote").textContent="קריאה בלבד. עמלה: "+FIN_FEE+" ₪ לרכישת קורס (או הסכום ברשימת המשווקים), "+FIN_UP_FEE+" ₪ לאפסייל. ממתינה "+PAY_DAYS+" ימים מהרכישה ואז לתשלום; החזר מבטל. תשלום למשווקים ביום ראשון. סימון \"שולם\" או החזר: לבקש מהצ'אט הראשי (Make). "+(codes.some(c=>AFF[c]&&AFF[c].budget)?"":"תקציב יומי: חסר נתון עד שיתווסף השדה ב-Make. ")+(FIN_PROC_RATE==null?"עמלות סליקה: חסר נתון עד שבן ימסור את השיעור.":"");
}
/* ================= 🧪 lab (ב43) ================= */'''
rep('''/* ================= 🧪 lab (ב43) ================= */''', JS)

# 7. בורר התקופה ובחירת משווק
rep('''$("showTests").onchange=e=>{showTests=e.target.checked;render()};''',
    '''$("showTests").onchange=e=>{showTests=e.target.checked;render()};document.querySelectorAll("#finPer button").forEach(x=>x.onclick=()=>{finPer=x.dataset.p;render()});$("finAffSel").onchange=e=>{finAff=e.target.value;render()};''')

open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
