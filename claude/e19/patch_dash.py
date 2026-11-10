# ע19 בדשבורד: סרטוני הזהב (gold_h1_NN / gold_h2_NN) - שורה לכל קוד בלשונית "מעבדה: לפי מודעה" גם לפני שיש כניסות,
# וסיכום לפי כותרת (h1 מול h2): כניסות, הגעה לסליקה ורכישות מאומתות (והוצאה ו-CPA כשמוזנת הוצאה לפי מודעה).
# הרצה מתיקיית הריפו (main): python3 claude/e19/patch_dash.py [HH:MM לשורת היומן] ; אחריו python3 claude/b53/build_campaign.py
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "nlp", "dashboard.html"); s = open(P, encoding="utf8").read()
assert "GOLD19" not in s, "already patched"
HM = sys.argv[1] if len(sys.argv) > 1 else "00:00"
def sub1(a, b):
    global s; assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
H = {"1": "למה המוח שלך מחפש חסרונות?", "2": "המוח שלך גורם לך להאמין שאתה לא מספיק טוב."}
# מהרשימה "סרטוני זהב - רשימה לאישור בן (ע19, 10.11)"
GOLD = [("gold_h1_01", "המוח מחפש חסרונות - טייק 1"), ("gold_h1_02", "המוח מחפש חסרונות - טייק 2"), ("gold_h1_03", "המוח מחפש חסרונות - טייק 3"),
        ("gold_h1_04", "המוח מחפש חסרונות - טייק 4"), ("gold_h2_01", "לא מספיק טוב - טייק 1"), ("gold_h2_02", "לא מספיק טוב - טייק 2"), ("gold_h2_03", "לא מספיק טוב - טייק 3")]
lab = ",".join('"%s":{"name":"%s","open":"%s","type":"סרטון","copy":"כותרת %s","group":"זהב ע19"}' % (c, n, H[c[6]], c[6]) for c, n in GOLD)
# 1. שמות (LAB ו-VIDEO_NAMES, כדי שכל הלשוניות יציגו שם ולא קוד)
sub1('const LAB={', 'const LAB={' + lab + ',')
sub1('const VIDEO_NAMES={', 'const VIDEO_NAMES={' + ",".join('%s:"%s"' % (c, n) for c, n in GOLD) + ',')
# 2. רשימת הקודים והכותרות
sub1('const LAB_MIN={spend:250,ppl:100};', '''const LAB_MIN={spend:250,ppl:100};
/* ע19: סרטוני הזהב. כל קוד מקבל שורה בטבלת המודעות גם לפני הכניסה הראשונה, וסיכום לפי כותרת. קוד חדש מאותה סדרה (gold_hN_NN) נספר בכותרת שלו גם אם לא ברשימה */
const GOLD19={codes:%s,heads:{h1:"%s",h2:"%s"}};''' % ("[" + ",".join('"%s"' % c for c, _ in GOLD) + "]", H["1"], H["2"]))
# 3. שורות ריקות לקודים שעוד אין להם כניסות
sub1('''const L=Object.values(G);L.forEach(r=>{''', '''GOLD19.codes.forEach(k=>{if(!Object.keys(G).some(x=>x.toLowerCase()===k))G[k]=Object.assign(F(),{cr:k,info:labInfo(k),pg:{},none:true})});
 const L=Object.values(G);L.forEach(r=>{''')
