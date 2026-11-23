// item 14: AA contrast audit of a5v4 text (solid backgrounds walked up the tree; gradient backgrounds sampled by their first color stop)
const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"],deviceScaleFactor:1});
await c.route("**/*",r=>r.request().url().startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""}));
const p=await c.newPage();await p.goto(process.argv[2]+"a5v4.html?internal=1",{waitUntil:"networkidle"});
await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,15))}});await p.waitForTimeout(800);
const r=await p.evaluate(()=>{const P=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);return [a[0],a[1],a[2],a.length>3?a[3]:1]};
 const L=c=>{const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
 const mix=(t,b)=>[0,1,2].map(i=>t[i]*t[3]+b[i]*(1-t[3])).concat(1);
 function bg(e){const st=[];for(let x=e;x;x=x.parentElement){const cs=getComputedStyle(x);let c=P(cs.backgroundColor);if((!c||c[3]===0)&&cs.backgroundImage.includes("gradient")){c=P(cs.backgroundImage)}if(c&&c[3]>0){st.push(c);if(c[3]>=1)break}}let out=[14,14,16,1];for(let i=st.length-1;i>=0;i--)out=mix(st[i],out);return out}
 const bad=[];let n=0;document.querySelectorAll("body *").forEach(e=>{if(e.closest(".sticky,.sp-modal,script,style,svg"))return;const own=[...e.childNodes].some(t=>t.nodeType===3&&t.textContent.trim().length>1);if(!own)return;const r=e.getBoundingClientRect();if(!r.width||!r.height)return;const cs=getComputedStyle(e);if(cs.visibility==="hidden"||+cs.opacity===0)return;
  let fg=P(cs.color);const b=bg(e);fg=mix(fg,b);let op=1;for(let x=e;x;x=x.parentElement)op*=+getComputedStyle(x).opacity;if(op<1)fg=mix(fg.slice(0,3).concat(op),b);
  const l1=L(fg),l2=L(b),cr=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);const big=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.66&&+cs.fontWeight>=700);n++;
  if(cr<(big?3:4.5))bad.push({t:e.textContent.trim().slice(0,40),cls:e.className&&e.className.baseVal===undefined?e.className:"",cr:+cr.toFixed(2),fg:fg.slice(0,3).map(Math.round).join(","),bg:b.slice(0,3).map(Math.round).join(","),fs:cs.fontSize})});
 return {n,bad}});
console.log("checked",r.n,"below AA",r.bad.length);r.bad.slice(0,30).forEach(x=>console.log(JSON.stringify(x)));await b.close()})();
