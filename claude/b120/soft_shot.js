// ב120: צילום "עוד לא בטוח?" (תצוגה מקדימה, SOFT_ON כבוי באוויר) + בדיקה שהבקשה יוצאת עם aff ומקור
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, OUT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 400))) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp" };
const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/460.0.0.36.108;FBSN/iOS]";
const SOFT = "39kj2y452zq059jpdcneylg155umd3to";
async function page(b, preview, qs) { const c = await b.newContext({ viewport: { width: 390, height: 664 }, userAgent: UA, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
 const soft = [], trk = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, decodeURIComponent(u.pathname)); return fs.existsSync(fp) ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] || "application/octet-stream" }) : r.fulfill({ status: 404, body: "" }) }
  if (u.href.includes(SOFT)) { soft.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))); return r.fulfill({ status: 200, body: "Accepted" }) }
  if (u.hostname.endsWith("make.com")) { trk.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))); return r.fulfill({ status: 200, contentType: "application/json", body: "{}" }) }
  return r.fulfill({ status: 204, body: "" }) });
 if (preview) await c.addInitScript(() => { window.NLP_SOFT_PREVIEW = true });
 const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
 await p.goto("https://local.test/nlp/checkout.html?" + qs); await p.waitForTimeout(900); return { c, p, soft, trk, errs } }
(async () => { const b = await chromium.launch();
 { const { c, p, errs } = await page(b, false, "co=b2&aff=gal&utm_source=ig&utm_medium=affiliate");
   ok("off by default (SOFT_ON=false): link hidden", await p.evaluate(() => document.getElementById("softWrap").hidden), ""); ok("no JS errors", !errs.length, errs); await c.close() }
 { const { c, p, soft, trk, errs } = await page(b, true, "co=b2&exp=rt_2111&aff=gal&utm_source=ig&utm_medium=affiliate&utm_campaign=NLP%20%7C%20Aff%20gal&utm_content=p25_brain_c3&v=a5v6");
   await p.fill("#fName", "בדיקה"); await p.fill("#fEmail", "soft.test@example.com");
   const link = p.locator("#softBtn"); await link.scrollIntoViewIfNeeded(); ok("link text 'עוד לא בטוח?' under the form", (await link.textContent()) === "עוד לא בטוח?" && await p.evaluate(() => { const f = document.getElementById("det").getBoundingClientRect(), s = document.getElementById("softWrap").getBoundingClientRect(); return s.top > f.bottom }), "");
   await link.click(); await p.waitForTimeout(200);
   ok("box opens, email prefilled from the form, consent unchecked", await p.inputValue("#softEmail") === "soft.test@example.com" && !(await p.isChecked("#softConsent")), await p.inputValue("#softEmail"));
   await p.evaluate(() => document.getElementById("softWrap").scrollIntoView({ block: "center" })); await p.waitForTimeout(150);
   if (OUT) await p.screenshot({ path: OUT + "_open.png" });
   await p.fill("#softEmail", "bad"); await p.click("#softGo"); ok("bad email -> error, nothing sent", soft.length === 0 && /תקין/.test(await p.textContent("#softErr")), soft);
   await p.fill("#softEmail", "soft.test@example.com"); await p.check("#softConsent"); await p.click("#softGo"); await p.waitForTimeout(400);
   const s = soft[0] || {};
   ok("sent to the soft hook with aff=gal + source + page + sid + consent=1", s.email === "soft.test@example.com" && s.aff === "gal" && s.utm_source === "ig" && s.utm_medium === "affiliate" && s.utm_content === "p25_brain_c3" && s.exp === "rt_2111" && s.page === "/nlp/checkout.html" && !!s.sid && s.consent === "1" && s.name === "בדיקה", s);
   ok("tracking: soft_open + soft_submit (with aff), no email in tracking", trk.some(t => t.ev === "soft_open") && trk.some(t => t.ev === "soft_submit" && /aff=gal/.test(t.x || "")) && !trk.some(t => JSON.stringify(t).includes("soft.test@")), trk.map(t => t.ev));
   ok("after send: placeholder thanks shown, box closed", !(await p.evaluate(() => document.getElementById("softOk").hidden)) && await p.evaluate(() => document.getElementById("softBox").hidden), "");
   if (OUT) { await p.evaluate(() => document.getElementById("softWrap").scrollIntoView({ block: "center" })); await p.screenshot({ path: OUT + "_sent.png" }) }
   ok("no JS errors", !errs.length, errs); await c.close() }
 { const { c, p, soft } = await page(b, true, "co=b2&utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab&utm_id=1");
   await p.click("#softBtn"); await p.fill("#softEmail", "ben.own@example.com"); await p.click("#softGo"); await p.waitForTimeout(300);
   ok("Ben's own traffic -> aff empty (sale stays Ben's)", soft[0] && soft[0].aff === "" && soft[0].utm_campaign === "lenatzeach_lab", soft[0]); await c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
