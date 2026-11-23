// ב120: מסך ראשון של checkout.html בדפדפן הפנימי של פייסבוק. שימוש: node measure.js <root> <out-prefix> [file=nlp/checkout.html]
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, OUT, FILE] = process.argv.slice(2); const F = FILE || "nlp/checkout.html";
const CT = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".css": "text/css", ".json": "application/json" };
const UA_AND = "Mozilla/5.0 (Linux; Android 13; SM-A536B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/460.0.0.48.109;]";
const UA_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/460.0.0.36.108;FBBV/600000000;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.4;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5]";
// גודל החלון שהדף מקבל בתוך הדפדפן של פייסבוק (המסך פחות שורת המצב, סרגל הדפדפן של פייסבוק והסרגל התחתון)
const DEV = [
 ["android_360x640", 360, 640, UA_AND, 3], ["android_412x760", 412, 760, UA_AND, 2.625],
 ["iphone_375x560", 375, 560, UA_IOS, 2], ["iphone_390x664", 390, 664, UA_IOS, 3], ["iphone_430x760", 430, 760, UA_IOS, 3]];
(async () => { const b = await chromium.launch(); const res = [];
 for (const [name, w, h, ua, dpr] of DEV) {
  const c = await b.newContext({ viewport: { width: w, height: h }, userAgent: ua, deviceScaleFactor: dpr, isMobile: true, hasTouch: true, locale: "he-IL" });
  await c.route("**/*", r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(ROOT, decodeURIComponent(u.pathname)); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] || "application/octet-stream" }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) return r.fulfill({ status: 200, contentType: "application/json", body: "{}" });
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto("https://local.test/" + F + "?co=b2&exp=rt_2111&go=1&utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab&utm_content=car4_warm_a&aff=gal"); await p.waitForTimeout(1200);
  const m = await p.evaluate(() => { const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { top: Math.round(b.top), bottom: Math.round(b.bottom), vis: getComputedStyle(e).display !== "none" && b.height > 0 } };
   return { H: innerHeight, W: innerWidth, sw: document.documentElement.scrollWidth, name: r("#fName"), email: r("#fEmail"), phone: r("#fPhone"), terms: r("#fTerms"), btn: r("#det button.go"), hint: r("#coHint"), soft: r("#softWrap"), consent: r("#fConsent"), co: window.NLP_CO } });
  m.dev = name; m.firstField = !!(m.name && m.name.bottom <= m.H); m.button = !!(m.btn && m.btn.vis && m.btn.bottom <= m.H); m.termsVis = !!(m.terms && m.terms.bottom <= m.H); m.hintVis = !!(m.hint && m.hint.vis && m.hint.bottom <= m.H); m.errs = errs; res.push(m);
  await p.screenshot({ path: `${OUT}_${name}.png` }); await c.close() }
 console.log(JSON.stringify(res, null, 1)); await b.close() })();
