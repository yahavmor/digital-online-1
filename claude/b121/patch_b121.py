# ב121 (24.11): (1) נרמול קוד משווק בקריאה - "affX" ו-"aff_X" נחשבים X (שרשרת הקופה שמרה aff=affyehudit ברכישה ובאפסייל);
# (2) תמונת מצב: אריח אפסייל, הכנסות ו-ROAS כולל אפסייל עם פירוט קורס / אפסייל; (3) אזור המשווקים: אפסייל 72 ₪ לצד הקורס 220 ₪.
# שימוש: python3 patch_b121.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os, hashlib
root, day, hm = sys.argv[1:4]
H = lambda s: hashlib.sha256(s.encode()).hexdigest()[:16]
def patch(f, reps, want=None):
    p = os.path.join(root, f); s = open(p, encoding="utf-8").read(); h0 = H(s)
    if want: assert h0 == want, (f, "changed since ב121 was prepared:", h0)
    for a, b, *o in reps:
        assert s.count(a) == (o[0] if o else 1), (f, a[:70], s.count(a)); s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s); print(f, h0, "->", H(s))
LOG = '["%s","%s - ב121 (\\"מאשר\\" מיהב): קוד משווק נקי בקריאה - affX ו-aff_X נחשבים X (רכישת 23.11 נשמרה כ-affyehudit). תמונת מצב: אריח אפסייל, הכנסות ו-ROAS כולל אפסייל עם פירוט קורס / אפסייל. אזור המשווקים: אפסייל 72 ₪ לצד 220 ₪ לקורס."],\n' % (day, hm)

