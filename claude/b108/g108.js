const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const CASES = [["ig bio (ig_org)", "utm_source=instagram&utm_medium=bio"], ["whatsapp group", "utm_source=whatsapp&utm_medium=group"], ["ig story", "utm_source=instagram&utm_medium=story"],
 ["fb page", "utm_source=facebook&utm_medium=page"], ["fb page_post", "utm_source=facebook&utm_medium=page_post"], ["ben paid ad", "utm_source=facebook&utm_medium=paid&utm_id=1"]];
(async () => { const b = await chromium.launch();
 for (const [lab, q] of CASES) for (const prior of [false, true]) { const c = await b.newContext();
  if (prior) await c.addInitScript(() => { try { if (!sessionStorage.getItem("_i")) { const t = Date.now() - 864e5 * 3; localStorage.setItem("nlp_aff", JSON.stringify({ c: "gal", t })); sessionStorage.setItem("_i", "1") } } catch (e) {} });
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(process.argv[2] || "wtmain72", u.pathname); return fs.existsSync(fp) ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: "text/html; charset=utf-8" }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto("https://local.test/nlp/go.html?" + q); await p.waitForTimeout(1200);
  const u = new URL(p.url()), st = await p.evaluate(() => ({ owner: window.NLP_OWNER ? NLP_OWNER() : "?", arm: localStorage.getItem("nlp_go_on_1711"), co: localStorage.getItem("nlp_co_ab") }));
  console.log(lab.padEnd(16), prior ? "prior aff=gal" : "no prior     ", "-> page", u.pathname.split("/").pop().padEnd(10), "exp=" + (u.searchParams.get("exp") || "-").padEnd(8), "route=" + (u.searchParams.get("route") || "-").padEnd(7), "arm=" + st.arm, "checkout=" + st.co, "owner=" + (st.owner || "ben"));
  await c.close() }
 await b.close() })();
