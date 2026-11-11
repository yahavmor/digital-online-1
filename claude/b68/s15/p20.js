const {chromium,devices}=require('playwright');const [B,DIR]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"],deviceScaleFactor:1});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 for(const pg of ["a5v4s","a5v4p","a5v4"]){const p=await c.newPage();await p.goto(B+pg+".html?internal=1",{waitUntil:"networkidle"});
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,20))}});await p.waitForTimeout(800);
  for(const [n,sel] of [["peek",'[data-name="מה יש בפנים"] .v4-peek, [data-name="מה יש בפנים"] .peek'],["t15",'[data-slot="t15"]']]){
   const ok=await p.evaluate(s=>{const e=document.querySelector(s);if(!e)return false;const r=e.getBoundingClientRect();scrollTo({top:scrollY+r.top-70,behavior:"instant"});return true},sel);
   if(ok){await p.waitForTimeout(500);await p.screenshot({path:DIR+"/"+pg+"_"+n+".jpg",type:"jpeg",quality:75});}}
  if(pg==="a5v4s"){await p.click('[data-slot="peek20"] .v4-box');await p.waitForTimeout(2500);
   console.log(await p.evaluate(()=>({bar:document.querySelector(".v4-pl-bar i").style.width,v:!!document.querySelector('[data-slot="peek20"] video'),muted:document.querySelector('[data-slot="peek20"] video').muted})));
   await p.evaluate(()=>{const e=document.querySelector(".v4-peek");scrollTo({top:scrollY+e.getBoundingClientRect().top-70,behavior:"instant"})});await p.waitForTimeout(300);await p.screenshot({path:DIR+"/a5v4s_peek_playing.jpg",type:"jpeg",quality:75});}
  await p.close();}
 await b.close()})();
