# ב102 (ראשי 16.11, בן אישר): ניסוי דפים on_1611 - המסלול הישן (a.html + סליקה A, שני שלבים) מול a5v6 + סליקה B2. הכנה מקומית; פריסה רק אחרי "מאשר ב102".
# שימוש: python3 patch_b102.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"   (שעת הפריסה; ההשוואה מ-10 דקות אחריה, אחרי המטמון)
import sys, os
from datetime import datetime, timedelta
root, day, hm = sys.argv[1:4]
T0 = datetime.strptime(day + " " + hm, "%Y-%m-%d %H:%M"); ST = T0 + timedelta(minutes=10)
D = day[8:10] + "." + day[5:7]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:90], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)

# ---------- go.html ----------
patch("nlp/go.html", [
 ('''  var EXP="pg_1611", K="nlp_go_"+EXP, v=null, o=null; try{ v=localStorage.getItem(K); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  if(v!=="a5v6"&&v!=="pr2"){
    if(o==="a5"||o==="pr2"){ v=(o==="a5"?"a5v6":"pr2"); }
    else { var A=["a5v6","pr2"]; try{ var r=new Uint8Array(1); crypto.getRandomValues(r); v=A[r[0]%2]; }catch(e){ v=A[Math.random()<0.5?0:1]; } }
    try{ localStorage.setItem(K,v); }catch(e){}
  }
''', '''  /* ב102 ("מאשר ב102" מיהב, %s %s, בן אישר): ניסוי on_1611 - המסלול הישן (a.html + סליקה A, שני שלבים) מול a5v6 + סליקה B2. חצי-חצי, קבוע לדפדפן,
     לכל התנועה שעוברת ב-go.html. pg_1611 נסגר: מי ששובץ בו (או ב-ap2_0811) נשאר בדף שלו עם ה-exp הישן ולא נכנס לניתוח. pr2 נשאר באתר, מחוץ לחלוקה.
     הזרוע נשמרת גם ב-nlp_co_ab, ודף התשלום פותח לפיה סליקה A או B2. אינסטגרם אורגני ממשיך ל-a בלי exp (ב44), אבל מבקר חדש מוגרל קודם לזרוע (nlp_co_ab), ולכן בסליקה הוא מקבל A או B2 לפי הזרוע */
  var EXP="on_1611", K="nlp_go_"+EXP, v=null, pg=null, o=null, ex=EXP; try{ v=localStorage.getItem(K); pg=localStorage.getItem("nlp_go_pg_1611"); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  if(v!=="a"&&v!=="a5v6"){
    if(pg==="a5v6"||pg==="pr2"){ v=pg; ex="pg_1611"; }
    else if(o==="a5"||o==="pr2"){ v=(o==="a5"?"a5v6":"pr2"); ex="ap2_0811"; }
    else { var A=["a","a5v6"]; try{ var r=new Uint8Array(1); crypto.getRandomValues(r); v=A[r[0]%%2]; }catch(e){ v=A[Math.random()<0.5?0:1]; }
      try{ localStorage.setItem(K,v); localStorage.setItem("nlp_co_ab",v==="a"?"a":"b2"); }catch(e){} }
  }
''' % (D, hm)),
 ('''  q.set("exp",EXP);
''', '''  q.set("exp",ex);
'''),
])

