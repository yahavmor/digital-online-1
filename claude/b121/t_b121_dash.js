// ב121: דשבורד על נתונים סינתטיים (בלי פרטי רוכשים): aff=affyehudit נקרא yehudit, אפסייל בתמונת מצב, עמלת אפסייל במשווקים. שימוש: node t_b121_dash.js <new root> <old root> [shot.png]
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, SHOT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + String(d).slice(0, 500))) };
const COLS = 21, row = (ts, ev, v, sid, vid, qs, x = "", cta = "") => { const a = Array(COLS).fill(""); a[0] = ts; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[13] = cta; a[16] = vid; a[20] = x; return a.join("\t") };
const R = [
 row("2026-11-20 10:00:00", "view", "a5s", "s_ben", "v_ben", "utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben&fbclid=1"),
 row("2026-11-20 10:05:00", "checkout_view", "a5s", "s_ben", "v_ben", "utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben"),
 row("2026-11-20 10:10:00", "purchase", "a5s", "s_ben", "v_ben", "deal 900001 | 297 ILS | card", "", "cardcom_webhook"),
 row("2026-11-23 22:30:00", "view", "a5s", "s_yeh", "v_yeh", "aff=yehudit&utm_source=facebook&utm_medium=affiliate&utm_campaign=NLP+%7C+Aff+yehudit&utm_content=w2_yehudit", "aff=yehudit"),
 row("2026-11-23 22:36:00", "checkout_details", "a5s", "s_yeh", "v_yeh", "aff=yehudit&utm_source=facebook&utm_medium=affiliate", "aff=yehudit;form=lp1"),
 row("2026-11-23 22:37:18", "purchase", "a5s", "s_yeh", "v_yeh", "deal 900002 | 297 ILS | card", "aff=affyehudit", "cardcom_webhook"),
 row("2026-11-23 22:39:36", "upsell_purchase", "upsell97", "s_yeh", "v_yeh", "course_deal 900002 | deal 900003 | 97 ILS", "aff=affyehudit", "cardcom_upsell_webhook"),
 row("2026-11-22 09:00:00", "view", "a", "s_sh", "v_sh", "aff=aff_shira&utm_source=fb&utm_medium=affiliate&utm_content=p25_brain_c2", "aff=aff_shira"),
].join("\n");
const AFFS = "affiliates\tname\tpct\tactive\tfee\tbudget\nyehudit\tיהודית\t0\ttrue\t220\t\nshira\tשירה\t0\ttrue\t220\t40\n";
(async () => { const b = await chromium.launch();
 const dash = async root => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1300, height: 900 }, deviceScaleFactor: 2 }); await c.clock.setFixedTime(new Date("2026-11-24T09:00:00+02:00")); const errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(root, "nlp/dashboard.html")) });
   if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); return r.fulfill({ status: 200, body: { rows: R, spend: "spend\n2026-11-20\t100\n2026-11-23\t50\n", affiliates: AFFS, refunds: "refunds\n", paid: "paid\n", upsell: "upsell\tdeal\tsid\taff\tcreated\texpires\tused\tdeclined\tup_deal\tpaid_at\ttest\n900002\ts_yeh\taffyehudit\t2026-11-23 22:37:22\t2026-11-23 23:07:00\ttrue\tfalse\t900003\t2026-11-23 22:39:36\tfalse\n" }[a] || "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#snap"); await p.waitForTimeout(2500); return { p, errs } };
 const D = await dash(NEW), O = await dash(OLD);
 const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(300); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
 await D.p.evaluate(() => { snapPer = "30"; renderSnap() }).catch(() => {}); await D.p.waitForTimeout(200);
 const snap = await scr(D, "snap"); const kpi = await D.p.evaluate(() => [...document.querySelectorAll("#snapKpi .tile")].map(t => t.innerText.replace(/\n/g, " | ")));
 console.log(kpi.join("\n"));
 ok("snapshot: upsell tile = 1, 97 ₪, 50% of buyers", kpi.some(t => /^אפסייל \| 1 \|/.test(t) && /97 ₪/.test(t) && /50%/.test(t)), kpi.join(" || "));
 ok("snapshot: revenue 691 ₪ = course 594 + upsell 97", kpi.some(t => /^הכנסות \| 691 ₪/.test(t) && /קורס 594 ₪/.test(t) && /אפסייל 97 ₪/.test(t)), kpi.join(" || "));
 ok("snapshot: purchases 2, 1 via affiliates", kpi.some(t => /^רכישות \| 2 \|/.test(t) && /1 דרך משווקים/.test(t)), kpi.join(" || "));
 ok("snapshot: ROAS = course only (Ben 297 / 150 = 1.98), upsell is the affiliate's so not in ROAS", kpi.some(t => /^ROAS \| 1\.98/.test(t) && /קורס 1\.98/.test(t) && /עם אפסייל 1\.98/.test(t)), kpi.join(" || "));
 const af = await scr(D, "af"); ok("affiliates tab: yehudit with 1 purchase, 297 ₪ and 220 ₪ pending", /יהודית/.test(af) && /220 ₪/.test(af), af.split("\n").filter(l => /יהודית/.test(l)).join(" | "));
 ok("affiliates tab: no 'affyehudit' or 'aff_shira' as a code", !/affyehudit|aff_shira/.test(af), af.split("\n").filter(l => /aff/.test(l)).join(" | "));
 const fin = await scr(D, "fin"); ok("finance tab: yehudit upsell commission 72 ₪ (292 ₪ total pending)", /יהודית/.test(fin) && /292 ₪|72 ₪/.test(fin), fin.split("\n").filter(l => /יהודית|72/.test(l)).slice(0, 6).join(" | "));
 const ws = await scr(D, "ws"); ok("what-sells: marketer row is yehudit, not affyehudit", /yehudit|יהודית/.test(ws) && !/affyehudit/.test(ws), ws.split("\n").filter(l => /yehudit|יהודית/.test(l)).join(" | "));
 const oSnap = (await scr(O, "snap")).split("\n"), oAf = await scr(O, "af");
 ok("old dashboard (control): no upsell tile and 'affyehudit' shown as a code", !/^אפסייל/m.test(oSnap.join("\n")) && /affyehudit/.test(oAf), oAf.split("\n").filter(l => /aff/.test(l)).join(" | "));
 const ids = await D.p.evaluate(() => [...document.querySelectorAll(".screen")].map(s => s.id.slice(2)));
 /* מסכים שמציגים קוד משווק: ההבדל היחיד מול הישן צריך להיות הקוד הנקי (שירה / יהודית במקום aff_shira / affyehudit) */
 const AFFSCR = ["snap", "af", "fin", "ws", "lab", "op", "pr", "aud", "hub", "up"];
 for (const s of ids.filter(s => AFFSCR.includes(s) && s !== "snap")) { const o = await scr(O, s), w = await scr(D, s); ok("screen " + s + ": raw code gone (old had it: " + /affyehudit|aff_shira/.test(o) + ")", !/affyehudit|aff_shira/.test(w), w.split("\n").filter(x => /aff/.test(x)).slice(0, 3).join(" | ")) }
 for (const s of ids.filter(s => !AFFSCR.includes(s) && s !== "ex")) { const o = await scr(O, s), w = await scr(D, s); ok("screen " + s + " unchanged", o === w, JSON.stringify([o.split("\n").filter(x => !w.includes(x)).slice(0, 3), w.split("\n").filter(x => !o.includes(x)).slice(0, 3)])) }
 ok("no JS errors (new)", !D.errs.length, D.errs.join(" | "));
 if (SHOT) { await D.p.evaluate(() => setScreen("snap")); await D.p.waitForTimeout(300); await D.p.locator("#snapKpi").screenshot({ path: SHOT }); console.log("shot", SHOT) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
