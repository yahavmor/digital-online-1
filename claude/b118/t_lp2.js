// ב118: בדיקת landing_option2 אחרי השינוי (נייד). שימוש: node t_lp2.js <root עם landing-pages/, funnels/, shared/, marketers/, nlp/, index.html>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT] = process.argv.slice(2); let n = 0, f = 0;
const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 500))) };
const CT = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".css": "text/css" };
const ALERT = "78f809msf3m36h2r8g2q4s6khabqj8vs", INGEST = "9nycxwodyby36g30ezp05idn0rqihnlh", LM = "j4ktylebkczp1tgvlj0h4tfbxb77q9b1", OLD = "jp6ukjt7tpk3y4yly9c691g01f47cq8q";
async function run(b, qs) { const c = await b.newContext({ ...devices["iPhone 13"] }); const hooks = {}, pix = [], errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, decodeURIComponent(u.pathname)); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "nf" }) }
  if (u.hostname.endsWith("make.com")) { const id = u.pathname.slice(1); (hooks[id] = hooks[id] || []).push(r.request().postData() || ""); return r.fulfill({ status: 200, contentType: "application/json", body: "{}" }) }
  if (u.href.includes("fbevents.js")) return r.fulfill({ status: 200, contentType: "text/javascript", body: "" });
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); const FBQ = [];
 await p.exposeFunction("__rec", (page, args) => { if (/landing_option2/.test(page)) FBQ.push(JSON.parse(args)) });
 await p.addInitScript(() => { Object.defineProperty(window, "fbq", { configurable: true, set(v) { this.__realfbq = v }, get() { const self = this; return function () { try { window.__rec(location.pathname, JSON.stringify([...arguments].slice(0, 2))) } catch (e) { } if (self.__realfbq) try { return self.__realfbq.apply(this, arguments) } catch (e) { } } } }) });
 await p.goto("https://local.test/landing-pages/landing_option2.html" + qs); await p.waitForTimeout(1500);
 await p.evaluate(() => window.openPopup());
 await p.fill("#fName", "יהב בדיקה"); await p.fill("#fPhone", "0500000000"); await p.fill("#fEmail", "t118@example.com");
 await p.evaluate(() => { document.getElementById("legalBox").checked = true });
 await p.evaluate(() => window.submitForm());
 await p.waitForURL(/two-page-funnel-1/, { timeout: 8000 }).catch(() => { }); await p.waitForTimeout(800);
 const fbq = FBQ;
 const url = p.url(); await c.close(); return { hooks, url, errs, fbq } }
const J = s => { try { return JSON.parse(s) } catch (e) { return {} } };
(async () => { const b = await chromium.launch();
 for (const [lab, qs, mk, sup, px] of [
  ["aff=gal (marketer by aff)", "?aff=gal&utm_source=ig&utm_medium=affiliate&utm_campaign=x", "galba", "48240", "2401943686950969"],
  ["marketer=rachel", "?marketer=rachel&utm_source=fb&utm_medium=paid", "rachel", "45165", "2599105640487498"],
  ["aff=karlin", "?aff=karlin", "karlen", "43121", "2401943686950969"],
  ["no marketer", "?utm_source=fb", "", "35213", "2401943686950969"]]) {
  const R = await run(b, qs);
  const al = (R.hooks[ALERT] || []).map(J)[0] || {}, ig = (R.hooks[INGEST] || []).map(J).find(x => x.stage === 1) || {}, lm = (R.hooks[LM] || []).map(J)[0] || {};
  const lmq = new URLSearchParams(lm.qs || "");
  ok(`${lab}: alert hook gets name/phone/email/page + marketer=${mk || "(empty)"}`, al.name === "יהב בדיקה" && al.phone === "0500000000" && al.email === "t118@example.com" && al.page === "landing_option2" && al.marketer === mk, al);
  ok(`${lab}: old missing hook jp6uk no longer called`, !R.hooks[OLD], Object.keys(R.hooks));
  ok(`${lab}: store 148094 (ingest stage 1) gets marketer=${mk || "(empty)"}`, ig.stage === 1 && ig.marketer === mk && ig.page === "landing_option2", ig);
  ok(`${lab}: LeadManager lm_supplier=${sup}`, lmq.get("lm_supplier") === sup, lmq.get("lm_supplier"));
  const inits = R.fbq.filter(x => x[0] === "init").map(x => x[1]), lead = R.fbq.some(x => x[0] === "track" && x[1] === "Lead");
  ok(`${lab}: pixel ${px} (by marketer= only, mapping unchanged) + Lead fired`, inits.includes(px) && lead, [inits, lead]);
  ok(`${lab}: goes to panel 6 (two-page-funnel-1?panel=6) with params`, /two-page-funnel-1\.html/.test(R.url) && /panel=6/.test(R.url) && (qs.length < 2 || R.url.includes(qs.slice(1).split("&")[0])), R.url);
  ok(`${lab}: no JS errors`, !R.errs.length, R.errs) }
 { const c = await b.newContext(); await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname === "/" ? "index.html" : u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
   const p = await c.newPage(); await c.route("**/nlp/a5*.html*", r => r.fulfill({ status: 200, contentType: "text/html", body: "<p>x</p>" }));
   await p.goto("https://local.test/?utm_source=fb&utm_campaign=lenatzeach_lab"); await p.waitForTimeout(2000);
   ok("home page -> /nlp/go.html -> routed page, utm kept", /\/nlp\/a5v[67]\.html/.test(p.url()) && p.url().includes("utm_campaign=lenatzeach_lab"), p.url()); await c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
