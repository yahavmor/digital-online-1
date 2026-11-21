// ב115: הרצות מדומות של go.html החדש. שימוש: node t_go.js <root עם nlp/> [N לחלוקה, ברירת מחדל 400]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, NN] = process.argv.slice(2), N = +(NN || 400); let n = 0, f = 0;
const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 400))) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };
async function mk(b, dev, pre) { const c = await b.newContext(dev || {}); const hooks = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
  if (u.hostname.endsWith("make.com")) { hooks.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))); return r.fulfill({ status: 200, contentType: "application/json", body: "{}" }) }
  return r.fulfill({ status: 204, body: "" }) });
 if (pre) await c.addInitScript(pre);
 return { c, hooks } }
const land = async (p) => { await p.waitForURL(u => !/\/go\.html/.test(u.toString()), { timeout: 8000 }).catch(() => { }); await p.waitForTimeout(300); return new URL(p.url()) };
const pg = u => u.pathname.split("/").pop().replace(".html", "");
(async () => { const b = await chromium.launch();
 // 1. חלוקה: N דפדפנים חדשים
 const cnt = { a5v6: 0, a5v7: 0, other: 0 };
 for (let i = 0; i < N; i += 20) { await Promise.all(Array.from({ length: Math.min(20, N - i) }, async () => {
   const { c } = await mk(b); await c.route("**/nlp/a5v*.html*", r => r.fulfill({ status: 200, contentType: "text/html", body: "<p>x</p>" }));
   const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html?utm_source=facebook&utm_medium=paid"); const u = await land(p);
   const k = pg(u); cnt[k in cnt ? k : "other"]++; await c.close() })) }
 const sh = cnt.a5v6 / N, se = Math.sqrt(0.8 * 0.2 / N);
 ok(`split ${N} new browsers: a5v6 ${cnt.a5v6} (${(sh * 100).toFixed(1)}%), a5v7 ${cnt.a5v7}, other ${cnt.other} - within 3 SE of 80%`, cnt.other === 0 && Math.abs(sh - 0.8) <= 3 * se, cnt);
 // 2. החלוקה עצמה, בלי אקראיות: כל 100 הערכים של n
 { const res = { a5v6: 0, a5v7: 0 }; for (let k = 0; k < 100; k++) { const { c } = await mk(b, null, `crypto.getRandomValues=function(a){a[0]=${k}+100*7;return a}`);
   await c.route("**/nlp/a5v*.html*", r => r.fulfill({ status: 200, contentType: "text/html", body: "<p>x</p>" }));
   const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html"); res[pg(await land(p))]++; await c.close() }
  ok("exact split over all 100 values: 80 a5v6 / 20 a5v7", res.a5v6 === 80 && res.a5v7 === 20, res) }
 // 3. קבוע לדפדפן + שיבוץ ישן של on_1711 מוגרל מחדש + B2
 { const { c } = await mk(b, null, `if(!sessionStorage.getItem("x")){sessionStorage.setItem("x",1);localStorage.setItem("nlp_go_on_1711","a");localStorage.setItem("nlp_co_ab","a")}`);
   const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html"); const u1 = await land(p); const s1 = await p.evaluate(() => [localStorage.getItem("nlp_go_rt_2111"), localStorage.getItem("nlp_co_ab"), localStorage.getItem("nlp_go_on_1711")]);
   ok("old on_1711 'a' visitor is re-drawn into a5v6/a5v7, nlp_co_ab -> b2, old key kept", /^a5v[67]$/.test(pg(u1)) && s1[0] === pg(u1) && s1[1] === "b2" && s1[2] === "a", [pg(u1), s1]);
   const seen = new Set(); for (let i = 0; i < 6; i++) { await p.goto("https://local.test/nlp/go.html?utm_source=email"); seen.add(pg(await land(p))) }
   ok("same browser always gets the same page (6 more visits)", seen.size === 1 && seen.has(pg(u1)), [...seen]); await c.close() }
 // 4. utm ו-aff נשמרים, exp=rt_2111, go=1, ושיוך למשווק
 { const { c } = await mk(b); const p = await c.newPage();
   await p.goto("https://local.test/nlp/go.html?aff=rami&utm_source=facebook&utm_medium=paid&utm_campaign=c1&utm_content=w1_promised&fbclid=XYZ"); const u = await land(p); const q = u.searchParams;
   ok("aff + utm_* + fbclid kept, exp=rt_2111, go=1", q.get("aff") === "rami" && q.get("utm_source") === "facebook" && q.get("utm_medium") === "paid" && q.get("utm_campaign") === "c1" && q.get("utm_content") === "w1_promised" && q.get("fbclid") === "XYZ" && q.get("exp") === "rt_2111" && q.get("go") === "1", u.search);
   ok("aff=rami saved as owner (nlp_aff)", /"c":"rami"/.test(await p.evaluate(() => localStorage.getItem("nlp_aff") || "")), await p.evaluate(() => localStorage.getItem("nlp_aff")));
   await c.close() }
 // 5. קישורי המיילים
 for (const qs of ["utm_source=email&utm_medium=email&utm_campaign=nlp_rec1", "utm_source=responder&utm_medium=email&utm_campaign=mail3"]) { const { c } = await mk(b); const p = await c.newPage();
   await p.goto("https://local.test/nlp/go.html?" + qs); const u = await land(p); const q = u.searchParams;
   ok(`email link (${qs.split("&")[0]}) lands on a5v6/a5v7 with utm kept, exp=rt_2111, owner = Ben`, /^a5v[67]$/.test(pg(u)) && q.get("utm_source") === new URLSearchParams(qs).get("utm_source") && q.get("utm_campaign") === new URLSearchParams(qs).get("utm_campaign") && q.get("exp") === "rt_2111" && /"c":""/.test(await p.evaluate(() => localStorage.getItem("nlp_aff") || "")), [pg(u), u.search]);
   await c.close() }
 // 6. אינסטגרם אורגני בלי שינוי
 { const { c } = await mk(b); const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html?utm_source=instagram&utm_medium=bio"); const u = await land(p);
   ok("instagram bio -> a.html, route=ig_org, no exp, nlp_co_ab not set", pg(u) === "a" && u.searchParams.get("route") === "ig_org" && !u.searchParams.has("exp") && (await p.evaluate(() => localStorage.getItem("nlp_co_ab"))) === null, [pg(u), u.search]); await c.close() }
 // 7. כפתור קנייה -> סליקה B2, עם aff ו-utm, בשני הדפים (נייד)
 for (const want of ["a5v6", "a5v7"]) { const k = want === "a5v6" ? 0 : 99;
  const { c, hooks } = await mk(b, devices["iPhone 13"], `crypto.getRandomValues=function(a){a[0]=${k};return a}`); const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto("https://local.test/nlp/go.html?aff=gal&utm_source=facebook&utm_medium=paid&utm_content=p25_brain_c3"); const u = await land(p);
  await p.waitForTimeout(1200);
  const btn = await p.$("[data-checkout]"); await btn.scrollIntoViewIfNeeded(); await btn.click();
  await p.waitForURL(/checkout\.html/, { timeout: 8000 }).catch(() => { }); await p.waitForTimeout(1500);
  const cu = new URL(p.url()), co = await p.evaluate(() => [window.NLP_CO, document.documentElement.getAttribute("data-co2")]).catch(() => []);
  console.log("   checkout url:", cu.search); const ow = await p.evaluate(() => typeof NLP_OWNER === "function" ? NLP_OWNER() : "?").catch(() => "?");
  ok(`${want}: buy button -> checkout.html, B2 (NLP_CO=b2), utm_content + exp in checkout url, owner gal`, pg(u) === want && pg(cu) === "checkout" && co[0] === "b2" && co[1] === "1" && cu.searchParams.get("utm_content") === "p25_brain_c3" && cu.searchParams.get("exp") === "rt_2111" && ow === "gal", [pg(u), cu.pathname + cu.search, co, ow]);
  const owner = hooks.filter(h => h.aff !== undefined || h.owner !== undefined).map(h => h.aff || h.owner);
  ok(`${want}: tracking events carry exp=rt_2111 and owner gal`, hooks.some(h => JSON.stringify(h).includes("rt_2111")) && hooks.some(h => JSON.stringify(h).includes("gal")), hooks.slice(0, 3));
  ok(`${want}: no JS errors`, !errs.length, errs); await c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
