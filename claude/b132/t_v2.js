// ב132: שלד גרסה 2 (a5s2). node t_v2.js <a5s2.html> [shots]
const {chromium,devices}=require("playwright"),fs=require("fs");const [P,SHOTS]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
(async()=>{const br=await chromium.launch();
async function page(){const c=await br.newContext({...devices["iPhone 13"]});const errs=[],hooks=[],track=[],nav=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("a5s2.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(P,"utf8")});
   if(/checkout\.html/.test(u.pathname)){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html>CHECKOUT</html>"})}return r.fulfill({status:204,body:""})}
  if(u.hostname==="secure.cardcom.solutions"){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html>CARDCOM</html>"})}
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";hooks.push({p:u.pathname,b});
   if(u.pathname.includes("axjt5wu2")){track.push(Object.fromEntries(new URLSearchParams(b)));return r.fulfill({status:200,body:"ok"})}
   if(u.pathname.includes("9yp88pz9"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({url:"https://secure.cardcom.solutions/EA/LPC6/201667/00000000-0000-4000-8000-000000000002?t=24",lp:"00000000-0000-4000-8000-000000000002",code:"0"})});
   return r.fulfill({status:200,body:"{}"})}
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.addInitScript(()=>{try{localStorage.setItem("nlp_int","1")}catch(e){}});
 await p.goto("https://funnel.digitalonline.co.il/nlp/a5s2.html?internal=1&claude=b132&utm_source=test&utm_campaign=lenatzeach_w40&utm_content=w2_ben",{waitUntil:"load"});await p.waitForTimeout(1000);
 return {c,p,errs,hooks,track,nav}}
const sent=h=>h.filter(x=>x.p.includes("9yp88pz9")).map(x=>Object.fromEntries(new URLSearchParams(x.b)));
// 1. מבנה
{const X=await page();const st=await X.p.evaluate(()=>({v:document.documentElement.dataset.variant,phones:document.querySelectorAll('input[name="phone"]').length,pay3:[...document.querySelectorAll(".lpf-pay3.v2")].map(e=>e.textContent),guar:[...document.querySelectorAll(".lpf-guar")].map(e=>e.textContent),boxReq:[...document.querySelectorAll('input[name="box"]')].map(b=>b.required),peek:document.getElementById("v2Peek").hidden,ben:document.getElementById("v2Ben").hidden,consent:document.querySelector('[data-v2text="consent"]').textContent}));
 ok("וריאנט a5s2",st.v==="a5s2",st.v);ok("שדה טלפון בשני הטפסים",st.phones===2,st.phones);
 ok("3 תשלומים בולט בשני המקומות",st.pay3.length===2&&/3 תשלומים של 99 ₪/.test(st.pay3[0]),st.pay3);
 ok("אחריות + שורת תנאים צמודות לכפתור בשני הטפסים",st.guar.length===2&&/החזר מלא תוך 7 ימים/.test(st.guar[0])&&/התקנון/.test(st.guar[0]),st.guar);
 ok("התיבה לא חובה ונוסח ההסכמה מכסה מייל ווואטסאפ",st.boxReq.every(b=>!b)&&/וואטסאפ/.test(st.consent),[st.boxReq,st.consent]);
 ok("סלוטי הווידאו מוסתרים כשאין קובץ",st.peek&&st.ben,[st.peek,st.ben]);
 ok("אירוע view עם variant=a5s2",X.track.some(t=>t.ev==="view"&&t.variant==="a5s2"),X.track.filter(t=>t.ev==="view"));
 const f1=await X.p.$('form[data-form="1"]');await f1.scrollIntoViewIfNeeded();await X.p.waitForTimeout(400);
 if(SHOTS)await X.p.screenshot({path:SHOTS+"/v2_form.png"});
 // 2. שליחה בלי תיבה ובלי טלפון - עוברת (הסכמה לא חובה)
 await X.p.fill('form[data-form="1"] input[name="name"]',"בדיקה פנימית");await X.p.fill('form[data-form="1"] input[name="email"]',"t+b132@example.com");
 await X.p.click('form[data-form="1"] button[type="submit"]');await X.p.waitForTimeout(1200);
 const s1=sent(X.hooks);ok("בלי תיבה ובלי טלפון: נשלח להוק עם variant=a5s2, phone ריק, consent 0",s1.length===1&&s1[0].variant==="a5s2"&&s1[0].phone===""&&X.track.some(t=>t.ev==="checkout_details"&&t.lead_consent==="0"),[s1,X.track.filter(t=>t.ev==="checkout_details").map(t=>t.lead_consent)]);
 ok("הפניה לקארדקום",X.nav.some(u=>/cardcom/.test(u)),X.nav);ok("בלי שגיאות JS",X.errs.length===0,X.errs);await X.c.close()}
// 3. טלפון לא תקין חוסם, טלפון תקין נשלח מנורמל, תיבה מסומנת -> consent 1
{const X=await page();await X.p.fill('form[data-form="2"] input[name="name"]',"בדיקה פנימית");await X.p.fill('form[data-form="2"] input[name="email"]',"t+b132@example.com");
 await X.p.fill('form[data-form="2"] input[name="phone"]',"0501");await X.p.click('form[data-form="2"] button[type="submit"]');await X.p.waitForTimeout(400);
 const err=await X.p.evaluate(()=>document.querySelector('form[data-form="2"] .lpf-err').textContent);
 ok("טלפון קצר: הודעת שגיאה ובלי שליחה",/טלפון/.test(err)&&sent(X.hooks).length===0,[err,sent(X.hooks).length]);
 ok("form_error עם phone",X.track.some(t=>t.ev==="form_error"&&/phone/.test(t.name)),X.track.filter(t=>t.ev==="form_error"));
 await X.p.fill('form[data-form="2"] input[name="phone"]',"+972 50-123 4567");await X.p.check('form[data-form="2"] input[name="box"]');await X.p.click('form[data-form="2"] button[type="submit"]');await X.p.waitForTimeout(1200);
 const s2=sent(X.hooks);ok("טלפון תקין: נשלח 0501234567, consent 1, lead_phone באירוע",s2.length===1&&s2[0].phone==="0501234567"&&X.track.some(t=>t.ev==="checkout_details"&&t.lead_consent==="1"&&t.lead_phone==="0501234567"),[s2.map(s=>s.phone),X.track.filter(t=>t.ev==="checkout_details")]);
 ok("בלי שגיאות JS (2)",X.errs.length===0,X.errs);await X.c.close()}
await br.close();console.log(`\n${n-f}/${n} passed`);process.exit(f?1:0)})();
