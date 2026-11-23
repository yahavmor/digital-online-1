// ב109: צילומי מסך בנייד. שימוש: node shots109.js <root> <shots dir> [suffix]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, SH, SUF = ""] = process.argv.slice(2);
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".mp4": "video/mp4", ".jpg": "image/jpeg", ".png": "image/png" };
(async () => { const b = await chromium.launch(); const c = await b.newContext({ ...devices["iPhone 13"] }); const errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/a5s.html?utm_source=claude_test"); await p.waitForTimeout(1500);
 // מלמעלה עד ההצעה: גלילה הדרגתית כדי שתמונות עצלות ייטענו, ואז צילום של האזור
 const offTop = await p.evaluate(() => Math.round(document.getElementById("offer").getBoundingClientRect().top + scrollY));
 for (let y = 0; y < offTop + 900; y += 400) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(120) } await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400);
 await p.screenshot({ path: path.join(SH, "b109_mobile_top_to_offer" + SUF + ".png"), fullPage: true, clip: { x: 0, y: 0, width: 390, height: offTop + 260 } });
 const pr = await p.$('details.fold.hot[data-fold="תוצאות אמיתיות"]'), pr2 = await p.$('details.fold.hot[data-fold="מה אומרים"]');
 const box = await p.evaluate(() => { const g = document.querySelector("section.guar"), r = document.querySelector('details[data-fold="רגע לפני"]'); return { a: Math.round(g.getBoundingClientRect().top + scrollY), z: Math.round(r.getBoundingClientRect().bottom + scrollY) } });
 for (let y = box.a - 400; y < box.z + 400; y += 400) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(120) }
 await p.screenshot({ path: path.join(SH, "b109_mobile_proofs_closed" + SUF + ".png"), fullPage: true, clip: { x: 0, y: box.a, width: 390, height: box.z - box.a + 20 } });
 await pr.evaluate(d => d.open = true); await pr2.evaluate(d => d.open = true); await p.waitForTimeout(600);
 const box2 = await p.evaluate(() => { const a = document.querySelector('details[data-fold="תוצאות אמיתיות"]').closest("section"), z = document.querySelector('details[data-fold="מה אומרים"]').closest("section"); return { a: Math.round(a.getBoundingClientRect().top + scrollY), z: Math.round(z.getBoundingClientRect().bottom + scrollY) } });
 for (let y = box2.a - 200; y < box2.z + 200; y += 400) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(150) }
 await p.screenshot({ path: path.join(SH, "b109_mobile_proofs_open" + SUF + ".png"), fullPage: true, clip: { x: 0, y: box2.a, width: 390, height: box2.z - box2.a } });
 console.log("offer at", offTop, "proofs", box, "errs", errs); await b.close() })();
