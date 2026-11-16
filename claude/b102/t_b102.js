// ב102: go.html on_1611 (a + סליקה A מול a5v6 + B2), שיבוץ קודם, סליקה לפי זרוע, מדידה, דשבורד. שימוש: node t_b102.js <nlp אחרי> <nlp לפני> [shots dir]
process.env.TZ = "Asia/Jerusalem";
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), OLD = path.resolve(process.argv[3]), SH = process.argv[4] ? path.resolve(process.argv[4]) : null, H = "https://funnel.digitalonline.co.il/nlp/";
const T = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".woff2": "font/woff2", ".json": "application/json" };
let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => { const b = await chromium.launch(); if (SH) fs.mkdirSync(SH, { recursive: true });
  const ctx = async (dir, pre, light, dev) => { const c = await b.newContext({ ...(dev || devices["iPhone 13"]) }); const ev = [];
    await c.route("**/*", r => { const u = new URL(r.request().url());
      if (u.href.startsWith(H)) { const fp = path.join(dir, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "nf" });
        if (light && /a5v6|pr2|\/a\.html/.test(u.pathname)) return r.fulfill({ status: 200, contentType: "text/html", body: "<html><body>stub</body></html>" });
        return r.fulfill({ status: 200, contentType: T[path.extname(fp)] || "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (/make\.com/.test(u.hostname)) { const pd = r.request().postData() || ""; try { const o = Object.fromEntries(new URLSearchParams(pd)); o.__hook = u.pathname; ev.push(o) } catch (e) {} return r.fulfill({ status: 200, body: "{}" }) }
      return r.fulfill({ status: 204, body: "" }) });
    if (pre) await c.addInitScript(pre);
    const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); return { c, p, ev, errs } };
  const land = async (X, qs) => { await X.p.goto(H + "go.html?" + qs); await X.p.waitForURL(/(a5v6|pr2|\/a)\.html/, { timeout: 10000 }); return new URL(X.p.url()) };
  const LS = X => X.p.evaluate(() => ({ on: localStorage.getItem("nlp_go_on_1611"), ab: localStorage.getItem("nlp_co_ab") }));
  const AD = "utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p24&utm_id=1&fbclid=z";
  // 1. חלוקה
  const C = { a: 0, a5v6: 0 }; let good = true;
  for (let i = 0; i < 120; i++) { const X = await ctx(DIR, null, true); const u = await land(X, AD); const pg = u.pathname.split("/").pop().replace(".html", ""); C[pg] = (C[pg] || 0) + 1; const l = await LS(X);
    if (u.searchParams.get("exp") !== "on_1611" || u.searchParams.get("utm_content") !== "p24" || l.on !== pg || l.ab !== (pg === "a" ? "a" : "b2")) good = false; await X.c.close() }
  ok("split ~50/50 over 120 (each 40-80), only a/a5v6", C.a >= 40 && C.a <= 80 && C.a + C.a5v6 === 120, JSON.stringify(C));
  ok("all: exp=on_1611, params kept, arm + checkout version stored", good);
  // 2. קבוע
  { const S = await ctx(DIR, null, true); const first = (await land(S, AD)).pathname; let same = true; for (let i = 0; i < 4; i++) { if ((await land(S, AD)).pathname !== first) same = false } ok("sticky across 5 visits", same, first); await S.c.close() }
  // 3. שיבוץ קודם
  for (const [k, val, page, exp] of [["nlp_go_pg_1611", "pr2", "pr2", "pg_1611"], ["nlp_go_pg_1611", "a5v6", "a5v6", "pg_1611"], ["nlp_go_ap2_0811", "a5", "a5v6", "ap2_0811"], ["nlp_go_ap2_0811", "pr2", "pr2", "ap2_0811"]]) {
    const X = await ctx(DIR, `try{localStorage.setItem("${k}","${val}")}catch(e){}`, true); const u = await land(X, AD); const l = await LS(X);
    ok(k + "=" + val + " → " + page + " exp=" + exp + ", not in on_1611", u.pathname.endsWith("/" + page + ".html") && u.searchParams.get("exp") === exp && !l.on && !l.ab, u.href + " " + JSON.stringify(l)); await X.c.close() }
  // 4. אינסטגרם אורגני
  { const X = await ctx(DIR, null, true); const u = await land(X, "utm_source=instagram&utm_medium=bio"); ok("ig bio → a.html route=ig_org, no exp", u.pathname.endsWith("/a.html") && u.searchParams.get("route") === "ig_org" && !u.searchParams.has("exp"), u.href); await X.c.close() }
  // 5. מסלול מלא בכל זרוע (דפים אמיתיים) עד דף התשלום, עם משווק
  for (const [arm, co] of [["a", "a"], ["a5v6", "b2"]]) {
    const X = await ctx(DIR, `try{if(!sessionStorage.getItem("__s")){localStorage.setItem("nlp_go_on_1611","${arm}");localStorage.setItem("nlp_co_ab","${co}");sessionStorage.setItem("__s","1")}}catch(e){}`); const u = await land(X, AD + "&aff=gal"); await X.p.waitForTimeout(1500);
    ok(arm + ": landed with exp=on_1611", u.pathname.endsWith("/" + arm + ".html") && u.searchParams.get("exp") === "on_1611", u.href);
    ok(arm + ": page events carry exp=on_1611 and aff=gal", X.ev.some(e => e.variant === arm && /exp=on_1611/.test(e.qs || "") && /aff=gal/.test(e.x || "")));
    await Promise.all([X.p.waitForURL(/checkout\.html/, { timeout: 10000 }).catch(() => {}), X.p.click('[data-cta="hero_main"] >> nth=0')]); await X.p.waitForTimeout(1500);
    const c = new URL(X.p.url()); const st = await X.p.evaluate(() => ({ co: window.NLP_CO, dco: document.documentElement.getAttribute("data-co"), trust: getComputedStyle(document.getElementById("coTrust")).display, one1: getComputedStyle(document.querySelector(".one1")).display, price: getComputedStyle(document.querySelector(".order .price")).display, pay3: getComputedStyle(document.querySelector(".pay3")).display }));
    ok(arm + ": checkout with v, exp, sid", /checkout\.html$/.test(c.pathname) && c.searchParams.get("v") === arm && /on_1611/.test(c.search) && !!c.searchParams.get("sid"), c.search);
    ok(arm + ": checkout version " + co, st.co === co && st.dco === (co === "a" ? "a" : "b"), JSON.stringify(st));
    if (arm === "a") ok("a: checkout A as it was - price card shown, no one-line card, no trust row, 3 payments line shown (mobile)", st.price !== "none" && st.one1 === "none" && st.trust === "none" && st.pay3 !== "none", JSON.stringify(st));
    else ok("a5v6: B2 as today - one-line card, trust row (mobile)", st.one1 !== "none" && st.trust !== "none" && st.price === "none", JSON.stringify(st));
    if (SH) await X.p.screenshot({ path: path.join(SH, "arm_" + arm + "_checkout_iphone13.png") });
    await X.p.fill("#fName", "בדיקה פנימית"); await X.p.waitForTimeout(500);
    const cs = X.ev.find(e => e.ev === "checkout_contact_started");
    ok(arm + ": checkout_contact_started with co=" + co + ";cx=co_on_1611 and aff=gal", cs && new RegExp("co=" + co + ";cx=co_on_1611").test(cs.x || "") && /aff=gal/.test(cs.x || ""), cs && cs.x);
    await X.p.fill("#fEmail", "t@example.com"); await X.p.fill("#fPhone", "0501234567"); await X.p.check("#fTerms"); await X.p.waitForTimeout(300);
    if (arm === "a") { await X.p.click('form#det button[type="submit"]'); }
    await X.p.waitForTimeout(2500);
    const lp = X.ev.find(e => e.name && e.email && e.co);
    ok(arm + ": payment-page request to Make with co=" + (co === "a" ? "a" : "b"), lp && lp.co === (co === "a" ? "a" : "b"), lp && lp.co);
    ok(arm + ": no JS errors", !X.errs.length, X.errs.join("|")); await X.c.close() }
  // 6. דף התשלום ישירות (חזרה מקארדקום, קישורים ישנים)
  for (const [nm, pre, qs, want] of [["return from Cardcom, arm a (stored)", 'localStorage.setItem("nlp_co_ab","a")', "status=failed", "a"], ["fresh device, no params", "", "", "b2"], ["old B device (ב90)", 'localStorage.setItem("nlp_co_b2","b")', "", "b"], ["old B device but arm b2", 'localStorage.setItem("nlp_co_b2","b");localStorage.setItem("nlp_co_ab","b2")', "", "b2"], ["co=b in URL wins", 'localStorage.setItem("nlp_co_ab","a")', "co=b", "b"], ["exp=on_1611&v=a in URL", "", "exp=on_1611&v=a", "a"]]) {
    const X = await ctx(DIR, pre ? `try{if(!sessionStorage.getItem("__s")){${pre};sessionStorage.setItem("__s","1")}}catch(e){}` : null); await X.p.goto(H + "checkout.html?test=1" + (qs ? "&" + qs : "")); await X.p.waitForTimeout(800);
    const co = await X.p.evaluate(() => window.NLP_CO); ok("checkout: " + nm + " → " + want, co === want, co); await X.c.close() }
  // 7. צילומים: A היום (אחרי) מול A לפני הטלאי, 375x667
  if (SH) for (const [nm, dir] of [["A_before_patch", OLD], ["A_after_patch", DIR], ["B2_after_patch", DIR]]) { const X = await ctx(dir, null, false, { viewport: { width: 375, height: 667 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }); await X.p.goto(H + "checkout.html?test=1&co=" + (nm.startsWith("A") ? "a" : "b2")); await X.p.waitForTimeout(1200); await X.p.screenshot({ path: path.join(SH, nm + "_375x667.png") }); await X.c.close() }
  // 8. דשבורד
  const row = (t, ev, v, sid, vid, qs, extra) => { const a = Array(21).fill(""); a[0] = "2026-11-16 " + t; a[1] = ev; a[2] = v; a[3] = sid; a[16] = vid; a[17] = "m-ios-fb"; a[8] = qs; Object.assign(a, extra || {}); return a.join("\t") };
  const Q = "utm_source=fb&utm_medium=paid&utm_id=1&exp=on_1611&go=1", QA = "utm_source=fb&utm_medium=affiliate&aff=gal&exp=on_1611&go=1"; const R = [];
  const sess = (t, v, sid, vid, evs, qs) => evs.forEach((e, i) => R.push(row(t.replace(/:(\d\d)$/, (m, s) => ":" + String(+s + i).padStart(2, "0")), e, v, sid, vid, qs || Q)));
  sess("20:30:00", "a", "s1", "v1", ["view"]); sess("20:31:00", "a", "s2", "v2", ["view", "checkout_view", "checkout_contact_started", "checkout_details"]); sess("20:32:00", "a", "s3", "v3", ["view", "checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"]);
  sess("20:33:00", "a5v6", "s4", "v4", ["view"]); sess("20:34:00", "a5v6", "s5", "v4", ["view", "checkout_view"]); sess("20:35:00", "a5v6", "s6", "v6", ["view", "checkout_view", "checkout_contact_started"]);
  sess("20:36:00", "a5v6", "s7", "v7", ["view", "checkout_view"], QA); R.forEach((x, i) => { if (/\ts7\t/.test(x)) { const a = x.split("\t"); a[20] = "aff=gal;"; R[i] = a.join("\t") } });
  R.push(row("20:37:00", "view", "pr2", "s8", "v8", "utm_source=fb&utm_medium=paid&exp=pg_1611"));
  const EV = R.join("\n");
  const dash = async dir => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-16T22:00:00+02:00")); const errs = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(dir, "dashboard.html")) });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\n", refunds: "refunds\n", paid: "paid\tat\taff\n", ads: "ads\n", upsell: "upsell\n" }[a] || "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#op"); await p.waitForTimeout(3000); return { p, errs } };
  const D2 = await dash(DIR), D1 = await dash(OLD);
  const tb = id => D2.p.evaluate(id => { const t = document.getElementById(id); return t ? [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())) : null }, id);
  const t1 = await tb("onT"), t2 = await tb("onT2"); console.log(JSON.stringify(t1)); console.log(JSON.stringify(t2));
  const cell = (t, r, c) => +((t[r] || [])[c] || "").split(" ")[0];
  ok("on table (Ben's ads): people 3 / 2 (v4 twice = 1), other exp + aff not counted", t1 && cell(t1, 1, 1) === 3 && cell(t1, 1, 2) === 2, t1 && t1[1] && t1[1].join("|"));
  ok("on table: checkout 2/2, started 2/1, details 2/0, payment form 1/0", cell(t1, 2, 1) === 2 && cell(t1, 2, 2) === 2 && cell(t1, 3, 1) === 2 && cell(t1, 3, 2) === 1 && cell(t1, 4, 1) === 2 && cell(t1, 4, 2) === 0 && cell(t1, 5, 1) === 1 && cell(t1, 5, 2) === 0, t1 && t1.slice(2).map(r => r.join("|")).join(" / "));
  ok("on table (affiliates): 0 / 1 person", t2 && cell(t2, 1, 1) === 0 && cell(t2, 1, 2) === 1, t2 && t2[1] && t2[1].join("|"));
  const note = await D2.p.evaluate(() => document.getElementById("onN").textContent); ok("stop-rule progress shown (3 / 2)", /150/.test(note) && /3 \/ 2/.test(note), note);
  ok("dashboard: no JS errors", !D2.errs.length, D2.errs.join("|"));
  const ex = await D2.p.evaluate(() => [ON_START.toISOString(), CHANGELOG[0][1].slice(0, 30), EXPERIMENTS[0].id, EXPERIMENTS.find(e => e.id === "pg_1611").status]);
  ok("start 20:10, changelog ב102, experiments on_1611 first, pg_1611 closed", ex[0] === "2026-11-16T18:10:00.000Z" && /ב102/.test(ex[1]) && ex[2] === "on_1611" && /נסגר/.test(ex[3]), JSON.stringify(ex));
  const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
  for (const s of ["snap", "co", "af", "fin", "up"]) ok("screen " + s + " unchanged", (await scr(D1, s)) === (await scr(D2, s)));
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
