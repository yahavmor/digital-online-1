// ב68: בדיקת go.html והדשבורד אחרי make_exp.py. שימוש: node t_exp.js <base url של nlp/> <winner a5|pr2> [rows.tsv]
const {chromium,devices}=require('playwright');const fs=require('fs');const B=process.argv[2],W=process.argv[3],NEW=W+"v3",ROWS=process.argv[4]?fs.readFileSync(process.argv[4],"utf8"):"";
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",n,e)};
async function ctx(b){const c=await b.newContext(devices["iPhone 13"]);
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com")){const a=new URL(u).searchParams.get("action")||"";const body={rows:ROWS,spend:"key\tvalue\n",affiliates:"affiliates\tname\tpct\tactive\tfee\n",refunds:"refunds\n",paid:"paid\n"}[a];return r.fulfill({status:200,body:body==null?"ok":body})}
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});return c}
(async()=>{const b=await chromium.launch();
 // 1. חלוקה: 200 דפדפנים חדשים
 const cnt={};for(let i=0;i<200;i++){const c=await ctx(b);const p=await c.newPage();await p.goto(B+"go.html?utm_source=facebook&utm_medium=paid&utm_content=p25",{waitUntil:"commit"});await p.waitForURL(/\/(a5|pr2|a5v3|pr2v3)\.html/);const u=new URL(p.url());const k=u.pathname.split("/").pop()+"|"+u.searchParams.get("exp");cnt[k]=(cnt[k]||0)+1;await c.close();}
 const keys=Object.keys(cnt);ok("split only between "+W+" and "+NEW+" with new exp",keys.length===2&&keys.every(k=>(k.startsWith(W+".html|")||k.startsWith(NEW+".html|"))&&k.endsWith("|v3_1411")),JSON.stringify(cnt));
 const a=cnt[W+".html|v3_1411"]||0;ok("roughly 50/50 (200 browsers)",a>=70&&a<=130,a+"/200");
 // 2. קבוע לדפדפן
 {const c=await ctx(b);const p=await c.newPage();const seen=new Set();for(let i=0;i<4;i++){await p.goto(B+"go.html?utm_content=p25",{waitUntil:"commit"});await p.waitForURL(/\/(a5|pr2|a5v3|pr2v3)\.html/);seen.add(new URL(p.url()).pathname);}ok("sticky per browser",seen.size===1,[...seen].join(","));await c.close();}
 // 3. מי ששובץ ב-ap2_0811 ממשיך לדף שלו, מחוץ לניסוי החדש
 for(const old of ["a5","pr2"]){const c=await ctx(b);await c.addInitScript(o=>{try{localStorage.setItem("nlp_go_ap2_0811",o)}catch(e){}},old);const p=await c.newPage();await p.goto(B+"go.html?utm_content=p25",{waitUntil:"commit"});await p.waitForURL(/\.html\?/);const u=new URL(p.url());
  ok("ap2 assignee "+old+" keeps page, exp=ap2_0811",u.pathname.endsWith("/"+old+".html")&&u.searchParams.get("exp")==="ap2_0811",u.pathname+" "+u.searchParams.get("exp"));await c.close();}
 // 4. אינסטגרם אורגני עדיין ל-a
 {const c=await ctx(b);const p=await c.newPage();await p.goto(B+"go.html?utm_source=instagram&utm_medium=bio",{waitUntil:"commit"});await p.waitForURL(/a\.html/);ok("ig_org still to a",new URL(p.url()).searchParams.get("route")==="ig_org");await c.close();}
 // 5. הדשבורד נטען עם הניסוי החדש
 {const c=await ctx(b);const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));await p.goto(B+"dashboard.html",{waitUntil:"networkidle"});await p.waitForTimeout(1500);
  const sub=await p.evaluate(()=>document.querySelector(".sub")?document.querySelector(".sub").innerText:"");
  const exps=await p.evaluate(()=>EXPERIMENTS.slice(0,2).map(e=>e.id+":"+e.end));
  ok("dashboard: no JS errors",errs.length===0,errs.join("|"));ok("dashboard: header shows new experiment",sub.includes("v3_1411")&&sub.includes(NEW),sub.slice(0,80));
  ok("dashboard: experiments list new first, ap2 ended",exps[0]==="v3_1411:"&&exps[1]==="ap2_0811:2026-11-14",exps.join(" "));
  for(const t of ["op","ov","lab","aud"]){const btn=await p.$('nav.tabs button[data-s="'+t+'"]');if(btn){await btn.click();await p.waitForTimeout(400);}}
  ok("dashboard: tabs render without errors",errs.length===0,errs.join("|"));await c.close();}
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
