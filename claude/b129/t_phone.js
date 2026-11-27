// ב129: שדה טלפון רשות בדף התודה. node t_phone.js <thanks_phone.html> [shots dir]
const {chromium,devices}=require("playwright"),fs=require("fs");const [TH,SHOTS]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
const AT=new Date("2026-12-02T10:00:00+02:00");
(async()=>{const br=await chromium.launch();
async function page(opts){opts=opts||{};const c=await br.newContext({...devices["iPhone 13"]});const errs=[],hooks=[],track=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("thanks.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(TH,"utf8")});
   if(/upsell-97\.html/.test(u.pathname))return r.fulfill({status:200,contentType:"text/html",body:"<html>UPSELL</html>"});return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com")){const b=r.request().postData()||"";hooks.push({p:u.pathname,b});
   if(u.pathname.includes("axjt5wu2"))track.push(Object.fromEntries(new URLSearchParams(b)));
   if(u.pathname.includes("s9ay2kp6"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify(opts.verify||{ok:true,link:"https://app.schooler.biz/x",deal:"271000000",email:"t@example.com"})});
   if(u.pathname.includes("qhq5knj8"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({up:""})});
   if(u.pathname.includes("9gjwxco9"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify(opts.phoneResp||{ok:true})});
   return r.fulfill({status:200,body:"{}"})}
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.clock.install({time:AT});
 await p.addInitScript(o=>{ if(o.cc) sessionStorage.setItem("cc_det",JSON.stringify(o.cc)); if(o.ls) for(const k in o.ls) localStorage.setItem(k,o.ls[k]); },{cc:opts.cc,ls:opts.ls});
 await p.goto("https://funnel.digitalonline.co.il/nlp/thanks.html"+(opts.qs||"?v=a5s&lowprofilecode=11111111-2222-3333-4444-555555555555&claude=b129"),{waitUntil:"load"});
 await p.waitForTimeout(700);await p.clock.runFor(2000);await p.waitForTimeout(300);
 return {c,p,errs,hooks,track}}
const st=async p=>p.evaluate(()=>({box:!document.getElementById("ph").hidden,form:!document.getElementById("phForm").hidden,ty:!document.getElementById("phTy").hidden,err:document.getElementById("phErr").hidden?"":document.getElementById("phErr").textContent,go:!document.getElementById("go").hidden,h:document.getElementById("phH").textContent}));
// 1. רוכש a5s (cc_det בלי טלפון): התיבה מוצגת אחרי האימות
{const X=await page({cc:{name:"בדיקה",email:"t@example.com",phone:""}});const s=await st(X.p);
 ok("a5s: הקישור לקורס מוצג והתיבה מוצגת",s.go&&s.box,s);ok("הכותרת: בן ישמח לוודא שהכל עובד לך",s.h==="בן ישמח לוודא שהכל עובד לך",s.h);
 ok("אירוע thanks_phone shown לגיליון, עם מספר העסקה ובלי טלפון",X.track.some(t=>t.ev==="thanks_phone"&&t.name==="shown"&&t.x==="deal=271000000"),X.track);
 // מספר לא תקין
 await X.p.fill("#phIn","05012");await X.p.click("#phBtn");await X.p.waitForTimeout(200);let s2=await st(X.p);
 ok("מספר קצר: הודעת שגיאה, בלי שליחה",/לא שלם/.test(s2.err)&&!X.hooks.some(h=>h.p.includes("9gjwxco9")),[s2.err,X.hooks.filter(h=>h.p.includes("9gjwxco9"))]);
 // מספר תקין עם מקפים ורווחים
 await X.p.fill("#phIn","050-123 4567");await X.p.click("#phBtn");await X.p.waitForTimeout(500);s2=await st(X.p);
 const sent=X.hooks.filter(h=>h.p.includes("9gjwxco9")).map(h=>Object.fromEntries(new URLSearchParams(h.b)));
 ok("נשלח להוק: deal, lookup_lp וטלפון מנורמל 0501234567",sent.length===1&&sent[0].deal==="271000000"&&sent[0].lookup_lp==="11111111-2222-3333-4444-555555555555"&&sent[0].phone==="0501234567",sent);
 ok("אחרי שמירה: הטופס נעלם ומופיע 'תודה! בן יחזור אליך.'",!s2.form&&s2.ty&&!s2.err,s2);
 ok("אירוע thanks_phone saved (בלי המספר)",X.track.some(t=>t.ev==="thanks_phone"&&t.name==="saved")&&!JSON.stringify(X.track).includes("0501234567"),X.track);
 const ls=await X.p.evaluate(()=>localStorage.getItem("ph_271000000"));ok("סימון בדפדפן שלא להציג שוב",ls==="1",ls);
 ok("בלי שגיאות JS",X.errs.length===0,X.errs);
 if(SHOTS){const g=await X.p.$("#ph");await g.scrollIntoViewIfNeeded();await X.p.waitForTimeout(200);await X.p.screenshot({path:SHOTS+"/ph_saved.png"});}
 await X.c.close()}
// 2. צילום של התיבה לפני השליחה
if(SHOTS){const X=await page({cc:{name:"בדיקה",email:"t@example.com",phone:""}});const g=await X.p.$("#ph");await g.scrollIntoViewIfNeeded();await X.p.waitForTimeout(200);await X.p.screenshot({path:SHOTS+"/ph_box.png"});await X.c.close()}
// 3. רוכש checkout.html (יש טלפון ב-cc_det): לא מוצג
{const X=await page({cc:{name:"בדיקה",email:"t@example.com",phone:"0521234567"}});const s=await st(X.p);ok("checkout.html (טלפון כבר נשמר): התיבה לא מוצגת",s.go&&!s.box,s);await X.c.close()}
// 4. בלי cc_det (דפדפן אחר): מוצג
{const X=await page({});const s=await st(X.p);ok("בלי פרטי סליקה בדפדפן: התיבה מוצגת",s.go&&s.box,s);await X.c.close()}
// 5. כבר נשמר בדפדפן הזה: לא מוצג
{const X=await page({ls:{"ph_271000000":"1"}});const s=await st(X.p);ok("כבר נשלח מהדפדפן הזה: לא מוצג שוב",!s.box,s);await X.c.close()}
// 6. תשלום לא מאומת: לא מוצג
{const X=await page({verify:{ok:false,email:"",link:""}});await X.p.clock.runFor(9000);const s=await st(X.p);ok("תשלום לא מאומת: התיבה לא מוצגת",!s.box,s);await X.c.close()}
// 7. השרת מחזיר ok:false: הודעת שגיאה, הכפתור חוזר
{const X=await page({phoneResp:{ok:false,why:"no_match"}});await X.p.fill("#phIn","0501234567");await X.p.click("#phBtn");await X.p.waitForTimeout(500);const s=await st(X.p);
 const dis=await X.p.evaluate(()=>document.getElementById("phBtn").disabled);
 ok("השרת דחה: הודעת 'לא הצלחנו לשמור', הטופס נשאר והכפתור פעיל",/לא הצלחנו/.test(s.err)&&s.form&&!s.ty&&!dis,[s,dis]);
 ok("אירוע thanks_phone fail",X.track.some(t=>t.ev==="thanks_phone"&&t.name==="fail"),X.track);await X.c.close()}
// 8. בתוך iframe (framed): לא מוצג
{const c=await br.newContext({...devices["iPhone 13"]});const errs=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("thanks.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(TH,"utf8")});
   if(u.pathname.endsWith("outer.html"))return r.fulfill({status:200,contentType:"text/html",body:'<html><body><iframe id="f" src="/nlp/thanks.html?v=a5s&lowprofilecode=11111111-2222-3333-4444-555555555555" style="width:390px;height:800px"></iframe></body></html>'});return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com")){if(u.pathname.includes("s9ay2kp6"))return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({ok:true,link:"https://app.schooler.biz/x",deal:"271000000",email:"t@example.com"})});return r.fulfill({status:200,body:"{}"})}
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.goto("https://funnel.digitalonline.co.il/nlp/outer.html",{waitUntil:"load"});await p.waitForTimeout(2500);
 /* דף התודה יוצא מה-iframe לחלון הראשי (סקריפט קיים בראש הדף), ואז התיבה מוצגת כרגיל */
 const s={url:p.url(),frames:p.frames().length};s.box=await p.evaluate(()=>!document.getElementById("ph").hidden).catch(()=>null);
 ok("בתוך iframe: הדף יוצא לחלון הראשי (קוד קיים) ורק אז התיבה מוצגת",/thanks\.html/.test(s.url)&&s.frames===1&&s.box===true,s);await c.close()}
await br.close();console.log(`\n${n-f}/${n} passed`);process.exit(f?1:0)})();
