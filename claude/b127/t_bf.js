// ב127.2: בלאק פריידיי - באנר, ספירה ותיבת מתנה מופיעים רק בחלון (עד 30.11 23:59 ישראל), ונעלמים לבד אחריו; דף התודה: בתקופה בלי אפסייל + הודעת מתנה, אחריה אפסייל כרגיל.
// node t_bf.js <a5s_bf.html> <thanks_bf.html> <assets dir> [shots dir]
const {chromium,devices}=require("playwright"),fs=require("fs");const [A5S,TH,ASSETS,SHOTS]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
const IN=new Date("2026-11-28T10:00:00+02:00"), LAST=new Date("2026-11-30T23:58:30+02:00"), AFTER=new Date("2026-12-01T00:00:30+02:00");
(async()=>{const br=await chromium.launch();
async function page(file,path,at,qs){const c=await br.newContext({...devices["iPhone 13"]});const errs=[],hooks=[],nav=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith(path))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(file,"utf8")});
   const m=u.pathname.match(/assets\/pay\/([a-z-]+\.svg)$/);if(m&&fs.existsSync(ASSETS+"/"+m[1]))return r.fulfill({status:200,contentType:"image/svg+xml",body:fs.readFileSync(ASSETS+"/"+m[1])});
   if(/upsell-97\.html/.test(u.pathname)){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html>UPSELL</html>"})}
   return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";hooks.push({p:u.pathname,b});
   if(u.pathname.includes("s9ay2kp6"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({ok:true,link:"https://app.schooler.biz/x",deal:"271000000",email:"t@example.com"})});
   if(u.pathname.includes("qhq5knj8"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({up:"a".repeat(32)})});
   return r.fulfill({status:200,body:"{}"})}
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.clock.install({time:at});
 await p.goto("https://funnel.digitalonline.co.il/nlp/"+path+(qs||"?claude=b127"),{waitUntil:"load"});await p.clock.runFor(2500);await p.waitForTimeout(300);
 return {c,p,errs,hooks,nav}}
// a5s
{const X=await page(A5S,"a5s.html",IN);const st=await X.p.evaluate(()=>({bar:!document.getElementById("bfBar").hidden,gift:!document.getElementById("bfGift").hidden,cd:document.getElementById("bfCd").textContent,cdHtml:document.getElementById("bfCd").innerHTML,price:document.querySelector(".v4-ko-now b").textContent}));
 ok("בתוך החלון (28.11): הבאנר מוצג",st.bar,st);ok("בתוך החלון: תיבת המתנה הכפולה ליד המחיר מוצגת",st.gift,st);
 ok("ספירה לאחור: 2 ימים ו-13:59:xx (המספרים בתוך bdi)",/^2 ימים ו-13:5[0-9]:\d\d$/.test(st.cd)&&st.cdHtml.includes("<bdi>"),[st.cd,st.cdHtml]);ok("המחיר לא השתנה (297 ₪)",st.price==="297 ₪",st.price);
 const tx=await X.p.evaluate(()=>({bar:document.getElementById("bfBar").textContent,gift:document.getElementById("bfGift").textContent}));
 ok("נוסח הבאנר של יהב",/בלאק פריידיי עד שני 30.11 בחצות/.test(tx.bar)&&/האוטומט החדש שלי/.test(tx.bar)&&/מפגש הטמעה אישי/.test(tx.bar),tx.bar);
 ok("נוסח תיבת המתנה: 2 סעיפים, 97 ₪, המחיר נשאר 297, 7 ימי אחריות",/12 חודשי גישה/.test(tx.gift)&&/97 ₪/.test(tx.gift)&&/המחיר נשאר 297 ₪/.test(tx.gift)&&/7 ימי אחריות/.test(tx.gift)&&(await X.p.$$eval("#bfGift li",l=>l.length))===2,tx.gift);
 ok("בתוך החלון: בלי שגיאות JS",X.errs.length===0,X.errs);
 if(SHOTS){await X.p.screenshot({path:SHOTS+"/bf_a5s_top.png"});const g=await X.p.$("#bfGift");await g.scrollIntoViewIfNeeded();await X.p.waitForTimeout(300);await X.p.screenshot({path:SHOTS+"/bf_a5s_gift.png"});}
 await X.c.close()}
{const X=await page(A5S,"a5s.html",LAST);await X.p.clock.runFor(120000);const st=await X.p.evaluate(()=>({bar:!document.getElementById("bfBar").hidden,gift:!document.getElementById("bfGift").hidden}));
 ok("חזרה אוטומטית: 90 שניות אחרי 23:59 הבאנר והמתנה נעלמים בלי רענון",!st.bar&&!st.gift,st);await X.c.close()}
{const X=await page(A5S,"a5s.html",AFTER);const st=await X.p.evaluate(()=>({bar:!document.getElementById("bfBar").hidden,gift:!document.getElementById("bfGift").hidden}));
 ok("אחרי החלון (1.12): הדף רגיל, בלי באנר ובלי מתנה",!st.bar&&!st.gift,st);ok("אחרי החלון: בלי שגיאות JS",X.errs.length===0,X.errs);await X.c.close()}
// thanks
for(const [label,at,expectBF] of [["בתוך החלון",IN,true],["אחרי החלון",AFTER,false]]){
 const X=await page(TH,"thanks.html",at,"?v=a5s&lowprofilecode=lp-test-1&claude=b127");await X.p.waitForTimeout(600);
 const st=await X.p.evaluate(()=>({go:!document.getElementById("go").hidden,note:!document.getElementById("bfNote").hidden,noteTx:document.getElementById("bfNote").textContent}));
 if(expectBF) ok("thanks: נוסח המתנה של יהב (24 שעות, כשבוע מהיום)",/תוך 24 שעות/.test(st.noteTx)&&/כשבוע מהיום/.test(st.noteTx),st.noteTx);
 await X.p.clock.runFor(4000);await X.p.waitForTimeout(600);
 ok("thanks "+label+": קישור הכניסה לקורס מוצג",st.go,st);
 ok("thanks "+label+": "+(expectBF?"הודעת המתנה מוצגת":"בלי הודעת מתנה"),st.note===expectBF,st);
 ok("thanks "+label+": "+(expectBF?"בלי קריאה לאפסייל ובלי מעבר אליו":"האפסייל כרגיל (קוד הונפק + מעבר)"),expectBF?(!X.hooks.some(h=>h.p.includes("qhq5knj8"))&&X.nav.length===0):(X.hooks.some(h=>h.p.includes("qhq5knj8"))&&X.nav.length===1),{hooks:X.hooks.map(h=>h.p.slice(1,9)),nav:X.nav});
 ok("thanks "+label+": אין קריאה לשרת בשביל הגישה (נפתחת ידנית)",!X.hooks.some(h=>/bf=bf_2611|grant/.test(h.b+h.p)));
 ok("thanks "+label+": בלי שגיאות JS",X.errs.length===0,X.errs);
 if(SHOTS&&expectBF)await X.p.screenshot({path:SHOTS+"/bf_thanks.png"});await X.c.close()}
await br.close();console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)})();
