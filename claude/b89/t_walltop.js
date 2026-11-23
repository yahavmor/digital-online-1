// ב89 המשך: בדיקת Apple Pay ו-Google Pay בראש דף התשלום (A ו-B), לחיצה, ודפדפן של אינסטגרם/פייסבוק.
// שימוש: node t_walltop.js [base=http://127.0.0.1:8789/nlp]
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const UA = {
  safari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
  chrome_and: 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
  ig_ios: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 Instagram 356.0.0.28.109 (iPhone15,2; iOS 18_1; he_IL; he; scale=3.00; 1179x2556; 657224343)',
  fb_ios: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22B83 [FBAN/FBIOS;FBAV/489.0.0.40.104;FBBV/650000000;FBDV/iPhone15,2;FBMD/iPhone;FBSN/iOS;FBSV/18.1;FBSS/3;FBCR/;FBID/phone;FBLC/he_IL;FBOP/5]',
  ig_and: 'Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 Instagram 356.0.0.40.109 Android (34/14; 480dpi; 1080x2340; samsung; SM-S918B; dm3q; qcom; he_IL; 657224343)',
};
const TXT = 'משלמים ב-Apple Pay או ב-Google Pay בלחיצה, אחרי שם, מייל וטלפון';
const H_IOS = 'ל-Apple Pay: לחצו על שלוש הנקודות למעלה ופתחו בספארי', H_AND = 'ל-Google Pay: לחצו על שלוש הנקודות למעלה ופתחו בכרום';
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log('FAIL', m); } };
(async () => {
  const b = await chromium.launch();
  async function open(ua, q) {
    const ctx = await b.newContext({ userAgent: UA[ua], viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); const errs = [], beacons = [];
    p.on('pageerror', e => errs.push(String(e)));
    await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => { const d = r.request().postData() || ''; if (/ev=checkout_wallet_tap/.test(d)) beacons.push(d); r.abort(); });
    await p.goto(BASE + '/checkout.html' + (q || ''), { waitUntil: 'load' });
    await p.waitForTimeout(300);
    return { ctx, p, errs, beacons };
  }
  const state = p => p.evaluate(() => {
    const vis = e => !!(e && !e.hidden && e.offsetParent !== null && getComputedStyle(e).display !== 'none');
    const W = document.getElementById('wallTop'), imgs = [...W.querySelectorAll('.wt-b img')];
    const r = e => e.getBoundingClientRect();
    return { shown: vis(W), row: vis(document.getElementById('wtRow')), t: vis(document.getElementById('wtT')) ? document.getElementById('wtT').textContent : '',
      h: vis(document.getElementById('wtH')) ? document.getElementById('wtH').textContent.replace(/[⁦⁩]/g, '') : '',
      hs: imgs.map(i => Math.round(r(i).height)), loaded: imgs.every(i => i.naturalWidth > 0),
      appleRight: imgs.length === 2 && r(imgs[0]).left > r(imgs[1]).left, alts: imgs.map(i => i.alt),
      aboveFields: r(W).bottom <= r(document.getElementById('fName')).top, inFirstScreen: r(W).bottom <= innerHeight,
      lowerHints: [...document.querySelectorAll('.paylogos .pl-h')].filter(vis).length };
  });
  for (const q of ['', '?co=a']) for (const ua of ['safari', 'chrome_and']) {
    const { ctx, p, errs, beacons } = await open(ua, q);
    const s = await state(p), tag = (q || 'B') + ' ' + ua;
    ok(errs.length === 0, tag + ' errors ' + errs);
    ok(s.shown && s.row && s.t === TXT && s.h === '', tag + ' visible+text ' + JSON.stringify(s));
    ok(s.hs.join() === '44,44' && s.loaded && s.appleRight && s.alts.join() === 'Apple Pay,Google Pay', tag + ' logos ' + JSON.stringify(s));
    ok(s.aboveFields && s.inFirstScreen, tag + ' position ' + JSON.stringify(s));
    for (const w of ['apple', 'google']) {
      await p.evaluate(() => scrollTo(0, 0));
      await p.click('.wt-b[data-w="' + w + '"]');
      await p.waitForTimeout(700);
      const f = await p.evaluate(() => { const e = document.getElementById('fName'), r = e.getBoundingClientRect(); return { focus: document.activeElement === e, flash: e.classList.contains('wt-flash'), inView: r.top >= 0 && r.bottom <= innerHeight }; });
      ok(f.focus && f.flash && f.inView, tag + ' click ' + w + ' ' + JSON.stringify(f));
    }
    ok(beacons.length === 2 && /w%3Dapple/.test(beacons[0]) && /w%3Dgoogle/.test(beacons[1]), tag + ' track ' + beacons.length + ' ' + (beacons[0] || '').slice(0, 120));
    await p.waitForTimeout(1300);
    ok(!(await p.evaluate(() => document.getElementById('fName').classList.contains('wt-flash'))), tag + ' flash removed');
    await ctx.close();
  }
  for (const q of ['', '?co=a']) for (const [ua, hint] of [['ig_ios', H_IOS], ['fb_ios', H_IOS], ['ig_and', H_AND]]) {
    const { ctx, p, errs } = await open(ua, q);
    const s = await state(p), tag = (q || 'B') + ' ' + ua;
    ok(errs.length === 0, tag + ' errors ' + errs);
    ok(s.shown && !s.row && s.t === '' && s.h === hint && s.lowerHints === 0, tag + ' inapp ' + JSON.stringify(s));
    await ctx.close();
  }
  await b.close();
  console.log(pass + '/' + (pass + fail));
  process.exit(fail ? 1 : 0);
})();
