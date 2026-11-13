# ב86 (ראשי 13.11 08:43, "מאשר ב86 - פריסה ותיקון"): מעל patch_spend_keys.py.
# 1. aff_rachel_g12 - אצל רחל ב"אחרי", כמו COLD_18.
# 2. יוסף (aff=yosef) - שורה חדשה בלשונית 10 מ-12.11 21:44, קהל קר, 40 ₪ ליום, להשוואה בין 2 סרטונים.
#    הוצאה בלי ספירה כפולה: לפי מודעה נשמר במפתח של קוד המודעה (תאריך|p25_yosef, תאריך|g12_0466_a_yosef), כמו הוצאה לפי מודעה אצל בן.
#    aff_yosef = סה"כ הקמפיין, נספר רק ביום שאין לו הוצאה לפי מודעה. ביום שיש - השורה של יוסף = סכום המודעות. הסה"כ של בן (מפתח תאריך בלבד) לא כולל את יוסף.
#    בטבלת הסרטונים: הוצאה ועלות לרכישה לכל סרטון של יוסף.
# 3. טופס: הערך של כל אפשרות הוא המפתח המלא; שמירה בלי שם משווק (aff_ ריק) נחסמת, גם בטופס ההוצאה הכללי.
# שימוש: python3 patch_spend_keys2.py <dashboard אחרי patch_spend_keys.py> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)

# יוסף בקמפיינים
rep('''{code:"yahel",lbl:"יהל",aud:"קהל קר",copy:"p25_brain_c3",budget:40,from:"2026-11-09T21:00:00",day0:"2026-11-09",sw:"2026-11-10T10:27:00"}]};''',
    '''{code:"yahel",lbl:"יהל",aud:"קהל קר",copy:"p25_brain_c3",budget:40,from:"2026-11-09T21:00:00",day0:"2026-11-09",sw:"2026-11-10T10:27:00"},
 /* ב86/ב87 (13.11): יוסף - קמפיין חדש להשוואה בין 2 סרטונים. הוצאה לפי מודעה במפתחות הסרטונים (ads); aff_yosef רק ביום בלי הוצאה לפי מודעה */
 {code:"yosef",lbl:"יוסף",aud:"קהל קר",copy:["p25_yosef","g12_0466_a_yosef"],budget:40,from:"2026-11-12T21:44:00",day0:"2026-11-12",sw:null,noSwitch:"מ-12.11 21:44",ph0:"השוואת 2 סרטונים",ads:["p25_yosef","g12_0466_a_yosef"]}]};''')
rep('''pre=Object.assign({},c,{key:c.code+"|pre",ph:"pre",phl:"לפני · רכישה"''', '''pre=Object.assign({},c,{key:c.code+"|pre",ph:"pre",phl:c.ph0||"לפני · רכישה"''')

# רחל G12 + מודעות יוסף בטופס
rep('''{key:"rachel|post",spk:"aff_rachel_cold18",lbl:"רחל",phl:"קמפיין COLD_18",aud:"נספר בשורת \\"אחרי\\" של רחל"}];''',
    '''{key:"rachel|post",spk:"aff_rachel_cold18",lbl:"רחל",phl:"קמפיין COLD_18",aud:"נספר בשורת \\"אחרי\\" של רחל"},{key:"rachel|post",spk:"aff_rachel_g12",lbl:"רחל",phl:"קמפיין G12",aud:"נספר בשורת \\"אחרי\\" של רחל"}];
const AUD_ADS=[];AUD.seg.forEach(g=>(g.ads||[]).forEach(a=>AUD_ADS.push({key:g.key,spk:a,lbl:g.lbl,phl:"מודעה "+a,aud:"הוצאה לפי מודעה (בלי aff_)"})));''')

# הוצאה: ביום עם הוצאה לפי מודעה - סכום המודעות; אחרת המפתח של הקמפיין
rep('''function audSpend(g){let t=0;const D=new Set();for(const k in cspend){const [d,cc]=k.split("|");if((cc===g.spk||(g.xspk||[]).includes(cc))&&d>=g.sday){t+=cspend[k];D.add(d)}}return D.size?{t,days:D.size}:null}''',
    '''function audSpend(g){const A=(g.ads||[]).map(x=>x.toLowerCase()),byD={},adD={};for(const k in cspend){const [d,cc]=k.split("|");if(!cc||d<g.sday)continue;const c=cc.toLowerCase();
  if(A.includes(c)){adD[d]=(adD[d]||0)+cspend[k]}else if(cc===g.spk||(g.xspk||[]).includes(cc)){byD[d]=(byD[d]||0)+cspend[k]}}
 for(const d in adD)byD[d]=adD[d]; /* ב86: ביום עם הוצאה לפי מודעה - רק סכום המודעות, כדי לא לספור פעמיים */
 const ds=Object.keys(byD);return ds.length?{t:ds.reduce((x,d)=>x+byD[d],0),days:ds.length}:null}
function audAdSpend(g,ad){if(!(g.ads||[]).some(x=>x.toLowerCase()===String(ad).toLowerCase()))return null;let t=0,n=0;for(const k in cspend){const [d,cc]=k.split("|");if(cc&&d>=g.sday&&cc.toLowerCase()===String(ad).toLowerCase()){t+=cspend[k];n++}}return n?t:null}''')

