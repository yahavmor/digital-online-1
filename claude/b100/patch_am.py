# ב100 תוספת: התאמה מתקדמת ידנית בפיקסל (הכנה בלבד - לפרוס רק אחרי "מאשר").
# checkout.html: NLP_PIX_UD מוסיף fn/ln מהשם (למעט em/ph שכבר נשלחים). thanks.html: init עם אותם נתונים מ-cc_det (היום init בלי נתונים).
# הפיקסל מגבב em/ph/fn/ln בדפדפן לפני השליחה. external_id לא נשלח מהדפדפן (רק מגובב ב-CAPI), כדי לא לשלוח מזהה לא מגובב.
# שימוש: python3 patch_am.py <repo root>
import sys, os
root = sys.argv[1]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for o, n in pairs:
        assert s.count(o) == 1, (fn, o[:70], s.count(o)); s = s.replace(o, n, 1)
    open(p, "w", encoding="utf8").write(s)
OLD = 'window.NLP_PIX_UD=function(d){var u={};try{if(d&&d.email)u.em=String(d.email).trim().toLowerCase();if(d&&d.phone){var p=String(d.phone).replace(/\\D/g,"").replace(/^0/,"972");if(p)u.ph=p;}}catch(e){}return u};'
NEW = 'window.NLP_PIX_UD=function(d){var u={};try{if(d&&d.email)u.em=String(d.email).trim().toLowerCase();if(d&&d.phone){var p=String(d.phone).replace(/\\D/g,"").replace(/^0/,"972");if(p)u.ph=p;}if(d&&d.name){var w=String(d.name).trim().toLowerCase().split(/\\s+/).filter(Boolean);if(w[0])u.fn=w[0];if(w.length>1)u.ln=w[w.length-1];}}catch(e){}return u}; /* ב100: גם fn/ln */'
patch("nlp/checkout.html", [(OLD, NEW)])
patch("nlp/thanks.html", [('fbq("init","1278104408729813");fbq("init","1651086743466533");fbq("track","PageView");fbq("trackCustom","ThanksView");',
  'var ud={};try{var d=JSON.parse(sessionStorage.getItem("cc_det")||"{}")||{};if(d.email)ud.em=String(d.email).trim().toLowerCase();if(d.phone){var p=String(d.phone).replace(/\\D/g,"").replace(/^0/,"972");if(p)ud.ph=p}if(d.name){var w=String(d.name).trim().toLowerCase().split(/\\s+/).filter(Boolean);if(w[0])ud.fn=w[0];if(w.length>1)ud.ln=w[w.length-1]}}catch(e){} /* ב100: התאמה מתקדמת ידנית ל-Purchase */fbq("init","1278104408729813",ud);fbq("init","1651086743466533",ud);fbq("track","PageView");fbq("trackCustom","ThanksView");')])
print("ok")
