// ב91: לשונית האפסייל בדשבורד. נתונים מדומים, Make מדומה (גם מצב שבו הנתיב upsell עוד לא קיים).
// שימוש: node t_upsell_tab.js <dashboard לפני> <dashboard אחרי>
process.env.TZ = "Asia/Jerusalem";
const { chromium } = require("playwright"), fs = require("fs");
const [O, P] = process.argv.slice(2).map(f => fs.readFileSync(f, "utf8"));
const row = (ts, ev, extra) => { const a = Array(21).fill(""); a[0] = ts; a[1] = ev; a[2] = "a5v6"; a[3] = "s-" + ts.replace(/\D/g, ""); Object.assign(a, extra || {}); return a.join("\t"); };
const R = [];
// רכישת קורס רגילה (כדי שיהיו נתונים בשאר המסכים)
R.push(row("2026-11-14 09:00:00", "checkout_view", { 8: "utm_source=fb&utm_medium=paid", 16: "v1" }));
R.push(row("2026-11-14 09:05:00", "purchase", { 8: "cardcom | 297 ILS | deal 900001 | src ", 13: "cardcom_webhook" }));
const up = (ts, deal, cdeal, aff) => R.push(row(ts, "upsell_purchase", { 8: "upsell97 | 97 ILS | deal " + deal + " | course_deal " + cdeal, 13: "cardcom_upsell_webhook", 20: aff ? "aff=" + aff : "" }));
up("2026-11-14 10:05:00", "800001", "900001", "gal");
up("2026-11-14 10:06:00", "800001", "900001", "gal");          // כפילות - נספרת פעם אחת
up("2026-11-10 10:05:00", "800005", "900005", "");
up("2026-11-12 10:05:00", "800012", "900012", "gal");          // הוחזר
up("2026-11-03 10:05:00", "800007", "900007", "amir");
up("2026-11-14 14:05:00", "800010", "270060105", "");           // קורס של עסקת בדיקה
up("2026-10-30 10:05:00", "800011", "900011", "gal");          // חודש קודם
const EV = R.join("\n");
const AFF = "affiliates\tname\tpct\tactive\tfee\tbudget\ngal\tגל\t0\ttrue\t220\t\namir\tאמיר\t74\ttrue\t0\t\n";
const c = (created, mins, used, declined, test, aff, deal, upd) => { const d = new Date(created.replace(" ", "T") + "+02:00"), e = new Date(+d + mins * 6e4), f = x => x.toLocaleString("sv-SE", { timeZone: "Asia/Jerusalem" });
  return [created, f(e), used, declined, used === "true" ? f(new Date(+d + 5 * 6e4)) : "", test, aff, deal, upd].join("\t") };
const UPS = "upsell\tcreated\texpires\tused\tdeclined\tpaid_at\ttest\taff\tdeal\tup_deal\n" + [
  c("2026-11-14 10:00:00", 30, "true", "false", "false", "gal", "900001", "800001"),
  c("2026-11-14 11:00:00", 30, "false", "true", "false", "", "900002", ""),
  c("2026-11-14 12:00:00", 30, "false", "false", "false", "", "900003", ""),
  c("2026-11-14 21:50:00", 30, "false", "false", "false", "", "900004", ""),   // עדיין בתוקף ב-22:00
  c("2026-11-10 10:00:00", 30, "true", "", "", "", "900005", "800005"),          // שדות בוליאניים ריקים
  c("2026-11-10 11:00:00", 30, "false", "true", "false", "", "900006", ""),
  c("2026-11-03 10:00:00", 30, "true", "false", "false", "amir", "900007", "800007"),
  c("2026-11-03 11:00:00", 30, "false", "false", "false", "", "900008", ""),
  c("2026-11-14 13:00:00", 30, "true", "false", "true", "", "900009", "800009"),     // test=true
  c("2026-11-14 14:00:00", 30, "false", "true", "false", "", "270060105", ""),       // TEST_DEALS
  c("2026-10-30 10:00:00", 30, "true", "false", "false", "gal", "900011", "800011"), // חודש קודם
  "\t\t\t\t\t\t\t\t" ].join("\n");                                                      // שורה ריקה (בלי רשומות)
