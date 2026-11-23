// ב116: הרצות מדומות - תנועה קרה של בן -> a5s (B2), כל השאר נשאר ב-rt_2111. שימוש: node t_cold.js <root עם nlp/>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT] = process.argv.slice(2); let n = 0, f = 0;
const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 400))) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };
const CHK = "9yp88pz9bfvxbr7w6xkb4ckun82ote6a";
async function mk(b, dev) { const c = await b.newContext(dev || {}); const hooks = [], pay = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
  if (u.href.includes(CHK)) { pay.push(r.request().postData() || ""); return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ url: "https://secure.cardcom.solutions/External/LowProfile.aspx?LowProfileCode=test", code: 0 }) }) }
  if (u.hostname.endsWith("make.com")) { hooks.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))); return r.fulfill({ status: 200, contentType: "application/json", body: "{}" }) }
  if (u.hostname.endsWith("cardcom.solutions")) return r.fulfill({ status: 200, contentType: "text/html", body: "<p>cardcom</p>" });
  return r.fulfill({ status: 204, body: "" }) });
 return { c, hooks, pay } }
const land = async p => { await p.waitForURL(u => !/\/go\.html/.test(u.toString()), { timeout: 8000 }).catch(() => { }); await p.waitForTimeout(300); return new URL(p.url()) };
const pg = u => u.pathname.split("/").pop().replace(".html", "");
const E = encodeURIComponent;
const CASES = [
 ["Ben cold: lenatzeach_cold", "utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p25&utm_id=1", "a5s"],
 ["Ben cold: old campaign 'NLP | Cold | Sales | IC | 10.11'", "utm_source=fb&utm_medium=paid&utm_campaign=" + E("NLP | Cold | Sales | IC | 10.11") + "&utm_content=p24", "a5s"],
 ["Ben cold, upper case", "utm_source=fb&utm_medium=paid&utm_campaign=LENATZEACH_COLD", "a5s"],
 ["affiliate gal 'NLP | Aff gal | Sales | Cold | P25' + aff", "aff=gal&utm_source=ig&utm_medium=affiliate&utm_campaign=" + E("NLP | Aff gal | Sales | Cold | P25") + "&utm_content=p25_brain_c3", "rt"],
 ["affiliate rachel COLD_18 + aff", "aff=rachel&utm_source=fb&utm_medium=affiliate&utm_campaign=" + E("NLP | Aff rachel | Sales | Cold | COLD_18"), "rt"],
 ["lenatzeach_cold but with aff=rami", "aff=rami&utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_cold", "rt"],
 ["lenatzeach_cold with utm_medium=affiliate (no aff)", "utm_source=fb&utm_medium=affiliate&utm_campaign=lenatzeach_cold", "rt"],
 ["warm carousel lenatzeach_lab / car4_warm_a", "utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_lab&utm_content=car4_warm_a", "rt"],
 ["email link", "utm_source=email&utm_medium=email&utm_campaign=nlp_rec1", "rt"],
 ["no utm (direct)", "", "rt"],
 ["women campaign lenatzeach_w40 through go.html", "utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w1_ben", "rt"],
];
(async () => { const b = await chromium.launch();
 for (const [lab, qs, want] of CASES) { const { c } = await mk(b); await c.route("**/nlp/a5*.html*", r => r.fulfill({ status: 200, contentType: "text/html", body: "<p>x</p>" }));
  const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html" + (qs ? "?" + qs : "")); const u = await land(p), q = u.searchParams, v = pg(u);
  const ls = await p.evaluate(() => ({ co: localStorage.getItem("nlp_co_ab"), rt: localStorage.getItem("nlp_go_rt_2111"), aff: localStorage.getItem("nlp_aff") })).catch(() => ({}));
  const inQ = new URLSearchParams(qs), kept = [...inQ.keys()].every(k => q.get(k) === inQ.get(k));
  if (want === "a5s") ok(`${lab} -> a5s, exp=cold_2211, go=1, all params kept, checkout B2, owner Ben`, v === "a5s" && q.get("exp") === "cold_2211" && q.get("go") === "1" && kept && ls.co === "b2" && /"c":""/.test(ls.aff || ""), [v, u.search, ls]);
  else ok(`${lab} -> stays in rt_2111 (a5v6/a5v7, exp=rt_2111), params kept`, /^a5v[67]$/.test(v) && q.get("exp") === "rt_2111" && kept && ls.rt === v, [v, u.search, ls]);
  await c.close() }
 { const { c } = await mk(b); const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html?utm_source=instagram&utm_medium=bio"); const u = await land(p);
   ok("instagram bio -> a.html, route=ig_org (unchanged)", pg(u) === "a" && u.searchParams.get("route") === "ig_org" && !u.searchParams.has("exp"), u.search); await c.close() }
 // cold visitor who was already in rt_2111 still goes to a5s; later non-cold visit returns to the stored rt arm
 { const { c } = await mk(b); await c.route("**/nlp/a5*.html*", r => r.fulfill({ status: 200, contentType: "text/html", body: "<p>x</p>" })); const p = await c.newPage();
   await p.goto("https://local.test/nlp/go.html?utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_lab"); const u1 = await land(p);
   await p.goto("https://local.test/nlp/go.html?utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_cold"); const u2 = await land(p);
   await p.goto("https://local.test/nlp/go.html?utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_lab"); const u3 = await land(p);
   ok("same browser: warm -> rt arm, cold -> a5s, warm again -> same rt arm", /^a5v[67]$/.test(pg(u1)) && pg(u2) === "a5s" && pg(u3) === pg(u1), [pg(u1), pg(u2), pg(u3)]); await c.close() }
 // full path on the real a5s (mobile): cold -> a5s -> buy button -> form -> payment page with utm_campaign
 { const { c, hooks, pay } = await mk(b, devices["iPhone 13"]); const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
   await p.goto("https://local.test/nlp/go.html?utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p25"); const u = await land(p); await p.waitForTimeout(1200);
   const hasForm = await p.evaluate(() => !!document.getElementById("lpForm1"));
   await p.evaluate(() => { const e = document.querySelector('[data-cta="hero_main"]') || document.querySelector("[data-checkout]"); e && e.click() }); await p.waitForTimeout(1200);
   await p.fill("#lfName1", "בדיקה קרה"); await p.fill("#lfEmail1", "cold.test@example.com");
   await p.evaluate(() => { const b = document.querySelector('#lpForm1 input[type="checkbox"]:not([hidden])'); if (b && !b.checked) b.click() });
   await p.click('#lpForm1 button[type="submit"]'); await p.waitForURL(/cardcom\.solutions/, { timeout: 8000 }).catch(() => { });
   const body = new URLSearchParams(pay[0] || "");
   ok("cold on real a5s: page with the form, view logged with exp=cold_2211", pg(u) === "a5s" && hasForm && hooks.some(h => h.ev === "view" && /exp=cold_2211/.test(h.qs || "")), [pg(u), hasForm]);
   ok("cold on real a5s: submit -> lead (checkout_details) + payment request with utm_campaign=lenatzeach_cold, variant=a5s, no aff -> Cardcom", hooks.some(h => h.ev === "checkout_details") && body.get("utm_campaign") === "lenatzeach_cold" && body.get("variant") === "a5s" && !body.get("aff") && /cardcom/.test(p.url()), [Object.fromEntries(body), p.url()]);
   ok("cold on real a5s: no JS errors", !errs.length, errs); await c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