# ---------- checkout.html ----------
patch("nlp/checkout.html", [
 ('''<script>/* ב90: ניסוי co_b2_1311 - B מול B2 חצי-חצי, נשמר במכשיר. co=a/b/b2 בכתובת גובר */
(function(){var c="b";try{c=(new URLSearchParams(location.search).get("co")||"").toLowerCase();
if(c!=="a"&&c!=="b"&&c!=="b2"){var k="nlp_co_b2",v=null;try{v=localStorage.getItem(k)}catch(e){}
 if(v!=="b"&&v!=="b2"){v=Math.random()<0.5?"b2":"b";try{localStorage.setItem(k,v)}catch(e){}}c=v}}catch(e){c="b"}
window.NLP_CO=c;document.documentElement.setAttribute("data-co2",c==="b2"?"1":"0")})();</script>''',
  '''<script>/* ב102 (%s): ניסוי on_1611 - זרוע "ישן" = סליקה A, זרוע "חדש" = B2. סדר: co בכתובת > exp=on_1611 בכתובת (v=a -> A, אחרת B2) > nlp_co_ab (נשמר ב-go.html) > שיבוץ B/B2 קודם (ב90) > B2.
   ניסוי B מול B2 (ב90) נסגר: מכשיר חדש מחוץ לניסוי מקבל B2 */
(function(){var c="b2";try{var q=new URLSearchParams(location.search);c=(q.get("co")||"").toLowerCase();
if(c!=="a"&&c!=="b"&&c!=="b2"){if(q.get("exp")==="on_1611")c=(q.get("v")==="a"?"a":"b2");else{var ab=null,v=null;try{ab=localStorage.getItem("nlp_co_ab");v=localStorage.getItem("nlp_co_b2")}catch(e){}
 if(ab==="a"||ab==="b2")c=ab;else if(v==="b"||v==="b2")c=v;else{c="b2";try{localStorage.setItem("nlp_co_b2","b2")}catch(e){}}}}}catch(e){c="b2"}
window.NLP_CO=c;document.documentElement.setAttribute("data-co2",c==="b2"?"1":"0");document.documentElement.setAttribute("data-co",c==="a"?"a":"b")})();</script>''' % D),
 ('''<p class="once">תשלום חד-פעמי</p>''', '''<p class="once">תשלום חד-פעמי<span class="pay3i"> · או 3 תשלומים של 99 ₪</span></p>'''),
 ('''.fld+.trust{margin:-2px 0 12px}''', '''.fld+.trust{margin:-2px 0 12px}
html[data-co="a"] .trust{display:none} /* ב102: סליקה A כמו שהייתה (בלי שורת האמון של ב96) */
.pay3i{display:none}
@media (max-width:600px){html[data-co="a"] .pay3{display:none}html[data-co="a"] .pay3i{display:inline}} /* ב102: ב-A במובייל שורת 3 התשלומים מאוחדת עם "תשלום חד-פעמי" - בלי תוספת גובה */'''),
 ('''@media (max-width:600px){
.wrap{padding-top:10px}
.brand{padding:2px 0 8px}
.top,html[data-co2="1"] .top{padding:10px 0 0}
.top h1{font-size:26px;margin:0 0 2px}
.top .what{font-size:15.5px}
.top .what2{display:none}
.order,html[data-co2="1"] .order{margin:10px 0 0;padding:9px 12px}
.order>*:not(.one1){display:none!important}
.order .one1{display:block;margin:0;text-align:center;font-size:16px;font-weight:800;line-height:1.35}
.why,html[data-co2="1"] .why{margin-top:10px;padding-top:10px}
.why h2{margin:0 0 6px}
.incl-end{display:block;margin:16px 0 0;padding:14px 16px;border:1px solid var(--line);border-radius:var(--r);background:var(--soft)}
.incl-end .incl{margin:0;padding:0;border:0}
}''', '''@media (max-width:600px){ /* ב102: רק B ו-B2 - סליקה A נשארת בעיצוב שלה */
html:not([data-co="a"]) .wrap{padding-top:10px}
html:not([data-co="a"]) .brand{padding:2px 0 8px}
html:not([data-co="a"]) .top{padding:10px 0 0}
html:not([data-co="a"]) .top h1{font-size:26px;margin:0 0 2px}
html:not([data-co="a"]) .top .what{font-size:15.5px}
html:not([data-co="a"]) .top .what2{display:none}
html:not([data-co="a"]) .order{margin:10px 0 0;padding:9px 12px}
html:not([data-co="a"]) .order>*:not(.one1){display:none!important}
html:not([data-co="a"]) .order .one1{display:block;margin:0;text-align:center;font-size:16px;font-weight:800;line-height:1.35}
html:not([data-co="a"]) .why{margin-top:10px;padding-top:10px}
html:not([data-co="a"]) .why h2{margin:0 0 6px}
html:not([data-co="a"]) .incl-end{display:block;margin:16px 0 0;padding:14px 16px;border:1px solid var(--line);border-radius:var(--r);background:var(--soft)}
html:not([data-co="a"]) .incl-end .incl{margin:0;padding:0;border:0}
}'''),
 ('''const CO_EXP = "co_b2_1511m";''', '''const CO_EXP = "co_on_1611"; /* ב102 (%s %s): ניסוי on_1611 (A מול B2); ב90 נסגר */ const CO_EXP_OLD = "co_b2_1511m";''' % (D, hm)),
])

