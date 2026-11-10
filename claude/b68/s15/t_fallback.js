// ב68 v4: איך הדף נראה בגופן החלופי (כשהגופן לא הגיע בזמן, font-display optional). משווה מספר שורות בכותרות, בכפתורים ובמחירים
// בין Heebo לגופן המערכת, בודק שאין גלילה הצידה ושאין טקסט שגולש מכפתור, ושומר צילומים. שימוש: node t_fallback.js <base> <dir>
const {chromium,devices}=require('playwright');const [B,DIR]=process.argv.slice(2);
const res=[];const ok=(n,c,e="")=>{res.push(!!c);console.log(c?"PASS":"FAIL",n,e)};
const SEL='h1,h2,h3,.cta,.sub,.price,.now,.pricechip,.priceline,.cta-micro,.v4-sec,.micro,.terms li,.secure li,.tot,.row';
async function run(b,pg,dev,block){const c=await b.newContext(dev);
 await c.route("**/*",r=>{const u=r.request().url();if(block&&/\.woff2/.test(u))return r.abort();if(u.startsWith("http://127.0.0.1"))return r.continue();return r.fulfill({status:204,body:""})});
 const p=await c.newPage();await p.goto(B+pg+".html?internal=1",{waitUntil:"networkidle"});
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,20))}scrollTo(0,0)});await p.waitForTimeout(400);
 const d=await p.evaluate(SEL=>{const out=[];document.querySelectorAll(SEL).forEach((e,i)=>{const r=e.getBoundingClientRect();if(!r.height||e.closest(".sticky"))return;const lh=parseFloat(getComputedStyle(e).lineHeight)||parseFloat(getComputedStyle(e).fontSize)*1.3;
   out.push({k:e.tagName+"."+e.className.split(" ")[0]+"#"+i,lines:Math.round((r.height-parseFloat(getComputedStyle(e).paddingTop)-parseFloat(getComputedStyle(e).paddingBottom))/lh),ovf:[...e.children].some(x=>{const q=x.getBoundingClientRect();return q.width&&(q.left<r.left-2||q.right>r.right+2)}),t:e.innerText.slice(0,30)})});
  return {els:out,hs:document.documentElement.scrollWidth>innerWidth,heebo:document.fonts.check("700 20px Heebo","א")&&[...document.fonts].some(f=>f.family.replace(/"/g,"")==="Heebo"&&f.status==="loaded"),h:document.body.scrollHeight}},SEL);
 const shots=[];if(DIR){await p.screenshot({path:`${DIR}/${pg}_${block?"fallback":"heebo"}_${dev.isMobile?"m":"d"}_1first.png`});const o=await p.$('[data-cta="offer"]');await o.scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-200));await p.waitForTimeout(300);await p.screenshot({path:`${DIR}/${pg}_${block?"fallback":"heebo"}_${dev.isMobile?"m":"d"}_2offer.png`});}
 await c.close();return d}
(async()=>{const b=await chromium.launch();
for(const pg of ["a5v4","pr2v4"])for(const [dn,dev] of [["iphone",devices["iPhone 13"]],["android",devices["Pixel 7"]],["desktop",{viewport:{width:1280,height:900}}]]){
 const H=await run(b,pg,dev,false),F=await run(b,pg,dev,true);const tag=pg+"/"+dn;
 ok(tag+" Heebo loaded normally, fallback when blocked",H.heebo&&!F.heebo,JSON.stringify([H.heebo,F.heebo]));
 ok(tag+" fallback: no horizontal scroll",!F.hs);
 const ov=F.els.filter(e=>e.ovf&&/cta|price|now/.test(e.k));ok(tag+" fallback: no text overflowing a button or price",ov.length===0,JSON.stringify(ov.slice(0,3)));
 const hm=Object.fromEntries(H.els.map(e=>[e.k,e]));const diff=F.els.filter(e=>hm[e.k]&&e.lines!==hm[e.k].lines).map(e=>e.k+" "+hm[e.k].lines+"→"+e.lines+" "+e.t);
 const ctaD=diff.filter(x=>/^A\.cta/.test(x)),big=F.els.filter(e=>hm[e.k]&&Math.abs(e.lines-hm[e.k].lines)>1);
 ok(tag+" fallback: buttons keep their line count",ctaD.length===0,JSON.stringify(ctaD.slice(0,4)));
 ok(tag+" fallback: no element changes by more than 1 line",big.length===0,JSON.stringify(big.slice(0,3).map(e=>e.k+" "+e.t)));
 console.log("   ",tag,"elements",F.els.length,"with ±1 line:",diff.length,"| page height",H.h,"→",F.h,diff.length?"| e.g. "+diff.slice(0,3).join(" / "):"");
}
await b.close();console.log("TOTAL",res.length,"FAIL",res.filter(x=>!x).length)})();
