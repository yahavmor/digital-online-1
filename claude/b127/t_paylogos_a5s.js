// ב127.1: לוגואי תשלום ב-a5s - 4 שורות (hero, offer, form1, form2), ביט מוצג, הטקסט כולל ביט, התמונות נטענות, הטופס עדיין עובד. node t_paylogos_a5s.js <a5s.html> <assets dir> [shot.png]
const {chromium,devices}=require("playwright"),fs=require("fs");const [FILE,ASSETS,SHOT]=process.argv.slice(2);
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,JSON.stringify(i)||"")}else console.log("ok  ",m)};
(async()=>{const br=await chromium.launch();const c=await br.newContext({...devices["iPhone 13"]});const errs=[],hooks=[];
 await c.route("**/*",r=>{const u=new URL(r.request().url());
  if(u.hostname==="funnel.digitalonline.co.il"){if(u.pathname.endsWith("/a5s.html"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:fs.readFileSync(FILE,"utf8")});
   const m=u.pathname.match(/assets\/pay\/([a-z-]+\.svg)$/);if(m&&fs.existsSync(ASSETS+"/"+m[1]))return r.fulfill({status:200,contentType:"image/svg+xml",body:fs.readFileSync(ASSETS+"/"+m[1])});
   return r.fulfill({status:204,body:""})}
  if(u.hostname.endsWith("make.com")){hooks.push(r.request().postData()||"");return r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({code:"0",url:"https://secure.cardcom.solutions/EA/mock",lp:"lp1"})})}
  if(u.hostname.endsWith("cardcom.solutions"))return r.fulfill({status:200,contentType:"text/html",body:"<html>mock</html>"});
  return r.fulfill({status:200,contentType:"text/javascript",body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("https://funnel.digitalonline.co.il/nlp/a5s.html?claude=b127",{waitUntil:"load"});await p.waitForTimeout(1200);
 const R=await p.evaluate(()=>[...document.querySelectorAll("[data-paylogos]")].map(e=>({k:e.getAttribute("data-paylogos"),shown:[...e.querySelectorAll("li")].filter(l=>!l.hidden).map(l=>l.getAttribute("data-pl")),imgs:[...e.querySelectorAll("li:not([hidden]) img")].map(i=>i.naturalWidth>0),txt:e.querySelector(".pl-t").textContent,inForm:!!e.closest("form.lpf")})));
 ok("3 שורות לוגואים: hero (מתחת לכפתור הראשי), offer (מתחת לטופס 1), final (מתחת לטופס 2)",R.map(x=>x.k).join(",")==="hero,offer,final",R.map(x=>x.k));
 ok("בכל שורה: Apple Pay, Google Pay, ביט ואשראי",R.every(x=>x.shown.join(",")==="apple,google,bit,card"),R.map(x=>x.shown));
 ok("כל התמונות נטענות",R.every(x=>x.imgs.length===4&&x.imgs.every(Boolean)),R.map(x=>x.imgs));
 ok("הטקסט: אפשר לשלם ב-Apple Pay, Google Pay, ביט או אשראי",R.every(x=>/ביט או אשראי/.test(x.txt)),R.map(x=>x.txt));
 ok("שורות offer ו-final צמודות לטפסים (מיד אחרי </form>)",(()=>{const h=require("fs").readFileSync(FILE,"utf8");return /<\/form>\s*<div class="paylogos" data-paylogos="offer"/.test(h)&&/<\/form>\s*<div class="paylogos" data-paylogos="final"/.test(h)})());
 // הטופס עדיין עובד: מילוי ושליחה -> checkout_details + מעבר לקארדקום
 await p.fill("#lfName1","בדיקה ב127");await p.fill("#lfEmail1","b127@example.com");await p.check("#lfBox1");
 await Promise.all([p.waitForURL(/cardcom|checkout/,{timeout:8000}).catch(()=>{}),p.click('form#lpForm1 button[type="submit"]')]);await p.waitForTimeout(800);
 ok("שליחת הטופס עדיין עובדת (form_submit נשלח)",hooks.some(h=>/ev=form_submit/.test(h)),hooks.filter(h=>/ev=form/.test(h)).map(h=>h.slice(0,40)));
 ok("בלי שגיאות JS",errs.length===0,errs);
 if(SHOT){const p2=await c.newPage();await p2.goto("https://funnel.digitalonline.co.il/nlp/a5s.html?claude=b127",{waitUntil:"load"});await p2.waitForTimeout(800);const el=await p2.$('form#lpForm1');await el.scrollIntoViewIfNeeded();await p2.waitForTimeout(400);await p2.screenshot({path:SHOT});}
 await br.close();console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)})();
