// ב68 v4: בדיקות לפני עלייה. שרת מקומי (srv.js) עם nlp/ של main ועם הפלט של build_v4.py:
//   a5v4.html / pr2v4.html (בלי נכסים), a5v4s.html / pr2v4s.html (עם slots_test.json)
// שימוש: node t_v4.js http://127.0.0.1:8791/nlp/
const {chromium,devices}=require('playwright');const B=process.argv[2];
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
const res=[];const ok=(n,c,e="")=>{res.push(!!c);if(!c||process.env.V)console.log(c?"PASS":"FAIL",n,e)};
async function ctx(b,dev){const c=await b.newContext(dev);const T=[];c.T=T;
 await c.route("**/*",r=>{const u=r.request().url();
  if(/hook\.eu1\.make\.com/.test(u)){const d=r.request().postData()||"";T.push(Object.fromEntries(new URLSearchParams(d)));return r.fulfill({status:200,body:"ok"})}
  if(/\/nlp\/checkout\.html/.test(u))return r.fulfill({status:200,contentType:"text/html",body:"<p>CHECKOUT</p>"});
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});return c}
// אותו קופי: כל המילים של הדף החי, בלי "תשלום מאובטח" והמנעול (התוספת היחידה של v4) ובלי המספור הגדול של a5
const words=p=>p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;out.push(n.nodeValue)}
 return out.join(" ").replace(/🔒/g," ").replace(/תשלום מאובטח/g," ").replace(/מתוך \d+ · /g," ").split(/[\s·•]+/).filter(x=>x&&!/^(0[0-9]|1[0-5])$/.test(x))});
const media=p=>p.evaluate(()=>[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort());
const icq=p=>p.evaluate(()=>(window.fbq&&window.fbq.queue||[]).filter(a=>a[1]==="InitiateCheckout").length);
// כל מה שבמסך הראשון בטעינה: שקיפות מלאה, בלי הזזה ובלי מעבר (כלומר מוצג מיד, בלי אנימציה)
const firstScreen=p=>p.evaluate(()=>{const bad=[];document.querySelectorAll("body *").forEach(e=>{const r=e.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||!r.width)return;if(e.closest(".sticky,#sticky"))return;
 const cs=getComputedStyle(e);if(+cs.opacity<1&&cs.visibility!=="hidden"&&!e.closest("[aria-hidden=true],.was,s"))bad.push(e.tagName+"."+e.className+" op="+cs.opacity);if(e.classList.contains("v4r"))bad.push(e.tagName+" v4r")});return bad.slice(0,5)});
