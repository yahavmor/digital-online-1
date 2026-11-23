// ב84: בדיקה מקומית של לשונית "בקרה כספית". נתונים מדומים בלבד (בלי Make, בלי פרטים אישיים).
// node t_b84.js <dashboard_b84.html> <dashboard המקורי>
process.env.TZ = "Asia/Jerusalem";
const {chromium} = require("playwright"); const fs = require("fs");
const PAGE = fs.readFileSync(process.argv[2], "utf8"), ORIG = fs.readFileSync(process.argv[3], "utf8");
const pad = n => String(n).padStart(2, "0"), now = new Date();
const at = (dd, h = 12) => {const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - dd, h, 0, 0); return d};
const ts = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":00";
const day = d => ts(d).slice(0, 10);
const COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const R = []; const row = o => R.push(COLS.map(k => o[k] == null ? "" : o[k]).join("\t"));
const h = Math.min(now.getHours(), 10); // שעה של היום שכבר עברה
// כניסות של gal: 3 אנשים, 2 הגיעו לסליקה, ועוד ביקור סריקה של Meta שלא נספר
[["g1","v1",1],["g2","v2",1],["g3","v3",0]].forEach(([sid,vid,chk])=>{row({ts:ts(at(1,9)),ev:"view",variant:"a5",sid,vid,qs:"utm_source=fb&aff=gal",x:"aff=gal",dev:"m-ios-fb"});if(chk)row({ts:ts(at(1,9)).replace(":00:00",":05:00"),ev:"checkout_view",variant:"a5",sid,vid,x:"aff=gal"})});
row({ts:ts(at(1,9)),ev:"meta_scan",variant:"a5",sid:"g4",vid:"v4",x:"aff=gal"});
// רכישות דרך gal: 100101 לפני 12 ימים (לתשלום, באיחור 5 ימים), 100102 לפני יומיים (ממתינה), 100103 שולמה, 100104 הוחזרה, העברה בנקאית אתמול, אפסייל לפני יומיים
const buy = (d, deal, aff, sid) => row({ts:ts(d),ev:"purchase",variant:"a5",sid:sid||"",qs:"297 ILS | deal "+deal,cta:"cardcom_page_webhook",x:aff?"aff="+aff:""});
buy(at(12),"100101","gal","g1"); buy(at(2),"100102","gal","g2"); buy(at(9),"100103","gal"); buy(at(8),"100104","gal");
row({ts:ts(at(1)),ev:"purchase",variant:"a5",qs:"297 ILS | ref 77881234 | aff gal",cta:"manual_bank_transfer"});
row({ts:ts(at(2)),ev:"upsell_purchase",variant:"a5",qs:"97 ILS | deal 200201 | course_deal 100102",cta:"cardcom_upsell_webhook",x:"aff=gal"});
// שלנו: רכישה אתמול, רכישה היום, אפסייל היום
buy(at(1),"100201",""); buy(at(0,h),"100202","");
row({ts:ts(at(0,h)),ev:"upsell_purchase",variant:"a5",qs:"97 ILS | deal 200202 | course_deal 100202",cta:"cardcom_upsell_webhook"});
const ROWS = R.join("\n") + "\n";
// הוצאה: שלנו 10 ימים אחורה בלי יום אחד (לפני 3 ימים); gal - 3 ימים, אחד מהם 150 ₪
let SP = "key\tvalue\n"; for (let i = 1; i <= 10; i++) if (i !== 3) SP += day(at(i)) + "\t100\n";
SP += day(at(1)) + "|aff_gal\t80\n" + day(at(2)) + "|aff_gal\t150\n" + day(at(2)) + "|aff_gal_ic\t0\n" + day(at(1)) + "|aff_gal_ic\t10\n";
const AFF0 = "affiliates\tname\tpct\tactive\tfee\ngal\tגל\t74\ttrue\t220\namir\tאמיר\t74\ttrue\t0\n";
const AFF1 = "affiliates\tname\tpct\tactive\tfee\tbudget\ngal\tגל\t74\ttrue\t220\t100\namir\tאמיר\t74\ttrue\t0\t\n";
const REFS = "refunds\tat\taff\n100104\t" + at(5).toISOString() + "\tgal\n";
const PAID = "paid\tat\taff\n100103\t" + at(1).toISOString() + "\tgal\n";