# אפשרויות הטופס: הערך = המפתח המלא
rep('''const sel=$("audSpCamp");if(sel.options.length!==AUD.seg.length+AUD_X.length)sel.innerHTML=AUD.seg.concat(AUD_X).map(g=>'<option value="'+g.spk.slice(4)+'">'+esc(g.lbl+" · "+g.phl+" · "+g.aud)+'</option>').join("");''',
    '''const sel=$("audSpCamp"),OPT=AUD.seg.concat(AUD_X,AUD_ADS);if(sel.options.length!==OPT.length)sel.innerHTML=OPT.map(g=>'<option value="'+esc(g.spk)+'">'+esc(g.lbl+" · "+g.phl+" · "+g.aud)+'</option>').join("");''')
rep('''cc=AUD.seg.concat(AUD_X).find(x=>x.spk===c);''', '''cc=AUD.seg.concat(AUD_X,AUD_ADS).find(x=>x.spk===c);''')
rep('''const ks=Object.keys(cspend).filter(k=>/\\|aff_/.test(k)&&k.split("|")[0]>=AUD.day0).sort().reverse();''',
    '''const ks=Object.keys(cspend).filter(k=>(/\\|aff_/.test(k)||AUD_ADS.some(a=>a.spk===k.split("|")[1]))&&k.split("|")[0]>=AUD.day0).sort().reverse();''')
rep('''c="aff_"+$("audSpCamp").value,a=$("audSpAmt").value;if(!d||a==="")return;''',
    '''c=$("audSpCamp").value,a=$("audSpAmt").value;if(!d||a==="")return;if(!c||/^aff_?$/i.test(c)){$("audSpState").textContent="בחרו קמפיין - לא נשמר בלי שם משווק";return}''')
rep('''c=($("spCr").value||"").replace(/[|\\s]/g,"");if(!d||a==="")return;''',
    '''c=($("spCr").value||"").replace(/[|\\s]/g,"");if(!d||a==="")return;if(/^aff_?$/i.test(c)){$("spendState").textContent="חסר שם משווק אחרי aff_ - לא נשמר";return}''')

# טבלת הסרטונים: שם מהמילון, והוצאה ועלות לרכישה לסרטונים של יוסף
rep('''table($("audVid"),["קמפיין","סרטון","קופי","כניסות","הגיעו לסליקה","רכישות"],rowsV,"אין עדיין כניסות מהקמפיינים");''',
    '''table($("audVid"),["קמפיין","סרטון","קופי","כניסות","הגיעו לסליקה","רכישות","הוצאה","עלות לרכישה"],rowsV,"אין עדיין כניסות מהקמפיינים");''')
rep('''rowsV.push('<tr><td>'+esc(o.c.lbl)+' · '+esc(o.c.phl)+' · '+esc(o.c.aud)+'</td><td>'+(i.named?'<b>'+esc(i.name)+'</b>':'<b>'+esc(k||"(בלי קוד סרטון)")+'</b><small>לא בטבלת המעבדה</small>')+'</td><td>'+esc(i.copy||"-")+'</td><td class="num">'+fmt(r.ppl.size)+'</td>'+cell(r.chk.size,r.ppl.size)+'<td class="num">'+fmt(r.deals.size)+'</td></tr>')''',
    '''const asp=o.c.ads?audAdSpend(o.c,k):null,dn=(typeof ADS!=="undefined"&&ADS[String(k).toLowerCase()])||null;rowsV.push('<tr><td>'+esc(o.c.lbl)+' · '+esc(o.c.phl)+' · '+esc(o.c.aud)+'</td><td>'+(i.named?'<b>'+esc(i.name)+'</b>':dn?'<b title="קוד: '+esc(k)+'">'+esc(dn.name)+'</b>':'<b>'+esc(k||"(בלי קוד סרטון)")+'</b><small>לא בטבלת המעבדה</small>')+'</td><td>'+esc(i.copy||"-")+'</td><td class="num">'+fmt(r.ppl.size)+'</td>'+cell(r.chk.size,r.ppl.size)+'<td class="num">'+fmt(r.deals.size)+'</td><td>'+(o.c.ads?(asp!=null?ils(asp):noData("לא הוזנה הוצאה למודעה")):'<span class="na">-</span>')+'</td><td>'+(o.c.ads&&asp!=null?(r.deals.size?ils(asp/r.deals.size):noData("אין רכישות")):'<span class="na">-</span>')+'</td></tr>')''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
