// ב114 המשך: בדיקה מקומית. (1) PAYLOGO_BIT=true בחמישה דפים: לוגו ביט נראה והטקסט כולל "ביט". (2) checkout.hide: כפתור הביט שלנו לא מופיע גם עם bit_url.
// node t_b114_bit.js work/
const {chromium,devices}=require("playwright"),fs=require("fs");const D=process.argv[2];
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
const BIT="https://secure.cardcom.solutions/api/LPC5/BitV3?x=1";
(async()=>{const br=await chromium.launch();
const ctx=async(html,path,bit)=>{const c=await br.newContext({...devices["iPhone 13"],viewport:{width:390,height:844}});const errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"&&u.pathname.endsWith(path))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:html});
  if(u.pathname.endsWith("bit-mark.svg"))return r.fulfill({status:200,contentType:"image/svg+xml",body:fs.readFileSync(D+"bit-mark.svg","utf8")});
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";if(/ev=/.test(b))return r.fulfill({status:200,body:"Accepted"});
   return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify(Object.assign({code:"0",url:"https://secure.cardcom.solutions/EA/mock?lp=lp1",lp:"lp1"},bit?{bit_url:bit}:{}))})}
  if(u.hostname.endsWith("cardcom.solutions"))return r.fulfill({status:200,contentType:"text/html",body:"<html><body>mock</body></html>"});
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));return {c,p,errs}};
for(const f of ["a5s","a5v6","a5v7","pr2","checkout"]){
 for(const [tag,file] of [["orig",f+".orig.html"],["bit",f+".bit.html"]]){
  const html=fs.readFileSync(D+file,"utf8");const path="/nlp/"+f+".html";
  const X=await ctx(html,path,null);await X.p.goto("https://funnel.digitalonline.co.il"+path+(f==="checkout"?"?v=a5s&co=b2&claude=b114":"?claude=b114"),{waitUntil:"load"});await X.p.waitForTimeout(900);
  const r=await X.p.evaluate(()=>{const li=[...document.querySelectorAll('[data-pl="bit"]')];const tx=[...document.querySelectorAll('[data-paylogos]')].map(e=>e.textContent).join(" ");
   return {n:li.length,shown:li.filter(e=>!e.hidden).length,txt:/ביט/.test(tx),imgs:li.filter(e=>!e.hidden).map(e=>e.querySelector("img")&&e.querySelector("img").naturalWidth>0)}});
  if(tag==="orig"){ok(f+" orig: bit logo hidden",r.n>0&&r.shown===0,JSON.stringify(r));ok(f+" orig: no 'ביט' in pay text",!r.txt)}
  else{ok(f+" bit: all bit logos shown ("+r.n+")",r.n>0&&r.shown===r.n,JSON.stringify(r));ok(f+" bit: 'ביט' in pay text",r.txt);ok(f+" bit: bit image rendered",r.imgs.length&&r.imgs.every(Boolean),JSON.stringify(r.imgs))}
  ok(f+" "+tag+": no JS errors",X.errs.length===0,X.errs.join(";"));
  if(tag==="bit"&&(f==="a5s"||f==="checkout"))await X.p.screenshot({path:D+"shot_"+f+"_bit.png",fullPage:false});
  await X.c.close()}}
// checkout.hide: bit_url present but our button stays hidden; card iframe loads
for(const [tag,file,expect] of [["orig","checkout.orig.html",true],["hide","checkout.hide.html",false]]){
 for(const co of ["a","b2"]){
 const X=await ctx(fs.readFileSync(D+file,"utf8"),"/nlp/checkout.html",BIT);
 await X.p.goto("https://funnel.digitalonline.co.il/nlp/checkout.html?v=a5v6&co="+co+"&claude=b114",{waitUntil:"load"});await X.p.waitForTimeout(800);
 await X.p.fill("#fName","בדיקה פנימית");await X.p.fill("#fEmail","b114@example.com");await X.p.fill("#fPhone","0501234567");await X.p.check("#fTerms");
 if(co==="a")await X.p.click('form#det button.go[type="submit"]');await X.p.waitForTimeout(2500);
 const v=await X.p.evaluate(()=>{const e=document.getElementById("bitWrap");return {bit:!!e&&!e.hidden&&!!e.offsetParent,cc:!document.getElementById("cc").hidden&&/cardcom/.test(document.getElementById("cc").src)}});
 ok("checkout "+tag+" co="+co+": bit button "+(expect?"shown":"hidden"),v.bit===expect,JSON.stringify(v));ok("checkout "+tag+" co="+co+": card iframe loads",v.cc);ok("checkout "+tag+" co="+co+": no JS errors",X.errs.length===0,X.errs.join(";"));
 if(tag==="hide"&&co==="b2")await X.p.screenshot({path:D+"shot_checkout_hide.png"});
 await X.c.close()}}
await br.close();console.log(n-f+"/"+n);process.exit(f?1:0)})();
