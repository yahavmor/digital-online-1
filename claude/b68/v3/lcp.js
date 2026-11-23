// ב65 סבב שני: LCP ב-3G מדומה מול שרת מקומי עם gzip (כמו GitHub Pages). חיצוני חסום.
const {chromium,devices}=require('playwright');
const BASE=process.argv[2]||"http://127.0.0.1:8790/nlp/";
const pages=(process.argv[3]||"x").split(",");
const RUNS=+(process.argv[4]||3);
(async()=>{const b=await chromium.launch();
for(const pg of pages){const res=[];
 for(let i=0;i<RUNS;i++){
  const c=await b.newContext(devices["iPhone 13"]);
  await c.route("**/*",r=>{const u=r.request().url();if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:200,body:""})});
  const p=await c.newPage();const reqs=[];
  p.on("requestfinished",async rq=>{try{const s=await rq.sizes();reqs.push({u:rq.url().split("/").slice(-1)[0].split("?")[0],b:s.responseBodySize+s.responseHeadersSize,t:Date.now()})}catch(e){}});
  const cd=await c.newCDPSession(p);await cd.send("Network.enable");await cd.send("Network.setCacheDisabled",{cacheDisabled:true});
  await cd.send("Network.emulateNetworkConditions",{offline:false,latency:400,downloadThroughput:400*1024/8,uploadThroughput:400*1024/8});
  const t0=Date.now();
  await p.goto(BASE+pg+".html?test=1",{waitUntil:"load",timeout:120000});
  const r=await p.evaluate(()=>new Promise(res=>{let v=0,el="";new PerformanceObserver(l=>{for(const e of l.getEntries()){v=e.startTime;el=(e.element&&(e.element.tagName+" "+(e.element.getAttribute("src")||e.element.className||"")).slice(0,60))||e.url}}).observe({type:"largest-contentful-paint",buffered:true});setTimeout(()=>res({lcp:Math.round(v),el}),800)}));
  const before=reqs.filter(q=>q.t-t0<=r.lcp+50);
  res.push({...r,kb:Math.round(before.reduce((s,q)=>s+q.b,0)/1024),n:before.length,list:before.map(q=>q.u+":"+Math.round(q.b/1024)).join(" ")});
  await c.close();}
 res.sort((x,y)=>x.lcp-y.lcp);const m=res[Math.floor(res.length/2)];
 console.log(pg,"LCP median",m.lcp,"ms (runs",res.map(x=>x.lcp).join("/")+") el:",m.el,"| before LCP:",m.kb,"KB in",m.n,"req:",m.list);}
await b.close()})();
