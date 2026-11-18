// ב109: a5s.html - הפסקה של בן וקיפולי ההוכחות. שימוש: node t_b109.js <new root> <old root (main)> [placeholder]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD, PH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp" };
const BEN = PH ? null : fs.readFileSync(path.join(__dirname, "ben_paragraph.txt"), "utf8").replace(/\r/g, "").split("\n").map(l => l.trim()).filter(Boolean).map(l => l.replace(/\s*[—–]\s*/g, " - "));
(async () => { const b = await chromium.launch();
 const open = async (root, mobile) => { const c = await b.newContext(mobile ? { ...devices["iPhone 13"] } : { viewport: { width: 1366, height: 860 } }); const ev = [], errs = [];
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { const d = r.request().postData(); if (d) ev.push(Object.fromEntries(new URLSearchParams(d))); return r.fulfill({ status: 200, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/a5s.html?utm_source=claude_test"); await p.waitForTimeout(1500); return { c, p, ev, errs } };
 for (const mobile of [true, false]) { const tag = mobile ? "mobile" : "desktop"; const N = await open(NEW, mobile), O = await open(OLD, mobile);
  const order = await N.p.evaluate(() => [...document.querySelectorAll("header.hero9, section, .sp-stories, .proofbar")].map(e => e.matches("header") ? "hero" : e.id === "offer" ? "offer" : e.classList.contains("bennote") ? "ben" : e.classList.contains("guar") ? "guar" : e.classList.contains("sp-stories") ? "stories" : e.classList.contains("proofbar") ? "proofbar" : (e.querySelector("details.fold") || {}).dataset ? e.querySelector("details.fold").dataset.fold : e.className.split(" ")[0]).slice(0, 9));
  ok(tag + ": order hero, ben, offer, guar, stories, proofbar, video, whatsapp, 'רגע לפני'", order.join(",") === "hero,ben,offer,guar,stories,proofbar,תוצאות אמיתיות,מה אומרים,רגע לפני", order.join(","));
  const t = await N.p.evaluate(() => [...document.querySelectorAll("details.fold.hot > summary")].map(s => s.innerText.trim()));
  ok(tag + ": hot fold titles exactly", t[0] === "מה אנשים שעברו את התהליך שלנו מספרים" && t[1] === "אנשים מספרים בתוך הקהילה הפרטית שלנו", t.join(" | "));
  const inner = (X, name) => X.p.evaluate(nm => { const d = document.querySelector('details.fold[data-fold="' + nm + '"]'); return d.querySelector(".fold-b").innerText.replace(/\s+/g, " ").trim() }, name);
  const oh = (X, name) => X.p.evaluate(nm => document.querySelector('details.fold[data-fold="' + nm + '"] > summary').innerText.replace(/\s+/g, " ").trim(), name);
  for (const nm of ["תוצאות אמיתיות", "מה אומרים"]) { await N.p.evaluate(nm => document.querySelector('details.fold[data-fold="' + nm + '"]').open = true, nm); await O.p.evaluate(nm => document.querySelector('details.fold[data-fold="' + nm + '"]').open = true, nm);
   const a = await inner(N, nm), o = (await oh(O, nm)) + " " + (await inner(O, nm)); ok(tag + ": '" + nm + "' content unchanged (old heading first inside)", a === o.trim(), [a.slice(0, 120), o.slice(0, 120)]) }
  const lines = await N.p.evaluate(() => [...document.querySelectorAll(".bennote .bn-in p")].map(p => p.innerText.trim()).filter(Boolean));
  if (BEN) { ok(tag + ": Ben's paragraph word for word (" + BEN.length + " lines)", JSON.stringify(lines) === JSON.stringify(BEN), JSON.stringify(lines).slice(0, 300)); ok(tag + ": no long dash in page", !/[—–]/.test(await N.p.evaluate(() => document.body.innerText))) }
  else ok(tag + ": placeholder build (structure only)", lines.length === 1 && /ממתין לנוסח/.test(lines[0]), lines.join("|"));
  // אין מילה חדשה חוץ מהכותרות של בן והפסקה שלו
  await N.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = true)); await O.p.evaluate(() => document.querySelectorAll("details").forEach(d => d.open = true));
  const W = async X => new Set((await X.p.evaluate(() => document.body.innerText)).replace(/\s+/g, " ").split(" ")), wN = await W(N), wO = await W(O);
  const allowed = new Set(("מה אנשים שעברו את התהליך שלנו מספרים אנשים מספרים בתוך הקהילה הפרטית שלנו " + (BEN ? BEN.join(" ") : "[הפסקה של בן - 13 שורות - ממתין לנוסח]")).split(/\s+/));
  const extra = [...wN].filter(w => !wO.has(w) && !allowed.has(w)); ok(tag + ": no new words except Ben's", !extra.length, extra.slice(0, 15).join(" "));
  ok(tag + ": hero is data-sec=1 (sticky/hero scripts)", await N.p.evaluate(() => !!document.querySelector('header.hero9[data-sec="1"]') && document.querySelectorAll("[data-sec]").length === new Set([...document.querySelectorAll("[data-sec]")].map(e => e.dataset.sec)).size));
  ok(tag + ": no JS errors", !N.errs.length, N.errs.join("|"));
  if (!mobile) { const F = await open(NEW, false);
   const k0 = F.ev.length; await F.p.click('details.fold.hot[data-fold="תוצאות אמיתיות"] > summary'); await F.p.waitForTimeout(400);
   const fo = F.ev.slice(k0).filter(e => e.ev === "fold_open"); ok("fold_open on hot fold", fo.length === 1 && fo[0].name === "תוצאות אמיתיות" && fo[0].variant === "a5s", JSON.stringify(fo)); await F.c.close();
   const hrefs = async X => X.p.$$eval("a[data-checkout]", a => [...new Set(a.map(x => x.getAttribute("href").replace(/sid=[^&]+/, "")))].join("|"));
   ok("checkout links unchanged", (await hrefs(N)) === (await hrefs(O))) }
  await N.c.close(); await O.c.close() }
 // רק a5s, dashboard ו-campaign משתנים
 const diff = fs.readdirSync(path.join(NEW, "nlp")).filter(fn => fn.endsWith(".html") && fs.existsSync(path.join(OLD, "nlp", fn)) && !fs.readFileSync(path.join(NEW, "nlp", fn)).equals(fs.readFileSync(path.join(OLD, "nlp", fn))));
 ok("only a5s, dashboard, campaign changed", diff.sort().join(",") === "a5s.html,campaign.html,dashboard.html", diff.join(","));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
