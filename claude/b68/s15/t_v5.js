// ב83 (עדכון בן 11.11 15:30-15:45): בדיקות a5v5 - 13 שלבים, משפטי מעבר, סגירה, מדידת section_view, סרטונים ע22, אנימציות.
// שימוש: node t_v5.js http://127.0.0.1:8791/nlp/   (a5v5 = slots_v5.json עם קבצי ע22; מושווה מול a5v4)
const {chromium,devices}=require('playwright');const B=process.argv[2];
const V5=require(__dirname+"/slots_v5.json"),BEN=require(__dirname+"/ben_v5.json");
const res=[];const ok=(n,c,e="")=>{res.push(!!c);if(!c)console.log("FAIL",n,String(e).slice(0,900));else console.log("PASS",n)};
const FB="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone14,5;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/he_IL;FBOP/5]";
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
const ORDER=["פתיחה","למי מתאים","רגע לפני","מה אם","לדעת או להטמיע","הפתרון","איך מתחילים","@cta1","איך נראית המציאות","עם מה תצא","מה אומרים","תוצאות אמיתיות","למה בניתי","עוד כמה דקות עם בן","@cta2","מה יש בפנים","בונוסים","ההצעה","שאלות","@final","סגירה"];
const STAGE_OF={"פתיחה":"hook","למי מתאים":"pain","רגע לפני":"pain","מה אם":"cause","לדעת או להטמיע":"old","הפתרון":"solution","איך מתחילים":"method","@cta1":"method","איך נראית המציאות":"result","עם מה תצא":"result","מה אומרים":"proof","תוצאות אמיתיות":"proof","למה בניתי":"proof","עוד כמה דקות עם בן":"proof","@cta2":"proof","מה יש בפנים":"course","בונוסים":"offer","ההצעה":"offer","שאלות":"objections","@final":"guarantee","סגירה":"close"};
const NEW_TEXT=["עוד כמה דקות עם בן","צפו בסרטון עם קול",...Object.values(BEN.transitions),...BEN.close];
async function ctx(b,opt={}){const c=await b.newContext({...devices["iPhone 13"],...opt});const ev=[];
 await c.route("**/*",r=>{const u=r.request().url();if(/hook\.eu1\.make\.com/.test(u)){const q=new URLSearchParams(r.request().postData()||"");ev.push({ev:q.get("ev"),variant:q.get("variant"),video:q.get("video"),cta:q.get("cta"),name:q.get("name"),section:q.get("section")});return r.fulfill({status:200,body:""})}
  return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});c.ev=ev;return c;}
