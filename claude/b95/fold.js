// ב95: איפה השדה הראשון (שם מלא) ביחס למסך הראשון, בכל גרסה של דף התשלום. שימוש: node fold.js <base dir> <commits...>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const BASE = path.resolve(process.argv[2]), CS = process.argv.slice(3), H = "https://funnel.digitalonline.co.il/nlp/";
const FB_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/480.0.0.40.104;FBBV/650000000;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5;FBRV/0]";
const FB_AND = "Mozilla/5.0 (Linux; Android 14; Pixel 7 Build/UQ1A.240205.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/460.0.0.48.109;]";
(async () => { const b = await chromium.launch();
  for (const [dn, d, ua] of [["iPhone13·FB", devices["iPhone 13"], FB_IOS], ["Pixel5·FB", devices["Pixel 5"], FB_AND], ["iPhoneSE·FB", devices["iPhone SE"], FB_IOS]]) for (const cm of CS) for (const co of ["b", "b2"]) {
    const dir = path.join(BASE, cm), c = await b.newContext({ ...d, userAgent: ua });
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith(H)) { const fp = path.join(dir, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "" }); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".css") ? "text/css" : fp.endsWith(".js") ? "text/javascript" : "application/octet-stream", body: fs.readFileSync(fp) }) } return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); await p.goto(H + "checkout.html?test=1&co=" + co + "&v=a5v6"); await p.waitForTimeout(1500);
    const r = await p.evaluate(() => { const e = document.getElementById("fName"), h = innerHeight; const t = e.getBoundingClientRect().top + scrollY; const lbl = [...document.querySelectorAll("h2,h3,legend,.ttl")].find(x => /הפרטים שלך/.test(x.textContent)); return { vh: h, top: Math.round(t), pct: Math.round(t / h * 100), hdr: lbl ? Math.round(lbl.getBoundingClientRect().top + scrollY) : null, co: window.NLP_CO } });
    console.log(dn.padEnd(12), cm, co.padEnd(2), "screen", r.vh, "| first field at", r.top, "px =", r.pct + "% of the first screen", r.co !== co ? "(version " + r.co + ")" : "");
    await c.close() }
  await b.close() })();
