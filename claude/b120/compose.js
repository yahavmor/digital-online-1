const { chromium } = require("playwright"), fs = require("fs");
(async () => { const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1 });
 for (const [dev, lab] of [["android_360x640", "Android 360×640 (פייסבוק)"], ["iphone_390x664", "iPhone 390×664 (פייסבוק)"], ["iphone_375x560", "iPhone קטן 375×560 (פייסבוק)"]]) {
  const im = n => "data:image/png;base64," + fs.readFileSync(n).toString("base64");
  await p.setContent(`<html dir="rtl"><body style="margin:0;background:#e9ebf1;font-family:Arial;padding:16px"><div style="font:700 22px Arial;margin:0 0 10px">${lab} - המסך הראשון בלי גלילה</div><div style="display:flex;gap:18px;align-items:flex-start">
   <div><div style="font:700 20px Arial;color:#b42318;margin:0 0 6px">לפני (היום)</div><img src="${im("before_" + dev + ".png")}" style="height:900px;border:1px solid #bbb;background:#fff"></div>
   <div><div style="font:700 20px Arial;color:#1f7a4d;margin:0 0 6px">אחרי (ב120)</div><img src="${im("after_" + dev + ".png")}" style="height:900px;border:1px solid #bbb;background:#fff"></div></div></body></html>`);
  await p.waitForTimeout(200); const h = await p.evaluate(() => document.body.scrollHeight), w = await p.evaluate(() => document.body.scrollWidth);
  await p.setViewportSize({ width: w, height: h }); await p.screenshot({ path: `b120_${dev}_before_after.png` }) }
 await b.close() })();