const split=t=>t.split(/[\s·•]+/).filter(x=>x&&!/^\d{1,2}$/.test(x));
const words=(p,skip)=>p.evaluate(skip=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;if(skip&&n.parentElement.closest(skip))continue;out.push(n.nodeValue)}return out.join(" ")},skip).then(split);
const media=p=>p.evaluate(()=>[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort());
const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
const order=p=>p.evaluate(()=>[...document.querySelectorAll("header[data-sec],section")].filter(s=>!s.closest(".sp-modal")).map(s=>s.dataset.name||(s.classList.contains("guar")?"@final":"@"+((s.querySelector("[data-cta]")||{}).dataset||{}).cta)));
const scrollAll=p=>p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=250){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,70))}});
(async()=>{const b=await chromium.launch();const P=B+"a5v5.html";
 // 1. סדר 13 השלבים, תגיות, מספור, noindex, v=a5v5
 {const c=await ctx(b);const p=await c.newPage();await p.goto(P+"?test=1",{waitUntil:"load"});await p.waitForTimeout(600);
  const o=await order(p);ok("order = Ben's 13 stages (21 blocks)",JSON.stringify(o)===JSON.stringify(ORDER),JSON.stringify(o));
  const st=await p.evaluate(()=>[...document.querySelectorAll("header[data-sec],section")].filter(s=>!s.closest(".sp-modal")).map(s=>s.dataset.stage||"-"));
  ok("every block carries its stage tag",JSON.stringify(st)===JSON.stringify(ORDER.map(k=>STAGE_OF[k])),JSON.stringify(st));
  ok("13 stages in Ben's order",JSON.stringify([...new Set(st)])===JSON.stringify(BEN.stages));
  ok("data-sec 1..n in order",await p.evaluate(()=>[...document.querySelectorAll("[data-sec]")].every((s,i)=>+s.dataset.sec===i+1)));
  ok("noindex + data-variant=a5v5 + view event a5v5",await p.evaluate(()=>!!document.querySelector('meta[name=robots][content*="noindex"]')&&document.documentElement.dataset.variant==="a5v5")&&c.ev.some(e=>e.ev==="view"&&e.variant==="a5v5"));
  ok("no <video> in the HTML beyond a5v4's 2 (existing video numbering kept)",await p.evaluate(()=>[...document.querySelectorAll("video")].filter(v=>!v.closest(".v5-loop,.v5-vid,.v5-modal")).length)===2);
  // כפתורים
  const ctas=await p.evaluate(()=>[...new Set([...document.querySelectorAll("a.cta[data-cta]")].map(a=>a.dataset.cta))]);
  ok("buy buttons = hero_main, cta1, cta2, offer, final, sticky (+ stories as today); know/peek/strip/cta3 gone",JSON.stringify(ctas)===JSON.stringify(["hero_main","cta1","cta2","offer","final","sticky","stories"]),JSON.stringify(ctas));
  ok("hero_shortcut link kept as today ('הפתיחה כמו היום')",await p.evaluate(()=>!!document.querySelector('header a.ghost[data-cta="hero_shortcut"]')));
  // משפטי המעבר
  const T=await p.evaluate(()=>[...document.querySelectorAll(".v5-tr")].map(e=>{const s=e.closest("header,section"),cs=getComputedStyle(e),bf=getComputedStyle(e,"::before");
   const blocks=[...document.querySelectorAll("header[data-sec],section")].filter(x=>!x.closest(".sp-modal"));const i=blocks.indexOf(s),nx=blocks[i+1];
   return {k:e.dataset.tr,t:e.textContent,stage:s.dataset.stage,next:nx?nx.dataset.stage:null,last:!e.nextElementSibling||s.tagName==="HEADER",w:cs.fontWeight,al:cs.textAlign,ff:cs.fontFamily===getComputedStyle(document.querySelector("p.sub")).fontFamily,line:bf.content!=="none"&&parseFloat(bf.height)<=1.5&&/254, 207, 0/.test(bf.backgroundColor)}}));
  ok("12 transitions, verbatim, in order",T.length===12&&T.every((x,i)=>x.k===String(i+1).padStart(2,"0")&&x.t===BEN.transitions[x.k]),JSON.stringify(T.map(x=>x.k+":"+x.t.slice(0,12))));
  ok("each transition ends its stage and leads into the next stage",T.every((x,i)=>x.stage===BEN.stages[i]&&x.next===BEN.stages[i+1]&&x.last),JSON.stringify(T.map(x=>[x.k,x.stage,x.next,x.last])));
  ok("transition style: centered, weight 600, same font, thin gold line above",T.every(x=>x.w==="600"&&x.al==="center"&&x.ff&&x.line),JSON.stringify(T[0]));
  ok("no Hebrew maqaf in transitions/close",![...Object.values(BEN.transitions),...BEN.close].some(t=>/־/.test(t)));
  // סגירה + אחריות
  const C=await p.evaluate(()=>{const c=document.querySelector('[data-name="סגירה"]'),g=document.querySelector("section.guar");const kids=[...c.querySelector(".wrap").children];
   return {lines:[...c.querySelectorAll(".v5-cl")].map(x=>x.textContent),finalAfter:kids.findIndex(e=>e.matches('a.cta[data-cta="final"]'))>kids.findIndex(e=>e.matches(".v5-cl-b")),guarFinal:!!g.querySelector('[data-cta="final"]'),guarH:g.querySelector("h2").textContent,close11:!!g.querySelector(".close11"),buyzone:c.hasAttribute("data-buyzone")}});
  ok("close: Ben's 2 sentences then final; guarantee section without final",JSON.stringify(C.lines)===JSON.stringify(BEN.close)&&C.finalAfter&&!C.guarFinal&&/^או שהתוכן הזה שווה לך/.test(C.guarH)&&C.close11&&C.buyzone,JSON.stringify(C));
  // הפתרון / הקורס
  const S=await p.evaluate(()=>{const s=document.querySelector('[data-name="הפתרון"]'),k=document.querySelector('[data-name="מה יש בפנים"]');const kk=[...k.querySelector(".wrap").children].map(e=>e.tagName+"."+e.className);
   return {h2:!!s.querySelector("h2"),first:s.querySelector(".wrap").firstElementChild.textContent.slice(0,14),last:s.querySelector(".v4-show").lastElementChild.textContent,kids:kk,peekBtn:!!k.querySelector('[data-cta="peek"]'),player:!!k.querySelector(".v4-player")}});
  ok("solution: Ben's text from 'כל חלק הוא צעד' to '...איך ליישם.', no heading",!S.h2&&S.first==="כל חלק הוא צעד"&&S.last==="המטרה היא שתסיים כל סרטון עם משהו חדש שאתה כבר יודע איך ליישם.",JSON.stringify(S));
  ok("course: heading, '👇 תגלול...', ע20 player, no peek button",/^H2\.[^,]*,P\.v4-show-go/.test(S.kids.join(","))&&S.player&&!S.peekBtn,JSON.stringify(S.kids));
  ok("old: no know button",await p.evaluate(()=>!document.querySelector('[data-cta="know"]')&&!!document.querySelector('[data-name="לדעת או להטמיע"] p.key')));
  // שאלות
  const F=await p.evaluate(()=>[...document.querySelectorAll('[data-name="שאלות"] .wrap > details > summary')].map(x=>x.textContent));
  ok("FAQ: Ben's 3 thoughts first, rest in existing order",JSON.stringify(F)===JSON.stringify([...BEN.faq_first,"צריך ניסיון קודם?","מקבלים גישה מיד?","שאלות נוספות"]),JSON.stringify(F));
  // מדידה: section_view לכל 13 השלבים, פעם אחת, בסדר, עם המיקום
  await scrollAll(p);await p.waitForTimeout(500);
  const SV=c.ev.filter(e=>e.ev==="section_view");
  ok("section_view for all 13 stages, once each, with stage id and position, variant a5v5",JSON.stringify(SV.map(e=>e.name))===JSON.stringify(BEN.stages)&&SV.every((e,i)=>+e.section===i+1&&e.variant==="a5v5"),JSON.stringify(SV.map(e=>e.name+":"+e.section)));
  await c.close();}
 // 1ב. a5v4: אותן תגיות על הסקשנים המקבילים, בלי שינוי תוכן
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v4.html?test=1",{waitUntil:"load"});await p.waitForTimeout(500);await scrollAll(p);await p.waitForTimeout(500);
  const SV=c.ev.filter(e=>e.ev==="section_view");
  ok("a5v4: section_view for the same 13 stage ids, once each",SV.length===13&&JSON.stringify([...SV.map(e=>e.name)].sort())===JSON.stringify([...BEN.stages].sort())&&SV.every(e=>e.variant==="a5v4"),JSON.stringify(SV.map(e=>e.name+":"+e.section)));
  await c.close();}
 // 2. קופי ומדיה מול a5v4: אותן מילים, חוץ מהטקסטים החדשים (מעברים, סגירה, 2 תוויות) ופחות הכפתורים שיצאו (know, peek, cta3)
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v4.html?test=1",{waitUntil:"load"});
  const W4=cnt(await words(p)),M4=await media(p);
  const gone=cnt(split(await p.evaluate(()=>[...document.querySelectorAll('.v4-ctab:has([data-cta="know"]),.v4-ctab:has([data-cta="peek"])'),...[...document.querySelectorAll("section.ctab")].filter(s=>s.querySelector('[data-cta="cta3"]'))].map(e=>{const o=[],w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode())o.push(n.nodeValue);return o.join(" ")}).join(" "))));
  await p.goto(P+"?test=1",{waitUntil:"load"});const W5=cnt(await words(p)),M5=await media(p);
  const allow=cnt([].concat(...NEW_TEXT.map(split)));
  const miss=Object.keys(W4).filter(k=>W4[k]-(W5[k]||0)>(gone[k]||0)),extra=Object.keys(W5).filter(k=>W5[k]-(W4[k]||0)>(allow[k]||0));
  ok("same copy as a5v4, only + Ben's transitions/close/2 labels, − removed buttons",!miss.length&&!extra.length,"missing:"+JSON.stringify(miss.slice(0,8))+" extra:"+JSON.stringify(extra.slice(0,8)));
  const posters=[V5.belief.poster,...V5.strip.map(x=>x.poster)];
  ok("same media as a5v4 (+ v5 posters)",JSON.stringify([...M4,...posters].sort())===JSON.stringify(M5),JSON.stringify(M5.filter(x=>!M4.includes(x))));
  await c.close();}
 // 3. המסך הראשון: הכפתור בפנים, בלי אנימציה, ה-LCP לא מונפש; מעבר 01 - השורה הראשונה אחרי קבוצת הכפתור
 for(const [w,h] of [[375,667],[390,844]]){const c=await ctx(b,{viewport:{width:w,height:h}});const p=await c.newPage();await p.goto(P+"?internal=1",{waitUntil:"load"});await p.waitForTimeout(800);
  const f=await p.evaluate(()=>{const s=document.querySelector('[data-sec="1"]'),q=e=>Math.round(e.getBoundingClientRect().bottom);const hid=[...document.querySelectorAll("body *")].filter(e=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0&&r.height>0&&!e.closest(".v5-loop,.sticky,.prog")&&(getComputedStyle(e).opacity==="0"||/(^|\s)(v5s|v5z|v5o|v4r)(\s|$)/.test(e.className))});
   const lcp=document.querySelector('[data-sec="1"] img[fetchpriority="high"]'),tr=document.querySelector(".hero9 .v5-tr");
   return {h1:q(s.querySelector("h1")),sub:q(s.querySelector(".sub")),cta:q(s.querySelector('[data-cta="hero_main"]')),vh:innerHeight,hidden:hid.map(e=>e.tagName+"."+e.className).slice(0,4),lcpAnim:/v5|v4r|rv/.test(lcp.className)||getComputedStyle(lcp).transitionDuration!=="0s",
    trTop:Math.round(tr.getBoundingClientRect().top),trPrev:tr.previousElementSibling.className,trNext:tr.nextElementSibling.className}});
  ok(w+"x"+h+": headline, sentence and button in the first screen; nothing hidden/animating; LCP untouched",f.h1<=f.vh&&f.sub<=f.vh&&f.cta<=f.vh&&!f.hidden.length&&!f.lcpAnim,JSON.stringify(f));
  ok(w+"x"+h+": transition 01 right after the button group (doesn't push the button), first new line after the fold",f.trPrev==="cta-bonus"&&f.trNext==="ident"&&f.trTop>f.cta&&f.trTop<f.vh+120,JSON.stringify(f));
  await c.close();}
 // 4. סרטונים: לולאה בלי קול (גם בפייסבוק ובאינסטגרם), הסרטון המלא, רק אחד מתנגן, נעצר מחוץ למסך, אירוע עם קוד
 for(const [nm,ua] of [["iphone",null],["fb",FB],["ig",IG]]){const c=await ctx(b,ua?{userAgent:ua}:{});const p=await c.newPage();await p.goto(P+"?test=1",{waitUntil:"load"});await p.waitForTimeout(2500);
  const L=await p.evaluate(()=>{const v=document.querySelector(".v5-loop video");return v?{paused:v.paused,muted:v.muted,inline:v.hasAttribute("playsinline"),loop:v.loop,t:v.currentTime,src:v.currentSrc}:null});
  ok(nm+": hero loop (ע22) plays muted, inline, looping (after the LCP image)",!!L&&!L.paused&&L.muted&&L.inline&&L.loop&&L.t>0&&/hero_loop_h1_02\.mp4$/.test(L.src),JSON.stringify(L));
  if(nm==="iphone"){
   await p.click(".v5-sound");await p.waitForTimeout(1500);
   const M=await p.evaluate(()=>{const v=document.querySelector(".v5-modal video"),l=document.querySelector(".v5-loop video");return {modal:!!v,playing:v&&!v.paused,muted:v&&v.muted,controls:v&&v.controls,loopPaused:l.paused,src:v&&v.currentSrc}});
   ok("'צפו בסרטון עם קול' opens gold_h1_02 with sound, loop pauses, event v5_gold_h1_02",M.modal&&M.playing&&!M.muted&&M.controls&&M.loopPaused&&/gold_h1_02_web\.mp4$/.test(M.src)&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.hero.code),JSON.stringify(M));
   await p.click(".v5-modal .v5-x");await p.waitForTimeout(300);
   ok("modal closes",!(await p.$(".v5-modal")));
   ok("v5 videos are poster buttons (lazy WebP poster, 4:5) - no video before a click (preload none)",await p.evaluate(()=>[...document.querySelectorAll("[data-v5src]")].every(b=>{const i=b.querySelector("img");return i&&i.loading==="lazy"&&/\.webp$/.test(i.getAttribute("src"))&&b.style.aspectRatio.replace(/\s/g,"")==="720/900"})));
   await p.evaluate(()=>{const e=document.querySelector('[data-name="מה אם"] .v5-vid');scrollTo({top:scrollY+e.getBoundingClientRect().top-80,behavior:"instant"})});await p.waitForTimeout(500);
   await p.click('[data-name="מה אם"] .v5-box');await p.waitForTimeout(1500);
   ok("stage 3: gold_h2_01 plays on click, event v5_gold_h2_01",await p.evaluate(()=>{const v=document.querySelector('[data-name="מה אם"] video');return v&&!v.paused&&/gold_h2_01_web\.mp4$/.test(v.currentSrc)})&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.belief.code));
   await p.evaluate(()=>{const e=document.querySelector(".v5-strip");scrollTo({top:scrollY+e.getBoundingClientRect().top-80,behavior:"instant"})});await p.waitForTimeout(800);
   ok("a video that leaves the screen pauses",await p.evaluate(()=>document.querySelector('[data-name="מה אם"] video').paused));
   await p.click('.v5-strip .v5-sv:nth-child(1) .v5-box');await p.waitForTimeout(1500);
   const s3=await p.evaluate(()=>{const vs=[...document.querySelectorAll("video")].filter(v=>!v.paused);return {playing:vs.length,code:vs[0]&&vs[0].closest("[data-v5code]")&&vs[0].closest("[data-v5code]").dataset.v5code}});
   ok("strip video plays, only one playing, event with its code",s3.playing===1&&s3.code===V5.strip[0].code&&c.ev.some(e=>e.ev==="video_play"&&e.video==="v5_"+V5.strip[0].code),JSON.stringify(s3));
   await p.click('.v5-strip .v5-sv:nth-child(2) .v5-box');await p.waitForTimeout(1500);
   const s4=await p.evaluate(()=>[...document.querySelectorAll("video")].filter(v=>!v.paused).map(v=>v.closest("[data-v5code]").dataset.v5code));
   ok("second strip video stops the first",JSON.stringify(s4)===JSON.stringify([V5.strip[1].code])&&c.ev.some(e=>e.video==="v5_"+V5.strip[1].code),JSON.stringify(s4));
   ok("strip: 5 videos in temp order h1/h2 alternating, sideways scroll-snap, no own button, cta2 right after",await p.evaluate(codes=>{const s=document.querySelector(".v5-strip"),sec=s.closest("section");return JSON.stringify([...s.querySelectorAll(".v5-vid")].map(x=>x.dataset.v5code))===JSON.stringify(codes)&&s.scrollWidth>s.clientWidth+100&&getComputedStyle(s).scrollSnapType.includes("x")&&!sec.querySelector("a.cta")&&!!sec.nextElementSibling.querySelector('[data-cta="cta2"]')},V5.strip.map(x=>x.code)));}
  await c.close();}
 // 5. אנימציות
 {const c=await ctx(b);const p=await c.newPage();await p.goto(P+"?internal=1",{waitUntil:"load"});await p.waitForTimeout(600);
  const pre=await p.evaluate(()=>({v5a:document.documentElement.classList.contains("v5a"),stag:document.querySelectorAll(".bx2.v5s,.v4-ko-list li.v5s").length,ko:document.querySelector(".v4-ko").classList.contains("v5z"),koOp:getComputedStyle(document.querySelector(".v4-ko")).opacity}));
  ok("animations armed below the fold (bonus cards + value rows staggered, offer box zoom)",pre.v5a&&pre.stag>=11&&pre.ko&&+pre.koOp===0,JSON.stringify(pre));
  const d=await p.evaluate(()=>[...document.querySelectorAll(".v4-ko-list li")].map(l=>getComputedStyle(l).transitionDelay.split(",")[0]));
  ok("value rows 70ms apart",d.length===6&&d.every((x,i)=>Math.abs(parseFloat(x)*1000-i*70)<2),JSON.stringify(d));
  ok("only transform/opacity are transitioned by the v5 layer",await p.evaluate(()=>[...document.querySelectorAll(".v5s,.v5z,.v5o,.v4-ko-now b")].every(e=>getComputedStyle(e).transitionProperty.split(",").every(x=>/^\s*(opacity|transform)\s*$/.test(x)))));
  ok("transitions: at most the text's fade-in (no zoom/stagger); 01 in the opening not animated",await p.evaluate(()=>{const t=[...document.querySelectorAll(".v5-tr")];const cls=e=>(e.className.match(/\b(v4r|rv|v5s|v5z|v5o)\b/)||[""])[0];
   return !cls(t[0])&&t.slice(1).every(e=>["","v4r","rv"].includes(cls(e)))}));
  await scrollAll(p);
  await p.evaluate(()=>{const e=document.querySelector(".v4-ko-tot");scrollTo({top:scrollY+e.getBoundingClientRect().top-300,behavior:"instant"})});await p.waitForTimeout(2600);
  const post=await p.evaluate(()=>({left:[...document.querySelectorAll(".v5s,.v5z,.rv,.v4r")].filter(e=>e.getBoundingClientRect().height>0&&+getComputedStyle(e).opacity<1).map(e=>e.tagName+"."+e.className).slice(0,4),
   tot:document.querySelector(".v4-ko-tot b").textContent,reg:document.querySelector(".v4-ko-reg").classList.contains("in"),now:document.querySelector(".v4-ko-now b").classList.contains("in"),nowOp:getComputedStyle(document.querySelector(".v4-ko-now b")).opacity}));
  ok("after scrolling everything revealed; price moment: 2,411 counted, strike drawn, 297 shown",!post.left.length&&post.tot==="2,411 ₪"&&post.reg&&post.now&&+post.nowOp===1,JSON.stringify(post));
  await c.close();}
 // 6. הפחתת תנועה
 {const c=await ctx(b,{reducedMotion:"reduce"});const p=await c.newPage();await p.goto(P+"?internal=1",{waitUntil:"load"});await p.waitForTimeout(1500);
  const r=await p.evaluate(()=>({v5a:document.documentElement.classList.contains("v5a"),loop:!!document.querySelector(".v5-loop video"),hidden:[...document.querySelectorAll("[data-sec] *")].filter(e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).opacity==="0").length,sound:!!document.querySelector(".v5-sound")}));
  ok("reduced motion: no loop, no v5 animations, nothing hidden, full video still available",!r.v5a&&!r.loop&&!r.hidden&&r.sound,JSON.stringify(r));await c.close();}
 // 7. בלי JS
 {const c=await b.newContext({...devices["iPhone 13"],javaScriptEnabled:false});await c.route("**/*",r=>r.request().url().startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""}));
  const p=await c.newPage();await p.goto(P+"?internal=1",{waitUntil:"load"});
  const r=await p.evaluate(()=>({hidden:[...document.querySelectorAll("[data-sec] *")].filter(e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).opacity==="0").map(e=>e.tagName+"."+e.className).slice(0,4),offer:document.querySelector(".v4-ko-now b").textContent,secs:document.querySelectorAll("[data-sec]").length,tr:document.querySelectorAll(".v5-tr").length,close:document.querySelectorAll(".v5-cl").length}));
  ok("no JS: all content visible (offer, price, all sections, transitions, close)",!r.hidden.length&&r.offer==="297 ₪"&&r.secs===ORDER.filter(k=>k[0]!=="@").length&&r.tr===12&&r.close===2,JSON.stringify(r));await c.close();}
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
