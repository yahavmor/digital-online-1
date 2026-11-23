// ב99 אחרי פריסה: הדף כפי שנפרס (hash זהה לחי), 375x667, internal=1. לוכד את בקשת checkout_contact_started כדי לשלוח אותה ל-Make מה-workbench.
const { chromium } = require("playwright"), fs = require("fs"), path = require("path"); const H = "https://funnel.digitalonline.co.il/nlp/", DIR = process.argv[2];
const IG = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 345.0.0.32.110 (iPhone15,2; iOS 17_5; he_IL; he; scale=3.00; 1179x2556; 634108168)";
(async () => { const b = await chromium.launch(); const out = [];
 for (const co of ["b", "b2"]) {
  const c = await b.newContext({ viewport: { width: 375, height: 667 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: IG }); const reqs = [];
  await c.route("**/*", r => { const q = r.request(), u = new URL(q.url());
   if (u.href.startsWith(H)) { const fp = path.join(DIR, u.pathname.replace(/^\/nlp\//, "")); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "" }); return r.fulfill({ status: 200, contentType: fp.endsWith(".html") ? "text/html; charset=utf-8" : fp.endsWith(".svg") ? "image/svg+xml" : fp.endsWith(".webp") ? "image/webp" : "application/octet-stream", body: fs.readFileSync(fp) }) }
   if (u.host.includes("make.com")) { reqs.push({ url: q.url(), method: q.method(), headers: q.headers(), body: q.postData() }); return r.fulfill({ status: 200, body: "Accepted" }) }
   return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto(H + "checkout.html?co=" + co + "&internal=1&utm_source=b99_live_check"); await p.waitForTimeout(1200);
  const top = await p.evaluate(() => Math.round(document.getElementById("fName").getBoundingClientRect().top + scrollY));
  await p.screenshot({ path: "wtb51/claude/b99/shots_live_375x667_" + co + ".png" });
  await p.fill("#fName", "בדיקה פנימית"); await p.waitForTimeout(700);
  const cs = reqs.filter(r => /checkout_contact_started/.test((r.body || "") + r.url));
  console.log(co, "name top", top, "| contact_started captured:", cs.length);
  out.push(...cs.map(r => ({ co, ...r }))); await c.close() }
 fs.writeFileSync("b99/cs_reqs.json", JSON.stringify(out, null, 1)); await b.close() })();
