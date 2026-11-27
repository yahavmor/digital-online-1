// ב130: בדיקת זרימה בנייד בדף a5s החי (עותק זהה ל-main) עם internal=1 עד ההפניה לדף התשלום, בלי לשלם. ההוק של הסליקה מדומה.
const {chromium,devices}=require("playwright"),fs=require("fs");const [A5S,SHOTS]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
const FBUA="Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/490.0.0.0;]";
(async()=>{const br=await chromium.launch();
async function run(label,ctxOpts,hookMode){
 const c=await br.newContext(ctxOpts);const errs=[],hooks=[],track=[],nav=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("a5s.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(A5S,"utf8")});
   if(/checkout\.html/.test(u.pathname)){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html>CHECKOUT</html>"})}
   return r.fulfill({status:204,body:""})}
  if(u.hostname==="secure.cardcom.solutions"){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html>CARDCOM</html>"})}
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";hooks.push({p:u.pathname,b});
   if(u.pathname.includes("axjt5wu2")){track.push(Object.fromEntries(new URLSearchParams(b)));return r.fulfill({status:200,body:"ok"})}
   if(u.pathname.includes("9yp88pz9")){ if(hookMode==="timeout") return; /* לא עונים */
     return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({url:"https://secure.cardcom.solutions/EA/LPC6/201667/00000000-0000-4000-8000-000000000001?t=24",lp:"00000000-0000-4000-8000-000000000001",code:"0"})})}
   return r.fulfill({status:200,body:"{}"})}
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.addInitScript(()=>{try{localStorage.setItem("nlp_int","1")}catch(e){}});
 await p.goto("https://funnel.digitalonline.co.il/nlp/a5s.html?internal=1&claude=b130&utm_source=test&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben",{waitUntil:"load"});
 await p.waitForTimeout(1200);
 const forms=await p.evaluate(()=>[...document.querySelectorAll("form[data-form]")].map(f=>({n:f.dataset.form,fields:[...f.querySelectorAll("input,button")].map(i=>i.name||i.type),hidden:f.closest("[hidden]")!==null})));
 ok(label+": יש טפסים בדף (שם, מייל, תיבה, כפתור)",forms.length>=1&&forms[0].fields.join(",").includes("name")&&forms[0].fields.join(",").includes("email"),forms);
 // גלילה לטופס הראשון
 const f1=await p.$('form[data-form="1"]');await f1.scrollIntoViewIfNeeded();await p.waitForTimeout(900);
 const opened=track.filter(t=>t.ev==="form_open");ok(label+": נשלח form_open כשהטופס נכנס למסך (בלי לחיצה)",opened.length>=1&&/int=1/.test(opened[0].x||""),opened);
 if(SHOTS)await p.screenshot({path:SHOTS+"/flow_"+label+"_form.png"});
 // מקלידים
 await p.focus('form[data-form="1"] input[name="name"]');await p.waitForTimeout(300);
 ok(label+": נשלח form_start בפוקוס על השדה",track.some(t=>t.ev==="form_start"),track.map(t=>t.ev));
 await p.fill('form[data-form="1"] input[name="name"]',"בדיקה פנימית");await p.fill('form[data-form="1"] input[name="email"]',"test+b130@example.com");
 // שליחה בלי תיבה
 await p.click('form[data-form="1"] button[type="submit"]');await p.waitForTimeout(400);
 const err1=await p.evaluate(()=>document.querySelector('form[data-form="1"] .lpf-err').textContent);
 ok(label+": בלי סימון התיבה - הודעה 'חסר: סימון התיבה' ואין שליחה",/סימון התיבה/.test(err1)&&!hooks.some(h=>h.p.includes("9yp88pz9")),[err1,hooks.filter(h=>h.p.includes("9yp88pz9")).length]);
 ok(label+": נשלח form_error עם name=box",track.some(t=>t.ev==="form_error"&&/box/.test(t.name)),track.filter(t=>t.ev==="form_error"));
 if(SHOTS)await p.screenshot({path:SHOTS+"/flow_"+label+"_err.png"});
 // מסמנים ושולחים
 await p.check('form[data-form="1"] input[name="box"]');await p.click('form[data-form="1"] button[type="submit"]');
 await p.waitForTimeout(hookMode==="timeout"?16000:1500);
 const sent=hooks.filter(h=>h.p.includes("9yp88pz9")).map(h=>{try{return Object.fromEntries(new URLSearchParams(h.b))}catch(e){return h.b}});
 ok(label+": נשלח להוק הסליקה עם variant=a5s, שם, מייל, test/internal",sent.length===1&&sent[0].variant==="a5s"&&sent[0].email==="test+b130@example.com"&&(sent[0].test==="1"||sent[0].internal==="1"||/int/.test(JSON.stringify(sent[0]))),sent.map(s=>Object.keys(s).join(",")+" test="+s.test+" phone="+JSON.stringify(s.phone)));
 ok(label+": נשלחו form_submit ו-checkout_pay_redirect",track.some(t=>t.ev==="form_submit")&&(hookMode==="timeout"||track.some(t=>t.ev==="checkout_pay_redirect")),track.map(t=>t.ev));
 if(hookMode==="timeout") ok(label+": ההוק לא ענה - נפילה ל-checkout.html",nav.some(u=>/checkout\.html/.test(u))&&track.some(t=>t.ev==="checkout_load_error"),nav);
 else ok(label+": הדפדפן הופנה לדף התשלום של קארדקום",nav.some(u=>/secure\.cardcom\.solutions\/EA\/LPC6/.test(u)),nav);
 ok(label+": בלי שגיאות JS בדף",errs.length===0,errs);
 await c.close()}
await run("iphone",{...devices["iPhone 13"]});
await run("android_fb",{...devices["Pixel 7"],userAgent:FBUA});
await run("iphone_hook_timeout",{...devices["iPhone 13"]},"timeout");
await br.close();console.log(`\n${n-f}/${n} passed`);process.exit(f?1:0)})();
