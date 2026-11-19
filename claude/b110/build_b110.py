# ב110 (ראשי 19.11): "שם ומייל כצעד ראשון" - טיוטה בלבד, לא חיה. שני קבצים נפרדים, לא מקושרים מאף דף, noindex.
# הקבצים נבנים מהדפים החיים של main ונשמרים בענף העבודה בלבד (claude/b110/draft), לא ב-nlp/ ולא באתר.
#  1. a5s_b110.html - הדף הקצר, ובכרטיס ההצעה טופס: שם מלא + מייל + תיבת סימון + הכפתור הקיים.
#     בשליחה: הליד נשמר מיד באותו מנגנון של הסליקה (אירוע checkout_details ל-hook המעקב, עם lead_name/lead_email/lead_consent,
#     בלי טלפון) -> 7798267 שומר ל-210989 כמו היום. אחר כך מעבר לסליקה, והפרטים עוברים ב-sessionStorage (cc_det, cc_cons) ולא בכתובת.
#  2. checkout_b110.html - הסליקה: השם והמייל מגיעים ממולאים (הסליקה החיה כבר קוראת את cc_det), והטלפון לא חובה.
# נוסח: תיבת הסימון מחכה לבן ([נוסח - מחכה לבן]). "(לא חובה)" ליד הטלפון הוא תוספת נוסח - לאישור בן.
# הרצה: python3 build_b110.py <שורש main> <תיקיית יעד>
import sys, os, re
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
def rd(f): return open(os.path.join(SRC, "nlp", f), encoding="utf8").read()
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a)); return s.replace(a, b)

# ---------- 1. הדף הקצר עם הטופס ----------
s = rd("a5s.html")
s = rep(s, 'data-variant="a5s"', 'data-variant="a5s_f"')   # בטיוטה: גרסה נפרדת, כדי שלא תתערבב בנתונים
m = re.search(r'<a class="cta" data-cta="offer" data-checkout href="#">(.*?)</a>', s, re.S); assert m
btn_inner = m.group(1)
FORM = ('<form class="lpf" id="lpForm" novalidate>'
        '<label class="lpf-f"><b>שם מלא</b><input id="lfName" name="name" autocomplete="name" maxlength="50" required></label>'
        '<label class="lpf-f"><b>מייל</b><input id="lfEmail" name="email" type="email" inputmode="email" autocomplete="email" dir="ltr" required></label>'
        '<label class="lpf-c"><input type="checkbox" id="lfBox" name="box" value="1"><span>[נוסח תיבת הסימון - מחכה לבן]</span></label>'
        '<p class="lpf-err" id="lfErr" role="alert"></p>'
        '<button class="cta" type="submit" data-cta="offer_form">' + btn_inner + '</button></form>')
