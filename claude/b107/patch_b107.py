# ב107 (ראשי 18.11, בקשת בן): בדשבורד, לשונית "תמונת מצב":
#  (1) "תנועה מיום ליום" - 14 ימים: מבקרים (המודעות של בן / משווקים / חינם), הגיעו לדף התשלום, השאירו פרטים, רכישות,
#      שורה אחת בשפה פשוטה (אתמול מול שלשום ומול ממוצע 7 ימים), וממוצע 7 ימים.
#  (2) מקורות חינם: utm_source=whatsapp -> "וואטסאפ (קבוצות)", utm_source=facebook עם utm_medium=page/page_post -> "דף הפייסבוק",
#      לצד אינסטגרם אורגני, מייל ו-ManyChat. טבלת פירוט של "חינם" לפי מקור.
# שימוש: python3 patch_b107.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
def patch(path, pairs):
    p = os.path.join(root, path); s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:80], s.count(a)); s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
JS = r'''/* ב107: תנועה מיום ליום (בקשת בן 18.11). יום = יום תחילת הביקור. אנשים = מכשירים (vid). בלי בדיקות פנימיות ובלי סריקות של Meta.
   "המודעות של בן" = מודעות Meta בלי משווק; "משווקים" = aff; "חינם" = כל השאר (פירוט לפי מקור בטבלה השנייה).
   הגיעו לדף התשלום = chk; השאירו פרטים = det/pay/buy (כמו המדד הראשי בניסוי); רכישות = מאומתות, לפי יום הרכישה. */
const D14_FREE=["אינסטגרם אורגני","וואטסאפ (קבוצות)","דף הפייסבוק","פייסבוק אורגני","מייל","ManyChat","Meta (fbclid)","ישיר / לא ידוע"];
function renderDaily14(){
 const n=new Date(),sod=new Date(n.getFullYear(),n.getMonth(),n.getDate()),a=new Date(+sod-13*864e5),b=new Date(+sod+864e5);
 const keep=[fSrc,fDev,fOwn,showTests];fSrc="";fDev="";fOwn="";showTests=false;let M;try{M=build(a,b)}finally{[fSrc,fDev,fOwn,showTests]=keep}
 const TV=snapTV(),internal=s=>TV.has(s.vid)||SNAP_TEST_VIDS.some(p=>(s.vid||"").indexOf(p)===0),who=s=>s.vid||s.sid;
 const grp=s=>s.aff?"aff":s.src==="מודעות Meta"?"ben":"free",dk=s=>dayKey(SNAP_FIRST.get(s.sid)||s.t);
 const S=M.sess.filter(s=>!internal(s)&&!(SNAP_FIRST.get(s.sid)<a)),days=[];for(let i=0;i<14;i++)days.push(dayKey(new Date(+sod-i*864e5)));
 const D={};days.forEach(d=>D[d]={ben:new Set,aff:new Set,free:new Set,all:new Set,chk:new Set,det:new Set,buy:0,fs:{}});
 S.forEach(s=>{const o=D[dk(s)];if(!o)return;const w=who(s);o[grp(s)].add(w);o.all.add(w);if(s.chk)o.chk.add(w);if(s.det||s.pay||s.buy)o.det.add(w);
  if(grp(s)==="free"){const k=D14_FREE.includes(s.src)?s.src:"אחר";(o.fs[k]=o.fs[k]||{p:new Set,c:new Set,d:new Set}).p.add(w);if(s.chk)o.fs[k].c.add(w);if(s.det||s.pay||s.buy)o.fs[k].d.add(w)}});
 M.buys.filter(x=>!(x.s&&internal(x.s))).forEach(x=>{const o=D[dayKey(x.t)];if(o)o.buy++});
 const V=d=>{const o=D[d];return {ben:o.ben.size,aff:o.aff.size,free:o.free.size,all:o.all.size,chk:o.chk.size,det:o.det.size,buy:o.buy}};
 const K=["ben","aff","free","all","chk","det","buy"],avg=ds=>{const r={};K.forEach(k=>r[k]=ds.reduce((x,d)=>x+V(d)[k],0)/ds.length);return r};
 const y=V(days[1]),y2=V(days[2]),a7=avg(days.slice(1,8)),f1=v=>Math.round(v*10)/10;
 const cmp=(v,ref)=>"אתמול נכנסו "+(!ref?(v?"יותר אנשים":"אותו מספר אנשים"):v/ref>=1.15?"יותר אנשים":v/ref<=0.85?"פחות אנשים":"בערך אותו מספר אנשים")+".";
 const dd=d=>d.split("-").reverse().slice(0,2).join(".");
 $("d14Line").innerHTML='<b>אתמול ('+dd(days[1])+'):</b> '+fmt(y.all)+' אנשים נכנסו לדף ('+fmt(y.ben)+' מהמודעות של בן, '+fmt(y.aff)+' דרך משווקים, '+fmt(y.free)+' בחינם), '+fmt(y.chk)+' הגיעו לדף התשלום, '+fmt(y.det)+' השאירו פרטים, '+fmt(y.buy)+' רכישות.'+
  '<br><b>שלשום:</b> '+fmt(y2.all)+' אנשים, '+fmt(y2.chk)+' לדף התשלום, '+fmt(y2.det)+' השאירו פרטים, '+fmt(y2.buy)+' רכישות. '+cmp(y.all,y2.all)+
  '<br><b>ממוצע 7 ימים:</b> '+f1(a7.all)+' אנשים ביום, '+f1(a7.chk)+' לדף התשלום, '+f1(a7.det)+' השאירו פרטים, '+f1(a7.buy)+' רכישות. '+cmp(y.all,a7.all);
 const row=(lab,v,cls)=>'<tr'+(cls?' class="'+cls+'"':'')+'><td>'+lab+'</td>'+K.map(k=>'<td class="num">'+(Number.isInteger(v[k])?fmt(v[k]):f1(v[k]))+'</td>').join("")+'</tr>';
 const body=days.map((d,i)=>row(dd(d)+(i===0?' <small>היום, עד עכשיו</small>':i===1?' <small>אתמול</small>':''),V(d),i===1?"d14y":"")).concat([row("<b>ממוצע 7 ימים</b> <small>אתמול ו-6 הימים שלפניו</small>",a7,"d14a")]);
 table($("d14T"),["יום","המודעות של בן","משווקים","חינם","סה\"כ אנשים","הגיעו לדף התשלום","השאירו פרטים","רכישות"],body,"אין נתונים");
 const FS={};days.forEach((d,i)=>{for(const k in D[d].fs){const o=D[d].fs[k],f=FS[k]=FS[k]||{y:new Set,w:new Set,m:new Set,c:new Set,d:new Set};if(i===1)o.p.forEach(x=>f.y.add(x));if(i>=1&&i<=7)o.p.forEach(x=>f.w.add(x));o.p.forEach(x=>f.m.add(x));o.c.forEach(x=>f.c.add(x));o.d.forEach(x=>f.d.add(x))}});
 const order=D14_FREE.concat(["אחר"]).filter(k=>FS[k]);
 table($("d14F"),["מקור","אתמול","7 ימים","14 ימים","הגיעו לדף התשלום (14 ימים)","השאירו פרטים (14 ימים)"],order.map(k=>{const f=FS[k];return '<tr><td>'+esc(k)+'</td><td class="num">'+fmt(f.y.size)+'</td><td class="num">'+fmt(f.w.size)+'</td><td class="num">'+fmt(f.m.size)+'</td><td class="num">'+fmt(f.c.size)+'</td><td class="num">'+fmt(f.d.size)+'</td></tr>'}),"אין כניסות חינם ב-14 הימים");
}
'''
PANEL = '''    <div class="panel" id="d14"><div class="panel-h"><h2>תנועה מיום ליום</h2><span class="note">14 ימים, לפי מכשיר. "חינם" = כל מה שלא מודעה של בן ולא משווק (פירוט למטה). בלי בדיקות פנימיות ובלי סריקות של Meta</span></div><p class="d14-line" id="d14Line"></p><div class="tw"><table id="d14T"></table></div>
      <h3 class="d14-h">מקורות חינם</h3><div class="tw"><table id="d14F"></table></div><p class="note">וואטסאפ = utm_source=whatsapp. דף הפייסבוק = utm_source=facebook עם utm_medium=page או page_post. Meta (fbclid) = הגיעו מפייסבוק או אינסטגרם בלי קוד מעקב, ואי אפשר לדעת אם ממודעה או לא</p></div>
'''
patch("nlp/dashboard.html", [
 (' if(/email|responder/.test(s+m))return "מייל";\n', ' if(/^(whatsapp|wa)$/.test(s))return "וואטסאפ (קבוצות)"; /* ב107: קבוצות הוואטסאפ של בן */\n if(/facebook|fb/.test(s)&&/^(page|page_post)$/.test(m))return "דף הפייסבוק"; /* ב107: פוסטים בדף הפייסבוק */\n if(/email|responder/.test(s+m))return "מייל";\n'),
 ('    <div class="tiles snap-tiles" id="snapKpi"></div>\n', '    <div class="tiles snap-tiles" id="snapKpi"></div>\n' + PANEL),
 ('#snapAds td,#snapAds th,', '#d14T td,#d14T th,#d14F td,#d14F th,#snapAds td,#snapAds th,'),
 ('function renderSnap(){', JS + 'function renderSnap(){'),
 ('snap:()=>renderSnap()', 'snap:()=>{renderSnap();renderDaily14()}'),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב107 (בקשת בן 18.11): בלשונית תמונת מצב - \\"תנועה מיום ליום\\": 14 ימים של מבקרים (המודעות של בן, משווקים, חינם), הגעה לדף התשלום, השארת פרטים ורכישות, שורה בשפה פשוטה (אתמול מול שלשום ומול ממוצע 7 ימים), וטבלת מקורות חינם. מקורות חדשים: וואטסאפ (utm_source=whatsapp) ודף הפייסבוק (utm_source=facebook עם utm_medium=page/page_post)."],\n' % (day, hm)),
])
p = os.path.join(root, "nlp/dashboard.html"); s = open(p, encoding="utf-8").read()
s = s.replace("</style>", ".d14-line{font-size:15px;line-height:1.75;margin:4px 0 12px}.d14-h{font-size:15px;margin:16px 0 6px}#d14T tr.d14y td{background:rgba(212,175,55,.08);font-weight:700}#d14T tr.d14a td{border-top:2px solid var(--line,#ddd)}\n</style>", 1)
open(p, "w", encoding="utf-8").write(s); print("ok")