(async()=>{const b=await chromium.launch();
for(const [pg,live] of [["pr2v4","pr2"],["a5v4","a5"]]){
 {const c=await ctx(b,{viewport:{width:1280,height:900}});const p=await c.newPage();
  await p.goto(B+live+".html?test=1",{waitUntil:"networkidle"});const LW=await words(p),LM=await media(p);
  await p.goto(B+pg+".html?test=1",{waitUntil:"networkidle"});const NW=await words(p),NM=await media(p);
  const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});const lc=cnt(LW),nc=cnt(NW);
  const miss=Object.keys(lc).filter(k=>(nc[k]||0)<lc[k]),extra=Object.keys(nc).filter(k=>(lc[k]||0)<nc[k]);
  ok(pg+" same copy as live (only lock + תשלום מאובטח added)",miss.length===0&&extra.length===0,"missing:"+JSON.stringify(miss.slice(0,6))+" extra:"+JSON.stringify(extra.slice(0,6)));
  ok(pg+" same images/videos as live (no empty slots in the page)",JSON.stringify(LM)===JSON.stringify(NM)&&!(await p.$(".v4-slot")),LM.length+" vs "+NM.length);
  ok(pg+" no robots noindex, no 0183/0184/0188",!(await p.evaluate(()=>!!document.querySelector('meta[name=robots]')||/018[348]/.test(document.body.innerHTML))));
  // כל כפתור (חוץ מהדביק) עם "תשלום מאובטח" ומנעול מיד אחריו
  const lk=await p.evaluate(()=>[...document.querySelectorAll("a.cta[data-checkout]")].filter(a=>a.dataset.cta!=="sticky").map(a=>{let n=a.nextElementSibling||a.parentElement.nextElementSibling,t="";for(let i=0;i<3&&n&&!n.matches("a.cta");i++,n=n.nextElementSibling)t+=n.innerHTML;return [a.dataset.cta,/class="v4-li"|<rect/.test(t)&&/תשלום מאובטח/.test(t)]}));
  ok(pg+" every CTA has lock + תשלום מאובטח right after it",lk.every(x=>x[1]),JSON.stringify(lk.filter(x=>!x[1])));
  await c.close();}
 for(const [dn,dev] of [["iphone",devices["iPhone 13"]],["android-ig",{...devices["Pixel 7"],userAgent:IG}],["desktop",{viewport:{width:1280,height:900}}]]){
  const tag=pg+"/"+dn;const c=await ctx(b,dev);const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));
  await p.goto(B+pg+".html?utm_source=facebook&utm_medium=paid&utm_content=p25",{waitUntil:"domcontentloaded"});
  ok(tag+" first screen shown at once (no hidden/animated element in view)",(await firstScreen(p)).length===0,JSON.stringify(await firstScreen(p)));
  await p.waitForLoadState("networkidle");await p.waitForTimeout(500);
  ok(tag+" reveal on: elements below the fold hidden until scrolled (page's own .rv + v4)",await p.evaluate(()=>document.documentElement.classList.contains("v4rv")&&[...document.querySelectorAll(".v4r:not(.in),.rv:not(.in)")].filter(e=>+getComputedStyle(e).opacity<1).length>3));
  const fq=await p.evaluate(()=>(window.fbq&&window.fbq.queue||[]).map(a=>[...a].slice(0,2).join(":")));
  ok(tag+" pixel: 2 inits, PageView once, ViewContent once",fq.filter(x=>x.startsWith("init:")).length===2&&fq.filter(x=>x==="track:PageView").length===1&&fq.filter(x=>x==="track:ViewContent").length===1,fq.join(","));
  const vw=c.T.filter(t=>t.ev==="view");ok(tag+" view event with new variant",vw.length===1&&vw[0].variant===pg,JSON.stringify(vw.map(v=>v.variant)));
  const fs=await p.evaluate(()=>{const a=document.querySelector('[data-sec="1"] [data-cta="hero_main"]').getBoundingClientRect();return {cta:Math.round(a.bottom),h:innerHeight}});
  if(dn!=="desktop") ok(tag+" price + CTA in first screen",fs.cta<=fs.h,JSON.stringify(fs));
  const order=await p.evaluate(()=>[...document.querySelectorAll("[data-sec]")].map(s=>s.dataset.sec+":"+s.dataset.name));
  const OI=pg==="a5v4"?3:2;
  ok(tag+" order as v3 (offer: pr2 3, a5 4), numbering 1..n",order[OI]===(OI+1)+":ההצעה"&&order.every((x,i)=>x.startsWith((i+1)+":")),order.slice(0,5).join(" | "));
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}});await p.waitForTimeout(3000);
  {const left=await p.evaluate(()=>[...document.querySelectorAll(".v4r,.rv")].filter(e=>e.getBoundingClientRect().height>0&&+getComputedStyle(e).opacity<1).map(e=>e.tagName+"."+e.className));
  ok(tag+" after scrolling everything revealed",left.length===0,JSON.stringify(left.slice(0,4)));}
  const secEv=c.T.filter(t=>t.ev==="section").map(t=>t.section+":"+t.name);ok(tag+" section events in new order",secEv.includes((OI+1)+":ההצעה"),secEv.slice(0,5).join(","));
  await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(200);
  const href=await p.getAttribute('[data-sec="1"] [data-cta="hero_main"]',"href");const q=new URL(href,B).searchParams;
  ok(tag+" checkout link v/utm_content/sid",q.get("v")===pg&&q.get("utm_content")==="p25"&&!!q.get("sid"),href.slice(0,120));
  await p.click('[data-sec="1"] [data-cta="hero_main"]');await p.waitForURL(/checkout\.html/);
  const ctaEv=c.T.filter(t=>t.ev==="cta_click");ok(tag+" cta_click event at_section=1, new variant",ctaEv.length===1&&ctaEv[0].at_section==="1"&&ctaEv[0].variant===pg,JSON.stringify(ctaEv.map(t=>[t.at_section,t.variant])));
  await p.goBack({waitUntil:"networkidle"});await p.waitForTimeout(300);
  const ss=await p.evaluate(()=>sessionStorage.getItem("nlp_ic"));
  await p.evaluate(()=>{document.querySelectorAll("a[data-checkout]").forEach(a=>a.addEventListener("click",e=>e.preventDefault()))});
  await p.evaluate(()=>document.querySelectorAll("a[data-checkout]")[1].click());
  ok(tag+" InitiateCheckout not again after returning in same tab",ss==="1"&&(await icq(p))===0,"ss="+ss+" ic="+(await icq(p)));
  ok(tag+" no horizontal scroll",!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)),await p.evaluate(()=>document.documentElement.scrollWidth+">"+innerWidth));
  ok(tag+" no JS errors",errs.length===0,errs.join("|"));
  await c.close();}
 // הפחתת תנועה: שום דבר לא מוסתר ושום דבר לא זז
 {const c=await ctx(b,{...devices["iPhone 13"],reducedMotion:"reduce"});const p=await c.newPage();await p.goto(B+pg+".html?utm_content=p25",{waitUntil:"networkidle"});
  const st=await p.evaluate(()=>({v4rv:document.documentElement.classList.contains("v4rv"),hidden:[...document.querySelectorAll(".rv,.v4r,.hero8 .copy>*,.hero8 .visual")].filter(e=>+getComputedStyle(e).opacity<1).length,smooth:getComputedStyle(document.documentElement).scrollBehavior}));
  await p.evaluate(()=>document.querySelector('[data-cta="offer"]').scrollIntoView());await p.waitForTimeout(800);
  const sh=await p.evaluate(()=>[...document.querySelectorAll("a.cta")].some(a=>a.classList.contains("v4-shine")||getComputedStyle(a,"::after").animationName!=="none"));
  ok(pg+" reduced motion: nothing hidden, no shine, no smooth scroll",!st.v4rv&&st.hidden===0&&!sh&&st.smooth==="auto",JSON.stringify(st)+" shine="+sh);await c.close();}
 // בלי IntersectionObserver: שום דבר לא מוסתר
 {const c=await ctx(b,devices["iPhone 13"]);await c.addInitScript(()=>{delete window.IntersectionObserver});const p=await c.newPage();await p.goto(B+pg+".html?utm_content=p25",{waitUntil:"networkidle"});
  ok(pg+" without IntersectionObserver nothing hidden",await p.evaluate(()=>!document.documentElement.classList.contains("v4rv")&&document.querySelectorAll(".v4r").length===0));await c.close();}
 for(const qs of ["fbclid=IwZXh0bgNhZW0yNTYyODEwNDA1NTgAAR","test=1"]){const c=await ctx(b,devices["iPhone 13"]);const p=await c.newPage();await p.goto(B+pg+".html?"+qs,{waitUntil:"networkidle"});
  const st=await p.evaluate(()=>({noPix:window.__noPix,fbq:typeof window.fbq}));ok(pg+" ב23: no pixel for "+qs.slice(0,12),st.noPix===true&&st.fbq==="undefined",JSON.stringify(st));await c.close();}
 {const c=await ctx(b,devices["iPhone 13"]);const p=await c.newPage();await p.goto(B+pg+".html?utm_content=p25",{waitUntil:"networkidle"});
  await p.evaluate(()=>{document.querySelectorAll("a[data-checkout]").forEach(a=>a.addEventListener("click",e=>e.preventDefault()))});
  await p.evaluate(()=>{const a=document.querySelectorAll("a[data-checkout]");a[0].click();a[a.length-1].click()});
  const n=await icq(p);ok(pg+" InitiateCheckout once for 2 clicks",n===1,"n="+n);await c.close();}
 // המקומות לנכסים (עם slots_test.json): טעינה עצלה, גודל קבוע, הסרטון נטען רק בלחיצה, video_play עם שם המקום
 {const c=await ctx(b,devices["iPhone 13"]);const vreq=[];c.on("request",r=>{if(/\.mp4/.test(r.url()))vreq.push(r.url())});const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));
  await p.goto(B+pg+"s.html?utm_content=p25",{waitUntil:"networkidle"});
  const sl=await p.evaluate(()=>[...document.querySelectorAll(".v4-slot")].map(f=>{const s=f.closest("[data-sec]");const im=f.querySelector("img");return {k:f.dataset.slot,sec:s&&s.dataset.name,lazy:im&&im.loading,wh:im&&!!(im.getAttribute("width")&&im.getAttribute("height")),ar:f.querySelector(".v4-box").style.aspectRatio,complete:im&&im.complete&&im.naturalWidth>0}}));
  ok(pg+" slots placed (t15+wa in testimonials, trial in drop point 2)",sl.length===3&&sl[0].k==="t15"&&/עדויות|מה אומרים/.test(sl.find(x=>x.k==="t15").sec)&&/עדויות|מה אומרים/.test(sl.find(x=>x.k==="wa").sec)&&/הבעיה|לדעת או להטמיע/.test(sl.find(x=>x.k==="trial").sec),JSON.stringify(sl));
  ok(pg+" slot images lazy with width/height + aspect-ratio box",sl.every(x=>x.lazy==="lazy"&&x.wh&&/\d+ \/ \d+/.test(x.ar)),JSON.stringify(sl.map(x=>[x.k,x.lazy,x.wh,x.ar])));
  ok(pg+" t15 headline above the video (Ben 10.11), nothing about buying the course",await p.evaluate(()=>{const h=document.querySelector('[data-slot="t15"] .v4-slot-h');return !!h&&h.textContent==="אנשים בדיוק כמוך, שבחרו לעשות צעד עם בן"&&h.nextElementSibling.classList.contains("v4-box")}));
  ok(pg+" no video downloaded before click",vreq.length===0,vreq.join(","));
  const before=await p.evaluate(()=>{const b=document.querySelector('[data-slot="t15"] .v4-box');b.scrollIntoView({block:"center"});return Math.round(b.getBoundingClientRect().height)});await p.waitForTimeout(600);
  await p.click('[data-slot="t15"] .v4-box');await p.waitForTimeout(800);
  const after=await p.evaluate(()=>{const v=document.querySelector('[data-slot="t15"] video');return v?{h:Math.round(v.getBoundingClientRect().height),src:v.getAttribute("src"),controls:v.controls}:null});
  ok(pg+" click plays the slot video in place, same height",after&&after.src==="assets/t1.mp4"&&after.controls&&Math.abs(after.h-before)<=2,JSON.stringify([before,after]));
  const vp=c.T.filter(t=>t.ev==="video_play");ok(pg+" video_play sent with slot name",vp.length===1&&vp[0].video==="slot_t15",JSON.stringify(vp.map(t=>t.video)));
  ok(pg+"s no JS errors",errs.length===0,errs.join("|"));await c.close();}
}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
