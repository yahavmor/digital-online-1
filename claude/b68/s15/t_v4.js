// ב68 v4: בדיקות לפני עלייה. שרת מקומי (srv.js) עם nlp/ של main ועם הפלט של build_v4.py:
//   a5v4.html / pr2v4.html (בלי נכסים), a5v4s.html / pr2v4s.html (עם slots_test.json)
// שימוש: node t_v4.js http://127.0.0.1:8791/nlp/
const {chromium,devices}=require('playwright');const B=process.argv[2];
// הערות בן 11.11 (ben_1111.json): ההבדלים המותרים בקופי של a5v4 מול a5 החי - רק המילים של הנוסחים הישנים/החדשים והכפתורים החדשים
const BEN=require(__dirname+"/ben_1111.json");
const wl=t=>t.replace(/<[^>]+>/g," ").replace(/&nbsp;/g," ").replace(/🔒/g," ").replace(/תשלום מאובטח/g," ").split(/[\s·•]+/).filter(Boolean);
const cntw=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
const mul=(x,a)=>x[2]==="all"?[].concat(...Array(6).fill(a)):a;
const BEN_OLD=cntw([].concat(...BEN.a5.map(x=>mul(x,wl(x[0]))),...BEN.a5_removed_text.map(wl)));
const BEN_NEW=cntw([].concat(...BEN.a5.map(x=>mul(x,wl(x[1]))),...BEN.a5_buttons.map(b=>wl(b.text+" ← "+b.micro)),...BEN.a5_insert_after.map(i=>wl(i.html))));
const REBUILT='[data-name="מה יש בפנים"],[data-name="בונוסים"],#offer';/* חלקים 6-7: נבדקים בנפרד */
const SL=require(__dirname+"/slots.json");const T15=SL.t15&&SL.t15.src?SL.t15:null;
if(T15){const o=wl("מה באמת השתנה אצלם? · 2:01"),n=wl(T15.title+" "+(T15.play_label||""));o.forEach(w=>BEN_OLD[w]=(BEN_OLD[w]||0)+1);n.forEach(w=>BEN_NEW[w]=(BEN_NEW[w]||0)+1);}
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
const res=[];const ok=(n,c,e="")=>{res.push(!!c);if(!c||process.env.V)console.log(c?"PASS":"FAIL",n,e)};
async function ctx(b,dev){const c=await b.newContext(dev);const T=[];c.T=T;
 await c.route("**/*",r=>{const u=r.request().url();
  if(/hook\.eu1\.make\.com/.test(u)){const d=r.request().postData()||"";T.push(Object.fromEntries(new URLSearchParams(d)));return r.fulfill({status:200,body:"ok"})}
  if(/\/nlp\/checkout\.html/.test(u))return r.fulfill({status:200,contentType:"text/html",body:"<p>CHECKOUT</p>"});
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});return c}
// אותו קופי: כל המילים של הדף החי, בלי "תשלום מאובטח" והמנעול (התוספת היחידה של v4) ובלי המספור הגדול של a5
const wordsOf=(p,sel)=>p.evaluate(sel=>{const e=document.querySelector(sel);if(!e)return [];const out=[];const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let x;while(x=w.nextNode())out.push(x.nodeValue);return out.join(" ").replace(/🔒/g," ").replace(/תשלום מאובטח/g," ").split(/[\s·•]+/).filter(x=>x&&!/^(0[0-9]|1[0-5])$/.test(x))},sel);
const P20=SL.peek20&&SL.peek20.src?SL.peek20:null;
const words=(p,skip)=>p.evaluate(skip=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest("script,style,noscript"))continue;if(skip&&n.parentElement.closest(skip))continue;out.push(n.nodeValue)}
 return out.join(" ").replace(/🔒/g," ").replace(/תשלום מאובטח/g," ").replace(/מתוך \d+ · /g," ").split(/[\s·•]+/).filter(x=>x&&!/^(0[0-9]|1[0-5])$/.test(x))},skip);
