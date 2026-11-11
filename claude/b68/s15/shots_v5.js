// ב83: צילומי מובייל של a5v5 (גרסת הבדיקה a5v5s עם קבצי בדיקה): פתיחה עם הלולאה, אמונה + h2, רצועה, הצעה
const {chromium,devices}=require('playwright');const [B,DIR,PG]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto(B+(PG||"a5v5s")+".html?internal=1",{waitUntil:"load"});await p.waitForTimeout(2500);
 await p.screenshot({path:DIR+"/v5_01_hero.jpg",type:"jpeg",quality:80});
 const st=await p.evaluate(()=>{const v=document.querySelector(".v5-loop video");return v?{loop:true,paused:v.paused,muted:v.muted,inline:v.hasAttribute("playsinline"),on:v.classList.contains("on")}:{loop:false}});console.log("loop",JSON.stringify(st));
 const go=async(sel,i=0,off=60)=>{await p.evaluate(([s,i,off])=>{const e=document.querySelectorAll(s)[i];scrollTo({top:scrollY+e.getBoundingClientRect().top-off,behavior:"instant"})},[sel,i,off]);await p.waitForTimeout(1300);};
 for(const [n,s,i,o] of [["v5_02_belief",'[data-name="מה אם"] h2'],["v5_03_belief_video",'[data-name="מה אם"] .v5-vid',0,120],["v5_04_social",'[data-name="מה אומרים"] h2'],["v5_05_know",'[data-cta="know"]',0,300],
   ["v5_06_results",'[data-name="תוצאות אמיתיות"] h2'],["v5_07_inside",'[data-name="מה יש בפנים"] h2'],["v5_08_bonus",'[data-name="בונוסים"] h2'],["v5_09_offer",'#offer h2'],["v5_10_offer_price",'#offer .v4-ko-tot',0,200],["v5_11_strip",'[data-name="עוד כמה דקות עם בן"] h2']]){
  if(!(await p.$(s))){console.log("missing",n);continue;}await go(s,i||0,o||60);await p.screenshot({path:DIR+"/"+n+".jpg",type:"jpeg",quality:80});}
 await b.close()})();
