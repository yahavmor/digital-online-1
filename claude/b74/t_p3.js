// פ3 (20.11): נוסח ניטרלי באפסייל - הזרימה לא השתנתה. שימוש: node t_p3.js <root חדש> <root ישן>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 300))) };
const TOK = "AbCdEfGhIjKlMnOpQrStUvWxYz012345", API = "afnx34prmqo6zjf7b8zoqe7fvvy6q97b";
async function ctx(b, root, dev) { const c = await b.newContext(dev); const calls = [], errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : undefined }) : r.fulfill({ status: 404, body: "" }) }
  if (u.href.includes(API)) { const p = new URLSearchParams(r.request().postData() || ""); calls.push(p.get("action") + (p.get("agree") ? ":agree=" + p.get("agree") : ""));
   const a = p.get("action"); const body = a === "check" ? { state: "ok", name: "דנה", email: "d***@x.co" } : a === "create" ? { test: true, would_charge: 97 } : { ok: true }; return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) }) }
  if (u.hostname.endsWith("make.com")) return r.fulfill({ status: 200, body: "" });
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); return { c, p, calls, errs } }
const txt = p => p.evaluate(() => { document.querySelectorAll("details").forEach(d => d.open = true); return document.body.innerText.replace(/\s+/g, " ") });
const MASC = /אתה |אני ממשיך|שתמשיך|כשתמשיך|אני מצטרף|אני מוסיף|הוסף עכשיו/;
(async () => { const b = await chromium.launch();
 for (const [dn, dev] of [["mobile", devices["iPhone 13"]], ["desktop", { viewport: { width: 1280, height: 860 } }]]) {
  const N = await ctx(b, NEW, dev), O = await ctx(b, OLD, dev);
  for (const X of [N, O]) { await X.p.goto("https://local.test/nlp/upsell-97.html?t=" + TOK); await X.p.waitForTimeout(1500) }
  const tn = await txt(N.p);
  ok(dn + ": upsell-97 offer shown after check", N.calls.includes("check") && /97/.test(tn), N.calls);
  ok(dn + ": new wording in place", /הוסיפו לי את האוטומט החדש שלי/.test(tn) && /לא תודה, המשך לקורס/.test(tn) && /מבטיחים לעצמנו שמחר מתחילים/.test(tn), tn.slice(0, 200));
  const m = tn.match(MASC); ok(dn + ": no 2nd-person masculine left", !m, m && tn.slice(Math.max(0, m.index - 30), m.index + 30));
  ok(dn + ": same number of buttons and links as before", (await N.p.$$eval("a,button", a => a.length)) === (await O.p.$$eval("a,button", a => a.length)));
  ok(dn + ": no JS errors (upsell-97)", !N.errs.length, N.errs);
  const cta = X => X.p.evaluate(() => [...document.querySelectorAll("[data-ab]")].filter(e => /^cta/.test(e.dataset.ab)).map(e => { const a = e.closest("a,button"); return a ? a.tagName + ":" + (a.getAttribute("href") || a.id || a.className) : "-" }).join("|"));
  const href = await cta(N), hrefO = await cta(O);
  ok(dn + ": buy button goes to the same place as before", href && href === hrefO, [href, hrefO]);
  N.p.on("dialog", d => d.accept().catch(() => { })); const k0 = N.calls.length; await N.p.click('button[data-decline="hero"]').catch(() => { }); await N.p.waitForTimeout(500); await N.p.click("#confirmDecline").catch(() => { }); await N.p.waitForTimeout(1200);
  ok(dn + ": 'לא תודה, המשך לקורס' still sends decline", N.calls.slice(k0).some(x => x.startsWith("decline")), N.calls.slice(k0));
  await N.c.close(); await O.c.close();
  const C = await ctx(b, NEW, dev); await C.p.goto("https://local.test/nlp/checkout97.html?t=" + TOK); await C.p.waitForTimeout(1500);
  const tc = await txt(C.p);
  ok(dn + ": checkout97 new wording", /הוסיפו עכשיו את המאמן האישי הדיגיטלי שלכם ב-97 ₪ בלבד/.test(tc) && /אחרי היציאה מהדף הזה, ההצעה המיוחדת/.test(tc) && /לא תודה, המשך לקורס/.test(tc), tc.slice(0, 200));
  const mc = tc.match(MASC); ok(dn + ": checkout97 no 2nd-person masculine left", !mc, mc && tc.slice(Math.max(0, mc.index - 30), mc.index + 30));
  for (const cb of await C.p.$$('input[type="checkbox"]')) await cb.check({ force: true }).catch(() => { });
  await C.p.waitForTimeout(500); await C.p.click("#go").catch(() => { }); await C.p.waitForTimeout(1500);
  ok(dn + ": checkout97 calls create with agree=1 after both boxes", C.calls.some(x => x === "create:agree=1"), C.calls);
  ok(dn + ": no JS errors (checkout97)", !C.errs.length, C.errs); await C.c.close() }
 const diff = fs.readdirSync(path.join(NEW, "nlp")).filter(x => x.endsWith(".html") && !fs.readFileSync(path.join(NEW, "nlp", x)).equals(fs.readFileSync(path.join(OLD, "nlp", x))));
 ok("only upsell-97.html and checkout97.html changed", diff.sort().join(",") === "checkout97.html,upsell-97.html", diff);
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
