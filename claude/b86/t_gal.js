// ב86 - גל: "לפני" עד 10.11 09:16, "חפיפה" עד 11.11 07:52 (בלי הוצאה, עם הערה), "אחרי" מ-11.11 07:52 עם aff_gal_ic מ-10.11
process.env.TZ="Asia/Jerusalem";const {chromium}=require("playwright"),fs=require("fs");const [O,P,EV,SP]=process.argv.slice(2).map(f=>fs.readFileSync(f,"utf8"));
let n=0,f=0;const ok=(m,c,i)=>{n++;if(!c){f++;console.log("FAIL",m,i||"")}else console.log("PASS",m)};
(async()=>{const b=await chromium.launch();const run=async html=>{const c=await b.newContext({timezoneId:"Asia/Jerusalem"});await c.clock.setFixedTime(new Date("2026-11-13T10:00:00+02:00"));const errs=[];
await c.route("**/*",r=>{const u=new URL(r.request().url());if(u.href.startsWith("https://local.test/"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:html});if(u.hostname.endsWith("make.com")){const a=u.searchParams.get("action");return r.fulfill({status:200,body:{rows:EV,spend:SP,affiliates:"affiliates\tname\tpct\tactive\tfee\n",refunds:"refunds\n",paid:"paid\n"}[a]||""})}return r.fulfill({status:204,body:""})});
const p=await c.newPage();p.on("pageerror",e=>errs.push(e.message));await p.goto("https://local.test/nlp/dashboard.html#aud");await p.waitForTimeout(3000);return {c,p,errs}};
const A=await run(O),B=await run(P);
const st=x=>x.p.evaluate(()=>Object.fromEntries(AUD.seg.map(g=>[g.key,{sp:audSpend(g),from:g.fromT&&g.fromT.toISOString(),to:g.toT&&g.toT.toISOString()}])));const sa=await st(A),sb=await st(B);
console.log(JSON.stringify({pre:sb["gal|pre"],ovl:sb["gal|ovl"],post:sb["gal|post"]}));
ok("gal segments: pre → 10.11 09:16, ovl 10.11 09:16 → 11.11 07:52, post from 11.11 07:52",sb["gal|pre"].to==="2026-11-10T07:16:00.000Z"&&sb["gal|ovl"].from==="2026-11-10T07:16:00.000Z"&&sb["gal|ovl"].to==="2026-11-11T05:52:00.000Z"&&sb["gal|post"].from==="2026-11-11T05:52:00.000Z");
ok("gal pre spend = aff_gal only: 7.19+27.56 = 34.75",Math.abs(sb["gal|pre"].sp.t-34.75)<.001,JSON.stringify(sb["gal|pre"].sp));
ok("gal overlap: no spend of its own",sb["gal|ovl"].sp===null);
ok("gal post spend = aff_gal_ic from 10.11: 42.27+41.33+28.39 = 112, 3 days",Math.abs(sb["gal|post"].sp.t-111.99)<.01&&sb["gal|post"].sp.days===3,JSON.stringify(sb["gal|post"].sp));
ok("other segments unchanged",Object.keys(sa).filter(k=>!/^gal/.test(k)).every(k=>JSON.stringify(sa[k])===JSON.stringify(sb[k])));
const camp=await B.p.evaluate(()=>[...document.querySelectorAll("#audCamp tr")].map(r=>[...r.children].map(x=>x.innerText.replace(/\s+/g," ").trim())));
const g=camp.filter(r=>/^גל/.test(r[0]));console.log(JSON.stringify(g.map(r=>[r[0].slice(0,90),r[2].slice(0,60),r[3]])));
ok("tab 10: 3 gal rows in order לפני / חפיפה / אחרי",g.length===3&&/לפני/.test(g[0][0])&&/חפיפה/.test(g[1][0])&&/אחרי/.test(g[2][0]));
ok("overlap row: time window and the note (no spend, utm_term finding)",/10\.11 09:16 עד 11\.11 07:52|09:16 עד .*07:52/.test(g[1][0])&&/שתי הקבוצות רצו יחד/.test(g[1][2])&&/utm_term/.test(g[1][2]),g[1][0]+" | "+g[1][2]);
const vis=x=>+x.replace(/[^\d].*$/,"");ok("visits split: pre 3, overlap and after have the rest",g[0][3].startsWith("3")||vis(g[0][3])<=3,JSON.stringify(g.map(r=>r[3])));
const opts=await B.p.$$eval("#audSpCamp option",o=>o.map(x=>x.value));
ok("form: aff_gal and aff_gal_ic once each, no empty/null option",opts.filter(v=>v==="aff_gal").length===1&&opts.filter(v=>v==="aff_gal_ic").length===1&&!opts.some(v=>!v||v==="null"),JSON.stringify(opts));
const A2=await run(O),B2=await run(P);const diff=[];for(const t of ["snap","ov","af","co","hub","lab"]){const g2=x=>x.p.evaluate(s=>{setScreen(s);return new Promise(r=>setTimeout(()=>r(document.getElementById("s-"+s).innerText.replace(/עודכן \d\d:\d\d/g,"")),250))},t);if(await g2(A2)!==await g2(B2))diff.push(t)}
ok("other screens unchanged",!diff.length,diff.join());
ok("no JS errors",!B.errs.length,B.errs.join("|"));
console.log("TOTAL",n-f+"/"+n);await b.close()})();
