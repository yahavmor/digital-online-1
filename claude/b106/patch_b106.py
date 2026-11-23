# ב106 (18.11): שאלה שלישית בדף התודה - טווח גיל (לא חובה), ועמודת גיל בלשונית 14 "פרופיל רוכשים".
# שימוש: python3 patch_b106.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
def patch(path, pairs):
    p = os.path.join(root, path); s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:80], s.count(a)); s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
AGES = [("a18_24","18-24"),("a25_34","25-34"),("a35_44","35-44"),("a45_54","45-54"),("a55_64","55-64"),("a65p","65+")]
btn = "".join('<button type="button" data-a="%s">%s</button>' % a for a in AGES)
patch("nlp/thanks.html", [
 ('<h2 id="srvH">2 שאלות קצרות, לא חובה</h2>', '<h2 id="srvH">3 שאלות קצרות, לא חובה</h2>'),
 ('<button type="button" data-a="youtube_google">יוטיוב או גוגל</button><button type="button" data-a="other">אחר</button></div>\n </fieldset>\n',
  '<button type="button" data-a="youtube_google">יוטיוב או גוגל</button><button type="button" data-a="other">אחר</button></div>\n </fieldset>\n'
  ' <fieldset id="srvQ3"><legend>מה טווח הגיל שלך?</legend><div class="ch">\n  ' + btn + '</div>\n </fieldset>\n'),
 ('cta = q1 (מה שכנע) או q2 (איפה שמע)', 'cta = q1 (מה שכנע), q2 (איפה שמע) או q3 (טווח גיל, ב106)'),
 ('const fin = () => { if(done("q1") && done("q2")) el("srvTy").hidden = false; };', 'const fin = () => { if(done("q1") && done("q2") && done("q3")) el("srvTy").hidden = false; };'),
 ('[["q1", "srvQ1"], ["q2", "srvQ2"]].forEach(', '[["q1", "srvQ1"], ["q2", "srvQ2"], ["q3", "srvQ3"]].forEach('),
 ('if(done("q1") && done("q2")) return; box.hidden = false;', 'if(done("q1") && done("q2") && done("q3")) return; box.hidden = false;'),
])
q3 = ",".join('%s:"%s"' % a for a in AGES)
patch("nlp/dashboard.html", [
 (' PR_Q2={facebook:"פייסבוק",instagram:"אינסטגרם",friend_aff:"חבר או משווק",youtube_google:"יוטיוב או גוגל",other:"אחר"},',
  ' PR_Q2={facebook:"פייסבוק",instagram:"אינסטגרם",friend_aff:"חבר או משווק",youtube_google:"יוטיוב או גוגל",other:"אחר"},\n PR_Q3={' + q3 + '},  /* ב106: טווח גיל */'),
 ('if(r.ev!=="buyer_survey"||!/^q[12]$/.test(r.cta||""))return;', 'if(r.ev!=="buyer_survey"||!/^q[123]$/.test(r.cta||""))return;'),
 ("'</td><td>'+prAns(an.q1,PR_Q1)+'</td><td>'+prAns(an.q2,PR_Q2)+'</td></tr>'", "'</td><td>'+prAns(an.q1,PR_Q1)+'</td><td>'+prAns(an.q2,PR_Q2)+'</td><td>'+prAns(an.q3,PR_Q3)+'</td></tr>'"),
 ('"משווק","מה שכנע","איפה שמע"],body,', '"משווק","מה שכנע","איפה שמע","גיל"],body,'),
 (' שאלות דף התודה נוספו ב-ב81, ולרכישות מלפני כן אין תשובות.";', ' שאלות דף התודה נוספו ב-ב81 (שאלת הגיל ב-ב106), ולרכישות מלפני כן אין תשובות.";'),
 ('const c1=cnt("q1",PR_Q1),c2=cnt("q2",PR_Q2),n1=c1.reduce((x,y)=>x+y[1],0),n2=c2.reduce((x,y)=>x+y[1],0),rows2=[];',
  'const c1=cnt("q1",PR_Q1),c2=cnt("q2",PR_Q2),c3=cnt("q3",PR_Q3),n1=c1.reduce((x,y)=>x+y[1],0),n2=c2.reduce((x,y)=>x+y[1],0),n3=c3.reduce((x,y)=>x+y[1],0),rows2=[];'),
 ("for(let i=0;i<Math.max(c1.length,c2.length);i++){const a=c1[i],b=c2[i];rows2.push('<tr><td>'+(a?esc(a[0]):\"\")+'</td><td class=\"num\">'+(a?fmt(a[1])+(n1?'<small>'+pf(pct(a[1],n1))+'</small>':''):\"\")+'</td><td>'+(b?esc(b[0]):\"\")+'</td><td class=\"num\">'+(b?fmt(b[1])+(n2?'<small>'+pf(pct(b[1],n2))+'</small>':''):\"\")+'</td></tr>')}",
  "for(let i=0;i<Math.max(c1.length,c2.length,c3.length);i++){const a=c1[i],b=c2[i],g=c3[i];rows2.push('<tr><td>'+(a?esc(a[0]):\"\")+'</td><td class=\"num\">'+(a?fmt(a[1])+(n1?'<small>'+pf(pct(a[1],n1))+'</small>':''):\"\")+'</td><td>'+(b?esc(b[0]):\"\")+'</td><td class=\"num\">'+(b?fmt(b[1])+(n2?'<small>'+pf(pct(b[1],n2))+'</small>':''):\"\")+'</td><td>'+(g?esc(g[0]):\"\")+'</td><td class=\"num\">'+(g?fmt(g[1])+(n3?'<small>'+pf(pct(g[1],n3))+'</small>':''):\"\")+'</td></tr>')}"),
 ('table($("prAns"),["מה שכנע ("+n1+" ענו)","רוכשים","איפה שמע לראשונה ("+n2+" ענו)","רוכשים"],n1||n2?rows2:[],"עוד אין תשובות");',
  'table($("prAns"),["מה שכנע ("+n1+" ענו)","רוכשים","איפה שמע לראשונה ("+n2+" ענו)","רוכשים","טווח גיל ("+n3+" ענו)","רוכשים"],n1||n2||n3?rows2:[],"עוד אין תשובות");'),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב106: שאלה שלישית בדף התודה - טווח גיל (לא חובה, 18-24 עד 65+), נשמרת כמו שתי השאלות של ב81 (buyer_survey, cta=q3, בלי פרטים מזהים). בלשונית 14 נוספה עמודת גיל וספירה לפי טווח."],\n' % (day, hm)),
])
print("ok")
