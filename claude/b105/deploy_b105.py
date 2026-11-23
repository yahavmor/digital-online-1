# ב105 פריסה + כניסה לניסוי ("מאשר ב105" מיהב, בן אישר, הוק א; 17.11): a5v7 נכנס לאתר, וניסוי on_1711 מחליף את on_1611:
#   המסלול הישן (a + סליקה A) מול a5v7 + B2, חצי-חצי, קבוע לדפדפן, ספירה חדשה. מי ששובץ ב-on_1611 (או קודם) נשאר בדף שלו עם ה-exp הישן.
# שימוש: python3 deploy_b105.py <repo root> "<YYYY-MM-DD>" "<HH:MM>" "<ON_START YYYY-MM-DDTHH:MM:00>"
import sys, os, subprocess
root, day, hm, start = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(HERE, "build_b105.py"), root, os.path.join(root, "nlp"), "--hook=a"])
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:90], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
patch("nlp/go.html", [
 ('''  var EXP="on_1611", K="nlp_go_"+EXP, v=null, pg=null, o=null, ex=EXP; try{ v=localStorage.getItem(K); pg=localStorage.getItem("nlp_go_pg_1611"); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  if(v!=="a"&&v!=="a5v6"){
    if(pg==="a5v6"||pg==="pr2"){ v=pg; ex="pg_1611"; }''',
  '''  /* ב105 ("מאשר ב105" מיהב, בן אישר, %s %s): ניסוי on_1711 - המסלול הישן (a.html + סליקה A) מול a5v7 + סליקה B2 (הדף החדש של בן: הוק חדש, ההצעה מיד אחרי הפתרון,
     ההוכחות מתחתיה, בלי "למה בניתי"). חצי-חצי, קבוע לדפדפן, ספירה חדשה. on_1611 נסגר: מי ששובץ בו נשאר בדף שלו (a או a5v6) עם exp=on_1611 ולא נכנס לניתוח החדש;
     כך גם מי ששובץ ב-pg_1611 או ב-ap2_0811. הזרוע נשמרת ב-nlp_co_ab כמו קודם (a -> A, a5v7 -> B2). אינסטגרם אורגני בלי שינוי (ב44) */
  var EXP="on_1711", K="nlp_go_"+EXP, v=null, p16=null, pg=null, o=null, ex=EXP; try{ v=localStorage.getItem(K); p16=localStorage.getItem("nlp_go_on_1611"); pg=localStorage.getItem("nlp_go_pg_1611"); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  if(v!=="a"&&v!=="a5v7"){
    if(p16==="a"||p16==="a5v6"){ v=p16; ex="on_1611"; }
    else if(pg==="a5v6"||pg==="pr2"){ v=pg; ex="pg_1611"; }''' % (day, hm)),
 ('''    else { var A=["a","a5v6"];''', '''    else { var A=["a","a5v7"];'''),
])
patch("nlp/checkout.html", [
 ('''if(q.get("exp")==="on_1611")c=(q.get("v")==="a"?"a":"b2");''',
  '''if(/^on_1[67]11$/.test(q.get("exp")||""))c=(q.get("v")==="a"?"a":"b2"); /* ב105: גם on_1711 (a -> A, a5v7 -> B2) */'''),
])
patch("nlp/dashboard.html", [
 ('const ALLV=["a2","b2","c2","a","b","c","a1","a3","a4","a5","a5v6","pr","pr2"], VLBL={',
  'const ALLV=["a2","b2","c2","a","b","c","a1","a3","a4","a5","a5v6","a5v7","pr","pr2"], VLBL={a5v7:"a5v7 - הדף החדש של בן: הוק חדש, ההצעה אחרי הפתרון (ב105)",'),
 ('const ON_START=new Date("2026-11-16T15:05:00");', 'const ON_START=new Date("%s"); /* ב105: on_1711 - פריסה + 10 דקות מטמון. on_1611 (מ-16.11 15:05) נסגר */' % start),
 ('function renderOn(M){const who=s=>s.vid||s.sid,ARM={a:"ישן: a + סליקה A",a5v6:"חדש: a5v6 + B2"};\n const all=M.sess.filter(s=>(s.v==="a"||s.v==="a5v6")&&s.p&&s.p.get("exp")==="on_1611");',
  'function renderOn(M){const who=s=>s.vid||s.sid,ARM={a:"ישן: a + סליקה A",a5v7:"חדש: a5v7 + B2"}; /* ב105: on_1711 */\n const all=M.sess.filter(s=>(s.v==="a"||s.v==="a5v7")&&s.p&&s.p.get("exp")==="on_1711");'),
 ('const tab=(S)=>{const P={a:K.map(()=>new Set()),a5v6:K.map(()=>new Set())};', 'const tab=(S)=>{const P={a:K.map(()=>new Set()),a5v7:K.map(()=>new Set())};'),
 ('''  return K.map(([l],i)=>'<tr><td>'+l+'</td>'+["a","a5v6"].map(v=>''', '''  return K.map(([l],i)=>'<tr><td>'+l+'</td>'+["a","a5v7"].map(v=>'''),
 ('table($("onT"),["ממודעות של בן (ראשי)",ARM.a,ARM.a5v6],ben.length?tab(ben):[],"עוד אין כניסות ממודעות של בן בניסוי on_1611 (מתחיל בפריסה)");',
  'table($("onT"),["ממודעות של בן (ראשי)",ARM.a,ARM.a5v7],ben.length?tab(ben):[],"עוד אין כניסות ממודעות של בן בניסוי on_1711 (מתחיל בפריסה)");'),
 ('table($("onT2"),["משווקים (בנפרד)",ARM.a,ARM.a5v6]', 'table($("onT2"),["משווקים (בנפרד)",ARM.a,ARM.a5v7]'),
 ('table($("onT3"),["סך הכול: בן + משווקים",ARM.a,ARM.a5v6]', 'table($("onT3"),["סך הכול: בן + משווקים",ARM.a,ARM.a5v7]'),
 ('const out=M.sess.filter(s=>(s.v==="a"||s.v==="a5v6")&&s.t>=ON_START', 'const out=M.sess.filter(s=>(s.v==="a"||s.v==="a5v6"||s.v==="a5v7")&&s.t>=ON_START'),
 ('(עכשיו "+n("a")+" / "+n("a5v6")+", יום "+d+"). מנצחת: פי 2 בהשארת פרטים ולפחות 5. בלי בדיקות; מי ששובץ קודם ב-pg_1611 לא נספר."',
  '(עכשיו "+n("a")+" / "+n("a5v7")+", יום "+d+"). מנצחת: פי 2 בהשארת פרטים ולפחות 5. בלי בדיקות; מי ששובץ קודם ב-on_1611 או ב-pg_1611 לא נספר."'),
 ('<h2>on_1611: המסלול הישן (a + סליקה A) מול a5v6 + B2 - לפי אנשים (ב102)</h2>', '<h2>on_1711: המסלול הישן (a + סליקה A) מול a5v7 + B2 - לפי אנשים (ב105)</h2>'),
 (',start:"2026-11-16",end:"",status:"פעיל",split:"50/50",primary:"השאירו פרטים לאדם, ממודעות של בן בלבד (משווקים בנפרד). עצירה: 150 אנשים לזרוע או 14 יום; מנצחת פי 2 ולפחות 5"',
  ',start:"2026-11-16",end:"%s",status:"נסגר (ב105) - הזרוע של a5v6 הוחלפה ב-a5v7, ספירה חדשה ב-on_1711",split:"50/50",primary:"השאירו פרטים לאדם, ממודעות של בן בלבד (משווקים בנפרד). עצירה: 150 אנשים לזרוע או 14 יום; מנצחת פי 2 ולפחות 5"' % day),
 (' {id:"on_1611",', ''' {id:"on_1711",name:"המסלול הישן מול a5v7 (ב105, 17.11)",hyp:"הדף החדש של בן (הוק עם כאב ממשי ולולאה פתוחה, ההצעה מיד אחרי הפתרון, ההוכחות מתחתיה) מביא יותר השארת פרטים מהמסלול הישן",change:"a5v7 (מ-a5v6: הוק א, בלי 'למה בניתי', ההצעה והאחריות אחרי הפתרון, ההוכחות מתחת להצעה) מחליף את a5v6 בזרוע החדשה. go.html חצי-חצי בין a (סליקה A) ל-a5v7 (סליקה B2), exp=on_1711. מי ששובץ ב-on_1611 נשאר בדף שלו מחוץ לניתוח",arms:"ישן (a + סליקה A) מול חדש (a5v7 + B2), חצי-חצי, שיוך קבוע לדפדפן",start:"%s",end:"",status:"פעיל",split:"50/50",primary:"השאירו פרטים לאדם, ממודעות של בן בלבד (משווקים בנפרד). עצירה: 150 אנשים לזרוע או 14 יום; מנצחת פי 2 ולפחות 5",secondary:"נשארו דקה ומעלה, הגעה לדף התשלום, התחלת מילוי, טופס תשלום, רכישות מאומתות",guard:"חלוקה תקינה (SRM), סליקה לפי זרוע (a->A, a5v7->B2), כפתור הפתיחה במסך הראשון"},
 {id:"on_1611",''' % day),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב105 (\\"מאשר ב105\\" מיהב, בן אישר, הוק א): a5v7 באתר (מ-a5v6: הוק חדש, בלי \\"למה בניתי\\", ההצעה והאחריות אחרי הפתרון, ההוכחות מתחת להצעה). ניסוי on_1711 מחליף את on_1611: a + סליקה A מול a5v7 + B2, חצי-חצי, ספירה חדשה מ-%s. מי ששובץ ב-on_1611 נשאר בדף שלו מחוץ לניתוח. טבלת הניסוי בלשונית 00 עברה ל-on_1711."],\n' % (day, hm, start.replace("T", " ")[:16])),
])
print("ok")
