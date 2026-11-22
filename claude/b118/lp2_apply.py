# ב118 ("מאשר ב118", יהב 22.11): landing_option2 - משווק גם לפי aff= (gal->galba, karlin->karlen), המשווק נשמר ב-148094 ונשלח להתראה החדשה (8737914)
# במקום ההוק jp6uk שלא קיים; index.html מפנה ל-/nlp/go.html. שימוש: python3 lp2_apply.py <שורש main>
import sys, os, hashlib
R = sys.argv[1]
def sh(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
P = os.path.join(R, "landing-pages", "landing_option2.html"); I = os.path.join(R, "index.html")
if sh(P) != "d89e79d0c5905ce3" or sh(I) != "a2dfbcb87c04ab3b": sys.exit("STOP: hash mismatch %s %s - לא שיניתי כלום" % (sh(P), sh(I)))
s = open(P, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a)); s = s.replace(a, b)
rep("  const p = getParams();\n  const resolvedSupplier = await resolveSupplier(p);",
    "  const p = getParams();\n"
    "  /* ב118: משווק גם לפי aff= (כמו בקישורי המשפך הנמכר), בנוסף ל-marketer=. gal ו-karlin נקראים ב-marketers.json galba ו-karlen */\n"
    "  var AFFMAP = {gal: 'galba', karlin: 'karlen'};\n"
    "  var affQ = (new URLSearchParams(location.search).get('aff') || '').toLowerCase().replace(/[^a-z0-9_-]/g, '');\n"
    "  if (!p.marketer && affQ) p.marketer = AFFMAP[affQ] || affQ;\n"
    "  var mkCode = (p.marketer || '').toLowerCase();\n"
    "  const resolvedSupplier = await resolveSupplier(p);")
rep("""    fetch('https://hook.eu1.make.com/jp6ukjt7tpk3y4yly9c691g01f47cq8q', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        event: 'lead_form',
        page: 'landing_option2',
        name: name,
        phone: phone,
        email: email,
        supplier: resolvedSupplier,
        timestamp: new Date().toLocaleString('he-IL')
      })
    })""", """    /* ב118: התראה במייל ליהב ולבן על כל ליד (8737914), במקום ההוק jp6uk שכבר לא קיים */
    fetch('https://hook.eu1.make.com/78f809msf3m36h2r8g2q4s6khabqj8vs', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        event: 'lead_form',
        page: 'landing_option2',
        name: name,
        phone: phone,
        email: email,
        marketer: mkCode,
        supplier: resolvedSupplier,
        timestamp: new Date().toLocaleString('he-IL')
      })
    })""")
rep("body: JSON.stringify({phone: phone, name: name, email: email, stage: 1, stage_label: 'landing', page: 'landing_option2'}),",
    "body: JSON.stringify({phone: phone, name: name, email: email, stage: 1, stage_label: 'landing', page: 'landing_option2', marketer: mkCode}),")
open(P, "w", encoding="utf-8").write(s)
open(I, "w", encoding="utf-8").write("""<!DOCTYPE html>
<html>
  <head><meta charset="UTF-8">
  <!-- ב118 (יהב 22.11): דף הבית מפנה ל-/nlp/go.html (במקום marketers/client1.html שלא קיים), עם כל הפרמטרים -->
  <script>location.replace('/nlp/go.html' + location.search + location.hash);</script>
  <meta http-equiv="refresh" content="0; url=/nlp/go.html">
</head>
  <body></body>
</html>
""")
print("landing_option2.html", sh(P), "index.html", sh(I))
