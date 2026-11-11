// ב82: בדף התשלום, A ו-B: במצב הרגיל בלי "צריך עזרה? ... WhatsApp" ובלי שורת "תמיכה"; אחרי תשלום שנכשל הקישור מופיע. האירועים לא השתנו
const {chromium,devices}=require('playwright');const B=process.argv[2],DIR=process.argv[3];
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",n,e)};
(async()=>{const b=await chromium.launch();
for(const co of ["a","b"])for(const st of ["","&status=failed"]){
 const c=await b.newContext({...devices["iPhone 13"]});const evs=[],errs=[];
 await c.route("**/*",r=>{const u=r.request().url();if(/hook\.eu1\.make\.com/.test(u)){evs.push(new URLSearchParams(r.request().postData()||"").get("ev"));return r.fulfill({status:200,body:""})}return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(String(e)));
 await p.goto(B+"checkout.html?co="+co+"&v=a5v4&test=1"+st,{waitUntil:"networkidle"});await p.waitForTimeout(500);
 const s=await p.evaluate(()=>({help:!document.getElementById("help").hidden,helpTxt:document.getElementById("help").textContent.trim(),tmicha:[...document.querySelectorAll(".deal dt")].map(d=>d.textContent).includes("תמיכה"),rows:document.querySelectorAll(".deal dt").length,wa:[...document.querySelectorAll('a[href*="wa.me"]')].filter(a=>!a.closest("#help[hidden]")).length}));
 const tag="co="+co+(st?" failed":" normal");
 if(!st) ok(tag+": no WhatsApp help link, no תמיכה row (6 rows left)",!s.help&&s.wa===0&&!s.tmicha&&s.rows===6,JSON.stringify(s));
 else ok(tag+": WhatsApp help link shown after a failed payment, no תמיכה row",s.help&&s.wa===1&&/WhatsApp/.test(s.helpTxt)&&!s.tmicha,JSON.stringify(s));
 ok(tag+": no JS errors, page event sent ("+(st?"checkout_failed":"checkout_view")+")",errs.length===0&&evs.includes(st?"checkout_failed":"checkout_view"),JSON.stringify({errs,evs}));
 if(DIR){await p.screenshot({path:DIR+"/checkout_"+co+(st?"_failed":"")+"_mobile.jpg",type:"jpeg",quality:80,fullPage:true});}
 await c.close();}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
