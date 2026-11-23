// ב87: כניסה ישירה ל-a5v6 עם aff=yosef - הקבצים החיים (main) מוגשים מקומית בדומיין האמיתי; בקשות ל-Make נלכדות ולא נשלחות
const {chromium,devices}=require("playwright"),fs=require("fs"),path=require("path");const ROOT=process.argv[2];
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const b=await chromium.launch(),c=await b.newContext({...devices["iPhone 13"]});const T=[],PAY=[];
await c.route("**/*",async r=>{const u=new URL(r.request().url());
 if(u.hostname==="funnel.digitalonline.co.il"){let p=path.join(ROOT,decodeURIComponent(u.pathname));if(fs.existsSync(p)&&fs.statSync(p).isFile()){const ext=path.extname(p);return r.fulfill({status:200,contentType:{".html":"text/html; charset=utf-8",".js":"text/javascript",".css":"text/css",".png":"image/png",".jpg":"image/jpeg",".webp":"image/webp",".svg":"image/svg+xml",".mp4":"video/mp4"}[ext]||"application/octet-stream",body:fs.readFileSync(p)})}return r.fulfill({status:404,body:""})}
 if(u.hostname.endsWith("make.com")){const body=r.request().postData()||"";if(u.pathname.startsWith("/axjt5w"))T.push(decodeURIComponent(u.search+" "+body));else PAY.push(decodeURIComponent(u.search+" "+body));return r.fulfill({status:200,contentType:"application/json",body:u.pathname.startsWith("/axjt5w")?"Accepted":JSON.stringify({ok:false})})}
 return r.fulfill({status:204,body:""})});
const p=await c.newPage();
await p.goto("https://funnel.digitalonline.co.il/nlp/a5v6.html?aff=yosef&claude=b87",{waitUntil:"load"});await p.waitForTimeout(2500);
ok("a5v6: NLP_OWNER() = yosef",await p.evaluate(()=>NLP_OWNER())==="yosef");
const ck=(await c.cookies()).find(x=>x.name==="nlp_aff");ok("cookie nlp_aff = yosef.<time>, 30 days",ck&&/^yosef\./.test(decodeURIComponent(ck.value))&&ck.expires-Date.now()/1e3>29*864e2,ck&&ck.value);
const v=T.find(x=>/view/.test(x));ok("view event sent with aff=yosef (qs + owner)",!!v&&/aff=yosef/.test(v),(v||"").slice(0,300));
await p.click('[data-cta="hero_main"]');await p.waitForURL(/checkout/,{timeout:8000});await p.waitForTimeout(2000);
ok("checkout opened from a5v6 with v=a5v6",/v=a5v6/.test(p.url()),p.url());
ok("checkout: NLP_OWNER() = yosef (the CTA link itself carries no aff)",await p.evaluate(()=>NLP_OWNER())==="yosef");
const cv=T.filter(x=>/checkout_view/.test(x));ok("checkout_view event carries aff=yosef",cv.length&&cv.every(x=>/aff=yosef/.test(x)),(cv[0]||"").slice(0,300));
// מסלול שני: מגיע אחר כך ממודעה של בן? לא משנה (נבדק בנפרד). כאן - חזרה ישירה אחרי יום בלי aff נשארת ליוסף
await p.fill("#fName","בדיקה ב87");await p.fill("#fEmail","b87@example.com");await p.fill("#fPhone","0500000000");await p.check("#fTerms").catch(()=>{});
 const sub=p.locator('button[type="submit"]:visible').first();console.log("submit buttons visible:",await p.locator('button[type="submit"]:visible').count());await sub.click({timeout:5000}).catch(e=>console.log("click err",e.message.slice(0,80)));await p.waitForTimeout(3000)
 const pay=PAY.find(x=>/yosef/.test(x));ok("payment-page request (7827398, intercepted, not sent) carries owner yosef",!!pay,PAY.map(x=>x.replace(/b87@example\.com|0500000000/g,"…").slice(0,200)).join(" || "));
 if(pay)console.log("payment req fields with yosef:",(pay.match(/[a-z_]*=?[^&\s"]*yosef[^&\s"]*/gi)||[]).slice(0,4).join(" | "));
const p2=await c.newPage();T.length=0;await p2.goto("https://funnel.digitalonline.co.il/nlp/a5v6.html?claude=b87",{waitUntil:"load"});await p2.waitForTimeout(1500);
ok("return visit without aff stays yosef",await p2.evaluate(()=>NLP_OWNER())==="yosef");
fs.writeFileSync(__dirname+"/yosef_view.txt",T.find(x=>/ev=view/.test(x))||"");
console.log("TOTAL",n-f+"/"+n);await b.close()})();
