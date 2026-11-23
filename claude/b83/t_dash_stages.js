// ב83: בדיקה מקומית לפאנל "מעברים בין שלבים" (לשונית 06). נתונים מדומים בלבד.
// node t_dash_stages.js <dashboard אחרי התיקון> <dashboard המקורי>
process.env.TZ = "Asia/Jerusalem";
const {chromium} = require("playwright"); const fs = require("fs");
const PAGE = fs.readFileSync(process.argv[2], "utf8"), ORIG = fs.readFileSync(process.argv[3], "utf8");
const pad = n => String(n).padStart(2, "0"), now = new Date();
const ts = m => {const d = new Date(+now - m * 6e4); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds())};
const COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const R = []; const row = o => R.push(COLS.map(k => o[k] == null ? "" : o[k]).join("\t"));
const ST = ["hook","pain","cause","old","solution","method","result","proof","course","offer","objections","guarantee","close"];
// a5v5 (int=1): p1 עד הסוף + סליקה, p2 עד proof, p3 רק hook, p4 hook+pain. מספר הסקשן של "ההצעה" = 16
const v5 = (id, upto, maxs, chk) => {const b = {variant: "a5v5", sid: "s" + id, vid: "v" + id, x: "int=1", dev: "m-ios-sf"};
 row({...b, ts: ts(30), ev: "view", max_section: 1});
 ST.slice(0, upto).forEach((s, i) => row({...b, ts: ts(29 - i), ev: "section_view", name: s, section: i + 1, max_section: maxs}));
 if (maxs >= 16) row({...b, ts: ts(10), ev: "section", section: 16, name: "ההצעה", max_section: 16});
 if (chk) row({...b, ts: ts(5), ev: "checkout_view"});};
v5(1, 13, 18, true); v5(2, 8, 12, false); v5(3, 1, 1, false); v5(4, 2, 3, false);
// a5v4 (int=1): שני אנשים, סדר שונה בדף (proof לפני pain)
const v4o = ["hook","proof","pain","cause","old","result","course","solution","offer","method","objections","guarantee","close"];
[["7", 13], ["8", 2], ["9", 1]].forEach(([id, upto]) => {const b = {variant: "a5v4", sid: "s" + id, vid: "v" + id, x: "int=1"};
 row({...b, ts: ts(30), ev: "view"}); v4o.slice(0, upto).forEach((s, i) => row({...b, ts: ts(29 - i), ev: "section_view", name: s, section: i + 1, max_section: i + 2}));});
// a5 חי (בלי בדיקה): 3 אנשים, 2 עברו מסך ראשון, 1 הגיע להצעה (סקשן 6) ולסליקה; בלי section_view
[["a", 1], ["b", 3], ["c", 7]].forEach(([id, m]) => {const b = {variant: "a5", sid: "s" + id, vid: "v" + id};
 row({...b, ts: ts(20), ev: "view", max_section: 1}); row({...b, ts: ts(19), ev: "scroll", max_section: m});
 if (m >= 6) {row({...b, ts: ts(18), ev: "section", section: 6, name: "ההצעה", max_section: 6}); row({...b, ts: ts(17), ev: "checkout_view"})}});
