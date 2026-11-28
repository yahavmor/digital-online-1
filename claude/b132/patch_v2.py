#!/usr/bin/env python3
# ב132: גרסה 2 של a5s (a5s2.html) - שלד: וריאנט a5s2, טלפון לא חובה, תיבת הסכמה אחת לא חובה (א34), תנאי העסקה כשורת טקסט,
# הבלטת "3 תשלומים של 99 ₪", אחריות צמודה לכפתור, סלוטים (מוסתרים) להצצה של 42 שניות ולסרטון של בן. הטקסטים הסופיים (א34, שאלות) יוכנסו כשיגיעו.
# usage: patch_v2.py <a5s.html> <out a5s2.html>
import sys, re
src = open(sys.argv[1], encoding="utf8").read()
def rep(old, new, cnt=1):
    global src
    assert src.count(old) == cnt, ("anchor", old[:60], src.count(old))
    src = src.replace(old, new)

# וריאנט
rep('data-variant="a5s"', 'data-variant="a5s2"')

# תיבת ההסכמה לא חובה (א34), התנאים כשורת טקסט
rep('var BOX_MODE="one_required";', 'var BOX_MODE="one_optional"; /* ב132/א34: תיבת הסכמה אחת, לא מסומנת ולא חובה; תנאי העסקה כשורת טקסט מתחת לכפתור */')

# CSS
rep('.lpf-pay3{margin:-2px 0 0;text-align:center;font-size:14.5px;font-weight:700;color:var(--ink2,#ccc)}',
    '.lpf-pay3{margin:-2px 0 0;text-align:center;font-size:14.5px;font-weight:700;color:var(--ink2,#ccc)}\n'
    '/* ב132 */\n'
    '.lpf-pay3.v2{font-size:18px;color:var(--ink,#fff);margin:2px 0 4px}.lpf-pay3.v2 b{color:#FECF00;font-size:20px}\n'
    '.lpf-f small{display:block;font-weight:400;font-size:12.5px;color:var(--ink2,#ccc);margin-top:2px}\n'
    '.lpf-guar{margin:8px 0 0;text-align:center;font-size:14px;font-weight:700;color:var(--ink,#fff)}.lpf-guar span{display:block;font-weight:400;font-size:12.5px;color:var(--ink2,#ccc);margin-top:2px}\n'
    '.v2-slot{margin:14px auto 0;max-width:420px}.v2-slot video,.v2-slot img{width:100%;border-radius:14px;display:block}.v2-slot p{font-size:13.5px;color:var(--ink2,#ccc);text-align:center;margin:6px 0 0}\n')

# 3 תשלומים בולט (שני המקומות)
rep('<p class="lpf-pay3">או 3 תשלומים של 99 ₪</p>', '<p class="lpf-pay3 v2">או <b>3 תשלומים של 99 ₪</b>, בלי ריבית</p>', 2)

# טפסים: טלפון לא חובה אחרי המייל, תיבה לא חובה, שורת תנאים, אחריות צמודה לכפתור
for n in ("1", "2"):
    rep(f'<label class="lpf-f"><b>מייל</b><input id="lfEmail{n}" name="email" type="email" inputmode="email" autocomplete="email" dir="ltr" required></label>',
        f'<label class="lpf-f"><b>מייל</b><input id="lfEmail{n}" name="email" type="email" inputmode="email" autocomplete="email" dir="ltr" required></label>'
        f'<label class="lpf-f"><b>טלפון <small>לא חובה. אם משהו לא יעבוד לך, בן יוכל לחזור אליך.</small></b><input id="lfPhone{n}" name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" maxlength="20" placeholder="050-0000000"></label>')
    rep(f'<input type="checkbox" id="lfBox{n}" name="box" value="1" required><span>קראתי ואני מאשר/ת את <a href="terms.html" target="_blank" rel="noopener">התקנון</a> ו<a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a>, ומסכים/ה לקבל מבן נחום מיילים עם תוכן והצעות. אפשר להסיר בכל רגע.</span></label>',
        f'<input type="checkbox" id="lfBox{n}" name="box" value="1"><span data-v2text="consent">אני מסכים/ה שבן ישלח לי מיילים והודעות וואטסאפ עם תוכן והצעות. לא חובה לרכישה, ואפשר להסיר בכל רגע.</span></label>')
    rep(f'<p class="lpf-err" id="lfErr{n}" role="alert"></p><button class="cta" type="submit" data-cta="form{n}">',
        f'<p class="lpf-err" id="lfErr{n}" role="alert"></p><button class="cta" type="submit" data-cta="form{n}">')
