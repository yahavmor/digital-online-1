# ב94 (ראשי 15.11): ניסוי דפים pg_1611 - a5v6 מול pr2, חצי-חצי, קבוע לדפדפן. הכנה מקומית בלבד.
# פריסה רק אחרי שבן מאשר את דף הפרימיום (pr2) ויהב נותן "מאשר ב94". הדפים, דף התשלום וניסוי B מול B2 לא משתנים.
# שימוש: python3 patch_pg.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"   (שעת הפריסה; ההשוואה מתחילה 10 דקות אחריה, אחרי המטמון)
import sys, os
from datetime import datetime, timedelta
root, day, hm = sys.argv[1:4]
T0 = datetime.strptime(day + " " + hm, "%Y-%m-%d %H:%M"); ST = T0 + timedelta(minutes=10)
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
D = day[8:10] + "." + day[5:7]
# --- go.html ---
patch("nlp/go.html", [
 ('''  var EXP="a5v6_1511";
''', '''  /* ב94 ("מאשר ב94" מיהב, %s %s): ניסוי דפים pg_1611 - a5v6 מול pr2, חצי-חצי, קבוע לדפדפן, לכל התנועה שעוברת ב-go.html (כל המודעות והמשווקים).
     מי ששובץ ב-ap2_0811 נשאר בדף שלו (a5 = a5v6, pr2 = pr2), כדי שלא יראה דף אחר בחזרה; זה סימטרי בין שני הדפים. כל השאר מוגרלים.
     אינסטגרם אורגני ממשיך ל-a (ב44). הדפים, דף התשלום וניסוי B מול B2 לא משתנים */
  var EXP="pg_1611", K="nlp_go_"+EXP, v=null, o=null; try{ v=localStorage.getItem(K); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  if(v!=="a5v6"&&v!=="pr2"){
    if(o==="a5"||o==="pr2"){ v=(o==="a5"?"a5v6":"pr2"); }
    else { var A=["a5v6","pr2"]; try{ var r=new Uint8Array(1); crypto.getRandomValues(r); v=A[r[0]%%2]; }catch(e){ v=A[Math.random()<0.5?0:1]; } }
    try{ localStorage.setItem(K,v); }catch(e){}
  }
''' % (D, hm)),
 ('''  location.replace("a5v6.html?"+q.toString()); /* a, a1-a5, b, c, a2/b2/c2, pr, pr_v1 ו-pr2 נשארים באתר, מחוץ לחלוקה */''',
  '''  location.replace(v+".html?"+q.toString()); /* a, a1-a5, b, c, a2/b2/c2, pr ו-pr_v1 נשארים באתר, מחוץ לניסוי */''')])
