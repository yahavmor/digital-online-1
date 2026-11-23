// ב89: צילומי מסך במובייל (390x844, x2) - ספארי רגיל מול הדפדפן הפנימי של אינסטגרם
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const UA = { safari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
  ig: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 Instagram 356.0.0.28.109 (iPhone15,2; iOS 18_1; he_IL; he; scale=3.00; 1179x2556; 657224343)' };
const J = [ ['checkout.html', '', '[data-paylogos="co_pay"]', 'checkout_b'], ['checkout.html', '?co=a', '[data-paylogos="co_det"]', 'checkout_a'],
  ['checkout_bit.html', '', '[data-paylogos="co_pay"]', 'checkout_b_withbit'],
  ['a5v6.html', '', '[data-paylogos="hero"]', 'a5v6_hero'], ['a5v6.html', '', '[data-paylogos="offer"]', 'a5v6_offer'],
  ['pr2.html', '', '[data-paylogos="hero"]', 'pr2_hero'], ['pr2.html', '', '[data-paylogos="offer"]', 'pr2_offer'] ];
(async () => {
  const b = await chromium.launch();
  for (const ua of ['safari', 'ig']) for (const [pg, q, sel, name] of J) {
    if (ua === 'ig' && /withbit|offer/.test(name)) continue;
    const ctx = await b.newContext({ userAgent: UA[ua], viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const p = await ctx.newPage(); await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => r.abort());
    await p.goto(BASE + '/' + pg + q, { waitUntil: 'load' });
    await p.addStyleTag({ content: '.sticky{display:none!important} *{animation:none!important;transition:none!important} .rv,[data-rv]{opacity:1!important;transform:none!important}' });
    await p.evaluate(s => { const e = document.querySelector(s); const y = e.getBoundingClientRect().top + scrollY - 470; scrollTo(0, Math.max(0, y)); }, sel);
    await p.waitForTimeout(700);
    await p.screenshot({ path: 'shots/' + name + '_' + ua + '.png' });
    await ctx.close();
  }
  await b.close(); console.log('done');
})();
