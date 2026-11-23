# ב74 השקה ("מאשר ב74 - השקה", ראשי 14.11): הקישור מדף התודה לאפסייל.
# מחליף את thanks_b74.patch: זה ציפה ש-7931441 יחזיר up, אבל 7931441 לא שונה אף פעם. במקום זה הדף פונה ישירות ל-8463664
# (hook 4068820) עם אותו lookup_lp, אחרי שהאימות של הקורס הצליח. 8463664 מאמת בעצמו מול קארדקום, דורש את רשומת הקורס ב-210157
# (נכתבת ב-7827404, ולכן עד 5 ניסיונות, כל 3 שניות) ומחזיר {"up":"<32>"} רק בתוך 30 הדקות מהרכישה.
# רק בחלון הראשי (לא בתוך ה-iframe של קארדקום), לא בחזרה מהאפסייל (?ups=1), ופעם אחת לכל קוד בלשונית. כפתור הכניסה לקורס כבר מוצג.
# שימוש: python3 patch_thanks_upsell.py <thanks.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old)); s = s.replace(old, new, 1)
rep('''    const VERIFY = "https://hook.eu1.make.com/s9ay2kp6sldk9527d77seuuq83xxto60";''',
    '''    const VERIFY = "https://hook.eu1.make.com/s9ay2kp6sldk9527d77seuuq83xxto60";
    const UPSELL_ISSUE = "https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd"; /* ב74: 8463664 - קוד חד-פעמי לאפסייל אחרי תשלום מאומת */''')
rep('''      const a = el("go"); a.href = d.link; a.hidden = false; el("wait").hidden = true;
''', '''      const a = el("go"); a.href = d.link; a.hidden = false; el("wait").hidden = true;
      upsell(0);
''')
rep('''    function ask(n){''', '''    /* ב74: הצעת האפסייל. ההמתנה של 1.5 שניות נותנת ל-Purchase ולאירועי הדף להישלח לפני המעבר */
    let upFired = false;
    function upsell(n){
      if(framed || !lp || qs.has("ups") || (n === 0 && upFired)) return; upFired = true;
      const retry = () => { if(n < 4) setTimeout(() => upsell(n + 1), 3000); };
      fetch(UPSELL_ISSUE, {method:"POST", body:new URLSearchParams({lookup_lp: lp})})
        .then(r => r.json()).then(u => {
          const t = u && typeof u.up === "string" ? u.up : "";
          if(!/^[A-Za-z0-9]{32}$/.test(t)) return retry();
          let seen = false; try{ seen = sessionStorage.getItem("ups_seen") === t; sessionStorage.setItem("ups_seen", t); }catch(e){}
          if(!seen) setTimeout(() => { location.href = "upsell-97.html?t=" + t; }, 1500);
        }).catch(retry);
    }
    function ask(n){''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
