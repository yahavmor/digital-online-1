// ב83 (עדכון בן 11.11): צילומי מובייל של a5v5 - מסך ראשון בשני הגדלים, כל משפט מעבר בהקשר (סוף השלב ותחילת הבא), הפתרון, הקורס, הרצועה, ההצעה, הסגירה
const {chromium,devices}=require('playwright');const [B,DIR]=process.argv.slice(2);
(async()=>{const b=await chromium.launch();
 for(const [nm,vp] of [["375",{viewport:{width:375,height:667},deviceScaleFactor:2,isMobile:true,hasTouch:true}],["390",{...devices["iPhone 13"]}]]){
  const c=await b.newContext(vp);await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
  const p=await c.newPage();await p.goto(B+"a5v5.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(2500);
  await p.screenshot({path:DIR+"/v5_"+nm+"_00_first_screen.png"});
  if(nm==="375"){await c.close();continue;}
  const go=async(sel,i,frac)=>{await p.evaluate(([s,i,f])=>{const e=document.querySelectorAll(s)[i];scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*f,behavior:"instant"})},[sel,i,frac]);await p.waitForTimeout(1400);};
  const T=await p.$$eval(".v5-tr",x=>x.length);
  for(let i=0;i<T;i++){await go(".v5-tr",i,0.55);await p.screenshot({path:DIR+"/v5_390_tr"+String(i+1).padStart(2,"0")+".png"});}
  for(const [n,s,f] of [["sol",'[data-name="הפתרון"]',0.02],["course",'[data-name="מה יש בפנים"]',0.02],["strip",'[data-name="עוד כמה דקות עם בן"]',0.02],["offer",'#offer .v4-ko-tot',0.3],["close",'[data-name="סגירה"]',0.25]]){await go(s,0,f);await p.screenshot({path:DIR+"/v5_390_"+n+".png"});}
  await c.close();}
 await b.close()})();
