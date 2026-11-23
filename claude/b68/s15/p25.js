// ב68 חלק 6: מה יש בפנים והבונוסים החדשים במובייל
const {chromium,devices}=require('playwright');const DIR=process.argv[2];
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("http://127.0.0.1:8791/nlp/a5v4.html?internal=1",{waitUntil:"networkidle"});
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,20))}});await p.waitForTimeout(800);
 const go=async(sel,i=0,off=70)=>{await p.evaluate(([s,i,off])=>{const e=document.querySelectorAll(s)[i];scrollTo({top:scrollY+e.getBoundingClientRect().top-off,behavior:"instant"})},[sel,i,off]);await p.waitForTimeout(900);};
 await go('[data-name="מה יש בפנים"] h2');await p.screenshot({path:DIR+"/p6_1_inside.jpg",type:"jpeg",quality:78});
 await go('.v4-peek');await p.screenshot({path:DIR+"/p6_2_player.jpg",type:"jpeg",quality:78});
 for(let i=0;i<5;i++){await go('article.bx2',i,40);await p.screenshot({path:DIR+"/p6_3_bonus"+(i+1)+".jpg",type:"jpeg",quality:78});}
 await go('.bx2-total',0,200);await p.screenshot({path:DIR+"/p6_4_total_final.jpg",type:"jpeg",quality:78});
 await b.close()})();