# ---- dashboard.html
D = [
 ('function parseX(x){const o={};(x||"").split(";").forEach(kv=>{const i=kv.indexOf("=");if(i>0)o[kv.slice(0,i)]=kv.slice(i+1)});return o}',
  'const normAff=c=>{c=String(c||"").trim().toLowerCase();const m=c.match(/^aff_?([a-z0-9][a-z0-9_-]*)$/);return m?m[1]:c}; /* ב121: קוד משווק נקי - "affX" ו-"aff_X" נחשבים X (שרשרת הקופה שמרה aff=affyehudit) */\n'
  'function parseX(x){const o={};(x||"").split(";").forEach(kv=>{const i=kv.indexOf("=");if(i>0){const k=kv.slice(0,i),v=kv.slice(i+1);o[k]=k==="aff"?normAff(v):v}});return o}'),
 ('aff:parseX(r.x).aff||(bank&&((r.qs||"").match(/aff\\s+([a-z0-9_-]+)/)||[])[1])||"",bank});});',
  'aff:parseX(r.x).aff||normAff(bank&&((r.qs||"").match(/aff\\s+([a-z0-9_-]+)/)||[])[1])||"",bank});});'),
 ('const affOf=s=>(s.aff||(s.p&&s.p.get("aff"))||"").toLowerCase(),', 'const affOf=s=>normAff(s.aff||(s.p&&s.p.get("aff"))||""),', 2),
 ('aff:(o.aff||"").toLowerCase(),deal:o.deal||"",up:o.up_deal||"",', 'aff:normAff(o.aff),deal:o.deal||"",up:o.up_deal||"",'),
 ('aff:(p.get("aff")||s.aff||"").toLowerCase(),chk:!!s.chk,', 'aff:normAff(p.get("aff")||s.aff||""),chk:!!s.chk,'),
 # תמונת מצב
 (''' const sp=spendIn(B.a,B.b),ours=buys.filter(b=>!b.aff),rev=buys.reduce((x,b)=>x+b.amt,0),ourRev=ours.reduce((x,b)=>x+b.amt,0),cpa=sp!=null&&ours.length?sp/ours.length:null;
 $("snapKpi").innerHTML=[''',
  ''' const sp=spendIn(B.a,B.b),ours=buys.filter(b=>!b.aff),rev=buys.reduce((x,b)=>x+b.amt,0),ourRev=ours.reduce((x,b)=>x+b.amt,0),cpa=sp!=null&&ours.length?sp/ours.length:null;
 /* ב121: אפסייל (97 ₪, cardcom_upsell_webhook) בתמונת המצב - בלי ביקורים פנימיים (לפי הסשן של רכישת הקורס). ההכנסות וה-ROAS כוללים אותו, עם פירוט */
 const sidS=new Map(M.sess.map(s=>[s.sid,s])),ups=finUps(M).filter(u=>{const s=u.sid&&sidS.get(u.sid);return !(s&&internal(s))}),upRev=ups.reduce((x,u)=>x+u.amt,0),ourUp=ups.filter(u=>!u.aff).reduce((x,u)=>x+u.amt,0),allRev=rev+upRev,allOur=ourRev+ourUp;
 $("snapKpi").innerHTML=['''),
 ('''  tile("הכנסות",ils(rev),"מרכישות מאומתות, כולל מע\\"מ",""),''',
  '''  tile("הכנסות",ils(allRev),"קורס "+ils(rev)+" · אפסייל "+ils(upRev)+" · מאומתות, כולל מע\\"מ",""),'''),
 ('''  tile("עלות לרכישה",cpa==null?na:ils(cpa),cpa==null?(sp?"אין עדיין רכישות מהמודעות של בן":""):''',
  '''  tile("אפסייל",fmt(ups.length),ups.length?ils(upRev)+" · "+pf(pct(ups.length,buys.length))+" מהרוכשים":"אין עדיין רכישות אפסייל בתקופה","97 ₪ אחרי רכישת הקורס, מאומת"),
  tile("עלות לרכישה",cpa==null?na:ils(cpa),cpa==null?(sp?"אין עדיין רכישות מהמודעות של בן":""):'''),
 ('''  tile("ROAS",sp?(ourRev/sp).toFixed(2):na,sp?"כל 1 ₪ על מודעות החזיר "+(ourRev/sp).toFixed(2)+" ₪":"","הכנסה שלא דרך משווק ÷ הוצאה")].join("");''',
  '''  tile("ROAS",sp?(allOur/sp).toFixed(2):na,sp?"קורס "+(ourRev/sp).toFixed(2)+" · עם אפסייל "+(allOur/sp).toFixed(2)+" · כל 1 ₪ על מודעות החזיר "+(allOur/sp).toFixed(2)+" ₪":"","הכנסה שלא דרך משווק (קורס + אפסייל) ÷ הוצאה")].join("");'''),
 ('$("snapNote").textContent="רק רכישות מאומתות (כרטיס והעברה בנקאית). ', '$("snapNote").textContent="רק רכישות מאומתות (כרטיס והעברה בנקאית), והאפסייל (97 ₪) רק כשקארדקום אישרה אותו. '),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n' + LOG),
]
patch("nlp/dashboard.html", D, want="2217db0da4dd74bf")
patch("nlp/campaign.html", [('const CHANGELOG=[\n', 'const CHANGELOG=[\n' + LOG)], want="baddff8fd63d20ba")

