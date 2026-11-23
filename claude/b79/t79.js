const {chromium,devices}=require('playwright');
const B="http://127.0.0.1:8772/nlp/checkout.html";
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",n,e)};
const IG="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36 Instagram 300.0.0.0";
async function mk(b,dev,co){const c=await b.newContext(dev);const T=[],C=[],errs=[];
 await c.route("**/*",async r=>{const u=r.request().url();
  if(u.includes("axjt5wu2oh5vf4zz9uut24s1m79ot6jc")){T.push(Object.fromEntries(new URLSearchParams(r.request().postData()||"")));return r.fulfill({status:200,body:"ok"})}
  if(u.includes("9yp88pz9bfvxbr7w6xkb4ckun82ote6a")){C.push(Object.fromEntries(new URLSearchParams(r.request().postData()||"")));return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({url:"https://secure.cardcom.solutions/mock",lp:"11111111-2222-3333-4444-555555555555"})})}
  if(u.startsWith("https://secure.cardcom.solutions/"))return r.fulfill({status:200,contentType:"text/html",body:"<p>MOCK</p>"});
  if(u.startsWith("http://127.0.0.1"))return r.continue(); return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.goto(B+"?co="+co+"&v=a5&utm_content=lp_a5",{waitUntil:"networkidle"});return {c,p,T,C,errs}}
const tv=(T,ev)=>T.filter(t=>t.ev===ev);
(async()=>{const b=await chromium.launch();
for(const [dn,dev] of [["iphone",devices["iPhone 13"]],["android-ig",{...devices["Pixel 7"],userAgent:IG}],["desktop",{viewport:{width:1280,height:900}}]]) for(const co of ["b","a"]){
 const tag=dn+"/"+co;
 // 1. accepted formats
 {const X=await mk(b,dev,co);const {p}=X;
  const good={"0541234567":"054-1234567","054-123-4567":"054-1234567","054 123 4567":"054-1234567","+972 54-123-4567":"054-1234567","972541234567":"054-1234567","00972541234567":"054-1234567","+972 (0)54 1234567":"054-1234567","541234567":"054-1234567","٠٥٤١٢٣٤٥٦٧":"054-1234567","(054) 123-4567":"054-1234567"};
  let allok=true,bad=[];
  for(const [inp,exp] of Object.entries(good)){await p.fill("#fPhone","");await p.type("#fPhone",inp);await p.click("h2");const v=await p.inputValue("#fPhone");const e=await p.textContent("#pErr");const isBad=await p.evaluate(()=>document.getElementById("fPhone").classList.contains("bad"));if(v!==exp||e||isBad){allok=false;bad.push(inp+"→"+v+(e?" ERR":""))}}
  ok(tag+" 1 common formats accepted + normalised to 05X-XXXXXXX",allok,bad.join(" | "));
  ok(tag+" 1 no validation events for valid numbers",tv(X.T,"checkout_validation_error").length===0,JSON.stringify(tv(X.T,"checkout_validation_error").map(t=>t.x)));
  ok(tag+" 1 no JS errors",X.errs.length===0,X.errs.join("|"));await X.c.close();}
 // 2. invalid: error only after leaving the field, with example, type logged without the number
 {const X=await mk(b,dev,co);const {p}=X;
  const badN={"02-1234567":"landline","077-1234567":"landline","+1 212 555 1234":"intl","05412345":"short","054123456789":"long","abc":"letters","0641234567":"prefix"};
  let r=[],allok=true;
  for(const [inp,typ] of Object.entries(badN)){await p.fill("#fPhone","");await p.type("#fPhone",inp);
    const during=await p.textContent("#pErr");await p.click("h2");const after=await p.textContent("#pErr");
    const evs=tv(X.T,"checkout_validation_error").filter(t=>(t.x||"").includes("pt="+typ));
    const leak=X.T.some(t=>t.ev!=="checkout_details"&&JSON.stringify(t).replace(/"(qs|sid|vid|sec_on_page|x)":"[^"]*"/g,"").match(/\d{5,}/));
    const xs=evs.map(t=>t.x).join(",");const digitsInX=/\d{4,}/.test(xs.replace(/len=\d+|cx=[^;,]*/g,""));
    const good=!during && /050-1234567/.test(after) && evs.length>=1 && !digitsInX && !leak;
    if(!good){allok=false;} r.push(inp+":"+(during?"shown-while-typing ":"")+(after?"msg ":"nomsg ")+evs.length+"ev "+xs);
    await p.fill("#fPhone","");await p.click("h2");}
  ok(tag+" 2 errors only on leaving the field, with example, pt type, no digits",allok,allok?"":r.join(" | "));
  // fix while typing clears
  await p.fill("#fPhone","");await p.type("#fPhone","05412");await p.click("h2");const e1=await p.textContent("#pErr");
  await p.focus("#fPhone");await p.type("#fPhone","34567");const e2=await p.textContent("#pErr");
  ok(tag+" 2 error clears while fixing",!!e1&&!e2);
  ok(tag+" 2 no JS errors",X.errs.length===0,X.errs.join("|"));await X.c.close();}
 // 3. terms not pre-ticked; continue without ticking -> scroll + highlight + event
 {const X=await mk(b,dev,co);const {p}=X;
  ok(tag+" 3 terms not pre-ticked",!(await p.isChecked("#fTerms")));
  await p.fill("#fName","ישראל ישראלי");await p.fill("#fEmail","a@b.co");await p.fill("#fPhone","054 123 4567");await p.click("h2");
  if(co==="b"){await p.click("#coPay");}else{await p.click("#det button.go",{force:true});}
  await p.waitForTimeout(900);
  const st=await p.evaluate(()=>{const w=document.getElementById("tWrap"),r=w.getBoundingClientRect();return {need:w.classList.contains("need"),pulse:w.classList.contains("pulse"),inView:r.top>=0&&r.bottom<=innerHeight,msg:document.getElementById("terr").textContent,frame:!!document.getElementById("cc").getAttribute("src")}});
  ok(tag+" 3 scrolls to terms, highlights, message, no payment form",st.need&&st.pulse&&st.inView&&st.msg&&!st.frame,JSON.stringify(st));
  ok(tag+" 3 terms_missing event",tv(X.T,"checkout_terms_missing").length===1);
  if(dn==="iphone"&&co==="b") await p.screenshot({path:__dirname+"/s_terms_missing.png"});
  // 4. tick -> payment form loads with normalised phone
  await p.check("#fTerms");if(co==="a"){await p.click("#det button.go",{force:true});}
  await p.waitForSelector("#cc:not([hidden])",{timeout:5000}).catch(()=>{});
  ok(tag+" 4 payment form loads after ticking",(await p.getAttribute("#cc","src")||"").startsWith("https://secure.cardcom.solutions/"));
  ok(tag+" 4 phone sent normalised (digits only)",X.C.length>=1&&X.C[X.C.length-1].phone==="0541234567",X.C.map(c=>c.phone).join(","));
  // 5. leave event
  await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await p.waitForTimeout(300);
  await p.evaluate(()=>dispatchEvent(new PageTransitionEvent("pagehide",{persisted:false})));await p.waitForTimeout(300);
  const lv=tv(X.T,"checkout_leave");const lx=lv[0]?lv[0].x:"";
  ok(tag+" 5 checkout_leave once with time/scroll/touch/payv/load",lv.length===1&&/scr=\d+/.test(lx)&&/touch=1/.test(lx)&&/payv=1/.test(lx)&&/ttfb=\d+;dcl=\d+;load=\d+/.test(lx)&&+lv[0].sec_on_page>=0&&!/lead_|@/.test(JSON.stringify(lv[0])),lx);
  const hs=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);ok(tag+" no horizontal scroll",!hs);
  ok(tag+" 5 no JS errors",X.errs.length===0,X.errs.join("|"));await X.c.close();}
 // 6. leave right away (the 12): leave fires with touch=0
 {const X=await mk(b,dev,co);const {p}=X;await p.waitForTimeout(400);await p.evaluate(()=>{Object.defineProperty(document,"visibilityState",{value:"hidden",configurable:true});document.dispatchEvent(new Event("visibilitychange"))});await p.waitForTimeout(200);
  const lv=tv(X.T,"checkout_leave");ok(tag+" 6 immediate exit: leave with touch=0 payv=0",lv.length===1&&/touch=0/.test(lv[0].x)&&/payv=0/.test(lv[0].x),lv[0]&&lv[0].x);
  if(dn==="android-ig"&&co==="b"){ await p.evaluate(()=>{});}
  await X.c.close();}
}
// screenshots: phone error on iPhone (b)
{const X=await mk(b,devices["iPhone 13"],"b");const {p}=X;await p.fill("#fName","ישראל ישראלי");await p.fill("#fEmail","a@b.co");await p.type("#fPhone","02-1234567");await p.click("h2");await p.waitForTimeout(200);
 await p.evaluate(()=>document.getElementById("fPhone").scrollIntoView({block:"center"}));await p.screenshot({path:__dirname+"/s_phone_err.png"});await X.c.close();}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length);})();