s = s[:m.start()] + FORM + s[m.end():]
CSS = """<style>/* ב110: טופס שם + מייל בכרטיס ההצעה (טיוטה) */
.lpf{display:grid;gap:10px;margin:14px 0 4px;text-align:right}
.lpf-f{display:grid;gap:4px;font-size:15px}.lpf-f b{font-weight:700}
.lpf-f input{font:inherit;font-size:16px;min-height:48px;padding:8px 14px;border-radius:12px;border:1.5px solid var(--gold-a,#8a7340);background:var(--card,#16161a);color:var(--ink,#fff)}
.lpf-f input.bad{border-color:#e5484d}
.lpf-c{display:flex;gap:9px;align-items:flex-start;font-size:13.5px;line-height:1.55;color:var(--ink2,#ccc)}.lpf-c input{width:20px;height:20px;margin-top:2px;flex:none}
.lpf-err{min-height:1em;margin:0;color:#e5484d;font-size:14px}
.lpf .cta{width:100%;border:0;cursor:pointer;font:inherit}
</style>
"""
JS = """<script>/* ב110 (טיוטה): שליחת שם + מייל מכרטיס ההצעה. נשמר מיד כמו בסליקה (checkout_details), ואז מעבר לסליקה עם הפרטים ב-sessionStorage */
(function(){var f=document.getElementById("lpForm");if(!f)return;var $=function(i){return document.getElementById(i)};
 var REQUIRE_BOX=false; /* תיבה אחת שכוללת דיוור: לא חובה כברירת מחדל (חוק התקשורת 30א - הסכמה לדיוור לא כתנאי לרכישה). לשנות רק לפי החלטה */
 function chk(){var n=$("lfName").value.replace(/["\\\\<>{}]/g,"").trim().replace(/\\s+/g," "),e=$("lfEmail").value.trim(),bad=[];
  var nok=n.length>=2&&/\\s/.test(n),eok=/^[^\\s@"'\\\\<>{}]+@[^\\s@"'\\\\<>{}]+\\.[^\\s@"'\\\\<>{}]{2,}$/.test(e);
  $("lfName").classList.toggle("bad",!nok);$("lfEmail").classList.toggle("bad",!eok);if(!nok)bad.push("שם מלא (שם פרטי ומשפחה)");if(!eok)bad.push("מייל תקין");
  if(REQUIRE_BOX&&!$("lfBox").checked)bad.push("סימון התיבה");$("lfErr").textContent=bad.length?"חסר: "+bad.join(", "):"";return bad.length?null:{name:n,email:e,phone:""}}
 f.addEventListener("submit",function(ev){ev.preventDefault();var d=chk(),S=window.__lpSend||function(){};
  if(!d){S("checkout_validation_error",{name:["lfName","lfEmail"].filter(function(i){return $(i).classList.contains("bad")}).map(function(i){return i.slice(2).toLowerCase()}).join(","),x:"form=lp"});return}
  var cn=$("lfBox").checked?"1":"0";
  try{sessionStorage.setItem("cc_det",JSON.stringify(d));sessionStorage.setItem("cc_cons",cn);sessionStorage.setItem("cc_from_lp","1")}catch(e){}
  S("cta_click",{cta:"offer_form",checkout_started:1,x:"form=lp"});
  S("checkout_details",{lead_name:d.name,lead_email:d.email,lead_phone:"",lead_consent:cn,x:"cons="+cn+";form=lp"}); /* אותו אירוע ואותו hook כמו בסליקה -> 7798267 -> 210989 */
  try{if(window.fbq&&!window.__noPix){var w=d.name.toLowerCase().split(/\\s+/),ud={em:d.email.toLowerCase()};if(w[0])ud.fn=w[0];if(w.length>1)ud.ln=w[w.length-1];
   fbq("init","1278104408729813",ud);fbq("init","1651086743466533",ud);fbq("track","Lead",{content_name:"lpform"});
   if(!window.__ic){var dn=false;try{dn=sessionStorage.getItem("nlp_ic")==="1";sessionStorage.setItem("nlp_ic","1")}catch(e){}window.__ic=1;if(!dn)fbq("track","InitiateCheckout",{value:297,currency:"ILS"})}}}catch(e){}
  var a=document.querySelector("a[data-checkout]"),href=(a&&a.getAttribute("href"))||"checkout.html";
  try{localStorage.setItem("nlp_lc",JSON.stringify({v:document.documentElement.dataset.variant,qs:location.search.slice(1),cta:"offer_form",ts:Date.now()}))}catch(e){}
  setTimeout(function(){location.href=href.replace(/^checkout\\.html/,"checkout_b110.html")},350)});
})();
</script>
"""
s = rep(s, "</head>", CSS + "</head>"); s = rep(s, "</body>", JS + "</body>")
assert 'data-cta="offer"' not in s and s.count('id="lpForm"') == 1 and 'noindex' in s
open(os.path.join(OUT, "a5s_b110.html"), "w", encoding="utf8").write(s)

# ---------- 2. הסליקה: טלפון לא חובה ----------
c = rd("checkout.html")
c = rep(c, '<b>טלפון נייד</b><input id="fPhone" name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" required placeholder="05X-XXXXXXX">',
           '<b>טלפון נייד (לא חובה)</b><input id="fPhone" name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" placeholder="05X-XXXXXXX">')
c = rep(c, 'const pok = /^05\\d{8}$/.test(pn);', 'const pok = !pn || /^05\\d{8}$/.test(pn); /* ב110: טלפון לא חובה - ריק תקין, ומספר שהוזן חייב להיות תקין */')
n = c.count('["fName","fEmail","fPhone"].every(k=>$(k).value.trim())')
c = c.replace('["fName","fEmail","fPhone"].every(k=>$(k).value.trim())', '["fName","fEmail"].every(k=>$(k).value.trim())')
assert n >= 1, n
c = rep(c, '<meta name="robots"', '<meta name="robots" data-b110="draft"') if '<meta name="robots"' in c else c
open(os.path.join(OUT, "checkout_b110.html"), "w", encoding="utf8").write(c)
print("ok", len(s), len(c))
