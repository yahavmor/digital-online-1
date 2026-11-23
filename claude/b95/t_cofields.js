// ב95 (בדיקה טכנית, בלי שינוי): השדות בדף התשלום במובייל - B ו-B2, עם test=1. האתר מעותק זהה של main (לפי גיבוב).
// שימוש: node t_cofields.js <nlp dir> <out dir>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]), H = "https://funnel.digitalonline.co.il/nlp/";
const T = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".json": "application/json" };
const FB_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/480.0.0.40.104;FBBV/650000000;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5;FBRV/0]";
const FB_AND = "Mozilla/5.0 (Linux; Android 14; Pixel 7 Build/UQ1A.240205.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/460.0.0.48.109;]";
const res = []; let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => {
  const b = await chromium.launch(); fs.mkdirSync(OUT, { recursive: true });
  const DEV = [["iPhone 13", devices["iPhone 13"], null], ["iPhone 13 · Facebook", devices["iPhone 13"], FB_IOS], ["Pixel 5", devices["Pixel 5"], null], ["Pixel 5 · Facebook", devices["Pixel 5"], FB_AND]];
  for (const [dn, d, ua] of DEV) for (const co of ["b", "b2"]) {
    const c = await b.newContext({ ...d, ...(ua ? { userAgent: ua } : {}) }); const ev = [], other = [];
    await c.route("**/*", r => { const u = new URL(r.request().url());
      if (u.href.startsWith(H)) { const fp = path.join(DIR, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "nf" }); return r.fulfill({ status: 200, contentType: T[path.extname(fp)] || "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (/make\.com/.test(u.hostname)) { const pd = r.request().postData() || ""; let o = {}; try { o = Object.fromEntries(new URLSearchParams(pd)) } catch (e) {} ev.push({ url: u.pathname, ...o }); return r.fulfill({ status: 200, contentType: "application/json", body: "{}" }) }
      other.push(u.hostname); return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
    const q = "test=1&co=" + co + "&v=a5v6&utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p24&exp=pg_1611&sid=t-" + Date.now();
    await p.goto(H + "checkout.html?" + q); await p.waitForTimeout(2500);
    const tag = dn + " · " + co.toUpperCase();
    ok(tag + ": checkout_view sent", ev.some(e => e.ev === "checkout_view"));
    const co2 = await p.evaluate(() => [window.NLP_CO, document.documentElement.getAttribute("data-co2")]); ok(tag + ": version " + co, co2[0] === co, co2.join(","));
    await p.screenshot({ path: path.join(OUT, (dn + "_" + co).replace(/[^\w]+/g, "_") + "_top.png") });
    // השדות: גלויים, לא מכוסים, אפשר ללחוץ ולהקליד
    for (const id of ["fName", "fEmail", "fPhone"]) {
      const info = await p.evaluate(id => { const e = document.getElementById(id); if (!e) return { missing: true }; e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
        const pts = [[r.left + r.width / 2, r.top + r.height / 2], [r.left + 8, r.top + r.height / 2], [r.right - 8, r.top + r.height / 2]];
        const hit = pts.map(([x, y]) => { const t = document.elementFromPoint(x, y); return t === e || (t && e.contains(t)) ? "ok" : (t ? (t.tagName + "#" + t.id + "." + String(t.className).slice(0, 40)) : "none") });
        return { w: Math.round(r.width), h: Math.round(r.height), vis: cs.visibility, disp: cs.display, op: cs.opacity, pe: cs.pointerEvents, dis: e.disabled, ro: e.readOnly, hit } }, id);
      ok(tag + ": #" + id + " visible and not covered", !info.missing && info.w > 50 && info.h > 20 && info.vis === "visible" && info.disp !== "none" && +info.op > 0.5 && info.pe !== "none" && !info.dis && !info.ro && info.hit.every(h => h === "ok"), JSON.stringify(info));
    }
    // לחיצה (tap) על השדה הראשון והקלדה
    await p.locator("#fName").scrollIntoViewIfNeeded(); await p.tap("#fName"); await p.waitForTimeout(300);
    const foc = await p.evaluate(() => document.activeElement && document.activeElement.id); ok(tag + ": tap focuses #fName", foc === "fName", foc);
    await p.keyboard.type("בדיקה טכנית", { delay: 30 }); await p.waitForTimeout(1200);
    const cs = ev.filter(e => e.ev === "checkout_contact_started");
    ok(tag + ": typing sends checkout_contact_started once", cs.length === 1, ev.map(e => e.ev).join(","));
    if (cs[0]) ok(tag + ": event marked test (int=1) with co=" + co, /(^|;)int=1(;|$)/.test(cs[0].x || "") && new RegExp("co=" + co + ";cx=" + (process.env.CX || "co_b2_1311")).test(cs[0].x || ""), cs[0].x);
    // גלילה לאורך הדף: אלמנטים קבועים (fixed/sticky) שעולים על השדות
    const fixed = await p.evaluate(() => [...document.querySelectorAll("body *")].filter(e => { const s = getComputedStyle(e); return (s.position === "fixed" || s.position === "sticky") && s.display !== "none" && s.visibility !== "hidden" && e.getBoundingClientRect().height > 0 }).map(e => { const r = e.getBoundingClientRect(); return e.tagName + "#" + e.id + "." + String(e.className).slice(0, 30) + " " + Math.round(r.top) + "-" + Math.round(r.bottom) + " z" + getComputedStyle(e).zIndex }));
    res.push({ tag, fixed, errs, cs: cs[0] || null, other: [...new Set(other)] });
    ok(tag + ": no JS errors", !errs.length, errs.join("|"));
    await p.evaluate(() => document.getElementById("fName").scrollIntoView({ block: "center" })); await p.screenshot({ path: path.join(OUT, (dn + "_" + co).replace(/[^\w]+/g, "_") + "_fields.png") });
    await c.close();
  }
  fs.writeFileSync(path.join(OUT, "res.json"), JSON.stringify(res, null, 1));
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0)
})();
