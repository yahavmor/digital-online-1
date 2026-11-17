const { chromium } = require("playwright"), fs = require("fs"), path = require("path"); const ROOT = process.argv[2] || "wtmain72"; // ב105 אחרי פריסה: הקבצים מ-main (זהים לאתר החי לפי hash), כי הסביבה חסומה לאתר עצמו
(async () => { const b = await chromium.launch();
 for (const rnd of [0, 1]) { const c = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await c.addInitScript(r => { crypto.getRandomValues = a => { a[0] = r; return a } }, rnd);
  const ev = [];
  await c.route("**/*", r => { const u = new URL(r.request().url());
   if (u.hostname === "funnel.digitalonline.co.il") { const fp = path.join(ROOT, u.pathname); if (fs.existsSync(fp) && fs.statSync(fp).isFile()) return r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: /\.html$/.test(fp) ? "text/html; charset=utf-8" : /\.svg$/.test(fp) ? "image/svg+xml" : undefined }); return r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) ev.push((r.request().postData() || u.search).slice(0, 200)); return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto("https://funnel.digitalonline.co.il/nlp/go.html?utm_source=fb&utm_medium=paid&utm_id=1&utm_content=claude_test105"); await p.waitForTimeout(2500);
  const page = p.url(), st = await p.evaluate(() => ({ k: localStorage.getItem("nlp_go_on_1711"), ab: localStorage.getItem("nlp_co_ab") }));
  const cta = p.locator('a[href*="checkout"]:visible').first(); await cta.scrollIntoViewIfNeeded();
  await Promise.all([p.waitForURL(/checkout/, { timeout: 20000 }), cta.click()]); await p.waitForTimeout(3000);
  const co = await p.evaluate(() => ({ url: location.href.replace(/^.*\/nlp\//, ""), ver: window.NLP_CO, h: document.body.innerText.slice(0,120).replace(/\s+/g," ") }));
  await p.screenshot({ path: "live105_" + rnd + ".png" });
  console.log(JSON.stringify({ rnd, page: page.replace(/^.*\/nlp\//, ""), st, co, errs, nev: ev.length })); await c.close() }
 await b.close() })();