// 7. failed redirect: rc logged, reload marked rep=1
(async()=>{const b=await chromium.launch();const c=await b.newContext(devices["iPhone 13"]);const T=[];const errs=[];
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("axjt5wu2oh5vf4zz9uut24s1m79ot6jc")){T.push(Object.fromEntries(new URLSearchParams(r.request().postData()||"")));return r.fulfill({status:200,body:"ok"})}if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.goto("http://127.0.0.1:8772/nlp/terms.html");await p.evaluate(()=>{sessionStorage.setItem("cc_lp","aaaaaaaa-1111-2222-3333-444444444444");sessionStorage.setItem("cc_det",JSON.stringify({name:"ישראל ישראלי",email:"a@b.co",phone:"0541234567"}))});
 const U="http://127.0.0.1:8772/nlp/checkout.html?co=b&status=failed&ResponseCode=60000303&Operation=1";
 await p.goto(U,{waitUntil:"networkidle"});await p.reload({waitUntil:"networkidle"});
 const f=T.filter(t=>t.ev==="checkout_failed").map(t=>t.x.split(";co=")[0]);
 console.log((f.length===2&&f[0]==="rc=60000303"&&f[1]==="rc=60000303;rep=1"&&!errs.length)?"PASS":"FAIL","7 failed: rc logged, reload rep=1",JSON.stringify(f),errs.join("|"));
 const msg=await p.textContent("#err");console.log(/Apple Pay/.test(msg)?"PASS":"FAIL","7 60000303 message unchanged");await b.close();})();
