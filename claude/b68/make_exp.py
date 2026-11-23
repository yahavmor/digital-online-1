# ב68: הניסוי החדש - הדף שניצח ב-ap2_0811 מול גרסת v3 שלו, חצי-חצי ב-go.html, עם מפתח ניסוי חדש.
# מריצים רק בעלייה (אחרי סוף ap2_0811 ו"מאשר ב68"), מתיקיית הריפו, אחרי build_v3.py:
#   python3 claude/b68/make_exp.py <a5|pr2> <YYYY-MM-DDTHH:MM שעת העלייה> [מזהה ניסוי, ברירת מחדל <גרסה>_DDMM] [--ver=v4]
#   --ver=v4 (תוכנית ראשון 15.11): המנצח מול גרסת v4 שלו (v3 + עיצוב פרימיום, s15/build_v4.py). ברירת המחדל v3
# משנה: nlp/go.html, nlp/dashboard.html (ניסוי, תוויות, טבלת הניסויים, יומן). אחר כך: python3 claude/b53/build_campaign.py
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VER = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--ver=")), "v3"); sys.argv = [a for a in sys.argv if not a.startswith("--ver=")]; assert VER in ("v3", "v4")
W = sys.argv[1]; START = sys.argv[2]; assert W in ("a5", "pr2") and re.match(r"\d{4}-\d\d-\d\dT\d\d:\d\d$", START)
NEW = W + VER; D = START[8:10] + START[5:7]; EID = sys.argv[3] if len(sys.argv) > 3 else VER + "_" + D
DESC = {"v3": "סדר ומהירות", "v4": "סדר ומהירות ועיצוב פרימיום"}[VER]
CHG = {"v3": "פתיחה טקסטואלית מהירה, המחיר והכפתור במסך הראשון, ההצעה מיד אחרי העדויות",
       "v4": "כמו v3 (המחיר והכפתור במסך הראשון, ההצעה מיד אחרי העדויות) ועוד כפתורים בולטים, מנעול ותשלום מאובטח ליד כל כפתור, כניסה עדינה בגלילה, רקעים וצללים, גופן מהאתר"}[VER]
DAY = START[8:10] + "." + START[5:7]; HM = START[11:16]

def sub1(s, a, b):
    assert s.count(a) == 1, (a[:60], s.count(a)); return s.replace(a, b)

# ---------- go.html ----------
p = os.path.join(ROOT, "nlp", "go.html"); s = open(p, encoding="utf8").read()
a0 = s.index('  /* ב63 (בן 08.11'); a1 = s.index('  var q=new URLSearchParams(location.search);')
s = s[:a0] + '''  /* ב68 (%s): ניסוי %s - %s מול %s (גרסת %s של אותו דף: %s), חצי-חצי, קבוע לדפדפן, לכל התנועה שעוברת ב-go.html.
     מי ששובץ ב-ap2_0811 (הניסוי הקודם, a5 מול pr2) ממשיך לדף שלו מחוץ לניסוי החדש (exp=ap2_0811), כדי שלא יראה דף אחר בחזרה
     ולא ייכנס להשוואה החדשה. %s ו-%s נשארים באתר. */
  var EXP="%s", K="nlp_go_"+EXP, v=null, o=null; try{ v=localStorage.getItem(K); o=localStorage.getItem("nlp_go_ap2_0811"); }catch(e){}
  var OLD=(o==="a5"||o==="pr2")?o:null;
  if(!OLD && v!=="%s" && v!=="%s"){
    var A=["%s","%s"]; try{ var r=new Uint8Array(1); crypto.getRandomValues(r); v=A[r[0]%%2]; }catch(e){ v=A[Math.random()<0.5?0:1]; }
    try{ localStorage.setItem(K,v); }catch(e){}
  }
''' % (DAY, EID, W, NEW, VER, DESC, "a5" if W == "pr2" else "pr2", W, EID, W, NEW, W, NEW) + s[a1:]
s = sub1(s, '  q.set("exp",EXP);\n  location.replace(v+".html?"+q.toString());',
            '  if(OLD){ q.set("exp","ap2_0811"); location.replace(OLD+".html?"+q.toString()); return; }\n  q.set("exp",EXP);\n  location.replace(v+".html?"+q.toString());')
open(p, "w", encoding="utf8").write(s)

