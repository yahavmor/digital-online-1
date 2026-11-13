// ב90: צילומי B2 (ו-B להשוואה) בטלפון - אייפון ואנדרואיד, דפדפן רגיל ודפדפן של פייסבוק
const { chromium, devices } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const FB_IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 [FBAN/FBIOS;FBAV/489.0.0.40.104;FBBV/650000000;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/18.1;FBSS/3;FBCR/;FBID/phone;FBLC/he_IL;FBOP/5]';
const FB_AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 7 Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/489.0.0.40.104;]';
const RUNS = [['iphone', devices['iPhone 13'], null], ['android', devices['Pixel 7'], null], ['iphone_fb', devices['iPhone 13'], FB_IOS], ['android_fb', devices['Pixel 7'], FB_AND]];
(async () => {
  const b = await chromium.launch();
  for (const [name, dev, ua] of RUNS) for (const co of ['b2', 'b']) {
    if (co === 'b' && name !== 'iphone') continue;
    const ctx = await b.newContext(Object.assign({}, dev, ua ? { userAgent: ua } : {}, { reducedMotion: 'reduce', locale: 'he-IL' }));
    const p = await ctx.newPage(); await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => r.abort());
    await p.goto(BASE + '/checkout.html?co=' + co, { waitUntil: 'load' }); await p.waitForTimeout(500);
    await p.screenshot({ path: `shots/${co}_${name}_1_top.png` });
    if (co === 'b2') {
      await p.evaluate(() => { const e = document.querySelector('#det').closest('section'); scrollTo(0, e.getBoundingClientRect().top + scrollY - 10); }); await p.waitForTimeout(300);
      await p.screenshot({ path: `shots/${co}_${name}_2_step1.png` });
      await p.evaluate(() => { const e = document.querySelector('.paytitle'); scrollTo(0, e.getBoundingClientRect().top + scrollY - 220); }); await p.waitForTimeout(300);
      await p.screenshot({ path: `shots/${co}_${name}_3_step2.png` });
      if (name === 'iphone') { await p.evaluate(() => { const e = document.querySelector('.deal'); scrollTo(0, e.getBoundingClientRect().top + scrollY - 10); }); await p.waitForTimeout(300); await p.screenshot({ path: `shots/${co}_${name}_4_deal.png` }); }
    }
    await ctx.close();
  }
  await b.close(); console.log('done');
})();
