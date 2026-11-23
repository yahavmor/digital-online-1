// ב68 v4: LCP ו-CLS במובייל (אייפון 13). שני פרופילים:
//  slow4g - כמו Lighthouse במובייל: RTT 150ms, 1.6Mbps, מעבד איטי פי 4, והגופנים של Google נטענים באמת (לא חסומים)
//  3g     - כמו בבדיקת v3: 400ms, 400kbps (הגופנים של Google חסומים, כמו אז; הגופן של v4 מהאתר כן נטען)
// שימוש: node lcp4.js <base url של nlp/> <דפים,מופרדים,בפסיק> [ריצות=5]
const {chromium,devices}=require('playwright');
const BASE=process.argv[2],pages=process.argv[3].split(","),RUNS=+(process.argv[4]||5);
const PROF={slow4g:{lat:150,down:1.6e6/8,up:750e3/8,cpu:4,fonts:true},"3g":{lat:400,down:400*1024/8,up:400*1024/8,cpu:1,fonts:false}};
(async()=>{const b=await chromium.launch();
for(const [pn,P] of Object.entries(PROF).filter(([k])=>!process.env.PROF||k===process.env.PROF))for(const pg of pages){const res=[];
 for(let i=0;i<RUNS;i++){
  const c=await b.newContext(devices["iPhone 13"]);
  await c.route("**/*",r=>{const u=r.request().url();if(u.startsWith("http://127.0.0.1"))return r.continue();if(P.fonts&&/fonts\.(googleapis|gstatic)\.com/.test(u))return r.continue();return r.fulfill({status:200,body:""})});
  const p=await c.newPage();
  const cd=await c.newCDPSession(p);await cd.send("Network.enable");await cd.send("Network.setCacheDisabled",{cacheDisabled:true});
  await cd.send("Network.emulateNetworkConditions",{offline:false,latency:P.lat,downloadThroughput:P.down,uploadThroughput:P.up});
  if(P.cpu>1)await cd.send("Emulation.setCPUThrottlingRate",{rate:P.cpu});
  await p.addInitScript(()=>{window.__cls=0;window.__lcp=[0,""];try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:"layout-shift",buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=[e.startTime,(e.element&&(e.element.tagName+" "+(e.element.getAttribute("src")||e.element.className||"")).slice(0,50))||e.url]}).observe({type:"largest-contentful-paint",buffered:true})}catch(e){}});
  await p.goto(BASE+pg+".html?test=1",{waitUntil:"load",timeout:120000});await p.waitForTimeout(1500);
  // גלילה איטית עד הסוף: אנימציות הכניסה לא אמורות להוסיף קפיצות בפריסה
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo(0,y);await new Promise(r=>setTimeout(r,40))}});await p.waitForTimeout(600);
  const r=await p.evaluate(()=>{const h=document.querySelector('[data-sec="1"] h1');let heebo="?";if(h){const r1=document.createRange();r1.selectNodeContents(h);const w1=r1.getBoundingClientRect().width;const ff=h.style.fontFamily;h.style.fontFamily="Arial";const w2=r1.getBoundingClientRect().width;h.style.fontFamily=ff;heebo=Math.abs(w1-w2)>2?"Y":"n"}
   return {lcp:Math.round(__lcp[0]),el:__lcp[1],cls:Math.round(__cls*1000)/1000,heebo}});res.push(r);await c.close();}
 res.sort((x,y)=>x.lcp-y.lcp);const m=res[Math.floor(res.length/2)];
 console.log(pn.padEnd(7),pg.padEnd(6),"LCP median",m.lcp,"ms (",res.map(x=>x.lcp).join("/"),") el:",m.el,"| CLS max",Math.max(...res.map(x=>x.cls)),"| H1 in Heebo:",res.map(x=>x.heebo).join(""));}
await b.close()})();
