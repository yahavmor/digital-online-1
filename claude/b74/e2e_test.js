// ב74: בדיקת המסלול המלא מקומית: thanks -> upsell-97 -> checkout97 -> (Cardcom מדומה). שרת מדומה, בלי Make ובלי חיוב.
const {chromium,devices}=require('playwright');
const BASE="http://127.0.0.1:8771/nlp/";
const TOK="AbCdEfGhIjKlMnOpQrStUvWxYz012345";
const res=[];const ok=(dn,name,cond,extra="")=>{res.push([dn,name,!!cond]);console.log((cond?"PASS":"FAIL"),dn,name,extra)};
async function ctx(b,dev,o={}){
  const st={state:o.state||"ok"},calls=[],ext=[],errs=[];let purN=0;
  const c=await b.newContext(dev);
  await c.addInitScript(()=>{let _f;Object.defineProperty(window,"fbq",{configurable:true,get(){return _f},set(v){_f=function(){if(arguments[1]==="Purchase"){try{localStorage.setItem("__purN",String(+(localStorage.getItem("__purN")||0)+1))}catch(e){}}return v.apply(this,arguments)};_f.push=_f;_f.queue=v.queue||[];_f.loaded=true;_f.version="2.0";}})});
  await c.route("**/*",async r=>{const u=r.request().url();
    if(u.includes("s9ay2kp6")){const d={ok:true,link:"https://x.schooler.biz/l",email:"a@b.co",deal:"123456789"};if(!o.noUp)d.up=TOK;return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify(d)})}
    if(u.startsWith("https://upsell.mock/")){const p=new URLSearchParams(r.request().postData()||"");const a=p.get("action");calls.push(a+":"+p.get("t")+(p.get("agree")?":agree="+p.get("agree"):""));
      let body={};
      if(p.get("t")!==TOK) body={state:"invalid"};
      else if(a==="check") body=st.state==="ok"?{state:"ok",name:"בדיקה",email:"test@example.com"}:{state:st.state};
      else if(a==="decline"){ if(st.state==="ok") st.state="declined"; body={ok:true}; }
      else if(a==="create") body=(st.state==="ok"&&p.get("agree")==="1")?{url:"https://secure.cardcom.solutions/mock-lp"}:{state:st.state};
      return r.fulfill({status:200,contentType:"application/json",headers:{"access-control-allow-origin":"*"},body:JSON.stringify(body)})}
    if(u.startsWith("https://secure.cardcom.solutions/"))return r.fulfill({status:200,contentType:"text/html",body:"<p>MOCK CARDCOM</p>"});
    if(u.startsWith("http://127.0.0.1"))return r.continue();
    if(!/fonts\.(googleapis|gstatic)\.com/.test(u))ext.push(u.split("?")[0]);
    return r.fulfill({status:204,body:""})});
  const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
  await p.goto(BASE+"terms.html");await p.evaluate(()=>sessionStorage.setItem("cc_lp","11111111-2222-3333-4444-555555555555"));
  return {c,p,st,calls,ext,errs,purN:async()=>+(await p.evaluate(()=>localStorage.getItem("__purN")||0))};
}
const toUpsell=async(p)=>{await p.goto(BASE+"thanks.html?sid=s1",{waitUntil:"domcontentloaded"});await p.waitForURL(/upsell-97\.html\?t=/,{timeout:8000});await p.waitForLoadState("networkidle");};
(async()=>{const b=await chromium.launch();
for(const [dn,dev] of [["m",devices["iPhone 13"]],["d",{viewport:{width:1280,height:900}}]]){
  // 1. מסלול רכישה: תודה -> אפסייל -> סליקה -> טופס Cardcom
  {const X=await ctx(b,dev);const {p}=X;
   await p.goto(BASE+"thanks.html?sid=s1",{waitUntil:"domcontentloaded"});
   await p.waitForSelector("#go:not([hidden])",{timeout:8000});ok(dn,"1 thanks shows course button before redirect",true);
   await p.waitForURL(/upsell-97\.html\?t=/,{timeout:8000});ok(dn,"1 thanks -> upsell with token",p.url().endsWith("t="+TOK));
   await p.waitForLoadState("networkidle");
   X.ext.length=0; /* מכאן רק דף האפסייל ודף הסליקה. הפיקסל והאירועים של דף התודה קיימים היום ונשארים */
   ok(dn,"1 upsell offer visible (not expired)",!(await p.evaluate(()=>document.body.classList.contains("expired"))));
   await p.screenshot({path:__dirname+"/s_"+dn+"_upsell.png"});
   await p.click("#heroCta");await p.waitForURL(/checkout97\.html/);await p.waitForLoadState("networkidle");
   ok(dn,"1 hero CTA -> checkout97?t=token",new URL(p.url()).searchParams.get("t")===TOK);
   ok(dn,"1 checkout offer shown",await p.isVisible("#offer"));
   ok(dn,"1 pay button locked before ticks",await p.isDisabled("#go"));
   await p.check("#cAgree");ok(dn,"1 still locked with one tick",await p.isDisabled("#go"));
   await p.check("#cTerms");ok(dn,"1 unlocked with both ticks",!(await p.isDisabled("#go")));
   await p.screenshot({path:__dirname+"/s_"+dn+"_checkout.png",fullPage:true});
   await p.click("#go");await p.waitForSelector("#cc:not([hidden])",{timeout:5000});
   ok(dn,"1 Cardcom form opens in iframe",(await p.getAttribute("#cc","src")).startsWith("https://secure.cardcom.solutions/"));
   ok(dn,"1 create sent with agree=1",X.calls.includes("create:"+TOK+":agree=1"));
   ok(dn,"1 Purchase pixel fired exactly once",(await X.purN())===1,"n="+(await X.purN()));
   ok(dn,"1 server calls",true,X.calls.join(" , "));
   ok(dn,"1 upsell+checkout: no external requests",X.ext.length===0,X.ext.join(" "));ok(dn,"1 no JS errors",X.errs.length===0,X.errs.join(" | "));await X.c.close();}
  // 2. ויתור בדף האפסייל: שורף בשרת, חוזר לתודה, בלי הפניה חוזרת ובלי Purchase כפול
  {const X=await ctx(b,dev);const {p}=X;await toUpsell(p);
   await p.click('[data-decline="hero"]');await p.waitForSelector("#declineModal.open");
   await p.click("#confirmDecline");await p.waitForURL(/thanks\.html\?ups=1/,{timeout:5000});
   ok(dn,"2 decline sent to server",X.calls.includes("decline:"+TOK));
   await p.waitForSelector("#go:not([hidden])",{timeout:8000});await p.waitForTimeout(2500);
   ok(dn,"2 back on thanks, course button, no re-redirect",/thanks\.html\?ups=1/.test(p.url()));
   ok(dn,"2 Purchase still once",(await X.purN())===1);
   await p.goto(BASE+"upsell-97.html?t="+TOK);await p.waitForLoadState("networkidle");
   ok(dn,"2 same link after decline -> expired view",await p.evaluate(()=>document.body.classList.contains("expired")));
   if(dn==="m")await p.screenshot({path:__dirname+"/s_m_upsell_expired.png"});
   await p.click(".expired-view [data-course-link]");await p.waitForURL(/thanks\.html\?ups=1/);ok(dn,"2 expired 'continue to course' -> thanks",true);
   await p.goto(BASE+"checkout97.html?t="+TOK);await p.waitForLoadState("networkidle");
   ok(dn,"2 checkout after decline -> expired screen",await p.isVisible("#stExpired"));
   ok(dn,"2 no create after decline",!X.calls.some(c=>c.startsWith("create")));
   ok(dn,"2 no JS errors",X.errs.length===0,X.errs.join(" | "));await X.c.close();}
  // 3. "לא תודה" בדף הסליקה
  {const X=await ctx(b,dev);const {p}=X;await toUpsell(p);await p.click("#heroCta");await p.waitForURL(/checkout97/);await p.waitForLoadState("networkidle");
   await p.click("#no");await p.waitForURL(/thanks\.html\?ups=1/,{timeout:5000});
   ok(dn,"3 checkout 'no thanks' burns offer + back to thanks",X.calls.includes("decline:"+TOK));await X.c.close();}
  // 4. כבר נרכש / פג
  for(const s of ["used","expired"]){const X=await ctx(b,dev,{state:s});const {p}=X;await toUpsell(p);
   ok(dn,"4 "+s+": upsell shows expired view",await p.evaluate(()=>document.body.classList.contains("expired")));
   await p.goto(BASE+"checkout97.html?t="+TOK);await p.waitForLoadState("networkidle");
   ok(dn,"4 "+s+": checkout state screen",await p.isVisible(s==="used"?"#stUsed":"#stExpired"));await X.c.close();}
  // 5. בלי טוקן מהשרת (המצב היום): אין הפניה לאפסייל
  {const X=await ctx(b,dev,{noUp:true});const {p}=X;await p.goto(BASE+"thanks.html?sid=s1");await p.waitForSelector("#go:not([hidden])",{timeout:8000});await p.waitForTimeout(3000);
   ok(dn,"5 no token -> stays on thanks",/thanks\.html/.test(p.url())&&X.calls.length===0);await X.c.close();}
  // 6. קישור בלי טוקן / טוקן לא נכון
  {const X=await ctx(b,dev);const {p}=X;await p.goto(BASE+"upsell-97.html");await p.waitForLoadState("networkidle");
   ok(dn,"6 upsell without token -> expired view",await p.evaluate(()=>document.body.classList.contains("expired")));
   await p.goto(BASE+"checkout97.html?t=WRONG");await p.waitForLoadState("networkidle");ok(dn,"6 wrong token -> invalid screen",await p.isVisible("#stInvalid"));await X.c.close();}
  // 7. כל כפתורי הרכישה מובילים לסליקה עם הטוקן
  for(const pl of ["benefits","offer","closing","sticky","decline_modal"]){const X=await ctx(b,dev);const {p}=X;await toUpsell(p);
   if(pl==="sticky"){await p.evaluate(()=>window.scrollTo(0,document.querySelector('[data-buy="benefits"]').getBoundingClientRect().top+scrollY-200));await p.waitForTimeout(600);
     if(!(await p.isVisible("#sticky.show"))){ok(dn,"7 sticky (n/a at this width)",true);await X.c.close();continue}}
   if(pl==="decline_modal"){await p.click('[data-decline="hero"]');await p.waitForSelector("#declineModal.open")}
   await p.click(`[data-buy="${pl}"]`);await p.waitForURL(/checkout97/,{timeout:5000});
   ok(dn,"7 "+pl+" -> checkout97 with token",new URL(p.url()).searchParams.get("t")===TOK);
   if(pl==="decline_modal")ok(dn,"7 decline_modal buy did not burn offer",!X.calls.some(c=>c.startsWith("decline")));await X.c.close();}
  // 8. התקנון: הקישור מוביל לסעיף 11
  {const X=await ctx(b,dev);const {p}=X;await p.goto(BASE+"checkout97.html?demo=ok");const href=await p.getAttribute('#cTerms ~ span a, label:has(#cTerms) a',"href");
   await p.goto(new URL(href,BASE+"checkout97.html").href);ok(dn,"8 terms link -> section 11 exists",href==="terms.html#s11"&&await p.isVisible("#s11"));await X.c.close();}
  // 9. תצוגה בלי שרת: upsell ?demo=ok -> checkout97 ?demo=ok
  {const X=await ctx(b,dev);const {p}=X;await p.goto(BASE+"upsell-97.html?demo=ok");await p.click("#heroCta");await p.waitForURL(/checkout97\.html\?demo=ok/);ok(dn,"9 demo chain",await p.isVisible("#offer"));await X.c.close();}
}
await b.close();const f=res.filter(r=>!r[2]);console.log("TOTAL",res.length,"FAIL",f.length);})();