let n = 0, f = 0; const ok = (m, cnd, i) => { n++; if (!cnd) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => {
  const b = await chromium.launch();
  const run = async (html, upsBody, scr) => { const cx = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await cx.clock.setFixedTime(new Date("2026-11-14T22:00:00+02:00")); const errs = [], calls = [];
    await cx.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: html });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); calls.push(a); const body = a === "upsell" ? upsBody : { rows: EV, spend: "spend\n", affiliates: AFF, refunds: "refunds\n800012\t2026-11-13\n", paid: "paid\tat\taff\n", ads: "ads\n" }[a]; return r.fulfill({ status: 200, body: body == null ? "Accepted" : body }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await cx.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#" + (scr || "up")); await p.waitForTimeout(2500); return { cx, p, errs, calls } };
  const grab = (X, id) => X.p.evaluate(id => { const t = document.getElementById(id); return t ? [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())) : null }, id);
  // 1. עם הנתיב
  const B = await run(P, UPS);
  const T = await grab(B, "upTable"), A = await grab(B, "upAff"); console.log(JSON.stringify(T)); console.log(JSON.stringify(A));
  const H = T[0]; ok("columns today/7/mtd", H.join("|") === "לפי מועד הנפקת הקוד|היום|7 ימים|מתחילת החודש", H.join("|"));
  const line = l => T.find(r => r[0].startsWith(l)) || [], v = (l, i) => (line(l)[i] || "").split(" ")[0].replace(/[^\d%.]/g, "");
  const exp = { "קודים שהונפקו": [4, 6, 8], "נוצלו": [1, 2, 3], "נדחו": [1, 2, 2], "פגו בלי החלטה": [1, 1, 2], "עדיין בתוקף": [1, 1, 1] };
  for (const k in exp) ok("count " + k + " = " + exp[k], exp[k].every((x, i) => parseInt(v(k, i + 1)) === x), [1, 2, 3].map(i => line(k)[i]).join(" / "));
  ok("used % of issued: 25%", /25%/.test(line("נוצלו")[1]), line("נוצלו")[1]);
  ok("conversion 25% / 33% / 38%", ["25%", "33%", "38%"].every((x, i) => line("אחוז המרה")[i + 1] === x), line("אחוז המרה").join("|"));
  ok("not opened = חסר נתון", [1, 2, 3].every(i => line("לא נפתחו")[i] === "חסר נתון"), line("לא נפתחו").join("|"));
  ok("purchases 1 / 2 (+1 refunded) / 3", parseInt(line("רכישות אפסייל")[1]) === 1 && /^2 1 הוחזרו/.test(line("רכישות אפסייל")[2]) && /^3 1 הוחזרו/.test(line("רכישות אפסייל")[3]), line("רכישות אפסייל").join("|"));
  ok("revenue 97 / 194 / 291", ["97 ₪", "194 ₪", "291 ₪"].every((x, i) => line("הכנסה מאפסייל")[i + 1] === x), line("הכנסה מאפסייל").join("|"));
  ok("commission 72 / 72 / 144", ["72 ₪", "72 ₪", "144 ₪"].every((x, i) => line("עמלות אפסייל")[i + 1] === x), line("עמלות אפסייל").join("|"));
  const ar = nm => A.find(r => r[0].startsWith(nm)) || [];
  ok("aff גל: 72 (1) / 72 (1, 1 refunded) / 72", ar("גל")[1] === "72 ₪ 1 רכישות" && ar("גל")[2] === "72 ₪ 1 רכישות · 1 הוחזרו" && ar("גל")[3] === "72 ₪ 1 רכישות · 1 הוחזרו", ar("גל").join("|"));
  ok("aff אמיר: 0 / 0 / 72", ar("אמיר")[1] === "0 ₪ 0 רכישות" && ar("אמיר")[3] === "72 ₪ 1 רכישות", ar("אמיר").join("|"));
  ok("no-aff row 0 / 1 / 1", ar("בלי משווק")[1] === "0 רכישות" && ar("בלי משווק")[2] === "1 רכישות" && ar("בלי משווק")[3] === "1 רכישות", ar("בלי משווק").join("|"));
  const src = await B.p.evaluate(() => { const e = document.getElementById("upSrc"); return e.hidden ? "" : e.innerText });
  ok("banner: not-opened missing", /לא נפתחו/.test(src) && /חסר נתון/.test(src), src);
  ok("one upsell call", B.calls.filter(a => a === "upsell").length === 1, B.calls.join(","));
  ok("no JS errors (with route)", !B.errs.length, B.errs.join("|"));
  // כולל בדיקות: הקוד עם test=true והקוד של עסקת הבדיקה נספרים
  await B.p.click("#showTests"); await B.p.waitForTimeout(400);
  const T2 = await grab(B, "upTable"); ok("with tests: issued today 6", parseInt((T2.find(r => r[0].startsWith("קודים שהונפקו")) || [])[1]) === 6, JSON.stringify(T2[1]));
  // שדה opened עתידי
  const UPS_O = UPS.replace("up_deal\n", "up_deal\topened\n").split("\n").map((l, i) => i === 0 ? l : l + (i === 1 ? "\t2026-11-14 10:01:00" : i === 2 ? "\t2026-11-14 11:01:00" : "\t")).join("\n");
  const Bo = await run(P, UPS_O); const To = await grab(Bo, "upTable"), lo = To.find(r => r[0].startsWith("לא נפתחו"));
  ok("with opened field: not opened today = 2 (50%)", lo && /^2/.test(lo[1]) && /50%/.test(lo[1]), lo && lo.join("|"));
  ok("with opened field: banner hidden", await Bo.p.evaluate(() => document.getElementById("upSrc").hidden));
  // 2. בלי הנתיב (Make מחזיר Accepted)
  const N = await run(P, null); const Tn = await grab(N, "upTable"), ln = l => Tn.find(r => r[0].startsWith(l)) || [];
  ok("no route: codes = חסר נתון", ln("קודים שהונפקו")[1] === "חסר נתון" && ln("אחוז המרה")[2] === "חסר נתון", ln("קודים שהונפקו").join("|"));
  ok("no route: revenue still from sheet 291", ln("הכנסה מאפסייל")[3] === "291 ₪", ln("הכנסה מאפסייל").join("|"));
  const sn = await N.p.evaluate(() => { const e = document.getElementById("upSrc"); return e.hidden ? "" : e.className + " " + e.innerText });
  ok("no route: warn banner", /warn/.test(sn) && /לא מחובר/.test(sn), sn);
  ok("no JS errors (no route)", !N.errs.length, N.errs.join("|"));
  // 3. שאר הלשוניות לא השתנו, ואין קריאת upsell כשלא נכנסים ללשונית
  const Ao = await run(O, UPS, "fin"), Bf = await run(P, UPS, "fin");
  ok("no upsell call outside the tab", !Bf.calls.includes("upsell"), Bf.calls.join(","));
  const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
  for (const s of ["snap", "ov", "co", "lp", "af", "fin"]) ok("screen " + s + " unchanged", (await scr(Ao, s)) === (await scr(Bf, s)));
  ok("tab button 12 אפסייל", await Bf.p.evaluate(() => !!document.querySelector('nav.tabs button[data-s="up"]') && document.querySelector('nav.tabs button[data-s="up"]').innerText.includes("אפסייל")));
  const cl = await Bf.p.evaluate(() => CHANGELOG[0][1]); ok("changelog ב91", /ב91/.test(cl), cl.slice(0, 60));
  // טלפון: בלי גלילה הצידה
  const ph = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, timezoneId: "Asia/Jerusalem" }); await ph.clock.setFixedTime(new Date("2026-11-14T22:00:00+02:00"));
  await ph.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: P });
    if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: a === "upsell" ? UPS : { rows: EV, spend: "spend\n", affiliates: AFF, refunds: "refunds\n800012\t2026-11-13\n", paid: "paid\tat\taff\n", ads: "ads\n" }[a] || "" }) }
    return r.fulfill({ status: 204, body: "" }) });
  const pp = await ph.newPage(); await pp.goto("https://local.test/nlp/dashboard.html#up"); await pp.waitForTimeout(2500);
  const sw = await pp.evaluate(() => document.documentElement.scrollWidth); ok("phone: no horizontal page scroll", sw <= 390, sw);
  await pp.screenshot({ path: __dirname + "/shot_upsell_phone.png", fullPage: true });
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0)
})();
