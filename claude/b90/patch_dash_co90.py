# ב90: טבלת B מול B2 בדף התשלום (co_b2_1311) בלשונית הסליקה - לפי אנשים, בכל דף מכירה בנפרד, ושורה ביומן.
# שימוש: python3 patch_dash_co90.py <dashboard.html> <out> "<YYYY-MM-DD>" "<HH:MM>"   (זמן הפריסה של B2, לשורת היומן)
import sys
src, out, day, hm = sys.argv[1:5]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)

rep('''    <div class="panel"><div class="panel-h"><h2>דף תשלום 1 מול דף תשלום 2 - לפי אנשים (ב54)</h2>''',
    '''    <div class="panel"><div class="panel-h"><h2>דף תשלום B מול B2 - לפי אנשים, בכל דף מכירה (ב90)</h2><span class="note" id="co90N"></span></div><div class="tw"><table id="co90"></table></div></div>
    <div class="panel"><div class="panel-h"><h2>דף תשלום 1 מול דף תשלום 2 - לפי אנשים (ב54)</h2>''')

rep('''
/* ב51: abandoned checkouts''', '''
/* ב90: B מול B2 (co_b2_1311) - חצי-חצי לכל מכשיר בדף התשלום, ולכן חצי-חצי בתוך כל דף מכירה. לפי אנשים (מכשיר), כל מקורות התנועה, בלי בדיקות */
const CO90_N=100;
function renderCo90(M){const who=s=>s.vid||s.sid,S=M.sess.filter(s=>(s.co==="b"||s.co==="b2")&&s.ev.some(r=>parseX(r.x).cx==="co_b2_1311"));
 const K=[["הגיעו לדף התשלום",s=>s.chk||s.buy],["התחילו למלא",s=>s.cstart||s.det||s.pay||s.buy],["הגיעו לטופס התשלום (קארדקום נטען)",s=>s.pay||s.buy],["רכישה מאומתת",s=>s.buy]];
 const PG=[["a5v6","a5v6"],["pr2","pr2"],["*","כל הדפים"]],C=[["b","B"],["b2","B2"]],P={};
 PG.forEach(([g])=>C.forEach(([c])=>{P[g+"|"+c]=K.map(()=>new Set())}));
 S.forEach(s=>{[s.v==="a5v6"||s.v==="pr2"?s.v:null,"*"].forEach(g=>{if(!g)return;const o=P[g+"|"+s.co];K.forEach(([,f],i)=>{if(f(s))o[i].add(who(s))})})});
 const cols=PG.flatMap(([g,gl])=>C.map(([c,cl])=>[g+"|"+c,gl+" · "+cl]));
 const rows=K.map(([l],i)=>'<tr><td>'+l+'</td>'+cols.map(([k])=>{const v=P[k][i].size,n=P[k][0].size;return '<td class="num">'+fmt(v)+(i?'<small>'+pf(pct(v,n))+'</small>':'')+'</td>'}).join("")+'</tr>');
 table($("co90"),["לפי אנשים"].concat(cols.map(([,l])=>esc(l))),S.length?rows:[],"עוד אין כניסות בניסוי B מול B2 (מתחיל בפריסה)");
 const nB=P["*|b"][0].size,nB2=P["*|b2"][0].size,ready=nB>=CO90_N&&nB2>=CO90_N;
 $("co90N").innerHTML=(ready?'':'<span class="pill warn">ראשוני</span> ')+'הגרלה חצי-חצי בדף התשלום, קבועה למכשיר (cx=co_b2_1311). B2 = B עם עוגן מחיר, שורת אחריות ושלבים 1-2. אחוזים מתוך מי שהגיע לדף התשלום באותה עמודה. בודקים אחרי כ-'+CO90_N+' שהגיעו בכל גרסה: עכשיו B '+nB+', B2 '+nB2+'.'}

/* ב51: abandoned checkouts''')

rep('''renderCo54(M)},''', '''renderCo90(M);renderCo54(M)},''')

rep('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב90: ניסוי בדף התשלום B מול B2 (cx=co_b2_1311): חצי-חצי לכל מכשיר, ולכן חצי-חצי בתוך כל דף מכירה (a5v6, pr2), והדפים עצמם לא השתנו. B2 = B עם 1,290 ₪ מחוק ליד 297 ₪ ו\\"מחיר השקה לזמן מוגבל\\", שורת אחריות של 7 ימים מתחת למחיר, \\"שלב 1 מתוך 2\\" / \\"שלב 2 מתוך 2\\", ופרטי העסקה עם Apple Pay ו-Google Pay. באירועים co=b או co=b2. טבלה חדשה בלשונית הסליקה, ובודקים אחרי כ-100 שהגיעו בכל גרסה."],
''' % (day, hm))
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
