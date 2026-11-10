// ב68 v3: בדיקות לפני עלייה. שרת מקומי עם nlp/ של main ועם pr2v3.html ו-a5v3.html מ-build_v3.py.
// שימוש: node t68.js http://127.0.0.1:8790/nlp/
const {chromium,devices}=require('playwright');const B=process.argv[2];
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
const res=[];const ok=(n,c,e="")=>{res.push(!!c);if(!c||process.env.V)console.log(c?"PASS":"FAIL",n,e)};
async function ctx(b,dev){const c=await b.newContext(dev);const T=[];c.T=T;
 await c.route("**/*",r=>{const u=r.request().url();
  if(/hook\.eu1\.make\.com/.test(u)){const d=r.request().postData()||"";T.push(Object.fromEntries(new URLSearchParams(d)));return r.fulfill({status:200,body:"ok"})}
  if(/\/nlp\/checkout\.html/.test(u))return r.fulfill({status:200,contentType:"text/html",body:"<p>CHECKOUT</p>"});
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});return c}
const texts=p=>p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const t=n.nodeValue.replace(/\s+/g," ").trim();if(t&&!n.parentElement.closest("script,style,noscript"))out.push(t)}return out});
const media=p=>p.evaluate(()=>[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort());
const icq=p=>p.evaluate(()=>(window.fbq&&window.fbq.queue||[]).filter(a=>a[1]==="InitiateCheckout").length);
(async()=>{const b=await chromium.launch();
for(const [pg,live] of [["pr2v3","pr2"],["a5v3","a5"]]){
 {const c=await ctx(b,{viewport:{width:1280,height:900}});const p=await c.newPage();
  await p.goto(B+live+".html?test=1",{waitUntil:"networkidle"});const LT=await texts(p),LM=await media(p);
  await p.goto(B+pg+".html?test=1",{waitUntil:"networkidle"});const NT=await texts(p),NM=await media(p);
  const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});const lc=cnt(LT),nc=cnt(NT);
  const num=x=>/^(0[0-9]|1[0-5])$/.test(x)||/^מתוך \d+ · /.test(x);
  const miss=Object.keys(lc).filter(k=>(nc[k]||0)<lc[k]&&!num(k)),extra=Object.keys(nc).filter(k=>(lc[k]||0)<nc[k]&&!num(k));
  const sec7=pg==="a5v3"?miss.filter(m=>/לפני שאתה ממשיך למחיר|האם תהיה מרוצה|הגיע הזמן להתחיל לעבוד על השורש/.test(m)):[];
  const missReal=miss.filter(m=>!sec7.includes(m));
  ok(pg+" same copy as live (a5: only sec 7 removed)",missReal.length===0&&extra.length===0,"missing:"+JSON.stringify(missReal.slice(0,5))+" extra:"+JSON.stringify(extra.slice(0,5))+" sec7:"+sec7.length);
  if(process.env.V) console.log("   removed (sec 7):",JSON.stringify(sec7));
  ok(pg+" same images/videos/testimonials as live",JSON.stringify(LM)===JSON.stringify(NM),LM.length+" vs "+NM.length);
  ok(pg+" no robots noindex",!(await p.evaluate(()=>!!document.querySelector('meta[name=robots]'))));
  ok(pg+" no testimonials 0183/0184/0188",!(await p.evaluate(()=>/018[348]/.test(document.body.innerHTML))));
  await c.close();}
 for(const [dn,dev] of [["iphone",devices["iPhone 13"]],["android-ig",{...devices["Pixel 7"],userAgent:IG}],["desktop",{viewport:{width:1280,height:900}}]]){
  const tag=pg+"/"+dn;const c=await ctx(b,dev);const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));
  await p.goto(B+pg+".html?utm_source=facebook&utm_medium=paid&utm_content=p25",{waitUntil:"networkidle"});await p.waitForTimeout(500);
  const fq=await p.evaluate(()=>(window.fbq&&window.fbq.queue||[]).map(a=>[...a].slice(0,2).join(":")));
  ok(tag+" pixel: 2 inits, PageView once, ViewContent once",fq.filter(x=>x.startsWith("init:")).length===2&&fq.filter(x=>x==="track:PageView").length===1&&fq.filter(x=>x==="track:ViewContent").length===1,fq.join(","));
  const vw=c.T.filter(t=>t.ev==="view");ok(tag+" view event with new variant",vw.length===1&&vw[0].variant===pg,JSON.stringify(vw.map(v=>v.variant)));
  const fs=await p.evaluate(()=>{const a=document.querySelector('[data-sec="1"] [data-cta="hero_main"]').getBoundingClientRect();return {cta:Math.round(a.bottom),h:innerHeight}});
  if(dn!=="desktop") ok(tag+" price + CTA in first screen",fs.cta<=fs.h,JSON.stringify(fs));
  const order=await p.evaluate(()=>[...document.querySelectorAll("[data-sec]")].map(s=>s.dataset.sec+":"+s.dataset.name));
  ok(tag+" offer is section 3 after testimonials, numbering 1..n",order[2]==="3:ההצעה"&&/עדויות|מה אומרים/.test(order[1])&&order.every((x,i)=>x.startsWith((i+1)+":")),order.slice(0,4).join(" | "));
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}});await p.waitForTimeout(800);
  const secEv=c.T.filter(t=>t.ev==="section").map(t=>t.section+":"+t.name);ok(tag+" section events in new order",secEv.includes("3:ההצעה")&&secEv.includes("2:"+order[1].split(":")[1]),secEv.slice(0,5).join(","));
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
  ok(tag+" no horizontal scroll",!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));
  ok(tag+" no JS errors",errs.length===0,errs.join("|"));
  if(dn==="iphone"){await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:__dirname+"/s_"+pg+"_m.png"});}
  await c.close();}
 for(const qs of ["fbclid=IwZXh0bgNhZW0yNTYyODEwNDA1NTgAAR","test=1"]){const c=await ctx(b,devices["iPhone 13"]);const p=await c.newPage();await p.goto(B+pg+".html?"+qs,{waitUntil:"networkidle"});
  const st=await p.evaluate(()=>({noPix:window.__noPix,fbq:typeof window.fbq}));ok(pg+" ב23: no pixel for "+qs.slice(0,12),st.noPix===true&&st.fbq==="undefined",JSON.stringify(st));await c.close();}
 {const c=await ctx(b,devices["iPhone 13"]);const p=await c.newPage();await p.goto(B+pg+".html?utm_content=p25",{waitUntil:"networkidle"});
  await p.evaluate(()=>{document.querySelectorAll("a[data-checkout]").forEach(a=>a.addEventListener("click",e=>e.preventDefault()))});
  await p.evaluate(()=>{const a=document.querySelectorAll("a[data-checkout]");a[0].click();a[a.length-1].click()});
  const n=await icq(p);ok(pg+" InitiateCheckout once for 2 clicks",n===1,"n="+n);await c.close();}
}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
