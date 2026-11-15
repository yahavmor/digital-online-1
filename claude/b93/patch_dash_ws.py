# ב93 ("מאשר ב93" מיהב, 15.11): לשונית 13 "מה מוכר" בדשבורד - אותה לוגיקה כמו whatsells.py. קריאה בלבד (ב30).
# שימוש: python3 patch_dash_ws.py <dashboard.html> <out> "<YYYY-MM-DD>" "<HH:MM>"
import sys
src, out, day, hm = sys.argv[1:5]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old)); s = s.replace(old, new, 1)
rep('''body[data-scr="up"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}''',
    '''body[data-scr="up"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}
body[data-scr="ws"] :is(#range,#customBox,#fSrc,#fOwn,#fDev){display:none!important}
#wsAd td,#wsAd th,#wsCamp td,#wsCamp th,#wsAff td,#wsAff th{white-space:nowrap}''')
rep('''    <button role="tab" data-s="up"><b>12</b>אפסייל</button>''', '''    <button role="tab" data-s="up"><b>12</b>אפסייל</button>
    <button role="tab" data-s="ws"><b>13</b>מה מוכר</button>''')
rep('''  <!-- 10 (ב71): השוואת קהלים - P25.''', '''  <!-- 13 (ב93): מה מוכר - לפי מודעה, קמפיין ומשווק. קריאה בלבד -->
  <section class="screen" id="s-ws">
    <div class="panel"><div class="panel-h"><h2>מה מוכר</h2>
      <div class="seg" role="group" aria-label="תקופה" id="wsPer"><button data-p="7">7 ימים</button><button data-p="2010">מ-20.10</button></div></div>
      <p class="note" id="wsNote"></p></div>
    <div class="panel"><div class="panel-h"><h2>התנועה של בן - לפי מודעה</h2><span class="note" id="wsAdN"></span></div><div class="tw"><table id="wsAd"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>התנועה של בן - לפי קמפיין</h2><span class="note">ההוצאה במאגר נשמרת לפי מודעה, לא לפי קמפיין</span></div><div class="tw"><table id="wsCamp"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>משווקים</h2><span class="note">לפי aff. ההוצאה: ביום עם מודעה שהקוד שלו בשם (p25_yosef) - המודעות; אחרת aff_קוד</span></div><div class="tw"><table id="wsAff"></table></div></div>
  </section>

  <!-- 10 (ב71): השוואת קהלים - P25.''')
