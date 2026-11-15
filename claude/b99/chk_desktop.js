const { chromium } = require("playwright"), fs = require("fs"), path = require("path"); const H = "https://funnel.digitalonline.co.il/nlp/";
(async () => { const b = await chromium.launch();
 for (const [dir, tag] of [["b99/before/","before"],["b99/after/nlp/","after"]]) for (const co of ["b","b2"]) {
  const c = await b.newContext({ viewport: { width: 1280, height: 900 } });
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith(H)) { const fp = path.join(dir, u.pathname.replace(/^\/nlp\//, "")); if (!fs.existsSync(fp)) return r.fulfill({status:404,body:""}); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg")?"image/svg+xml":"application/octet-stream", body: fs.readFileSync(fp) }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto(H + "checkout.html?test=1&co=" + co); await p.waitForTimeout(800);
  const r = await p.evaluate(() => ({ name: Math.round(document.getElementById("fName").getBoundingClientRect().top), h: document.body.scrollHeight, one1: !!document.querySelector(".one1") && getComputedStyle(document.querySelector(".one1")).display, end: !!document.querySelector(".incl-end") && getComputedStyle(document.querySelector(".incl-end")).display, incl: getComputedStyle(document.querySelector(".order .incl")).display }));
  console.log("desktop", tag, co, JSON.stringify(r)); await c.close() }
 const c = await b.newContext({ viewport: { width: 375, height: 667 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
 await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.href.startsWith(H)) { const fp = path.join("b99/after/nlp/", u.pathname.replace(/^\/nlp\//, "")); if (!fs.existsSync(fp)) return r.fulfill({status:404,body:""}); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg")?"image/svg+xml":fp.endsWith(".webp")?"image/webp":"application/octet-stream", body: fs.readFileSync(fp) }) } return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); await p.goto(H + "checkout.html?test=1&co=b"); await p.waitForTimeout(800);
 const e = await p.$(".incl-end"); await e.scrollIntoViewIfNeeded(); await p.screenshot({ path: "wtb51/claude/b99/shots_after/375x667_b_end_list.png" });
 const pos = await p.evaluate(() => { const y = s => Math.round(document.querySelector(s).getBoundingClientRect().top + scrollY); return { form_end: y("#wallTop"), pay: y("#paySec"), deal: y("#deal"), safe: y(".safe"), list: y(".incl-end"), back: y("#back") } }); console.log("mobile order", JSON.stringify(pos));
 await b.close() })();
