// ב89 המשך: צילומי ראש דף התשלום במובייל (390x844, x2)
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const UA = { safari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
  ig: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 Instagram 356.0.0.28.109 (iPhone15,2; iOS 18_1; he_IL; he; scale=3.00; 1179x2556; 657224343)' };
(async () => {
  const b = await chromium.launch();
  for (const [ua, q, name, tap] of [['safari', '', 'wt_b_safari', 0], ['safari', '?co=a', 'wt_a_safari', 0], ['ig', '', 'wt_b_ig', 0], ['safari', '', 'wt_b_after_tap', 1]]) {
    const ctx = await b.newContext({ userAgent: UA[ua], viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const p = await ctx.newPage(); await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => r.abort());
    await p.goto(BASE + '/checkout.html' + q, { waitUntil: 'load' }); await p.waitForTimeout(400);
    if (tap) { await p.click('.wt-b[data-w="apple"]'); await p.waitForTimeout(500); }
    await p.screenshot({ path: 'shots/' + name + '.png' }); await ctx.close();
  }
  await b.close(); console.log('done');
})();
