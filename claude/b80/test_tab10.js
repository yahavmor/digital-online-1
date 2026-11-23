// ב80: לשונית 10 לפני/אחרי. שימוש: node test_tab10.js <rows.tsv> (ייצוא גיליון האירועים, לא בריפו). שרת מקומי על 8780 עם nlp/dashboard.html (חדש) ו-dashboard_main.html (הנוכחי)
const {chromium,devices}=require('playwright');const fs=require('fs');const ROWS=fs.readFileSync(process.argv[2],"utf8");
const AFFS="affiliates\tname\tpct\tactive\tfee\nshahar\tשחר\t74\ttrue\t220\nrachel\tרחל\t74\ttrue\t220\namir\tאמיר\t74\ttrue\t220\ngal\tגל\t74\ttrue\t220\nyahel\tיהל\t74\ttrue\t220";
const SPEND="key\tvalue\n2026-11-09|aff_shahar\t20\n2026-11-09|aff_rachel\t20\n2026-11-09|aff_amir\t40\n2026-11-09|aff_gal\t40\n2026-11-09|aff_yahel\t40\n2026-11-10|aff_amir\t15\n2026-11-10|aff_amir_ic\t20\n";
const setTime=async c=>{await c.addInitScript(()=>{const F=new Date("2026-11-10T13:05:00").getTime(),D=Date;class X extends D{constructor(...a){a.length?super(...a):super(F)}static now(){return F}}window.Date=X})};
(async()=>{const b=await chromium.launch();let fails=0;
for(const [dn,dev] of [["d",{viewport:{width:1366,height:900}}],["m",devices["iPhone 13"]]])for(const pg of ["dashboard_main.html","dashboard.html"]){
 const c=await b.newContext(dev);await setTime(c);const errs=[],saved=[];
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com")){const q=new URL(u).searchParams,a=q.get("action")||"";if(a==="spend_set"){saved.push(q.get("creative")+"="+q.get("amount"));return r.fulfill({status:200,body:"ok"})}
  const body={rows:ROWS,spend:SPEND,affiliates:AFFS,refunds:"refunds\n",paid:"paid\n"}[a];return r.fulfill({status:200,body:body==null?a:body});}
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("http://127.0.0.1:8780/nlp/"+pg+"#aud",{waitUntil:"networkidle"});await p.waitForTimeout(1500);
 await p.click('nav.tabs button[data-s="aud"]');await p.waitForTimeout(800);
 const g=t=>p.$$eval(t+" tr",rs=>rs.map(r=>[...r.children].map(x=>x.innerText.replace(/\s+/g," ").trim()).join(" | ")));
 const out={camp:await g("#audCamp"),sum:(await p.$eval("#audSum",e=>e.innerText)).split("\n"),opts:await p.$$eval("#audSpCamp option",o=>o.map(x=>x.value)),hs:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),note:await p.$eval("#audNote",e=>e.innerText),sp:await g("#audSpList")};
 if(pg==="dashboard.html"){await p.selectOption("#audSpCamp","rachel_ic");await p.fill("#audSpAmt","12");await p.click("#audSpSave");await p.waitForTimeout(500);
  await p.screenshot({path:__dirname+"/aud_"+dn+".png",fullPage:dn==="d"});
  const chk=[["errors none",!errs.length],["9 rows (5 before + 3 after + header)",out.camp.length===9],["spend options",out.opts.join(",")==="shahar,rachel,rachel_ic,amir,amir_ic,gal,yahel,yahel_ic"],["saved aff_rachel_ic",saved.includes("aff_rachel_ic=12")],["no hscroll",!out.hs],
   ["rachel after = cold",out.camp.some(r=>/^רחל · קהל קר אחרי/.test(r))],["rachel before = warm",out.camp.some(r=>/^רחל · קהל חם לפני/.test(r))],["amir after spend 20",out.camp.some(r=>/^אמיר · קהל חם אחרי.*20 ₪/.test(r))]];
  chk.forEach(([n,v])=>{if(!v)fails++;console.log(v?"PASS":"FAIL",dn,n)});}
 console.log("=====",dn,pg,"errors:",errs.length?errs:"none","| hscroll:",out.hs,"| saved:",saved.join(","));
 console.log(out.camp.join("\n"));console.log("--");console.log(out.sum.join("\n"));console.log("-- note:",out.note);console.log("-- spend:",out.sp.join(" || "));
 await c.close();}
await b.close();console.log("FAIL",fails)})();
