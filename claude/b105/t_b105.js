// ב105: בדיקות וצילומים ל-a5v7. שימוש: node t_b105.js <nlp dir with a5v7*.html and a5v6.html> [shots dir]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [DIR, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
(async () => { const b = await chromium.launch();
 const open = async (file, vp, opts = {}) => { const c = await b.newContext(Object.assign({ viewport: vp, deviceScaleFactor: opts.dpr || 1, isMobile: vp.width < 500, hasTouch: vp.width < 500 }, opts.ctx || {})); const errs = [], ev = [];
  await c.route("**/*", r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(DIR, u.pathname.replace(/^\/nlp\//, "")); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: ({html:"text/html; charset=utf-8",svg:"image/svg+xml",webp:"image/webp",png:"image/png",jpg:"image/jpeg",woff2:"font/woff2",mp4:"video/mp4",js:"text/javascript",css:"text/css"})[fp.split(".").pop()] }) : r.fulfill({ status: 404, body: "" }) }
   if (/make\.com/.test(u.href)) { const p = r.request().postData() || ""; ev.push(Object.fromEntries(new URLSearchParams(p))); return r.fulfill({ status: 200, body: "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/" + file + "?utm_source=claude_test"); await p.waitForTimeout(1500); return { c, p, errs, ev } };
 const heroCta = p => p.evaluate(() => { const e = document.querySelector('[data-sec="1"] [data-cta="hero_main"]').getBoundingClientRect(); return { top: Math.round(e.top), bottom: Math.round(e.bottom), vh: innerHeight } });
 // 1. כפתור הפתיחה במסך הראשון - 3 ההוקים, 375x667 ו-390x844
 for (const [h, file] of [["a", "a5v7.html"], ["b", "a5v7_hookb.html"], ["c", "a5v7_hookc.html"]]) for (const vp of [{ width: 375, height: 667 }, { width: 390, height: 844 }]) {
  const X = await open(file, vp, { dpr: 2 }); const r = await heroCta(X.p);
  ok("hook " + h + " " + vp.width + "x" + vp.height + ": hero_main in first screen", r.bottom <= r.vh && r.top >= 0, JSON.stringify(r));
  if (SH) await X.p.screenshot({ path: path.join(SH, "first_screen_hook" + h + "_" + vp.width + "x" + vp.height + ".png") });
  ok("hook " + h + " " + vp.width + ": no JS errors", !X.errs.length, X.errs.join("|")); await X.c.close() }
 { const X = await open("a5v6.html", { width: 375, height: 667 }, { dpr: 2 }); const r = await heroCta(X.p); console.log("a5v6 375x667 hero_main", JSON.stringify(r)); if (SH) await X.p.screenshot({ path: path.join(SH, "first_screen_a5v6_375x667.png") }); await X.c.close() }
 // 2. סדר, הסרה, מספור, מדידה
 const X = await open("a5v7.html", { width: 390, height: 844 }, { dpr: 2 });
 const info = await X.p.evaluate(() => ({ v: document.documentElement.dataset.variant || document.querySelector("[data-variant]").getAttribute("data-variant"), robots: (document.querySelector('meta[name="robots"]') || {}).content,
  secs: [...document.querySelectorAll("[data-sec]")].map(e => e.dataset.sec + ":" + e.dataset.name), stages: [...document.querySelectorAll("[data-stage]")].map(e => e.dataset.stage),
  h1: document.querySelector("h1").innerText, sub: document.querySelector(".hero9 .sub").innerText, eyebrow: !!document.querySelector(".hero9 .eyebrow"), why: /למה בניתי את השיטה/.test(document.body.innerText),
  ctas: [...document.querySelectorAll("a.cta[data-cta]")].map(a => a.dataset.cta), checkout: [...document.querySelectorAll("a.cta[data-checkout]")].slice(0, 2).map(a => a.getAttribute("href")) }));
 console.log(JSON.stringify(info, null, 0));
 ok("variant a5v7, noindex", info.v === "a5v7" && /noindex/.test(info.robots || ""), info.v + " " + info.robots);
 ok("'למה בניתי' removed", !info.why && !info.secs.some(s => /למה בניתי/.test(s)));
 ok("data-sec 1..14 in order", info.secs.every((s, i) => +s.split(":")[0] === i + 1) && info.secs.length === 14, info.secs.join(","));
 const order = info.secs.map(s => s.split(":")[1]); const want = ["פתיחה", "רגע לפני", "מה אם", "לדעת או להטמיע", "איך נראית המציאות", "עם מה תצא", "מה יש בפנים", "בונוסים", "ההצעה", "מה אומרים", "תוצאות אמיתיות", "למי מתאים", "איך מתחילים", "שאלות"];
 ok("section order as spec", JSON.stringify(order) === JSON.stringify(want), order.join(" > "));
 ok("hook A text, no eyebrow", /שוב הלכת לישון/.test(info.h1) && /אבל למה זה ממשיך לקרות לך/.test(info.sub) && !info.eyebrow, info.h1 + " | " + info.sub);
 ok("guarantee right after offer, final CTA after FAQ", (() => { const o = info.ctas; return o.indexOf("offer") < o.indexOf("guar") && o.indexOf("guar") < o.indexOf("cta1") && o.indexOf("final") > o.indexOf("cta1") })(), info.ctas.join(","));
 // גלילה עד הסוף: אירועי section עולים, section_view לכל שלב, הכפתור הצף
 for (let y = 0; y < 40; y++) { await X.p.mouse.wheel(0, 700); await X.p.waitForTimeout(120) }
 await X.p.waitForTimeout(1200);
 const secEv = X.ev.filter(e => e.ev === "section").map(e => +e.section), sv = X.ev.filter(e => e.ev === "section_view").map(e => e.name);
 ok("section events increase to 14", secEv.length > 5 && secEv.every((v, i) => !i || v > secEv[i - 1]) && Math.max(...secEv) === 14, secEv.join(","));
 ok("section_view for each stage incl. guarantee", ["hook", "pain", "cause", "old", "result", "course", "offer", "guarantee", "proof", "method", "objections"].every(s => sv.includes(s)), sv.join(","));
 ok("events carry variant a5v7", X.ev.filter(e => e.ev).every(e => e.variant === "a5v7"), [...new Set(X.ev.map(e => e.variant))].join(","));
 ok("sticky CTA shown after scroll", await X.p.evaluate(() => document.getElementById("sticky").classList.contains("on")));
 ok("no JS errors (scroll)", !X.errs.length, X.errs.join("|"));
 // צילומים מלאים
 if (SH) { const full = async (vp, name, dpr) => { const Y = await open("a5v7.html", vp, { dpr }); for (let y = 0; y < 45; y++) { await Y.p.mouse.wheel(0, 600); await Y.p.waitForTimeout(80) } await Y.p.evaluate(() => scrollTo(0, 0)); await Y.p.waitForTimeout(800);
   await Y.p.evaluate(() => { const s = document.getElementById("sticky"); if (s) s.style.display = "none"; const pr = document.getElementById("prog"); if (pr) pr.style.display = "none" });
   await Y.p.screenshot({ path: path.join(SH, name), fullPage: true }); await Y.c.close() };
  await full({ width: 390, height: 844 }, "a5v7_full_mobile_390.png", 1); await full({ width: 1366, height: 900 }, "a5v7_full_desktop_1366.png", 1) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
