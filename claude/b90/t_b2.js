// ב90: בדיקת B2 מול B בדף התשלום - תצוגה, סימון באירועים, co שנשלח ל-Make, הגרלה חצי-חצי ונשמרת.
// שימוש: node t_b2.js [base=http://127.0.0.1:8789/nlp]
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8789/nlp';
const UA = { safari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
  fb_and: 'Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/489.0.0.40.104;]' };
const CHK = 'https://hook.eu1.make.com/9yp88pz9bfvxbr7w6xkb4ckun82ote6a', TRK = 'https://hook.eu1.make.com/axjt5wu2oh5vf4zz9uut24s1m79ot6jc';
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) pass++; else { fail++; console.log('FAIL', m); } };
(async () => {
  const b = await chromium.launch();
  async function open(q, ua, ctxIn) {
    const ctx = ctxIn || await b.newContext({ userAgent: UA[ua || 'safari'], viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); const errs = [], trk = [], chk = [];
    p.on('pageerror', e => errs.push(String(e)));
    await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => { const u = r.request().url(), d = r.request().postData() || '';
      if (u.startsWith(TRK)) trk.push(new URLSearchParams(d)); if (u.startsWith(CHK)) { chk.push(new URLSearchParams(d)); return r.fulfill({ status: 200, contentType: 'application/json', body: '{"url":"about:blank"}' }); }
      r.abort(); });
    await p.goto(BASE + '/checkout.html' + (q || ''), { waitUntil: 'load' }); await p.waitForTimeout(400);
    return { ctx, p, errs, trk, chk };
  }
  const view = p => p.evaluate(() => {
    const vis = e => !!(e && e.offsetParent !== null && getComputedStyle(e).display !== 'none'), q = s => document.querySelector(s), T = e => e.innerText.replace(/\s+/g, ' ').trim();
    return { co: document.documentElement.dataset.co, co2: document.documentElement.getAttribute('data-co2'), NLP_CO: window.NLP_CO,
      launch: vis(q('.b2-launch')), was: vis(q('.price s.was')), guar: vis(q('.b2-guar')) ? T(q('.b2-guar')) : '',
      h2: T(q('#det').closest('section').querySelector('h2')), pt: T(q('.paytitle')), how: T([...document.querySelectorAll('.deal dd')].find(d => /חד-פעמי/.test(d.textContent))),
      ac: ['fName', 'fEmail', 'fPhone'].map(i => q('#' + i).getAttribute('autocomplete')).join(','),
      priceOrder: [...q('.price').children].filter(vis).map(e => e.tagName).join(','),
      wasRight: vis(q('.price s.was')) ? q('.price s.was').getBoundingClientRect().left > q('.price b').getBoundingClientRect().left : null,
      guarBelowPrice: vis(q('.b2-guar')) ? q('.b2-guar').getBoundingClientRect().top >= q('.price').getBoundingClientRect().bottom : null };
  });
  const GUAR = '7 ימי אחריות: אם הקורס לא מתאים לך, שולחים מייל ומקבלים החזר מלא.';
  // B
  { const { ctx, p, errs, trk } = await open('?co=b'); const v = await view(p);
    ok(!errs.length, 'B errors ' + errs);
    ok(v.co === 'b' && v.co2 === '0' && !v.launch && !v.was && !v.guar, 'B no B2 elements ' + JSON.stringify(v));
    ok(v.h2 === 'הפרטים שלך' && /^פרטי תשלום/.test(v.pt) && /^תשלום חד-פעמי בכרטיס אשראי\. ללא מנוי/.test(v.how), 'B texts ' + JSON.stringify(v));
    ok(v.ac === 'name,email,tel', 'B autocomplete ' + v.ac);
    const x = trk.map(f => f.get('x') || ''); ok(x.length > 0 && x.every(s => /(^|;)co=b(;|$)/.test(s) && /cx=co_b2_1311/.test(s)), 'B events co=b ' + x.slice(0, 2));
    await ctx.close(); }
  // B2 + מילוי עד טעינת התשלום: ל-Make נשלח co=b
  { const { ctx, p, errs, trk, chk } = await open('?co=b2'); const v = await view(p);
    ok(!errs.length, 'B2 errors ' + errs);
    ok(v.co === 'b' && v.co2 === '1' && v.NLP_CO === 'b2', 'B2 flags ' + JSON.stringify(v));
    ok(v.launch && v.was && v.guar === GUAR && v.wasRight && v.guarBelowPrice, 'B2 price anchor + guarantee ' + JSON.stringify(v));
    ok(v.h2 === 'שלב 1 מתוך 2: הפרטים שלך', 'B2 step1 ' + v.h2);
    ok(/^שלב 2 מתוך 2: תשלום/.test(v.pt) && !/פרטי תשלום/.test(v.pt), 'B2 step2 ' + v.pt);
    ok(/^תשלום חד-פעמי באשראי, Apple Pay או Google Pay\. ללא מנוי/.test(v.how.replace(/[⁦⁩]/g, '')), 'B2 deal ' + v.how);
    ok(v.ac === 'name,email,tel', 'B2 autocomplete');
    await p.fill('#fName', 'בדיקה ישראלי'); await p.fill('#fEmail', 'b2.check@example.com'); await p.fill('#fPhone', '0501234567');
    await p.check('#fTerms'); await p.waitForTimeout(2500);
    ok(chk.length >= 1 && chk[0].get('co') === 'b', 'B2 Make co=b ' + (chk[0] && chk[0].get('co')));
    const x = trk.map(f => f.get('x') || ''); ok(x.length > 2 && x.every(s => /(^|;)co=b2(;|$)/.test(s) && /cx=co_b2_1311/.test(s)), 'B2 events co=b2 ' + x.slice(0, 2));
    ok(trk.some(f => f.get('ev') === 'checkout_contact_started') && trk.some(f => f.get('ev') === 'checkout_details'), 'B2 funnel events ' + trk.map(f => f.get('ev')).join());
    await ctx.close(); }
  // B2 עם ביט
  { const ctx = await b.newContext({ userAgent: UA.safari, viewport: { width: 390, height: 844 } }); const p = await ctx.newPage();
    await p.route(/^(?!http:\/\/127\.0\.0\.1)/, r => r.abort()); await p.goto(BASE + '/checkout_bit.html?co=b2', { waitUntil: 'load' }); await p.waitForTimeout(300);
    const how = await p.evaluate(() => [...document.querySelectorAll('.deal dd')].find(d => /חד-פעמי/.test(d.textContent)).innerText.replace(/[⁦⁩]/g, ''));
    ok(/^תשלום חד-פעמי באשראי, Apple Pay, Google Pay או ביט\./.test(how), 'B2 deal with bit ' + how); await ctx.close(); }
  // A נשאר A
  { const { ctx, p } = await open('?co=a'); const v = await view(p); ok(v.co === 'a' && v.co2 === '0' && !v.launch, 'A untouched ' + JSON.stringify(v)); await ctx.close(); }
  // דפדפן של פייסבוק באנדרואיד ב-B2: רמז, בלי שגיאות
  { const { ctx, p, errs } = await open('?co=b2', 'fb_and'); const h = await p.evaluate(() => document.getElementById('wtH').hidden ? '' : document.getElementById('wtH').textContent.replace(/[⁦⁩]/g, ''));
    ok(!errs.length && h === 'ל-Google Pay: לחצו על שלוש הנקודות למעלה ופתחו בכרום', 'B2 FB android hint ' + h + errs); await ctx.close(); }
  // הגרלה: בלי co בכתובת - נשמרת במכשיר, ושתי הזרועות מופיעות
  { const ctx = await b.newContext({ userAgent: UA.safari }); const r1 = await open('', 'safari', ctx), first = await r1.p.evaluate(() => window.NLP_CO);
    const r2 = await open('?utm_source=fb', 'safari', ctx), second = await r2.p.evaluate(() => window.NLP_CO);
    ok((first === 'b' || first === 'b2') && first === second, 'sticky ' + first + ' ' + second);
    const x = r2.trk.map(f => f.get('x') || ''); ok(x.every(s => s.includes('co=' + first + ';')), 'sticky events co=' + first);
    // התפלגות: מריצים את סקריפט ההגרלה 4000 פעמים עם אחסון ריק
    const dist = await r2.p.evaluate(() => { const src = [...document.scripts].find(s => s.text.includes('co_b2_1311') && s.text.includes('Math.random')).text.replace(/<\/?script>/g, '');
      const c = { b: 0, b2: 0 }; history.replaceState(null, '', location.pathname); for (let i = 0; i < 4000; i++) { localStorage.removeItem('nlp_co_b2'); new Function(src)(); c[window.NLP_CO]++; } return c; });
    ok(dist.b > 1850 && dist.b2 > 1850, 'split 50/50 ' + JSON.stringify(dist));
    await ctx.close(); }
  // כתובת עם co=b2 לא משנה את ההגרלה השמורה של המכשיר
  { const ctx = await b.newContext({ userAgent: UA.safari }); const r1 = await open('?co=b2', 'safari', ctx); const st = await r1.p.evaluate(() => localStorage.getItem('nlp_co_b2'));
    ok(st === null, 'forced co does not store ' + st); await ctx.close(); }
  await b.close();
  console.log(pass + '/' + (pass + fail)); process.exit(fail ? 1 : 0);
})();
