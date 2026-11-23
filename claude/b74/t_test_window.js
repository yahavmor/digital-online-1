// ב74 חלון בדיקה: צילומי האפליקציה במקום ההדמיה, וכתובת השרת בשלושת הדפים. שרת מדומה - שום בקשה לא יוצאת.
// שימוש: node t_test_window.js <nlp dir אחרי patch_test_window.py>
const {chromium,devices}=require("playwright"),fs=require("fs"),path=require("path");const D=process.argv[2];
const API="https://hook.eu1.make.com/afnx34prmqo6zjf7b8zoqe7fvvy6q97b";
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const br=await chromium.launch();
for(const dev of ["iPhone 13","Desktop Chrome"]){
 const c=await br.newContext({...devices[dev]});const calls=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){const p=path.join(D,u.pathname.replace(/^\/nlp\//,""));if(fs.existsSync(p)){const ct=p.endsWith(".html")?"text/html; charset=utf-8":p.endsWith(".jpg")?"image/jpeg":p.endsWith(".svg")?"image/svg+xml":"application/octet-stream";return r.fulfill({status:200,contentType:ct,body:fs.readFileSync(p)})}return r.fulfill({status:404,body:""})}
  if(r.request().url().startsWith(API)){const b=new URLSearchParams(r.request().postData()||"");calls.push(b.get("action")||b.get("ev")||"?");if(b.get("action")==="check")return r.fulfill({status:200,contentType:"application/json",body:'{"state":"ok","name":"בן","email":"b***@example.com"}'});return r.fulfill({status:200,body:"Accepted"})}
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));
 await p.goto("https://funnel.digitalonline.co.il/nlp/upsell-97.html?t=0000000000000000000000000000test&test=1",{waitUntil:"load"});await p.waitForTimeout(1500);
 const r=await p.evaluate(()=>{const ph=[...document.querySelectorAll(".phone .screen")];return {phones:ph.length,imgs:ph.map(s=>{const i=s.querySelector("img");return i?i.getAttribute("src")+":"+i.naturalWidth:"SIM"}),bar:(document.getElementById("testbar")||{}).innerText||""}});
 ok(dev+": every phone shows a real screenshot (no simulation)",r.phones>0&&r.imgs.every(x=>/assets\/upsell\/app-(home|plan|sos)\.jpg:780$/.test(x)),JSON.stringify(r.imgs));
 ok(dev+": all three screenshots used",["home","plan","sos"].every(k=>r.imgs.some(x=>x.includes("app-"+k))),JSON.stringify(r.imgs));
 ok(dev+": test bar no longer lists screenshots",!/צילומי מסך/.test(r.bar),r.bar);
 ok(dev+": page called the real API (check)",calls.includes("check"),calls.join());
 ok(dev+": no JS errors",!errs.length,errs.join("|"));
 if(dev==="iPhone 13"){await p.screenshot({path:path.join(__dirname,"shots_test_window_top.png")});
  await p.evaluate(()=>{const e=document.querySelectorAll(".phone")[1]||document.querySelector(".phone");e.scrollIntoView({block:"center"})});await p.waitForTimeout(400);await p.screenshot({path:path.join(__dirname,"shots_test_window_phone.png")})}
 await c.close()}
for(const f2 of ["checkout97.html","upsell-thanks.html"]){const s=fs.readFileSync(path.join(D,f2),"utf8");ok(f2+": API address set, no placeholder",s.includes(API)&&!s.includes("%UPSELL_API%"))}
console.log("TOTAL",n-f+"/"+n);await br.close();process.exit(f?1:0)})();
