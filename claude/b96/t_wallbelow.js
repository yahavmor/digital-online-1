// ב96: Apple Pay / Google Pay מתחת לטופס - בדפדפן רגיל לוגואים ולחיצה גוללת לשדה השם; בדפדפן פנימי הרמז. שימוש: node t_wallbelow.js <nlp dir> <out dir>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]), H = "https://funnel.digitalonline.co.il/nlp/";
const FB_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/480.0.0.40.104;]";
let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => { const b = await chromium.launch(); fs.mkdirSync(OUT, { recursive: true });
  for (const [dn, ua, dev] of [["iPhone 13", null, "iPhone 13"], ["iPhone 13 · Facebook", FB_IOS, "iPhone 13"], ["Pixel 5", null, "Pixel 5"]]) for (const co of ["b", "b2"]) {
    const c = await b.newContext({ ...devices[dev], ...(ua ? { userAgent: ua } : {}) }); const ev = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith(H)) { const fp = path.join(DIR, u.pathname.replace(/^\/nlp\//, "")); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "" }); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (/make\.com/.test(u.hostname)) { try { ev.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))) } catch (e) {} return r.fulfill({ status: 200, body: "{}" }) } return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); await p.goto(H + "checkout.html?test=1&co=" + co); await p.waitForTimeout(1200);
    const t = dn + " · " + co.toUpperCase();
    const w = await p.evaluate(() => { const W = document.getElementById("wallTop"), F = document.getElementById("det"); return { below: !!(W && F && (F.compareDocumentPosition(W) & Node.DOCUMENT_POSITION_FOLLOWING) && W.closest(".why")), inTop: !!document.querySelector(".top #wallTop"), row: !document.getElementById("wtRow").hidden, hint: !document.getElementById("wtH").hidden && document.getElementById("wtH").textContent } });
    ok(t + ": the Apple Pay / Google Pay line is under the form, not at the top", w.below && !w.inTop, JSON.stringify(w));
    if (ua) ok(t + ": in-app - the hint (and no logos)", !w.row && /שלוש הנקודות/.test(w.hint || ""), JSON.stringify(w));
    else { ok(t + ": regular browser - logos shown", w.row, JSON.stringify(w));
      await p.locator('#wallTop .wt-b[data-w="apple"]').scrollIntoViewIfNeeded(); await p.tap('#wallTop .wt-b[data-w="apple"]'); await p.waitForTimeout(900);
      const r = await p.evaluate(() => { const e = document.getElementById("fName"), b = e.getBoundingClientRect(); return { foc: document.activeElement === e, inView: b.top >= 0 && b.bottom <= innerHeight } });
      ok(t + ": tap on the logo scrolls to the name field and focuses it", r.foc && r.inView, JSON.stringify(r));
      ok(t + ": checkout_wallet_tap sent", ev.some(e => e.ev === "checkout_wallet_tap")) }
    await p.evaluate(() => document.getElementById("wallTop").scrollIntoView({ block: "center" })); await p.screenshot({ path: path.join(OUT, (t).replace(/[^\w]+/g, "_") + "_below.png") });
    ok(t + ": no JS errors", !errs.length, errs.join("|")); await c.close() }
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
