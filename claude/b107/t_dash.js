// ב107: "תנועה מיום ליום" ומקורות חינם בדשבורד. שימוש: node t_dash.js <new root> <old root> [shots]
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const row = (ts, ev, v, sid, vid, qs, o = {}) => { const a = Array(21).fill(""); a[0] = ts; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[13] = o.cta || ""; a[16] = vid; a[17] = "m-ios-fb"; a[20] = o.x || ""; return a.join("\t") };
const PAID = "utm_source=facebook&utm_medium=paid&utm_id=1&utm_content=p25", AFF = "utm_source=fb&utm_medium=affiliate&aff=gal&utm_content=p25_brain_c3";
const R = [
 row("2026-11-16 10:00:00", "view", "a", "s1", "v1", PAID),
 row("2026-11-17 09:00:00", "view", "a", "s2", "v2", PAID), row("2026-11-17 09:01:00", "checkout_view", "a", "s2", "v2", PAID), row("2026-11-17 09:02:00", "checkout_details", "a", "s2", "v2", PAID),
 row("2026-11-17 10:00:00", "view", "a5v7", "s3", "v3", PAID),
 row("2026-11-17 11:00:00", "view", "a", "s4", "v4", AFF, { x: "aff=gal" }),
 row("2026-11-17 12:00:00", "view", "a", "s5", "v5", "utm_source=whatsapp&utm_medium=group&utm_campaign=ben_groups"), row("2026-11-17 12:01:00", "checkout_view", "a", "s5", "v5", "utm_source=whatsapp&utm_medium=group"),
 row("2026-11-17 13:00:00", "view", "a", "s6", "v6", "utm_source=facebook&utm_medium=page_post"),
 row("2026-11-17 14:00:00", "view", "a", "s7", "v7", "utm_source=instagram&utm_medium=bio"),
 row("2026-11-17 14:30:00", "purchase", "a", "s2", "", "cardcom | 297 ILS | deal 555 | src facebook", { cta: "cardcom_webhook" }),
 row("2026-11-18 09:00:00", "view", "a", "s8", "v8", PAID)];
const EV = R.join("\n");
(async () => { const b = await chromium.launch();
 const dash = async root => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 }); await c.clock.setFixedTime(new Date("2026-11-18T15:00:00+02:00")); const errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(root, "nlp/dashboard.html")) });
   if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\ngal\tגל\t\t1\t\t\n" }[a] || "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#snap"); await p.waitForTimeout(2500); return { p, errs } };
 const D = await dash(NEW), O = await dash(OLD);
 const T = await D.p.evaluate(() => [...document.getElementById("d14T").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())));
 const F = await D.p.evaluate(() => [...document.getElementById("d14F").rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())));
 const L = await D.p.evaluate(() => document.getElementById("d14Line").innerText); console.log(L); T.slice(0, 4).forEach(r => console.log(r.join(" | "))); console.log(T[T.length - 1].join(" | ")); F.forEach(r => console.log(r.join(" | ")));
 ok("15 rows (14 days + avg) + header", T.length === 16, T.length);
 const y = T.find(r => /אתמול/.test(r[0]));
 ok("yesterday 17.11: ben 2, aff 1, free 3, total 6, checkout 2, details 1, buys 1", y && y.slice(1).join(",") === "2,1,3,6,2,1,1", y && y.join("|"));
 ok("today 18.11: ben 1", /^18\.11/.test(T[1][0]) && T[1][1] === "1", T[1].join("|"));
 ok("16.11: ben 1", T[3][0].startsWith("16.11") && T[3][1] === "1", T[3].join("|"));
 ok("avg 7 days: total (1+6)/7=1", /ממוצע/.test(T[15][0]) && T[15][4] === "1", T[15].join("|"));
 ok("line: yesterday 6 people (2/1/3), 2 checkout, 1 details, 1 buy", /6 אנשים נכנסו לדף \(2 מהמודעות של בן, 1 דרך משווקים, 3 בחינם\), 2 הגיעו לדף התשלום, 1 השאירו פרטים, 1 רכישות/.test(L), L);
 ok("line: vs day before (1 person) -> more", /שלשום:.*1 אנשים.*אתמול נכנסו יותר אנשים/.test(L.replace(/\n/g, " ")), L);
 const fr = k => F.find(r => r[0] === k);
 ok("free: whatsapp 1 yesterday, 1 reached checkout", fr("וואטסאפ (קבוצות)") && fr("וואטסאפ (קבוצות)")[1] === "1" && fr("וואטסאפ (קבוצות)")[4] === "1", JSON.stringify(F));
 ok("free: facebook page 1", fr("דף הפייסבוק") && fr("דף הפייסבוק")[1] === "1", JSON.stringify(F));
 ok("free: instagram organic 1", fr("אינסטגרם אורגני") && fr("אינסטגרם אורגני")[1] === "1", JSON.stringify(F));
 ok("no deal numbers on screen", !/555/.test(await D.p.evaluate(() => document.getElementById("d14").innerText)));
 ok("changelog ב107 first", /ב107/.test(await D.p.evaluate(() => CHANGELOG[0][1])));
 ok("no JS errors", !D.errs.length, D.errs.join("|"));
 const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
 const snapOld = await scr(O, "snap"), snapNew = (await scr(D, "snap")).replace(await D.p.evaluate(() => document.getElementById("d14").innerText), "");
 const ol = snapOld.split("\n").filter(Boolean), nl = snapNew.split("\n").filter(Boolean); ok("snap screen otherwise unchanged", ol.join("\n") === nl.join("\n"), JSON.stringify([ol.filter(x => !nl.includes(x)), nl.filter(x => !ol.includes(x))]).slice(0, 600));
 for (const s of ["op", "co", "fin", "up", "pr", "af"]) ok("screen " + s + " unchanged", (await scr(O, s)) === (await scr(D, s)));
 if (SH) { await D.p.evaluate(() => setScreen("snap")); await D.p.waitForTimeout(400); await (await D.p.$("#d14")).screenshot({ path: path.join(SH, "dash_daily14_testdata.png") }) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
