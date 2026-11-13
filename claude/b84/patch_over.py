# ב84 - תיקון בדיקת החריגה ("מאשר ב84 - תיקון חריגה", ראשי 13.11): "הוצאה מעל 120% מהתקציב" בלשונית 11 מחשבת את ההוצאה היומית של כל משווק
# באותה פונקציה של לשונית 10 (audSegDays), כך שנכנסים גם rachel_cold18 ו-rachel_g12 (AUD_X), וההוצאה של יוסף לפי מודעה בלי ספירה כפולה עם aff_yosef.
# audSpend של לשונית 10 עובר להשתמש באותה פונקציה - בלי שינוי בתוצאה. משווק בלי שורה בלשונית 10: aff_<קוד> + aff_<קוד>_ic כמו קודם.
# שימוש: python3 patch_over.py <dashboard.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)
rep('''function audSpend(g){if(g.nospend)return null;const A=(g.ads||[]).map(x=>x.toLowerCase()),byD={},adD={};for(const k in cspend){const [d,cc]=k.split("|");if(!cc||d<g.sday)continue;const c=cc.toLowerCase();
  if(A.includes(c)){adD[d]=(adD[d]||0)+cspend[k]}else if(cc===g.spk||(g.xspk||[]).includes(cc)){byD[d]=(byD[d]||0)+cspend[k]}}
 for(const d in adD)byD[d]=adD[d]; /* ב86: ביום עם הוצאה לפי מודעה - רק סכום המודעות, כדי לא לספור פעמיים */
 const ds=Object.keys(byD);return ds.length?{t:ds.reduce((x,d)=>x+byD[d],0),days:ds.length}:null}
''', '''/* הוצאה יומית של שורה בלשונית 10 ({תאריך: סכום}). משמשת את לשונית 10 ואת בדיקת החריגה בלשונית 11 (ב84) */
function audSegDays(g){if(g.nospend)return null;const A=(g.ads||[]).map(x=>x.toLowerCase()),byD={},adD={};for(const k in cspend){const [d,cc]=k.split("|");if(!cc||d<g.sday)continue;const c=cc.toLowerCase();
  if(A.includes(c)){adD[d]=(adD[d]||0)+cspend[k]}else if(cc===g.spk||(g.xspk||[]).includes(cc)){byD[d]=(byD[d]||0)+cspend[k]}}
 for(const d in adD)byD[d]=adD[d]; /* ב86: ביום עם הוצאה לפי מודעה - רק סכום המודעות, כדי לא לספור פעמיים */
 return byD}
function audSpend(g){const byD=audSegDays(g);if(!byD)return null;const ds=Object.keys(byD);return ds.length?{t:ds.reduce((x,d)=>x+byD[d],0),days:ds.length}:null}
/* הוצאה יומית של משווק: סכום השורות שלו בלשונית 10 (המפתחות שלהן שונים, אז אין כפילות). בלי שורה בלשונית 10 - aff_<קוד> + aff_<קוד>_ic */
function affDaySpend(code){const S=AUD.seg.filter(g=>g.code===code),o={};
 if(!S.length){for(const k in cspend){const [d,c]=k.split("|");if(c==="aff_"+code||c==="aff_"+code+"_ic")o[d]=(o[d]||0)+cspend[k]}return o}
 S.forEach(g=>{const D=audSegDays(g);if(D)for(const d in D)o[d]=(o[d]||0)+D[d]});return o}
''')
rep('''const over={};for(const k in cspend){const [d,c]=k.split("|");if(c!=="aff_"+code&&c!=="aff_"+code+"_ic")continue;const dt=new Date(d+"T12:00");if(dt<B.a||dt>=B.b)continue;over[d]=(over[d]||0)+cspend[k]}''',
    '''const over={},ad=affDaySpend(code);for(const d in ad){const dt=new Date(d+"T12:00");if(dt<B.a||dt>=B.b)continue;over[d]=ad[d]} /* ב84: אותה הוצאה כמו בלשונית 10 */''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