# ---------- dashboard.html ----------
p = os.path.join(ROOT, "nlp", "dashboard.html"); s = open(p, encoding="utf8").read()
P2, A5 = "pr2" + VER, "a5" + VER
s = sub1(s, 'const ALLV=["a2","b2","c2","a","b","c","a1","a3","a4","a5","pr","pr2"], VLBL={',
            'const ALLV=["a2","b2","c2","a","b","c","a1","a3","a4","a5","pr","pr2","%s","%s"], VLBL={%s:"%s - pr2 ב%s (ב68)",%s:"%s - a5 ב%s (ב68)",' % (A5, P2, P2, P2, DESC, A5, A5, DESC))
s = sub1(s, 'VCOL={a:"var(--s1)"', 'VCOL={%s:"var(--s5)",%s:"var(--s6)",a:"var(--s1)"' % (P2, A5))
m = re.search(r'const EXP=\{id:"ap2_0811".*?\};', s); assert m
s = s.replace(m.group(0), 'const EXP={id:"%s",name:"%s מול %s (%s: %s, חצי-חצי מכל המודעות)",start:new Date("%s:00"),arms:["%s","%s"],split:{%s:1,%s:1},target:"",minN:300,minBuy:20,cut:{total:100,perPage:25,events:5,p:.9,ratio:.5,buyFrom:3}}; /* ב68. הקודם: ap2_0811 (a5 מול pr2), בטבלת הניסויים */' % (EID, W, NEW, VER, DESC, START, W, NEW, W, NEW), 1)
s = sub1(s, '297 ₪ · ניסוי a5 מול pr2 (ap2_0811) → קארדקום', '297 ₪ · ניסוי %s מול %s (%s) → קארדקום' % (W, NEW, EID))
m = re.search(r'רק ביקורים שנכנסו לניסוי דרך go\.html \(exp=ap2_0811, a5 מול pr2\), מ-08\.11 14:19 \([^)]*\)', s); assert m
s = s.replace(m.group(0), 'רק ביקורים שנכנסו לניסוי דרך go.html (exp=%s, %s מול %s), מ-%s %s. מי ששובץ בניסוי הקודם ap2_0811 ממשיך לדף שלו ולא נספר כאן' % (EID, W, NEW, DAY, HM), 1)
s = sub1(s, 'החלוקה בין a5 ל-pr2 היא של הניסוי ap2_0811 (חצי-חצי לכל התנועה)', 'החלוקה בין %s ל-%s היא של הניסוי %s (חצי-חצי לכל התנועה)' % (W, NEW, EID))
s = sub1(s, 'const EXPERIMENTS=[\n {id:"ap2_0811",', 'const EXPERIMENTS=[\n {id:"%s",name:"%s מול %s - אותו דף ב%s (ב68, %s)",hyp:"כשהמחיר והכפתור במסך הראשון וההצעה עולה מיד אחרי העדויות, יותר מבקרים מגיעים לסליקה",change:"%s: %s (ההצעה: pr2 סקשן 3; a5 סקשן 4, אחרי ״רגע לפני״). אותו קופי, אותן עדויות ואותה מדידה",arms:"%s, %s חצי-חצי, שיוך קבוע לדפדפן (go.html, exp=%s). מי ששובץ ב-ap2_0811 ממשיך לדף שלו מחוץ לניסוי",start:"%s",end:"",split:"50/50",primary:"הגעה לסליקה לכל מבקר, ואחריו עלות לרכישה מאומתת",secondary:"מעבר מסך ראשון, הגעה להצעה, לחיצות לפי מיקום",guard:"חלוקה תקינה (SRM), LCP במובייל, שגיאות טעינה וכשלי תשלום"},\n {id:"ap2_0811",' % (EID, W, NEW, DESC, DAY, NEW, CHG, W, NEW, EID, START[:10]))
m = re.search(r'(\{id:"ap2_0811",.*?start:"2026-11-08",end:)""', s); assert m
s = s.replace(m.group(0), m.group(1) + '"%s"' % START[:10], 1)
s = sub1(s, 'const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב68: ניסוי חדש %s - %s מול %s, חצי-חצי ב-go.html. %s היא אותו דף ב%s: %s (ההצעה: pr2 סקשן 3; a5 סקשן 4, אחרי ״רגע לפני״); אותו קופי, אותן עדויות ואותה מדידה. מדד ראשי: הגעה לסליקה לכל מבקר, ואחריו עלות לרכישה מאומתת. ap2_0811 הסתיים, ומי ששובץ בו ממשיך לדף שלו מחוץ לניסוי החדש."],\n' % (START[:10], HM, EID, W, NEW, NEW, DESC, CHG))
open(p, "w", encoding="utf8").write(s)
print("ok", EID, W, NEW, START)
