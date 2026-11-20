// ב113 (2): px_status מיד אחרי Purchase. שימוש: node t_px.js <root חדש> <root ישן (main)>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d))) };
const FB = 'window.__fb=window.__fb||[];(function(){var f=window.fbq;if(!f)return;f.callMethod=function(){window.__fb.push([].slice.call(arguments).map(function(x){return typeof x==="object"?JSON.stringify(x):String(x)}))};(f.queue||[]).forEach(function(a){f.callMethod.apply(f,a)});f.queue=[];})();';
async function run(b, root, verified) { const c = await b.newContext({ ...devices["iPhone 13"] }); const ev = []; const t0 = Date.now();
 await c.route("**/*", async r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : undefined }) : r.fulfill({ status: 404, body: "" }) }
  if (u.hostname === "connect.facebook.net") return r.fulfill({ status: 200, contentType: "application/javascript", body: FB });
  if (u.hostname.endsWith("make.com")) { const p = u.pathname, d = Object.fromEntries(new URLSearchParams(r.request().postData() || ""));
   if (p.includes("s9ay2kp6")) return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(verified ? { ok: true, link: "https://x.schooler.biz/c", deal: "123456", email: "t@example.com" } : { ok: false }) });
   if (p.includes("qhq5knj8")) return r.fulfill({ status: 200, contentType: "application/json", body: '{"up":""}' });
   if (d.ev) ev.push(Object.assign({ ms: Date.now() - t0 }, d)); return r.fulfill({ status: 200, body: "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
 await p.goto("https://local.test/nlp/thanks.html?v=a5s&sid=S-113&lowprofilecode=LP-113"); await p.waitForTimeout(4000);
 const early = ev.filter(e => e.ev === "px_status"); const fb = await p.evaluate(() => window.__fb || []);
 await p.waitForTimeout(10500); const all = ev.filter(e => e.ev === "px_status"); await c.close(); return { early, all, fb, errs } }
(async () => { const b = await chromium.launch();
 const A = await run(b, NEW, true);
 const pur = A.fb.filter(x => x[0] === "track" && x[1] === "Purchase");
 ok("new: Purchase fired once with eventID = deal", pur.length === 1 && /"eventID":"123456"/.test(pur[0][3] || ""), pur);
 ok("new: px_status sent right after the Purchase (within 4s, at=pur, pur=1)", A.early.length === 1 && /pur=1/.test(A.early[0].x) && /at=pur/.test(A.early[0].x) && A.early[0].ms < 4000, A.early);
 ok("new: only one px_status in the visit (no second one at 12s)", A.all.length === 1, A.all.map(e => e.x));
 ok("new: no JS errors", !A.errs.length, A.errs);
 const B = await run(b, NEW, false);
 ok("new, no verified purchase: px_status only at 12s with pur=0 (at=12s)", B.early.length === 0 && B.all.length === 1 && /pur=0/.test(B.all[0].x) && /at=12s/.test(B.all[0].x), B.all.map(e => e.x));
 const O = await run(b, OLD, true);
 ok("old (live) for comparison: no px_status in the first 4 seconds", O.early.length === 0 && O.all.length === 1, O.all.map(e => e.x));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
