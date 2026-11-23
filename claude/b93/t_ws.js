// ב93: לשונית "מה מוכר" בדשבורד מול whatsells.py על אותם נתונים. שימוש: node t_ws.js <dash לפני> <dash אחרי> <events json> <spend.tsv> <ads.tsv> <out.json>
process.env.TZ = "Asia/Jerusalem";
const { chromium } = require("playwright"), fs = require("fs");
const [O, P, EVF, SPF, ADF, OUT] = process.argv.slice(2);
const EV = JSON.parse(fs.readFileSync(EVF, "utf8")).content.replace(/\r/g, ""), SP = fs.readFileSync(SPF, "utf8"), ADS = fs.readFileSync(ADF, "utf8");
const AFF = "affiliates\tname\tpct\tactive\tfee\tbudget\namir\tאמיר\t74\ttrue\t0\t\nrachel\tרחל\t0\ttrue\t220\t\ngal\tגל\t0\ttrue\t220\t\nyahel\tיהל\t0\ttrue\t220\t\nshahar\tשחר\t0\ttrue\t220\t\nyosef\tיוסף\t0\ttrue\t220\t\n";
(async () => {
  const b = await chromium.launch(); const res = {};
  const run = async (file, scr) => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-15T11:51:00+02:00")); const errs = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(file) });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: SP, affiliates: AFF, refunds: "refunds\n", paid: "paid\tat\taff\n", ads: ADS }[a] || "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#" + scr); await p.waitForTimeout(4000); return { p, errs } };
  const A = await run(P, "ws"); await A.p.evaluate(() => { try { snapAds() } catch (e) {} }); await A.p.waitForTimeout(1500);
  const grab = () => A.p.evaluate(() => Object.fromEntries(["wsAd", "wsCamp", "wsAff"].map(id => [id, [...document.getElementById(id).rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim()))]).concat([["note", document.getElementById("wsNote").innerText]])));
  for (const per of ["7", "2010"]) { await A.p.evaluate(p => { wsPer = p; render() }, per); await A.p.waitForTimeout(800); res[per] = await grab() }
  res.errs = A.errs;
  // שאר הלשוניות לא השתנו
  const B = await run(O, "snap"), C = await run(P, "snap"); const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(400); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
  res.same = {}; for (const s of ["snap", "ov", "co", "af", "fin", "up"]) res.same[s] = (await scr(B, s)) === (await scr(C, s));
  res.cl = await C.p.evaluate(() => CHANGELOG[0][1].slice(0, 30));
  fs.writeFileSync(OUT, JSON.stringify(res)); await b.close();
})();
