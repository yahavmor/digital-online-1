// ב69: הבקשה ל-7827398 כוללת test=1 רק בביקור פנימי. Make מדומה - שום בקשה לא יוצאת.
const {chromium,devices}=require("playwright"),fs=require("fs");const H=fs.readFileSync(process.argv[2],"utf8");
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const br=await chromium.launch();
const run=async(qs,pre)=>{const c=await br.newContext({...devices["iPhone 13"]});const B=[];
 if(pre)await c.addInitScript(()=>{try{localStorage.setItem("nlp_int","1")}catch(e){}});
 await c.route("**/*",r=>{const u=new URL(r.request().url());if(u.pathname.endsWith("/checkout.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:H});
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";if(/(^|&)ev=/.test(b))return r.fulfill({status:200,body:"Accepted"});B.push(new URLSearchParams(b));return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({code:"0",url:"https://secure.cardcom.solutions/EA/mock",lp:"lp1"})})}
  if(u.hostname.endsWith("cardcom.solutions"))return r.fulfill({status:200,contentType:"text/html",body:"<html></html>"});return r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("https://funnel.digitalonline.co.il/nlp/checkout.html?v=a&co=b"+qs,{waitUntil:"load"});await p.waitForTimeout(800);
 await p.fill("#fName","בדיקה ב69");await p.fill("#fEmail","b69@example.com");await p.fill("#fPhone","0501234567");await p.check("#fTerms");
 const s=p.locator('#det button[type="submit"]:visible');if(await s.count())await s.first().click();await p.waitForTimeout(1500);await c.close();return B};
let B=await run("&test=1");ok("?test=1 → request to 7827398 has test=1",B.length===1&&B[0].get("test")==="1",B.map(b=>b.get("test")).join());
B=await run("&claude=x");ok("?claude=… → test=1",B.length===1&&B[0].get("test")==="1");
B=await run("",true);ok("marked internal earlier (nlp_int) → test=1",B.length===1&&B[0].get("test")==="1");
B=await run("&utm_source=fb");ok("regular visitor → no test field",B.length===1&&!B[0].has("test"),B.map(b=>[...b.keys()].join(",")).join("|"));
ok("other fields unchanged (name/email/phone/co present)",["name","email","phone","co"].every(k=>B[0].has(k)));
console.log("TOTAL",n-f+"/"+n);await br.close();process.exit(f?1:0)})();
