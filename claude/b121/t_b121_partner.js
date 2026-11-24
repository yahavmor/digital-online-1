// ב121: אזור המשווקים על תשובת API סינתטית (שם ליד מדומה, בלי פרטים אמיתיים): רכישת קורס + אפסייל, 220 + 72 = 292 ₪ בהמתנה עד 30.11. שימוש: node t_b121_partner.js <root> [shot.png]
const { chromium } = require("playwright"), fs = require("fs"), path = require("path");
const [ROOT, SHOT] = process.argv.slice(2); let n = 0, f = 0; const ok = (m, c, d) => { n++; if (!c) f++; console.log((c ? "ok  " : "FAIL") + " " + m + (c ? "" : "  <- " + String(d).slice(0, 500))) };
const API = ["me\tyehudit\tיהודית\t220\t0", "rows",
 "2026-11-23 22:30:00\tview\ts_yeh\taff=yehudit&utm_source=facebook\t0", "2026-11-23 22:31:00\tcta_click\ts_yeh\t\t0", "2026-11-23 22:36:00\tcheckout_details\ts_yeh\t\t0",
 "2026-11-23 22:37:18\tpurchase\ts_yeh\tdeal 900002 | 297 ILS | card\t0", "2026-11-23 22:39:36\tupsell_purchase\ts_yeh\tcourse_deal 900002 | deal 900003 | 97 ILS\t0",
 "2026-11-23 18:55:05\tmeta_scan:view\ts_scan\t\t1",
 "leads", "s_yeh\t2026-11-23 22:36:50\tפ. ל\t123", "refunds", "", "paid", "\t"].join("\n");
(async () => { const b = await chromium.launch(); const c = await b.newContext({ timezoneId: "Asia/Jerusalem", viewport: { width: 420, height: 900 }, deviceScaleFactor: 2 }); await c.clock.setFixedTime(new Date("2026-11-24T09:00:00+02:00")); const errs = [];
 await c.route("**/*", r => { const u = new URL(r.request().url()); if (u.hostname === "local.test") { const fp = path.join(ROOT, u.pathname); return fs.existsSync(fp) ? r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(fp) }) : r.fulfill({ status: 404, body: "" }) }
  if (u.hostname.endsWith("make.com")) return r.fulfill({ status: 200, contentType: "text/plain; charset=utf-8", body: u.searchParams.get("t") === "T".repeat(32) ? API : "Accepted" });
  return r.fulfill({ status: 204, body: "" }) });
 const p = await c.newPage(); p.on("pageerror", e => errs.push(e.message)); await p.goto("https://local.test/nlp/partner.html#t=" + "T".repeat(32)); await p.waitForTimeout(1500);
 const tiles = await p.evaluate(() => [...document.querySelectorAll("#tiles .tile")].map(t => t.innerText.replace(/\n/g, ": "))); console.log(tiles.join(" | "));
 ok("title shows the marketer", /יהודית/.test(await p.textContent("#title")));
 ok("tiles: 1 course purchase and 1 upsell", tiles.includes("רכישות קורס: 1") && tiles.includes("אפסיילים: 1"), tiles.join(" | "));
 ok("tiles: 292 ₪ pending (220 + 72), 0 due, 0 paid", tiles.includes("עמלה ממתינה: 292 ₪") && tiles.includes("עמלה לתשלום: 0 ₪") && tiles.includes("עמלה ששולמה: 0 ₪"), tiles.join(" | "));
 const fee = await p.textContent("#feeNote"); ok("fee note: 220 ₪ per course + 72 ₪ per upsell", /220 ₪ לרכישת קורס \+ 72 ₪ לאפסייל/.test(fee), fee);
 const tbl = await p.evaluate(() => document.getElementById("leads").innerText); console.log(tbl.replace(/\n/g, " | "));
 ok("lead row: purchased, pending until 30.11, 220 ₪, and upsell 97 ₪ pending until 30.11, 72 ₪", /רכש/.test(tbl) && /ממתין עד 30\.11/.test(tbl) && /220 ₪/.test(tbl) && /אפסייל 97 ₪/.test(tbl) && /72 ₪/.test(tbl), tbl);
 ok("one lead row only (upsell is attached to the same lead, not a new row)", (tbl.match(/רכש/g) || []).length === 1 && !/ - \n/.test(tbl), tbl);
 ok("no JS errors", !errs.length, errs.join(" | "));
 if (SHOT) { await p.screenshot({ path: SHOT, fullPage: true }); console.log("shot", SHOT) }
 console.log("TOTAL", n - f + "/" + n); await b.close(); process.exit(f ? 1 : 0) })();
