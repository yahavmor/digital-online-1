const {chromium,devices}=require('playwright');const B="http://127.0.0.1:8771/nlp/";const TOK="AbCdEfGhIjKlMnOpQrStUvWxYz012345";
const res=[];const ok=(dn,n,c,x="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",dn,n,x)};
(async()=>{const b=await chromium.launch();
for(const [dn,dev] of [["m",devices["iPhone 13"]],["d",{viewport:{width:1280,height:900}}]]){
 for(const [lbl,seq] of [["used after 2 polls",["ok","ok","used"]],["invalid",["invalid"]],["never confirmed",["ok"]]]){
  const c=await b.newContext(dev);let n=0;const ext=[],errs=[];
  await c.route("**/*",r=>{const u=r.request().url();
   if(u.startsWith("https://upsell.mock/")){const st=seq[Math.min(n++,seq.length-1)];return r.fulfill({status:200,contentType:"application/json",headers:{"access-control-allow-origin":"*"},body:JSON.stringify({state:st})})}
   if(u.startsWith("https://secure.cardcom.solutions/"))return r.fulfill({status:302,headers:{location:B+"upsell-thanks.html?t="+TOK}});
   if(u.startsWith("http://127.0.0.1"))return r.continue(); if(!/fonts\./.test(u))ext.push(u); return r.fulfill({status:204,body:""})});
  const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
  // מדמים את ה-iframe של דף הסליקה: Cardcom מפנה בתוכו לדף האישור
  await p.goto(B+"terms.html");await p.evaluate(u=>{const f=document.createElement("iframe");f.src=u;document.body.appendChild(f)},"https://secure.cardcom.solutions/mock-success");
  await p.waitForURL(/upsell-thanks\.html/,{timeout:8000});ok(dn,lbl+": broke out of iframe to top",p.url().includes("upsell-thanks.html?t="));
  const want=lbl.startsWith("used")?"#stDone":lbl==="invalid"?"#stNone":"#stWait";
  await p.waitForSelector(want+":not([hidden])",{timeout:lbl==="never confirmed"?25000:10000});
  if(lbl==="never confirmed"){await p.waitForTimeout(21000);ok(dn,lbl+": stays processing, stops polling",await p.isVisible("#stWait")&&n<=8,"polls="+n)}
  else ok(dn,lbl+": state "+want,await p.isVisible(want),"polls="+n);
  ok(dn,lbl+": course button -> thanks?ups=1",(await p.getAttribute("#course","href"))==="thanks.html?ups=1");
  if(lbl.startsWith("used"))await p.screenshot({path:__dirname+"/ut_"+dn+".png"});
  ok(dn,lbl+": no external requests / errors",ext.length===0&&errs.length===0,ext.join(" ")+errs.join("|"));await c.close();}
 for(const d of ["used","processing","invalid"]){const c=await b.newContext(dev);const p=await c.newPage();let api=0;await c.route("https://upsell.mock/**",r=>{api++;r.abort()});
  await p.goto(B+"upsell-thanks.html?demo="+d);const id={used:"#stDone",processing:"#stWait",invalid:"#stNone"}[d];ok(dn,"demo "+d,await p.isVisible(id)&&api===0);
  const w=await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);ok(dn,"demo "+d+" no horizontal scroll",w);await c.close();}
}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