# --- dashboard: EXP, טבלה לפי אנשים בלשונית 00, רשימת ניסויים, יומן ---
patch("nlp/dashboard.html", [
 ('''const EXP={id:"ap2_0811",name:"a5v6 מול pr2 (חצי-חצי מכל המודעות; a5v6 במקום a5 מ-12.11, ב85)",start:new Date("2026-11-12T11:54:00"),''',
  '''const EXP={id:"pg_1611",name:"a5v6 מול pr2 (pg_1611, חצי-חצי מכל המודעות, ב94)",start:new Date("%s"),''' % ST.strftime("%Y-%m-%dT%H:%M:00")),
 ('''  <section class="screen" id="s-op">
    <div class="banner" id="opMeta"></div>
''', '''  <section class="screen" id="s-op">
    <div class="banner" id="opMeta"></div>
    <div class="panel"><div class="panel-h"><h2>pg_1611: a5v6 מול pr2 - לפי אנשים (ב94)</h2><span class="note" id="pgN"></span></div><div class="tw"><table id="pgT"></table></div></div>
'''),
 ('''
/* ב51: abandoned checkouts''', '''
/* ב94: pg_1611 - a5v6 מול pr2 לפי אנשים (מכשיר). מחליטים לפי לידים (השאירו פרטים) ורכישות מאומתות. בלי בדיקות */
function renderPg(M){const who=s=>s.vid||s.sid,S=M.sess.filter(s=>(s.v==="a5v6"||s.v==="pr2")&&s.p&&s.p.get("exp")==="pg_1611");
 const K=[["אנשים",s=>true],["הגיעו לדף התשלום",s=>s.chk||s.buy],["התחילו למלא",s=>s.cstart||s.det||s.pay||s.buy],["לידים (השאירו פרטים)",s=>s.det||s.pay||s.buy],["רכישות מאומתות",s=>s.buy]];
 const P={a5v6:K.map(()=>new Set()),pr2:K.map(()=>new Set())};S.forEach(s=>K.forEach(([,f],i)=>{if(f(s))P[s.v][i].add(who(s))}));
 const pb=i=>{const a=P.a5v6,b=P.pr2,na=a[0].size,nb=b[0].size;if(!na||!nb)return ["-","-"];let w=0;const N=4000,bt=(x,y)=>{const g=k=>{let s=0;for(let j=0;j<k;j++)s-=Math.log(Math.random());return s};const u=g(x),v=g(y);return u/(u+v)};for(let j=0;j<N;j++){if(bt(1+a[i].size,1+na-a[i].size)>bt(1+b[i].size,1+nb-b[i].size))w++}return [pf(w/N*100),pf(100-w/N*100)]};
 const rows=K.map(([l],i)=>{const pp=i>=3?pb(i):null;return '<tr><td>'+l+'</td>'+["a5v6","pr2"].map((v,j)=>'<td class="num">'+fmt(P[v][i].size)+(i?'<small>'+pf(pct(P[v][i].size,P[v][0].size))+'</small>':'')+(pp?'<small>הטוב ביותר: '+pp[j]+'</small>':'')+'</td>').join("")+'</tr>'});
 table($("pgT"),["לפי אנשים","a5v6","pr2"],S.length?rows:[],"עוד אין כניסות בניסוי pg_1611 (מתחיל בפריסה)");
 $("pgN").textContent="רק ביקורים עם exp=pg_1611 דרך go.html. אחוזים מתוך האנשים בכל דף. מחליטים לפי לידים ורכישות; עד אז מעט נתונים."}

/* ב51: abandoned checkouts'''),
 ('''op:()=>renderOpt(),''', '''op:()=>{renderPg(build(EXP.start,new Date(Date.now()+864e5)));renderOpt()},'''),
 ('''const EXPERIMENTS=[
''', '''const EXPERIMENTS=[
 {id:"pg_1611",name:"a5v6 מול pr2 - ניסוי דפים (ב94, %s)",hyp:"בין a5v6 לדף הפרימיום pr2, אחד מביא יותר לידים ורכישות מאומתות",change:"go.html מחלק את כל התנועה חצי-חצי בין a5v6 ל-pr2, קבוע לדפדפן, exp=pg_1611. מי ששובץ ב-ap2_0811 נשאר בדף שלו. הדפים, דף התשלום וניסוי B מול B2 בלי שינוי",arms:"a5v6, pr2 חצי-חצי, שיוך קבוע לדפדפן",start:"%s",end:"",status:"פעיל",split:"50/50",primary:"לפי אנשים: לידים (השאירו פרטים) ורכישות מאומתות",secondary:"הגעה לדף התשלום, התחלת מילוי",guard:"חלוקה תקינה (SRM), שגיאות טעינה וכשלי תשלום"},
''' % (D, day)),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב94 (\\"מאשר ב94\\" מיהב, אחרי אישור בן לדף הפרימיום): ניסוי דפים pg_1611 - go.html מחלק את כל התנועה חצי-חצי בין a5v6 ל-pr2, קבוע לדפדפן (מי ששובץ ב-ap2_0811 נשאר בדף שלו). אינסטגרם אורגני ל-a. הדפים, דף התשלום וניסוי B מול B2 בלי שינוי. טבלה חדשה בלשונית 00: אנשים, הגיעו לתשלום, התחילו למלא, לידים ורכישות, וההשוואה בלשונית מתחילה ב-%s."],
''' % (day, hm, ST.strftime("%H:%M")))])
# --- הסיכום היומי (ענף): שורות pg_1611 ---
patch("claude/daily/daily_0811.py", [
 ('''SC=datetime(2026,11,15,7,33)''', '''PG=datetime(%d,%d,%d,%d,%d)  # ב94: pg_1611 a5v6 מול pr2 (פריסה + 10 דקות מטמון)
SC=datetime(2026,11,15,7,33)''' % (ST.year, ST.month, ST.day, ST.hour, ST.minute)),
 ('''    if e in("checkout_details","checkout_contact_started"): s["det"]=1''', '''    if e in("checkout_details","checkout_contact_started"): s["det"]=1
    if e=="checkout_details": s["lead"]=1'''),
 ('''EXPID="a5v6_1511"''', '''EXPID="pg_1611"
for only in (True,False):
    E=[s for s in S.values() if s["exp"]=="pg_1611" and s["v"] in("a5v6","pr2") and s["t"]>=PG and (not only or s["src"]=="paid")]
    P=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for s in E:
        o=P[s["v"]][s["vid"] or s["v"]+s["t"].isoformat()]
        for f in ("chk","det","lead","buy"): o[f]|=s.get(f,0)
    print("b94 pg_1611","paid" if only else "all",{v:{"people":len(P[v]),"checkout":sum(o["chk"] for o in P[v].values()),"started":sum(o["det"] for o in P[v].values()),"leads":sum(o["lead"] for o in P[v].values()),"buys":sum(o["buy"] for o in P[v].values())} for v in ("a5v6","pr2")})
EXPID="a5v6_1511"'''),
 ])
print("ok", T0, ST)