# ---- partner.html
P = [
 ('const PARTNER_API="https://hook.eu1.make.com/fyvfta25i5igncdufnq5wwkh17a2ubk5", PAY_DAYS=7;',
  'const PARTNER_API="https://hook.eu1.make.com/fyvfta25i5igncdufnq5wwkh17a2ubk5", PAY_DAYS=7, UP_FEE=72; /* ב121: עמלת אפסייל 97 ₪ - 72 ₪ קבוע */'),
 ('''  R.forEach(r=>{if(r.ev!=="purchase")return;const m=r.q.match(/deal\\s+(\\d+)/),rf=/bank_transfer/.test(r.q)&&r.q.match(/ref\\s+([^\\s|]+)/),a=r.q.match(/(\\d+(?:\\.\\d+)?)\\s*ILS/),deal=m?m[1]:rf?"bank_"+rf[1]:""; /* ב64: העברה בנקאית - מפתח bank_אסמכתא, כמו בדשבורד */const k=deal||r.sid;if(seen.has(k))return;seen.add(k);
    const st=D.refunds.has(deal)?"refund":D.paid.has(deal)?"paid":(now-r.t<PAY_DAYS*864e5?"pending":"due");buys.push({t:r.t,sid:r.sid,deal,amt:a?+a[1]:297,st,fee:fee(a?+a[1]:297)})});''',
  '''  R.forEach(r=>{const up=r.ev==="upsell_purchase";if(r.ev!=="purchase"&&!up)return; /* ב121: גם אפסייל (97 ₪) - "deal" של האפסייל ולא course_deal */
    const m=r.q.match(/(?:^|[^_a-z])deal\\s+(\\d+)/),rf=/bank_transfer/.test(r.q)&&r.q.match(/ref\\s+([^\\s|]+)/),a=r.q.match(/(\\d+(?:\\.\\d+)?)\\s*ILS/),deal=m?m[1]:rf?"bank_"+rf[1]:""; /* ב64: העברה בנקאית - מפתח bank_אסמכתא, כמו בדשבורד */const k=(up?"up_":"")+(deal||r.sid);if(seen.has(k))return;seen.add(k);
    const amt=a?+a[1]:(up?97:297),st=D.refunds.has(deal)?"refund":D.paid.has(deal)?"paid":(now-r.t<PAY_DAYS*864e5?"pending":"due");buys.push({t:r.t,sid:r.sid,deal,amt,st,up,fee:up?UP_FEE:fee(amt)})});'''),
 ('''["רכישות",fmt(B.filter(b=>b.st!=="refund").length)],''',
  '''["רכישות קורס",fmt(B.filter(b=>!b.up&&b.st!=="refund").length)],["אפסיילים",fmt(B.filter(b=>b.up&&b.st!=="refund").length)],'''),
 ('''$("feeNote").textContent="עמלה: "+(D.me.fee>0?ils(D.me.fee)+" לכל רכישה":D.me.pct+"% מכל רכישה")+". הביקורים''',
  '''$("feeNote").textContent="עמלה: "+(D.me.fee>0?ils(D.me.fee)+" לרכישת קורס":D.me.pct+"% מרכישת קורס")+" + "+ils(UP_FEE)+" לאפסייל (97 ₪). הביקורים'''),
 ('''  const byS=new Map(buys.map(b=>[b.sid,b])),rowsL=D.leads.filter(l=>inR(l.t)).map(l=>({t:l.t,nm:l.nm,ph:l.ph,b:byS.get(l.sid)||null}));
  const leadS=new Set(D.leads.map(l=>l.sid));B.filter(b=>!leadS.has(b.sid)).forEach(b=>rowsL.push({t:b.t,nm:"",ph:"",b}));''',
  '''  const byS=new Map(buys.filter(b=>!b.up).map(b=>[b.sid,b])),byU=new Map(buys.filter(b=>b.up).map(b=>[b.sid,b])),rowsL=D.leads.filter(l=>inR(l.t)).map(l=>({t:l.t,nm:l.nm,ph:l.ph,b:byS.get(l.sid)||null,u:byU.get(l.sid)||null}));
  const leadS=new Set(D.leads.map(l=>l.sid));B.filter(b=>!b.up&&!leadS.has(b.sid)).forEach(b=>rowsL.push({t:b.t,nm:"",ph:"",b,u:byU.get(b.sid)||null}));'''),
 ('''+rowsL.map(x=>{const b=x.b;
    let s,c;''',
  '''+rowsL.map(x=>{const b=x.b,u=x.u,uc=u?'<div class="sub2">אפסייל 97 ₪: <span class="pill '+st[u.st][1]+'">'+st[u.st][0]+(u.st==="pending"?" עד "+day(new Date(+u.t+PAY_DAYS*864e5)):"")+'</span> '+(u.st==="refund"?"":ils(u.fee))+'</div>':""; /* ב121 */
    let s,c;'''),
 ('''+s+(b&&b.st!=="refund"?'<div class="sub2">'+c+'</div>':'')+'</td></tr>'}).join("")''',
  '''+s+(b&&b.st!=="refund"?'<div class="sub2">'+c+'</div>':'')+uc+'</td></tr>'}).join("")'''),
 ('<p class="note">העמלה משולמת 7 ימים אחרי הרכישה, ורק אם לא הייתה בקשת החזר.', '<p class="note">העמלה (220 ₪ לקורס, 72 ₪ לאפסייל) משולמת 7 ימים אחרי הרכישה, ורק אם לא הייתה בקשת החזר.'),
]
patch("nlp/partner.html", P)
