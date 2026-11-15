// ב99: איפה שדות הטופס בדף התשלום במובייל. שימוש: node m99.js <nlp dir> <out dir> [shots]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]), SHOT = process.argv[4] === "shots", H = "https://funnel.digitalonline.co.il/nlp/";
fs.mkdirSync(OUT, { recursive: true });
const SAF = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";
const IG = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 345.0.0.32.110 (iPhone15,2; iOS 17_5; he_IL; he; scale=3.00; 1179x2556; 634108168)";
const FB_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/480.0.0.40.104;FBBV/650000000;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5;FBRV/0]";
const FB_AND = "Mozilla/5.0 (Linux; Android 14; Pixel 7 Build/UQ1A.240205.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/460.0.0.48.109;]";
const mob = (w, h) => ({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const V = [
  ["375x667", mob(375, 667), SAF, ""],
  ["393x852", mob(393, 852), SAF, ""],
  ["393x659·Safari", mob(393, 659), SAF, ""],
  ["393x659·IG·int", mob(393, 659), IG, "&internal=1"],
  ["iPhone13·FB", devices["iPhone 13"], FB_IOS, ""],
  ["Pixel5·FB", devices["Pixel 5"], FB_AND, ""],
];
(async () => { const b = await chromium.launch(); const res = [];
  for (const [vn, d, ua, q] of V) for (const co of ["b", "b2"]) {
    const c = await b.newContext({ ...d, userAgent: ua }); const ev = [];
    await c.route("**/*", r => { const u = new URL(r.request().url());
      if (u.href.startsWith(H)) { const fp = path.join(DIR, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "" }); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : fp.endsWith(".webp") ? "image/webp" : "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (u.host.includes("make.com")) { try { const pd = r.request().postData() || ""; ev.push(pd + " " + u.search) } catch (e) {} return r.fulfill({ status: 200, body: "Accepted" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); await p.goto(H + "checkout.html?co=" + co + "&v=a5v6&utm_source=ig" + (q || "&test=1")); await p.waitForTimeout(1200);
    const r = await p.evaluate(() => { const R = id => document.getElementById(id).getBoundingClientRect(); return { vh: innerHeight, sw: document.documentElement.scrollWidth, vw: innerWidth, name: Math.round(R("fName").top + scrollY), nameB: Math.round(R("fName").bottom + scrollY), email: Math.round(R("fEmail").bottom + scrollY), phone: Math.round(R("fPhone").bottom + scrollY), co: window.NLP_CO } });
    r.all3 = r.phone <= r.vh; r.v = vn; r.ver = co; res.push(r);
    console.log(vn.padEnd(15), co.padEnd(2), "screen", r.vh, "| name top", r.name, "| phone input bottom", r.phone, r.all3 ? "→ all 3 fields in the first screen" : "→ phone below the first screen", r.sw > r.vw ? "| HORIZONTAL OVERFLOW" : "");
    if (q) { await p.fill("#fName", "בדיקה פנימית"); await p.waitForTimeout(600); const cs = ev.filter(e => /checkout_contact_started/.test(e)); console.log("   IG internal=1: checkout_contact_started sent:", cs.length, "| int=1:", cs.some(e => /int(%3D|=)1/.test(e)), "| cx:", (cs.join(" ").match(/cx(%3D|=)([\w]+)/) || [])[2]) }
    if (SHOT) await p.screenshot({ path: path.join(OUT, vn.replace(/[^\w]/g, "_") + "_" + co + ".png") });
    await c.close() }
  fs.writeFileSync(path.join(OUT, "res.json"), JSON.stringify(res, null, 1)); await b.close() })();
