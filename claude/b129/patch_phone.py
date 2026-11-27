#!/usr/bin/env python3
# ב129: שדה טלפון רשות בדף התודה ("בן ישמח לוודא שהכל עובד לך"). טיוטה - לעלייה אחרי 1.12.
# מוצג רק אחרי תשלום מאומת, בחלון הראשי, ורק כשאין טלפון מהסליקה באותו דפדפן (רוכשי a5s).
# נשלח ל-Make (ב129, הוק 9gjwxco9…) עם מספר העסקה, מזהה התשלום והטלפון; נשמר ברשומת הרכישה (210157) רק אם אין בה טלפון.
# usage: patch_phone.py <in thanks.html> <out>
import sys, re
src = open(sys.argv[1], encoding="utf8").read()
def rep(old, new, cnt=1):
    global src
    assert src.count(old) == cnt, ("anchor", old[:70], src.count(old))
    src = src.replace(old, new)

# 1) CSS
rep('.srv .ch button:focus-visible{outline:3px solid var(--gold2);outline-offset:2px}\n',
'.srv .ch button:focus-visible{outline:3px solid var(--gold2);outline-offset:2px}\n'
'/* ב129: טלפון רשות אחרי תשלום מאומת */\n'
'.ph{margin:22px 0 0;padding:16px 14px 14px;border:1px solid var(--line);border-radius:16px;background:#FBF9F4;text-align:right}\n'
'.ph h2{font-size:16px;font-weight:800;margin:0 0 4px}\n'
'.ph p{font-size:14.5px;color:var(--ink2);margin:0 0 10px}\n'
'.ph form{display:flex;gap:8px}\n'
'.ph input{flex:1;min-width:0;font:inherit;font-size:17px;min-height:46px;padding:0 12px;border:1.5px solid var(--line);border-radius:12px;background:#fff;direction:ltr;text-align:left}\n'
'.ph input:focus-visible{outline:3px solid var(--gold2);outline-offset:1px}\n'
'.ph button{font:inherit;font-weight:700;font-size:15px;min-height:46px;padding:0 16px;border-radius:12px;border:0;background:var(--ink);color:#fff;cursor:pointer;white-space:nowrap}\n'
'.ph button[disabled]{opacity:.6;cursor:default}\n'
'.ph .err{color:#B3261E;margin:8px 0 0}\n'
'.ph .ty{color:var(--ok);font-weight:700;margin:8px 0 0}\n')

# 2) HTML - לפני "איפה פרטי הגישה?"
rep('<section class="acc" id="acc" aria-labelledby="accH">',
'<!-- ב129: טלפון רשות. מוצג רק אחרי אימות התשלום, רק כשאין טלפון מהסליקה (רוכשי a5s). נשלח ל-Make עם מספר העסקה ומזהה התשלום בלבד ונשמר ברשומת הרכישה. לא לגיליון ולא ל-Meta -->\n'
'<section class="ph" id="ph" aria-labelledby="phH" hidden>\n'
' <h2 id="phH">בן ישמח לוודא שהכל עובד לך</h2>\n'
' <p>השאר טלפון (לא חובה) ובן יחזור אליך לוודא שהגישה לקורס עובדת ושאין שאלות פתוחות.</p>\n'
' <form id="phForm" novalidate><input id="phIn" type="tel" inputmode="tel" autocomplete="tel" placeholder="050-0000000" aria-label="טלפון" maxlength="20" data-clarity-mask="True"><button type="submit" id="phBtn">שלחו לבן</button></form>\n'
' <p class="err" id="phErr" role="alert" hidden>נראה שהמספר לא שלם. 10 ספרות, מתחיל ב-05.</p>\n'
' <p class="ty" id="phTy" role="status" hidden>תודה! בן יחזור אליך.</p>\n'
'</section>\n'
'<section class="acc" id="acc" aria-labelledby="accH">')

# 3) כתובת ההוק
rep('    const UPSELL_ISSUE = "https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd";',
'    const PHONE_HOOK = "https://hook.eu1.make.com/9gjwxco9k4wj4pi9sdhe74jxg1o8gbkn"; /* ב129: טלפון רשות מדף התודה → רשומת הרכישה */\n'
'    const UPSELL_ISSUE = "https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd";')

# 4) קריאה אחרי האימות
rep('      survey(d);\n', '      survey(d);\n      phone(d); /* ב129 */\n')

# 5) הפונקציה
rep('    /* ב74: הצעת האפסייל.',
'''    /* ב129: טלפון רשות, רק אחרי תשלום מאומת ובחלון הראשי, ורק כשאין טלפון מהסליקה באותו דפדפן (רוכשי a5s; ב-checkout.html הטלפון כבר נשמר).
       נשלח ל-Make עם מספר העסקה, מזהה התשלום והטלפון. נשמר ברשומת הרכישה רק אם אין בה טלפון. לגיליון נשלח רק אירוע thanks_phone בלי המספר. לא ל-Meta */
    function phone(d){
      if(framed || PHONE_HOOK[0] === "%") return;
      const deal = d && /^\\d+$/.test(String(d.deal || "")) ? String(d.deal) : ""; if(!deal || !lp) return;
      const box = el("ph"); if(!box || box.dataset.on) return; box.dataset.on = "1";
      const K = "ph_" + deal; try{ if(localStorage.getItem(K)) return; }catch(e){}
      let cc = ""; try{ cc = String((JSON.parse(sessionStorage.getItem("cc_det") || "{}") || {}).phone || ""); }catch(e){}
      if(cc.replace(/\\D/g, "").length >= 9) return;
      const ev = r => { try{ if(TRACK_ENDPOINT[0] === "%") return; let lc = {}; try{ lc = JSON.parse(localStorage.getItem("nlp_lc") || "{}"); }catch(e){}
        const f = new URLSearchParams({ev:"thanks_phone", variant:lc.v || qs.get("v") || "", sid:lc.sid || qs.get("sid") || "", name:r, x:"deal=" + deal});
        try{ if(localStorage.getItem("nlp_int") === "1") f.set("x", f.get("x") + ";int=1"); }catch(e){}
        if(!(navigator.sendBeacon && navigator.sendBeacon(TRACK_ENDPOINT, f))) fetch(TRACK_ENDPOINT, {method:"POST", body:f, mode:"no-cors"}); }catch(e){} };
      const err = el("phErr"), btn = el("phBtn");
      const fail = () => { btn.disabled = false; err.textContent = "לא הצלחנו לשמור. אפשר לנסות שוב, או לכתוב לנו בוואטסאפ למטה."; err.hidden = false; ev("fail"); };
      el("phForm").addEventListener("submit", e => { e.preventDefault();
        let p = String(el("phIn").value || "").replace(/\\D/g, ""); if(p.startsWith("972")) p = "0" + p.slice(3);
        if(!/^05\\d{8}$/.test(p)){ err.textContent = "נראה שהמספר לא שלם. 10 ספרות, מתחיל ב-05."; err.hidden = false; return; }
        err.hidden = true; btn.disabled = true;
        fetch(PHONE_HOOK, {method:"POST", body:new URLSearchParams({deal:deal, lookup_lp:lp, phone:p})})
          .then(r => r.json()).then(j => { if(!(j && j.ok === true)) return fail();
            try{ localStorage.setItem(K, "1"); }catch(e){} el("phForm").hidden = true; el("phTy").hidden = false; ev("saved"); })
          .catch(fail); });
      box.hidden = false; ev("shown");
    }
    /* ב74: הצעת האפסייל.''')
open(sys.argv[2], "w", encoding="utf8").write(src)
print("ok", len(src))
