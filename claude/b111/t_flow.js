// ב111: כניסה -> לחיצה -> סליקה, מהדף הקצר ומשתי הזרועות של on_1711. שימוש: node t_flow.js <root>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp" };
(async () => { const b = await chromium.launch();
 const run = async (start, rnd, ls, cta) => { const c = await b.newContext({ ...devices["iPhone 13"] }); const errs = [], ev = [];
  await c.addInitScript(([ls, rnd]) => { try { if (!sessionStorage.getItem("_i")) { for (const k in ls) localStorage.setItem(k, ls[k]); sessionStorage.setItem("_i", "1") } } catch (e) {} crypto.getRandomValues = a => { a[0] = rnd; return a } }, [ls || {}, rnd]);
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
   if (u.hostname.endsWith("make.com")) { const d = r.request().postData(); if (d && /(^|&)ev=/.test(d)) ev.push(Object.fromEntries(new URLSearchParams(d)).ev); return r.fulfill({ status: 200, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/" + start); await p.waitForTimeout(1500);
  const page = p.url().split("/").pop().split("?")[0]; const a = p.locator(cta ? '[data-cta="' + cta + '"]' : "a[data-checkout]:visible").first(); await a.scrollIntoViewIfNeeded(); await a.click(); await p.waitForURL(/checkout/); await p.waitForTimeout(2500);
  const st = await p.evaluate(() => ({ co: window.NLP_CO, fields: [...document.querySelectorAll("input")].filter(i => i.offsetParent).length, btn: [...document.querySelectorAll("button")].some(x => x.offsetParent) }));
  await c.close(); return { page, ...st, errs, chkEv: ev.filter(e => /^checkout_/.test(e)) } };
 const Q = "utm_source=facebook&utm_medium=paid&utm_id=1&utm_content=claude_flow";
 const r1 = await run("a5s.html?utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w1_ben", 0, {}, "offer");
 ok("a5s -> checkout B2, form visible, no JS errors, checkout_view sent", r1.co === "b2" && r1.fields > 0 && r1.btn && !r1.errs.length && r1.chkEv.includes("checkout_view"), JSON.stringify(r1));
 const r1b = await run("a5s.html?utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben", 0, { nlp_go_on_1711: "a", nlp_co_ab: "a" }, "offer");
 ok("a5s (browser in arm a) -> checkout B2", r1b.co === "b2" && r1b.fields > 0 && !r1b.errs.length, JSON.stringify(r1b));
 const r2 = await run("go.html?" + Q, 0, {}, null);
 ok("go.html arm a -> a.html -> checkout A, form visible, no JS errors", r2.page === "a.html" && r2.co === "a" && r2.fields > 0 && !r2.errs.length && r2.chkEv.includes("checkout_view"), JSON.stringify(r2));
 const r3 = await run("go.html?" + Q, 1, {}, null);
 ok("go.html arm a5v7 -> a5v7.html -> checkout B2, form visible, no JS errors", r3.page === "a5v7.html" && r3.co === "b2" && r3.fields > 0 && !r3.errs.length && r3.chkEv.includes("checkout_view"), JSON.stringify(r3));
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
