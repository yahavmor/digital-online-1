// ב111: קישור של בן לדף הקצר (בלי aff) - שיוך, סליקה, אירועים, ודשבורד. שימוש: node t_b111.js <root> <out json>
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, OUT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp" };
const BEN = c => "utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=" + c, RAMI = "aff=rami&utm_source=fb&utm_medium=affiliate&utm_campaign=NLP+%2F+Aff+rami+%2F+Sales+%2F+Cold+%2F+W40+%2F+a5s&utm_content=w1_promised";
(async () => { const b = await chromium.launch(); const ALL = [];
 const visit = async (q, ls, tag, i) => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-19T12:0" + i + ":00+02:00")); const EV = [];
  await c.addInitScript(ls => { try { if (!sessionStorage.getItem("_i")) { for (const k in ls) localStorage.setItem(k, ls[k]); sessionStorage.setItem("_i", "1") } } catch (e) {} }, ls || {});
  await c.route("**/*", r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { const d = r.request().postData(); if (d && /(^|&)ev=/.test(d)) EV.push(Object.fromEntries(new URLSearchParams(d))); return r.fulfill({ status: 200, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto("https://local.test/nlp/a5s.html?" + q); await p.waitForTimeout(1200);
  const owner = await p.evaluate(() => NLP_OWNER()); await p.click('[data-cta="offer"]'); await p.waitForURL(/checkout/); await p.waitForTimeout(2000);
  const co = await p.evaluate(() => ({ co: window.NLP_CO, owner: NLP_OWNER(), url: location.search }));
  await c.close(); EV.forEach(e => ALL.push(e)); return { tag, owner, co, ev: EV } };
 const r1 = await visit(BEN("w1_ben"), {}, "ben w1 fresh", 1);
 ok("Ben link, new browser: owner ben, checkout owner ben", r1.owner === "" && r1.co.owner === "", JSON.stringify(r1.co));
 ok("Ben link: checkout gets v=a5s and utm_content=w1_ben", /v=a5s/.test(r1.co.url) && /utm_content=w1_ben/.test(r1.co.url) && !/aff=/.test(r1.co.url), r1.co.url);
 console.log("   checkout version (new browser):", r1.co.co);
 const r2 = await visit(BEN("w2_ben"), { nlp_aff: JSON.stringify({ c: "gal", t: Date.now() - 2 * 864e5 }) }, "ben w2 prior gal", 2);
 ok("Ben link after an affiliate click: owner resets to ben (utm_medium=paid)", r2.owner === "" && r2.co.owner === "", JSON.stringify([r2.owner, r2.co.owner]));
 const r3 = await visit(BEN("w3_ben"), { nlp_go_on_1711: "a", nlp_co_ab: "a" }, "ben w3 browser in on_1711 arm a", 3);
 console.log("   checkout version (browser already in on_1711 arm a):", r3.co.co);
 const r4 = await visit(RAMI, {}, "rami", 4);
 ok("Rami link: owner rami", r4.owner === "rami" && r4.co.owner === "rami", JSON.stringify(r4.co));
 ok("events from Ben's visits carry no aff", [r1, r2, r3].every(r => r.ev.every(e => !/aff=/.test((e.qs || "") + ";" + (e.x || "")))), "");
 // rows + purchases (webhook rows, like Make writes) -> json for the dashboard and the daily scripts
 const ts = i => "2026-11-19 12:" + String(10 + i).padStart(2, "0") + ":00";
 const rows = ALL.map((e, i) => COLS.map(k => k === "ts" ? ts(i % 40) : (e[k] || "").replace(/[\t\n]/g, " ")).join("\t"));
 const sidOf = r => r.ev.find(e => e.ev === "view").sid;
 rows.push(COLS.map(k => ({ ts: "2026-11-19 12:55:00", ev: "purchase", variant: "a5s", sid: sidOf(r1), qs: "cardcom | 297 ILS | deal 990001 | src facebook", cta: "cardcom_webhook" })[k] || "").join("\t"));
 rows.push(COLS.map(k => ({ ts: "2026-11-19 12:56:00", ev: "purchase", variant: "a5s", sid: sidOf(r4), qs: "cardcom | 297 ILS | deal 990002 | src fb", cta: "cardcom_webhook", x: "aff=rami" })[k] || "").join("\t"));
 fs.writeFileSync(OUT, JSON.stringify({ content: COLS.join("\t") + "\n" + rows.join("\n") }));
 // dashboard
 const d = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 } }); await d.clock.setFixedTime(new Date("2026-11-19T13:30:00+02:00"));
 await d.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(ROOT, "nlp/dashboard.html")) });
  if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: rows.join("\n"), spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\nrami\tרמי\t0\ttrue\t220\t30\n" }[a] || "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const q = await d.newPage(); const errs = []; q.on("pageerror", e => errs.push(e.message)); await q.goto("https://local.test/nlp/dashboard.html#snap"); await q.waitForTimeout(3000);
 const res = await q.evaluate(() => { const M = build(new Date(0), new Date(Date.now() + 864e5)); return { sess: M.sess.map(s => ({ v: s.v, src: s.src, aff: s.aff || "", cr: s.cr, chk: !!s.chk })), buys: M.allBuys.map(b => ({ aff: b.aff || "", v: b.s && b.s.v, cr: b.s && b.s.cr })) } });
 console.log(JSON.stringify(res));
 const ben = res.sess.filter(s => !s.aff && s.v === "a5s");
 ok("dashboard: 3 Ben sessions on a5s, source 'מודעות Meta', no aff", ben.length === 3 && ben.every(s => s.src === "מודעות Meta"), JSON.stringify(ben));
 ok("dashboard: Ben sessions split by utm_content w1_ben/w2_ben/w3_ben", ["w1_ben", "w2_ben", "w3_ben"].every(c => ben.some(s => (s.cr || "").includes(c))), JSON.stringify(ben.map(s => s.cr)));
 ok("dashboard: Rami session separate (aff=rami)", res.sess.some(s => s.aff === "rami" && s.v === "a5s"), "");
 ok("dashboard: Ben purchase without aff, Rami purchase with aff=rami", res.buys.some(x => !x.aff && x.v === "a5s") && res.buys.some(x => x.aff === "rami"), JSON.stringify(res.buys));
 const snap = await q.evaluate(() => document.getElementById("snapAds").innerText); ok("snap ads table lists w1_ben", /w1_ben/.test(snap), snap.slice(0, 200));
 ok("dashboard no JS errors", !errs.length, errs.join("|"));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
