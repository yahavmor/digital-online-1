// צילום אזור המחיר לפני/אחרי. שימוש: node shot_price.js <root> <out dir> <tag>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, OUT, TAG] = process.argv.slice(2);
(async () => { const b = await chromium.launch();
 for (const pg of ["a5s", "a"]) { const c = await b.newContext({ ...devices["iPhone 13"] });
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : undefined }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto("https://local.test/nlp/" + pg + ".html?stay=1"); await p.waitForTimeout(800);
  await p.addStyleTag({ content: "html,body{scroll-behavior:auto!important} #sticky,#prog,.sticky{display:none!important} *{animation-duration:0s!important;transition:none!important}" });
  await p.evaluate(async () => { const t = document.querySelector(".v4-ko,.stack6"); const y = t.getBoundingClientRect().top + scrollY; for (let k = 0; k <= y; k += 300) { scrollTo(0, k); await new Promise(r => setTimeout(r, 50)) } });
  await p.waitForTimeout(2500);
  const box = await p.evaluate(() => { const a = document.querySelector(".v4-ko,.stack6").getBoundingClientRect(), z = document.querySelector(".v4-ko-now,.pay .now").getBoundingClientRect(); return { y: a.top + scrollY, h: z.bottom - a.top + 16 } });
  await p.evaluate(y => scrollTo(0, y - 10), box.y); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(OUT, "price_" + pg + "_" + TAG + ".png"), clip: { x: 0, y: 0, width: 390, height: Math.min(box.h + 20, 844) } }); await c.close() }
 await b.close() })();
