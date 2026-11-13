// ב90: טבלת B מול B2 בדשבורד (לשונית הסליקה). נתונים מדומים, Make מדומה.
// שימוש: node t_co90.js <dashboard לפני> <dashboard אחרי>
process.env.TZ = "Asia/Jerusalem";
const { chromium } = require("playwright"), fs = require("fs");
const [O, P] = process.argv.slice(2).map(f => fs.readFileSync(f, "utf8"));
const row = (t, ev, v, sid, vid, x, extra) => { const a = Array(21).fill(""); a[0] = "2026-11-14 " + t; a[1] = ev; a[2] = v; a[3] = sid; a[16] = vid; a[17] = "m-ios-fb"; a[20] = x || ""; a[8] = "utm_source=fb&utm_medium=paid"; Object.assign(a, extra || {}); return a.join("\t"); };
const X = (co, more) => "co=" + co + ";cx=co_b2_1311" + (more ? ";" + more : "");
const R = [];
const sess = (t, v, sid, vid, co, evs, more) => evs.forEach((e, i) => R.push(row(t.replace(/:(\d\d)$/, (m, s) => ":" + String(+s + i).padStart(2, "0")), e, v, sid, vid, X(co, more))));
// a5v6 · B: 3 אנשים - רק הגיע / התחיל / הגיע לטופס וקנה
sess("10:00:00", "a5v6", "s1", "v1", "b", ["checkout_view"]);
sess("10:01:00", "a5v6", "s2", "v2", "b", ["checkout_view", "checkout_contact_started"]);
sess("10:02:00", "a5v6", "s3", "v3", "b", ["checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"]);
// a5v6 · B2: 2 אנשים, אחד מהם בשני ביקורים (נספר פעם אחת)
sess("10:03:00", "a5v6", "s4", "v4", "b2", ["checkout_view", "checkout_contact_started"]);
sess("10:04:00", "a5v6", "s5", "v4", "b2", ["checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"]);
sess("10:05:00", "a5v6", "s6", "v6", "b2", ["checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"]);
// pr2 · B: אחד; pr2 · B2: שניים, אחד קנה
sess("10:06:00", "pr2", "s7", "v7", "b", ["checkout_view"]);
sess("10:07:00", "pr2", "s8", "v8", "b2", ["checkout_view"]);
sess("10:08:00", "pr2", "s9", "v9", "b2", ["checkout_view", "checkout_contact_started", "checkout_details", "checkout_payment_viewed"]);
// לא נספרים: ניסוי ישן (co_b_0811), ובדיקה פנימית (int=1)
R.push(row("10:09:00", "checkout_view", "a5v6", "s10", "v10", "co=b;cx=co_b_0811"));
R.push(row("10:10:00", "checkout_view", "a5v6", "s11", "v11", X("b2", "int=1")));
// רכישות מאומתות: s3 (a5v6 B), s9 (pr2 B2)
const buy = (t, v, sid, deal) => R.push(row(t, "purchase", v, sid, "", "", { 8: "cardcom | 297 ILS | deal " + deal + " | src ", 13: "cardcom_webhook", 17: "" }));
buy("10:20:00", "a5v6", "s3", "990000001"); buy("10:21:00", "pr2", "s9", "990000002");
const EV = R.join("\n");
const AFF = "affiliates\tname\tpct\tactive\tfee\tbudget\n";
let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i || "") } else console.log("PASS", m) };
(async () => {
  const b = await chromium.launch();
  const run = async html => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem" }); await c.clock.setFixedTime(new Date("2026-11-14T12:00:00+02:00")); const errs = [];
    await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: html });
      if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: EV, spend: "spend\n", affiliates: AFF, refunds: "refunds\n", paid: "paid\tat\taff\n", ads: "ads\n" }[a] || "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#co"); await p.waitForTimeout(3000); return { c, p, errs } };
  const A = await run(O), B = await run(P);
  const tab = await B.p.evaluate(() => { const t = document.getElementById("co90"); return t ? [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, " ").trim())) : null });
  console.log(JSON.stringify(tab));
  ok("table exists with header + 4 rows", tab && tab.length === 5, tab && tab.length);
  const H = tab[0], col = l => H.indexOf(l), cell = (r, l) => (tab[r][col(l)] || "").split(" ")[0];
  ok("columns: a5v6/pr2/all × B/B2", ["a5v6 · B", "a5v6 · B2", "pr2 · B", "pr2 · B2", "כל הדפים · B", "כל הדפים · B2"].every(l => col(l) > 0), H.join("|"));
  const exp = { "a5v6 · B": [3, 2, 1, 1], "a5v6 · B2": [2, 2, 2, 0], "pr2 · B": [1, 0, 0, 0], "pr2 · B2": [2, 1, 1, 1], "כל הדפים · B": [4, 2, 1, 1], "כל הדפים · B2": [4, 3, 3, 1] };
  for (const l in exp) ok("counts " + l + " = " + exp[l], exp[l].every((v, i) => +cell(i + 1, l) === v), [1, 2, 3, 4].map(i => cell(i, l)).join(","));
  ok("percent of reached: a5v6 B2 started 100%", /100%/.test(tab[2][col("a5v6 · B2")]), tab[2][col("a5v6 · B2")]);
  const note = await B.p.evaluate(() => document.getElementById("co90N").innerText);
  ok("note: early + progress B 4, B2 4 of 100", /ראשוני/.test(note) && /B 4, B2 4/.test(note) && /100/.test(note), note);
  const cl = await B.p.evaluate(() => CHANGELOG[0][1]); ok("changelog line ב90", /ב90/.test(cl) && /co_b2_1311/.test(cl), cl.slice(0, 80));
  // שאר מסך הסליקה ושאר הלשוניות לא השתנו
  const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => { const e = document.getElementById("s-" + s).cloneNode(true); e.querySelectorAll("#co90,#co90N").forEach(x => { const pn = x.closest(".panel"); if (pn) pn.remove() }); return e.innerText.replace(/עודכן \d\d:\d\d/g, "") }, s) };
  { const a = (await scr(A, "co")).split("\n"), b2 = (await scr(B, "co")).split("\n"); const d = b2.filter(l => !a.includes(l)).concat(a.filter(l => !b2.includes(l)).map(l => "-" + l)); if (d.length) console.log("DIFF", JSON.stringify(d.slice(0, 8))); ok("checkout screen otherwise unchanged", !d.length); }
  for (const s of ["snap", "ov", "lp", "af", "fin"]) ok("screen " + s + " unchanged", (await scr(A, s)) === (await scr(B, s)));
  ok("no JS errors", !B.errs.length, B.errs.join("|"));
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0)
})();
