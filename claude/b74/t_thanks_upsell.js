// ב74 השקה: דף התודה פונה ל-8463664 אחרי אימות הקורס, ועובר לאפסייל רק עם קוד תקין. Make מדומה - שום בקשה לא יוצאת.
// שימוש: node t_thanks_upsell.js <thanks.html אחרי patch_thanks_upsell.py>
const {chromium,devices}=require("playwright"),fs=require("fs");const H=fs.readFileSync(process.argv[2],"utf8");
const VERIFY="https://hook.eu1.make.com/s9ay2kp6sldk9527d77seuuq83xxto60",ISSUE="https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd";
const LP="11111111-2222-3333-4444-555555555555",TOK="abcdef0123456789abcdef0123456789";
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const br=await chromium.launch();
const run=async(o)=>{const c=await br.newContext({...devices["iPhone 13"]});const calls={verify:0,issue:[]};let nav="";
 await c.route("**/*",r=>{const u=r.request().url();
  if(/\/nlp\/thanks\.html/.test(u))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:H});
  if(/\/nlp\/upsell-97\.html/.test(u)){nav=u;return r.fulfill({status:200,contentType:"text/html",body:"<html>upsell</html>"})}
  if(u.startsWith(VERIFY)){calls.verify++;return r.fulfill({status:200,contentType:"application/json",body:o.verifyOk===false?'{"ok":false}':'{"ok":true,"link":"https://x.schooler.biz/course","deal":"123456","email":"a@b.co"}'})}
  if(u.startsWith(ISSUE)){calls.issue.push(new URLSearchParams(r.request().postData()||"").get("lookup_lp"));const k=calls.issue.length;const body=o.issue(k);return r.fulfill({status:200,contentType:body[0]==="{"?"application/json":"text/plain",body})}
  return r.fulfill({status:204,body:""})});
 const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));
 if(o.seen)await p.addInitScript(t=>{try{sessionStorage.setItem("ups_seen",t)}catch(e){}},TOK);
 await p.goto("https://funnel.digitalonline.co.il/nlp/thanks.html?lowprofilecode="+LP+(o.qs||""),{waitUntil:"load"});
 await p.waitForTimeout(o.wait||9000);
 const go=await p.evaluate(()=>{const a=document.getElementById("go");return a?!a.hidden:null}).catch(()=>null);
 await c.close();return {calls,nav,errs,go}};
let r=await run({issue:k=>k<2?'{"up":""}':'{"up":"'+TOK+'"}'});
ok("normal: verify then issue with the same lookup_lp",r.calls.verify>=1&&r.calls.issue.length===2&&r.calls.issue.every(x=>x===LP),JSON.stringify(r.calls));
ok("normal: redirect to upsell-97.html?t=<code> after the code arrives",r.nav.endsWith("/nlp/upsell-97.html?t="+TOK),r.nav);
ok("normal: no JS errors",!r.errs.length,r.errs.join("|"));
r=await run({issue:k=>'{"up":"'+TOK+'"}',qs:"&ups=1",wait:5000});
ok("back from upsell (?ups=1): no issue call, no redirect, course button shown",r.calls.issue.length===0&&!r.nav&&r.go===true,JSON.stringify(r));
r=await run({issue:k=>'{"up":""}',wait:17000});
ok("no valid code (expired / not found): 5 tries max, no redirect, course button shown",r.calls.issue.length===5&&!r.nav&&r.go===true,JSON.stringify({i:r.calls.issue.length,nav:r.nav,go:r.go}));
r=await run({issue:k=>'Accepted',wait:17000});
ok("scenario off (Accepted, not JSON): no redirect, no errors",!r.nav&&!r.errs.length&&r.go===true,JSON.stringify({i:r.calls.issue.length,nav:r.nav,e:r.errs}));
r=await run({issue:k=>'{"up":"'+TOK+'"}',seen:1,wait:5000});
ok("same code already seen in this tab: no second redirect",!r.nav,r.nav);
r=await run({issue:k=>'{"up":"'+TOK+'"}',verifyOk:false,wait:9000});
ok("course payment not verified: no issue call",r.calls.issue.length===0&&!r.nav,JSON.stringify(r.calls));
r=await run({issue:k=>'{"up":"<script>x</script>"}',wait:5000});
ok("malformed code ignored",!r.nav,r.nav);
console.log("TOTAL",n-f+"/"+n);await br.close();process.exit(f?1:0)})();
