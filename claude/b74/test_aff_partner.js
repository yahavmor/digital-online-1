const {chromium,devices}=require('playwright');
const ts=d=>{const x=new Date(Date.now()-d*864e5);const p=n=>String(n).padStart(2,"0");return x.getFullYear()+"-"+p(x.getMonth()+1)+"-"+p(x.getDate())+" "+p(x.getHours())+":"+p(x.getMinutes())+":"+p(x.getSeconds())};
/* כמו תשובת 8252865 אחרי השינוי המוצע: גם ב-upsell_purchase מוחזר הטקסט עם מספר העסקה */
const BODY=["me\tgal\tגל\t220\t74","rows",
 ts(3)+"\tview\tsg1\t\t0", ts(3)+"\tpurchase\tsg1\tcardcom | 297 ILS | deal 5001 | src ig\t0",
 ts(2.9)+"\tupsell_purchase\tsg1\tupsell97 | 97 ILS | deal 9901 | course_deal 5001\t0", ts(2.9)+"\tupsell_purchase\tsg1\tupsell97 | 97 ILS | deal 9901 | course_deal 5001\t0",
 ts(12)+"\tpurchase\tsg2\tcardcom | 297 ILS | deal 5005 | src ig\t0", ts(12)+"\tupsell_purchase\tsg2\tupsell97 | 97 ILS | deal 9905 | course_deal 5005\t0",
 "leads", "sg1\t"+ts(3)+"\tישראל י\t123","sg2\t"+ts(12)+"\tדנה כ\t456","refunds","paid","9905\t"+ts(1)].join("\n");
(async()=>{const b=await chromium.launch();
for(const [dn,dev] of [["m",devices["iPhone 13"]],["d",{viewport:{width:1280,height:900}}]])for(const pg of ["partner_main.html","partner.html"]){
 const c=await b.newContext(dev);const errs=[];
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com"))return r.fulfill({status:200,headers:{"access-control-allow-origin":"*"},body:BODY});if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("http://127.0.0.1:8771/nlp/"+pg+"#t=abcdefghijklmnopqrstuvwxyz123456",{waitUntil:"networkidle"});await p.waitForTimeout(800);
 await p.click('#range button[data-r="all"]').catch(()=>{});await p.waitForTimeout(300);
 const o=await p.evaluate(()=>({tiles:[...document.querySelectorAll("#tiles .tile")].map(t=>t.innerText.replace(/\s+/g," ")).join(" | "),rows:[...document.querySelectorAll("#leads tbody tr")].map(r=>r.innerText.replace(/\s+/g," ")),note:document.getElementById("feeNote").innerText.slice(0,120)}));
 console.log(dn,pg,"\n tiles:",o.tiles,"\n rows:",o.rows.join(" || "),"\n note:",o.note,"\n errors:",errs.length?errs:"none",
  "\n hscroll:",await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth));
 if(pg==="partner.html")await p.screenshot({path:__dirname+"/partner_"+dn+".png",fullPage:true});await c.close();}
await b.close()})();
