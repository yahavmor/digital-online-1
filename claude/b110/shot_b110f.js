// ב114: צילום כרטיס ההצעה עם בלוק ההמלצות (סימונים). שימוש: node shot_b114.js <root> <out dir>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, OUT] = process.argv.slice(2);
(async () => { const b = await chromium.launch();
 for (const [nm, dev] of [["mobile", { ...devices["iPhone 13"] }], ["desktop", { viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 }]]) {
  const c = await b.newContext(dev);
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : undefined }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto("https://local.test/nlp/" + (process.argv[4] || "a5s_b110v2.html")); await p.waitForTimeout(1500);
  await p.addStyleTag({ content: "html,body{scroll-behavior:auto!important} #sticky,#prog{display:none!important}" });
  await p.evaluate(() => document.querySelector("#offer .v4-ko-price").scrollIntoView({ block: "start" })); await p.waitForTimeout(1500);
  const box = await p.evaluate(() => { const a = document.querySelector("#offer .v4-ko-price").getBoundingClientRect(), z = document.querySelector("#lpForm1 button").getBoundingClientRect(); return { x: Math.max(0, Math.min(a.left, z.left) - 12), y: Math.max(0, a.top - 12), w: Math.max(a.width, z.width) + 24, h: z.bottom - a.top + 24 } });
  await p.screenshot({ path: path.join(OUT, (process.argv[5] || "b114_testimonials_") + nm + ".png"), clip: { x: box.x, y: box.y, width: Math.min(box.w, 1280), height: box.h } });
  await c.close() }
 await b.close() })();
