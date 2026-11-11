// ב68 הערות בן 11.11: צילום מובייל (אייפון 13) לכל שינוי ב-a5v4. שימוש: node shots_ben1111.js <base של nlp/> <dir>
const {chromium,devices}=require('playwright');const [B,DIR]=process.argv.slice(2);
const S=[["1_hero",null],["2_offer",'[data-cta="offer"]'],["3_inside",'[data-name="מה יש בפנים"] .lead'],["4_reality",'[data-name="איך נראית המציאות"] .reality'],
 ["5_outcomes",'[data-name="עם מה תצא"] .outcomes'],["6_fit",'[data-name="למי מתאים"]'],["7_know",'[data-cta="know"]'],["8_keys",'[data-cta="keys"]']];
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto(B+"a5v4.html?internal=1",{waitUntil:"networkidle"});await p.waitForTimeout(400);
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo(0,y);await new Promise(r=>setTimeout(r,25))}});await p.waitForTimeout(800);
 for(const [n,sel] of S){if(!sel){await p.evaluate(()=>scrollTo(0,0));}else{await p.evaluate(s=>{const e=document.querySelector(s);const r=e.getBoundingClientRect();scrollTo(0,scrollY+r.top-(n=>n)(Math.max(40,(innerHeight-Math.min(r.height,innerHeight))/2)))},sel);}
  await p.waitForTimeout(900);await p.screenshot({path:DIR+"/a5v4_ben_"+n+".jpg",type:"jpeg",quality:80});}
 await b.close()})();
