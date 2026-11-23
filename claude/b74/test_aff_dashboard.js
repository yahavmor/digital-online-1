const {chromium}=require('playwright');const fs=require('fs');const ROWS=fs.readFileSync(__dirname+"/rows_aff.tsv","utf8");
const AFFS="affiliates\tname\tpct\tactive\tfee\ngal\tגל\t74\ttrue\t220\namir\tאמיר\t74\ttrue\t0";
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:1366,height:900}});const errs=[];
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com")){const a=new URL(u).searchParams.get("action")||"";
  const body={rows:ROWS,spend:"key\tvalue\n",affiliates:AFFS,refunds:"refunds\n9903\n",paid:"paid\n"}[a];return r.fulfill({status:200,body:body==null?a:body});}
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));
 await p.goto("http://127.0.0.1:8771/nlp/dashboard.html#af",{waitUntil:"networkidle"});await p.waitForTimeout(1200);
 await p.click('nav.tabs button[data-s="af"]');await p.waitForTimeout(600);
 const t=await p.evaluate(()=>{const g=t=>[...document.querySelectorAll(t+" tr")].map(r=>[...r.children].map(x=>x.innerText.replace(/\s+/g," ").trim()).join(" | "));return {af:g("#afTable"),buys:g("#afBuys"),note:document.getElementById("afNote").innerText}});
 console.log(t.af.join("\n"));console.log("---");console.log(t.buys.join("\n"));console.log("---",t.note.slice(0,170));console.log("errors",errs);
 await p.screenshot({path:__dirname+"/af_d.png",fullPage:true});await b.close()})();
