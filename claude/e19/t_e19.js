// ע19: בדיקת הדשבורד עם שורות סינתטיות (לא אמיתיות) של סרטוני הזהב. שימוש: node t_e19.js <base של nlp/> <events.tsv>
const {chromium}=require('playwright');const fs=require('fs');const [B,TSV]=process.argv.slice(2);
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",n,e)};
const now=new Date(),ts=d=>new Date(now-d*6e4).toISOString().replace("T"," ").slice(0,19);
const q=c=>"exp=ap2_0811&go=1&utm_source=facebook&utm_medium=paid&utm_campaign=lenatzeach_lab&utm_id=1&utm_content="+c;
const R=(t,ev,v,sid,qs,extra={})=>{const r={ts:t,ev,variant:v,sid,sec_on_page:"5",max_section:"1",sections:"10",max_scroll_pct:"5",qs,at_section:"",section:"",name:"",video:"",cta:"",checkout_started:"",depth:"",vid:"v_"+sid,dev:"m-ios-fb",nv:"1",act:"",x:"",...extra};return Object.values(r).join("\t")};
const syn=[R(ts(50),"view","a5","g1",q("gold_h1_02")),R(ts(49),"cta_click","a5","g1",q("gold_h1_02"),{cta:"hero_main",at_section:"1"}),R(ts(48),"checkout_view","a5","g1",q("gold_h1_02")),
 R(ts(47),"purchase","a5","g1","cardcom | 297 ILS | deal 999000001 | src facebook",{cta:"cardcom_webhook",name:"-"}),
 R(ts(40),"view","pr2","g2",q("gold_h1_02")),R(ts(30),"view","pr2","g3",q("GOLD_H1_03")),
 R(ts(20),"view","a5","g4",q("gold_h2_01")),R(ts(19),"checkout_view","a5","g4",q("gold_h2_01")),R(ts(10),"view","pr2","g5",q("gold_h2_09"))];
const rows=fs.readFileSync(TSV,"utf8").replace(/\r/g,"").trimEnd()+"\n"+syn.join("\n")+"\n";
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:1400,height:900}});
 await c.route("**/*",r=>{const u=r.request().url();if(u.includes("hook.eu1.make.com")){const a=new URL(u).searchParams.get("action")||"";const body={rows,spend:"key\tvalue\n",affiliates:"affiliates\tname\tpct\tactive\tfee\n",refunds:"refunds\n",paid:"paid\n"}[a];return r.fulfill({status:200,body:body==null?"ok":body})}
  if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();const errs=[];p.on("pageerror",e=>errs.push(e.message));await p.goto(B+"dashboard.html",{waitUntil:"networkidle"});await p.waitForTimeout(1500);
 await p.click('nav.tabs button[data-s="lab"]');await p.waitForTimeout(800);
 const ads=await p.evaluate(()=>[...document.querySelectorAll("#labAds tr")].map(t=>t.innerText.replace(/\s+/g," ")).filter(t=>/gold|זהב|טייק/i.test(t)));
 ok("7 gold rows + the extra code (gold_h2_09)",ads.length===8,ads.length+"");
 ok("named rows (not codes) for the 7 listed",["טייק 1","טייק 2","טייק 3","טייק 4"].every(n=>ads.some(a=>a.includes(n))),ads.slice(0,2).join(" | "));
 ok("codes without entries marked 'עוד לא עלה'",ads.filter(a=>a.includes("עוד לא עלה")).length===4,ads.filter(a=>a.includes("עוד לא עלה")).length+"");
 const g=await p.evaluate(()=>[...document.querySelectorAll("#labGold tr")].slice(1).map(t=>[...t.cells].map(x=>x.innerText.replace(/\s+/g," "))));
 console.log(JSON.stringify(g));
 ok("h1 lists 4 videos (case-insensitive)",g[0]&&/^4 /.test(g[0][1]),g[0]&&g[0][1]);
 ok("h1: 3 people, 1/3 reached checkout, 1 verified purchase",g[0]&&/^3/.test(g[0][3])&&/1\/3/.test(g[0][4])&&g[0][5].trim()==="1",JSON.stringify(g[0]));
 ok("h2: 2 people (incl. unlisted gold_h2_09), 1/2 to checkout, 0 purchases",g[1]&&/^2/.test(g[1][3])&&/1\/2/.test(g[1][4])&&g[1][5].trim()==="0",JSON.stringify(g[1]));
 ok("no JS errors",errs.length===0,errs.join("|"));
 await p.click('nav.tabs button[data-s="cr"]');await p.waitForTimeout(600);ok("creatives tab renders, gold named",errs.length===0&&await p.evaluate(()=>/המוח מחפש חסרונות - טייק 2/.test(document.body.innerText)));
 await p.screenshot({path:__dirname+"/../../../b68/e19_lab.png",fullPage:false});
 await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
