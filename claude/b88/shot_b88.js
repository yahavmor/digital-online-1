const {chromium,devices}=require("playwright"),fs=require("fs");const H=fs.readFileSync(process.argv[2],"utf8"),OUT=process.argv[3];
(async()=>{const br=await chromium.launch();for(const co of ["a","b"]){const c=await br.newContext({...devices["iPhone 13"],viewport:{width:390,height:844}});
await c.route("**/*",r=>{const u=new URL(r.request().url());if(u.pathname.endsWith("/checkout.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:H});
 if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";if(/ev=/.test(b))return r.fulfill({status:200,body:"Accepted"});return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({code:"0",url:"https://secure.cardcom.solutions/EA/mock",lp:"lp1",bit_url:"https://secure.cardcom.solutions/api/LPC5/Bit?lpc=lp1"})})}
 if(u.hostname.endsWith("cardcom.solutions"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:"<html><body style='margin:0;font:16px sans-serif;color:#888;display:flex;align-items:center;justify-content:center;height:600px;background:#fafafa'>טופס הכרטיס של קארדקום (מדומה)</body></html>"});
 return r.fulfill({status:204,body:""})});
const p=await c.newPage();await p.goto("https://funnel.digitalonline.co.il/nlp/checkout.html?v=a5v6&co="+co+"&claude=b88",{waitUntil:"load"});await p.waitForTimeout(800);
await p.fill("#fName","בדיקה ב88");await p.fill("#fEmail","b88@example.com");await p.fill("#fPhone","0501234567");await p.check("#fTerms");
const s=p.locator('#det button[type="submit"]:visible');if(await s.count())await s.first().click();await p.waitForTimeout(1500);
console.log(co,await p.evaluate(()=>({bit:document.getElementById("bitWrap").hidden,cc:document.getElementById("cc").hidden,src:document.getElementById("cc").src,pay:document.getElementById("paySec").hidden,hold:!!document.getElementById("coHold").offsetParent})));await p.evaluate(()=>document.querySelector(".paytitle").scrollIntoView({block:"start"}));await p.waitForTimeout(300);
await p.screenshot({path:OUT+"/b88_final_"+co+".png"});await c.close()}await br.close()})();
