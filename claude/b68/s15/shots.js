// ב68 v4: צילומי מסך - מסך ראשון, ההצעה, והמקומות לנכסים, באייפון ובמחשב. שימוש: node shots.js <base> <dir> <pages,..> [dsf=1]
const {chromium,devices}=require('playwright');const [B,DIR,PG,DSF]=process.argv.slice(2);const dsf=+(DSF||1);
(async()=>{const b=await chromium.launch();
for(const pg of PG.split(","))for(const [dn,dev] of [["m",{...devices["iPhone 13"],deviceScaleFactor:dsf}],["d",{viewport:{width:1366,height:850},deviceScaleFactor:dsf}]]){
 const c=await b.newContext(dev);await c.route("**/*",r=>{const u=r.request().url();if(u.startsWith("http://127.0.0.1")||/fonts\.(googleapis|gstatic)/.test(u))return r.continue();return r.fulfill({status:200,body:""})});
 const p=await c.newPage();await p.goto(B+pg+".html?lab=1",{waitUntil:"networkidle"});await p.waitForTimeout(600);
 await p.screenshot({path:`${DIR}/${pg}_${dn}_1first.jpg`,type:"jpeg",quality:80});
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=250){scrollTo(0,y);await new Promise(r=>setTimeout(r,30))}});await p.waitForTimeout(900);
 const shot=async(sel,name)=>{const e=await p.$(sel);if(!e)return;await e.scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-20));await p.waitForTimeout(900);await p.screenshot({path:`${DIR}/${pg}_${dn}_${name}.jpg`,type:"jpeg",quality:80});};
 await shot('[data-cta="offer"]','2offer');await shot('[data-slot="t15"]','3t15');await shot('[data-slot="wa"]','4wa');await shot('[data-slot="trial"]','5trial');
 await c.close();}
await b.close()})();
