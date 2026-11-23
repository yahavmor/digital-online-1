// ב87: אזור המשווקים מסנן שורות בדיקה (עמודה 5 = 1 מ-8252865). הקובץ החי, תשובה מדומה
const {chromium}=require("playwright"),fs=require("fs");const P=fs.readFileSync(process.argv[2],"utf8");
const ts="2026-11-12 20:26:18";
const mk=rows=>"me\tyosef\tיוסף\t220\t0\nrows\n"+rows.join("\n")+"\nleads\n\nrefunds\n\npaid\n";
const cases=[["test row only (flag 1) → 0",[ts+"\tview\tsidT\t\t1"],"0"],["meta_scan only → 0",[ts+"\tmeta_scan:view\tsidM\t\t1"],"0"],["real row (flag 0) → 1",[ts+"\tview\tsidR\t\t0"],"1"],["real + test → 1",[ts+"\tview\tsidR\t\t0",ts+"\tview\tsidT\t\t1"],"1"]];
(async()=>{const b=await chromium.launch();let n=0,f=0;
for(const [nm,rows,exp] of cases){const c=await b.newContext({timezoneId:"Asia/Jerusalem"});await c.clock.setFixedTime(new Date("2026-11-12T21:00:00+02:00"));
 await c.route("**/*",r=>{const u=r.request().url();if(u.startsWith("https://local.test/"))return r.fulfill({status:200,contentType:"text/html; charset=utf-8",body:P});if(u.includes("make.com"))return r.fulfill({status:200,contentType:"text/plain; charset=utf-8",body:mk(rows)});return r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto("https://local.test/nlp/partner.html#t=TESTTOKEN_xxxxxxxxxxxxxxxxxxxxxxxx");await p.waitForTimeout(1500);
 const v=await p.evaluate(()=>{const t=[...document.querySelectorAll("#tiles .tile, #tiles > *")].find(x=>/ביקורים/.test(x.innerText));return t?t.innerText.replace(/\s+/g," "):"(no tile)"});
 n++;const good=new RegExp("ביקורים "+exp+"( |$)").test(v)||new RegExp("^"+exp+" ביקורים").test(v);if(!good)f++;console.log(good?"PASS":"FAIL",nm,"|",v);await c.close()}
console.log("TOTAL",n-f+"/"+n);await b.close()})();
