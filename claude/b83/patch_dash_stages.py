# ב83 (בן: "שימדוד את המעברים בדף הזה... שהם יותר גדולים מהדף שקיים עכשיו"): בלשונית 06 (מעבדת ניסויים) - פאנל "מעברים בין שלבים".
# לכל דף: אחוז האנשים שהגיעו לכל אחד מ-13 השלבים (section_view), המעבר משלב לשלב, ובנוסף מעבר מסך ראשון, הגעה להצעה והגעה לסליקה לאדם.
# מחושב ישירות מהשורות (לא דרך build), כך שדפי הבדיקה a5v4/a5v5 נכנסים בלי לשנות את רשימת הגרסאות של שאר הלשוניות.
# שימוש: python3 patch_dash_stages.py <dashboard.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)


rep('''    <div class="panel"><div class="panel-h"><h2>היסטוריית ניסויים ושינויים</h2></div><div class="tw"><table id="exLog"></table></div></div>''',
    '''    <div class="panel"><div class="panel-h"><h2>מעברים בין שלבים</h2><span class="note" id="stNote"></span></div>
      <div class="tw"><table id="stTop"></table></div>
      <div class="tw" style="margin-top:12px"><table id="stTable"></table></div>
      <p class="note">אנשים = מזהה מבקר ייחודי. שלב נספר כשתחילתו נכנסה למסך (section_view, פעם אחת לביקור). "מהשלב הקודם" = לפי הסדר בדף עצמו. מעבר מסך ראשון = הגיעו לסקשן 2. הגעה להצעה = הגיעו לסקשן "ההצעה". הגעה לסליקה = נפתח דף התשלום.</p></div>
    <div class="panel"><div class="panel-h"><h2>היסטוריית ניסויים ושינויים</h2></div><div class="tw"><table id="exLog"></table></div></div>''')

rep('''ex:()=>renderExperiments(M)''', '''ex:()=>{renderExperiments(M);renderStages(B)}''')

JS = r'''/* ================= ב83: מעברים בין שלבים (section_view) ================= */
const STAGES=[["hook","הוק"],["pain","כאב"],["cause","הסיבה האמיתית"],["old","למה מה שניסה לא עבד"],["solution","הפתרון"],["method","למה השיטה שלנו"],["result","התוצאה"],["proof","הוכחות"],["course","הקורס"],["offer","ההצעה"],["objections","התנגדויות"],["guarantee","אחריות"],["close","סגירה"]],
 STAGE_PAGES=["a5","pr2","a5v4","a5v5"],STAGE_LBL={a5:"a5 (חי)",pr2:"pr2 (חי)",a5v4:"a5v4 (בדיקה)",a5v5:"a5v5 (בדיקה)"};
function renderStages(B){
 const R=rows.filter(r=>!isNaN(r.t)&&r.t>=B.a&&r.t<B.b&&(showTests||!isTest(r))&&STAGE_PAGES.includes(r.variant)),pid=r=>r.vid||r.sid;
 const P={};STAGE_PAGES.forEach(v=>P[v]={ppl:new Set(),sec2:new Set(),off:new Set(),chk:new Set(),st:{},pos:{},offIdx:0,maxs:{}});
 R.forEach(r=>{const x=P[r.variant],id=pid(r);if(!id)return;
  if(r.ev==="view")x.ppl.add(id);
  if(r.ev==="section"&&/^ההצעה$/.test(r.name||"")&&+r.section)x.offIdx=+r.section;
  x.maxs[id]=Math.max(x.maxs[id]||0,+r.max_section||0);
  if(/^checkout_/.test(r.ev))x.chk.add(id);
  if(r.ev==="section_view"&&r.name){(x.st[r.name]=x.st[r.name]||new Set()).add(id);(x.pos[r.name]=x.pos[r.name]||[]).push(+r.section||0)}});
 const live=STAGE_PAGES.filter(v=>P[v].ppl.size);
 live.forEach(v=>{const x=P[v];for(const id in x.maxs){if(!x.ppl.has(id))continue;if(x.maxs[id]>=2)x.sec2.add(id);if(x.offIdx&&x.maxs[id]>=x.offIdx)x.off.add(id)}});
 const c=(k,n)=>'<td>'+(n?pf(pct(k,n)):'<span class="na">-</span>')+'<small>'+fmt(k)+'/'+fmt(n)+'</small></td>';
 table($("stTop"),["דף","אנשים","מעבר מסך ראשון","הגעה להצעה","הגעה לסליקה"],live.map(v=>{const x=P[v],n=x.ppl.size;return '<tr><td><b>'+esc(STAGE_LBL[v])+'</b></td><td class="num">'+fmt(n)+'</td>'+c(x.sec2.size,n)+(x.offIdx?c(x.off.size,n):'<td><span class="na">-</span></td>')+c(x.chk.size,n)+'</tr>'}),"אין כניסות בתקופה");
 const tagged=live.filter(v=>Object.keys(P[v].st).length);
 const ord=v=>{const x=P[v],med=a=>{const s=a.slice().sort((p,q)=>p-q);return s[Math.floor(s.length/2)]};return STAGES.map(s=>s[0]).filter(k=>x.st[k]).sort((p,q)=>med(x.pos[p])-med(x.pos[q]))};
 const body=STAGES.map(([k,l])=>'<tr><td><b>'+esc(l)+'</b> <small>'+k+'</small></td>'+tagged.map(v=>{const x=P[v],n=x.ppl.size,o=ord(v),i=o.indexOf(k),prev=i>0?x.st[o[i-1]].size:null,got=x.st[k]?x.st[k].size:0;
  return x.st[k]?'<td>'+pf(pct(got,n))+'<small>'+fmt(got)+(prev!=null?' · '+pf(pct(got,prev))+' מהשלב הקודם':'')+'</small></td>':'<td><span class="na">-</span></td>'}).join("")+'</tr>');
 table($("stTable"),["שלב"].concat(tagged.map(v=>STAGE_LBL[v]+' <small>('+fmt(P[v].ppl.size)+' אנשים)</small>')),tagged.length?body:[],"עוד אין נתוני שלבים. a5v4 ו-a5v5 מסומנים כבדיקה (int=1) - מוצגים רק עם \"כולל בדיקות\"");
 $("stNote").textContent=showTests?"כולל בדיקות":"בלי בדיקות (דפי הבדיקה int=1 לא נספרים)";
}
/* ================= 00 optimization (Ben's doc, section 10) ================= */'''
rep('''/* ================= 00 optimization (Ben's doc, section 10) ================= */''', JS)
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
