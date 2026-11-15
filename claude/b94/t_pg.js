// ב94: go.html - pg_1611 חצי-חצי a5v6/pr2, קבוע לדפדפן; מדידה עד דף התשלום; טבלת הדשבורד. אייפון 13, האתר מתיקייה מקומית.
// שימוש: node t_pg.js <nlp אחרי הטלאי> <nlp לפני>
process.env.TZ = "Asia/Jerusalem";
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), OLD = path.resolve(process.argv[3]), H = "https://funnel.digitalonline.co.il/nlp/";
const T = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".woff2": "font/woff2", ".json": "application/json" };
let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => {
  const b = await chromium.launch();
  const ctx = async (dir, pre, light) => { const c = await b.newContext({ ...devices["iPhone 13"] }); const ev = [];
    await c.route("**/*", r => { const u = new URL(r.request().url());
      if (u.href.startsWith(H)) { if (light && !/go\.html|a5v6\.html|pr2\.html|a\.html/.test(u.pathname)) return r.fulfill({ status: 204, body: "" });
        const fp = path.join(dir, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "nf" });
        if (light && /a5v6|pr2|\/a\.html/.test(u.pathname)) return r.fulfill({ status: 200, contentType: "text/html", body: "<html><body>stub</body></html>" });
        return r.fulfill({ status: 200, contentType: T[path.extname(fp)] || "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (/make\.com/.test(u.hostname)) { const pd = r.request().postData() || ""; try { const o = Object.fromEntries(new URLSearchParams(pd)); ev.push(o) } catch (e) {} return r.fulfill({ status: 200, body: "{}" }) }
      return r.fulfill({ status: 204, body: "" }) });
    if (pre) await c.addInitScript(pre);
    const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); return { c, p, ev, errs } };
  const land = async (X, qs) => { await X.p.goto(H + "go.html?" + qs); await X.p.waitForURL(/(a5v6|pr2|\/a)\.html/, { timeout: 10000 }); return new URL(X.p.url()) };
  const AD = "utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p24&utm_id=1&fbclid=z";
  // 1. חלוקה: 200 דפדפנים חדשים
  const C = { a5v6: 0, pr2: 0 }; let allExp = true;
  for (let i = 0; i < 200; i++) { const X = await ctx(DIR, null, true); const u = await land(X, AD); const pg = u.pathname.split("/").pop().replace(".html", ""); C[pg] = (C[pg] || 0) + 1; if (u.searchParams.get("exp") !== "pg_1611" || u.searchParams.get("utm_content") !== "p24" || u.searchParams.get("go") !== "1") allExp = false; await X.c.close() }
  ok("split ~50/50 over 200 (each 70-130)", C.a5v6 >= 70 && C.a5v6 <= 130 && C.a5v6 + C.pr2 === 200, JSON.stringify(C));
  ok("all: exp=pg_1611, params kept, go=1", allExp);
  // 2. קבוע לדפדפן: 5 כניסות באותו דפדפן
  const S = await ctx(DIR, null, true); const first = (await land(S, AD)).pathname; let same = true;
  for (let i = 0; i < 4; i++) { const u = await land(S, AD); if (u.pathname !== first) same = false }
  ok("sticky across 5 visits", same, first);
  // 3. שיבוץ קודם ב-ap2_0811
  for (const [o, exp] of [["a5", "a5v6"], ["pr2", "pr2"]]) { const X = await ctx(DIR, `try{localStorage.setItem("nlp_go_ap2_0811","${o}")}catch(e){}`, true); const u = await land(X, AD); ok("ap2_0811=" + o + " → " + exp, u.pathname.endsWith("/" + exp + ".html"), u.pathname); await X.c.close() }
  // 4. אינסטגרם אורגני
  { const X = await ctx(DIR, null, true); const u = await land(X, "utm_source=instagram&utm_medium=bio"); ok("ig bio → a.html route=ig_org, no exp", u.pathname.endsWith("/a.html") && u.searchParams.get("route") === "ig_org" && !u.searchParams.has("exp"), u.href) }
  // 5. מדידה מלאה בכל דף עד דף התשלום (דפים אמיתיים)
  for (const pg of ["a5v6", "pr2"]) {
    const X = await ctx(DIR, `try{localStorage.setItem("nlp_go_pg_1611","${pg}")}catch(e){}`); const u = await land(X, AD + "&aff=gal"); await X.p.waitForTimeout(1500);
    ok(pg + ": landed with exp", u.pathname.endsWith("/" + pg + ".html") && u.searchParams.get("exp") === "pg_1611", u.href);
    ok(pg + ": events carry exp=pg_1611 and aff=gal", X.ev.some(e => (e.variant === pg) && /exp=pg_1611/.test(e.qs || "") && /aff=gal/.test(e.x || "")), JSON.stringify(X.ev[0] || {}).slice(0, 200));
    const px = await X.p.evaluate(() => (window.fbq && window.fbq.queue || []).map(a => [...a].slice(0, 2).join(":")));
    ok(pg + ": pixel PageView", px.includes("track:PageView"), px.join(","));
    await Promise.all([X.p.waitForURL(/checkout\.html/, { timeout: 10000 }).catch(() => {}), X.p.click('[data-cta="hero_main"]')]); await X.p.waitForTimeout(1200);
    const c = new URL(X.p.url());
    ok(pg + ": hero → checkout with v, utm_content, sid, exp", /checkout\.html$/.test(c.pathname) && c.searchParams.get("v") === pg && c.searchParams.get("utm_content") === "p24" && !!c.searchParams.get("sid") && /pg_1611/.test(c.search), c.search);
    ok(pg + ": checkout events with same sid and aff", X.ev.some(e => /^checkout_/.test(e.ev || "") && e.sid === c.searchParams.get("sid") && /aff=gal/.test(e.x || "")));
    ok(pg + ": no JS errors", !X.errs.length, X.errs.join("|")); await X.c.close() }
  // 6. דשבורד: טבלת pg_1611 עם נתונים מדומים
  const row = (t, ev, v, sid, vid, extra) => { const a = Array(21).fill(""); a[0] = "2026-11-15 " + t; a[1] = ev; a[2] = v; a[3] = sid; a[16] = vid; a[17] = "m-ios-fb"; a[8] = "utm_source=fb&utm_medium=paid&utm_id=1&exp=pg_1611&go=1"; Object.assign(a, extra || {}); return a.join("\t") };
  const R = [];
  const sess = (t, v, sid, vid, evs) => evs.forEach((e, i) => R.push(row(t.replace(/:(\d\d)$/, (m, s) => ":" + String(+s + i).padStart(2, "0")), e, v, sid, vid)));
  sess("14:30:00", "a5v6", "s1", "v1", ["view"]); sess("14:31:00", "a5v6", "s2", "v2", ["view", "checkout_view"]); sess("14:32:00", "a5v6", "s3", "v3", ["view", "checkout_view", "checkout_contact_started", "checkout_details"]);
  sess("14:33:00", "pr2", "s4", "v4", ["view"]); sess("14:34:00", "pr2", "s5", "v4", ["view", "checkout_view"]); sess("14:35:00", "pr2", "s6", "v6", ["view", "checkout_view", "checkout_contact_started"]);
  R.push(row("14:36:00", "view", "pr2", "s7", "v7", { 8: "utm_source=fb&utm_medium=paid&exp=ap2_0811" })); // ניסוי אחר - לא נספר
  R.push(row("14:50:00", "purchase", "a5v6", "s3", "", { 8: "cardcom | 297 ILS | deal 990000009 | src ", 13: "cardcom_webhook", 17: "" }));
  const EV = R.join("\n");
  const dash = async dir => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-15T16:00:00+02:00")); const errs = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(dir, "dashboard.html")) });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\n", refunds: "refunds\n", paid: "paid\tat\taff\n", ads: "ads\n" }[a] || "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#op"); await p.waitForTimeout(3000); return { p, errs } };
  const D2 = await dash(DIR), D1 = await dash(OLD);
  const tab = await D2.p.evaluate(() => { const t = document.getElementById("pgT"); return t ? [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())) : null });
  console.log(JSON.stringify(tab));
  const cell = (r, c) => +(tab[r][c] || "").split(" ")[0];
  ok("pg table: people 3/2 (v4 twice = 1), other exp not counted", tab && cell(1, 1) === 3 && cell(1, 2) === 2, tab && tab[1].join("|"));
  ok("pg table: checkout 2/2, started 1/1, leads 1/0, buys 1/0", cell(2, 1) === 2 && cell(2, 2) === 2 && cell(3, 1) === 1 && cell(3, 2) === 1 && cell(4, 1) === 1 && cell(4, 2) === 0 && cell(5, 1) === 1 && cell(5, 2) === 0, tab && tab.slice(2).map(r => r.join("|")).join(" / "));
  ok("pg table: P(best) on leads and buys", /הטוב ביותר/.test(tab[4][1]) && /הטוב ביותר/.test(tab[5][2]));
  ok("dashboard: no JS errors", !D2.errs.length, D2.errs.join("|"));
  const ex = await D2.p.evaluate(() => [EXP.id, EXP.arms.join(","), EXP.start.toISOString(), CHANGELOG[0][1].slice(0, 40), EXPERIMENTS[0].id]);
  ok("EXP=pg_1611 a5v6,pr2 from 14:17; changelog and experiments list", ex[0] === "pg_1611" && ex[1] === "a5v6,pr2" && ex[2] === "2026-11-15T12:17:00.000Z" && /ב94/.test(ex[3]) && ex[4] === "pg_1611", JSON.stringify(ex));
  const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
  for (const s of ["snap", "co", "af", "fin", "up"]) ok("screen " + s + " unchanged", (await scr(D1, s)) === (await scr(D2, s)));
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0)
})();
