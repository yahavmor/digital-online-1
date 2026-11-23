// ב119: בדיקת הדשבורד החדש (נייד). שימוש: node t_dash.js <dashboard.html> [shot.png]
const { chromium, devices } = require("playwright"), fs = require("fs");
const [FILE, SHOT] = process.argv.slice(2); let n = 0, f = 0;
const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + JSON.stringify(d).slice(0, 600))) };
const il = off => new Date(Date.now() - off * 864e5).toLocaleString("sv-SE", { timeZone: "Asia/Jerusalem" }).slice(0, 10);
const nowIL = () => new Date().toLocaleString("sv-SE", { timeZone: "Asia/Jerusalem" }).slice(0, 16);
const gv = (upd, data) => "/*O_o*/\ngoogle.visualization.Query.setResponse(" + JSON.stringify({ version: "0.6", status: "ok", table: { cols: [{ id: "A" }, { id: "B" }], rows: [{ c: [{ v: "updated" }, { v: upd }] }, { c: [{ v: "data" }, { v: data }] }] } }) + ");";
async function page(b, body, status) { const c = await b.newContext({ ...devices["iPhone 13"] }); const errs = [];
  await c.route("**/*", r => { const u = r.request().url();
    if (u.startsWith("https://local.test/")) return r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(FILE) });
    if (u.includes("/gviz/tq")) return r.fulfill({ status: status || 200, contentType: "text/javascript", body });
    if (u.includes("fonts.g")) return r.fulfill({ status: 200, body: "" });
    return r.abort() });
  const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/dashboard.html"); await p.waitForTimeout(700); return { c, p, errs } }
