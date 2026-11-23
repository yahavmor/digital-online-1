const {chromium,devices}=require('playwright');const fs=require('fs');const ROWS=fs.readFileSync(__dirname+"/rows_b78.tsv","utf8");
const AFFS="affiliates\tname\tpct\tactive\tfee\nshahar\tשחר\t74\ttrue\t220\nrachel\tרחל\t74\ttrue\t220\ngal\tגל\t74\ttrue\t220\nyahel\tיהל\t74\ttrue\t220";
const SPEND="key\tvalue\n2026-11-08|aff_shahar\t20\n2026-11-08|aff_rachel\t20\n2026-11-09|aff_gal\t40\n";
const setTime=async c=>{await c.addInitScript(()=>{const F=new Date("2026-11-09T23:30:00").getTime(),D=Date;class X extends D{constructor(...a){a.length?super(...a):super(F)}static now(){return F}}window.Date=X})};
(async()=>{const b=await chromium.launch();
for(const [dn,dev] of [["d",{viewport:{width:1366,height:900}}],["m",devices["iPhone 13"]]])for(const pg of ["dashboard_main.html","dashboard.html"]){
 const c=await b.newContext(dev);await setTime(c);const errs=[],saved=[];
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com")){const q=new URL(u).searchParams,a=q.get("action")||"";if(a==="spend_set"){saved.push(q.get("creative")+"="+q.get("amount"));return r.fulfill({status:200,body:"ok"})}
  const body={rows:ROWS,spend:SPEND,affiliates:AFFS,refunds:"refunds\n",paid:"paid\n"}[a];return r.fulfill({status:200,body:body==null?a:body});}
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("http://127.0.0.1:8778/nlp/"+pg+"#aud",{waitUntil:"networkidle"});await p.waitForTimeout(1200);
 await p.click('nav.tabs button[data-s="aud"]');await p.waitForTimeout(700);
 const g=t=>p.$$eval(t+" tr",rs=>rs.map(r=>[...r.children].map(x=>x.innerText.replace(/\s+/g," ").trim()).join(" | ")));
 const out={camp:await g("#audCamp"),page:await g("#audPage"),sum:(await p.$eval("#audSum",e=>e.innerText)).split("\n"),opts:await p.$$eval("#audSpCamp option",o=>o.map(x=>x.value)),hs:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)};
 if(pg==="dashboard.html"){await p.selectOption("#audSpCamp","yahel");await p.fill("#audSpAmt","40");await p.click("#audSpSave");await p.waitForTimeout(500);
  await p.screenshot({path:__dirname+"/aud_"+dn+".png",fullPage:true});}
 console.log("=====",dn,pg,"errors:",errs.length?errs:"none","| hscroll:",out.hs,"| spend opts:",out.opts.join(","),"| saved:",saved.join(","));
 console.log(out.camp.join("\n"));console.log("--");console.log(out.page.join("\n"));console.log("--");console.log(out.sum.join("\n"));
 await c.close();}
await b.close()})();
