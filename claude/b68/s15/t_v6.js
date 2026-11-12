// ב85 (אישור בן 09:49): בדיקות a5v6 מול a5v4. a5v6 = a5v4 + (1) ע21 בין 👇 לבין "הצצה פנימה" (2) כפתורים ירוקים, רטט כל 2.5 ש', ברק, צמוד לאורך הגלילה.
// שימוש: node t_v6.js http://127.0.0.1:8791/nlp/ [go.html]   (a5v6s = אותה בנייה עם קובץ סיור לבדיקה)
const {chromium,devices}=require('playwright');const fs=require('fs');const B=process.argv[2],GO=process.argv[3];
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log((c?"PASS ":"FAIL ")+n+(c?"":" "+String(e).slice(0,700)))};
async function ctx(b,opt={}){const c=await b.newContext({...devices["iPhone 13"],...opt});const ev=[];
 await c.route("**/*",r=>{const u=r.request().url();if(/hook\.eu1\.make\.com/.test(u)){const q=new URLSearchParams(r.request().postData()||"");ev.push({ev:q.get("ev"),variant:q.get("variant"),cta:q.get("cta"),name:q.get("name")});return r.fulfill({status:200,body:""})}
  return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});c.ev=ev;return c;}
const words=p=>p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;out.push(n.nodeValue)}return out.join(" ").split(/[\s·•]+/).filter(Boolean)});
const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
const snap=p=>p.evaluate(()=>({order:[...document.querySelectorAll("header[data-sec],section")].filter(s=>!s.closest(".sp-modal")).map(s=>(s.dataset.name||s.className)+"|"+(s.dataset.stage||"")),
 media:[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort(),
 ctas:[...document.querySelectorAll("a.cta")].map(a=>[a.dataset.cta,(a.getAttribute("href")||"").replace(/a5v[46]/g,"PAGE").replace(/sid=[^&]*/,"sid="),a.hasAttribute("data-checkout"),a.innerHTML.replace(/<svg[\s\S]*?<\/svg>/g,"")].join("|")),
 sec:[...document.querySelectorAll("[data-sec]")].map(s=>s.dataset.sec).join(",")}));
const scrollAll=p=>p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,60))}});
const recShk=p=>p.evaluate(()=>{window.__s=[];new MutationObserver(m=>m.forEach(x=>{if(x.target.classList.contains("v6shk"))window.__s.push({k:x.target.dataset.cta,t:Math.round(performance.now()),a:getComputedStyle(x.target).animationName})})).observe(document.body,{subtree:true,attributes:true,attributeFilter:["class"]})});
(async()=>{const b=await chromium.launch();
 // 1. מבנה, קופי ומדיה מול a5v4 - בלי שום הבדל
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v4.html?test=1",{waitUntil:"load"});const S4=await snap(p),W4=cnt(await words(p));
  await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await p.waitForTimeout(500);const S6=await snap(p),W6=cnt(await words(p));
  ok("same sections, order, numbering and stage tags as a5v4",JSON.stringify(S4.order)===JSON.stringify(S6.order)&&S4.sec===S6.sec,JSON.stringify(S6.order));
  ok("same media as a5v4 (no ע21 file yet)",JSON.stringify(S4.media)===JSON.stringify(S6.media));
  ok("same buttons: data-cta, checkout links, data-checkout and inner text incl. 'תשלום מאובטח' with the lock",JSON.stringify(S4.ctas)===JSON.stringify(S6.ctas),JSON.stringify(S6.ctas.filter((x,i)=>x!==S4.ctas[i])));
  const keys=[...new Set(Object.keys(W4).concat(Object.keys(W6)))],diff={};keys.forEach(k=>{const d=(W6[k]||0)-(W4[k]||0);if(d)diff[k]=d});
  ok("copy identical to a5v4 (word by word)",!Object.keys(diff).length,JSON.stringify(diff));
  ok("noindex + data-variant=a5v6 + view event a5v6",await p.evaluate(()=>!!document.querySelector('meta[name=robots][content*="noindex"]')&&document.documentElement.dataset.variant==="a5v6")&&c.ev.some(e=>e.ev==="view"&&e.variant==="a5v6"));
  ok("nothing from a5v5 (stages order, transitions, hero loop, strip)",await p.evaluate(()=>!document.querySelector(".v5-tr,.v5-loop,.v5-strip,.v5-sound,[data-name='סגירה'],[data-name='הפתרון']")));
  const G=await p.evaluate(()=>[...document.querySelectorAll("a.cta")].map(a=>{const cs=getComputedStyle(a),pay=a.querySelector(".v4-pay");return {k:a.dataset.cta,bg:cs.backgroundColor,img:cs.backgroundImage,col:getComputedStyle(a.querySelector(".ct-t,.st-txt")||a).color,pay:pay?pay.textContent:"",payCol:pay?getComputedStyle(pay).color:""}}));
  ok("all 10 join buttons incl. sticky green #18845A with white text",G.length===10&&G.every(x=>x.bg==="rgb(24, 132, 90)"&&x.img==="none"&&x.col==="rgb(255, 255, 255)"),JSON.stringify(G.filter(x=>x.bg!=="rgb(24, 132, 90)"||x.col!=="rgb(255, 255, 255)")));
  ok("'תשלום מאובטח' with the lock stays inside every button, as in a5v4 (light on green)",G.every(x=>x.pay==="תשלום מאובטח"&&/rgba?\(255, 255, 255/.test(x.payCol)),JSON.stringify(G.map(x=>[x.k,x.pay,x.payCol])));
  ok("button animations use only transform/opacity (v6shk, pulse, shine)",await p.evaluate(()=>{const ks=[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch(e){return []}}).filter(r=>r.type===7&&/^(v6shk|b45pulse|v4shine2?)$/.test(r.name));
   return ks.length>=3&&ks.every(k=>[...k.cssRules].every(f=>[...f.style].every(pr=>/^(transform|opacity|translate|rotate|scale)$/.test(pr))))&&!ks.some(k=>k.name==="ring")}));
  await scrollAll(p);await p.waitForTimeout(400);
  const SV=c.ev.filter(e=>e.ev==="section_view"&&e.variant==="a5v6");
  ok("section_view: 13 stages once each, variant a5v6",SV.length===13&&new Set(SV.map(e=>e.name)).size===13,SV.length);
  await c.close();}
 // 2. ע21 במקום הנכון (גרסת בדיקה עם קובץ)
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v6s.html?test=1",{waitUntil:"load"});
  const T=await p.evaluate(()=>{const s=document.querySelector('[data-name="מה יש בפנים"]'),t=s.querySelector("figure.v4-tour"),go=[...s.querySelectorAll("p")].find(x=>/^👇 תגלול ותראה בעצמך מה מחכה לך בפנים\.$/.test(x.textContent.trim())),h=[...s.querySelectorAll("h3")].find(x=>x.textContent.trim()==="הצצה פנימה");
   const all=[...document.querySelectorAll("*")],ix=e=>all.indexOf(e);return {t:!!t,go:!!go,h:!!h,between:!!(t&&go&&h)&&ix(go)<ix(t)&&ix(t)<ix(h),onlyOne:document.querySelectorAll("figure.v4-tour").length}});
  ok("ע21 exactly between '👇 תגלול ותראה בעצמך...' and 'הצצה פנימה'",T.between&&T.onlyOne===1,JSON.stringify(T));
  await p.evaluate(()=>{const e=document.querySelector("figure.v4-tour");scrollTo({top:scrollY+e.getBoundingClientRect().top-100,behavior:"instant"})});await p.waitForTimeout(2500);
  ok("ע21 plays muted inline when on screen (a5v4 tour logic)",await p.evaluate(()=>{const v=document.querySelector("figure.v4-tour video");return !!v&&!v.paused&&v.muted}));
  await c.close();}
 // 3. רטט כל 2.5 ש', ברק, כפתור צמוד לאורך הגלילה
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await recShk(p);
  await p.waitForTimeout(5600);let s=await p.evaluate(()=>window.__s);const h=[];s.filter(x=>x.k==="hero_main").sort((a,b)=>a.t-b.t).forEach(x=>{if(!h.length||x.t-h[h.length-1].t>1000)h.push(x)}); /* תחילת כל רטט (אותה הפעלה נרשמת כמה פעמים) */
  ok("on-screen button shakes (v6shk) every ~2.5s",h.length>=2&&h.every(x=>x.a==="v6shk")&&Math.abs((h[1].t-h[0].t)-2500)<400,JSON.stringify(s));
  ok("shine on the on-screen button (appears and fades every few seconds)",await p.evaluate(()=>{const a=document.querySelector('[data-cta="hero_main"]'),af=getComputedStyle(a,"::after");return a.classList.contains("v4-shine")&&/v4shine2/.test(af.animationName)&&af.animationIterationCount==="infinite"}));
  await p.evaluate(()=>scrollTo({top:document.body.scrollHeight*0.3,behavior:"instant"}));await p.waitForTimeout(3000);s=await p.evaluate(()=>window.__s);
  ok("sticky shown after the hero, shakes and shines",await p.evaluate(()=>{const st=document.getElementById("sticky"),a=st.querySelector("a.cta");return st.classList.contains("on")&&a.classList.contains("v4-shine")&&/v4shine2/.test(getComputedStyle(a,"::after").animationName)})&&s.some(x=>x.k==="sticky"),JSON.stringify(s.slice(-4)));
  for(const sel of ["#offer .v4-ko-now","section.guar [data-cta=\"final\"]",".ctab [data-cta=\"cta1\"]"]){await p.evaluate(s=>{const e=document.querySelector(s);scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight/2,behavior:"instant"})},sel);await p.waitForTimeout(500);
   ok("sticky stays on at "+sel,await p.evaluate(()=>{const st=document.getElementById("sticky");return st.classList.contains("on")&&st.getAttribute("aria-hidden")==="false"&&st.getBoundingClientRect().top<innerHeight}));}
  await p.evaluate(()=>scrollTo({top:0,behavior:"instant"}));await p.waitForTimeout(400);
  ok("sticky hidden again at the top (hero button visible), as in a5v4",await p.evaluate(()=>!document.getElementById("sticky").classList.contains("on")));
  await c.close();
  for(const [nm,opt,q] of [["reduced motion",{reducedMotion:"reduce"},""],["?shake=0",{},"&shake=0"]]){const c2=await ctx(b,opt);const p2=await c2.newPage();await p2.goto(B+"a5v6.html?test=1"+q,{waitUntil:"load"});await recShk(p2);await p2.waitForTimeout(3000);
   const r=await p2.evaluate(()=>({n:window.__s.length,shine:getComputedStyle(document.querySelector('[data-cta="hero_main"]'),"::after").animationName}));
   ok(nm+": no shake"+(nm==="reduced motion"?", no shine":""),r.n===0&&(nm!=="reduced motion"||r.shine==="none"),JSON.stringify(r));await c2.close();}}
 // 4. לחיצה: cta_click והמעבר לסליקה עם v=a5v6
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await p.waitForTimeout(400);
  await Promise.all([p.waitForURL(/checkout\.html/,{timeout:8000}).catch(()=>{}),p.click('[data-cta="hero_main"]')]);
  ok("click → cta_click hero_main and checkout with v=a5v6",c.ev.some(e=>e.ev==="cta_click"&&e.cta==="hero_main"&&e.variant==="a5v6")&&/checkout\.html/.test(p.url())&&/a5v6/.test(decodeURIComponent(p.url())),p.url());
  await c.close();}
 // 5. המסך הראשון
 for(const [w,h] of [[375,667],[390,844]]){const c=await ctx(b,{viewport:{width:w,height:h}});const p=await c.newPage();await p.goto(B+"a5v6.html?internal=1",{waitUntil:"load"});await p.waitForTimeout(500);
  const f=await p.evaluate(()=>({cta:Math.round(document.querySelector('[data-cta="hero_main"]').getBoundingClientRect().bottom),vh:innerHeight}));
  ok(w+"x"+h+": join button in the first screen",f.cta<=f.vh,JSON.stringify(f));await c.close();}
 if(GO)ok("a5v6 not referenced in go.html",!/a5v6/.test(fs.readFileSync(GO,"utf8")));
 {const c=await ctx(b);const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));await p.goto(B+"a5v6.html?test=1",{waitUntil:"load"});await scrollAll(p);await p.waitForTimeout(500);
  ok("no JS errors",!errs.length,errs.join(" | "));await c.close();}
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
