// ב126: שגיאת JS נשמרת עם קובץ ושורה, ולא נשלחת ל-Meta. node t_b126.js <dir with X.html and X.orig.html>
const {chromium,devices}=require("playwright"),fs=require("fs");const D=process.argv[2];
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
(async()=>{const br=await chromium.launch();
async function run(file,page){const c=await br.newContext({...devices["iPhone 13"]});const hooks=[],errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("/"+page+".html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(D+"/"+file,"utf8")});
   if(u.pathname.endsWith("/boom.js"))return r.fulfill({status:200,contentType:"text/javascript",body:"\n\nnull.foo;"});
   return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com")){hooks.push(r.request().postData()||"");return r.fulfill({status:200,body:"Accepted"})}
  if(/facebook|clarity|googletagmanager/.test(u.hostname))return r.fulfill({status:200,contentType:"text/javascript",body:""});
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.addInitScript(()=>{window.__fb=[];window.fbq=function(){window.__fb.push([].slice.call(arguments).map(String).join(":"))};window.fbq.queue=[]});
 await p.goto("https://funnel.digitalonline.co.il/nlp/"+page+".html?claude=b126",{waitUntil:"load"});await p.waitForTimeout(600);
 await p.evaluate(()=>{const s=document.createElement("script");s.src="/nlp/boom.js";document.body.appendChild(s)});await p.waitForTimeout(1200);
 const fb=await p.evaluate(()=>window.__fb);await c.close();
 const je=hooks.map(h=>Object.fromEntries(new URLSearchParams(h))).filter(o=>o.ev==="js_error");return {je,fb,errs}}
for(const page of ["a5s","a5v6","a5v7","a","pr2"]){
 const N=await run(page+".html",page),O=await run(page+".orig.html",page);
 ok(page+": js_error נשלח לגיליון",N.je.length>=1,N.je.length);
 ok(page+": name כולל הודעה + @boom.js:שורה:עמודה",N.je.length&&/@boom\.js:3:\d+$/.test(N.je[0].name)&&/TypeError|Cannot/.test(N.je[0].name),N.je[0]&&N.je[0].name);
 ok(page+": name עד 150 תווים",N.je.every(o=>o.name.length<=150));
 ok(page+": LP_js_error לא נשלח ל-Meta (אחרי)",!N.fb.some(x=>/LP_js_error/.test(x)),N.fb.filter(x=>/LP_/.test(x)));
 ok(page+": LP_view עדיין נשלח ל-Meta",N.fb.some(x=>/trackCustom:LP_view/.test(x)),N.fb.slice(0,4));
 ok(page+": בקרה - לפני: name בלי קובץ ושורה, ו-LP_js_error כן נשלח",O.je.length&&!/@boom/.test(O.je[0].name)&&O.fb.some(x=>/LP_js_error/.test(x)),{name:O.je[0]&&O.je[0].name,fb:O.fb.filter(x=>/LP_js/.test(x))});}
await br.close();console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)})();
