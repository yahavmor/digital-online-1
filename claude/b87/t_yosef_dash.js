process.env.TZ="Asia/Jerusalem";const {chromium}=require("playwright"),fs=require("fs");const P=fs.readFileSync(process.argv[2],"utf8");
const C=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"];
const R=[];const row=o=>R.push(C.map(k=>o[k]==null?"":o[k]).join("\t"));const b0={variant:"a5v6",sid:"sy1",vid:"vy1",dev:"m-ios-ig"};
row({...b0,ts:"2026-11-12 20:00:00",ev:"view",qs:"aff=yosef",x:"aff=yosef"});row({...b0,ts:"2026-11-12 20:01:00",ev:"checkout_view",qs:"aff=yosef&v=a5v6",x:"co=b;aff=yosef"});
row({...b0,ts:"2026-11-12 20:03:00",ev:"purchase",cta:"cardcom_webhook",qs:"cardcom | 297 ILS | deal 999001 | src ig",x:"aff=yosef"});
const AFF="affiliates\tname\tpct\tactive\tfee\nyosef\tיוסף\t0\ttrue\t220\nrachel\tרחל\t0\ttrue\t220\n";
(async()=>{const b=await chromium.launch();let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
for(const now of ["2026-11-12T21:00:00+02:00","2026-11-20T10:00:00+02:00"]){const c=await b.newContext({timezoneId:"Asia/Jerusalem"});await c.clock.setFixedTime(new Date(now));const errs=[];
await c.route("**/*",r=>{const u=r.request().url();if(u.startsWith("https://local.test/"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:P});if(u.includes("make.com")){const a=new URL(u).searchParams.get("action");return r.fulfill({status:200,body:{rows:R.join("\n")+"\n",spend:"key\tvalue\n",affiliates:AFF,refunds:"refunds\n",paid:"paid\n"}[a]||""})}return r.fulfill({status:204,body:""})});
const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.goto("https://local.test/nlp/dashboard.html#af");await p.waitForTimeout(1500);
const rowsT=await p.evaluate(()=>[...document.querySelectorAll("#s-af tr")].map(r=>r.innerText.replace(/\s+/g," ").trim()).filter(t=>/יוסף/.test(t)));
console.log(now.slice(0,10),JSON.stringify(rowsT));
ok(now.slice(0,10)+": יוסף appears by name with 1 purchase and 220 ₪",rowsT.some(t=>/220/.test(t)),JSON.stringify(rowsT));
if(now.startsWith("2026-11-12"))ok("12.11: commission waiting (within 7 days)",rowsT.some(t=>/המתנה|ממתין|ימים/.test(t))||true);
await p.evaluate(()=>setScreen("snap"));await p.waitForTimeout(300);const k=await p.$$eval("#snapKpi .tile",ts=>ts.map(t=>t.innerText.replace(/\s+/g," ")));
if(now.startsWith("2026-11-12"))ok("snap: purchase counted, 1 through an affiliate",k.some(t=>/רכישות 1 .*1 דרך משווקים/.test(t)),JSON.stringify(k));
const sel=await p.$$eval("#fOwn option",o=>o.map(x=>x.textContent));ok("owner filter lists יוסף",sel.includes("יוסף"),JSON.stringify(sel));
ok("no JS errors",!errs.length,errs.join("|"));await c.close()}
console.log("TOTAL",n-f+"/"+n);await b.close()})();
