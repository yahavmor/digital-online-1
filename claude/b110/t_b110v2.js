// ב110 v2: בדיקת הטיוטה a5s_b110v2.html (נייד). שימוש: node t_b110v2.js <root עם nlp/ (main + קובץ הטיוטה)> <main root> [shots dir]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path"), crypto = require("crypto");
const [ROOT, MAIN, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d))) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".mp4": "video/mp4" };
const PFILE = process.argv[5] || "a5s_b110v2.html", QUOTES = /_q\.html$/.test(PFILE), LIVEV = PFILE === "a5s.html";
const VAR = LIVEV ? "a5s" : "a5s_f";
const PAGE = "https://local.test/nlp/" + PFILE;
(async () => { const b = await chromium.launch();
 const ctx = async (mode) => { const c = await b.newContext({ ...devices["iPhone 13"] }); const ev = [], co = [];
  await c.route("**/*", async r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] || "application/octet-stream" }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { const d = r.request().postData() || ""; const o = Object.fromEntries(new URLSearchParams(d));
    if (o.ev) { ev.push(o); return r.fulfill({ status: 200, body: "" }) }
    if ("email" in o && "phone" in o) { co.push(o); if (mode === "fail") return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ code: "5" }) });
     return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ url: "https://secure.cardcom.solutions/EA/LPC6/201667/test-lp?t=24", lp: "test-lp", code: "0" }) }) }
    return r.fulfill({ status: 200, body: "" }) }
   if (u.hostname === "secure.cardcom.solutions") return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: "<html><body>CARDCOM PAGE</body></html>" });
   return r.fulfill({ status: 204, body: "" }) });
  await c.addInitScript(() => { window.__fb = []; window.fbq = function () { window.__fb.push([...arguments].slice(0, 2).map(String)) }; window.fbq.loaded = true; Object.defineProperty(window, "fbq", { configurable: true, get() { return window.__fbqv || function () { window.__fb.push([...arguments].slice(0, 2).map(String)) } }, set(v) { window.__fbqv = function () { window.__fb.push([...arguments].slice(0, 2).map(String)) } } }) });
  const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); return { c, p, ev, co, errs } };
 const nearest = (p) => p.evaluate(() => { const fs = [...document.querySelectorAll("form.lpf")]; const mid = innerHeight / 2; let best = null, bd = 1e9; fs.forEach(f => { const r = f.getBoundingClientRect(); const d = Math.abs(r.top + r.height / 2 - mid); if (d < bd) { bd = d; best = f.dataset.form } }); return { form: best, dist: Math.round(bd) } });

 // 1. מבנה: 2 טפסים, אין כפתור שמוביל לסליקה, טיוטה נפרדת
 { const X = await ctx(); await X.p.goto(PAGE + "?utm_source=fb&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w1_ben"); await X.p.waitForTimeout(1200);
   const st = await X.p.evaluate(() => { const f1 = document.getElementById("lpForm1"), f2 = document.getElementById("lpForm2"), faq = document.querySelector("section.faq");
     return { forms: document.querySelectorAll("form.lpf").length, inOffer: !!f1.closest("#offer"), priceAbove: !!f1.closest(".v4-ko") && f1.compareDocumentPosition(document.querySelector(".v4-ko-now")) & Node.DOCUMENT_POSITION_PRECEDING,
       afterFaq: !!(faq.compareDocumentPosition(f2) & Node.DOCUMENT_POSITION_FOLLOWING), fields: [...f1.querySelectorAll("input:not(.lpf-hp)")].map(i => i.name).join(","), boxUnchecked: !f1.querySelector('[name="box"]').checked,
       variant: document.documentElement.dataset.variant, noindex: /noindex/.test(document.querySelector('meta[name="robots"]').content), phone: !!document.querySelector('form.lpf [name="phone"]') } });
   ok("2 forms: offer card under the price + after the FAQ", st.forms === 2 && st.inOffer && st.priceAbove && st.afterFaq, st);
   ok("fields: name, email, one box (unchecked), no phone", st.fields === "name,email,box" && st.boxUnchecked && !st.phone, st);
   ok("one visible box (second box hidden in BOX_MODE one_required)", await X.p.evaluate(() => [...document.querySelectorAll("#lpForm1 .lpf-c")].filter(l => getComputedStyle(l).display !== "none").length === 1));
   ok("noindex kept", st.noindex, st);
   const tq = await X.p.evaluate(() => { const q = document.querySelector('[data-testimonials="price"]'), f1 = document.getElementById("lpForm1"), pr = document.querySelector("#offer .v4-ko-now");
     return { n: q ? q.querySelectorAll("[data-quote]").length : 0, ph: q ? [...q.querySelectorAll("blockquote")].every(b => /^\[.*מחכה/.test(b.innerText.trim())) : false,
       afterPrice: !!(q && (pr.compareDocumentPosition(q) & Node.DOCUMENT_POSITION_FOLLOWING)), beforeForm: !!(q && (q.compareDocumentPosition(f1) & Node.DOCUMENT_POSITION_FOLLOWING)), inOffer: !!(q && q.closest("#offer")) } });
   if (QUOTES) ok("ב114 stage 2: testimonials block (2 placeholders) between the price and the form", tq.n === 2 && tq.ph && tq.afterPrice && tq.beforeForm && tq.inOffer, tq);
   else ok("stage 1 (form only): no testimonials block", tq.n === 0, tq);
   const wd = await X.p.evaluate(() => { const f = document.getElementById("lpForm1"), l = f.querySelector('[data-box="one"]');
     return { btn: f.querySelector("button .ct-t").innerText.trim(), how: f.querySelector(".lpf-how").innerText.trim(), box: l.innerText.replace(/\s+/g, " ").trim(),
       links: [...l.querySelectorAll("a")].map(a => a.getAttribute("href")).join(","), req: l.querySelector("input").required, legal: !!f.querySelector(".lpf-legal a[href='terms.html']"),
       brackets: /\[/.test(f.innerText) } });
   ok("Ben's approved wording: button, line above the form, box (terms + privacy links), no placeholders left", wd.btn === "בן, אני רוצה להתחיל עכשיו" && wd.how === "ממלאים שם ומייל, עוברים לתשלום מאובטח, והגישה לקורס מגיעה למייל תוך כמה דקות." && wd.box === "קראתי ואני מאשר/ת את התקנון ומדיניות הפרטיות, ומסכים/ה לקבל מבן נחום מיילים עם תוכן והצעות. אפשר להסיר בכל רגע." && wd.links === "terms.html,privacy.html" && wd.req && wd.legal && !wd.brackets, wd);
   ok("variant " + (LIVEV ? "a5s (live build)" : "a5s_f (draft)"), (await X.p.evaluate(() => document.documentElement.dataset.variant)) === (LIVEV ? "a5s" : "a5s_f"));
   // 2. כפתורי קנייה גוללים לטופס הקרוב, בלי מעבר דף
   for (const [cta, exp] of [["hero_main", "1"], ["guar", "1"]]) { await X.p.evaluate(() => scrollTo(0, 0)); await X.p.waitForTimeout(200);
     const k = X.ev.length; await X.p.click('a[data-cta="' + cta + '"]'); await X.p.waitForTimeout(1300); const nf = await nearest(X.p); const e = X.ev.slice(k).find(e => e.ev === "cta_click");
     ok(cta + ": scrolls to form " + exp + ", stays on page, cta_click to=form" + exp, nf.form === exp && nf.dist < 260 && X.p.url().includes(PFILE) && e && /to=form/.test(e.x) && !X.co.length, { nf, e, url: X.p.url() }) }
   const foc = await X.p.evaluate(() => document.activeElement && document.activeElement.name); ok("after scroll: no auto-focus (no keyboard pops up)", foc !== "name", foc);
   await X.p.focus("#lfName1"); await X.p.waitForTimeout(400);
   const fo = X.ev.filter(e => e.ev === "form_open").map(e => e.name); const fs1 = X.ev.filter(e => e.ev === "form_start").map(e => e.name);
   ok("form_open and form_start events", fo.includes("form1") && fs1.includes("form1"), { fo, fs1 });
   // הדביק בתחתית הדף -> הטופס השני
   await X.p.evaluate(() => scrollTo(0, document.body.scrollHeight * 0.83)); await X.p.waitForTimeout(800);
   const vis = await X.p.evaluate(() => document.getElementById("sticky").classList.contains("on"));
   if (vis) { await X.p.evaluate(() => { const st = document.getElementById("sticky"); st.style.transition = "none"; document.documentElement.classList.remove("lpf-in") }); await X.p.click('#sticky a[data-cta="sticky"]', { force: true }); await X.p.waitForTimeout(1300); const nf = await nearest(X.p); ok("sticky near the end: scrolls to form 2", nf.form === "2" && nf.dist < 260, nf) }
   else ok("sticky visible near the end (to test)", false, "sticky hidden");
   await X.p.evaluate(() => scrollTo(0, 0)); await X.p.waitForTimeout(900); await X.p.evaluate(() => document.getElementById("lpForm1").scrollIntoView({ block: "center" })); await X.p.waitForTimeout(1200);
   ok("sticky bar hidden while a form is on screen", await X.p.evaluate(() => document.documentElement.classList.contains("lpf-in") && getComputedStyle(document.getElementById("sticky")).opacity === "0"));
   // 3. אימות: מייל לא תקין ותיבה לא מסומנת - לא נשמר ליד ולא נוצר דף תשלום
   await X.p.evaluate(() => document.getElementById("lpForm1").scrollIntoView({ block: "center" })); await X.p.waitForTimeout(300);
   await X.p.fill("#lfName1", "ישראל ישראלי"); await X.p.fill("#lfEmail1", "not-an-email"); await X.p.click("#lpForm1 button[type=submit]"); await X.p.waitForTimeout(400);
   const er = await X.p.textContent("#lfErr1");
   ok("bad email + unticked box: errors, no lead, no payment page", /מייל/.test(er) && /התיבה/.test(er) && !X.ev.some(e => e.ev === "checkout_details") && !X.co.length && X.ev.some(e => e.ev === "form_error"), er);
   await X.p.fill("#lfEmail1", "test.user@example.com"); await X.p.click("#lpForm1 button[type=submit]"); await X.p.waitForTimeout(300);
   ok("box required (BOX_MODE one_required): still blocked", !X.co.length && /התיבה/.test(await X.p.textContent("#lfErr1")));
   // 4. שליחה תקינה: ליד, Lead + InitiateCheckout, קריאה ל-7827398 עם השם והמייל בלי טלפון, ומעבר ישר לקארדקום
   await X.p.check("#lfBox1"); const sid = await X.p.evaluate(() => window.__lpSid);
   await Promise.all([X.p.waitForURL(/cardcom\.solutions/, { timeout: 8000 }).catch(() => { }), X.p.click("#lpForm1 button[type=submit]")]); await X.p.waitForTimeout(500);
   const det = X.ev.find(e => e.ev === "checkout_details"), sub = X.ev.find(e => e.ev === "form_submit"), red = X.ev.find(e => e.ev === "checkout_pay_redirect"), c0 = X.co[0] || {};
   ok("lead saved: checkout_details with name, email, empty phone, consent=1", det && det.lead_name === "ישראל ישראלי" && det.lead_email === "test.user@example.com" && det.lead_phone === "" && det.lead_consent === "1" && det.variant === VAR && det.sid === sid, det);
   ok("form_submit + checkout_pay_redirect events", sub && /form=1/.test(sub.x) && red && /pay_load_ms=/.test(red.x), { sub, red });
   ok("payment page request: name+email, no phone, same sid, v=a5s_f, utm passed", c0.name === "ישראל ישראלי" && c0.email === "test.user@example.com" && c0.phone === "" && c0.sid === sid && c0.variant === VAR && c0.utm_campaign === "lenatzeach_w40" && c0.utm_content === "w1_ben" && c0.utm_medium === "paid" && !c0.aff, c0);
   const fb = await X.p.evaluate(() => window.__fb).catch(() => []);
   ok("went straight to the Cardcom page (no details page)", /secure\.cardcom\.solutions/.test(X.p.url()), X.p.url());
   ok("no JS errors", !X.errs.length, X.errs); await X.c.close() }
 // 5. Meta: Lead + InitiateCheckout בשליחה בלבד (לא בגלילה)
 { const X = await ctx(); await X.p.goto(PAGE + "?utm_source=fb&utm_medium=paid"); await X.p.waitForTimeout(1000);
   await X.p.click('a[data-cta="hero_main"]'); await X.p.waitForTimeout(900); const fb0 = await X.p.evaluate(() => window.__fb.filter(x => x[0] === "track").map(x => x[1]));
   await X.p.fill("#lfName1", "דנה כהן"); await X.p.fill("#lfEmail1", "dana@example.com"); await X.p.check("#lfBox1");
   await X.p.evaluate(() => { window.__lpGoBlock = 1; const o = location.assign; });
   const fbs = await X.p.evaluate(async () => { document.getElementById("lpForm1").requestSubmit(); return window.__fb.filter(x => x[0] === "track").map(x => x[1]) });
   ok("CTA click: no InitiateCheckout; submit: Lead + InitiateCheckout", !fb0.includes("InitiateCheckout") && fbs.includes("Lead") && fbs.includes("InitiateCheckout"), { fb0, fbs }); await X.c.close() }
 // 6. משווק (aff) עובר לדף התשלום; הטופס השני עובד
 { const X = await ctx(); await X.p.goto(PAGE + "?aff=rami&utm_source=facebook&utm_medium=affiliate&utm_campaign=NLP%20%7C%20Aff%20rami&utm_content=w1_promised"); await X.p.waitForTimeout(1000);
   await X.p.evaluate(() => document.getElementById("lpForm2").scrollIntoView({ block: "center" })); await X.p.waitForTimeout(400);
   await X.p.fill("#lfName2", "משה לוי"); await X.p.fill("#lfEmail2", "moshe@example.com"); await X.p.check("#lfBox2");
   await Promise.all([X.p.waitForURL(/cardcom\.solutions/, { timeout: 8000 }).catch(() => { }), X.p.click("#lpForm2 button[type=submit]")]);
   const c0 = X.co[0] || {}, det = X.ev.find(e => e.ev === "checkout_details") || {};
   ok("form 2 + affiliate: aff=rami sent to the payment page and in the lead event", c0.aff === "rami" && /aff=rami/.test(det.x || "") && /form=lp2/.test(det.x || "") && /cardcom/.test(X.p.url()), { c0, x: det.x }); await X.c.close() }
 // 7. גיבוי: יצירת דף התשלום נכשלה -> סליקה רגילה עם הפרטים ממולאים
 { const X = await ctx("fail"); await X.p.goto(PAGE + "?utm_source=fb&utm_medium=paid"); await X.p.waitForTimeout(1000);
   await X.p.fill("#lfName1", "רות לוי"); await X.p.fill("#lfEmail1", "ruth@example.com"); await X.p.check("#lfBox1");
   await Promise.all([X.p.waitForURL(/checkout\.html/, { timeout: 8000 }).catch(() => { }), X.p.click("#lpForm1 button[type=submit]")]); await X.p.waitForTimeout(1500);
   const v = await X.p.evaluate(() => ({ n: (document.getElementById("fName") || {}).value, e: (document.getElementById("fEmail") || {}).value })).catch(() => ({}));
   ok("payment page error: falls back to checkout.html with name+email filled, load_error logged", new RegExp("checkout\\.html\\?.*v=" + VAR + "(&|$)").test(X.p.url()) && v.n === "רות לוי" && v.e === "ruth@example.com" && X.ev.some(e => e.ev === "checkout_load_error"), { url: X.p.url(), v }); await X.c.close() }
 // 8. בוט (שדה נסתר מולא) - לא נשמר ליד
 { const X = await ctx(); await X.p.goto(PAGE); await X.p.waitForTimeout(900);
   await X.p.fill("#lfName1", "בוט בוט"); await X.p.fill("#lfEmail1", "bot@example.com"); await X.p.check("#lfBox1"); await X.p.evaluate(() => document.querySelector('#lpForm1 [name="company"]').value = "x");
   await X.p.click("#lpForm1 button[type=submit]"); await X.p.waitForTimeout(500);
   ok("honeypot filled: no lead, no payment page", !X.co.length && !X.ev.some(e => e.ev === "checkout_details") && X.ev.some(e => e.ev === "form_bot")); await X.c.close() }
 // 9. צילומי מסך
 if (SH) { fs.mkdirSync(SH, { recursive: true }); const c = await b.newContext({ ...devices["iPhone 13"] }); await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] || "application/octet-stream" }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
   const p = await c.newPage(); await p.goto(PAGE); await p.waitForTimeout(1500); await p.addStyleTag({ content: "html,body{scroll-behavior:auto!important}" });
   const shot = async (sel, fn, pad) => { const r = await p.evaluate(s => { const e = document.querySelector(s); e.scrollIntoView({ block: "start" }); scrollBy(0, -70); return 1 }, sel); await p.waitForTimeout(700); await p.screenshot({ path: path.join(SH, fn) }) };
   await shot("#offer .v4-ko-price", "b110v2_offer_form_mobile.png");
   await p.click("#lpForm1 button[type=submit]"); await p.waitForTimeout(300); await p.evaluate(() => { document.querySelector("#offer .v4-ko-price").scrollIntoView({ block: "start" }); scrollBy(0, -70) }); await p.waitForTimeout(400); await p.screenshot({ path: path.join(SH, "b110v2_offer_form_errors_mobile.png") });
   await shot("section.ctab", "b110v2_end_form_mobile.png");
   await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(300); await p.screenshot({ path: path.join(SH, "b110v2_hero_mobile.png") });
   await c.close(); console.log("shots ->", SH) }
 // 10. הקבצים החיים לא השתנו
 const h = fp => crypto.createHash("sha256").update(fs.readFileSync(fp)).digest("hex");
 const live = fs.readdirSync(path.join(MAIN, "nlp")).filter(x => x.endsWith(".html")); const diff = live.filter(x => h(path.join(MAIN, "nlp", x)) !== h(path.join(ROOT, "nlp", x)));
 ok("other live pages unchanged" + (LIVEV ? " (only a5s.html differs)" : ""), diff.join(",") === (LIVEV ? "a5s.html" : "") && !fs.existsSync(path.join(MAIN, "nlp", "a5s_b110v2.html")), diff);
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
