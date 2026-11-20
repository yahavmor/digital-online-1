// מחיר מחוק 1,290 במקום 2,411 בכל 15 הדפים. שימוש: node t_price.js <root חדש> <root ישן (main)>
const { chromium, devices } = require("playwright"), fs = require("fs"), path = require("path");
const [NEW, OLD] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; if (!c) console.log("FAIL " + m + "  <- " + JSON.stringify(d).slice(0, 300)) };
const PAGES = ["a", "a1", "a2", "a3", "a4", "a5", "b", "b2", "c", "c2", "a5s", "a5v4", "a5v5", "a5v6", "a5v7"];
const CT = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg" };
async function open(b, root, dev, pg) { const c = await b.newContext(dev), errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url());
  if (u.hostname === "local.test") { const fp = path.join(root, u.pathname); return fs.existsSync(fp) && fs.statSync(fp).isFile() ? r.fulfill({ status: 200, body: fs.readFileSync(fp), contentType: CT[path.extname(fp)] }) : r.fulfill({ status: 404, body: "" }) }
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message));
 await p.goto("https://local.test/nlp/" + pg + ".html?stay=1"); // a2/b2/c2 מפנים ל-go.html בלי stay=1 await p.waitForTimeout(800);
 await p.addStyleTag({ content: "html,body{scroll-behavior:auto!important}" });
 // גלילה הדרגתית עד אזור המחיר, כדי שאנימציות הכניסה ירוצו
 await p.evaluate(async () => { const t = document.querySelector(".v4-ko,.pay"); const y = t.getBoundingClientRect().top + scrollY - 200; for (let k = 0; k <= y; k += 300) { scrollTo(0, k); await new Promise(r => setTimeout(r, 60)) } t.scrollIntoView({ block: "center" }) });
 await p.waitForTimeout(2500);
 const st = await p.evaluate(() => { const vis = e => { if (!e) return null; const r = e.getBoundingClientRect(); let o = 1; for (let x = e; x; x = x.parentElement) o *= +getComputedStyle(x).opacity; return r.width > 0 && r.height > 0 && o > 0.9 };
  const body = document.body.innerText;
  const was = [...document.querySelectorAll(".v4-ko-reg s, .pay s.was")].map(s => s.innerText.trim());
  const now = document.querySelector(".v4-ko-now b, .pay .now");
  return { has2411: /2,?411/.test(body), was, wasVis: [...document.querySelectorAll(".v4-ko-reg, .pay .now")].map(vis), nowTxt: now && now.innerText, nowVis: vis(now),
   totLine: /שווי כולל/.test(body), list: [...document.querySelectorAll(".v4-ko-list li, .stack6 .row")].map(r => r.innerText.replace(/\s+/g, " ")).join("|"),
   links: document.querySelectorAll("a,button").length, text: body.replace(/\s+/g, " ") } });
 await c.close(); return { st, errs } }
(async () => { const b = await chromium.launch();
 for (const [dn, dev] of [["mobile", devices["iPhone 13"]], ["desktop", { viewport: { width: 1280, height: 860 } }]]) for (const pg of PAGES) {
  const N = await open(b, NEW, dev, pg), O = await open(b, OLD, dev, pg), t = dn + " " + pg + ": ";
  ok(t + "no 2,411 on the page", !N.st.has2411, N.st);
  ok(t + "no 'שווי כולל' line", !N.st.totLine);
  ok(t + "crossed-out price is 1,290", N.st.was.length && N.st.was.every(w => /^1,290( ₪)?$/.test(w)), N.st.was);
  ok(t + "crossed-out price and 297 visible", N.st.wasVis.every(Boolean) && N.st.nowVis && /297/.test(N.st.nowTxt), [N.st.wasVis, N.st.nowVis, N.st.nowTxt]);
  ok(t + "item list unchanged", N.st.list === O.st.list, [N.st.list, O.st.list]);
  ok(t + "same buttons/links", N.st.links === O.st.links, [N.st.links, O.st.links]);
  ok(t + "no new JS errors", N.errs.length <= O.errs.length, N.errs);
  // רק הטקסט של המחיר השתנה
  const strip = s => s.replace(/שווי כולל( עם הבונוסים)?: ?2,411 ₪ ?/g, "").replace(/מחיר כולל הבונוסים 2,411 ₪/g, "מחיר הקורס 1,290 ₪").replace(/\s+/g, " ").trim();
  ok(t + "no other visible text changed", strip(O.st.text) === N.st.text.replace(/\s+/g, " ").trim(), "diff");
 }
 const diff = fs.readdirSync(path.join(NEW, "nlp")).filter(x => fs.statSync(path.join(NEW, "nlp", x)).isFile() && !fs.readFileSync(path.join(NEW, "nlp", x)).equals(fs.readFileSync(path.join(OLD, "nlp", x)))).map(x => x.replace(".html", "")).sort();
 ok("only the 15 pages changed", diff.join(",") === [...PAGES].sort().join(","), diff);
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
