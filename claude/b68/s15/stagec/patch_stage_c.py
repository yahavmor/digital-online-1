# ב68 שלב ג ("מאשר" מיהב דרך הראשי, 15.11): ap2_0811 נסגר, a5v6 נקבע כדף המוביל. כל התנועה ב-go.html ל-a5v6.
# a5v6 כבר בנוי מ-v4 (a5v4 = build_v4 + הרשימה של בן; a5v6 = a5v4 עם הכפתורים הירוקים, ב85), ולכן הדפים עצמם לא משתנים.
# שימוש: python3 patch_stage_c.py <nlp dir> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
d, day, hm = sys.argv[1:4]
def patch(fn, pairs):
    p = os.path.join(d, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)

G0 = '''  var EXP="ap2_0811", K="nlp_go_"+EXP, v=null, o=null; try{ v=localStorage.getItem(K); o=localStorage.getItem("nlp_go_aap_0511"); }catch(e){}
  if(v!=="a5"&&v!=="pr2"){
    if(o==="a5"||o==="pr"){ v=(o==="pr"?"pr2":"a5"); }
    else { var A=["a5","pr2"]; try{ var r=new Uint8Array(1); crypto.getRandomValues(r); v=A[r[0]%2]; }catch(e){ v=A[Math.random()<0.5?0:1]; } }
    try{ localStorage.setItem(K,v); }catch(e){}
  }
'''
G1 = '''  /* ב68 שלב ג ("מאשר" מיהב, %s %s): ap2_0811 נסגר - a5v6 נקבע כדף המוביל (9 מתוך 96 הגיעו לסליקה, מול 0 מתוך 90 ב-pr2).
     כל התנועה שעוברת ב-go.html (כל המודעות והמשווקים) עוברת ל-a5v6, בלי הגרלה, עם exp=a5v6_1511. גם מי ששובץ קודם ל-pr2.
     pr2 ו-a5 נשארים באתר, מחוץ לחלוקה. השיבוץ השמור של ap2_0811 נשאר בדפדפן ולא נקרא */
  var EXP="a5v6_1511";
''' % (day[8:10] + "." + day[5:7], hm)
patch("go.html", [(G0, G1),
  ('''  location.replace((v==="a5"?"a5v6":v)+".html?"+q.toString()); /* a, a1-a4, b, c, a2/b2/c2, pr ו-pr_v1 נשארים באתר, מחוץ לניסוי */''',
   '''  location.replace("a5v6.html?"+q.toString()); /* a, a1-a5, b, c, a2/b2/c2, pr, pr_v1 ו-pr2 נשארים באתר, מחוץ לחלוקה */''')])

for fn in ("dashboard.html",):
    patch(fn, [
     ('''start:"2026-11-12",end:"",split:"50/50"''', '''start:"2026-11-12",end:"%s",status:"נסגר %s %s: a5v6 נקבע כדף המוביל (הגעה לסליקה 9/96 מול 0/90 ב-pr2, רכישות 0 מול 0 בשלב הזה). כל התנועה ל-a5v6 (exp=a5v6_1511)",split:"50/50"''' % (day, day[8:10] + "." + day[5:7], hm)),
     ('''const DECISIONS=[
''', '''const DECISIONS=[
 {at:"%s %s",detected:"ap2_0811 שלב 2 (מ-12.11 11:54, ממומן, לפי אנשים): a5v6 - 9 מתוך 96 הגיעו לסליקה, pr2 - 0 מתוך 90 (99%% ש-a5v6 מוביל). רכישות מאומתות: 0 מול 0 בשלב 2, 1 מול 1 בכל הניסוי",problem:"מתחת לסף של 300 לדף ו-20 רכישות, אבל יהב החליט לסגור לפי המדד הראשי",change:"go.html מפנה את כל התנועה ל-a5v6 (exp=a5v6_1511, בלי הגרלה). pr2 ו-a5 נשארים באתר מחוץ לחלוקה. a5v6 עצמו, דף התשלום (B מול B2), דף התודה והאפסייל - בלי שינוי",hyp:"a5v6 (v4 עם הרשימה של בן והכפתורים הירוקים) מביא יותר אנשים לסליקה",traffic:"live",result:"a5v6 מוביל בהגעה לסליקה; ברכישות אין עדיין הבדל",kept:"a5v6",next:"לעקוב אחרי הגעה לסליקה ורכישות ב-a5v6 מול התקופה הקודמת, מהשעה הזו"},
''' % (day, hm)),
     ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב68 שלב ג (\\"מאשר\\" מיהב): ap2_0811 נסגר. a5v6 נקבע כדף המוביל (הגעה לסליקה 9/96 מול 0/90 ב-pr2), וכל התנועה ב-go.html עוברת אליו עם exp=a5v6_1511, בלי הגרלה. pr2 ו-a5 נשארים באתר, מחוץ לחלוקה. בלי שינוי ב-a5v6, בדף התשלום, בדף התודה ובאפסייל. ההשוואה בלשונית 00 נעצרת בשעה הזו (ביקורים חדשים לא מסומנים ap2_0811)."],
''' % (day, hm))])
print("ok")