const ROWS = R.join("\n") + "\n";
let fails = 0, n = 0; const ok = (name, c, info) => {n++; if (!c) {fails++; console.log("FAIL", name, info || "")} else console.log("PASS", name)};
(async () => {
 const b = await chromium.launch();
 const mk = async html => {const c = await b.newContext({viewport: {width: 1440, height: 900}, timezoneId: "Asia/Jerusalem"}); const errs = [];
  await c.route("**/*", r => {const u = r.request().url();
   if (u.startsWith("https://local.test/")) return r.fulfill({status: 200, contentType: "text/html; charset=utf-8", body: html});
   if (u.includes("hook.eu1.make.com")) {const a = new URL(u).searchParams.get("action"); return r.fulfill({status: 200, body: {rows: ROWS, spend: "key\tvalue\n", affiliates: "affiliates\tname\tpct\tactive\tfee\n", refunds: "refunds\n", paid: "paid\n"}[a] || ""})}
   return r.fulfill({status: 204, body: ""})});
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); return {c, p, errs}};
 const T = sel => [...document.querySelectorAll(sel + " tr")].map(r => [...r.children].map(x => x.innerText.replace(/\s+/g, " ").replace(/% (\d)/g, "%$1").trim()));
 {const X = await mk(PAGE); const {p} = X; await p.goto("https://local.test/nlp/dashboard.html#ex", {waitUntil: "load"}); await p.waitForTimeout(1000);
  await p.click('#range button[data-r="today"]'); await p.waitForTimeout(300);
  let top = await p.evaluate(T, "#stTop");
  ok("without tests: only live a5 shown", top.length === 2 && top[1][0] === "a5 (חי)", JSON.stringify(top));
  ok("a5: 3 people, first screen 67% (2/3), offer 33% (1/3), checkout 33%", JSON.stringify(top[1].slice(1)) === JSON.stringify(["3", "67%2/3", "33%1/3", "33%1/3"]), JSON.stringify(top[1]));
  ok("stages table empty with note about int=1", (await p.innerText("#stTable")).includes("כולל בדיקות"));
  await p.check("#showTests"); await p.waitForTimeout(300);
  top = await p.evaluate(T, "#stTop");
  const r5 = top.find(r => r[0] === "a5v5 (בדיקה)") || [];
  ok("with tests: a5v5 row - 4 people, first screen 3/4, offer 1/4, checkout 1/4", JSON.stringify(r5.slice(1)) === JSON.stringify(["4", "75%3/4", "25%1/4", "25%1/4"]), JSON.stringify(top));
  const st = await p.evaluate(T, "#stTable"); const H = st[0]; const i5 = H.findIndex(h => h.startsWith("a5v5")), i4 = H.findIndex(h => h.startsWith("a5v4"));
  ok("stages table: 13 rows + header, columns a5v4 and a5v5", st.length === 14 && i5 > 0 && i4 > 0, JSON.stringify(H));
  const cellOf = (k, i) => (st.find(r => r[0].endsWith(k)) || [])[i];
  ok("a5v5 hook 100% (4/4), first stage without 'from previous'", cellOf("hook", i5) === "100%4", cellOf("hook", i5));
  ok("a5v5 pain 75% (3/4) · 75% from previous", cellOf("pain", i5) === "75%3 · 75% מהשלב הקודם", cellOf("pain", i5));
  ok("a5v5 proof 50% (2/4) · 100%, offer 25% · 100% from previous (course)", cellOf("proof", i5) === "50%2 · 100% מהשלב הקודם" && cellOf("offer", i5) === "25%1 · 100% מהשלב הקודם", cellOf("proof", i5) + " | " + cellOf("offer", i5));
  ok("a5v5 cause 50% · 67% from previous", cellOf("cause", i5) === "50%2 · 67% מהשלב הקודם", cellOf("cause", i5));
  ok("a5v4 uses its own page order: pain after proof (1/3 · 50% of proof, not 33% of hook)", cellOf("pain", i4) === "33%1 · 50% מהשלב הקודם" && cellOf("proof", i4) === "67%2 · 67% מהשלב הקודם", cellOf("pain", i4) + " | " + cellOf("proof", i4));
  ok("no JS errors", X.errs.length === 0, X.errs.join(" | "));
  await p.screenshot({path: __dirname + "/stages_dash.png", fullPage: false, clip: {x: 0, y: 0, width: 1440, height: 900}});
  await X.c.close()}
 for (const tab of ["ov", "af", "co", "hub"]) {const a = await mk(ORIG), bb = await mk(PAGE);
  for (const X of [a, bb]) {await X.p.goto("https://local.test/nlp/dashboard.html#" + tab, {waitUntil: "load"}); await X.p.waitForTimeout(900)}
  const g = X => X.p.evaluate(t => document.getElementById("s-" + t).innerText.replace(/עודכן \d\d:\d\d/g, ""), tab);
  const [x, y] = [await g(a), await g(bb)]; ok("tab " + tab + " unchanged", x === y && x.length > 30, x.length + " vs " + y.length);
  await a.c.close(); await bb.c.close()}
 console.log("TOTAL", n - fails + "/" + n); await b.close(); process.exit(fails ? 1 : 0)})();
