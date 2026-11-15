// ב68 שלב ג: go.html מפנה הכול ל-a5v6, והמדידה עד הסליקה נשמרת. אייפון 13, האתר מהתיקייה המקומית (עותק של main עם השינוי).
// שימוש: node t_stagec.js <nlp dir>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const DIR = path.resolve(process.argv[2]), H = "https://funnel.digitalonline.co.il/nlp/";
const T = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".woff2": "font/woff2", ".json": "application/json" };
let n = 0, f = 0; const ok = (m, c, i) => { n++; if (!c) { f++; console.log("FAIL", m, i === undefined ? "" : i) } else console.log("PASS", m) };
(async () => {
  const b = await chromium.launch();
  const ctx = async (pre) => { const c = await b.newContext({ ...devices["iPhone 13"] }); const ev = [], px = [];
    await c.route("**/*", r => { const u = new URL(r.request().url());
      if (u.href.startsWith(H)) { const fp = path.join(DIR, decodeURIComponent(u.pathname.replace(/^\/nlp\//, ""))); if (!fs.existsSync(fp)) return r.fulfill({ status: 404, body: "nf" }); return r.fulfill({ status: 200, contentType: T[path.extname(fp)] || "application/octet-stream", body: fs.readFileSync(fp) }) }
      if (/make\.com/.test(u.hostname)) { const pd = r.request().postData() || ""; try { const o = Object.fromEntries(new URLSearchParams(pd)); ev.push(Object.keys(o).length > 1 ? o : JSON.parse(pd)) } catch (e) { ev.push({ raw: pd }) } return r.fulfill({ status: 200, body: "{}" }) }
      if (/facebook\.(com|net)/.test(u.hostname)) { px.push(u.href); return r.fulfill({ status: 200, body: "" }) }
      return r.fulfill({ status: 204, body: "" }) });
    if (pre) await c.addInitScript(pre);
    const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message)); return { c, p, ev, px, errs } };
  const land = async (X, qs) => { await X.p.goto(H + "go.html?" + qs); await X.p.waitForURL(/a5v6\.html|a\.html/, { timeout: 10000 }); await X.p.waitForTimeout(1500); return new URL(X.p.url()) };
  // 1. מודעה של בן
  const AD = "utm_source=fb&utm_medium=paid&utm_campaign=NLP%20%7C%20Cold&utm_content=car5_3habits_a&utm_id=123&fbclid=abc";
  const A = await ctx(); const u1 = await land(A, AD + "&exp=old");
  ok("ad → a5v6.html", /\/nlp\/a5v6\.html$/.test(u1.pathname), u1.href);
  ok("params kept + go=1 + exp=a5v6_1511 (old exp replaced)", ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_id", "fbclid"].every(k => u1.searchParams.get(k) === new URLSearchParams(AD).get(k)) && u1.searchParams.get("go") === "1" && u1.searchParams.get("exp") === "a5v6_1511" && u1.searchParams.getAll("exp").length === 1, u1.search);
  const v1 = A.ev.filter(e => e.variant === "a5v6" || (e.v === "a5v6"));
  ok("events from a5v6 with exp=a5v6_1511 in qs", v1.length > 0 && v1.every(e => /exp=a5v6_1511/.test(e.qs || "")), JSON.stringify(A.ev[0] || {}).slice(0, 300));
  const px1 = await A.p.evaluate(() => (window.fbq && window.fbq.queue || []).map(a => [...a].slice(0, 2).join(":")));
  ok("pixel: init + PageView + ViewContent", px1.some(x => /^init/.test(x)) && px1.includes("track:PageView") && px1.includes("track:ViewContent"), px1.join(","));
  const sid1 = await A.p.evaluate(() => { try { return sessionStorage.getItem("nlp_sid") || "" } catch (e) { return "" } });
  await Promise.all([A.p.waitForURL(/checkout\.html/, { timeout: 10000 }).catch(() => {}), A.p.click('[data-cta="hero_main"]')]);
  const c1 = new URL(A.p.url());
  ok("hero button → checkout.html", /checkout\.html$/.test(c1.pathname), c1.href);
  ok("checkout link: v=a5v6, utm_content, utm_campaign, sid, exp", c1.searchParams.get("v") === "a5v6" && c1.searchParams.get("utm_content") === "car5_3habits_a" && c1.searchParams.get("utm_campaign") === "NLP | Cold" && !!c1.searchParams.get("sid") && (!sid1 || c1.searchParams.get("sid") === sid1) && /a5v6_1511/.test(c1.search), c1.search);
  ok("cta_click hero_main sent", A.ev.some(e => e.ev === "cta_click" && e.cta === "hero_main"));
  await A.p.waitForTimeout(1500);
  ok("checkout events carry same sid", A.ev.some(e => /^checkout_/.test(e.ev || "") && e.sid === c1.searchParams.get("sid")), A.ev.filter(e => /^checkout/.test(e.ev || "")).map(e => e.ev + ":" + e.sid).join(","));
  ok("no JS errors (ad flow)", !A.errs.length, A.errs.join("|"));
  // 2. מי ששובץ קודם ל-pr2 (וגם ל-pr ב-aap_0511)
  const B = await ctx(() => { try { localStorage.setItem("nlp_go_ap2_0811", "pr2"); localStorage.setItem("nlp_go_aap_0511", "pr") } catch (e) {} });
  const u2 = await land(B, AD); ok("stored pr2 assignment → a5v6", /a5v6\.html$/.test(u2.pathname), u2.href);
  // 3. משווק
  const C = await ctx(); const u3 = await land(C, "aff=gal&utm_source=fb&utm_medium=affiliate&utm_campaign=p25&utm_content=p25_gal");
  ok("affiliate → a5v6 with aff=gal", /a5v6\.html$/.test(u3.pathname) && u3.searchParams.get("aff") === "gal" && u3.searchParams.get("exp") === "a5v6_1511", u3.search);
  const own = await C.p.evaluate(() => { try { return JSON.parse(localStorage.getItem("nlp_aff")).c } catch (e) { return "" } });
  ok("owner saved = gal", own === "gal", own);
  ok("events carry aff=gal", C.ev.some(e => /(^|;)aff=gal(;|$)/.test(e.x || "")), JSON.stringify(C.ev.map(e => e.x)).slice(0, 200));
  await Promise.all([C.p.waitForURL(/checkout\.html/, { timeout: 10000 }).catch(() => {}), C.p.click('[data-cta="hero_main"]')]); await C.p.waitForTimeout(1200);
  ok("affiliate checkout events carry aff=gal", C.ev.some(e => /^checkout_/.test(e.ev || "") && /(^|;)aff=gal(;|$)/.test(e.x || "")), C.ev.filter(e => /^checkout/.test(e.ev || "")).map(e => e.x).join(" / "));
  // 4. אינסטגרם אורגני - בלי שינוי
  const D = await ctx(); const u4 = await land(D, "utm_source=instagram&utm_medium=bio");
  ok("ig bio → a.html route=ig_org, no exp", /\/a\.html$/.test(u4.pathname) && u4.searchParams.get("route") === "ig_org" && !u4.searchParams.has("exp"), u4.href);
  // 5. מסך ראשון ומהירות בסיסית (בלי האטה)
  const E = await ctx(); await land(E, AD);
  const fs1 = await E.p.evaluate(() => { const a = document.querySelector('[data-cta="hero_main"]'), r = a.getBoundingClientRect(); return { btn: r.bottom <= innerHeight && r.top >= 0, sw: document.documentElement.scrollWidth, w: innerWidth } });
  ok("phone: hero button in first screen, no horizontal scroll", fs1.btn && fs1.sw <= fs1.w, JSON.stringify(fs1));
  await E.p.screenshot({ path: __dirname + "/shot_a5v6_from_go.png" });
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0)
})();