let fails = 0, n = 0; const ok = (name, c, info) => {n++; if (!c) {fails++; console.log("FAIL", name, info || "")}};
(async () => {
 const b = await chromium.launch();
 const mk = async (affs, html, vp) => {
  const c = await b.newContext({viewport: vp || {width: 1440, height: 900}, timezoneId: "Asia/Jerusalem", deviceScaleFactor: 2, permissions: ["clipboard-read", "clipboard-write"]});
  const reqs = []; const errs = [];
  await c.route("**/*", r => {const u = r.request().url();
   if (u.startsWith("https://local.test/nlp/dashboard.html")) return r.fulfill({status: 200, contentType: "text/html; charset=utf-8", body: html});
   if (u.includes("hook.eu1.make.com")) {reqs.push(r.request().method() + " " + (new URL(u).searchParams.get("action") || "")); const a = new URL(u).searchParams.get("action");
    const body = {rows: ROWS, spend: SP, affiliates: affs, refunds: REFS, paid: PAID}[a]; return r.fulfill({status: 200, body: body == null ? "" : body, headers: {"access-control-allow-origin": "*"}})}
   return r.fulfill({status: 204, body: ""})});
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); p.on("console", m => {if (m.type() === "error") errs.push(m.text())});
  return {c, p, reqs, errs}};
 const T = sel => document.querySelector(sel) ? [...document.querySelectorAll(sel + " tr")].map(r => [...r.children].map(x => x.innerText.replace(/\s+/g, " ").trim())) : null;
 const go = async (X, tab) => {await X.p.goto("https://local.test/nlp/dashboard.html#" + tab, {waitUntil: "load"}); await X.p.waitForFunction(() => window.rows !== undefined || true); await X.p.waitForTimeout(900)};
 const per = async (X, k) => {await X.p.click('#finPer button[data-p="' + k + '"]'); await X.p.waitForTimeout(250)};

 // 1. בלי עמודת תקציב
 {const X = await mk(AFF0, PAGE); await go(X, "fin"); const {p} = X;
  ok("tab button 11", await p.isVisible('nav.tabs button[data-s="fin"]'));
  ok("screen visible", await p.isVisible("#s-fin"));
  await per(X, "all");
  const A = await p.evaluate(T, "#finAff"); const gal = A.find(r => r[0].startsWith("גל")) || [];
  const H = A[0]; const col = name => gal[H.indexOf(name)];
  ok("all: header", H.join("|") === "משווק|תקציב יומי|הוצאה בתקופה|הוצאה מצטברת|מהתקציב|כניסות|הגיעו לסליקה|רכישות קורס|הכנסה 297|הכנסה 97|עמלה ממתינה|עמלה לתשלום|עמלה ששולמה|הוחזרו|יתרה לתשלום|תשלום הבא|עלות לרכישה (מול 220 ₪)", H.join("|"));
  ok("all: budget missing", col("תקציב יומי") === "חסר נתון" && col("מהתקציב") === "חסר נתון", gal.join("|"));
  ok("all: spend period+cumulative = 240", col("הוצאה בתקופה") === "240 ₪" && col("הוצאה מצטברת") === "240 ₪", gal.join("|"));
  ok("all: people 3 (scan excluded), checkout 2", col("כניסות") === "3" && col("הגיעו לסליקה") === "2", gal.join("|"));
  ok("all: purchases 4 = 3 card + 1 bank", /^4 3 כרטיס · 1 העברה$/.test(col("רכישות קורס")), col("רכישות קורס"));
  ok("all: income 297 = 1,188, 97 = 97 (1)", col("הכנסה 297") === "1,188 ₪" && col("הכנסה 97") === "97 ₪ 1", col("הכנסה 297") + " / " + col("הכנסה 97"));
  ok("all: commissions pending 512 (220+220+72), due 220, paid 220, refunds 1", col("עמלה ממתינה") === "512 ₪" && col("עמלה לתשלום") === "220 ₪" && col("עמלה ששולמה") === "220 ₪" && col("הוחזרו") === "1", gal.join("|"));
  const sun = await p.evaluate(() => {const n = new Date(), s = new Date(n.getFullYear(), n.getMonth(), n.getDate()); s.setDate(s.getDate() + (7 - s.getDay()) % 7); return s.toLocaleDateString("he-IL", {day: "2-digit", month: "2-digit", year: "numeric"})});
  ok("all: balance 220, next payment = coming Sunday", col("יתרה לתשלום") === "220 ₪" && col("תשלום הבא") === sun, col("תשלום הבא") + " vs " + sun);
  ok("all: cost per purchase 60 ≤ 220", /^60 ₪ עד 220 ₪$/.test(col("עלות לרכישה (מול 220 ₪)")), col("עלות לרכישה (מול 220 ₪)"));
  const amir = A.find(r => r[0].startsWith("אמיר")) || [];
  ok("amir row present, zero", amir.length === H.length && amir[H.indexOf("עמלה ממתינה")] === "0 ₪", amir.join("|"));
  // אצלנו
  const us = await p.evaluate(() => Object.fromEntries([...document.querySelectorAll("#finUs .tile")].map(t => [t.querySelector(".k").innerText.trim(), t.querySelector(".v").innerText.trim() + " || " + t.querySelector(".d").innerText.trim()])));
  ok("us: spend 900", us["הוצאה (החשבון שלנו)"].startsWith("900 ₪"), us["הוצאה (החשבון שלנו)"]);
  ok("us: income 1,976 (6 course + 2 upsell, refund out)", us["הכנסה מאומתת"].startsWith("1,976 ₪") && /6 קורס · 2 אפסייל/.test(us["הכנסה מאומתת"]), us["הכנסה מאומתת"]);
  ok("us: VAT 301", us["מע\"מ 18%"].startsWith("301 ₪"), us["מע\"מ 18%"]);
  ok("us: processing fees missing", us["עמלות סליקה"].startsWith("חסר נתון"), us["עמלות סליקה"]);
  ok("us: affiliate commissions 952", us["עמלות משווקים"].startsWith("952 ₪"), us["עמלות משווקים"]);
  ok("us: net = 1976/1.18 - 900 - 952 = -177", us["נטו לפני מס"].startsWith(Math.round(1976 / 1.18 - 900 - 952).toLocaleString("he-IL") + " ₪") || us["נטו לפני מס"].startsWith("‎-177 ₪") || /-177 ₪|177- ₪|‏-177/.test(us["נטו לפני מס"]), us["נטו לפני מס"]);
  ok("us: cpa 450 > 245", /^450 ₪ \|\| מעל 245 ₪$/.test(us["עלות לרכישה"]), us["עלות לרכישה"]);
  ok("us: ROAS (2*297+97)/900 = 0.77", us["ROAS"].startsWith("0.77"), us["ROAS"]);
  ok("us: refunds 1 / 297", /^1 \|\| 297 ₪$/.test(us["החזרים"]), us["החזרים"]);
  // התראות
  const al = await p.evaluate(() => [...document.querySelectorAll("#finAlerts .banner")].map(x => x.className + " :: " + x.innerText.replace(/\s+/g, " ")));
  ok("alert: due > 3 days for gal (5 days)", al.some(a => /crit/.test(a) && /לתשלום" יותר מ-3 ימים/.test(a) && /גל: 1 עמלות, 220 ₪, הוותיקה - 5 ימים/.test(a)), al.join(" ## "));
  const miss = day(at(3)).slice(8, 10) + "." + day(at(3)).slice(5, 7);
  ok("alert: day without our spend (" + miss + ")", al.some(a => /יום בלי הזנת הוצאה/.test(a) && a.includes(miss)), al.join(" ## "));
  ok("alert: 120% check inactive without budget", al.some(a => /לא פעילה/.test(a) && /חסר תקציב יומי ל-2 משווקים/.test(a)), al.join(" ## "));
  // פירוט
  const D = await p.evaluate(T, "#finDet");
  ok("detail: header", D[0].join("|") === "תאריך|מוצר|עסקה|עמלה|סטטוס", D[0].join("|"));
  ok("detail: 6 rows for gal (all)", D.length === 7, D.length);
  const dt = D.map(r => r.join(" | ")).join("\n");
  ok("detail: no full deal numbers / bank ref", !/100101|100102|100103|100104|200201|77881234/.test(dt), dt);
  ok("detail: masked 'מסתיים ב-101' and bank 'העברה, מסתיים ב-234'", /מסתיים ב-101/.test(dt) && /העברה, מסתיים ב-234/.test(dt), dt);
  ok("detail: paid row has date + reference missing", /שולמה · \d\d\.\d\d\.\d{4} · אסמכתא חסר נתון/.test(dt), dt);
  ok("detail: refund struck and cancelled", /בוטלה \(החזר\)/.test(dt) && await p.evaluate(() => !!document.querySelector("#finDet s")), dt);
  ok("detail: upsell 72", /אפסייל 97 ₪ \| מסתיים ב-201 \| 72 ₪/.test(dt), dt);
  await p.click("#finCopy"); await p.waitForTimeout(200);
  const clip = await p.evaluate(() => navigator.clipboard.readText());
  ok("copy: text with header and rows, no full numbers", /^פירוט עמלות - גל/.test(clip) && clip.split("\n").length >= 8 && !/100101|77881234|200201/.test(clip), clip);
  ok("copy: button feedback", (await p.innerText("#finCopy")) === "הועתק");
  // תקופות
  await per(X, "today");
  const At = await p.evaluate(T, "#finAff"), galT = At.find(r => r[0].startsWith("גל"));
  ok("today: gal no purchases", galT[H.indexOf("רכישות קורס")].startsWith("0 "), galT.join("|"));
  const usT = await p.evaluate(() => [...document.querySelectorAll("#finUs .tile")].map(t => t.innerText.replace(/\s+/g, " ")).join(" ## "));
  ok("today: income 394 (1 course + 1 upsell)", /הכנסה מאומתת 394 ₪/.test(usT), usT);
  const alT = await p.evaluate(() => document.getElementById("finAlerts").innerText);
  ok("today: missing-day alert only checks yesterday (none)", !/יום בלי הזנת הוצאה/.test(alT), alT);
  ok("today: due alert still shown (all time)", /לתשלום" יותר מ-3 ימים/.test(alT), alT);
  await per(X, "7");
  const A7 = await p.evaluate(T, "#finAff"), g7 = A7.find(r => r[0].startsWith("גל"));
  ok("7d: gal 2 purchases (100102 + bank), pending 512", g7[H.indexOf("רכישות קורס")].startsWith("2 ") && g7[H.indexOf("עמלה ממתינה")] === "512 ₪" && g7[H.indexOf("יתרה לתשלום")] === "220 ₪", g7.join("|"));
  ok("7d: pressed state", await p.getAttribute('#finPer button[data-p="7"]', "aria-pressed") === "true");
  // קריאה בלבד: רק GET לחמש הפעולות הקיימות, בלי טפסים
  ok("read-only: only GET of rows/spend/affiliates/refunds/paid/ads", X.reqs.every(r => /^GET (rows|spend|affiliates|refunds|paid|ads)$/.test(r)), X.reqs.join(","));
  ok("read-only: no form/inputs in tab other than select", await p.evaluate(() => !document.querySelector("#s-fin form,#s-fin input,#s-fin textarea")));
  ok("global filters hidden on this tab", !(await p.isVisible("#range")) && !(await p.isVisible("#fOwn")) && await p.isVisible("#refresh"));
  await p.click('nav.tabs button[data-s="af"]'); await p.waitForTimeout(200);
  ok("global filters back on other tabs", await p.isVisible("#range") && await p.isVisible("#fOwn"));
  await p.click('nav.tabs button[data-s="fin"]'); await p.waitForTimeout(200);
  ok("no JS errors", X.errs.length === 0, X.errs.join(" | "));
  await per(X, "all"); await p.screenshot({path: __dirname + "/fin_desktop.png", fullPage: true});
  await X.c.close()}

 // 2. עם עמודת תקציב
 {const X = await mk(AFF1, PAGE); await go(X, "fin"); const {p} = X; await per(X, "all");
  const A = await p.evaluate(T, "#finAff"), H = A[0], gal = A.find(r => r[0].startsWith("גל")), amir = A.find(r => r[0].startsWith("אמיר"));
  ok("budget: gal 100 ₪/day", gal[H.indexOf("תקציב יומי")] === "100 ₪", gal.join("|"));
  ok("budget: amir empty -> missing", amir[H.indexOf("תקציב יומי")] === "חסר נתון");
  ok("budget: % of budget numeric", /^\d+(\.\d)?%$/.test(gal[H.indexOf("מהתקציב")]), gal[H.indexOf("מהתקציב")]);
  const al = await p.evaluate(() => document.getElementById("finAlerts").innerText.replace(/\s+/g, " "));
  const d2 = day(at(2)).slice(8, 10) + "." + day(at(2)).slice(5, 7);
  ok("alert: spend over 120% (150 > 120) on " + d2, /הוצאה מעל 120% מהתקציב/.test(al) && al.includes("גל: " + d2 + " 150 ₪") && !al.includes(day(at(1)).slice(8, 10) + "." + day(at(1)).slice(5, 7) + " 90"), al);
  ok("alert: 120% inactive line now only for amir", /חסר תקציב יומי ל-1 משווקים/.test(al), al);
  ok("no JS errors (budget)", X.errs.length === 0, X.errs.join(" | "));
  await X.c.close()}

 // 3. מובייל: בלי גלילה אופקית של הדף
 {const X = await mk(AFF0, PAGE, {width: 390, height: 844}); await go(X, "fin"); const {p} = X;
  ok("mobile: no page horizontal scroll", await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), await p.evaluate(() => document.documentElement.scrollWidth));
  await p.screenshot({path: __dirname + "/fin_mobile.png", fullPage: true}); await X.c.close()}

 // 4. הלשוניות הקיימות לא השתנו (09 משווקים, 01 סקירה)
 for (const tab of ["af", "ov", "hub"]) {const a = await mk(AFF0, ORIG), bb = await mk(AFF0, PAGE); await go(a, tab); await go(bb, tab);
  const g = X => X.p.evaluate(t => document.getElementById("s-" + t).innerText.replace(/עודכן \d\d:\d\d/g, ""), tab);
  const [x, y] = [await g(a), await g(bb)];
  ok("tab " + tab + " identical to current dashboard", x === y && x.length > 50, x.length + " vs " + y.length);
  ok("tab " + tab + " no JS errors", bb.errs.length === 0, bb.errs.join(" | ")); await a.c.close(); await bb.c.close()}

 console.log("TOTAL", n - fails + "/" + n); await b.close(); process.exit(fails ? 1 : 0)})();
