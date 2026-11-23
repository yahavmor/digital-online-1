// ב110: בדיקת הטיוטה (a5s_b110 + checkout_b110). שימוש: node t_b110.js <root עם nlp/ + קבצי הטיוטה> [shots]
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, SH] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };
(async () => { const b = await chromium.launch();
 const ctx = async () => { const c = await b.newContext({ ...devices["iPhone 13"] }); const ev = [], co = [];
  await c.route("**/*", async r => { const u = new URL(r.request().url());
   if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { const d = r.request().postData() || ""; const o = Object.fromEntries(new URLSearchParams(d));
    if (o.ev) { ev.push(o); return r.fulfill({ status: 200, body: "" }) }
    if ("email" in o && "phone" in o) { co.push(o); return r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ url: "https://secure.cardcom.solutions/External/test", lp: "LP-T" }) }) }
    return r.fulfill({ status: 200, body: "" }) }
   return r.fulfill({ status: 204, body: "" }) });
  await c.addInitScript(() => { window.__fb = []; Object.defineProperty(window, "fbq", { configurable: true, get() { return window.__fbqv }, set(v) { window.__fbqv = function () { window.__fb.push([...arguments].slice(0, 2).map(String)); return v.apply(this, arguments) }; Object.assign(window.__fbqv, v) } }) });
  const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); return { c, p, ev, co, errs } };
 // 1. שליחה ריקה / מייל לא תקין - לא נשמר ליד
 { const X = await ctx(); await X.p.goto("https://local.test/nlp/a5s_b110.html?utm_source=fb&utm_medium=paid&utm_id=1&utm_content=t"); await X.p.waitForTimeout(1200);
   await X.p.fill("#lfName", "ישראל ישראלי"); await X.p.fill("#lfEmail", "not-an-email"); await X.p.click('#lpForm button[type=submit]'); await X.p.waitForTimeout(400);
   ok("bad email: no lead saved, error shown, stays on page", !X.ev.some(e => e.ev === "checkout_details") && /מייל/.test(await X.p.textContent("#lfErr")) && /a5s_b110/.test(X.p.url()), X.p.url());
   await X.c.close() }
 // 2. שליחה תקינה
 const X = await ctx(); await X.p.goto("https://local.test/nlp/a5s_b110.html?utm_source=fb&utm_medium=paid&utm_id=1&utm_content=t"); await X.p.waitForTimeout(1200);
 ok("form is inside the offer card, under the price", await X.p.evaluate(() => { const f = document.getElementById("lpForm"), o = document.getElementById("offer"), pr = o.querySelector(".v4-ko-now"); return o.contains(f) && !!pr && (pr.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING) }));
 ok("form: name, email, one checkbox, button - no phone field", await X.p.evaluate(() => { const f = document.getElementById("lpForm"); return f.querySelectorAll("input:not([type=checkbox])").length === 2 && f.querySelectorAll("input[type=checkbox]").length === 1 && !f.querySelector("[type=tel]") && !!f.querySelector("button[type=submit]") }));
 if (SH) { const el = await X.p.$("#offer"); await el.scrollIntoViewIfNeeded(); await X.p.waitForTimeout(400); await el.screenshot({ path: path.join(SH, "b110_offer_form_mobile.png") }) }
 await X.p.fill("#lfName", "ישראל ישראלי"); await X.p.fill("#lfEmail", "israel@example.com"); await X.p.check("#lfBox");
 await Promise.all([X.p.waitForURL(/checkout_b110\.html/, { timeout: 8000 }), X.p.click('#lpForm button[type=submit]')]); await X.p.waitForTimeout(1500);
 const det = X.ev.find(e => e.ev === "checkout_details");
 ok("lead saved immediately: checkout_details with name/email, empty phone, consent=1", det && det.lead_name === "ישראל ישראלי" && det.lead_email === "israel@example.com" && det.lead_phone === "" && det.lead_consent === "1" && /cons=1;form=lp/.test(det.x) && det.variant === "a5s_f", JSON.stringify(det));
 ok("cta_click offer_form sent", X.ev.some(e => e.ev === "cta_click" && e.cta === "offer_form"));
 const u = new URL(X.p.url()); ok("checkout URL carries no name/email", !/israel|example|%D7/.test(u.search) && u.searchParams.get("v") === "a5s_f", u.search);
 ok("checkout: name and email prefilled, phone empty, consent checked", await X.p.evaluate(() => document.getElementById("fName").value === "ישראל ישראלי" && document.getElementById("fEmail").value === "israel@example.com" && document.getElementById("fPhone").value === "" && document.getElementById("fConsent").checked));
 ok("checkout: phone not required", await X.p.evaluate(() => !document.getElementById("fPhone").required));
 if (SH) { await X.p.waitForTimeout(300); await X.p.screenshot({ path: path.join(SH, "b110_checkout_prefilled_mobile.png") }) }
 await X.p.check("#fTerms"); await X.p.waitForTimeout(500); const go = await X.p.$('#det .go'); if (go && await go.isVisible()) await go.click(); await X.p.waitForTimeout(1500);
 console.log("  checkout flow events:", X.ev.map(e => e.ev).join(","));
 const d2 = X.ev.filter(e => e.ev === "checkout_details"); const verr = X.ev.filter(e => e.ev === "checkout_validation_error");
 ok("checkout accepts details without phone (no validation error)", !verr.length && d2.length >= 1 && d2.every(e => e.lead_phone === ""), JSON.stringify(verr));
 ok("payment page request sent with empty phone (7827398 must accept it - to verify)", X.co.length === 1 && X.co[0].phone === "" && X.co[0].email === "israel@example.com", JSON.stringify(X.co.map(o => ({ phone: o.phone, email: !!o.email }))));
 ok("no JS errors", !X.errs.length, X.errs.join("|")); await X.c.close();
 // 3. טלפון שהוזן ולא תקין - עדיין שגיאה
 { const Y = await ctx(); await Y.p.goto("https://local.test/nlp/checkout_b110.html?v=a5s_f"); await Y.p.waitForTimeout(1000);
   await Y.p.fill("#fName", "ישראל ישראלי"); await Y.p.fill("#fEmail", "israel@example.com"); await Y.p.fill("#fPhone", "123"); await Y.p.check("#fTerms"); await Y.p.waitForTimeout(300); const g2 = await Y.p.$('#det .go'); if (g2 && await g2.isVisible()) await g2.click(); await Y.p.waitForTimeout(800);
   ok("checkout: a wrong phone that was typed is still rejected", !Y.ev.some(e => e.ev === "checkout_details") && Y.ev.some(e => e.ev === "checkout_validation_error"), JSON.stringify(Y.ev.map(e => e.ev))); await Y.c.close() }
 // 4. הקבצים החיים לא השתנו
 const main = p => fs.readFileSync(path.join(ROOT, "nlp", p));
 ok("draft files are separate: checkout.html and a5s.html in root are the live ones (no lpForm, phone required)", !main("a5s.html").includes("lpForm") && main("checkout.html").includes('autocomplete="tel" dir="ltr" required'));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