sub1('''const few=r=>r.ok?'':'<br><span class="na">מעט נתונים</span>''', '''const few=r=>r.none?'<br><span class="na">עוד לא עלה</span><small>אין כניסות עם הקוד הזה</small>':r.ok?'':'<br><span class="na">מעט נתונים</span>''')
# 4. סיכום לפי כותרת
sub1(''' const crsBy=f=>k=>L.filter(r=>f(r)===k).map(r=>r.cr);''', ''' const crsBy=f=>k=>L.filter(r=>f(r)===k).map(r=>r.cr);
 /* ע19: סרטוני הזהב לפי כותרת (h1 מול h2), ממומן בלבד. שתי השורות מוצגות תמיד */
 {const gk=cr=>{const m=String(cr||"").trim().toLowerCase().match(/^gold_(h[12])_\\d+$/);return m?m[1]:null};
  const A={h1:Object.assign(F(),{k:"h1"}),h2:Object.assign(F(),{k:"h2"})};paid.forEach(s=>{const k=gk(s.cr);if(k)addS(A[k],s)});
  const codesOf=k=>{const seen=new Set();return GOLD19.codes.concat(L.map(r=>r.cr)).filter(c=>gk(c)===k&&!seen.has(c.toLowerCase())&&seen.add(c.toLowerCase()))};
  table($("labGold"),["כותרת","סרטונים","הוצאה","כניסות","הגיעו לסליקה","רכישות מאומתות","CPA"],["h1","h2"].map(k=>{const a=A[k],cs=codesOf(k),sp=spSum(cs),n=a.ppl.size;
   const spc=sp.k===sp.n&&sp.n?ils(sp.t):sp.k?ils(sp.t)+'<small>חלקי: '+sp.k+' מתוך '+sp.n+' מודעות</small>':noData("לא הוזנה הוצאה");
   return '<tr><td><b>'+(k==="h1"?"כותרת 1":"כותרת 2")+'</b><small>'+esc(GOLD19.heads[k])+'</small>'+(n<LAB_MIN.ppl?'<br><span class="na">'+(n?"מעט נתונים":"עוד לא עלה")+'</span>':'')+'</td><td class="num">'+fmt(cs.length)+'<small>'+esc(cs.join(", "))+'</small></td><td>'+spc+'</td><td class="num">'+fmt(n)+'<small>'+fmt(a.v)+' ביקורים</small></td>'+cell(a.chk.size,n)+'<td class="num">'+fmt(a.buy)+'</td><td>'+(sp.k===sp.n&&sp.n&&a.buy?ils(sp.t/a.buy):noData(!a.buy?"אין רכישות":sp.k?"הוצאה חלקית - לא מחושב":"אין הוצאה"))+'</td></tr>'}));
  $("labGoldNote").textContent=fmt(A.h1.ppl.size+A.h2.ppl.size)+" כניסות מסרטוני הזהב בתקופה";}''')
# 5. הפאנל (אחרי "כל המודעות")
sub1('''    <div class="panel"><div class="panel-h"><h2>משפך לפי דף מכירה (ממומן)</h2></div><div class="tw"><table id="labPage"></table></div></div>''',
'''    <div class="panel"><div class="panel-h"><h2>סרטוני הזהב (ע19): כותרת 1 מול כותרת 2 (ממומן)</h2><span class="note" id="labGoldNote"></span></div><div class="tw"><table id="labGold"></table></div>
      <p class="note">כותרת 1 = gold_h1_NN, כותרת 2 = gold_h2_NN (לפי utm_content). כל סרטון גם בשורה משלו בטבלת המודעות למעלה. אנשים ולא ביקורים. הגעה לסליקה = הגיעו לדף הסליקה. רכישה = עסקה מאושרת בקארדקום. הוצאה ו-CPA רק כשהוזנה הוצאה לכל המודעות של הכותרת.</p></div>
    <div class="panel"><div class="panel-h"><h2>משפך לפי דף מכירה (ממומן)</h2></div><div class="tw"><table id="labPage"></table></div></div>''')
# 6. יומן שינויים
sub1('const CHANGELOG=[\n', 'const CHANGELOG=[\n["2026-11-15","%s - ע19: סרטוני הזהב בלשונית המעבדה - שורה לכל קוד (gold_h1_01-04, gold_h2_01-03) גם לפני הכניסה הראשונה, עם השם מהרשימה של ע19, וסיכום לפי כותרת (כותרת 1 מול כותרת 2): כניסות, הגעה לסליקה, רכישות מאומתות, והוצאה ו-CPA כשמוזנת הוצאה לפי מודעה."],\n' % HM)
open(P, "w", encoding="utf8").write(s); print("ok", len(s))
