// ב85: בדיקות a5v6 מול a5v4. שימוש: node t_v6.js http://127.0.0.1:8791/nlp/ [go.html המקומי של main]
const {chromium,devices}=require('playwright');const fs=require('fs');const B=process.argv[2],GO=process.argv[3];
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log((c?"PASS ":"FAIL ")+n+(c?"":" "+String(e).slice(0,700)))};
async function ctx(b,opt={}){const c=await b.newContext({...devices["iPhone 13"],...opt});const ev=[];
 await c.route("**/*",r=>{const u=r.request().url();if(/hook\.eu1\.make\.com/.test(u)){const q=new URLSearchParams(r.request().postData()||"");ev.push({ev:q.get("ev"),variant:q.get("variant"),cta:q.get("cta"),name:q.get("name")});return r.fulfill({status:200,body:""})}
  return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});c.ev=ev;return c;}
const words=p=>p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;out.push(n.nodeValue)}return out.join(" ").split(/[\s·•]+/).filter(Boolean)});
const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
const snap=p=>p.evaluate(()=>({order:[...document.querySelectorAll("header[data-sec],section")].filter(s=>!s.closest(".sp-modal")).map(s=>(s.dataset.name||s.className)+"|"+(s.dataset.stage||"")),
 media:[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort(),
 ctas:[...document.querySelectorAll("a.cta")].map(a=>[a.dataset.cta,(a.getAttribute("href")||"").replace(/a5v[46]/g,"PAGE").replace(/sid=[^&]*/,"sid="),a.hasAttribute("data-checkout")].join("|")),
 sec:[...document.querySelectorAll("[data-sec]")].map(s=>s.dataset.sec).join(",")}));
const scrollAll=p=>p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,60))}});
(async()=>{const b=await chromium.launch();
 // 1. מבנה, קופי ומדיה מול a5v4
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v4.html?test=1",{waitUntil:"load"});const S4=await snap(p),W4=cnt(await words(p));
  await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await p.waitForTimeout(500);const S6=await snap(p),W6=cnt(await words(p));
  ok("same sections, order, numbering and stage tags as a5v4",JSON.stringify(S4.order)===JSON.stringify(S6.order)&&S4.sec===S6.sec,JSON.stringify(S6.order));
  ok("same media as a5v4",JSON.stringify(S4.media)===JSON.stringify(S6.media));
  ok("same buttons: data-cta, checkout links and data-checkout identical",JSON.stringify(S4.ctas)===JSON.stringify(S6.ctas),JSON.stringify(S6.ctas));
  const keys=[...new Set(Object.keys(W4).concat(Object.keys(W6)))],diff={};keys.forEach(k=>{const d=(W6[k]||0)-(W4[k]||0);if(d)diff[k]=d});
  ok("copy identical except '🔒' x9 added (lock line under each in-page button; sticky has none, like pr2) and the in-button 'תשלום מאובטח' of the sticky gone",JSON.stringify(diff)===JSON.stringify({"תשלום":-1,"מאובטח":-1,"🔒":9})||JSON.stringify(diff)===JSON.stringify({"🔒":9,"תשלום":-1,"מאובטח":-1}),JSON.stringify(diff));
  ok("noindex + data-variant=a5v6 + view event a5v6",await p.evaluate(()=>!!document.querySelector('meta[name=robots][content*="noindex"]')&&document.documentElement.dataset.variant==="a5v6")&&c.ev.some(e=>e.ev==="view"&&e.variant==="a5v6"));
  ok("no 13-stage order / transitions / hero loop / strip",await p.evaluate(()=>!document.querySelector(".v5-tr,.v5-loop,.v5-strip,.v5-sound,[data-name='סגירה'],[data-name='הפתרון']")));
  // אזור הקורס וההצעה בסדר של בן
  const A=await p.evaluate(()=>{const pos=e=>e?[...document.querySelectorAll("*")].indexOf(e):-1;const sec=document.querySelector('[data-name="מה יש בפנים"]'),bon=document.querySelector('[data-name="בונוסים"]'),off=document.getElementById("offer");
   const o=[sec.querySelector("h2"),[...sec.querySelectorAll("p")].find(x=>/👇 תגלול ותראה בעצמך/.test(x.textContent)),sec.querySelector(".v4-peek .v4-player"),bon.querySelector("h2"),bon.querySelector("article.bx2"),off.querySelector(".v4-ko-tot"),off.querySelector(".v4-ko-reg s"),off.querySelector(".v4-ko-now b"),off.querySelector('a.cta[data-cta="offer"]')];
   return {all:o.every(Boolean),inc:o.every((e,i)=>!i||pos(e)>pos(o[i-1])),h2:sec.querySelector("h2").textContent,bh2:bon.querySelector("h2").textContent,cards:bon.querySelectorAll("article.bx2 .bx2-val s").length,tot:off.querySelector(".v4-ko-tot").textContent,now:off.querySelector(".v4-ko-now b").textContent,adj:sec.nextElementSibling===bon&&bon.nextElementSibling===off}});
  ok("course + offer in Ben's order: מה יש בפנים, 👇, (ע21), ע20, 'וזה עוד לפני שדיברנו...', 5 bonuses with values, total, struck price, 297, button",A.all&&A.inc&&A.adj&&A.bh2==="וזה עוד לפני שדיברנו על כל הבונוסים שמחכים לך במסגרת ההצעה…"&&A.cards===5&&/2,411/.test(A.tot)&&A.now==="297 ₪",JSON.stringify(A));
  // הכפתורים הירוקים
  const G=await p.evaluate(()=>[...document.querySelectorAll("a.cta")].map(a=>{const cs=getComputedStyle(a),af=getComputedStyle(a,"::after");return {k:a.dataset.cta,bg:cs.backgroundColor,img:cs.backgroundImage,col:cs.color,rad:cs.borderRadius,fw:cs.fontWeight,inPay:!!a.querySelector(".v4-pay"),after:af.content,lock:a.closest(".sticky,.sp-modal")?null:(a.nextElementSibling&&a.nextElementSibling.matches("p.v6-lock")?a.nextElementSibling.textContent:"")}}));
  ok("all join buttons green #18845A, white bold text, radius 14, no gold gradient/shine, nothing inside the button",G.length===10&&G.every(x=>x.bg==="rgb(24, 132, 90)"&&x.img==="none"&&x.col==="rgb(255, 255, 255)"&&x.rad==="14px"&&+x.fw>=800&&!x.inPay&&(x.after==="none"||x.after==="normal")),JSON.stringify(G.filter(x=>x.bg!=="rgb(24, 132, 90)"||x.inPay).slice(0,3)));
  ok("'🔒 תשלום מאובטח' right under every in-page button (stories modal + sticky excluded)",G.filter(x=>x.lock!==null).every(x=>x.lock==="🔒 תשלום מאובטח")&&G.filter(x=>x.lock!==null).length===8,JSON.stringify(G.map(x=>[x.k,x.lock])));
  ok("shk + ring keyframes identical to pr2",await p.evaluate(()=>{const ks=[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch(e){return []}}).filter(r=>r.type===7);const n=ks.map(r=>r.name);return n.includes("shk")&&n.includes("ring")}));
  await scrollAll(p);await p.waitForTimeout(400);
  const SV=c.ev.filter(e=>e.ev==="section_view"&&e.variant==="a5v6");
  ok("section_view: 13 stages once each, variant a5v6",SV.length===13&&new Set(SV.map(e=>e.name)).size===13&&SV.every(e=>e.variant==="a5v6"),SV.length);
  await c.close();}
 // 2. רטט: הכפתור במסך ואחר כך הכפתור הצמוד; כבוי בהפחתת תנועה ו-?shake=0
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});
  await p.evaluate(()=>{window.__s=[];new MutationObserver(m=>m.forEach(x=>{if(x.target.classList.contains("shk"))window.__s.push(x.target.dataset.cta+"|"+[...new Set(getComputedStyle(x.target).animationName.split(", "))].join("+"))})).observe(document.body,{subtree:true,attributes:true,attributeFilter:["class"]})});
  await p.waitForTimeout(4600);let s=await p.evaluate(()=>window.__s);
  ok("on-screen button shakes with shk+ring after ~4s",s.some(x=>/^hero_main\|shk\+ring$/.test(x)),JSON.stringify(s));
  await p.evaluate(()=>scrollTo({top:document.body.scrollHeight*0.35,behavior:"instant"}));await p.waitForTimeout(4600);s=await p.evaluate(()=>window.__s);
  ok("sticky button shakes too when shown",s.some(x=>/^sticky\|/.test(x))&&await p.evaluate(()=>document.getElementById("sticky").classList.contains("on")),JSON.stringify(s));
  ok("sticky button green, 1:1 with pr2 sticky (no lock line)",await p.evaluate(()=>{const a=document.querySelector(".sticky a.cta");return getComputedStyle(a).backgroundColor==="rgb(24, 132, 90)"&&!document.querySelector(".sticky .v6-lock")}));
  await c.close();
  for(const [nm,opt,q] of [["reduced motion",{reducedMotion:"reduce"},""],["?shake=0",{},"&shake=0"]]){const c2=await ctx(b,opt);const p2=await c2.newPage();await p2.goto(B+"a5v6.html?test=1"+q,{waitUntil:"load"});
   await p2.evaluate(()=>{window.__s=0;new MutationObserver(m=>m.forEach(x=>{if(x.target.classList.contains("shk"))window.__s++})).observe(document.body,{subtree:true,attributes:true,attributeFilter:["class"]})});await p2.waitForTimeout(4600);
   ok(nm+": no shake",await p2.evaluate(()=>window.__s)===0);await c2.close();}}
 // 3. לחיצה: אירוע cta_click והמעבר לסליקה עם v=a5v6
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await p.waitForTimeout(400);
  await Promise.all([p.waitForURL(/checkout\.html/,{timeout:8000}).catch(()=>{}),p.click('[data-cta="hero_main"]')]);
  ok("click → cta_click hero_main and checkout with the page variant",c.ev.some(e=>e.ev==="cta_click"&&e.cta==="hero_main"&&e.variant==="a5v6")&&/checkout\.html/.test(p.url())&&/a5v6/.test(decodeURIComponent(p.url())),p.url());
  await c.close();}
 // 4. המסך הראשון
 for(const [w,h] of [[375,667],[390,844]]){const c=await ctx(b,{viewport:{width:w,height:h}});const p=await c.newPage();await p.goto(B+"a5v6.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(500);
  const f=await p.evaluate(()=>({cta:Math.round(document.querySelector('[data-cta="hero_main"]').getBoundingClientRect().bottom),vh:innerHeight}));
  ok(w+"x"+h+": join button in the first screen",f.cta<=f.vh,JSON.stringify(f));await c.close();}
 // 5. לא ב-go.html
 if(GO)ok("a5v6 not referenced in go.html",!/a5v6/.test(fs.readFileSync(GO,"utf8")));
 // 6. בלי שגיאות JS
 {const c=await ctx(b);const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await scrollAll(p);await p.waitForTimeout(500);
  ok("no JS errors",!errs.length,errs.join(" | "));await c.close();}
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
