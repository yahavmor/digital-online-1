# ב101 (ראשי 17.11, שאלה 3): לקישורים האישיים של ב101 (תוקף 7 ימים) - "ההצעה בתוקף עד DD.MM" במקום "רק במסך הזה".
# מופעל רק כשבכתובת יש until=YYYY-MM-DD. בלי until (רוכש חדש מדף התודה) - הדפים בדיוק כמו היום.
# התוקף עצמו נבדק רק בשרת (8463689); הפרמטר משפיע על הנוסח בלבד. נוסח לאישור בן. פריסה רק אחרי "מאשר".
# שימוש: python3 patch_until.py <repo root>
import sys, os
root = sys.argv[1]
def patch(fn, pairs):
    p = os.path.join(root, fn); s = open(p, encoding="utf8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old)); s = s.replace(old, new, 1)
    open(p, "w", encoding="utf8").write(s)
patch("nlp/upsell-97.html", [
 ("const COPY = {\n  once: {", '''/* ב101: קישור אישי לרוכש קיים - until=YYYY-MM-DD בכתובת מחליף את "רק במסך הזה" ב"בתוקף עד". בלי until: הנוסח של ב74 בלי שינוי. התוקף נבדק רק בשרת */
const UNTIL_RAW = ((new URLSearchParams(location.search).get('until') || '').match(/^20\\d\\d-[01]\\d-[0-3]\\d$/) || [''])[0];
const UNTIL = UNTIL_RAW ? UNTIL_RAW.slice(8, 10) + '.' + UNTIL_RAW.slice(5, 7) : '';
const COPY = {
  once: {'''),
 ("}.once;", ''',
  until: { heroTag: 'הצעה חד-פעמית • לרוכשי הקורס', offerTag: 'הצעה אישית, בתוקף עד ' + UNTIL,
          urgent: '<b>שימו לב:</b> זו הצעה אישית לרוכשי הקורס. 97&nbsp;₪ בתוקף עד ' + UNTIL + ', ואחרי זה היא לא תחזור.',
          modal: 'אין בעיה. הגישה שלך לקורס נשארת שלך. רק חשוב לדעת: אם תוותר עכשיו, ההצעה הזו לא תחזור.',
          faq: 'הקורס שרכשת נשאר שלך. ההצעה להוסיף את האפליקציה ב-97&nbsp;₪ היא אישית ובתוקף עד ' + UNTIL + ', והיא לא תחזור.' }
}[UNTIL ? 'until' : 'once'];'''),
 ("document.querySelectorAll('[data-copy]').forEach(el => { el.innerHTML = COPY[el.dataset.copy]; });",
  "document.querySelectorAll('[data-copy]').forEach(el => { el.innerHTML = COPY[el.dataset.copy]; });\nif (UNTIL) { const h = document.querySelector('.expired-view h2'); if (h) h.textContent = 'ההצעה כבר לא זמינה'; } /* ב101 */"),
 ("location.href = CONFIG.checkoutPage + '?' + (TOKEN ? 't='+encodeURIComponent(TOKEN) : 'demo='+encodeURIComponent(DEMO));",
  "location.href = CONFIG.checkoutPage + '?' + (TOKEN ? 't='+encodeURIComponent(TOKEN) : 'demo='+encodeURIComponent(DEMO)) + (UNTIL_RAW ? '&until=' + UNTIL_RAW : ''); /* ב101: הנוסח \"בתוקף עד\" ממשיך לדף התשלום */"),
])
patch("nlp/checkout97.html", [
 (''' document.querySelectorAll("[data-course]").forEach(a => a.href = COURSE);''',
  ''' document.querySelectorAll("[data-course]").forEach(a => a.href = COURSE);
 /* ב101: קישור אישי לרוכש קיים (until=YYYY-MM-DD) - שורת הדחיפות ומסך "לא זמינה" בלי "מיד אחרי רכישת הקורס". בלי until: בלי שינוי */
 const until = ((q.get("until") || "").match(/^20\\d\\d-[01]\\d-[0-3]\\d$/) || [""])[0];
 if (until) { const d = until.slice(8, 10) + "." + until.slice(5, 7);
  $("urg").textContent = "ההצעה האישית ב-97 ₪ בתוקף עד " + d + ", ואחרי זה היא לא תהיה זמינה שוב";
  const ps = $("stExpired").querySelectorAll("p"); if (ps[0]) ps[0].textContent = "ההצעה האישית ב-97 ₪ כבר לא בתוקף."; if (ps[1]) ps[1].textContent = "זו הייתה הצעה אישית לזמן מוגבל, והיא לא חוזרת."; }'''),
])
print("ok")
