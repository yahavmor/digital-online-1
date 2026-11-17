// ב101: בדיקת הנוסח "בתוקף עד" בדף האפסייל ובדף התשלום. שימוש: node t_until.js <new root> <old root> [shots dir]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const TOK = "a".repeat(32);
(async () => { const b = await chromium.launch();
 const open = async (root, file, q, state = "ok", mobile = false) => { const c = await b.newContext(mobile ? { ...devices["iPhone SE"], deviceScaleFactor: 2 } : { viewport: { width: 1280, height: 900 } }); const errs = [], nav = [];
  await c.route("**/*", r => { const u = r.request().url();
   if (u.startsWith("https://local.test/")) { const fp = path.join(root, new URL(u).pathname); if (/checkout97/.test(u) && file !== "checkout97.html") nav.push(u);
    return fs.existsSync(fp) ? r.fulfill({ status: 200, contentType: /\.html$/.test(fp) ? "text/html; charset=utf-8" : undefined, body: fs.readFileSync(fp) }) : r.fulfill({ status: 404, body: "" }) }
   if (/make\.com/.test(u)) return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ state, name: "", email: "t***@example.com" }) });
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/" + file + q); await p.waitForTimeout(1200); return { c, p, errs, nav } };
 const txt = p => p.evaluate(() => document.body.innerText);
 // 1. בלי until - הדף זהה לגרסה של היום (רוכש חדש)
 for (const [file, st] of [["upsell-97.html", "ok"], ["upsell-97.html", "expired"], ["checkout97.html", "ok"], ["checkout97.html", "expired"]]) {
  const A = await open(NEW, file, "?t=" + TOK, st), B = await open(OLD, file, "?t=" + TOK, st);
  ok(file + " (" + st + ") without until: identical to today", (await txt(A.p)) === (await txt(B.p))); ok(file + " (" + st + ") no JS errors", !A.errs.length, A.errs.join("|")); await A.c.close(); await B.c.close() }
 // 2. עם until - "בתוקף עד 24.11", בלי "רק במסך הזה" ובלי "כשתמשיך מהדף הזה"
 { const A = await open(NEW, "upsell-97.html", "?t=" + TOK + "&until=2026-11-24", "ok", true); const t = await txt(A.p);
  const mt = await A.p.evaluate(() => document.querySelector('[data-copy="modal"]').innerText);
  ok("upsell with until: 'בתוקף עד 24.11' shown", /בתוקף עד 24\.11/.test(t), t.slice(0, 200));
  ok("upsell with until: no 'רק במסך הזה' / 'כשתמשיך מהדף הזה'", !/רק במסך הזה|כשתמשיך מהדף הזה/.test(t + mt), (t + mt).match(/.{0,30}(רק במסך הזה|כשתמשיך מהדף הזה).{0,30}/));
  ok("upsell with until: decline modal says 'אם תוותר עכשיו'", /אם תוותר עכשיו, ההצעה הזו לא תחזור/.test(mt), mt);
  ok("upsell with until: no JS errors", !A.errs.length, A.errs.join("|"));
  if (SH) { const el = await A.p.$('[data-copy="urgent"]'); await el.scrollIntoViewIfNeeded(); await A.p.waitForTimeout(300); await A.p.screenshot({ path: path.join(SH, "until_upsell_offer_375.png") }) }
  await A.p.evaluate(() => { const x = document.querySelector('[data-buy]'); x && x.click() }); await A.p.waitForTimeout(1500);
  ok("buy keeps until=2026-11-24 to checkout97", A.nav.some(u => /until=2026-11-24/.test(u)) || /until=2026-11-24/.test(A.p.url()), JSON.stringify(A.nav) + " " + A.p.url()); await A.c.close() }
 { const A = await open(NEW, "checkout97.html", "?t=" + TOK + "&until=2026-11-24", "ok", true); const u = await A.p.evaluate(() => document.getElementById("urg").textContent);
  ok("checkout97 with until: urgency line 'בתוקף עד 24.11'", /בתוקף עד 24\.11/.test(u) && !/לאחר שתמשיך מהדף הזה/.test(u), u);
  if (SH) await A.p.screenshot({ path: path.join(SH, "until_checkout97_375.png") }); await A.c.close() }
 { const A = await open(NEW, "checkout97.html", "?t=" + TOK + "&until=2026-11-24", "expired"); const t = await A.p.evaluate(() => document.getElementById("stExpired").innerText);
  ok("checkout97 expired with until: no 'מיד אחרי רכישת הקורס'", !/מיד אחרי רכישת הקורס/.test(t) && /כבר לא בתוקף/.test(t), t); await A.c.close() }
 { const A = await open(NEW, "upsell-97.html", "?t=" + TOK + "&until=2026-11-24", "expired"); const t = await txt(A.p);
  ok("upsell expired with until: 'ההצעה כבר לא זמינה'", /ההצעה כבר לא זמינה/.test(t) && !/במסך הזה/.test(t), t.slice(0, 150)); await A.c.close() }
 // 3. until לא תקין - מתעלמים (נוסח רגיל)
 { const A = await open(NEW, "upsell-97.html", "?t=" + TOK + "&until=%3Cscript%3E", "ok"), B = await open(OLD, "upsell-97.html", "?t=" + TOK, "ok");
  ok("invalid until ignored (same as today)", (await txt(A.p)) === (await txt(B.p))); await A.c.close(); await B.c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
