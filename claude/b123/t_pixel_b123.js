// ב123: landing_option2 עם ?marketer=karlen טוען את הפיקסל של קרלין (מ-marketers.json), ושליחת הטופס שולחת Lead אליו. הכול מדומה, שום בקשה לא יוצאת.
// node t_pixel_b123.js <landing_option2.html> <pixels.js> <marketers.json>
const {chromium,devices}=require("playwright"),fs=require("fs");const [LP,PX,MJ]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
(async()=>{const br=await chromium.launch();
const run=async(qs)=>{const c=await br.newContext({...devices["iPhone 13"]});const hooks=[],errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){
   if(u.pathname.endsWith("/landing_option2.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(LP,"utf8")});
   if(u.pathname==="/shared/pixels.js")return r.fulfill({status:200,contentType:"text/javascript",body:fs.readFileSync(PX,"utf8")});
   if(/^\/shared\/(params|countdown)\.js$/.test(u.pathname))return r.fulfill({status:200,contentType:"text/javascript",body:fs.readFileSync(require("path").dirname(PX)+"/"+u.pathname.split("/").pop(),"utf8")});
   if(u.pathname==="/marketers/marketers.json")return r.fulfill({status:200,contentType:"application/json",body:fs.readFileSync(MJ,"utf8")});
   if(/\.js$/.test(u.pathname))return r.fulfill({status:200,contentType:"text/javascript",body:""});
   return r.fulfill({status:200,contentType:"text/html",body:"<html>stub</html>"})}
  if(u.hostname==="connect.facebook.net")return r.fulfill({status:200,contentType:"text/javascript",body:"/* fbevents stub: calls stay in fbq.queue */"});
  if(/googletagmanager|google-analytics|clarity|fonts\.g/.test(u.hostname))return r.fulfill({status:200,contentType:"text/javascript",body:""});
  if(u.hostname.endsWith("make.com")){hooks.push({path:u.pathname,body:r.request().postData()||""});return r.fulfill({status:200,contentType:"application/json",body:"{}"})}
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("https://funnel.digitalonline.co.il/landing-pages/landing_option2.html?"+qs,{waitUntil:"load"});await p.waitForTimeout(1200);
 return {c,p,hooks,errs}};
const calls=p=>p.evaluate(()=>Array.from((window.fbq&&window.fbq.queue)||[]).map(x=>[].slice.call(x).map(String).join(":")));
for(const [qs,pix,label] of [["marketer=karlen","1653243919627695","karlen -> קרלין"],["marketer=rachel","2599105640487498","rachel (ללא שינוי)"],["","2401943686950969","בלי משווק -> yahav"]]){
 const X=await run(qs);const c0=await calls(X.p);
 ok(label+": pixel init "+pix,c0.some(x=>x==="init:"+pix),c0);
 /* הדף קורא ל-loadFacebookPixel פעמיים (pixels.js וגם שורה 371 בדף, מלפני ב123) - לכן init פעמיים, תמיד אותו פיקסל */
 ok(label+": every init is the same pixel (no other pixel)",c0.filter(x=>/^init:/.test(x)).every(x=>x==="init:"+pix),c0);
 ok(label+": PageView sent",c0.some(x=>x==="track:PageView"),c0);
 if(qs){await X.p.evaluate(()=>openPopup());await X.p.waitForTimeout(300);
  await X.p.fill("#fName","בדיקה ב123");await X.p.fill("#fPhone","0501234567");await X.p.fill("#fEmail","b123@example.com");await X.p.check("#legalBox");
  const rec=[];await X.p.exposeFunction("__rec",x=>rec.push(x));
  await X.p.evaluate(()=>{const o=window.fbq;window.fbq=function(){window.__rec([].slice.call(arguments).map(String).join(":"));return o.apply(this,arguments)}});
  await X.p.evaluate(()=>submitForm());await X.p.waitForTimeout(1500);const c1=rec;
  ok(label+": Lead event after submit",c1.some(x=>x==="track:Lead"),c1);
  const al=X.hooks.find(h=>/lead_form/.test(h.body));
  ok(label+": alert hook gets marketer="+qs.split("=")[1],al&&JSON.parse(al.body).marketer===qs.split("=")[1],X.hooks.map(h=>h.path+" "+h.body.slice(0,120)));}
 ok(label+": no JS errors",X.errs.length===0,X.errs);await X.c.close()}
await br.close();console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)})();
