// רכישת הבדיקה של בן (ראשי 14.11): קישור הבדיקה מסמן את הביקור כפנימי (test=1 ל-7827398) ומנקה aff ישן ששמור בדפדפן.
// Make וקארדקום מדומים - שום בקשה לא יוצאת. שימוש: node t_testlink.js <checkout.html אחרי patch_testflag>
const {chromium,devices}=require("playwright"),fs=require("fs");const H=fs.readFileSync(process.argv[2],"utf8");
const LINK="?co=b&utm_source=internal_test&utm_medium=email&utm_campaign=ben_test_1411";
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const br=await chromium.launch();
const run=async(qs,oldAff)=>{const c=await br.newContext({...devices["iPhone 13"]});const B=[],T=[];
 if(oldAff)await c.addInitScript(a=>{try{if(!sessionStorage.getItem("__seed")){sessionStorage.setItem("__seed","1");localStorage.setItem("nlp_aff",JSON.stringify({c:a,t:Date.now()-864e5}));document.cookie="nlp_aff="+encodeURIComponent(a+"."+(Date.now()-864e5))+"; path=/"}}catch(e){}},oldAff);
 await c.route("**/*",r=>{const u=new URL(r.request().url());if(u.pathname.endsWith("/checkout.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:H});
  if(u.hostname.endsWith("make.com")){const b=new URLSearchParams(r.request().postData()||"");if(b.get("ev")){T.push(b);return r.fulfill({status:200,body:"Accepted"})}B.push(b);return r.fulfill({status:200,contentType:"application/json",body:'{"url":"https://secure.cardcom.solutions/x"}'})}
  if(u.hostname.endsWith("cardcom.solutions"))return r.fulfill({status:200,contentType:"text/html",body:"<html></html>"});return r.fulfill({status:204,body:""})});
 const p=await c.newPage();let fb=0;p.on("request",q=>{if(/facebook\.(net|com)/.test(q.url()))fb++});
 await p.goto("https://funnel.digitalonline.co.il/nlp/checkout.html"+qs,{waitUntil:"load"});await p.waitForTimeout(800);
 await p.fill("#fName","בן בדיקה");await p.fill("#fEmail","ben+test1@example.com");await p.fill("#fPhone","0501234567");await p.check("#fTerms");await p.waitForTimeout(2500);
 const nopix=await p.evaluate(()=>window.__noPix===true);await c.close();return {B,T,fb,nopix}};
let r=await run(LINK,"amir");
ok("test link: request to 7827398 sent",r.B.length>=1,r.B.length);
ok("test link: test=1",r.B.length&&r.B[0].get("test")==="1");
ok("email with + accepted and sent as is",r.B.length&&r.B[0].get("email")==="ben+test1@example.com",r.B[0]&&r.B[0].get("email"));
ok("test link: old aff (amir) cleared - no aff in request",r.B.length&&!r.B[0].get("aff"),r.B[0]&&r.B[0].get("aff"));
ok("test link: events marked int=1, no aff",r.T.length&&r.T.every(t=>/(^|;)int=1(;|$)/.test(t.get("x")||"")&&!/aff=/.test(t.get("x")||"")),r.T.map(t=>t.get("x")).slice(0,2));
ok("test link: no Meta pixel (window.__noPix, no requests to facebook)",r.nopix&&r.fb===0,r.fb);
r=await run("?co=b","amir");
ok("control (regular link, old aff): aff=amir and no test flag",r.B.length&&r.B[0].get("aff")==="amir"&&!r.B[0].get("test"),r.B[0]&&[...r.B[0].keys()].join());
console.log("TOTAL",n-f+"/"+n);await br.close();process.exit(f?1:0)})();
