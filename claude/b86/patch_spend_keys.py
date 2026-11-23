# ב86 (ראשי 12.11 18:24): 2 מפתחות הוצאה חסרים בטופס הקמפיינים (לשונית 10): סדרת ה-IC של גל (aff_gal_ic) ו-COLD_18 של רחל (aff_rachel_cold18).
# בלי שינוי אחר: לגל אין עדיין שעת מעבר (sw:null), ולכן ההוצאה של ה-IC נספרת בשורה של גל עד שתימסר. COLD_18 רץ אצל רחל אחרי המעבר, ולכן נספר בשורת "אחרי" שלה.
# שימוש: python3 patch_spend_keys.py <dashboard.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)
rep('''function audSpend(g){let t=0,days=0;for(const k in cspend){const [d,cc]=k.split("|");if(cc===g.spk&&d>=g.sday){t+=cspend[k];days++}}return days?{t,days}:null}''',
'''/* ב86 (12.11): מפתחות הוצאה נוספים לקמפיין שכבר קיים בטבלה. גל - סדרת IC, נספרת בשורה של גל עד שתימסר שעת המעבר; רחל - COLD_18, נספר בשורת "אחרי" שלה */
const AUD_X=[{key:"gal|pre",spk:"aff_gal_ic",lbl:"גל",phl:"סדרת IC (מעבר לתשלום)",aud:"נספרת בשורה של גל עד שתימסר שעת המעבר"},{key:"rachel|post",spk:"aff_rachel_cold18",lbl:"רחל",phl:"קמפיין COLD_18",aud:"נספר בשורת \\"אחרי\\" של רחל"}];
AUD_X.forEach(x=>{const g=AUD.seg.find(s=>s.key===x.key);if(g)(g.xspk=g.xspk||[]).push(x.spk)});
function audSpend(g){let t=0;const D=new Set();for(const k in cspend){const [d,cc]=k.split("|");if((cc===g.spk||(g.xspk||[]).includes(cc))&&d>=g.sday){t+=cspend[k];D.add(d)}}return D.size?{t,days:D.size}:null}''')
rep('''const sel=$("audSpCamp");if(sel.options.length!==AUD.seg.length)sel.innerHTML=AUD.seg.map(g=>'<option value="'+g.spk.slice(4)+'">'+esc(g.lbl+" · "+g.phl+" · "+g.aud)+'</option>').join("");''',
'''const sel=$("audSpCamp");if(sel.options.length!==AUD.seg.length+AUD_X.length)sel.innerHTML=AUD.seg.concat(AUD_X).map(g=>'<option value="'+g.spk.slice(4)+'">'+esc(g.lbl+" · "+g.phl+" · "+g.aud)+'</option>').join("");''')
rep('''cc=AUD.seg.find(x=>x.spk===c);''', '''cc=AUD.seg.concat(AUD_X).find(x=>x.spk===c);''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
