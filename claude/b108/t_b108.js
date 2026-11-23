// ב108: שיוך למשווקים (NLP_OWNER) - group/story/page/page_post ו-whatsapp מאפסים לבן. הניתוב לא משתנה.
// שימוש: node t_b108.js <new root> <old root>
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + d)) };
(async () => { const b = await chromium.launch();
 // ls: localStorage לפני הכניסה; rnd: ההגרלה (0 -> a, 1 -> a5v7)
 const visit = async (root, pg, q, o = {}) => { const c = await b.newContext();
  await c.addInitScript(([ls, rnd]) => { try { if (!sessionStorage.getItem("_i")) { for (const k in ls) localStorage.setItem(k, ls[k]); sessionStorage.setItem("_i", "1") } } catch (e) {}
   if (rnd != null) crypto.getRandomValues = a => { a[0] = rnd; return a } }, [o.ls || {}, o.rnd ?? 0]);
  await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: "text/html; charset=utf-8" }) : r.fulfill({ status: 404, body: "" }) } return r.fulfill({ status: 204, body: "" }) });
  const p = await c.newPage(); await p.goto("https://local.test/nlp/" + pg + (q ? "?" + q : "")); await p.waitForTimeout(1300);
  const u = new URL(p.url()), st = await p.evaluate(() => ({ owner: window.NLP_OWNER ? NLP_OWNER() : "?", arm: localStorage.getItem("nlp_go_on_1711"), co: localStorage.getItem("nlp_co_ab") }));
  let coOwner = null; if (o.thenCheckout) { await p.goto("https://local.test/nlp/checkout.html?v=" + (st.arm || "a")); await p.waitForTimeout(700); coOwner = await p.evaluate(() => window.NLP_OWNER ? NLP_OWNER() : "?") }
  await c.close(); return { page: u.pathname.split("/").pop(), exp: u.searchParams.get("exp") || "", route: u.searchParams.get("route") || "", ...st, coOwner } };
 const GAL = { nlp_aff: JSON.stringify({ c: "gal", t: Date.now() - 3 * 864e5 }) };
 const SRC = [["whatsapp group", "utm_source=whatsapp&utm_medium=group"], ["instagram story", "utm_source=instagram&utm_medium=story"], ["facebook page", "utm_source=facebook&utm_medium=page"], ["facebook page_post", "utm_source=facebook&utm_medium=page_post"], ["whatsapp (no medium)", "utm_source=whatsapp"]];
 // 1. ארבעת המקורות (ועוד whatsapp בלי medium): עם ובלי שיוך קודם - השיוך לבן; הדף והזרוע כמו היום
 for (const [lab, q] of SRC) for (const prior of [false, true]) for (const rnd of [0, 1]) {
  const o = { ls: prior ? GAL : {}, rnd }, N = await visit(NEW, "go.html", q, { ...o, thenCheckout: true }), O = await visit(OLD, "go.html", q, o);
  ok(lab + (prior ? " +prior gal" : "") + " rnd" + rnd + ": owner ben (also in checkout), page/arm/exp as today (" + N.page + ", " + N.exp + ")",
   N.owner === "" && N.coOwner === "" && N.page === O.page && N.arm === O.arm && N.co === O.co && N.exp === O.exp && N.exp === "on_1711" && N.route === "", JSON.stringify([N, O])) }
 // 2. גם בכניסה ישירה לדף (בלי go.html) השיוך מתאפס
 for (const pg of ["a.html", "a5v7.html", "a5s.html"]) { const N = await visit(NEW, pg, "utm_source=whatsapp&utm_medium=group", { ls: GAL }); ok("direct " + pg + " whatsapp group +prior gal: owner ben", N.owner === "", JSON.stringify(N)) }
 // 3. רגרסיה
 { const N = await visit(NEW, "go.html", "utm_source=fb&utm_medium=affiliate&aff=amir&utm_content=p25_brain_c1", { ls: GAL }); ok("aff link: owner = amir", N.owner === "amir", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "utm_source=whatsapp&utm_medium=affiliate&aff=amir", { ls: GAL }); ok("aff link from whatsapp: owner = amir", N.owner === "amir", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "utm_source=fb&utm_medium=affiliate", { ls: GAL }); ok("utm_medium=affiliate without aff: prior gal kept", N.owner === "gal", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "utm_source=whatsapp&utm_medium=affiliate", { ls: GAL }); ok("utm_medium=affiliate + whatsapp source: prior gal kept", N.owner === "gal", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "", { ls: GAL }); ok("direct visit without utm: prior gal kept", N.owner === "gal", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "utm_source=instagram&utm_medium=bio", { ls: GAL }), O = await visit(OLD, "go.html", "utm_source=instagram&utm_medium=bio", { ls: GAL });
   ok("ig_org unchanged: a.html, route=ig_org, no exp, owner ben", N.page === "a.html" && N.route === "ig_org" && !N.exp && N.owner === "" && JSON.stringify(N) === JSON.stringify(O), JSON.stringify([N, O])) }
 { const N = await visit(NEW, "go.html", "utm_source=facebook&utm_medium=paid&utm_id=1", { ls: GAL }); ok("Ben paid ad: owner ben (as before)", N.owner === "", JSON.stringify(N)) }
 for (const arm of ["a", "a5v7"]) { const N = await visit(NEW, "go.html", "utm_source=whatsapp&utm_medium=group", { ls: { nlp_go_on_1711: arm, nlp_co_ab: arm === "a" ? "a" : "b2" }, rnd: arm === "a" ? 1 : 0 });
   ok("stored arm " + arm + " kept for whatsapp visitor", N.page === arm + ".html" && N.arm === arm && N.exp === "on_1711", JSON.stringify(N)) }
 { const N = await visit(NEW, "go.html", "utm_source=whatsapp&utm_medium=group", { ls: { nlp_go_on_1611: "a5v6" } }); ok("legacy on_1611 a5v6 stays a5v6 (exp=on_1611)", N.page === "a5v6.html" && N.exp === "on_1611", JSON.stringify(N)) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