# ---------- dashboard.html ----------
patch("nlp/dashboard.html", [
 ('''    <div class="panel"><div class="panel-h"><h2>pg_1611: a5v6 מול pr2 - לפי אנשים (ב94)</h2><span class="note" id="pgN"></span></div><div class="tw"><table id="pgT"></table></div></div>
''', '''    <div class="panel"><div class="panel-h"><h2>on_1611: המסלול הישן (a + סליקה A) מול a5v6 + B2 - לפי אנשים (ב102)</h2><span class="note" id="onN"></span></div><div class="tw"><table id="onT"></table></div><div class="tw"><table id="onT2"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>pg_1611: a5v6 מול pr2 - לפי אנשים (ב94, נסגר %s)</h2><span class="note" id="pgN"></span></div><div class="tw"><table id="pgT"></table></div></div>
''' % D),
 ('''/* ב94: pg_1611 - a5v6 מול pr2 לפי אנשים (מכשיר).''', '''/* ב102: on_1611 - "ישן" (a + סליקה A) מול "חדש" (a5v6 + B2), לפי אנשים. מדד ראשי: השאירו פרטים, ממודעות של בן בלבד (בלי משווקים).
   כלל עצירה: 150 אנשים לזרוע ממודעות של בן או 14 יום. מנצחת: פי 2 לפחות בהשארת פרטים ולפחות 5 משאירי פרטים. ההחלטה בסקירה השבועית */
const ON_START=new Date("%s");
function renderOn(M){const who=s=>s.vid||s.sid,ARM={a:"ישן: a + סליקה A",a5v6:"חדש: a5v6 + B2"};
 const all=M.sess.filter(s=>(s.v==="a"||s.v==="a5v6")&&s.p&&s.p.get("exp")==="on_1611");
 const K=[["אנשים",s=>true],["הגיעו לדף התשלום",s=>s.chk||s.buy],["התחילו למלא",s=>s.cstart||s.det||s.pay||s.buy],["השאירו פרטים (מדד ראשי)",s=>s.det||s.pay||s.buy],["הגיעו לטופס התשלום",s=>s.pay||s.buy],["רכישות מאומתות",s=>s.buy]];
 const tab=(S)=>{const P={a:K.map(()=>new Set()),a5v6:K.map(()=>new Set())};S.forEach(s=>K.forEach(([,f],i)=>{if(f(s))P[s.v][i].add(who(s))}));
  return K.map(([l],i)=>'<tr><td>'+l+'</td>'+["a","a5v6"].map(v=>'<td class="num">'+fmt(P[v][i].size)+(i?'<small>'+pf(pct(P[v][i].size,P[v][0].size))+'</small>':'')+'</td>').join("")+'</tr>')};
 const ben=all.filter(s=>s.src==="מודעות Meta"&&!s.aff),aff=all.filter(s=>s.aff);
 table($("onT"),["ממודעות של בן (ראשי)",ARM.a,ARM.a5v6],ben.length?tab(ben):[],"עוד אין כניסות ממודעות של בן בניסוי on_1611 (מתחיל בפריסה)");
 table($("onT2"),["משווקים (בנפרד)",ARM.a,ARM.a5v6],aff.length?tab(aff):[],"עוד אין כניסות של משווקים בניסוי");
 const n=v=>new Set(ben.filter(s=>s.v===v).map(who)).size,d=Math.floor((Date.now()-ON_START)/864e5);
 $("onN").textContent="מ-"+ON_START.toLocaleString("he-IL",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})+". עצירה: 150 אנשים לזרוע ממודעות של בן או 14 יום (עכשיו "+n("a")+" / "+n("a5v6")+", יום "+d+"). מנצחת: פי 2 בהשארת פרטים ולפחות 5. בלי בדיקות; מי ששובץ קודם ב-pg_1611 לא נספר."}

/* ב94: pg_1611 - a5v6 מול pr2 לפי אנשים (מכשיר).''' % ST.strftime("%Y-%m-%dT%H:%M:00")),
 ('''op:()=>{renderPg(build(EXP.start,new Date(Date.now()+864e5)));renderOpt()},''', '''op:()=>{renderOn(build(ON_START,new Date(Date.now()+864e5)));renderPg(build(EXP.start,new Date(Date.now()+864e5)));renderOpt()},'''),
 ('''const EXPERIMENTS=[
''', '''const EXPERIMENTS=[
 {id:"on_1611",name:"המסלול הישן מול הדף החדש (ב102, %s)",hyp:"המסלול הישן (a + סליקה A בשני שלבים) מביא יותר השארת פרטים מ-a5v6 + B2 (ב-Pilot: a 8 מ-129, a5/pr2/a5v6 יחד 1 מ-208)",change:"go.html מחלק חצי-חצי בין a (סליקה A) ל-a5v6 (סליקה B2), קבוע לדפדפן, exp=on_1611. pg_1611 וניסוי B מול B2 נסגרו; מי ששובץ קודם נשאר בדף שלו מחוץ לניתוח. אינסטגרם אורגני: ל-a בלי exp, ובסליקה A או B2 לפי הזרוע שהוגרלה",arms:"ישן (a + סליקה A) מול חדש (a5v6 + B2), חצי-חצי, שיוך קבוע לדפדפן",start:"%s",end:"",status:"פעיל",split:"50/50",primary:"השאירו פרטים לאדם, ממודעות של בן בלבד (משווקים בנפרד). עצירה: 150 אנשים לזרוע או 14 יום; מנצחת פי 2 ולפחות 5",secondary:"הגעה לדף התשלום, התחלת מילוי, טופס תשלום, רכישות מאומתות",guard:"חלוקה תקינה (SRM), סליקה לפי זרוע (a->A, a5v6->B2), שגיאות טעינה וכשלי תשלום"},
''' % (D, day)),
 ('''arms:"a5v6, pr2 חצי-חצי, שיוך קבוע לדפדפן",start:"2026-11-15",end:"",status:"פעיל",''', '''arms:"a5v6, pr2 חצי-חצי, שיוך קבוע לדפדפן",start:"2026-11-15",end:"%s",status:"נסגר (ב102)",''' % day),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב102 (\\"מאשר ב102\\" מיהב, בן אישר): ניסוי on_1611 - go.html מחלק חצי-חצי בין המסלול הישן (a + סליקה A, שני שלבים) ל-a5v6 + B2, קבוע לדפדפן. pg_1611 וניסוי B מול B2 נסגרו (מי ששובץ קודם נשאר בדף שלו). סליקה A בעיצוב שלה (בלי שורת האמון ובלי כרטיס השורה האחת של ב99), עם 3 התשלומים, ביט, Apple Pay ו-Google Pay, ההתאמה המתקדמת וסימון הבדיקה. cx=co_on_1611. אינסטגרם אורגני ממשיך ל-a בלי exp, אבל מבקר חדש מוגרל לזרוע ובסליקה מקבל A או B2 לפיה (שורה נפרדת בסיכום היומי). ההשוואה מ-%s."],
''' % (day, hm, ST.strftime("%H:%M"))),
])

# ---------- daily_0811.py (ענף) ----------
patch("claude/daily/daily_0811.py", [
 ('''EXPID="a5v6_1511"
report(SC''', '''# ב102: on_1611 - "ישן" (a + סליקה A) מול "חדש" (a5v6 + B2). ראשי: השאירו פרטים (checkout_details) לאדם, ממודעות של בן בלבד. משווקים בנפרד
ON=datetime(%d,%d,%d,%d,%d)  # פריסה + 10 דקות מטמון
for lab,keep in (("paid",lambda s:s["src"]=="paid"),("aff",lambda s:s["src"]=="aff"),("all",lambda s:True)):
    E=[s for s in S.values() if s["exp"]=="on_1611" and s["v"] in("a","a5v6") and s["t"]>=ON and keep(s)]
    P=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for s in E:
        o=P[s["v"]][s["vid"] or s["v"]+s["t"].isoformat()]
        for f in ("chk","det","lead","pay","buy"): o[f]|=s.get(f,0)
    R3={v:{"people":len(P[v]),"checkout":sum(o["chk"] for o in P[v].values()),"started":sum(o["det"] for o in P[v].values()),"leads":sum(o["lead"] for o in P[v].values()),"payform":sum(o["pay"] for o in P[v].values()),"buys":sum(o["buy"] for o in P[v].values())} for v in ("a","a5v6")}
    print("b102 on_1611",lab,R3,"| SRM",srm(R3["a"]["people"],R3["a5v6"]["people"]))
print("b102 stop rule: paid people per arm (150) a=%%d a5v6=%%d, days %%d of 14" %% (len({s["vid"] or s["t"] for s in S.values() if s["exp"]=="on_1611" and s["v"]=="a" and s["t"]>=ON and s["src"]=="paid"}),len({s["vid"] or s["t"] for s in S.values() if s["exp"]=="on_1611" and s["v"]=="a5v6" and s["t"]>=ON and s["src"]=="paid"}),max(0,(datetime.now()-ON).days)))
IG=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for s in S.values():
    if s["route"]=="ig_org" and s["t"]>=ON and s["chk"]:
        o=IG[s["co"] or "-"][s["vid"] or s["t"].isoformat()]
        for f in ("chk","lead","buy"): o[f]|=s.get(f,0)
IGP=defaultdict(set)
for s in S.values():
    if s["route"]=="ig_org" and s["t"]>=ON: IGP["all"].add(s["vid"] or s["t"].isoformat())
print("b102 ig_org by checkout (A vs B2): people (all ig_org)",len(IGP["all"]),{co:{"reached checkout":len(P),"details":sum(o["lead"] for o in P.values()),"buys":sum(o["buy"] for o in P.values())} for co,P in IG.items()})
print("b102 checkout version by arm (should be a->a, a5v6->b2):",Counter((s["v"],s["co"] or "-") for s in S.values() if s["exp"]=="on_1611" and s["chk"]))
EXPID="a5v6_1511"
report(SC''' % (ST.year, ST.month, ST.day, ST.hour, ST.minute)),
])
print("ok", T0, ST)
