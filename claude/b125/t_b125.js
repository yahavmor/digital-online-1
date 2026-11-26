// ב125: go.html שולח הכול ל-a5s, עם כל הפרמטרים. node t_b125.js <go.html> <a5s.html> [go.orig.html]
const {chromium,devices}=require("playwright"),fs=require("fs");const [GO,A5S,ORIG]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
const CASES=[["חם (קרוסלה) internal=1","utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab&utm_content=car4_warm_a&internal=1"],
 ["מייל רצף internal=1","utm_source=email&utm_medium=responder&utm_campaign=a27&utm_content=m1_story&internal=1"],
 ["משווק gal","aff=gal&utm_source=facebook&utm_medium=affiliate&utm_campaign=NLP%20%7C%20Aff%20gal%20%7C%20Sales%20%7C%20Cold%20%7C%20P25&utm_content=p25_brain_c3"],
 ["קר של בן","utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_cold&utm_content=p25"],
 ["אינסטגרם אורגני (ביו)","utm_source=instagram&utm_medium=bio"],
 ["ManyChat","utm_source=ig&utm_medium=dm&utm_campaign=manychat"],
 ["בלי פרמטרים",""],
 ["נשים (w40) דרך הנתב","utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben"]];
(async()=>{const br=await chromium.launch();
async function run(gohtml,qs,pre){const c=await br.newContext({...devices["iPhone 13"]});const errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("/go.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:gohtml});
   if(u.pathname.endsWith("/a5s.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(A5S,"utf8")});
   if(/\.html$/.test(u.pathname))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:"<html><body>OTHER "+u.pathname+"</body></html>"});
   return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com"))return r.fulfill({status:200,body:"{}"});return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 if(pre)await p.addInitScript(pre);
 await p.goto("https://funnel.digitalonline.co.il/nlp/go.html"+(qs?"?"+qs:""),{waitUntil:"load"});await p.waitForTimeout(1200);
 const url=new URL(p.url());const ls=await p.evaluate(()=>({co:localStorage.getItem("nlp_co_ab"),rt:localStorage.getItem("nlp_go_rt_2111")}));
 await c.close();return {url,ls,errs}}
const go=fs.readFileSync(GO,"utf8");
for(const [label,qs] of CASES){const R=await run(go,qs);const sp=new URLSearchParams(qs);const P=R.url.searchParams;
 ok(label+": נוחת ב-a5s.html",R.url.pathname.endsWith("/a5s.html"),R.url.href);
 ok(label+": כל הפרמטרים המקוריים נשמרו",[...sp.entries()].every(([k,v])=>P.get(k)===v),R.url.search);
 ok(label+": go=1 ו-exp=a5s_2611",P.get("go")==="1"&&P.get("exp")==="a5s_2611",R.url.search);
 ok(label+": סליקה B2 (nlp_co_ab=b2)",R.ls.co==="b2",R.ls);
 ok(label+": בלי שגיאות JS",R.errs.length===0,R.errs);}
{const R=await run(go,"utm_source=instagram&utm_medium=bio");ok("ig_org: route=ig_org נשמר",R.url.searchParams.get("route")==="ig_org",R.url.search)}
{const R=await run(go,"utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab",'try{localStorage.setItem("nlp_go_rt_2111","a5v7")}catch(e){}');
 ok("דפדפן ששובץ קודם ל-a5v7 מגיע ל-a5s",R.url.pathname.endsWith("/a5s.html"),R.url.href);ok("השיבוץ הישן לא נמחק (לא נקרא)",R.ls.rt==="a5v7",R.ls)}
if(ORIG){const o=fs.readFileSync(ORIG,"utf8");const R=await run(o,"utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab&internal=1");
 ok("בקרה: go.html המקורי שולח את החם ל-a5v6/a5v7",/a5v[67]\.html$/.test(R.url.pathname),R.url.href)}
await br.close();console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)})();
