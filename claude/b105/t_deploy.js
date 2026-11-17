// ב105: בדיקת go.html (on_1711), דף התשלום ו-renderOn. שימוש: node t_deploy.js <new root> <old root>
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
(async () => { const b = await chromium.launch();
 const ctx = async (root, ls, rnd) => { const c = await b.newContext(); await c.addInitScript(([ls, rnd]) => { try { if (!sessionStorage.getItem("_i")) { for (const k in ls) localStorage.setItem(k, ls[k]); sessionStorage.setItem("_i", "1") } } catch (e) {}
   if (rnd != null) crypto.getRandomValues = a => { a[0] = rnd; return a } }, [ls || {}, rnd]);
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: /\.html$/.test(fp) ? "text/html; charset=utf-8" : undefined }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) }); return c };
 const go = async (ls, rnd, q = "?utm_source=fb&utm_medium=paid&utm_id=1") => { const c = await ctx(NEW, ls, rnd), p = await c.newPage(); const urls = []; p.on("request", r => { if (r.isNavigationRequest()) urls.push(r.url()) });
  await p.goto("https://local.test/nlp/go.html" + q); await p.waitForTimeout(700); const st = await p.evaluate(() => ({ k: localStorage.getItem("nlp_go_on_1711"), ab: localStorage.getItem("nlp_co_ab") })); await c.close(); return { u: urls.find(u => !/go\.html/.test(u)) || "", st } };
 let r = await go({}, 0); ok("new visitor rnd=0 -> a, exp=on_1711, co_ab=a", /\/nlp\/a\.html\?.*exp=on_1711/.test(r.u) && r.st.k === "a" && r.st.ab === "a", JSON.stringify(r));
 r = await go({}, 1); ok("new visitor rnd=1 -> a5v7, exp=on_1711, co_ab=b2", /\/nlp\/a5v7\.html\?.*exp=on_1711/.test(r.u) && r.st.k === "a5v7" && r.st.ab === "b2", JSON.stringify(r));
 r = await go({ nlp_go_on_1711: "a5v7" }, 0); ok("returning on_1711 a5v7 stays a5v7", /a5v7\.html\?.*exp=on_1711/.test(r.u), r.u);
 r = await go({ nlp_go_on_1611: "a5v6", nlp_co_ab: "b2" }, 0); ok("legacy on_1611 a5v6 -> a5v6 with exp=on_1611, not assigned to on_1711", /a5v6\.html\?.*exp=on_1611/.test(r.u) && r.st.k === null, JSON.stringify(r));
 r = await go({ nlp_go_on_1611: "a", nlp_co_ab: "a" }, 1); ok("legacy on_1611 a -> a with exp=on_1611", /\/a\.html\?.*exp=on_1611/.test(r.u) && r.st.k === null, JSON.stringify(r));
 r = await go({ nlp_go_pg_1611: "pr2" }, 1); ok("legacy pg_1611 pr2 -> pr2 exp=pg_1611", /pr2\.html\?.*exp=pg_1611/.test(r.u), r.u);
 r = await go({ nlp_go_ap2_0811: "a5" }, 1); ok("legacy ap2_0811 a5 -> a5v6 exp=ap2_0811", /a5v6\.html\?.*exp=ap2_0811/.test(r.u), r.u);
 r = await go({}, 1, "?utm_source=instagram&utm_medium=bio"); ok("ig_org -> a without exp (co_ab assigned)", /\/a\.html\?/.test(r.u) && !/exp=/.test(r.u) && /route=ig_org/.test(r.u) && r.st.ab === "b2", JSON.stringify(r));
 // דף התשלום
 const co = async (q, ls) => { const c = await ctx(NEW, ls), p = await c.newPage(); await p.goto("https://local.test/nlp/checkout.html" + q); await p.waitForTimeout(500); const v = await p.evaluate(() => window.NLP_CO); await c.close(); return v };
 ok("checkout exp=on_1711&v=a -> A (even without co_ab)", (await co("?exp=on_1711&v=a")) === "a");
 ok("checkout exp=on_1711&v=a5v7 -> B2", (await co("?exp=on_1711&v=a5v7")) === "b2");
 ok("checkout exp=on_1611&v=a -> A (unchanged)", (await co("?exp=on_1611&v=a")) === "a");
 ok("checkout no exp, co_ab=a -> A (unchanged)", (await co("?v=a", { nlp_co_ab: "a" })) === "a");
 // הדשבורד
 const row = (t, ev, v, sid, vid, qs) => { const a = Array(21).fill(""); a[0] = "2026-11-17 " + t; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[16] = vid; a[17] = "m-ios-fb"; return a.join("\t") };
 const Q = e => "utm_source=fb&utm_medium=paid&utm_id=1&go=1&exp=" + e;
 const R = [row("14:10:00", "view", "a", "s1", "v1", Q("on_1711")), row("14:11:00", "view", "a5v7", "s2", "v2", Q("on_1711")), row("14:11:30", "checkout_details", "a5v7", "s2", "v2", Q("on_1711")), row("14:12:00", "view", "a5v7", "s3", "v3", Q("on_1711")),
  row("14:13:00", "view", "a5v6", "s4", "v4", Q("on_1611")), row("13:00:00", "view", "a5v7", "s5", "v5", Q("on_1711"))];
 const dash = async root => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 } }); await c.clock.setFixedTime(new Date("2026-11-17T15:00:00+02:00")); const errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(root, "nlp/dashboard.html")) });
   if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: R.join("\n"), spend: "spend\n" }[a] || "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#op"); await p.waitForTimeout(2500); return { p, errs } };
 const D = await dash(NEW), D0 = await dash(OLD);
 const T = await D.p.evaluate(() => [...document.getElementById("onT").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim()))); console.log(JSON.stringify(T.slice(0, 2)), JSON.stringify(T[5]));
 ok("onT header a vs a5v7", /a5v7/.test(T[0][2]) && /סליקה A/.test(T[0][1]), T[0].join("|"));
 ok("people 1 / 2 from start 14:00 (13:00 and on_1611 excluded)", /^1/.test(T[1][1]) && /^2/.test(T[1][2]), T[1].join("|"));
 ok("details 0 / 1", /^0/.test(T[5][1]) && /^1/.test(T[5][2]), T[5].join("|"));
 ok("experiments list: on_1711 active, on_1611 closed", await D.p.evaluate(() => EXPERIMENTS.find(e => e.id === "on_1711").status === "פעיל" && /נסגר/.test(EXPERIMENTS.find(e => e.id === "on_1611").status)));
 ok("ALLV has a5v7", await D.p.evaluate(() => ALLV.includes("a5v7")));
 ok("dashboard no JS errors", !D.errs.length, D.errs.join("|"));
 const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
 for (const s of ["fin", "up", "af", "pr"]) { const o = await scr(D0, s), w = await scr(D, s); ok("screen " + s + " unchanged", o === w); if (o !== w) { const ol = o.split("\n"), wl = w.split("\n"); console.log("  OLD-only:", ol.filter(x => !wl.includes(x)).join(" / ")); console.log("  NEW-only:", wl.filter(x => !ol.includes(x)).join(" / ")) } }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