const card = (p, sel) => p.$$eval(sel + " .t", ts => ts.map(t => [t.querySelector(".k").textContent, t.querySelector(".v").textContent]));
(async () => { const b = await chromium.launch();
  // 1. הנתונים: רחל ירוק, אמיר צהוב (25 ₪), גל אדום (35 ₪), בלי מכירות (גיליון ריק) -> "עוד אין נתון"
  const T = il(0), Y = il(1), OLD = "2026-11-22";
  const data = ["#v1", "spend_rows\t5", "sales_rows\t0",
    `${OLD}\trachel\t10\t2\t150\t0`, `${T}\trachel\t5\t1\t50\t0`,
    `${OLD}\tamir\t4\t0\t100\t0`, `${T}\tamir\t0\t0\t\t0`,
    `${OLD}\tgal\t2\t1\t70\t0`, `${T}\tother\t3\t1\t\t0`].join("\n");
  { const { c, p, errs } = await page(b, gv(nowIL(), data));
    ok("default period = since start (22.11), title + 'עודכן לאחרונה: היום'", (await p.getAttribute('[data-p="all"]', "aria-pressed")) === "true" && /עודכן לאחרונה: היום ב-\d\d:\d\d/.test(await p.textContent("#upd")), await p.textContent("#upd"));
    const S = await card(p, ".card.sum");
    ok("summary: 6 numbers only, labels in order", S.map(x => x[0]).join("|") === "הוצאנו|לידים|עלות לליד|לידים חמים|מכירות|עלות למכירה", S);
    ok("summary since start: spend 370, leads 24, hot 5, sales = no data", S[0][1] === "370 ₪" && S[1][1] === "24" && S[3][1] === "5" && S[4][1] === "עוד אין נתון" && S[5][1] === "עוד אין נתון", S);
    const cards = await p.$$eval(".card[data-mk]", cs => cs.map(c => [c.querySelector("h2").textContent, c.querySelector(".dot").className]));
    ok("cards: רחל, אמיר, גל in order", cards.map(x => x[0]).join(",") === "רחל,אמיר,גל", cards);
    ok("dots: רחל green (13 ₪), אמיר yellow (25 ₪), גל red (35 ₪)", /\bg\b/.test(cards[0][1]) && /\by\b/.test(cards[1][1]) && /\br\b/.test(cards[2][1]), cards);
    const R = await card(p, '[data-mk="rachel"]');
    ok("רחל: 200 ₪, 15 leads, 13 ₪ per lead, 3 hot", R[0][1] === "200 ₪" && R[1][1] === "15" && R[2][1] === "13 ₪" && R[3][1] === "3", R);
    await p.click('[data-p="today"]'); await p.waitForTimeout(100);
    const S2 = await card(p, ".card.sum"), A2 = await card(p, '[data-mk="amir"]'), G2 = await card(p, '[data-mk="gal"]');
    const d2 = await p.$$eval(".card[data-mk] .dot", ds => ds.map(d => d.className));
    ok("today: summary 50 ₪ / 8 leads / 2 hot; אמיר spend = 'עוד אין נתון' (not 0); גל no rows -> 0 leads, spend no data", S2[0][1] === "50 ₪" && S2[1][1] === "8" && S2[3][1] === "2" && A2[0][1] === "עוד אין נתון" && A2[2][1] === "עוד אין נתון" && G2[1][1] === "0" && G2[0][1] === "עוד אין נתון", [S2, A2, G2]);
    ok("today: under 60 ₪ -> all grey", d2.every(c => /\bn\b/.test(c)), d2);
    await p.click('[data-p="7"]'); await p.waitForTimeout(100);
    const exp7 = OLD >= il(6) ? "370 ₪" : "50 ₪";
    ok("7 days period works (" + exp7 + ")", (await card(p, ".card.sum"))[0][1] === exp7, await card(p, ".card.sum"));
    const html = await p.content();
    ok("no technical words on the page (A/B, panel, utm, CPL, Make, stage)", !/A\/B|panel|פאנל|utm|CPL|CPA|Make|stage|webhook/i.test(await p.innerText("body")), "");
    ok("no horizontal scroll on phone", await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]));
    ok("noindex + RTL + Hebrew", /noindex/.test(html) && (await p.getAttribute("html", "dir")) === "rtl", "");
    ok("no JS errors", !errs.length, errs);
    await p.click('[data-p="all"]'); await p.waitForTimeout(100);
    if (SHOT) await p.screenshot({ path: SHOT, fullPage: true });
    await c.close() }
  // 2. כללי הצבע: 450 ₪ בלי ליד חם -> צהוב; 1,000 ₪ בלי מכירה (כשיש מכירות בגיליון) -> אדום; אין לידים עם הוצאה -> אדום; עלות למכירה מול היעד
  { const d = ["#v1", "spend_rows\t3", "sales_rows\t2", `${OLD}\trachel\t30\t0\t450\t0`, `${OLD}\tamir\t60\t3\t1000\t0`, `${OLD}\tgal\t0\t0\t80\t0`, `${OLD}\tother\t40\t2\t1500\t2`].join("\n");
    const { c, p, errs } = await page(b, gv(nowIL(), d)); const ds = await p.$$eval(".card[data-mk] .dot", x => x.map(e => e.className));
    ok("רחל 15 ₪/lead but 450 ₪ with no hot lead -> yellow", /\by\b/.test(ds[0]), ds);
    ok("אמיר 16.7 ₪/lead but 1,000 ₪ with no sale -> red", /\br\b/.test(ds[1]), ds);
    ok("גל 80 ₪ and 0 leads -> red", /\br\b/.test(ds[2]), ds);
    const S = await card(p, ".card.sum"), A = await card(p, '[data-mk="amir"]');
    ok("sales known: summary 2 sales, cost per sale 1,515 ₪ (red, over target); אמיר sales 0 -> 'עוד אין מכירה'", S[4][1] === "2" && S[5][1] === "1,515 ₪" && (await p.$eval(".card.sum .t:nth-child(6) .v", e => e.className)).includes("bad") && A[4][1] === "0" && A[5][1] === "עוד אין מכירה", [S, A]);
    ok("no JS errors", !errs.length, errs); await c.close() }
  // 3. שגיאה ונתונים ישנים
  { const { c, p } = await page(b, "x", 500); ok("load failure -> clear Hebrew message", /לא הצלחנו לטעון/.test(await p.textContent("#out")), await p.textContent("#out")); await c.close() }
  { const { c, p } = await page(b, gv(il(1) + " 01:00", "#v1\nspend_rows\t0\nsales_rows\t0"));
    ok("stale update -> red warning; empty data -> zeros for leads, 'עוד אין נתון' for spend/sales", /לא מעודכן/.test(await p.textContent("#upd")) && (await card(p, ".card.sum"))[1][1] === "0" && (await card(p, ".card.sum"))[0][1] === "עוד אין נתון", [await p.textContent("#upd"), await card(p, ".card.sum")]); await c.close() }
  console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
