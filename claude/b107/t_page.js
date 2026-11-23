// ב107: דף הבדיקה הקצר a5s מול a5v7. שימוש: node t_page.js <root with nlp/a5s.html + nlp/a5v7.html> [shots]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".css": "text/css", ".js": "text/javascript", ".mp4": "video/mp4" };
(async () => { const b = await chromium.launch();
 const open = async (pg, mobile) => { const c = await b.newContext(mobile ? { ...devices["iPhone SE"], deviceScaleFactor: 2 } : { viewport: { width: 1366, height: 860 } }); const ev = [], errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { ev.push(Object.fromEntries(new URLSearchParams(r.request().postData() || u.search))); return r.fulfill({ status: 200, body: "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/" + pg + ".html?utm_source=claude_test"); await p.waitForTimeout(1500); return { c, p, ev, errs } };
 const text = p => p.evaluate(() => document.body.innerText.replace(/\s+/g, " "));
 for (const mobile of [true, false]) { const tag = mobile ? "mobile" : "desktop";
  const S = await open("a5s", mobile), V = await open("a5v7", mobile);
  const top = (p, sel) => p.evaluate(sel => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null }, sel);
  const oS = await top(S.p, "#offer"), oV = await top(V.p, "#offer"), H = mobile ? 667 : 860;
  ok(tag + ": offer right after hero (a5s " + oS + "px vs a5v7 " + oV + "px)", oS !== null && oS < oV / 3, [oS, oV]);
  const hS = await S.p.evaluate(() => document.documentElement.scrollHeight), hV = await V.p.evaluate(() => document.documentElement.scrollHeight);
  ok(tag + ": page shorter when folded (" + hS + " vs " + hV + ")", hS < hV * 0.6, [hS, hV]);
  ok(tag + ": hero identical to a5v7", await S.p.evaluate(() => document.querySelector("header.hero9").innerText) === await V.p.evaluate(() => document.querySelector("header.hero9").innerText));
  ok(tag + ": 12 folds, all closed", (await S.p.$$eval("details.fold", d => d.length + ":" + d.filter(x => x.open).length)) === "12:0");
  if (!mobile) {
   const before = S.ev.length; await S.p.click('details.fold[data-fold="מה יש בפנים"] > summary'); await S.p.waitForTimeout(400); await S.p.click('details.fold[data-fold="מה יש בפנים"] > summary'); await S.p.click('details.fold[data-fold="מה יש בפנים"] > summary'); await S.p.waitForTimeout(400);
   const fo = S.ev.slice(before).filter(e => e.ev === "fold_open"); ok("fold_open sent once with name", fo.length === 1 && fo[0].name === "מה יש בפנים" && fo[0].variant === "a5s", JSON.stringify(fo));
   // אותו טקסט - שום מילה חדשה (חוץ מכפתורי הביניים שיצאו)
   const words = t => new Set(t.split(" ")); await S.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = true)); await V.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = true));
   const wS = words(await text(S.p)), wV = words(await text(V.p)); const extra = [...wS].filter(w => !wV.has(w));
   ok("no new words vs a5v7 (all folds open)", extra.length === 0, extra.slice(0, 20).join(" "));
   await S.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = false));
   ok("variant a5s in events", S.ev.some(e => e.ev === "view" && e.variant === "a5s"), JSON.stringify(S.ev.slice(0, 2)));
   const hrefs = async p => p.$$eval("a[data-checkout]", a => [...new Set(a.map(x => x.getAttribute("href").replace(/(utm_content=lp_|v=)a5(s|v7)/g, "$1X").replace(/sid=[^&]+/, "sid=X")))].join("|"));
   ok("checkout links same as a5v7", (await hrefs(S.p)) === (await hrefs(V.p)), [await hrefs(S.p), await hrefs(V.p)]);
   ok("noindex", await S.p.evaluate(() => /noindex/.test(document.querySelector('meta[name=robots]').content)));
  }
  ok(tag + ": no JS errors", !S.errs.length, S.errs.join("|"));
  if (SH) { await S.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = false)); await S.p.evaluate(() => scrollTo(0, 0)); await S.p.waitForTimeout(300);
   await S.p.screenshot({ path: path.join(SH, "a5s_" + tag + "_first.png") });
   await S.p.screenshot({ path: path.join(SH, "a5s_" + tag + "_full.png"), fullPage: true });
   if (mobile) { await S.p.click('details.fold[data-fold="מה יש בפנים"] > summary'); await S.p.waitForTimeout(500); const el = await S.p.$('details.fold[data-fold="מה יש בפנים"]'); await el.screenshot({ path: path.join(SH, "a5s_mobile_fold_open.png") }) } }
  await S.c.close(); await V.c.close() }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
