// ב86: בדיקה מקומית למסך "תמונת מצב". חלק א - נתונים מדומים (כללים). חלק ב - ייצוא אמיתי של האירועים (קבלה מול הראשי) + צילומי 390x844.
// node t_b86.js <dashboard אחרי התיקון> <dashboard המקורי> <ev.tsv> <spend.tsv>
process.env.TZ = "Asia/Jerusalem";
const {chromium} = require("playwright"); const fs = require("fs");
const [PAGE, ORIG, EV, SPEND] = process.argv.slice(2, 6).map(f => fs.readFileSync(f, "utf8"));
const ADS = JSON.parse(fs.readFileSync(__dirname + "/ads_dict.json", "utf8"));
const NOW = new Date("2026-11-12T13:00:00+02:00");
const COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const pad = n => String(n).padStart(2, "0"), fmtTs = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":00";
let fails = 0, n = 0; const ok = (name, c, info) => {n++; if (!c) {fails++; console.log("FAIL", name, info || "")} else console.log("PASS", name)};

/* --- נתונים מדומים: 3 מודעות מהמילון + קוד לא מזוהה + ביקור פנימי --- */
const [G, R, Y] = ["p24", "w31a4", "warm3_chg_pain"], NM = c => ADS.find(a => a[0] === c)[1];
const F = []; const row = o => F.push(COLS.map(k => o[k] == null ? "" : o[k]).join("\t"));
const T0 = new Date("2026-11-10T10:00:00+02:00"); let k = 0;
const sess = (code, v, opt = {}) => {const i = ++k, sid = "s" + i, vid = opt.vid || "v" + i, t = new Date(+T0 + i * 6e4), b = {variant: v, sid, vid};
 row({...b, ts: fmtTs(t), ev: "view", qs: "go=1&utm_content=" + code, max_section: 1});
 if (opt.chk) row({...b, ts: fmtTs(new Date(+t + 3e4)), ev: "checkout_view"});
 if (opt.start) row({...b, ts: fmtTs(new Date(+t + 4e4)), ev: "checkout_contact_started"});
 if (opt.pay) row({...b, ts: fmtTs(new Date(+t + 5e4)), ev: "checkout_payment_viewed"});
 if (opt.buy) row({...b, ts: fmtTs(new Date(+t + 6e4)), ev: "purchase", cta: "cardcom_webhook", qs: "cardcom | 297 ILS | deal 9" + i + " | src facebook"});
 if (opt.test) row({...b, ts: fmtTs(new Date(+t + 7e4)), ev: "view", qs: "claude=1"});};
for (let i = 0; i < 10; i++) sess(G, "a5v6", {chk: i < 2, start: i < 2, pay: i < 1, buy: i < 1});
for (let i = 0; i < 5; i++) sess(R, "pr2");
for (let i = 0; i < 8; i++) sess(Y, "pr2", {chk: i < 1});
sess("zz_new_ad", "a5v6"); sess("zz_new_ad", "a5v6");
sess(G, "a5v6", {vid: "fead4466-0000", chk: true, buy: true});        // מזהה הבדיקה של הממומן - לא נספר
sess(Y, "pr2", {vid: "vint", chk: true}); sess(Y, "pr2", {vid: "vint", test: true}); // מבקר שהופיע בבדיקה - לא נספר בכלל
const FROWS = F.join("\n") + "\n";
const FSP = "key\tvalue\n2026-11-10\t600\n2026-11-10|" + G + "\t200\n2026-11-10|" + R.toUpperCase() + "\t260\n2026-11-10|" + Y + "\t60\n";

