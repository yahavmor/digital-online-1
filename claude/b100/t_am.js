const { chromium } = require("playwright"), fs = require("fs"), path = require("path"); const H="https://funnel.digitalonline.co.il/nlp/", DIR=path.resolve("b100t/nlp");
(async()=>{const b=await chromium.launch();let ok=0,n=0;
 for(const pg of ["thanks.html","checkout.html"]){const c=await b.newContext();
  await c.addInitScript(()=>{sessionStorage.setItem("cc_det",JSON.stringify({name:"ישראל ישראלי כהן",email:" Test@Example.com ",phone:"050-1234567"}));window.__inits=[];Object.defineProperty(window,"fbq",{configurable:true,set(v){this._f=v},get(){return this._f}});});
  await c.route("**/*",r=>{const u=new URL(r.request().url());if(u.href.startsWith(H)){const fp=path.join(DIR,u.pathname.replace(/^\/nlp\//,""));if(!fs.existsSync(fp))return r.fulfill({status:404,body:""});return r.fulfill({status:200,contentType:fp.endsWith(".html")?"text/html; charset=utf-8":"application/octet-stream",body:fs.readFileSync(fp)})}
   if(u.host.includes("connect.facebook.net"))return r.fulfill({status:200,contentType:"text/javascript",body:"(function(){var q=window.fbq&&window.fbq.queue||[];q.forEach(a=>{if(a[0]==='init')window.__inits.push(a)});})()"});return r.fulfill({status:204,body:""})});
  const p=await c.newPage();await p.goto(H+pg+"?co=b");await p.waitForTimeout(1500);
  const inits=await p.evaluate(()=>window.__inits.concat((window.fbq&&window.fbq.queue||[]).filter(a=>a[0]==="init")));
  const u=(inits[0]||[])[2]||{};n++;const good=u.em==="test@example.com"&&u.ph==="972501234567"&&u.fn==="ישראל"&&u.ln==="כהן"&&!u.external_id;if(good)ok++;
  console.log(pg,good?"PASS":"FAIL",JSON.stringify(u));await c.close()}
 console.log("TOTAL",ok+"/"+n);await b.close()})();