rep('''/* ================= 🧪 lab (ב43) ================= */''', r'''/* ================= 13 מה מוכר (ב93) ================= */
/* כמו claude/b93/whatsells.py: שיוך לפי הכניסה הראשונה של ה-sid, לפי אנשים. ליד = השאירו פרטים (checkout_details). רכישה = מאומתת.
   עלות רק כשההוצאה של המודעה מכסה את כל הטווח, אחרת "חלקי". לטווח מ-20.10 סכומים כוללים (ראשי 15.11) */
let wsPer="7";
const WS_OVR={p25:[1780,"2026-11-14","סה\"כ P25 בפיילוט עד 14.11"],p24:[838.73+27.09,"2026-11-14","סה\"כ P24v2 + מעבדה"],t9_motivation_b:[101.51,"2026-11-10","סה\"כ עד 10.11"]};
const WS_AUD_FIX={w1_trust_b:"חם",car4_warm_a:"חם"},WS_AFF_AUD={amir:"חם"},WS_ORG=["(בלי קמפיין)","launch_oct","manychat","guide"],WS_P24T=new Date("2026-11-15T00:00:00"),WS_P24L="p24 (בדיקות P24, מ-15.11)";
function wsAud(camp,ad,aff){if(WS_AFF_AUD[aff])return WS_AFF_AUD[aff];if(WS_AUD_FIX[ad])return WS_AUD_FIX[ad];const v=((typeof ADS!=="undefined"&&ADS[ad])||{}).aud||"";
 if(v==="חם")return "חם";if(v==="קר"||v==="קר (מעבדה)")return "קר";const c=camp.toLowerCase();if(c.includes("warm"))return "חם";if(/cold|lab|(^|[\/ _])ic([\/ _]|$)/.test(c))return "קר";
 if(v.includes("חם")&&!v.includes("קר"))return "חם";if(v.includes("קר")&&!v.includes("חם"))return "קר";return "לא ידוע"}
function renderWs(){
 document.querySelectorAll("#wsPer button").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.p===wsPer)));
 const now=new Date(),A=wsPer==="7"?new Date(+now-7*864e5):new Date("2026-10-20T00:00:00"),useOvr=wsPer!=="7";
 const keep=[fSrc,fDev,fOwn];fSrc="";fDev="";fOwn="";let M;try{M=build(new Date(0),new Date(+now+864e5))}finally{[fSrc,fDev,fOwn]=keep}
 const vb=new Set(M.allBuys.filter(b=>b.sid).map(b=>b.sid));
 /* כמו whatsells.py: utm_campaign=x = בדיקה, ומבקר (vid) שהיה לו ביקור בדיקה כלשהו לא נספר */
 const TV=new Set(rows.filter(r=>r.vid&&r.ev!=="purchase"&&isTest(r)).map(r=>r.vid));
 const SS=M.sess.filter(s=>!(s.vid&&TV.has(s.vid))&&!(s.p&&s.p.get("utm_campaign")==="x")).map(s=>{const p=s.p||new URLSearchParams(),camp=(p.get("utm_campaign")||"(בלי קמפיין)").replace(/\|/g,"/");let ad=(p.get("utm_content")||"(בלי מודעה)").toLowerCase();if(ad==="p24"&&s.t>=WS_P24T)ad=WS_P24L;
  return {t:s.t,who:s.vid||s.sid,camp,ad,aff:(p.get("aff")||s.aff||"").toLowerCase(),chk:!!s.chk,start:!!(s.cstart||s.det),lead:!!s.det,buy:vb.has(s.sid)}});
 const E=SS.filter(s=>s.t>=A&&s.t<now),AFFS=[...new Set(SS.map(s=>s.aff).filter(a=>a.length>2).concat(Object.keys(AFF||{})))];
 const agg=L=>{const P={};L.forEach(s=>{const o=P[s.who]||(P[s.who]=[1,0,0,0,0]);o[1]|=s.chk;o[2]|=s.start;o[3]|=s.lead;o[4]|=s.buy});const v=Object.values(P);return [0,1,2,3,4].map(i=>v.reduce((x,o)=>x+o[i],0))};
 /* הוצאה */
 const SP={};const add=(d,k,v)=>{if(k==="p24"&&d>="2026-11-15")k=WS_P24L;SP[d+"|"+k]=(SP[d+"|"+k]||0)+v};
 for(const d in spend)add(d,"",+spend[d]);for(const k in cspend){const i=k.indexOf("|");add(k.slice(0,i),k.slice(i+1).trim().toLowerCase(),+cspend[k])}
 const d0=dayKey(A),d1=dayKey(now),D=[...new Set(Object.keys(SP).map(k=>k.split("|")[0]))].filter(d=>d>=d0&&d<=d1).sort();
 const isAffKey=k=>k.startsWith("aff_")||AFFS.some(f=>k.includes(f)),keysOn=d=>Object.keys(SP).filter(k=>k.startsWith(d+"|")).map(k=>k.slice(11)).filter(Boolean);
 const tot=d=>SP[d+"|"]!=null?SP[d+"|"]:null,unal=d=>{const t=tot(d);if(t==null)return 0;return Math.max(0,t-keysOn(d).filter(k=>!isAffKey(k)).reduce((x,k)=>x+SP[d+"|"+k],0))};
 const itemized=d=>{const t=tot(d);return t==null||unal(d)<=Math.max(5,.03*t)};
 const adSpend=(ad,L)=>{const vis=new Set(L.map(s=>dayKey(s.t)));let sp=0,nd=0,full=true,cut=null;if(useOvr&&WS_OVR[ad]){sp=WS_OVR[ad][0];cut=WS_OVR[ad][1]}
  D.forEach(d=>{if(cut&&d<=cut)return;const k=d+"|"+ad;if(SP[k]!=null){sp+=SP[k];if(SP[k]>0)nd++;return}if(itemized(d)||!vis.has(d))return;full=false});return {sp,nd,full,cut}};
 const affDay=(d,f)=>{const ks=keysOn(d),ad=ks.filter(k=>k.includes(f)&&!k.startsWith("aff_"));if(ad.length)return ad.reduce((x,k)=>x+SP[d+"|"+k],0);return ks.filter(k=>k==="aff_"+f||k.startsWith("aff_"+f+"_")).reduce((x,k)=>x+SP[d+"|"+k],0)};
 const per=(sp,n,full)=>!full?'<span class="na">חלקי</span>':(!sp?"-":(!n?"אין":ils(sp/n)));
 const cells=n=>n.map(v=>'<td class="num">'+fmt(v)+'</td>').join("");
 const H=["קהל","הוצאה","אנשים","הגיעו לתשלום","התחילו למלא","לידים","רכישות","₪ לליד","₪ לרכישה"];
 /* בן לפי מודעה */
 const ben=E.filter(s=>!s.aff),G={};ben.forEach(s=>(G[s.ad]=G[s.ad]||[]).push(s));let alloc=0;const adRows=[];
 Object.keys(G).forEach(ad=>{const L=G[ad],r=adSpend(ad,L);if(L.every(s=>WS_ORG.includes(s.camp))&&!r.sp)r.full=true;alloc+=r.sp;const n=agg(L),cc={};L.forEach(s=>cc[s.camp]=(cc[s.camp]||0)+1);
  const au=[...new Set(L.map(s=>wsAud(s.camp,ad,"")))].sort().join("/"),spt=r.sp?ils(r.sp)+(r.cut?' <small>('+WS_OVR[ad][2]+(r.nd?" + "+r.nd+" ימים":"")+')</small>':(r.nd?' <small>'+r.nd+' ימים</small>':"")):"-";
  adRows.push({n,sp:r.sp,au,full:r.full,html:'<tr><td><b>'+esc(ad)+'</b> <small>'+esc(Object.entries(cc).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([c,v])=>c+": "+v).join(", "))+'</small></td><td>'+au+'</td><td>'+spt+(r.full?"":' <small class="na">חלקי</small>')+'</td>'+cells(n)+'<td>'+per(r.sp,n[3],r.full)+'</td><td>'+per(r.sp,n[4],r.full)+'</td></tr>'})});
 [...new Set(D.flatMap(d=>keysOn(d).filter(k=>!isAffKey(k))))].filter(k=>!G[k]).forEach(ad=>{const r=adSpend(ad,[]);alloc+=r.sp;if(r.sp)adRows.push({n:[0,0,0,0,0],sp:r.sp,au:wsAud("",ad,""),full:true,html:'<tr><td><b>'+esc(ad)+'</b> <small>בלי כניסות</small></td><td>'+wsAud("",ad,"")+'</td><td>'+ils(r.sp)+'</td>'+cells([0,0,0,0,0])+'<td>אין</td><td>אין</td></tr>'})});
 const big=adRows.filter(r=>r.n[0]>=10||r.n[1]>0||r.n[4]>0||r.sp>=20),small=adRows.filter(r=>!big.includes(r));big.sort((a,b)=>b.n[4]-a.n[4]||b.n[0]-a.n[0]);
 const out=big.map(r=>r.html);
 if(small.length){const sp=small.reduce((x,r)=>x+r.sp,0),n=[0,1,2,3,4].map(i=>small.reduce((x,r)=>x+r.n[i],0)),f=small.every(r=>r.full);out.push('<tr><td>שאר המודעות <small>'+small.length+' מודעות, כל אחת פחות מ-10 אנשים ובלי סליקה</small></td><td>'+[...new Set(small.map(r=>r.au))].sort().join("/")+'</td><td>'+(sp?ils(sp):"-")+(f?"":' <small class="na">חלקי</small>')+'</td>'+cells(n)+'<td>'+per(sp,n[3],f)+'</td><td>'+per(sp,n[4],f)+'</td></tr>')}
 const tb=D.reduce((x,d)=>x+(tot(d)||0),0),nofull=D.filter(d=>!itemized(d)),nb=agg(ben);
 out.push('<tr><td><b>הוצאה של בן שלא משויכת למודעה</b> <small>'+(nofull.length?"ימים בלי פירוט מלא: "+(nofull.length>8?nofull.length+" ימים":nofull.map(d=>d.slice(8,10)+"."+d.slice(5,7)).join(", ")):"")+'</small></td><td></td><td>'+ils(tb-alloc)+'</td><td colspan="7"></td></tr>');
 out.push('<tr><td><b>סה"כ בן</b></td><td></td><td><b>'+ils(tb)+'</b></td>'+cells(nb)+'<td>'+per(tb,nb[3],true)+'</td><td>'+per(tb,nb[4],true)+'</td></tr>');
 table($("wsAd"),["מודעה (קמפיינים: אנשים)"].concat(H),out,"אין כניסות בתקופה");
 /* בן לפי קמפיין */
 const cl=s=>s.camp==="lenatzeach_lab"?"lenatzeach_lab · "+wsAud(s.camp,s.ad,""):s.camp!=="lenatzeach_cold"?s.camp:"lenatzeach_cold · "+(s.ad==="p25"?"p25 (פיילוט)":s.ad===WS_P24L?WS_P24L:s.ad==="p24"?"p24 (עד 14.11)":"מודעות אחרות");
 const GC={};ben.forEach(s=>(GC[cl(s)]=GC[cl(s)]||[]).push(s));if(now>WS_P24T)GC["lenatzeach_cold · "+WS_P24L]=GC["lenatzeach_cold · "+WS_P24L]||[];
 table($("wsCamp"),["קמפיין","קהל","אנשים","הגיעו לתשלום","התחילו למלא","לידים","רכישות"],Object.entries(GC).map(([c,L])=>({c,L,n:L.length?agg(L):[0,0,0,0,0]})).sort((a,b)=>b.n[4]-a.n[4]||b.n[0]-a.n[0]).map(o=>'<tr><td>'+esc(o.c)+'</td><td>'+([...new Set(o.L.map(s=>wsAud(s.camp,s.ad,"")))].sort().join("/")||"קר")+'</td>'+cells(o.n)+'</tr>'),"אין כניסות בתקופה");
 /* משווקים */
 const af=E.filter(s=>s.aff),GA={};af.forEach(s=>(GA[s.aff]=GA[s.aff]||[]).push(s));D.forEach(d=>keysOn(d).filter(k=>k.startsWith("aff_")).forEach(k=>{const f=k.slice(4).split("_")[0];GA[f]=GA[f]||[]}));
 let spa=0;const ra=Object.entries(GA).map(([f,L])=>{const sp=D.reduce((x,d)=>x+affDay(d,f),0),nd=D.filter(d=>affDay(d,f)>0).length,n=L.length?agg(L):[0,0,0,0,0],cc=[...new Set(L.map(s=>s.camp))].slice(0,2).join(", ");spa+=sp;
  return {n,html:'<tr><td><b>'+esc((AFF[f]||{}).name||f)+'</b> <small>'+esc(cc)+'</small></td><td>'+([...new Set(L.map(s=>wsAud(s.camp,s.ad,f)))].sort().join("/")||"-")+'</td><td>'+(sp?ils(sp)+' <small>'+nd+' ימים</small>':"-")+'</td>'+cells(n)+'<td>'+per(sp,n[3],true)+'</td><td>'+per(sp,n[4],true)+'</td></tr>'}}).sort((a,b)=>b.n[4]-a.n[4]||b.n[0]-a.n[0]).map(o=>o.html);
 const na=agg(af);ra.push('<tr><td><b>סה"כ משווקים</b></td><td></td><td><b>'+ils(spa)+'</b></td>'+cells(na)+'<td>'+per(spa,na[3],true)+'</td><td>'+per(spa,na[4],true)+'</td></tr>');
 table($("wsAff"),["משווק"].concat(H),ra,"אין משווקים בתקופה");
 const ta=agg(E);$("wsNote").textContent=(wsPer==="7"?"7 הימים האחרונים":"מ-20.10")+": "+fmt(ta[0])+" אנשים, "+fmt(ta[1])+" הגיעו לתשלום, "+fmt(ta[2])+" התחילו למלא, "+fmt(ta[3])+" לידים, "+fmt(ta[4])+" רכישות. שיוך לפי הכניסה הראשונה של כל ביקור, לפי אנשים, בלי בדיקות וסריקות. ליד = השאירו פרטים בדף התשלום. ₪ לליד ולרכישה רק כשההוצאה של המודעה מכסה את כל התקופה (אחרת \"חלקי\")"+(useOvr?". מ-20.10: p25, p24 ו-t9_motivation_b לפי הסכומים הכוללים מהראשי (15.11)":"")+". קהל: לפי מילון המודעות ושם הקמפיין; w1_trust_b, car4_warm_a ואמיר - חם.";
 $("wsAdN").textContent="p24 מ-15.11 = קמפיין הבדיקות של P24 (שורה נפרדת)";
}
/* ================= 🧪 lab (ב43) ================= */''')
rep('''up:()=>renderUpsell()})[screen]()''', '''up:()=>renderUpsell(),ws:()=>renderWs()})[screen]()''')
rep('''document.querySelectorAll("#finPer button").forEach(x=>x.onclick=()=>{finPer=x.dataset.p;render()});''', '''document.querySelectorAll("#finPer button").forEach(x=>x.onclick=()=>{finPer=x.dataset.p;render()});document.querySelectorAll("#wsPer button").forEach(x=>x.onclick=()=>{wsPer=x.dataset.p;render()});''')
rep('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב93 (\\"מאשר ב93\\" מיהב): לשונית 13 \\"מה מוכר\\" (קריאה בלבד) - 7 ימים / מ-20.10: לפי מודעה, לפי קמפיין (lenatzeach_cold לפי מודעה, lenatzeach_lab לפי חם/קר) ולפי משווק - קהל, הוצאה, אנשים, הגיעו לתשלום, התחילו למלא, לידים, רכישות, ₪ לליד ולרכישה (רק בכיסוי מלא, אחרת \\"חלקי\\"). אותה לוגיקה כמו claude/b93/whatsells.py."],
''' % (day, hm))
open(out, "w", encoding="utf8").write(s); print("ok", len(s))
