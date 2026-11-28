// ב132: נתב 50/50 דביק. node t_router.js <go.html> <a5s_split.html> <a5s2.html>
const {chromium,devices}=require("playwright"),fs=require("fs");const [GO,A5S,A5S2]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
(async()=>{const br=await chromium.launch();
async function ctx(){const c=await br.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){const h=u.pathname.endsWith("go.html")?GO:u.pathname.endsWith("a5s2.html")?A5S2:u.pathname.endsWith("a5s.html")?A5S:null;
   if(h)return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(h,"utf8")});return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com"))return r.fulfill({status:200,body:"ok"});return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 return c}
async function land(c,url){const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));await p.goto("https://funnel.digitalonline.co.il/nlp/"+url,{waitUntil:"load"});await p.waitForTimeout(300);
 const u=new URL(p.url());const r={page:u.pathname.split("/").pop(),exp:u.searchParams.get("exp"),v:await p.evaluate(()=>document.documentElement.dataset.variant),qs:u.search,ls:await p.evaluate(()=>localStorage.getItem("nlp_v2")),errs};await p.close();return r}
// 1. go.html: שיבוץ 50/50 ודביקות
let a=0,b=0;for(let i=0;i<30;i++){const c=await ctx();const r=await land(c,"go.html?utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben&aff=");
 if(r.page==="a5s2.html"&&r.exp==="a5s_v2"&&r.v==="a5s2")b++;else if(r.page==="a5s.html"&&r.exp==="a5s_v1"&&r.v==="a5s")a++;
 if(i===0){ok("go.html: go=1 ו-utm נשמרים",/go=1/.test(r.qs)&&/utm_content=w2_ben/.test(r.qs),r.qs);ok("go.html: בלי שגיאות JS",r.errs.length===0,r.errs)}
 const r2=await land(c,"go.html?utm_source=facebook&utm_medium=paid");ok(i<2?"go.html: ביקור שני באותו דפדפן - אותו דף":"",r2.page===r.page,[r.page,r2.page]);await c.close()}
ok("go.html: 30 דפדפנים מתפצלים (כל צד בין 6 ל-24)",a+b===30&&a>=6&&b>=6,{a5s:a,a5s2:b});
// 2. קישור ישיר ל-a5s.html (W40): גם מתפצל ודביק
a=0;b=0;for(let i=0;i<30;i++){const c=await ctx();const r=await land(c,"a5s.html?utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_w40&utm_content=w2_ben");
 if(r.page==="a5s2.html"&&r.exp==="a5s_v2")b++;else if(r.page==="a5s.html"&&r.exp==="a5s_v1")a++;
 if(i===0)ok("a5s ישיר: utm נשמר ו-exp נוסף",/utm_content=w2_ben/.test(r.qs)&&/exp=a5s_v[12]/.test(r.qs),r.qs);
 const r2=await land(c,"a5s.html?aff=rami");if(i<2)ok("a5s ישיר: ביקור שני - אותו דף",r2.page===r.page,[r.page,r2.page]);await c.close()}
ok("a5s ישיר: 30 דפדפנים מתפצלים (כל צד בין 6 ל-24)",a+b===30&&a>=6&&b>=6,{a5s:a,a5s2:b});
// 3. כפייה v2=1 / v2=0, ו-a5s2 ישיר לא מפנה
{const c=await ctx();const r=await land(c,"a5s.html?v2=1&test=1");ok("v2=1 כופה a5s2 ומוריד את v2 מהכתובת",r.page==="a5s2.html"&&!/v2=/.test(r.qs)&&r.exp==="a5s_v2",r);
 const r2=await land(c,"go.html?v2=0&x=1");ok("v2=0 כופה a5s גם אחרי שיבוץ ל-v2",r2.page==="a5s.html"&&r2.exp==="a5s_v1"&&r2.ls==="0",r2);await c.close()}
{const c=await ctx();const r=await land(c,"a5s2.html?utm_source=x");ok("a5s2 ישיר: נשאר ב-a5s2, בלי שגיאות",r.page==="a5s2.html"&&r.v==="a5s2"&&r.errs.length===0,r);await c.close()}
{const c=await ctx();const r=await land(c,"a5s.html?exp=cold_2211&utm_campaign=lenatzeach_cold");ok("exp אחר (ישן) לא נדרס כשנשארים ב-a5s",r.page!=="a5s.html"||r.exp==="cold_2211",r);await c.close()}
await br.close();console.log(`\n${n-f}/${n} passed`);process.exit(f?1:0)})();
