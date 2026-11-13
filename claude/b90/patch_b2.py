# ב90 (בקשת יהב דרך הראשי, 13.11): גרסת בדיקה B2 לדף התשלום, על בסיס B הנוכחית. מקומי, פריסה רק אחרי "מאשר".
#  הגרלה: co_b2_1311 - חצי-חצי B מול B2 לכל מכשיר (localStorage nlp_co_b2), בלי קשר לדף המכירה. כך בכל דף מכירה (a5v6, pr2) יש
#  חלוקה של חצי-חצי בנפרד, והניסוי בין הדפים לא מושפע (הדפים עצמם לא משתנים). co=a / co=b / co=b2 בכתובת גובר (לבדיקות).
#  באירועים: co=b2 (או co=b), cx=co_b2_1311. ל-Make נשלח co=b בשתי הגרסאות (B2 = B בתצוגה בלבד), אז 7827398 לא משתנה.
#  B2 מוסיפה רק תצוגה (מוסתרת ב-B):
#   1. עוגן מחיר: 1,290 ₪ מחוק ליד 297 ₪, ו"מחיר השקה לזמן מוגבל".
#   2. מתחת למחיר: "7 ימי אחריות: אם הקורס לא מתאים לך, שולחים מייל ומקבלים החזר מלא."
#   3. "שלב 1 מתוך 2: הפרטים שלך" מעל השדות, "שלב 2 מתוך 2: תשלום" מעל טופס התשלום.
#   4. שורת הלוגואים: בדפדפן של פייסבוק/אינסטגרם ביט ראשון - כבר כך (Apple Pay ו-Google Pay מוסתרים שם, וביט לפני האשראי), ורק כש-PAYLOGO_BIT.
#   5. פרטי העסקה: "תשלום חד-פעמי באשראי, Apple Pay או Google Pay" (וביט כשהוא בשורה).
#   6. autocomplete: כבר name / email / tel בשדות - לא שונה.
# שימוש: python3 patch_b2.py <checkout.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)

# הגרלה מוקדמת (ב-head), כדי שהתצוגה של B2 תופיע בלי הבהוב
rep('</head>', '''<script>/* ב90: ניסוי co_b2_1311 - B מול B2 חצי-חצי, נשמר במכשיר. co=a/b/b2 בכתובת גובר */
(function(){var c="b";try{c=(new URLSearchParams(location.search).get("co")||"").toLowerCase();
if(c!=="a"&&c!=="b"&&c!=="b2"){var k="nlp_co_b2",v=null;try{v=localStorage.getItem(k)}catch(e){}
 if(v!=="b"&&v!=="b2"){v=Math.random()<0.5?"b2":"b";try{localStorage.setItem(k,v)}catch(e){}}c=v}}catch(e){c="b"}
window.NLP_CO=c;document.documentElement.setAttribute("data-co2",c==="b2"?"1":"0")})();</script>
<style>/* ב90: תצוגת B2 (מוסתרת ב-B) */
.b2x,.b2xi,.pt-b{display:none}
html[data-co2="1"] .b2x{display:block}
html[data-co2="1"] .b2xi,html[data-co2="1"] .pt-b{display:inline}
html[data-co2="1"] .pt-a{display:none}
.b2-launch{margin:10px auto 0;width:max-content;max-width:100%;padding:3px 12px;border:1px solid var(--gold2);border-radius:999px;font-size:14px;font-weight:700;color:var(--gold)}
.b2-guar{margin:10px auto 2px;max-width:360px;padding:8px 12px;border-radius:12px;background:#EEF6F1;color:var(--ok);font-size:14.5px;font-weight:600;line-height:1.45}
.b2-step{color:var(--gold)}
.paytitle .pt-a,.paytitle .pt-b{font-size:inherit;font-weight:inherit;color:inherit}
</style>
</head>''')

# 1 + 2: עוגן מחיר ואחריות
rep('''<p class="item">הקורס המלא + כל הבונוסים</p>
<p class="price"><b>297</b><span>₪</span></p>''', '''<p class="item">הקורס המלא + כל הבונוסים</p>
<p class="b2x b2-launch">מחיר השקה לזמן מוגבל</p>
<p class="price"><s class="was b2xi">1,290 ₪</s><b>297</b><span>₪</span></p>
<p class="b2x b2-guar">7 ימי אחריות: אם הקורס לא מתאים לך, שולחים מייל ומקבלים החזר מלא.</p>''')

# 3: שלבים
rep('<h2>הפרטים שלך</h2>', '<h2><span class="b2xi b2-step">שלב 1 מתוך 2: </span>הפרטים שלך</h2>')
rep('<p class="paytitle">פרטי תשלום<span>', '<p class="paytitle"><span class="pt-a">פרטי תשלום</span><span class="pt-b">שלב 2 מתוך 2: תשלום</span><span>')

# 5: פרטי העסקה
rep('<dd>תשלום חד-פעמי בכרטיס אשראי. ללא מנוי', '<dd><span class="pt-a">תשלום חד-פעמי בכרטיס אשראי</span><span class="pt-b" id="b2PayHow">תשלום חד-פעמי באשראי, <bdi>Apple Pay</bdi> או <bdi>Google Pay</bdi></span>. ללא מנוי')

# הגרסה בלוגיקה (B2 = B) ובמדידה (co=b2)
rep('''const CO_EXP = "co_b_0811"; let CV = (qs.get("co")||"").toLowerCase();
  if (CV!=="a" && CV!=="b") CV = "b";''', '''const CO_EXP = "co_b2_1311"; const CO_L = window.NLP_CO==="a"||window.NLP_CO==="b2" ? window.NLP_CO : "b"; let CV = CO_L==="a" ? "a" : "b"; /* ב90: B2 מתנהגת כמו B; רק התצוגה והסימון (co=b2) שונים */''')
rep('''try{ if(window.clarity) clarity("set","co",CV); }catch(e){}''', '''try{ if(window.clarity) clarity("set","co",CO_L); }catch(e){}''')
rep('''extra.x=(extra.x?extra.x+";":"")+"co="+CV+";cx="+CO_EXP;''', '''extra.x=(extra.x?extra.x+";":"")+"co="+CO_L+";cx="+CO_EXP;''')

# ביט בפרטי העסקה של B2, רק כשהוא בשורת הלוגואים
rep('</body>', '''<script>/* ב90: B2 - ביט בפרטי העסקה רק כשהוא מופיע בשורת הלוגואים (PAYLOGO_BIT) */
(function(){if(window.NLP_CO!=="b2")return;var bit=document.querySelector('.paylogos [data-pl="bit"]:not([hidden])'),el=document.getElementById("b2PayHow");
if(bit&&el)el.innerHTML='תשלום חד-פעמי באשראי, <bdi>Apple Pay</bdi>, <bdi>Google Pay</bdi> או ביט'})();</script>
</body>''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