(async () => {
 const b = await chromium.launch();
 const mk = async (html, rowsTxt, spendTxt, vp) => {const c = await b.newContext({viewport: vp || {width: 1440, height: 900}, deviceScaleFactor: vp ? 2 : 1, timezoneId: "Asia/Jerusalem"}); const errs = [];
  await c.clock.setFixedTime(NOW);
  await c.route("**/*", r => {const u = r.request().url();
   if (u.startsWith("https://local.test/")) return r.fulfill({status: 200, contentType: "text/html; charset=utf-8", body: html});
   if (u.includes("hook.eu1.make.com")) {const a = new URL(u).searchParams.get("action"); return r.fulfill({status: 200, body: {rows: rowsTxt, spend: spendTxt, affiliates: "affiliates\tname\tpct\tactive\tfee\n", refunds: "refunds\n", paid: "paid\n"}[a] || ""})}
   return r.fulfill({status: 204, body: ""})});
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); return {c, p, errs}};
 const T = sel => [...document.querySelectorAll(sel + " tr")].map(r => [...r.children].map(x => x.innerText.replace(/\s+/g, " ").trim()));
 const kpi = p => p.$$eval("#snapKpi .tile", ts => ts.map(t => [t.querySelector(".k").innerText, t.querySelector(".v").innerText.trim(), t.querySelector(".d").innerText.trim()]));

 /* ===== חלק א: כללים על נתונים מדומים ===== */
 {const X = await mk(PAGE, FROWS, FSP); const {p} = X;
  await p.goto("https://local.test/nlp/dashboard.html", {waitUntil: "load"}); await p.waitForTimeout(900);
  ok("default screen is snap (no hash)", await p.evaluate(() => screen === "snap" && document.getElementById("s-snap").classList.contains("on")));
  ok("only 'תמונת מצב' and 'מתקדם' visible in nav", JSON.stringify(await p.$$eval("nav.tabs button", bs => bs.filter(x => x.offsetParent).map(x => x.innerText.trim()))) === JSON.stringify(["◎תמונת מצב", "מתקדם ▾"]));
  ok("global filters hidden on snap", await p.evaluate(() => ["range", "fSrc", "fOwn", "fDev", "showTests"].every(i => !document.getElementById(i).offsetParent)));
  ok("default period: השבוע pressed", await p.getAttribute('#snapPer button[data-p="week"]', "aria-pressed") === "true");
  const K = await kpi(p);
  ok("KPI: spend 600", K[0][1] === "600 ₪", JSON.stringify(K[0]));
  ok("KPI: 1 verified purchase (the fead4466 test purchase excluded), CPA 600", K[2][1] === "1" && K[3][1] === "600 ₪", JSON.stringify(K));
  const ads = await p.evaluate(T, "#snapAds"), byName = nm => ads.find(r => r[0].startsWith(nm)) || [];
  ok("ads: green ad by name, 10 people (fead4466 excluded), 2 checkout, 1 purchase, spend 200, CPA 200", JSON.stringify(byName(NM(G)).slice(1, 6)) === JSON.stringify(["10", "2 20%", "1", "200 ₪ יום אחד", "200 ₪"]), JSON.stringify(byName(NM(G))));
  ok("ads: spend matched case-insensitively (W31A4 → w31a4) 260", byName(NM(R))[4] === "260 ₪ יום אחד", JSON.stringify(byName(NM(R))));
  ok("ads: yellow ad 8 people (internal vid excluded)", byName(NM(Y))[1] === "8", JSON.stringify(byName(NM(Y))));
  ok("ads: unknown code shown as 'לא מזוהה'", ads.some(r => r[0] === "לא מזוהה" && r[1] === "2"), JSON.stringify(ads.map(r => r[0])));
  ok("ads: code only in hover (title), not in the cell text", (await p.getAttribute('#snapAds b[title="קוד: ' + G + '"]', "title")) && !ads.some(r => r[0].includes(G)));
  ok("ads note lists unknown count", (await p.innerText("#snapAdsNote")).includes("לא מזוהים (1)"));
  const L = await p.$$eval("#snapLines .snap-line", ls => ls.map(l => [l.className.split(" ")[1], l.innerText]));
  ok("3 lines: green, yellow, red", L.map(l => l[0]).join() === "g,y,r", JSON.stringify(L));
  ok("green = " + G + " (CPA 200 ≤ 245)", L[0][1].includes(NM(G)) && L[0][1].includes("200 ₪"), L[0][1]);
  ok("yellow = " + Y + " (60 ₪ per checkout > 35)", L[1][1].includes(NM(Y)) && L[1][1].includes("60 ₪"), L[1][1]);
  ok("red = " + R + " (260 ₪ no checkout ≥ 250) → stop", L[2][1].includes(NM(R)) && L[2][1].includes("לעצור"), L[2][1]);
  ok("no code shown in lines", !L.some(l => /p24|w31a4|warm3/.test(l[1])));
  const pg = await p.evaluate(T, "#snapPages"), r6 = pg.find(r => r[0].includes("a5v6")) || [];
  ok("pages: a5v6 12 people (10 + 2 unknown), 2 checkout, 2 started, 1 payment, 1 purchase", JSON.stringify(r6.slice(1)) === JSON.stringify(["12", "2 17%", "2 17%", "1 8.3%", "1 8.3%"]), JSON.stringify(r6));
  const co = await p.evaluate(T, "#snapCo");
  ok("checkout table: 3 people reached checkout (A unknown → 'לא ידוע')", co.length === 2 && co[1][1] === "3", JSON.stringify(co));
  await p.click('#snapPer button[data-p="today"]'); await p.waitForTimeout(200);
  ok("today (12.11): no spend, no sessions", (await kpi(p))[0][1] === "-" && (await p.innerText("#snapAds")).includes("אין כניסות"));
  await p.click("#advT"); await p.waitForTimeout(150);
  ok("'מתקדם' opens the existing 13 tabs", (await p.$$eval("nav.tabs button[data-s]", bs => bs.filter(x => x.offsetParent).length)) === 14);
  await p.click('nav.tabs button[data-s="ov"]'); await p.waitForTimeout(300);
  ok("advanced tab works and filters return", await p.evaluate(() => document.getElementById("s-ov").classList.contains("on") && !!document.getElementById("range").offsetParent));
  await p.click('nav.tabs button[data-s="snap"]'); await p.waitForTimeout(200);
  ok("back to snap: advanced tabs stay open until toggled", await p.evaluate(() => document.getElementById("tabsNav").classList.contains("open")));
  await p.click("#advT"); await p.waitForTimeout(150);
  ok("toggle closes advanced", (await p.$$eval("nav.tabs button[data-s]", bs => bs.filter(x => x.offsetParent).length)) === 1);
  ok("no JS errors (fixtures)", X.errs.length === 0, X.errs.join(" | "));
  await X.c.close()}

 /* ===== חלק ב: ייצוא אמיתי ===== */
 {const X = await mk(PAGE, EV, SPEND); const {p} = X;
  await p.goto("https://local.test/nlp/dashboard.html", {waitUntil: "load"}); await p.waitForTimeout(2500);
  const K = await kpi(p);
  ok("week (08.11-12.11) spend = 585.01+248.93+271.36, entered until 10.11", K[0][1] === "1,105 ₪" && K[0][2].includes("מוזן עד 10.11"), JSON.stringify(K[0]));
  console.log("  week KPI:", JSON.stringify(K));
  // קבלה: 08.11 14:19 עד 12.11 09:26, תנועת go.html בלבד
  await p.check("#snapGo");
  await p.evaluate(() => {snapBounds = () => ({a: new Date("2026-11-08T14:19:00"), b: new Date("2026-11-12T09:26:00")}); render()});
  const pg = await p.evaluate(T, "#snapPages"), row = v => (pg.find(r => r[0].includes("(" + v + ")")) || []).slice(1).map(x => x.split(" ")[0]);
  console.log("  acceptance pages:", JSON.stringify(pg));
  ok("acceptance pr2 = 655, 13, 3, 2, 1", row("pr2").join() === "655,13,3,2,1", row("pr2").join());
  const a5 = row("a5"); ok("acceptance a5 = 608, (8 vs main 7), 1, 1, 1", a5[0] === "608" && a5.slice(2).join() === "1,1,1" && (a5[1] === "7" || a5[1] === "8"), a5.join());
  console.log("  a5 checkout people:", a5[1], "(main: 7)");
  ok("no JS errors (real data)", X.errs.length === 0, X.errs.join(" | "));
  await X.c.close()}

 /* ===== טלפון 390x844 + צילומים ===== */
 for (const per of ["week", "30"]) {const X = await mk(PAGE, EV, SPEND, {width: 390, height: 844}); const {p} = X;
  await p.goto("https://local.test/nlp/dashboard.html", {waitUntil: "load"}); await p.waitForTimeout(2500);
  if (per !== "week") {await p.click('#snapPer button[data-p="' + per + '"]'); await p.waitForTimeout(400)}
  const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  ok("phone 390x844 (" + per + "): no horizontal page scroll", ov <= 0, ov);
  if (per === "30") {const L = await p.$$eval("#snapLines .snap-line", ls => ls.map(l => [l.className.split(" ")[1], l.innerText])); ok("30d lines consistent: yellow line never claims a cost ≤35 is above 35", !L.some(l => l[0] === "y" && /(^|\D)([0-9]|[12][0-9]|3[0-5]) ₪ לכל מי שהגיע לסליקה, מעל 35/.test(l[1])), JSON.stringify(L))}
  if (per === "30") console.log("  30d lines:", JSON.stringify(await p.$$eval("#snapLines .snap-line", ls => ls.map(l => l.innerText))));
  await p.screenshot({path: __dirname + "/b86_phone_" + per + "_top.png"});
  await p.screenshot({path: __dirname + "/b86_phone_" + per + "_full.png", fullPage: true});
  ok("no JS errors (phone " + per + ")", X.errs.length === 0, X.errs.join(" | "));
  await X.c.close()}
 {const X = await mk(PAGE, EV, SPEND); await X.p.goto("https://local.test/nlp/dashboard.html", {waitUntil: "load"}); await X.p.waitForTimeout(2500);
  await X.p.screenshot({path: __dirname + "/b86_desktop_week.png", fullPage: true}); await X.c.close()}

 /* ===== הלשוניות הקיימות לא השתנו ===== */
 for (const tab of ["op", "ov", "lab", "af", "co", "hub", "ex"]) {const a = await mk(ORIG, EV, SPEND), bb = await mk(PAGE, EV, SPEND);
  for (const X of [a, bb]) {await X.p.goto("https://local.test/nlp/dashboard.html#" + tab, {waitUntil: "load"}); await X.p.waitForTimeout(2200)}
  const g = X => X.p.evaluate(t => document.getElementById("s-" + t).innerText.replace(/עודכן \d\d:\d\d/g, ""), tab);
  const [x, y] = [await g(a), await g(bb)]; ok("tab " + tab + " unchanged (via #" + tab + ")", x === y && x.length > 30, x.length + " vs " + y.length);
  await a.c.close(); await bb.c.close()}
 console.log("TOTAL", n - fails + "/" + n); await b.close(); process.exit(fails ? 1 : 0)})();
