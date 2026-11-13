# ב89 - שורת לוגואים של אמצעי התשלום (בקשת יהב דרך הראשי, 13.11). מקומי בלבד, פריסה רק אחרי "מאשר".
#  - דף התשלום: גרסה ב' - בראש "פרטי תשלום" (המסגרת גלויה מההתחלה). גרסה א' - מעל כפתור "המשך לתשלום מאובטח",
#    כי שם "פרטי תשלום" נפתח רק אחרי הכפתור. כך בשתי הגרסאות השורה גלויה לפני מילוי הפרטים.
#  - a5v6 ו-pr2: מתחת לכפתור הראשי (hero_main) ומתחת לכפתור באזור המחיר (offer). אותו קטע בדיוק בשני הדפים.
#  - ביט: מוסתר עד שיהב מאמת בטלפון שכפתור הביט מופיע (bit_url לא ריק). ההפעלה: PAYLOGO_BIT=true בשלושת הדפים יחד.
#  - דפדפן פנימי של אינסטגרם/פייסבוק: Apple Pay ו-Google Pay לא נתמכים שם (WKWebView / WebView), אז הלוגואים שלהם מוסתרים
#    ומוצג רמז קצר (הנוסח ממתין לאישור).
# שימוש: python3 patch_paylogos.py <nlp dir מקור> <nlp dir יעד>
import sys, os, shutil
SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))

CSS = '''<style>/* ב89: שורת אמצעי תשלום. גבהים שווים, Apple Pay ראשון (מימין), רווח של 8px לפחות סביב כל סימן */
.paylogos{margin:10px auto 0;text-align:center;max-width:420px}
.paylogos .pl-row{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none;direction:rtl}
.paylogos .pl-row li{display:block;line-height:0}
.paylogos .pl-row li[hidden]{display:none}
.paylogos img{display:block;height:26px;width:auto}
.paylogos .pl-t{margin:6px 0 0;font-size:13.5px;line-height:1.4;font-weight:500;opacity:.78}
.paylogos .pl-h{margin:3px 0 0;font-size:13px;line-height:1.4;font-weight:600;opacity:.9}
.paylogos .pl-h[hidden]{display:none}
</style>
'''

def block(where, lazy):
    L = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    return ('<div class="paylogos" data-paylogos="%s"><ul class="pl-row" aria-hidden="true">'
            '<li data-pl="apple"><img src="assets/pay/apple-pay-mark.svg" alt="" width="41" height="26"%s></li>'
            '<li data-pl="google"><img src="assets/pay/google-pay-mark.svg" alt="" width="49" height="26"%s></li>'
            '<li data-pl="bit" hidden><img src="assets/pay/bit-mark.svg" alt="" width="41" height="26"%s></li>'
            '<li data-pl="card"><img src="assets/pay/card.svg" alt="" width="41" height="26"%s></li></ul>'
            '<p class="pl-t">אפשר לשלם ב-<bdi>Apple Pay</bdi>, <bdi>Google Pay</bdi> או אשראי</p><p class="pl-h" hidden></p></div>') % (where, L, L, L, L)

JS = '''<script>/* ב89: שורת אמצעי תשלום - ביט רק אחרי אימות, ובדפדפן פנימי של אינסטגרם/פייסבוק בלי Apple Pay ו-Google Pay */
(function(){var PAYLOGO_BIT=false;
var ua=navigator.userAgent||"",inapp=/Instagram|FBAN|FBAV|FB_IAB|FBIOS|FB4A|FBAN\\/Messenger/i.test(ua),ios=/iPhone|iPad|iPod/i.test(ua)||(/Macintosh/i.test(ua)&&navigator.maxTouchPoints>1),and=/Android/i.test(ua);
var els=document.querySelectorAll("[data-paylogos]");for(var i=0;i<els.length;i++){var el=els[i],p=[];
 function show(k,on){var li=el.querySelector('[data-pl="'+k+'"]');if(li)li.hidden=!on}
 show("apple",!inapp);show("google",!inapp);show("bit",PAYLOGO_BIT);
 if(!inapp){p.push("\u2066Apple Pay\u2069","\u2066Google Pay\u2069")} /* בידוד כיווניות, כדי שהשמות באנגלית לא יהפכו את סדר המשפט */if(PAYLOGO_BIT)p.push("ביט");
 var t=el.querySelector(".pl-t"),h=el.querySelector(".pl-h");
 t.textContent=inapp?(PAYLOGO_BIT?"אפשר לשלם בביט או באשראי":"אפשר לשלם באשראי"):"אפשר לשלם ב-"+p.join(", ")+" או אשראי";
 if(inapp){h.textContent=ios?"ל-\u2066Apple Pay\u2069 פתחו את הדף בספארי":and?"ל-\u2066Google Pay\u2069 פתחו את הדף בכרום":"ל-\u2066Apple Pay\u2069 או \u2066Google Pay\u2069 פתחו את הדף בדפדפן";h.hidden=false}
 el.setAttribute("data-inapp",inapp?"1":"0")}
})();</script>
'''

