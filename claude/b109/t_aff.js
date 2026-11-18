// ב109: כניסה ל-a5s.html עם aff נספרת בלשונית המשווקים (ביקור, הגעה לסליקה, רכישה).
// האירועים נאספים מהדפים עצמם (a5s ודף התשלום), ומוזנים לדשבורד. שימוש: node t_aff.js <root>
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const COLS = ["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp" };
(async () => { const b = await chromium.launch(); const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-18T16:00:00+02:00")); const EV = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
  if (u.hostname.endsWith("make.com")) { const d = r.request().postData(); if (d && /(^|&)ev=/.test(d)) EV.push(Object.fromEntries(new URLSearchParams(d))); return r.fulfill({ status: 200, body: "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); await p.goto("https://local.test/nlp/a5s.html?utm_source=fb&utm_medium=affiliate&aff=zzqa&utm_content=p25_brain_c1"); await p.waitForTimeout(1500);
 const owner = await p.evaluate(() => NLP_OWNER()); ok("a5s with aff: NLP_OWNER = zzqa", owner === "zzqa", owner);
 const href = await p.getAttribute('[data-cta="offer"]', "href"); ok("checkout link keeps aff + v=a5s", /aff=zzqa/.test(href) && /v=a5s/.test(href), href);
 await p.click('[data-cta="offer"]'); await p.waitForURL(/checkout/); await p.waitForTimeout(2500);
 const coOwner = await p.evaluate(() => window.NLP_OWNER ? NLP_OWNER() : "?"); ok("checkout: NLP_OWNER = zzqa", coOwner === "zzqa", coOwner);
 const view = EV.find(e => e.ev === "view" && e.variant === "a5s"), chk = EV.find(e => /^checkout_/.test(e.ev));
 ok("view event from a5s carries aff", view && /aff=zzqa/.test((view.qs || "") + ";" + (view.x || "")), JSON.stringify(view).slice(0, 300));
 ok("checkout event carries aff", chk && /aff=zzqa/.test((chk.qs || "") + ";" + (chk.x || "")), JSON.stringify(chk || {}).slice(0, 300));
 // לגיליון: כל אירוע שורה, כמו ש-Make כותב (ts בשעון ישראל)
 const ts = (i) => "2026-11-18 15:" + String(10 + i).padStart(2, "0") + ":00";
 const rows = EV.map((e, i) => COLS.map(k => k === "ts" ? ts(i) : (e[k] || "").replace(/[\t\n]/g, " ")).join("\t"));
 const sid = view.sid; rows.push(COLS.map(k => ({ ts: "2026-11-18 15:59:00", ev: "purchase", variant: "a5s", sid, qs: "cardcom | 297 ILS | deal 999001 | src fb", cta: "cardcom_webhook", x: "aff=zzqa" })[k] || "").join("\t"));
 const d = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 } }); await d.clock.setFixedTime(new Date("2026-11-18T16:00:00+02:00"));
 await d.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(ROOT, "nlp/dashboard.html")) });
  if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: rows.join("\n"), spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\nzzqa\tמשווק QA\t\t1\t\t\n" }[a] || "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const q = await d.newPage(); const errs = []; q.on("pageerror", e => errs.push(e.message)); await q.goto("https://local.test/nlp/dashboard.html#af"); await q.waitForTimeout(3000);
 const T = await q.evaluate(() => [...document.getElementById("afTable").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())));
 console.log(T[0].join(" | "));  const r = T.find(x => /משווק QA|zzqa/.test(x[0])); console.log(r && r.join(" | "));
 const col = name => T[0].findIndex(h => h.startsWith(name));
 ok("affiliate tab: zzqa row with 1 visit, 1 visitor, reached checkout 1, 1 purchase", r && r[col("ביקורים")] === "1" && r[col("מבקרים")] === "1" && /(^| )1\/1$/.test(r[col("הגיעו לסליקה")]) && /^1/.test(r[col("רכישות")]), r && r.join("|"));
 const B = await q.evaluate(() => [...document.getElementById("afBuys").rows].map(r => r.innerText.replace(/\s+/g, " ")).join(" / "));
 ok("purchase listed under the affiliate", /משווק QA|zzqa/.test(B), B.slice(0, 300));
 ok("dashboard no JS errors", !errs.length, errs.join("|"));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
