// ב117: כניסה ל-a5s.html?aff=yehudit - השיוך נשמר, האירועים (view, form_submit, checkout_details) נושאים aff=yehudit, ובקשת דף התשלום (7827398, נלכדת ולא נשלחת) נושאת aff=yehudit. שימוש: node t_a5s_yehudit.js <root>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + String(d).slice(0, 400))) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };
const CHK = "9yp88pz9bfvxbr7w6xkb4ckun82ote6a";
(async () => { const b = await chromium.launch(); const c = await b.newContext({ ...devices["iPhone 13"] }); const EV = [], PAY = [], errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] || "application/octet-stream" }) : r.fulfill({ status: 404, body: "" }) }
  if (u.hostname.endsWith("make.com")) { const d = r.request().postData() || ""; if (u.pathname.includes(CHK)) { PAY.push(Object.fromEntries(new URLSearchParams(d))); return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ url: "https://local.test/nlp/thanks.html?claude=b117" }) }) }
   if (/(^|&)ev=/.test(d)) EV.push(Object.fromEntries(new URLSearchParams(d))); return r.fulfill({ status: 200, body: "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message));
 await p.goto("https://local.test/nlp/a5s.html?aff=yehudit&utm_source=facebook&utm_medium=affiliate&utm_campaign=NLP_Aff_yehudit_Sales_Cold&utm_content=ad1"); await p.waitForTimeout(1500);
 ok("a5s: NLP_OWNER() = yehudit", await p.evaluate(() => NLP_OWNER()) === "yehudit");
 const ck = (await c.cookies()).find(x => x.name === "nlp_aff"); ok("cookie nlp_aff = yehudit, 30 days", ck && /^yehudit\./.test(decodeURIComponent(ck.value)) && ck.expires - Date.now() / 1e3 > 29 * 864e2, ck && ck.value);
 const v = EV.find(e => e.ev === "view"); ok("view event carries aff=yehudit (in x) and the utm", !!v && /aff=yehudit/.test(v.x || "") && /aff=yehudit/.test(v.qs || ""), JSON.stringify(v));
 const F = p.locator('form.lpf[data-form="1"]'); await F.scrollIntoViewIfNeeded(); await F.locator('[name="name"]').fill("בדיקה ב117"); await F.locator('[name="email"]').fill("b117@example.com"); await F.locator('[name="box"]').check();
 await F.locator("button").click(); await p.waitForTimeout(2500);
 const fs_ = EV.find(e => e.ev === "form_submit"), cd = EV.find(e => e.ev === "checkout_details");
 ok("form_submit event carries aff=yehudit", !!fs_ && /aff=yehudit/.test(fs_.x || ""), JSON.stringify(fs_));
 ok("checkout_details event carries aff=yehudit", !!cd && /aff=yehudit/.test(cd.x || ""), JSON.stringify(cd));
 ok("payment-page request (7827398, intercepted) carries aff=yehudit", PAY.length === 1 && PAY[0].aff === "yehudit", JSON.stringify(PAY).replace(/b117@example\.com/g, "…"));
 ok("after the mocked payment-page reply the browser leaves a5s (redirect)", /thanks\.html|checkout/.test(p.url()), p.url());
 ok("no JS errors", !errs.length, errs.join(" | "));
 const p2 = await c.newPage(); await p2.goto("https://local.test/nlp/a5s.html?utm_source=facebook&utm_medium=affiliate"); await p2.waitForTimeout(800);
 ok("return visit without aff stays yehudit", await p2.evaluate(() => NLP_OWNER()) === "yehudit");
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