def rep(s, old, new, name):
    assert s.count(old) == 1, (name, old[:80], s.count(old))
    return s.replace(old, new, 1)

def head(s, name):
    # ה-CSS לפני </head>
    return rep(s, '</head>', CSS + '</head>', name + ':css')

def tail(s, name):
    return rep(s, '</body>', JS + '</body>', name + ':js')

os.makedirs(OUT, exist_ok=True)

# דף התשלום
n = 'checkout.html'; s = open(os.path.join(SRC, n), encoding='utf8').read()
s = head(s, n)
s = rep(s, '<p class="paytitle">פרטי תשלום<span>🔒 התשלום מאובטח באמצעות Cardcom</span></p>\n',
        '<p class="paytitle">פרטי תשלום<span>🔒 התשלום מאובטח באמצעות Cardcom</span></p>\n' + block('co_pay', False) + '\n', n)
s = rep(s, '<button class="go" type="submit"><span>המשך לתשלום מאובטח',
        block('co_det', False) + '\n<button class="go" type="submit"><span>המשך לתשלום מאובטח', n)
s = rep(s, '.cohold .note{', '''html[data-co="b"] #det .paylogos,html:not([data-co="b"]) #paySec .paylogos{display:none} /* ב89: ב' בראש "פרטי תשלום", א' מעל כפתור ההמשך */
#paySec .paylogos{margin:0 auto 12px}
#det .paylogos{margin:4px auto 12px}
.cohold .note{''', n)
s = tail(s, n)
open(os.path.join(OUT, n), 'w', encoding='utf8').write(s)

# a5v6
n = 'a5v6.html'; s = open(os.path.join(SRC, n), encoding='utf8').read()
s = head(s, n)
HERO_A = 'data-cta="hero_main" data-checkout href="#">'
i = s.index(HERO_A); j = s.index('</a>', i) + 4
assert s.count(HERO_A) == 1
s = s[:j] + '\n' + block('hero', False) + s[j:]
OFF_A = 'data-cta="offer" data-checkout href="#">'
assert s.count(OFF_A) == 1
i = s.index(OFF_A); j = s.index('</a>', i) + 4
s = s[:j] + '\n' + block('offer', True) + s[j:]
s = tail(s, n)
open(os.path.join(OUT, n), 'w', encoding='utf8').write(s)

# pr2
n = 'pr2.html'; s = open(os.path.join(SRC, n), encoding='utf8').read()
s = head(s, n)
s = rep(s, '<a class="cta" data-cta="hero_main" data-checkout href="checkout.html">אני רוצה ללמוד איך לצאת מהאוטומט <span class="ar" aria-hidden="true">←</span></a>\n',
        '<a class="cta" data-cta="hero_main" data-checkout href="checkout.html">אני רוצה ללמוד איך לצאת מהאוטומט <span class="ar" aria-hidden="true">←</span></a>\n  ' + block('hero', False) + '\n', n)
s = rep(s, '<a class="cta" data-cta="offer" data-checkout href="checkout.html">כן, אני רוצה להצטרף עכשיו - 297 ₪ <span class="ar" aria-hidden="true">←</span></a>\n',
        '<a class="cta" data-cta="offer" data-checkout href="checkout.html">כן, אני רוצה להצטרף עכשיו - 297 ₪ <span class="ar" aria-hidden="true">←</span></a>\n  ' + block('offer', True) + '\n', n)
s = tail(s, n)
open(os.path.join(OUT, n), 'w', encoding='utf8').write(s)

# הלוגואים
os.makedirs(os.path.join(OUT, 'assets', 'pay'), exist_ok=True)
for f in ('apple-pay-mark.svg', 'google-pay-mark.svg', 'bit-mark.svg', 'card.svg'):
    shutil.copy(os.path.join(HERE, 'pay', f), os.path.join(OUT, 'assets', 'pay', f))
print('ok')
