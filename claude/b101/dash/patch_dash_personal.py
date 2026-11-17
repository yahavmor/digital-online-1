# ב101 (ראשי 17.11, "מאשר ... שינוי הדשבורד"): בלשונית 12 (אפסייל), קודים שהתוקף שלהם יותר מיום מההנפקה (קישורים אישיים של ב101, 7 ימים)
# לא נספרים ב"קודים שהונפקו" ובאחוז ההמרה, ומוצגים בשורה נפרדת. קוד רגיל מדף התודה תקף 30 דקות.
# שימוש: python3 patch_dash_personal.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
p = os.path.join(root, "nlp/dashboard.html"); s = open(p, encoding="utf8").read()
pairs = [
 ('function upsTestDeal(d){return !!d&&TEST_DEALS.includes(d)}',
  'function upsTestDeal(d){return !!d&&TEST_DEALS.includes(d)}\nfunction upsPersonal(r){return !!(r.created&&r.expires)&&(r.expires-r.created)>864e5} /* ב101: קישור אישי לרוכש קיים (תוקף 7 ימים), לא קוד מדף התודה (30 דקות) */'),
 ('const C=UPS?UPS.rows.filter(r=>showTests||!(r.test||upsTestDeal(r.deal)||upsTestDeal(r.up))):[],',
  'const C0=UPS?UPS.rows.filter(r=>showTests||!(r.test||upsTestDeal(r.deal)||upsTestDeal(r.up))):[],C=C0.filter(r=>!upsPersonal(r)),CP=C0.filter(upsPersonal),'),
 ('''rowsT.push('<tr><td colspan="'+(PER.length+1)+'" class="note">לפי מועד הרכישה (גיליון האירועים)</td></tr>');''',
  '''rowsT.push('<tr><td>קישורים אישיים לרוכשים קיימים <small>ב101, תוקף 7 ימים. לא נספרים בשורות ובהמרה שלמעלה</small></td>'+PER.map(([,,a])=>{if(!UPS)return '<td class="num">'+(UPS_ST==="loading"||UPS_ST==="idle"?WAIT:MISS)+'</td>';const I=CP.filter(r=>inP(r.created,a));return '<td class="num">'+fmt(I.length)+(I.length?'<small>'+fmt(I.filter(r=>r.used).length)+' נוצלו · '+fmt(I.filter(r=>r.declined&&!r.used).length)+' נדחו</small>':'')+'</td>'}).join("")+'</tr>'); /* ב101 */
 rowsT.push('<tr><td colspan="'+(PER.length+1)+'" class="note">לפי מועד הרכישה (גיליון האירועים)</td></tr>');'''),
 ('". אחוזים מתוך הקודים שהונפקו באותה תקופה.";',
  '". אחוזים מתוך הקודים שהונפקו באותה תקופה. קישורים אישיים לרוכשים קיימים (ב101, תוקף יותר מיום) מוצגים בשורה נפרדת ולא נספרים בהמרה. רכישות האפסייל וההכנסה למטה כוללות את כל הרכישות.";'),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - ב101 (\\"מאשר\\" מיהב): בלשונית 12 (אפסייל) קישורים אישיים לרוכשים קיימים (תוקף 7 ימים) לא נספרים ב\\"קודים שהונפקו\\" ובאחוז ההמרה, ומוצגים בשורה נפרדת. רכישות והכנסה בלי שינוי."],\n' % (day, hm)),
]
for o, n in pairs:
    assert s.count(o) == 1, (o[:80], s.count(o)); s = s.replace(o, n, 1)
open(p, "w", encoding="utf8").write(s); print("ok")
