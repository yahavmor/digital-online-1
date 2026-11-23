// ב68 חלק 7: צילומי מובייל של 12 (מה יש בפנים), 13 (בונוסים) והסיכום (#offer)
const {chromium,devices}=require('playwright');const DIR=process.argv[2];
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("http://127.0.0.1:8791/nlp/a5v4.html?internal=1",{waitUntil:"networkidle"});
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,20))}});await p.waitForTimeout(800);
 const go=async(sel,i=0,off=60)=>{await p.evaluate(([s,i,off])=>{const e=document.querySelectorAll(s)[i];scrollTo({top:scrollY+e.getBoundingClientRect().top-off,behavior:"instant"})},[sel,i,off]);await p.waitForTimeout(900);};
 const shots=[["p7_12a_inside",'[data-name="מה יש בפנים"] h2'],["p7_12b_player",'.v4-peek'],["p7_13a_bonus_head",'[data-name="בונוסים"] h2'],["p7_13b_bonus2",'article.bx2',1],["p7_offer_a",'#offer h2'],["p7_offer_b",'#offer .v4-ko-price']];
 for(const [n,s,i] of shots){await go(s,i||0,n==="p7_offer_b"?220:60);await p.screenshot({path:DIR+"/"+n+".jpg",type:"jpeg",quality:80});}
 await b.close()})();
