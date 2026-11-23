// ב103: בדיקת הלוח - שירה, טבלת סך הכול, נשארו דקה ומעלה, מחוץ לניסוי. שימוש: node t_b103.js <new dashboard> <old dashboard> [shots dir]
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const row = (t, ev, v, sid, vid, qs, sec, x) => { const a = Array(21).fill(""); a[0] = "2026-11-16 " + t; a[1] = ev; a[2] = v; a[3] = sid; a[4] = sec || ""; a[16] = vid; a[17] = "m-ios-fb"; a[8] = qs; a[20] = x || ""; return a.join("\t") };
const Q = "utm_source=fb&utm_medium=paid&utm_id=1&exp=on_1611&go=1", QS = "utm_source=fb&utm_medium=affiliate&aff=shira&utm_content=p25_brain_c2&exp=on_1611&go=1", QY = "utm_source=fb&utm_medium=affiliate&aff=yosef&utm_content=p25_yosef";
const R = []; const sess = (t, v, sid, vid, evs, qs, sec, x) => evs.forEach((e, i) => R.push(row(t.replace(/:(\d\d)$/, (m, s) => ":" + String(+s + i).padStart(2, "0")), e, v, sid, vid, qs || Q, sec, x)));
sess("20:30:00", "a", "s1", "v1", ["view", "leave"], Q, 30); sess("20:31:00", "a", "s2", "v2", ["view", "checkout_view", "checkout_contact_started", "checkout_details", "leave"], Q, 90); sess("20:32:00", "a", "s3", "v3", ["view", "checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"], Q, 70);
sess("20:33:00", "a5v6", "s4", "v4", ["view"], Q, 10); sess("20:34:00", "a5v6", "s5", "v4", ["view", "checkout_view"], Q, 61); sess("20:35:00", "a5v6", "s6", "v6", ["view", "checkout_view", "checkout_contact_started"], Q, 40);
sess("20:36:00", "a5v6", "s7", "v7", ["view", "checkout_view", "checkout_contact_started", "checkout_details"], QS, 65, "aff=shira;");
sess("20:37:00", "a", "s8", "v8", ["view", "leave"], QY, 80, "aff=yosef;"); sess("20:38:00", "a5v6", "s9", "v9", ["view"], QY, 5, "aff=yosef;");
sess("20:39:00", "a", "s10", "v10", ["view"], "utm_source=ig&route=ig_org&go=1", 20); // אינסטגרם אורגני - לא מחוץ לניסוי
sess("14:00:00", "a", "s11", "v11", ["view"], QY, 20, "aff=yosef;"); // לפני תחילת הניסוי - לא נספר
const EV = R.join("\n");
(async () => { const b = await chromium.launch();
  const dash = async file => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 }); await c.clock.setFixedTime(new Date("2026-11-16T22:00:00+02:00")); const errs = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(file) });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\nshira\tשירה\t\t1\t\t\nyosef\tיוסף\t\t1\t\t\n", refunds: "refunds\n", paid: "paid\tat\taff\n", ads: "ads\n", upsell: "upsell\n" }[a] || "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#op"); await p.waitForTimeout(3000); return { p, errs } };
  const D2 = await dash(NEW), D1 = await dash(OLD);
  const tb = id => D2.p.evaluate(id => { const t = document.getElementById(id); return t ? [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())) : null }, id);
  const t1 = await tb("onT"), t2 = await tb("onT2"), t3 = await tb("onT3"); [t1, t2, t3].forEach(t => console.log(JSON.stringify(t)));
  const cell = (t, r, c) => +((t[r] || [])[c] || "").split(" ")[0], lab = (t, r) => (t[r] || [])[0];
  ok("row 2 is 'נשארו דקה ומעלה' in all 3 tables", [t1, t2, t3].every(t => t && lab(t, 2) === "נשארו דקה ומעלה"), t1 && lab(t1, 2));
  ok("Ben: people 3/2, minute+ 2/1 (v4 max 61s)", cell(t1, 1, 1) === 3 && cell(t1, 1, 2) === 2 && cell(t1, 2, 1) === 2 && cell(t1, 2, 2) === 1, t1 && t1.slice(1, 3).join(" / "));
  ok("Ben: details (primary) 2/0 unchanged", lab(t1, 5) === "השאירו פרטים (מדד ראשי)" && cell(t1, 5, 1) === 2 && cell(t1, 5, 2) === 0, t1 && t1[5]);
  ok("affiliates: Shira 0/1, minute+ 0/1, Yosef direct not counted", cell(t2, 1, 1) === 0 && cell(t2, 1, 2) === 1 && cell(t2, 2, 2) === 1, t2 && t2.slice(1, 3).join(" / "));
  ok("total: people 3/3, minute+ 2/2, details 2/1", /סך הכול/.test(t3[0][0]) && cell(t3, 1, 1) === 3 && cell(t3, 1, 2) === 3 && cell(t3, 2, 1) === 2 && cell(t3, 2, 2) === 2 && cell(t3, 5, 1) === 2 && cell(t3, 5, 2) === 1, t3 && t3.map(r => r.join("|")).join(" / "));
  const out = await D2.p.evaluate(() => document.getElementById("onOut").textContent); console.log(out);
  ok("out of experiment: Yosef 1 on a + 1 on a5v6, no ig_org, nothing before start", /מחוץ לניסוי/.test(out) && /משווק יוסף \(דף a\): 1/.test(out) && /משווק יוסף \(דף a5v6\): 1/.test(out) && !/ig_org|אינסטגרם/.test(out), out);
  const note = await D2.p.evaluate(() => document.getElementById("onN").textContent); ok("stop rule unchanged (3 / 2 of 150)", /150/.test(note) && /3 \/ 2/.test(note), note);
  const aud = await D2.p.evaluate(() => { setScreen("aud"); return new Promise(r => setTimeout(() => r(document.getElementById("s-aud").innerText), 600)) });
  ok("audiences tab lists שירה with p25_brain_c2 and 40", /שירה/.test(aud) && /p25_brain_c2/.test(aud), aud.slice(0, 300));
  const spk = await D2.p.evaluate(() => AUD.seg.filter(g => /shira/.test(g.spk || g.key || "")).map(g => g.spk || g.key)); ok("spend key aff_shira", spk.includes("aff_shira"), JSON.stringify(spk));
  const cl = await D2.p.evaluate(() => CHANGELOG[0][1]); ok("changelog ב103 first", /ב103/.test(cl), cl.slice(0, 60));
  ok("dashboard: no JS errors", !D2.errs.length, D2.errs.join("|"));
  const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
  for (const s of ["snap", "co", "fin", "up", "ov"]) ok("screen " + s + " unchanged", (await scr(D1, s)) === (await scr(D2, s)));
  if (SH) { await D2.p.evaluate(() => setScreen("op")); await D2.p.waitForTimeout(400); const el = await D2.p.$("#onT"); const pn = await el.evaluateHandle(e => e.closest(".panel")); await pn.screenshot({ path: path.join(SH, "on_1611_table.png") }) }
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
