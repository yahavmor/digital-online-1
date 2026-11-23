// ב68 חלק 5: "מה יש בפנים" במובייל - הסדר החדש, הכפתור "לכל 90 השיעורים", והסיור (בגרסת הבדיקה a5v4s) שרץ רק כשהוא במסך
const {chromium,devices}=require('playwright');const DIR=process.argv[2];
(async()=>{const b=await chromium.launch();
 for(const [pg,rm] of [["a5v4",false],["a5v4s",false],["a5v4s",true]]){
 const c=await b.newContext({...devices["iPhone 13"],reducedMotion:rm?"reduce":"no-preference"});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("http://127.0.0.1:8791/nlp/"+pg+".html?internal=1",{waitUntil:"networkidle"});
 const before=await p.evaluate(()=>({videos:document.querySelectorAll("video").length,tourVideo:!!document.querySelector(".v4-tour video")}));
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,20))}});await p.waitForTimeout(600);
 const go=async sel=>{await p.evaluate(s=>{const e=document.querySelector(s);scrollTo({top:scrollY+e.getBoundingClientRect().top-70,behavior:"instant"})},sel);await p.waitForTimeout(1200);};
 if(pg==="a5v4"&&!rm){
  await go('[data-name="מה יש בפנים"] h2');await p.screenshot({path:DIR+"/p5_1_head_notcourse.jpg",type:"jpeg",quality:78});
  await go('.v4-show');await p.screenshot({path:DIR+"/p5_2_ben_text.jpg",type:"jpeg",quality:78});
  await go('.v4-peek');await p.screenshot({path:DIR+"/p5_3_player.jpg",type:"jpeg",quality:78});
  await go('[data-name="מה יש בפנים"] .toolbox');await p.screenshot({path:DIR+"/p5_4_all_closed.jpg",type:"jpeg",quality:78});
  await p.click('.v4-all > summary');await p.waitForTimeout(500);await p.screenshot({path:DIR+"/p5_5_all_open.jpg",type:"jpeg",quality:78});
  console.log(pg,JSON.stringify(before),JSON.stringify(await p.evaluate(()=>({allOpen:document.querySelector(".v4-all").open,modsVisible:!!document.querySelector(".v4-all .mods").offsetHeight}))));
 } else {
  await go('.v4-tour');await p.waitForTimeout(1500);
  const st=await p.evaluate(()=>{const v=document.querySelector(".v4-tour video");return v?{video:true,muted:v.muted,loop:v.loop,playsinline:v.playsInline,controls:v.controls,paused:v.paused,t:+v.currentTime.toFixed(1)}:{video:false,button:!!document.querySelector(".v4-tour [data-v4tour]")}});
  if(!rm)await p.screenshot({path:DIR+"/p5_tour_test.jpg",type:"jpeg",quality:78});
  await go('[data-name="בונוסים"]');await p.waitForTimeout(600);
  const off=await p.evaluate(()=>{const v=document.querySelector(".v4-tour video");return v?{paused:v.paused}:null});
  console.log(pg,rm?"reduced":"",JSON.stringify(before),"in view:",JSON.stringify(st),"scrolled away:",JSON.stringify(off));
 }
 await c.close();}
 await b.close()})();