# שורת התנאים מתחת לכפתור + אחריות: מוסיפים אחרי כל </button></form> של הטפסים
rep('<span class="v4-pay"><svg class="v4-li" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>תשלום מאובטח</span></button></form>',
    '<span class="v4-pay"><svg class="v4-li" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>תשלום מאובטח</span></button>'
    '<p class="lpf-guar" data-v2text="guar">7 ימי אחריות עם החזר מלא<span>בלחיצה על הכפתור את/ה מאשר/ת את <a href="terms.html" target="_blank" rel="noopener">התקנון</a> ו<a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a>.</span></p></form>', 2)

# הטלפון: בדיקה ושליחה
rep('''  f.querySelector(".lpf-err").textContent=bad.length?"חסר: "+bad.join(", "):"";
  return bad.length?null:{name:n,email:e,phone:""}}''',
'''  var ph=$(f,"phone"),p=ph?ph.value.replace(/\\D/g,""):"";if(p.indexOf("972")===0)p="0"+p.slice(3);var pok=!p||/^05\\d{8}$/.test(p);if(ph)ph.classList.toggle("bad",!pok);if(!pok)bad.push("טלפון (10 ספרות, מתחיל ב-05, או להשאיר ריק)"); /* ב132: טלפון לא חובה */
  f.querySelector(".lpf-err").textContent=bad.length?"חסר: "+bad.join(", "):"";
  return bad.length?null:{name:n,email:e,phone:pok?p:""}}''')
rep('S("form_error",{name:["name","email","box"].filter(', 'S("form_error",{name:["name","email","phone","box"].filter(')
rep('lead_phone:"",lead_consent:cn', 'lead_phone:d.phone,lead_consent:cn')
rep('name:d.name,email:d.email,phone:"",utm_source', 'name:d.name,email:d.email,phone:d.phone,utm_source')

# סלוט להצצה של 42 שניות (סוף מקטע 2, מוסתר עד שיש קובץ) וסלוט לסרטון של בן בהצעה
rep('''<p>המטרה היא שהחיים שלך ימשיכו לאמן אותך גם הרבה אחרי שסיימת ללמוד.</p>
</div></div></section>''',
'''<p>המטרה היא שהחיים שלך ימשיכו לאמן אותך גם הרבה אחרי שסיימת ללמוד.</p>
<!-- ב132: הצצה של 42 שניות משיעור העוגן (ע20). מוסתר עד שהקובץ בתיקייה: למלא data-src ולהסיר hidden -->
<div class="v2-slot" id="v2Peek" data-src="" hidden><video controls playsinline preload="none" poster=""></video><p>42 שניות מתוך השיעור הראשון בקורס</p></div>
</div></div></section>''')
rep('<section id="offer" data-sec="3" data-name="ההצעה" data-buyzone data-stage="offer"><div class="wrap stack">',
    '<section id="offer" data-sec="3" data-name="ההצעה" data-buyzone data-stage="offer"><div class="wrap stack">\n<!-- ב132: סרטון קצר של בן ליד ההצעה (30-45 שניות). מוסתר עד שהקובץ קיים -->\n<div class="v2-slot" id="v2Ben" data-src="" hidden><video controls playsinline preload="none" poster=""></video><p>בן, ב-40 שניות</p></div>')
# הפעלת הסלוטים אם יש data-src
rep('</body>', '<script>/* ב132: סלוטי וידאו - מוצגים רק כשיש קובץ */(function(){["v2Peek","v2Ben"].forEach(function(id){var b=document.getElementById(id);if(!b)return;var s=b.getAttribute("data-src");if(s){b.querySelector("video").src=s;b.hidden=false;b.querySelector("video").addEventListener("play",function(){try{window.__lpSend&&window.__lpSend("video_play",{name:id})}catch(e){}},{once:true})}})})();</script>\n</body>')
open(sys.argv[2], "w", encoding="utf8").write(src)
print("ok", len(src))
