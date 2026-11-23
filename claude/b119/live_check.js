const { chromium, devices } = require("playwright"), fs = require("fs");
const [FILE, SHOT, URL] = process.argv.slice(2);
(async () => { const b = await chromium.launch(); const c = await b.newContext({ ...devices["iPhone 13"] });
  if (process.env.GV) await c.route("**/gviz/tq*", r => r.fulfill({ status: 200, contentType: "text/javascript", body: fs.readFileSync(process.env.GV) }));
  if (!URL) await c.route("https://local.test/**", r => r.fulfill({ status: 200, contentType: "text/html; charset=utf-8", body: fs.readFileSync(FILE) }));
  const p = await c.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto(URL || "https://local.test/dashboard.html"); await p.waitForTimeout(4000);
  console.log(await p.innerText("#upd")); console.log((await p.innerText("#out")).replace(/\n+/g, " | ").slice(0, 900)); console.log("errs", errs);
  if (SHOT) await p.screenshot({ path: SHOT, fullPage: true }); await b.close() })();
