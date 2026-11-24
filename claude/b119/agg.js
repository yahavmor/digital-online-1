// ב119: הקוד שרץ בתוך מודול ה-Code של תרחיש הסיכומים ב-Make. מקבל input = {leads, calls, spend, sales} (טקסטים) ומחזיר רק סיכומים לפי יום ומשווק.
// leads: שורות "stage|first_seen(YYYY-MM-DD)|marketer|phone|t?" מ-148094 (שלב 1 ושלב 7). calls: טלפון בכל שורה (153039, callback_requested).
// spend / sales: שורות "תאריך|משווק|סכום" מהגיליונות (UNFORMATTED, תאריך יכול להיות מספר סידורי של גוגל).
// הפלט: שורה לכל יום+משווק: date \t mk \t leads \t hot \t spend(ריק = לא הוזן) \t sales. בלי טלפונים, בלי שמות.
const START = "2026-11-22";
const norm = p => { const d = String(p || "").replace(/\D/g, ""); return d.length >= 9 ? d.slice(-9) : ""; };
const MK = m => { m = String(m || "").toLowerCase().trim();
  if (m === "rachel" || m === "רחל") return "rachel"; if (m === "amir" || m === "אמיר") return "amir";
  if (m === "galba" || m === "gal" || m === "גל") return "gal";
  if (m === "karlen" || m === "karlin" || m === "קרלין") return "karlen"; /* ב123 */ return "other"; };
const day = v => { v = String(v == null ? "" : v).trim(); let m;
  if (/^\d{5}(\.\d+)?$/.test(v)) return new Date(Date.UTC(1899, 11, 30) + Math.floor(+v) * 864e5).toISOString().slice(0, 10);
  if ((m = v.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/))) return m[1] + "-" + m[2].padStart(2, "0") + "-" + m[3].padStart(2, "0");
  if ((m = v.match(/^(\d{1,2})[.\/-](\d{1,2})(?:[.\/-](\d{2,4}))?$/))) { const y = m[3] ? (m[3].length === 2 ? "20" + m[3] : m[3]) : "2026"; return y + "-" + m[2].padStart(2, "0") + "-" + m[1].padStart(2, "0"); }
  return null; };
const lines = s => String(s || "").split("\n");
const hot = new Set(), leads = [];
for (const l of lines(input.leads)) { const a = l.split("|"); if (a.length < 4) continue; const ph = norm(a[3]); if (!ph) continue;
  if (a[0].trim() === "7") hot.add(ph); else if (a[0].trim() === "1" && !(a[4] || "").trim()) leads.push({ d: a[1].trim(), m: a[2], ph }); }
for (const l of lines(input.calls)) { const ph = norm(l); if (ph) hot.add(ph); }
const G = {}, g = (d, m) => G[d + "\t" + m] || (G[d + "\t" + m] = { l: 0, h: 0, s: null, n: 0 });
const seen = new Set();
for (const x of leads) { if (!/^\d{4}-\d{2}-\d{2}$/.test(x.d) || x.d < START || seen.has(x.ph)) continue; seen.add(x.ph); const o = g(x.d, MK(x.m)); o.l++; if (hot.has(x.ph)) o.h++; }
let spendRows = 0, salesRows = 0;
for (const l of lines(input.spend)) { const a = l.split("|"), d = day(a[0]), amt = parseFloat(String(a[2] == null ? "" : a[2]).replace(/[^\d.]/g, ""));
  if (!d || isNaN(amt)) continue; spendRows++; const o = g(d, MK(a[1])); o.s = (o.s || 0) + amt; }
for (const l of lines(input.sales)) { const a = l.split("|"), d = day(a[0]); if (!d) continue; salesRows++; g(d, MK(a[1])).n++; }
const out = Object.keys(G).sort().map(k => { const o = G[k]; return [k, o.l, o.h, o.s == null ? "" : Math.round(o.s * 100) / 100, o.n].join("\t"); });
const now = new Date().toLocaleString("sv-SE", { timeZone: "Asia/Jerusalem" }).slice(0, 16);
return { data: ["#v1", "spend_rows\t" + spendRows, "sales_rows\t" + salesRows].concat(out).join("\n"), updated: now };
