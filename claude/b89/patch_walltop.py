# ב89 המשך (בקשת יהב דרך הראשי, 13.11): בדף התשלום (A ו-B) בראש הדף, לפני שדות הפרטים:
#  - Apple Pay ו-Google Pay גדולים (44px, אותו גובה, Apple Pay מימין), ומתחתם "משלמים ב-Apple Pay או ב-Google Pay בלחיצה, אחרי שם, מייל וטלפון".
#  - לחיצה על לוגו: גלילה לשדה השם, פוקוס וסימון זמני. נרשם checkout_wallet_tap (x=w=apple/google).
#  - בדפדפן של אינסטגרם/פייסבוק: במקום הלוגואים והטקסט - הרמז הקיים (שלוש הנקודות). הרמז לא חוזר בשורה התחתונה.
#  - ביט: לא בבלוק הזה עד שיאומת.
# רץ על checkout.html אחרי ב89 (live 5227dd4c5723002d).
# שימוש: python3 patch_walltop.py <checkout.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new, 1)

rep('</head>', '''<style>/* ב89 המשך: Apple Pay ו-Google Pay בראש דף התשלום */
.walltop{margin:14px auto 2px;text-align:center}
.walltop .wt-row{display:flex;justify-content:center;align-items:center;gap:14px;direction:rtl}
.walltop .wt-b{display:block;padding:0;margin:0;border:0;background:none;cursor:pointer;line-height:0;border-radius:10px;-webkit-tap-highlight-color:transparent}
.walltop .wt-b:focus-visible{outline:3px solid var(--gold2);outline-offset:3px}
.walltop .wt-b img{display:block;height:44px;width:auto}
.walltop .wt-t{margin:10px 0 0;font-size:15px;line-height:1.45;font-weight:600;color:var(--ink2)}
.walltop .wt-h{margin:0;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:#F4F6F8;font-size:15px;line-height:1.45;font-weight:600;color:var(--ink2)}
.walltop [hidden]{display:none}
.fld input.wt-flash{outline:3px solid var(--gold2);outline-offset:1px;box-shadow:0 0 0 6px rgba(201,169,110,.28);transition:box-shadow .3s}
</style>
</head>''')

rep('''<p class="what">עוד רגע זה שלך. לאחר אישור התשלום תקבל גישה מיידית לקורס ולכל הבונוסים.</p>
</section>''', '''<p class="what">עוד רגע זה שלך. לאחר אישור התשלום תקבל גישה מיידית לקורס ולכל הבונוסים.</p>
<div class="walltop" id="wallTop"><div class="wt-row" id="wtRow"><button type="button" class="wt-b" data-w="apple" aria-label="תשלום ב-Apple Pay: מתחילים בשם, מייל וטלפון"><img src="assets/pay/apple-pay-mark.svg" alt="Apple Pay" width="69" height="44" decoding="async"></button><button type="button" class="wt-b" data-w="google" aria-label="תשלום ב-Google Pay: מתחילים בשם, מייל וטלפון"><img src="assets/pay/google-pay-mark.svg" alt="Google Pay" width="82" height="44" decoding="async"></button></div>
<p class="wt-t" id="wtT">משלמים ב-<bdi>Apple Pay</bdi> או ב-<bdi>Google Pay</bdi> בלחיצה, אחרי שם, מייל וטלפון</p><p class="wt-h" id="wtH" hidden></p></div>
</section>''')

# המדידה של הדף (track) זמינה לסקריפט של הבלוק
rep('''  /* ב79: בכשל תשלום נרשם קוד הדחייה''', '''  window.NLP_CO_TRACK=track; /* ב89 המשך: לחיצה על לוגו בראש הדף */
  /* ב79: בכשל תשלום נרשם קוד הדחייה''')

rep('</body>', '''<script>/* ב89 המשך: Apple Pay ו-Google Pay בראש הדף. לחיצה = גלילה לשדה השם וסימון. בדפדפן פנימי - הרמז במקום הלוגואים */
(function(){var W=document.getElementById("wallTop");if(!W)return;
var ua=navigator.userAgent||"",inapp=/Instagram|FBAN|FBAV|FB_IAB|FBIOS|FB4A/i.test(ua),ios=/iPhone|iPad|iPod/i.test(ua)||(/Macintosh/i.test(ua)&&navigator.maxTouchPoints>1),and=/Android/i.test(ua);
if(inapp){var hint=ios?"ל-\\u2066Apple Pay\\u2069: לחצו על שלוש הנקודות למעלה ופתחו בספארי":and?"ל-\\u2066Google Pay\\u2069: לחצו על שלוש הנקודות למעלה ופתחו בכרום":"";
 document.getElementById("wtRow").hidden=true;document.getElementById("wtT").hidden=true;
 var h=document.getElementById("wtH");if(hint){h.textContent=hint;h.hidden=false}else W.hidden=true;
 var L=document.querySelectorAll(".paylogos .pl-h");for(var i=0;i<L.length;i++)L[i].hidden=true; /* הרמז רק פעם אחת, בראש הדף */
 return}
var B=W.querySelectorAll(".wt-b");for(var j=0;j<B.length;j++)B[j].addEventListener("click",function(){var w=this.getAttribute("data-w"),f=document.getElementById("fName");
 try{if(window.NLP_CO_TRACK)NLP_CO_TRACK("checkout_wallet_tap",{x:"w="+w})}catch(e){}
 if(!f)return;try{f.scrollIntoView({behavior:"smooth",block:"center"})}catch(e){f.scrollIntoView()}
 try{f.focus({preventScroll:true})}catch(e){f.focus()}
 f.classList.add("wt-flash");setTimeout(function(){f.classList.remove("wt-flash")},1800)});
})();</script>
</body>''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
