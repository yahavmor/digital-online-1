// מ53: aff_rami ו-aff_karlin בטופס ההוצאה, שמירה שולחת את המפתח, ושאר הלשוניות לא משתנות. שימוש: node t_m53.js <new root> <old root>
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const COLS = 21, row = (ts, ev, v, sid, vid, qs, x = "") => { const a = Array(COLS).fill(""); a[0] = ts; a[1] = ev; a[2] = v; a[3] = sid; a[8] = qs; a[16] = vid; a[20] = x; return a.join("\t") };
const R = [row("2026-11-18 16:30:00", "view", "a5s", "s1", "v1", "aff=rami&utm_source=fb&utm_medium=affiliate&utm_campaign=x&utm_content=ad1", "aff=rami"), row("2026-11-18 16:31:00", "checkout_view", "a5s", "s1", "v1", "aff=rami&utm_source=fb&utm_medium=affiliate", "aff=rami"),
 row("2026-11-17 10:00:00", "view", "a", "s2", "v2", "aff=shira&utm_source=fb&utm_medium=affiliate&utm_content=p25_brain_c2", "aff=shira")].join("\n");
(async () => { const b = await chromium.launch();
 const dash = async root => { const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 1400, height: 900 } }); await c.clock.setFixedTime(new Date("2026-11-18T17:00:00+02:00")); const errs = [], sent = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(path.join(root, "nlp/dashboard.html")) });
   if (u.hostname.endsWith("make.com")) { const a = u.searchParams.get("action"); if (a === "spend_set") sent.push(u.searchParams.get("creative")); return r.fulfill({ status: 200, body: { rows: R, spend: "spend\n", affiliates: "affiliates\tname\tpct\tactive\tfee\tbudget\nrami\tרמי\t0\ttrue\t220\t\nkarlin\tקרלין\t0\ttrue\t220\t\nshira\tשירה\t0\ttrue\t220\t40\n" }[a] || "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/dashboard.html#snap"); await p.waitForTimeout(2500); return { p, errs, sent } };
 const D = await dash(NEW), O = await dash(OLD);
 const ids = await D.p.evaluate(() => [...document.querySelectorAll(".screen")].map(s => s.id.slice(2)));
 for (const s of ids) { await D.p.evaluate(s => setScreen(s), s); await D.p.waitForTimeout(250) }
 const audId = await D.p.evaluate(() => { const f = document.getElementById("audSpendForm"); return f ? f.closest(".screen").id.slice(2) : null });
 await D.p.evaluate(s => setScreen(s), audId); await D.p.waitForTimeout(500);
 const opts = await D.p.$$eval("#audSpCamp option", o => o.map(x => x.value)); console.log(opts.join(", "));
 ok("spend form lists aff_rami and aff_karlin", opts.includes("aff_rami") && opts.includes("aff_karlin"), opts.join(","));
 const txt = await D.p.evaluate(s => document.getElementById("s-" + s).innerText, audId); ok("tab 10 shows רמי and קרלין", /רמי/.test(txt) && /קרלין/.test(txt));
 ok("dashboard: no JS errors on any tab", !D.errs.length, D.errs.join("|"));
 const scr = async (X, s) => { await X.p.evaluate(s => setScreen(s), s); await X.p.waitForTimeout(250); return X.p.evaluate(s => document.getElementById("s-" + s).innerText.replace(/עודכן \d\d:\d\d/g, ""), s) };
 for (const s of ids.filter(s => s !== audId && s !== "ex" && s !== "fin" && s !== "af")) { const o = (await scr(O, s)).split("\n"), w = (await scr(D, s)).split("\n"); ok("screen " + s + " unchanged", o.join("\n") === w.join("\n"), JSON.stringify([o.filter(x => !w.includes(x)).slice(0, 4), w.filter(x => !o.includes(x)).slice(0, 4)]).slice(0, 500)) }
 await D.p.evaluate(s => setScreen(s), audId); await D.p.waitForTimeout(300);
 await D.p.selectOption("#audSpCamp", "aff_rami"); await D.p.fill("#audSpAmt", "12"); await D.p.click("#audSpSave"); await D.p.waitForTimeout(500);
 ok("save sends creative=aff_rami", D.sent.includes("aff_rami"), JSON.stringify(D.sent));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
