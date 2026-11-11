// ב68 סעיף 16: הקרוסלה במובייל - שקופית ראשונה, ושכפתור "הבא" מגיע עד השקופית האחרונה
const {chromium,devices}=require('playwright');const DIR=process.argv[2];
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("http://127.0.0.1:8791/nlp/a5v4.html?internal=1",{waitUntil:"networkidle"});
 await p.evaluate(()=>scrollTo({top:300,behavior:"instant"}));await p.waitForTimeout(600);
 await p.evaluate(()=>{const e=document.querySelector('[data-name="מה אומרים"] h2');scrollTo({top:scrollY+e.getBoundingClientRect().top-20,behavior:"instant"})});await p.waitForTimeout(1200);
 await p.screenshot({path:DIR+"/a5v4_16_wa_first_slide.jpg",type:"jpeg",quality:80});
 const n=await p.evaluate(()=>document.querySelectorAll('[data-carousel] .car-slide').length);
 for(let k=0;k<n+1;k++){await p.click('[data-carousel] .car-btn.next');await p.waitForTimeout(450);}
 console.log(JSON.stringify(await p.evaluate(()=>{const d=[...document.querySelectorAll('[data-carousel] .car-dots i')];return {slides:document.querySelectorAll('[data-carousel] .car-slide').length,dots:d.length,on:d.findIndex(x=>x.classList.contains("on"))+1}})));
 await b.close()})();
