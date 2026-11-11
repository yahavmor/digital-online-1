const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h] of [[375,667],[390,844]]){const c=await b.newContext({viewport:{width:w,height:h},isMobile:true,hasTouch:true,deviceScaleFactor:1});
await c.route("**/*",r=>r.request().url().startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""}));const p=await c.newPage();
await p.goto("http://127.0.0.1:8791/nlp/a5v5.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(500);
console.log(w+"x"+h,JSON.stringify(await p.evaluate(()=>{const y=e=>e.getBoundingClientRect().top+scrollY;const c1=document.querySelector('[data-cta="cta1"]').closest("section"),k=document.querySelector('[data-cta="know"]');
 const s=document.querySelector('[data-sec="1"]');return {cta1_bottom:Math.round(y(c1)+c1.offsetHeight),know_top:Math.round(y(k)),gap:Math.round(y(k)-(y(c1)+c1.offsetHeight)),vh:innerHeight,hero_cta_bottom:Math.round(s.querySelector('[data-cta="hero_main"]').getBoundingClientRect().bottom),h1:Math.round(s.querySelector("h1").getBoundingClientRect().bottom)}})));await c.close();}
await b.close()})();
