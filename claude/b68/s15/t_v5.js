// ב83: בדיקות a5v5 (סעיף 6 במפרט). שימוש: node t_v5.js http://127.0.0.1:8791/nlp/
// a5v5 = בנייה עם slots_v5.json (בלי קבצים עד ע22), a5v5s = עם slots_v5_test.json (קבצי בדיקה). מושווה מול a5v4.
const {chromium,devices}=require('playwright');const B=process.argv[2];
const V5=require(__dirname+"/slots_v5_test.json");
const res=[];const ok=(n,c,e="")=>{res.push(!!c);if(!c)console.log("FAIL",n,e);else console.log("PASS",n)};
const FB="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5]";
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
const ORDER=["פתיחה","מה אם","מה אומרים","@cta1","רגע לפני","לדעת או להטמיע","תוצאות אמיתיות","איך נראית המציאות","מה יש בפנים","בונוסים","ההצעה","עוד כמה דקות עם בן","למה בניתי","למי מתאים","עם מה תצא","@cta2","איך מתחילים","@cta3","שאלות","@final"];
const NEW_TEXT=["עוד כמה דקות עם בן","צפו בסרטון עם קול","כן, אני רוצה להתחיל עכשיו ב- 1,290 297 ₪ ← תשלום מאובטח מחיר השקה לזמן מוגבל · גישה מיידית לקורס ולבונוסים · החזר מלא תוך 7 ימים"];
async function ctx(b,opt={}){const c=await b.newContext({...devices["iPhone 13"],...opt});const ev=[];
 await c.route("**/*",r=>{const u=r.request().url();if(/hook\.eu1\.make\.com/.test(u)){const q=new URLSearchParams(r.request().postData()||"");ev.push({ev:q.get("ev"),variant:q.get("variant"),video:q.get("video"),cta:q.get("cta")});return r.fulfill({status:200,body:""})}
  return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});c.ev=ev;return c;}
const words=p=>p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;out.push(n.nodeValue)}
 return out.join(" ").split(/[\s·•]+/).filter(x=>x&&!/^\d{1,2}$/.test(x))}); /* מספרי הסקשנים (01..) ומונה הסקשנים משתנים עם הסדר */