const media=p=>p.evaluate(()=>[...document.querySelectorAll("img,video,source")].map(e=>e.getAttribute("src")||e.getAttribute("data-v4src")||e.getAttribute("srcset")||e.getAttribute("poster")||"").filter(Boolean).sort());
const icq=p=>p.evaluate(()=>(window.fbq&&window.fbq.queue||[]).filter(a=>a[1]==="InitiateCheckout").length);
// כל מה שבמסך הראשון בטעינה: שקיפות מלאה, בלי הזזה ובלי מעבר (כלומר מוצג מיד, בלי אנימציה)
const firstScreen=p=>p.evaluate(()=>{const bad=[];document.querySelectorAll("body *").forEach(e=>{const r=e.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||!r.width)return;if(e.closest(".sticky,#sticky"))return;
 const cs=getComputedStyle(e);if(+cs.opacity<1&&cs.visibility!=="hidden"&&!e.closest("[aria-hidden=true],.was,s"))bad.push(e.tagName+"."+e.className+" op="+cs.opacity);if(e.classList.contains("v4r"))bad.push(e.tagName+" v4r")});return bad.slice(0,5)});
(async()=>{const b=await chromium.launch();
for(const [pg,live] of [["pr2v4","pr2"],["a5v4","a5"]]){
 {const c=await ctx(b,{viewport:{width:1280,height:900}});const p=await c.newPage();
  await p.goto(B+live+".html?test=1",{waitUntil:"networkidle"});const LW=await words(p,pg==="a5v4"?REBUILT:null),LM=await media(p),LPW=pg==="a5v4"&&P20?await wordsOf(p,".peek"):[],LRW=pg==="a5v4"?[].concat(...await Promise.all((BEN.a5_remove_sections||[]).map(x=>wordsOf(p,'[data-name="'+x[0]+'"]')))):[];
  await p.goto(B+pg+".html?test=1",{waitUntil:"networkidle"});const NW=await words(p,pg==="a5v4"?REBUILT:null),NM=await media(p),NPW=pg==="a5v4"&&P20?await wordsOf(p,".v4-peek"):[];
  const cnt=a=>a.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});const lc=cnt(LW),nc=cnt(NW);
  const ALO=pg==="a5v4"?{...BEN_OLD}:{},ALN=pg==="a5v4"?{...BEN_NEW}:{};
  if(pg==="a5v4"){const nd=LW.filter(x=>x==="—").length;ALO["—"]=(ALO["—"]||0)+nd;ALN["-"]=(ALN["-"]||0)+nd;LPW.forEach(w=>ALO[w]=(ALO[w]||0)+1);LRW.forEach(w=>ALO[w]=(ALO[w]||0)+1);if(BEN.a5_inside){wl(BEN.a5_inside.html+" "+BEN.a5_inside.all_btn).forEach(w=>ALN[w]=(ALN[w]||0)+1);}if(SL.wa&&SL.wa.quote){wl(SL.wa.quote).forEach(w=>ALN[w]=(ALN[w]||0)+1);}if(BEN.a5_guarantee){wl(BEN.a5_guarantee.html).forEach(w=>ALN[w]=(ALN[w]||0)+1);wl("החזר מלא תוך 7 ימים").forEach(w=>ALO[w]=(ALO[w]||0)+1);}NPW.forEach(w=>ALN[w]=(ALN[w]||0)+1);}
  const miss=Object.keys(lc).filter(k=>(nc[k]||0)<lc[k]-(ALO[k]||0)),extra=Object.keys(nc).filter(k=>nc[k]-(lc[k]||0)>(ALN[k]||0));
  ok(pg+" same copy as live (only lock + תשלום מאובטח"+(pg==="a5v4"?" + Ben 11.11 edits":"")+")",miss.length===0&&extra.length===0,"missing:"+JSON.stringify(miss.slice(0,6))+" extra:"+JSON.stringify(extra.slice(0,6)));
  if(pg==="a5v4"){const t=(await p.evaluate(()=>document.body.innerText)).replace(/\s+/g," ");
   ok("a5v4 Ben 11.11: every new text present word for word",BEN.a5.filter(x=>x[1]&&!(BEN.a5_dropped_items||{})[x[3]]).map(x=>x[1]).concat(BEN.a5_insert_after.map(i=>i.html)).every(h=>h.replace(/<h3>[^<]*<\/h3>/,"").split(/<\/?(?:p|h2|h3|li|ul|ol|div|section)\b[^>]*>/).map(x=>x.replace(/<[^>]+>/g,"").replace(/\s+/g," ").trim()).filter(x=>x.length>1).every(x=>t.includes(x))),"");
   ok("a5v4 Ben 11.11: removed texts gone (notfit, WhatsApp in offer box, old sub, old pause, old notcourse, footer line)",!/פתרון קסם|יש שאלה לפני שמצטרפים|בקורס לומדים להטמיע|אם שום דבר בדפוסים|מזהים בחיים|ואינה מחליפה ייעוץ/.test(t)&&!(await p.$('[data-wa="offer"]')));
   ok("a5v4 removed sections gone (המנגנון, with the keys button)",await p.evaluate(R=>R.every(x=>!document.querySelector('[data-name="'+x[0]+'"]'))&&!document.querySelector('[data-cta="keys"]')&&!/כשהאוטומט מתחלף/.test(document.body.innerText),BEN.a5_remove_sections||[]));
   ok("a5v4 guarantee block in the cta1 box (shield, Ben's text), no refund line under cta1, other buttons keep it",await p.evaluate(G=>{const a=document.querySelector('[data-cta="cta1"]'),box=a.closest(".box"),g=box&&box.querySelector(".v4-guar"),m=a.nextElementSibling;const t=g&&g.innerText.replace(/\s+/g," ");return !!g&&!!g.querySelector("svg.v4-shield")&&t.includes("7 ימי אחריות מלאה. הסיכון עלינו, ההחלטה שלך.")&&t.includes("בלי שאלות. בלי שכנועים. בלי אותיות קטנות.")&&/מחיר השקה לזמן מוגבל/.test(m.textContent)&&!/החזר מלא/.test(m.textContent)&&/החזר מלא תוך 7 ימים/.test(document.querySelector('[data-cta="cta2"]').nextElementSibling.textContent)},BEN.a5_guarantee));
   ok("a5v4 new button: know, 297 + access + refund under the button",await p.evaluate(()=>["know"].every(k=>{const a=document.querySelector('[data-cta="'+k+'"][data-checkout]');return !!a&&/297/.test(a.nextElementSibling.textContent)&&/החזר מלא תוך 7 ימים/.test(a.nextElementSibling.textContent)})));
   ok("a5v4 13: lock + תשלום מאובטח inside every buy button (sticky included), not repeated under it",await p.evaluate(()=>[...document.querySelectorAll("a.cta[data-checkout]")].every(a=>{const v=a.querySelector(".v4-pay");const n=a.nextElementSibling;return v&&v.querySelector(".v4-li")&&/תשלום מאובטח/.test(v.textContent)&&!(n&&/תשלום מאובטח/.test(n.textContent))})));
   if(T15)ok("a5v4 19: ע15 replaces the testimonials video in place, poster set, headline above, nothing preloaded",await p.evaluate(T=>{const f=document.querySelector('[data-name="תוצאות אמיתיות"] figure.vid[data-slot="t15"]');if(!f)return false;const v=f.querySelector("video");return v.getAttribute("src")===T.src&&v.getAttribute("poster")===T.poster&&v.getAttribute("preload")==="none"&&f.previousElementSibling.textContent===T.title&&!document.querySelector('[data-name="תוצאות אמיתיות"] video[src="assets/t3.mp4"]')},T15));
   ok("a5v4 ראשי 11.11: no long dashes in the page text",!/[—–]/.test(t));
   if(P20)ok("a5v4 17/20: ע20 player replaces the old peek box (label, lesson, 0:43, 1 of 90, buy button)",await p.evaluate(P=>{const f=document.querySelector('[data-name="מה יש בפנים"] .v4-peek');if(!f||document.querySelector(".peek"))return false;const b=f.querySelector('[data-slot="peek20"] .v4-box');return b.dataset.v4src===P.src&&f.querySelector(".v4-pl-top").textContent==="שיעור אמיתי מתוך הקורס"&&f.querySelector(".v4-pl-meta b").textContent===P.lesson&&f.querySelector(".v4-pl-d").textContent===P.dur&&f.querySelector(".v4-peek-n").textContent==="זה שיעור אחד מתוך 90"&&!!f.querySelector('a.cta[data-cta="peek"][data-checkout]')},P20));
   if(SL.wa&&SL.wa.src)ok("a5v4 16: WhatsApp screenshot = first carousel slide (lazy, size set, alt = the message), one dot per slide",await p.evaluate(W=>{const c=document.querySelector('[data-name="מה אומרים"] [data-carousel]');const f=c.querySelector(".car-track > figure.car-slide:first-child");const i=f&&f.querySelector("img");const n=c.querySelectorAll(".car-slide").length;return !!i&&f.dataset.slot==="wa"&&(i.getAttribute("src")||i.dataset.v4src)===W.src&&i.loading==="lazy"&&+i.getAttribute("width")===W.w&&+i.getAttribute("height")===W.h&&i.alt===W.alt&&c.querySelectorAll(".car-dots i").length===n},SL.wa));
   if(BEN.a5_inside)ok("a5v4 חלק 6: מה יש בפנים = head, line, Ben text, (tour), ע20 player only",await p.evaluate(()=>{const s=document.querySelector('[data-name="מה יש בפנים"] .wrap');const kids=[...s.children].map(e=>e.matches("h2")?"h2":e.matches("p.lead")?"lead":e.matches(".v4-show")?"show":e.matches(".v4-tour")?"tour":e.matches(".v4-peek,.peek")?"peek":"?:"+e.className);return kids.filter(k=>k!=="tour").join(",")==="h2,lead,show,peek"&&!document.querySelector(".notcourse,.v4-all,.mods,p.toolbox")},),JSON.stringify(await p.evaluate(()=>[...document.querySelector('[data-name="מה יש בפנים"] .wrap').children].map(e=>e.tagName+"."+e.className))));
   if(BEN.a5_bonus)ok("a5v4 חלק 7: bonuses right after מה יש בפנים (new heading), 5 cards (name, kind, 3-5 points - bonus 2 Ben's exact 5, struck value, free), no summary inside, #offer right after, cta3 after איך מתחילים",await p.evaluate(B=>{const o=[...document.querySelectorAll("[data-sec]")].map(x=>x.dataset.name);if(o.indexOf("בונוסים")!==o.indexOf("מה יש בפנים")+1||o.indexOf("ההצעה")!==o.indexOf("בונוסים")+1)return false;const sec=document.querySelector('[data-name="בונוסים"]');if(sec.querySelector("h2").textContent!==B.h2)return false;const cards=[...sec.querySelectorAll("article.bx2")];if(cards.length!==5)return false;const ok=cards.every((c,i)=>{const d=B.cards[i],li=[...c.querySelectorAll(".bx2-ul li")].map(x=>x.textContent);return c.querySelector("h3").textContent==="בונוס "+d.n+": "+d.name&&c.querySelector(".bx2-kind").textContent===d.kind&&li.length>=3&&li.length<=5&&li.join("|")===d.bullets.map(x=>x[0]).join("|")&&c.querySelector(".bx2-val s").textContent==="שווי: "+d.value+" ₪"&&c.querySelector(".bx2-val b").textContent===B.free});const ht=document.querySelector('[data-name="איך מתחילים"]').nextElementSibling;return ok&&!sec.querySelector(".bx-worlds,.bx-sum,.bx-final,.bx2-total,a.cta")&&sec.nextElementSibling.id==="offer"&&!!ht&&!!ht.querySelector('[data-cta="cta3"]')},BEN.a5_bonus));
   if(BEN.a5_offer)ok("a5v4 חלק 7: #offer knockout - heading, 6 value rows, total 2,411, regular 1,290 struck vs launch 297, button with lock inside, 7-day line; old box gone",await p.evaluate(O=>{const f=document.getElementById("offer");if(!f||f.dataset.name!=="ההצעה"||!f.hasAttribute("data-buyzone"))return false;const rows=[...f.querySelectorAll(".v4-ko-list li")].map(li=>li.querySelector("span").textContent+"="+li.querySelector("b").textContent);const a=f.querySelector('a.cta[data-cta="offer"][data-checkout]');return f.querySelector("h2").textContent===O.h2&&rows.join("|")===O.rows.map(r=>r[0]+"="+r[1]).join("|")&&f.querySelector(".v4-ko-tot").textContent===O.total.join("")&&f.querySelector(".v4-ko-reg s").textContent===O.regular[1]&&f.querySelector(".v4-ko-now b").textContent===O.launch[1]&&!!a&&!!a.querySelector(".v4-pay .v4-li")&&a.nextElementSibling.textContent===O.micro&&!f.querySelector(".pcard,.avs,.secure,.guar1,.anchor")&&f.querySelectorAll("h2").length===1},BEN.a5_offer));
   ok("a5v4 11: new section right after רגע לפני, before the offer",await p.evaluate(()=>{const o=[...document.querySelectorAll("[data-sec]")].map(x=>x.dataset.name);return o.indexOf("מה אם")===o.indexOf("רגע לפני")+1}));
   ok("a5v4 14: colors - background #0E0E10, white text, yellow CTA with black text, no beige left",await p.evaluate(()=>{const cs=getComputedStyle(document.body),b=getComputedStyle(document.querySelector('[data-cta="hero_main"]'));const src=document.documentElement.outerHTML;return cs.backgroundColor==="rgb(14, 14, 16)"&&cs.color==="rgb(255, 255, 255)"&&b.color==="rgb(0, 0, 0)"&&/254, ?207, ?0|255, ?225, ?77|FECF00|FFE14D/i.test(b.backgroundImage)&&!/#(D3B77A|C9A96E|EADBB5|F3EDE2|F0E2BE)\b|211, ?183, ?122|234, ?219, ?181/i.test(src)}));}
  const LMx=pg==="a5v4"&&T15?(()=>{const a=LM.slice();a[a.indexOf("assets/t3.mp4")]=T15.src;if(P20)a.push(P20.poster);if(SL.wa&&SL.wa.src)a.push(SL.wa.src);return a.sort()})() /* רק הסרטון שבסקשן; הסטוריז "תלמידים מספרים" נשארים על t3 */:LM;
  ok(pg+" same images/videos as live"+(pg==="a5v4"&&T15?" (t3 → ע15)":"")+" (no empty slots in the page)",JSON.stringify(LMx)===JSON.stringify(NM)&&!(await p.$(".v4-slot .v4-ph")),LM.length+" vs "+NM.length);
  ok(pg+" no robots noindex, no 0183/0184/0188",!(await p.evaluate(()=>!!document.querySelector('meta[name=robots]')||/018[348]/.test(document.body.innerHTML))));
  // כל כפתור (חוץ מהדביק) עם "תשלום מאובטח" ומנעול מיד אחריו
  const lk=await p.evaluate(()=>[...document.querySelectorAll("a.cta[data-checkout]")].filter(a=>a.dataset.cta!=="sticky").map(a=>{let n=a.nextElementSibling||a.parentElement.nextElementSibling,t="";for(let i=0;i<3&&n&&!n.matches("a.cta");i++,n=n.nextElementSibling)t+=n.innerHTML;return [a.dataset.cta,/class="v4-li"|<rect/.test(t)&&/תשלום מאובטח/.test(t)]}));
  if(pg!=="a5v4")ok(pg+" every CTA has lock + תשלום מאובטח right after it",lk.every(x=>x[1]),JSON.stringify(lk.filter(x=>!x[1])));
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
  if(dn==="iphone"){for(const [w,h] of [[375,667],[390,844]]){await p.setViewportSize({width:w,height:h});await p.waitForTimeout(150);
   const f=await p.evaluate(()=>{const s=document.querySelector('[data-sec="1"]'),q=e=>Math.round(e.getBoundingClientRect().bottom);return {h1:q(s.querySelector("h1")),sub:q(s.querySelector(".sub")),cta:q(s.querySelector('[data-cta="hero_main"]')),vh:innerHeight}});
   ok(tag+" "+w+"x"+h+": headline, sentence and button in first screen",f.h1<=f.vh&&f.sub<=f.vh&&f.cta<=f.vh,JSON.stringify(f));}
   await p.setViewportSize(dev.viewport);await p.waitForTimeout(150);}
  const order=await p.evaluate(()=>[...document.querySelectorAll("[data-sec]")].map(s=>s.dataset.sec+":"+s.dataset.name));
  const OI=pg==="a5v4"?order.findIndex(x=>/:בונוסים$/.test(x))+1:2; /* a5v4 חלק 7: ההצעה מיד אחרי הבונוסים */
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
  if(pg==="a5v4"){const st=await p.evaluate(()=>({t15:(document.querySelector('[data-sec] figure.vid[data-slot="t15"] video')||{}).getAttribute?.("src"),head:(document.querySelector('figure.vid[data-slot="t15"]')||{}).previousElementSibling?.textContent,wa:!!document.querySelector('.car-track > figure.car-slide[data-slot="wa"]:first-child img[loading="lazy"][width][height]'),peek:!document.querySelector(".peek")&&!!document.querySelector('[data-name="מה יש בפנים"] [data-slot="peek20"] .v4-box'),vids:document.querySelectorAll("video").length}));
   ok("a5v4 15/16/17 slots: ע15 replaces the testimonials video (headline above), WhatsApp = first carousel slide, ע20 replaces the peek box",st.t15==="assets/t1.mp4"&&st.head==="אנשים בדיוק כמוך, שבחרו לעשות צעד עם בן"&&st.wa&&st.peek,JSON.stringify(st));}
  if(pg==="a5v4"){const pl=await p.evaluate(()=>{const f=document.querySelector('[data-name="מה יש בפנים"] .v4-peek');if(!f)return null;const a=f.querySelector('a.cta[data-cta="peek"][data-checkout]');return {h:f.querySelector(".v4-peek-h").textContent,lab:f.querySelector(".v4-pl-top").textContent,bar:!!f.querySelector(".v4-pl-bar i"),meta:!!f.querySelector(".v4-pl-meta b").textContent&&!!f.querySelector(".v4-pl-d").textContent,n:f.querySelector(".v4-peek-n").textContent,btn:!!a&&!!a.querySelector(".v4-pay")&&/297/.test(a.textContent)&&/החזר מלא תוך 7 ימים/.test(a.nextElementSibling.textContent)}});
   ok("a5v4 20: הצצה פנימה player - label, progress bar, lesson/part/duration, 'זה שיעור אחד מתוך 90', buy button",!!pl&&pl.h==="הצצה פנימה"&&pl.lab==="שיעור אמיתי מתוך הקורס"&&pl.bar&&pl.meta&&pl.n==="זה שיעור אחד מתוך 90"&&pl.btn,JSON.stringify(pl));}
  else ok(pg+" slots placed (t15+wa in testimonials, trial in drop point 2)",sl.length===3&&sl[0].k==="t15"&&/עדויות|מה אומרים/.test(sl.find(x=>x.k==="t15").sec)&&/עדויות|מה אומרים/.test(sl.find(x=>x.k==="wa").sec)&&/הבעיה|לדעת או להטמיע/.test(sl.find(x=>x.k==="trial").sec),JSON.stringify(sl));
  ok(pg+" slot images lazy with width/height + aspect-ratio box",sl.every(x=>x.lazy==="lazy"&&x.wh&&/\d+ \/ \d+/.test(x.ar)),JSON.stringify(sl.map(x=>[x.k,x.lazy,x.wh,x.ar])));
  if(pg!=="a5v4")ok(pg+" t15 headline above the video (Ben 10.11), nothing about buying the course",await p.evaluate(()=>{const h=document.querySelector('[data-slot="t15"] .v4-slot-h');return !!h&&h.textContent==="אנשים בדיוק כמוך, שבחרו לעשות צעד עם בן"&&h.nextElementSibling.classList.contains("v4-box")}));
  ok(pg+" no video downloaded before click",vreq.length===0,vreq.join(","));
  const SK=pg==="a5v4"?"peek20":"t15",SV=pg==="a5v4"?"assets/t2.mp4":"assets/t1.mp4";
  const before=await p.evaluate(SK=>{const b=document.querySelector('[data-slot="'+SK+'"] .v4-box');b.scrollIntoView({block:"center"});return Math.round(b.getBoundingClientRect().height)},SK);await p.waitForTimeout(600);
  await p.click('[data-slot="'+SK+'"] .v4-box');await p.waitForTimeout(800);
  const after=await p.evaluate(SK=>{const v=document.querySelector('[data-slot="'+SK+'"] video');return v?{h:Math.round(v.getBoundingClientRect().height),src:v.getAttribute("src"),controls:v.controls}:null},SK);
  ok(pg+" click plays the slot video in place, same height",after&&after.src===SV&&(pg!=="a5v4"||await p.evaluate(async()=>{const v=document.querySelector('[data-slot="peek20"] video');await new Promise(r=>setTimeout(r,1500));return !v.muted&&parseFloat(document.querySelector(".v4-pl-bar i").style.width)>0}))&&after.controls&&Math.abs(after.h-before)<=2,JSON.stringify([before,after]));
  const vp=c.T.filter(t=>t.ev==="video_play");ok(pg+" video_play sent with slot name",vp.length===1&&vp[0].video==="slot_"+SK,JSON.stringify(vp.map(t=>t.video)));
  ok(pg+"s no JS errors",errs.length===0,errs.join("|"));await c.close();}
}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
