// ב106: שאלה שלישית (טווח גיל) בדף התודה ועמודת גיל בלשונית 14. שימוש: node t_b81.js <new root> <old root> [shots dir]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const VERIFY = "s9ay2kp6sldk9527d77seuuq83xxto60", UPS = "qhq5knj8mf2npzvmn4wufssrsk7uzyqd", TRK = "axjt5wu2oh5vf4zz9uut24s1m79ot6jc";
(async () => { const b = await chromium.launch();
 const thanks = async (root, o = {}) => { const c = await b.newContext(o.mobile ? { ...devices["iPhone SE"], deviceScaleFactor: 2 } : { viewport: { width: 1280, height: 900 } }); const beacons = [], errs = [];
  await c.addInitScript(() => { try { sessionStorage.setItem("cc_lp", "LP-TEST-1"); localStorage.setItem("nlp_lc", JSON.stringify({ v: "a", sid: "s-buy" })) } catch (e) {} });
  if (o.answered) await c.addInitScript(n => { try { for (let i = 1; i <= n; i++) localStorage.setItem("srv_123456_q" + i, "1") } catch (e) {} }, o.answered);
  await c.route("**/*", async r => { const u = r.request().url();
   if (u.startsWith("https://local.test/")) { const fp = path.join(root, new URL(u).pathname); return fs.existsSync(fp) ? r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(fp) }) : r.fulfill({ status: 404, body: "" }) }
   if (u.includes(VERIFY)) { await new Promise(z => setTimeout(z, 1200)); return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(o.fail ? { ok: false } : { ok: true, link: "https://x.schooler.biz/c/1", deal: "123456" }) }) }
   if (u.includes(UPS)) return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(o.up ? { up: "A".repeat(32) } : {}) });
   if (u.includes(TRK)) { beacons.push(Object.fromEntries(new URLSearchParams(r.request().postData() || ""))); return r.fulfill({ status: 200, body: "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/thanks.html" + (o.q ?? "?ups=1")); return { c, p, beacons, errs } };
 const vis = (p, id) => p.evaluate(id => { const e = document.getElementById(id); if (!e || e.hidden || e.closest("[hidden]")) return null; const r = e.getBoundingClientRect(); return { top: Math.round(r.top + scrollY), bottom: Math.round(r.bottom + scrollY) } }, id);
 // 1. שלוש שאלות אחרי האימות; כפתור הקורס במקום; לחיצה בכל שאלה שולחת אירוע
 for (const mobile of [false, true]) { const tag = mobile ? "mobile" : "desktop";
  const T = await thanks(NEW, { mobile }), O = await thanks(OLD, { mobile }); await T.p.waitForTimeout(2000); await O.p.waitForTimeout(2000);
  const g = await vis(T.p, "go"), g0 = await vis(O.p, "go");
  ok(tag + ": q1, q2, q3 shown", !!(await vis(T.p, "srvQ1")) && !!(await vis(T.p, "srvQ2")) && !!(await vis(T.p, "srvQ3")));
  ok(tag + ": title says 3 questions", /^3 שאלות/.test(await T.p.textContent("#srvH")));
  ok(tag + ": 6 age buttons in order", (await T.p.$$eval("#srvQ3 button", x => x.map(b => b.textContent).join(","))) === "18-24,25-34,35-44,45-54,55-64,65+");
  ok(tag + ": course button at the same place as today", g && g0 && g.top === g0.top, JSON.stringify([g, g0]));
  if (mobile) { ok("mobile: course button still in first screen (667)", g && g.bottom <= 667, JSON.stringify(g)); if (SH) { await T.p.screenshot({ path: path.join(SH, "b106_thanks_375_full.png"), fullPage: true }); await (await T.p.$("#srv")).screenshot({ path: path.join(SH, "b106_thanks_375_survey.png") }) } }
  else if (SH) await (await T.p.$("#srv")).screenshot({ path: path.join(SH, "b106_thanks_desktop_survey.png") });
  if (!mobile) {
   await T.p.click('#srvQ1 button[data-a="video"]'); await T.p.click('#srvQ2 button[data-a="facebook"]'); await T.p.waitForTimeout(300);
   ok("after 2 answers: thanks line not yet, q3 still shown", (await vis(T.p, "srvTy")) === null && !!(await vis(T.p, "srvQ3")));
   await T.p.click('#srvQ3 button[data-a="a45_54"]'); await T.p.waitForTimeout(300);
   const e = T.beacons.filter(x => x.ev === "buyer_survey");
   ok("q3 click sends buyer_survey cta=q3 name=a45_54 x=deal=123456", e.length === 3 && e[2].cta === "q3" && e[2].name === "a45_54" && e[2].x === "deal=123456" && e[2].sid === "s-buy", JSON.stringify(e));
   ok("after 3 answers: q3 hidden, thanks line shown", (await vis(T.p, "srvQ3")) === null && !!(await vis(T.p, "srvTy")));
   ok("no email/phone fields in beacons", T.beacons.every(x => !("email" in x) && !("phone" in x)));
   await T.p.reload(); await T.p.waitForTimeout(2200); ok("after reload (3 answered) survey not shown", (await vis(T.p, "srv")) === null);
   ok("no JS errors on thanks", !T.errs.length, T.errs.join("|")) }
  await T.c.close(); await O.c.close() }
 // 2. מי שכבר ענה על 2 השאלות של ב81 רואה רק את שאלת הגיל
 { const T = await thanks(NEW, { answered: 2 }); await T.p.waitForTimeout(2000); ok("answered q1+q2 before: only q3 shown", !!(await vis(T.p, "srv")) && (await vis(T.p, "srvQ1")) === null && (await vis(T.p, "srvQ2")) === null && !!(await vis(T.p, "srvQ3"))); await T.c.close() }
 // 3. אימות נכשל - אין שאלות
 { const T = await thanks(NEW, { fail: true }); await T.p.waitForTimeout(9000); ok("verify failed: no survey", (await vis(T.p, "srv")) === null); await T.c.close() }
 // 4. ההפניה לאפסייל לא השתנתה
 for (const [lab, root] of [["new", NEW], ["old", OLD]]) { const T = await thanks(root, { up: true, q: "" }); await T.p.waitForTimeout(3600); ok("upsell redirect (" + lab + ")", /upsell-97\.html\?t=A{32}/.test(T.p.url()), T.p.url()); await T.c.close() }

 // ===== הדשבורד =====
 const row = (ts, ev, v, sid, vid, qs, o = {}) => { const a = Array(21).fill(""); a[0] = ts; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[13] = o.cta || ""; a[11] = o.name || ""; a[16] = vid; a[17] = o.dev || ""; a[20] = o.x || ""; return a.join("\t") };
 const Q1 = "utm_source=facebook&utm_medium=paid&utm_id=1&utm_campaign=lenatzeach_lab&utm_content=car4_warm_a", Q2 = "utm_source=fb&utm_medium=affiliate&aff=gal&utm_content=p25_brain_c3&utm_campaign=NLP+%7C+Aff+gal";
 const R = [row("2026-11-10 10:00:00", "view", "pr2", "s1", "v1", Q1, { dev: "m-android-fb" }), row("2026-11-12 06:40:00", "view", "pr2", "s2", "v1", Q1, { dev: "m-android-fb" }), row("2026-11-12 06:44:00", "checkout_view", "pr2", "s2", "v1", Q1, { dev: "m-android-fb" }),
  row("2026-11-12 06:47:00", "purchase", "pr2", "s2", "", "cardcom | 297 ILS | deal 111 | src facebook", { cta: "cardcom_webhook" }),
  row("2026-11-12 06:48:00", "buyer_survey", "pr2", "s2", "", "", { cta: "q1", name: "testimonials", x: "deal=111" }), row("2026-11-12 06:48:10", "buyer_survey", "pr2", "s2", "", "", { cta: "q2", name: "other", x: "deal=111" }), row("2026-11-12 06:48:20", "buyer_survey", "pr2", "s2", "", "", { cta: "q3", name: "a45_54", x: "deal=111" }),
  row("2026-11-14 20:00:00", "view", "a5v6", "s3", "v3", Q2, { dev: "d-win-web", x: "aff=gal" }), row("2026-11-14 20:30:00", "purchase", "a5v6", "s3", "", "cardcom | 297 ILS | deal 222 | src facebook", { cta: "cardcom_webhook", x: "aff=gal" }),
  row("2026-11-14 20:31:00", "buyer_survey", "a5v6", "s3", "", "", { cta: "q1", name: "other:הפודקאסט", x: "deal=222;aff=gal" }),
  row("2026-11-15 09:00:00", "purchase", "", "", "", "manual | 297 ILS | ref 777", { cta: "manual_bank_transfer" }),
  row("2026-11-13 19:24:00", "purchase", "a", "s9", "", "cardcom | 297 ILS | deal 999 | src ", { cta: "cardcom_webhook", x: "int=1" })];
 const EV = R.join("\n");
 const dash = async root => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 }); await c.clock.setFixedTime(new Date("2026-11-17T10:00:00+02:00")); const errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(root, "nlp/dashboard.html")) });
   if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\ngal\tגל\t\t1\t\t\n" }[a] || "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#snap"); await p.waitForTimeout(2500); return { p, errs } };
 const D2 = await dash(NEW), D1 = await dash(OLD);
 await D2.p.evaluate(() => setScreen("pr")); await D2.p.waitForTimeout(500);
 const T = await D2.p.evaluate(() => [...document.getElementById("prTable").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim()))); T.forEach(r => console.log(r.join(" | ")));
 ok("3 verified purchases (test deal excluded)", T.length === 4, T.length);
 const r1 = T.find(r => /12\.11/.test(r[0])), r2 = T.find(r => /14\.11/.test(r[0])), r3 = T.find(r => /15\.11/.test(r[0]));
 ok("12.11: pr2, Meta ads, lenatzeach_lab, car4_warm_a, mobile, android · fb app", r1 && r1[1] === "pr2" && r1[2] === "מודעות Meta" && r1[3] === "lenatzeach_lab" && r1[4] === "car4_warm_a" && r1[5] === "נייד" && /android/.test(r1[6]) && /פייסבוק/.test(r1[6]), r1 && r1.join("|"));
 ok("12.11: first visit 10.11 -> 2 visits, ~2 days", r1 && r1[8] === "2" && /ימים/.test(r1[7]), r1 && r1.slice(7, 9).join("|"));
 ok("12.11: answers - testimonials / other / 45-54", r1 && r1[10] === "ההמלצות בדף" && r1[11] === "אחר" && r1[12] === "45-54", r1 && r1.slice(10).join("|"));
 ok("14.11: no age answer -> dash", r2 && r2[12] === "-", r2 && r2.join("|"));
 ok("14.11: affiliate gal, desktop, 1 visit, under an hour, other text", r2 && /גל/.test(r2[9]) && r2[5] === "מחשב" && r2[8] === "1" && r2[7] === "פחות משעה" && r2[10] === "אחר: הפודקאסט" && r2[11] === "-", r2 && r2.join("|"));
 ok("15.11 bank transfer without visit: dashes", r3 && /העברה בנקאית/.test(r3[0]) && r3[2] === "-" && r3[8] === "-", r3 && r3.join("|"));
 const all = await D2.p.evaluate(() => document.getElementById("s-pr").innerText); ok("no deal numbers in the tab", !/111|222|777|999/.test(all), all.slice(0, 200));
 const A = await D2.p.evaluate(() => [...document.getElementById("prAns").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim()))); console.log(JSON.stringify(A));
 ok("answers summary: q1 2, q2 1, age 1 answered; 45-54 = 1", /2 ענו/.test(A[0][0]) && /1 ענו/.test(A[0][2]) && /טווח גיל \(1 ענו\)/.test(A[0][4]) && A.some(r => r[4] === "45-54" && /^1/.test(r[5])), A.map(r=>r.join("|")).join(" / "));
 ok("table header has age column", T[0][12] === "גיל", T[0].join("|"));
 ok("changelog ב106 first", /ב106/.test(await D2.p.evaluate(() => CHANGELOG[0][1])));
 ok("dashboard: no JS errors", !D2.errs.length, D2.errs.join("|"));
 const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
 for (const s of ["snap", "op", "co", "af", "fin", "up", "ws"]) ok("screen " + s + " unchanged", (await scr(D1, s)) === (await scr(D2, s)));
 if (SH) { await D2.p.evaluate(() => setScreen("pr")); await D2.p.waitForTimeout(400); await (await D2.p.$("#s-pr")).screenshot({ path: path.join(SH, "b106_dashboard_buyer_profile_testdata.png") }) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