const media=p=>p.evaluate(()=>[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort());
const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
const order=p=>p.evaluate(()=>[...document.querySelectorAll("body > section, body > header, main > section, main > header")].length?[...document.querySelectorAll("header[data-sec],section")].filter(s=>!s.closest(".sp-modal")).map(s=>s.dataset.name||(s.classList.contains("guar")?"@final":"@"+((s.querySelector("[data-cta]")||{}).dataset||{}).cta)):[]);
(async()=>{const b=await chromium.launch();
 // 1. סדר, מספור, noindex, v=a5v5
 for(const pg of ["a5v5","a5v5s"]){const c=await ctx(b);const p=await c.newPage();await p.goto(B+pg+".html?test=1",{waitUntil:"load"});await p.waitForTimeout(600);
  const o=(await order(p)).filter(x=>pg==="a5v5s"||x!=="עוד כמה דקות עם בן");const exp=ORDER.filter(x=>pg==="a5v5s"||x!=="עוד כמה דקות עם בן");
  ok(pg+" order as section 3 (strip only when files exist)",JSON.stringify(o)===JSON.stringify(exp),JSON.stringify(o));
  ok(pg+" data-sec 1..n in order",await p.evaluate(()=>[...document.querySelectorAll("[data-sec]")].every((s,i)=>+s.dataset.sec===i+1)));
  ok(pg+" noindex + data-variant=a5v5 + page view event with variant a5v5",await p.evaluate(()=>!!document.querySelector('meta[name=robots][content*="noindex"]')&&document.documentElement.dataset.variant==="a5v5")&&c.ev.some(e=>e.ev==="view"&&e.variant==="a5v5"),JSON.stringify(c.ev.slice(0,3)));
  ok(pg+" no <video> in the HTML beyond a5v4's (numbering of existing videos kept)",await p.evaluate(()=>[...document.querySelectorAll("video")].filter(v=>!v.dataset.v5bg).length)===2);
  await c.close();}
 // 2. קופי ומדיה מול a5v4: אותן מילים, חוץ מהטקסטים החדשים שבמפרט; אותה מדיה (+ פוסטרים של v5 בגרסת הבדיקה)
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v4.html?test=1",{waitUntil:"load"});const W4=cnt(await words(p)),M4=await media(p);
  for(const pg of ["a5v5","a5v5s"]){await p.goto(B+pg+".html?test=1",{waitUntil:"load"});const W5=cnt(await words(p)),M5=await media(p);
   const allow=cnt(pg==="a5v5s"?[].concat(...NEW_TEXT.map(t=>t.split(/[\s·•]+/).filter(Boolean))):[]);
   const miss=Object.keys(W4).filter(k=>(W5[k]||0)<W4[k]),extra=Object.keys(W5).filter(k=>W5[k]-(W4[k]||0)>(allow[k]||0));
   ok(pg+" same copy as a5v4 (only the 2 new labels + the strip button)",!miss.length&&!extra.length,"missing:"+JSON.stringify(miss.slice(0,6))+" extra:"+JSON.stringify(extra.slice(0,8)));
   const posters=pg==="a5v5s"?[V5.belief.poster,...V5.strip.map(x=>x.poster)]:[];
   ok(pg+" same media as a5v4 (+ v5 posters)",JSON.stringify([...M4,...posters].sort())===JSON.stringify(M5),M4.length+" vs "+M5.length);}
  await c.close();}
 // 3. המסך הראשון: הכפתור בפנים, בלי אנימציה, ה-LCP לא מונפש
 for(const [w,h] of [[375,667],[390,844]]){const c=await ctx(b,{viewport:{width:w,height:h}});const p=await c.newPage();await p.goto(B+"a5v5s.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(800);
  const f=await p.evaluate(()=>{const s=document.querySelector('[data-sec="1"]'),q=e=>Math.round(e.getBoundingClientRect().bottom);const hid=[...document.querySelectorAll("body *")].filter(e=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0&&r.height>0&&!e.closest(".v5-loop,.sticky,.prog")&&(getComputedStyle(e).opacity==="0"||/(^|\s)(v5s|v5z|v5o|v4r)(\s|$)/.test(e.className))});
   const lcp=document.querySelector('[data-sec="1"] img[fetchpriority="high"]');return {h1:q(s.querySelector("h1")),sub:q(s.querySelector(".sub")),cta:q(s.querySelector('[data-cta="hero_main"]')),vh:innerHeight,hidden:hid.map(e=>e.tagName+"."+e.className).slice(0,4),lcpAnim:/v5|v4r|rv/.test(lcp.className)||getComputedStyle(lcp).transitionDuration!=="0s"}});
  ok(w+"x"+h+": headline, sentence and button in the first screen; nothing hidden/animating there; LCP image untouched",f.h1<=f.vh&&f.sub<=f.vh&&f.cta<=f.vh&&!f.hidden.length&&!f.lcpAnim,JSON.stringify(f));await c.close();}
 // 4. סרטונים: לולאה בלי קול (גם בפייסבוק ובאינסטגרם), הסרטון המלא, רק אחד מתנגן, נעצר מחוץ למסך, אירוע עם קוד
 for(const [nm,ua] of [["iphone",null],["fb",FB],["ig",IG]]){const c=await ctx(b,ua?{userAgent:ua}:{});const p=await c.newPage();await p.goto(B+"a5v5s.html?test=1",{waitUntil:"load"});await p.waitForTimeout(2500);
  const L=await p.evaluate(()=>{const v=document.querySelector(".v5-loop video");return v?{paused:v.paused,muted:v.muted,inline:v.hasAttribute("playsinline"),loop:v.loop,t:v.currentTime}:null});
  ok(nm+": hero loop plays muted, inline, looping (after the LCP image)",!!L&&!L.paused&&L.muted&&L.inline&&L.loop&&L.t>0,JSON.stringify(L));
  if(nm==="iphone"){
   await p.click(".v5-sound");await p.waitForTimeout(1500);
   const M=await p.evaluate(()=>{const v=document.querySelector(".v5-modal video"),l=document.querySelector(".v5-loop video");return {modal:!!v,playing:v&&!v.paused,muted:v&&v.muted,controls:v&&v.controls,loopPaused:l.paused}});
   ok("'צפו בסרטון עם קול' opens the full video with sound, loop pauses, event v5_"+V5.hero.code,M.modal&&M.playing&&!M.muted&&M.controls&&M.loopPaused&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.hero.code),JSON.stringify(M)+JSON.stringify(c.ev.filter(e=>e.ev==="video_play")));
   await p.click(".v5-modal .v5-x");await p.waitForTimeout(300);
   ok("modal closes",!(await p.$(".v5-modal")));
   const pre=await p.evaluate(()=>[...document.querySelectorAll("[data-v5src]")].every(b=>{const i=b.querySelector("img");return i&&i.loading==="lazy"&&i.getAttribute("width")&&b.style.aspectRatio}));
   ok("v5 videos are poster buttons (lazy poster, fixed ratio) - no video loaded before a click (preload none)",pre);
   await p.evaluate(()=>{const e=document.querySelector('[data-name="מה אם"] .v5-vid');scrollTo({top:scrollY+e.getBoundingClientRect().top-80,behavior:"instant"})});await p.waitForTimeout(500);
   await p.click('[data-name="מה אם"] .v5-box');await p.waitForTimeout(1500);
   const s1=await p.evaluate(()=>{const v=document.querySelector('[data-name="מה אם"] video');return v&&!v.paused});
   ok("belief video plays on click, event v5_"+V5.belief.code,s1&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.belief.code));
   await p.evaluate(()=>{const e=document.querySelector(".v5-strip");scrollTo({top:scrollY+e.getBoundingClientRect().top-80,behavior:"instant"})});await p.waitForTimeout(800);
   const s2=await p.evaluate(()=>{const v=document.querySelector('[data-name="מה אם"] video');return v.paused});
   ok("a video that leaves the screen pauses",s2);
   await p.evaluate(()=>{const v=document.querySelector('[data-name="מה אם"] video');window.__b=v;});
   await p.click('.v5-strip .v5-sv:nth-child(1) .v5-box');await p.waitForTimeout(1500);
   const s3=await p.evaluate(()=>{const vs=[...document.querySelectorAll("video")].filter(v=>!v.paused);return {playing:vs.length,code:vs[0]&&vs[0].closest("[data-v5code]")&&vs[0].closest("[data-v5code]").dataset.v5code}});
   ok("strip video plays, only one video playing, event with its code",s3.playing===1&&s3.code===V5.strip[0].code&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.strip[0].code),JSON.stringify(s3));
   ok("strip scrolls sideways (5 videos, scroll-snap)",await p.evaluate(()=>{const s=document.querySelector(".v5-strip");return s.querySelectorAll(".v5-vid").length===5&&s.scrollWidth>s.clientWidth+100&&getComputedStyle(s).scrollSnapType.includes("x")}));
   await p.click('[data-cta="strip"]').catch(()=>{});await p.waitForTimeout(500);
   ok("strip button sends cta_click with cta=strip",c.ev.some(e=>e.ev==="cta_click"&&e.cta==="strip"),JSON.stringify(c.ev.filter(e=>e.ev==="cta_click")));}
  await c.close();}
 // 5. אנימציות: מתחת למסך הראשון מוסתר עד הגלילה, ואחרי גלילה הכול גלוי; רגע המחיר
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v5s.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(600);
  const pre=await p.evaluate(()=>({v5a:document.documentElement.classList.contains("v5a"),stag:document.querySelectorAll(".bx2.v5s,.v4-ko-list li.v5s").length,ko:document.querySelector(".v4-ko").classList.contains("v5z"),koOp:getComputedStyle(document.querySelector(".v4-ko")).opacity}));
  ok("animations armed below the fold (bonus cards + value rows staggered, offer box zoom)",pre.v5a&&pre.stag>=11&&pre.ko&&+pre.koOp===0,JSON.stringify(pre));
  const d=await p.evaluate(()=>[...document.querySelectorAll(".v4-ko-list li")].map(l=>getComputedStyle(l).transitionDelay.split(",")[0]));
  ok("value rows 70ms apart",d.length===6&&d.every((x,i)=>Math.abs(parseFloat(x)*1000-i*70)<2),JSON.stringify(d));
  ok("only transform/opacity are transitioned by the v5 layer",await p.evaluate(()=>[...document.querySelectorAll(".v5s,.v5z,.v5o,.v4-ko-now b")].every(e=>getComputedStyle(e).transitionProperty.split(",").every(x=>/^\s*(opacity|transform)\s*$/.test(x)))));
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,60))}});
  await p.evaluate(()=>{const e=document.querySelector(".v4-ko-tot");scrollTo({top:scrollY+e.getBoundingClientRect().top-300,behavior:"instant"})});await p.waitForTimeout(2600);
  const post=await p.evaluate(()=>({left:[...document.querySelectorAll(".v5s,.v5z,.rv,.v4r")].filter(e=>e.getBoundingClientRect().height>0&&+getComputedStyle(e).opacity<1).map(e=>e.tagName+"."+e.className).slice(0,4),
   tot:document.querySelector(".v4-ko-tot b").textContent,reg:document.querySelector(".v4-ko-reg").classList.contains("in"),now:document.querySelector(".v4-ko-now b").classList.contains("in"),nowOp:getComputedStyle(document.querySelector(".v4-ko-now b")).opacity}));
  ok("after scrolling everything revealed; price moment: 2,411 counted, strike drawn, 297 shown",!post.left.length&&post.tot==="2,411 ₪"&&post.reg&&post.now&&+post.nowOp===1,JSON.stringify(post));
  await c.close();}
 // 6. הפחתת תנועה: בלי לולאה, בלי אנימציות, שום דבר מוסתר
 {const c=await ctx(b,{reducedMotion:"reduce"});const p=await c.newPage();await p.goto(B+"a5v5s.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(1500);
  const r=await p.evaluate(()=>({v5a:document.documentElement.classList.contains("v5a"),loop:!!document.querySelector(".v5-loop video"),hidden:[...document.querySelectorAll("[data-sec] *")].filter(e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).opacity==="0").length,sound:!!document.querySelector(".v5-sound")}));
  ok("reduced motion: no loop, no v5 animations, nothing hidden, full video still available",!r.v5a&&!r.loop&&!r.hidden&&r.sound,JSON.stringify(r));await c.close();}
 // 7. בלי JS: התוכן גלוי
 {const c=await b.newContext({...devices["iPhone 13"],javaScriptEnabled:false});await c.route("**/*",r=>r.request().url().startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""}));
  const p=await c.newPage();await p.goto(B+"a5v5s.html?internal=1",{waitUntil:"load"});
  const r=await p.evaluate(()=>({hidden:[...document.querySelectorAll("[data-sec] *")].filter(e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).opacity==="0").map(e=>e.tagName+"."+e.className).slice(0,4),offer:document.querySelector(".v4-ko-now b").textContent,secs:document.querySelectorAll("[data-sec]").length}));
  ok("no JS: all content visible (offer, price, all sections)",!r.hidden.length&&r.offer==="297 ₪"&&r.secs===16,JSON.stringify(r));await c.close();}
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
