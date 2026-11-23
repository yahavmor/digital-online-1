# ב103 (ראשי 16.11, "מאשר ב103" מיהב): שירה בלשונית המשווקים ובסיכום; on_1611 - טבלת סך הכול (בן + משווקים), שורת "נשארו דקה ומעלה", וכניסות בלי go.html מסומנות "מחוץ לניסוי".
# לא נוגעים ב-go.html, בדפים, בסליקה, ב-7827404 ובמודעות. המדד הראשי וכלל העצירה לא משתנים.
# שימוש: python3 patch_b103.py <repo root> (פעם על main ופעם על הענף; קובץ שהשינוי שלו כבר בפנים - להריץ רק על השני) "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
def patch(fn, pairs):
    p = os.path.join(root, fn)
    if not os.path.exists(p): print("skip", fn); return  # הלוח ב-main, הסקריפט היומי בענף
    s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:90], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
patch("nlp/dashboard.html", [
 # שירה
 ('''ads:["p25_yosef","g12_0466_a_yosef"]}]};''', '''ads:["p25_yosef","g12_0466_a_yosef"]},
 /* ב103 (16.11): שירה - קהל קר 25-55 בלי החרגות, 40 ₪ ליום, p25_brain_c2, פורסם 16.11 20:05. הוצאה במפתח aff_shira */
 {code:"shira",lbl:"שירה",aud:"קהל קר",copy:"p25_brain_c2",budget:40,from:"2026-11-16T20:05:00",day0:"2026-11-16",sw:null,noSwitch:"מ-16.11 20:05"}]};'''),
 # טבלאות on_1611
 ('''<div class="tw"><table id="onT"></table></div><div class="tw"><table id="onT2"></table></div></div>''',
  '''<div class="tw"><table id="onT"></table></div><div class="tw"><table id="onT2"></table></div><div class="tw"><table id="onT3"></table></div><p class="note" id="onOut"></p></div>'''),
 ('''const K=[["אנשים",s=>true],["הגיעו לדף התשלום",s=>s.chk||s.buy],["התחילו למלא",s=>s.cstart||s.det||s.pay||s.buy],["השאירו פרטים (מדד ראשי)",s=>s.det||s.pay||s.buy],["הגיעו לטופס התשלום",s=>s.pay||s.buy],["רכישות מאומתות",s=>s.buy]];''',
  '''const K=[["אנשים",s=>true],["נשארו דקה ומעלה",s=>(s.time||0)>=60],["הגיעו לדף התשלום",s=>s.chk||s.buy],["התחילו למלא",s=>s.cstart||s.det||s.pay||s.buy],["השאירו פרטים (מדד ראשי)",s=>s.det||s.pay||s.buy],["הגיעו לטופס התשלום",s=>s.pay||s.buy],["רכישות מאומתות",s=>s.buy]]; /* ב103: שורת "נשארו דקה ומעלה" (זמן בדף 60 שניות ומעלה) */'''),
 ('''table($("onT2"),["משווקים (בנפרד)",ARM.a,ARM.a5v6],aff.length?tab(aff):[],"עוד אין כניסות של משווקים בניסוי");''',
  '''table($("onT2"),["משווקים (בנפרד)",ARM.a,ARM.a5v6],aff.length?tab(aff):[],"עוד אין כניסות של משווקים בניסוי");
 const tot=all.filter(s=>(s.src==="מודעות Meta"&&!s.aff)||s.aff); /* ב103: סך הכול - המודעות של בן יחד עם המשווקים */
 table($("onT3"),["סך הכול: בן + משווקים",ARM.a,ARM.a5v6],tot.length?tab(tot):[],"עוד אין כניסות בניסוי");
 /* ב103: כניסות ישר לדף בלי go.html (בלי exp, לא אינסטגרם אורגני) - מחוץ לניסוי, לא נספרות בזרוע */
 const out=M.sess.filter(s=>(s.v==="a"||s.v==="a5v6")&&s.t>=ON_START&&s.p&&!s.p.get("exp")&&s.p.get("route")!=="ig_org"&&s.p.get("go")!=="1");
 const oc={};out.forEach(s=>{const c=s.aff&&AUD.camps.find(c=>c.code===s.aff),k=(s.aff?"משווק "+(c?c.lbl:s.aff):s.src)+" (דף "+s.v+")";(oc[k]=oc[k]||new Set()).add(who(s))});
 $("onOut").textContent="מחוץ לניסוי (נכנסו ישר לדף בלי go.html, לא נספרים בזרוע): "+(Object.keys(oc).length?Object.entries(oc).sort((x,y)=>y[1].size-x[1].size).map(([k,v])=>k+": "+v.size).join(" · "):"אין");'''),
 ('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב103 (\\"מאשר ב103\\" מיהב): שירה בלשונית המשווקים (aff=shira, קהל קר, 40 ₪ ליום, p25_brain_c2, מ-16.11 20:05, הוצאה aff_shira). בטבלת on_1611: טבלת סך הכול (בן + משווקים) ושורת \\"נשארו דקה ומעלה\\" לכל זרוע; כניסות ישר לדף בלי go.html (למשל המודעות של יוסף) מסומנות \\"מחוץ לניסוי\\" ולא נספרות בזרוע. המדד הראשי וכלל העצירה בלי שינוי."],
''' % (day, hm)),
])
patch("claude/daily/daily_0811.py", [
 ('''    if e=="checkout_payment_viewed": s["pay"]=1''', '''    if e=="checkout_payment_viewed": s["pay"]=1
    try: s["time"]=max(s.get("time",0),float(r.get("sec_on_page") or 0))  # ב103: זמן בדף
    except Exception: pass'''),
 ('''for lab,keep in (("paid",lambda s:s["src"]=="paid"),("aff",lambda s:s["src"]=="aff"),("all",lambda s:True)):
    E=[s for s in S.values() if s["exp"]=="on_1611" and s["v"] in("a","a5v6") and s["t"]>=ON and keep(s)]''',
  '''for lab,keep in (("paid",lambda s:s["src"]=="paid"),("aff",lambda s:s["src"]=="aff"),("ben+aff",lambda s:s["src"] in("paid","aff")),("all",lambda s:True)):  # ב103: ben+aff = סך הכול
    E=[s for s in S.values() if s["exp"]=="on_1611" and s["v"] in("a","a5v6") and s["t"]>=ON and keep(s)]'''),
 ('''        for f in ("chk","det","lead","pay","buy"): o[f]|=s.get(f,0)
    R3={v:{"people":len(P[v]),''', '''        for f in ("chk","det","lead","pay","buy"): o[f]|=s.get(f,0)
        o["min1"]|=int(s.get("time",0)>=60)
    R3={v:{"people":len(P[v]),"stayed_1min":sum(o["min1"] for o in P[v].values()),'''),
 ('''IG=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))''', '''OUT=defaultdict(set)  # ב103: ישר לדף בלי go.html - מחוץ לניסוי
for s in S.values():
    if s["v"] in("a","a5v6") and s["t"]>=ON and not s["exp"] and s["route"]!="ig_org" and "go=1" not in s["qs"]:
        OUT[(s["src"],s["v"])].add(s["vid"] or s["t"].isoformat())
print("b103 out of experiment (direct to page, no go.html):",{"%s/%s"%k:len(v) for k,v in sorted(OUT.items(),key=lambda kv:-len(kv[1]))})
IG=defaultdict(lambda: defaultdict(lambda: defaultdict(int)))'''),
])
print("ok")
