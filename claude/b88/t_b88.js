// ב41/ב62 + ביט: בדיקה מקומית של checkout.html. Make וקארדקום מדומים - שום בקשה לא יוצאת.
// node t_b88.js <checkout מקורי> <אחרי patch_wallet> <אחרי patch_bit> <אחרי שניהם> <תיקיית צילומים>
const {chromium,devices}=require("playwright"),fs=require("fs");
const [ORIG,W,B,WB]=process.argv.slice(2,6).map(f=>fs.readFileSync(f,"utf8")),OUT=process.argv[6];
const BIT="https://secure.cardcom.solutions/api/LPC5/Bit?lpc=lp123";
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const br=await chromium.launch();
const run=async(html,{co,bit,qs,shot})=>{const c=await br.newContext({...devices["iPhone 13"],viewport:{width:390,height:844}});const T=[],nav=[],errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"&&u.pathname.endsWith("/checkout.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:html});
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";if(/ev=/.test(b)){T.push(decodeURIComponent(b));return r.fulfill({status:200,body:"Accepted"})}
   return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify(Object.assign({code:"0",url:"https://secure.cardcom.solutions/EA/mock?lp=lp123",lp:"lp123"},bit?{bit_url:bit}:{}))})}
  if(u.hostname.endsWith("cardcom.solutions")){nav.push(u.href);return r.fulfill({status:200,contentType:"text/html",body:"<html><body style='font:20px sans-serif;padding:20px'>Cardcom mock "+u.pathname+"</body></html>"})}
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("https://funnel.digitalonline.co.il/nlp/checkout.html?v=a5v6&co="+co+"&claude=b88"+(qs||""),{waitUntil:"load"});await p.waitForTimeout(800);
 return {c,p,T,nav,errs}};
const fillGo=async p=>{await p.fill("#fName","בדיקה ב88");await p.fill("#fEmail","b88@example.com");await p.fill("#fPhone","0501234567");await p.check("#fTerms");
 const sub=p.locator('#det button[type="submit"]:visible');if(await sub.count())await sub.first().click();await p.waitForTimeout(1500)};
const vis=(p,id)=>p.evaluate(i=>{const e=document.getElementById(i);return !!e&&!e.hidden&&!!e.offsetParent},id);
for(const co of ["a","b"]){
 // ביט
 {const X=await run(B,{co,bit:BIT});await fillGo(X.p);
  ok(co+": Bit button shown after the box is ticked and bit_url exists",await vis(X.p,"bitWrap"));
  ok(co+": Bit link = bit_url",(await X.p.getAttribute("#bitBtn","href"))===BIT);
  ok(co+": card iframe still loads as before",await X.p.evaluate(()=>!document.getElementById("cc").hidden&&/cardcom/.test(document.getElementById("cc").src)));
  await X.p.screenshot({path:OUT+"/b88_bit_"+co+".png",fullPage:false});
  await X.p.screenshot({path:OUT+"/b88_bit_"+co+"_full.png",fullPage:true});
  await X.p.uncheck("#fTerms");await X.p.waitForTimeout(600);
  ok(co+": unticking hides the Bit button (with the payment form)",!(await vis(X.p,"bitWrap")),await X.p.evaluate(()=>document.getElementById("bitWrap").hidden));
  await X.p.check("#fTerms");await X.p.waitForTimeout(1500);
  ok(co+": ticking again shows it again",await vis(X.p,"bitWrap"));
  await Promise.all([X.p.waitForURL(/LPC5\/Bit/,{timeout:8000}),X.p.click("#bitBtn")]);await X.p.waitForTimeout(400);
  ok(co+": click goes to Cardcom's Bit page in the same window",/secure\.cardcom\.solutions\/api\/LPC5\/Bit/.test(X.p.url()),X.p.url());
  ok(co+": checkout_bit_click event sent",X.T.some(t=>/ev=checkout_bit_click/.test(t)));
  ok(co+": no JS errors (Bit)",!X.errs.length,X.errs.join("|"));await X.c.close()}
 {const X=await run(B,{co,bit:null});await fillGo(X.p);
  ok(co+": no bit_url → no Bit button",!(await vis(X.p,"bitWrap")));await X.c.close()}
 {const X=await run(B,{co,bit:"https://evil.example.com/Bit"});await fillGo(X.p);
  ok(co+": non-Cardcom bit_url is ignored",!(await vis(X.p,"bitWrap")));await X.c.close()}
 {const X=await run(B,{co,bit:BIT});await X.p.fill("#fName","בדיקה");await X.p.fill("#fEmail","b88@example.com");await X.p.fill("#fPhone","0501234567");
  const sub=X.p.locator('#det button[type="submit"]:visible');if(await sub.count())await sub.first().click({force:true});await X.p.waitForTimeout(1200);
  ok(co+": box not ticked → no Bit button",!(await vis(X.p,"bitWrap")));await X.c.close()}
 // ארנק
 {const O=await run(ORIG,{co}),X=await run(W,{co});
  ok(co+": before: fixed wallet note exists",/Apple Pay ו-Google Pay לא זמינים/.test(await O.p.content()));
  ok(co+": after: no fixed wallet note",!/לא זמינים/.test(await X.p.evaluate(()=>document.body.innerText))&&!(await X.p.$("#walNote")));
  await O.c.close();await X.c.close()}
 {const X=await run(W,{co,qs:"&status=failed&ResponseCode=60000303"});await fillGo(X.p);const t=await X.p.innerText("#err");
  ok(co+": decline 60000303 → general message, no wallet wording",/לא בוצע חיוב/.test(t)&&!/Apple Pay|Google Pay|ארנק/.test(t),t);
  await X.p.screenshot({path:OUT+"/b88_fail_60000303_"+co+".png",fullPage:false});await X.c.close()}
 {const X=await run(W,{co,qs:"&status=failed&ResponseCode=33"});await fillGo(X.p);const t=await X.p.innerText("#err");
  ok(co+": other decline → same general message, without the wallet line",/לא בוצע חיוב\. אפשר לנסות שוב/.test(t)&&!/ארנק|Apple/.test(t),t);await X.c.close()}
 {const X=await run(WB,{co,bit:BIT});await fillGo(X.p);
  ok(co+": both patches together: Bit button + no wallet note, no JS errors",await vis(X.p,"bitWrap")&&!(await X.p.$("#walNote"))&&!X.errs.length);await X.c.close()}
}
// בלי bit_url: הדף אחרי patch_bit זהה בתצוגה למקור
{const O=await run(ORIG,{co:"b"}),X=await run(B,{co:"b"});for(const Y of [O,X])await fillGo(Y.p);
 const g=Y=>Y.p.evaluate(()=>document.body.innerText);ok("without bit_url: visible text identical to the original",(await g(O))===(await g(X)));await O.c.close();await X.c.close()}
console.log("TOTAL",n-f+"/"+n);await br.close();process.exit(f?1:0)})();
