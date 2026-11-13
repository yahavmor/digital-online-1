// ב89: בדיקת שורת אמצעי התשלום בשלושת הדפים, בספארי/כרום רגיל ובדפדפן הפנימי של אינסטגרם/פייסבוק.
// שימוש: node t_paylogos.js [base=http://127.0.0.1:8789/nlp]
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const UA = {
  safari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
  ig_ios: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 Instagram 356.0.0.28.109 (iPhone15,2; iOS 18_1; he_IL; he; scale=3.00; 1179x2556; 657224343)',
  fb_ios: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 [FBAN/FBIOS;FBAV/489.0.0.40.104;FBBV/650000000;FBDV/iPhone15,2;FBMD/iPhone;FBSN/iOS;FBSV/18.1;FBSS/3;FBCR/;FBID/phone;FBLC/he_IL;FBOP/5]',
  chrome_and: 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
  ig_and: 'Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 Instagram 356.0.0.40.109 Android (34/14; 480dpi; 1080x2340; samsung; SM-S918B; dm3q; qcom; he_IL; 657224343)',
};
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log('FAIL', m); } };
(async () => {
  const b = await chromium.launch();
  async function probe(page, ua, q) {
    const ctx = await b.newContext({ userAgent: UA[ua], viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(String(e)));
    await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => r.abort());
    await p.goto(BASE + '/' + page + (q || ''), { waitUntil: 'load' });
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => [...document.querySelectorAll('[data-paylogos]')].map(el => {
      const vis = e => !!(e && e.offsetParent !== null && getComputedStyle(e).display !== 'none');
      const li = k => el.querySelector('[data-pl="' + k + '"]');
      return { where: el.dataset.paylogos, shown: vis(el), apple: vis(li('apple')), google: vis(li('google')), bit: vis(li('bit')), card: vis(li('card')),
        t: el.querySelector('.pl-t').textContent.replace(/[\u2066\u2069]/g, ''), h: el.querySelector('.pl-h').hidden ? '' : el.querySelector('.pl-h').textContent.replace(/[\u2066\u2069]/g, ''),
        imgs: [...el.querySelectorAll('img')].filter(i => vis(i)).map(i => i.naturalWidth > 0 && Math.round(i.getBoundingClientRect().height)) };
    }));
    await ctx.close();
    return { r, errs };
  }
  const FULL = 'אפשר לשלם ב-Apple Pay, Google Pay או אשראי';
  for (const page of ['a5v6.html', 'pr2.html']) {
    for (const ua of ['safari', 'chrome_and']) {
      const { r, errs } = await probe(page, ua);
      ok(errs.length === 0, page + ' ' + ua + ' errors ' + errs);
      ok(r.length === 2 && r.map(x => x.where).join() === 'hero,offer', page + ' places ' + JSON.stringify(r.map(x => x.where)));
      r.forEach(x => { ok(x.shown && x.apple && x.google && !x.bit && x.card, page + ' ' + ua + ' ' + x.where + ' logos ' + JSON.stringify(x));
        ok(x.t === FULL && x.h === '', page + ' ' + ua + ' text ' + x.t + '|' + x.h); });
    }
    for (const [ua, hint] of [['ig_ios', ''], ['fb_ios', ''], ['ig_and', '']]) {
      const { r } = await probe(page, ua);
      r.forEach(x => { ok(!x.apple && !x.google && !x.bit && x.card, page + ' ' + ua + ' ' + x.where + ' inapp logos');
        ok(x.t === 'אפשר לשלם באשראי' && x.h === hint, page + ' ' + ua + ' inapp text ' + x.t + '|' + x.h); });
    }
  }
  // דף התשלום: ב' (ברירת מחדל) - בראש פרטי תשלום; א' - מעל כפתור ההמשך
  {
    const { r, errs } = await probe('checkout.html', 'safari');
    ok(errs.length === 0, 'checkout errors ' + errs);
    const v = Object.fromEntries(r.map(x => [x.where, x]));
    ok(v.co_pay && v.co_pay.shown && !v.co_det.shown, 'checkout B: row in pay section only ' + JSON.stringify(r.map(x => [x.where, x.shown])));
    ok(v.co_pay.apple && v.co_pay.google && !v.co_pay.bit && v.co_pay.card && v.co_pay.t === FULL, 'checkout B logos');
    ok(v.co_pay.imgs.every(h => h === 26), 'checkout B heights ' + v.co_pay.imgs);
  }
  {
    const { r } = await probe('checkout.html', 'safari', '?co=a');
    const v = Object.fromEntries(r.map(x => [x.where, x]));
    ok(v.co_det.shown && !v.co_pay.shown, 'checkout A: row above continue button ' + JSON.stringify(r.map(x => [x.where, x.shown])));
  }
  {
    const { r } = await probe('checkout.html', 'ig_ios');
    const v = Object.fromEntries(r.map(x => [x.where, x]));
    ok(!v.co_pay.apple && !v.co_pay.google && v.co_pay.h === 'ל-Apple Pay: לחצו על שלוש הנקודות למעלה ופתחו בספארי', 'checkout IG hint ' + v.co_pay.h);
    const { r: ra } = await probe('checkout.html', 'ig_and');
    const va = Object.fromEntries(ra.map(x => [x.where, x]));
    ok(!va.co_pay.apple && !va.co_pay.google && va.co_pay.h === 'ל-Google Pay: לחצו על שלוש הנקודות למעלה ופתחו בכרום', 'checkout IG android hint ' + va.co_pay.h);
    const { r: rf } = await probe('checkout.html', 'fb_ios', '?co=a');
    const vf = Object.fromEntries(rf.map(x => [x.where, x]));
    ok(vf.co_det.shown && !vf.co_det.apple && vf.co_det.h === 'ל-Apple Pay: לחצו על שלוש הנקודות למעלה ופתחו בספארי', 'checkout A FB hint ' + vf.co_det.h);
  }
  {
    const { r } = await probe('checkout_bit.html', 'safari');
    const v = Object.fromEntries(r.map(x => [x.where, x]));
    ok(v.co_pay.bit && v.co_pay.t === 'אפשר לשלם ב-Apple Pay, Google Pay, ביט או אשראי', 'checkout with PAYLOGO_BIT=true ' + v.co_pay.t);
    const { r: r2 } = await probe('checkout_bit.html', 'ig_ios');
    const w = Object.fromEntries(r2.map(x => [x.where, x]));
    ok(w.co_pay.bit && w.co_pay.t === 'אפשר לשלם בביט או באשראי', 'checkout bit+IG text ' + w.co_pay.t);
  }
  await b.close();
  console.log(pass + '/' + (pass + fail));
  process.exit(fail ? 1 : 0);
})();
