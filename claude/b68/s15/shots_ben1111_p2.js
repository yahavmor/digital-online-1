// ב68 הערות בן 11.11 (חלקים 1-3): צילום מובייל (אייפון 13) לכל סעיף 1-21 ב-a5v4. 16 מגרסת התצוגה (a5v4p, המקום השמור מסומן); 20 גם מגרסת הבדיקה (a5v4s, נגן עם קטע בדיקה) ומגרסת התצוגה.
// שימוש: node shots_ben1111_p2.js <base של nlp/> <dir>
const {chromium,devices}=require('playwright');const [B,DIR]=process.argv.slice(2);
const S=[
 ["01_hero_sentence","a5v4",null],
 ["02_offer_price_text","a5v4",'#offer .cheap'],
 ["03_inside_lead","a5v4",'[data-name="מה יש בפנים"] .lead'],
 ["04_reality_cards","a5v4",'[data-name="איך נראית המציאות"] .reality'],
 ["05_outcomes_communication","a5v4",'[data-name="עם מה תצא"] .outcomes > div:last-child'],
 ["06_fit_no_magic","a5v4",'[data-name="למי מתאים"] .fitlist'],
 ["07_offer_no_whatsapp","a5v4",'#offer [data-cta="offer"]'],
 ["08_button_shine","a5v4",'[data-cta="keys"]'],
 ["09_cards_depth","a5v4",'[data-name="איך נראית המציאות"] .reality .r'],
 ["10_pause","a5v4",'[data-name="רגע לפני"]'],
 ["11_belief_top","a5v4",'[data-name="מה אם"] h2'],
 ["11_belief_bottom","a5v4",'[data-name="מה אם"] .key'],
 ["12_notcourse","a5v4",'.notcourse'],
 ["13_lock_in_button","a5v4",'[data-cta="know"]'],
 ["14_colors_offer","a5v4",'#offer .pcard'],
 ["15_19_t15_e15","a5v4",'[data-name="תוצאות אמיתיות"] .v4-slot-h'],
 ["16_wa_pending","a5v4p",'.car-track'],
 ["17_peek_until_clip","a5v4",'[data-name="מה יש בפנים"] .peek'],
 ["18_footer","a5v4",'footer'],
 ["20_player_test_clip","a5v4s",'[data-name="מה יש בפנים"] .v4-peek'],
 ["20_player_slot","a5v4p",'[data-name="מה יש בפנים"] .v4-peek']];
(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices["iPhone 13"]});
 await c.route("**/*",r=>{const u=r.request().url();return u.startsWith("http://127.0.0.1")?r.continue():r.fulfill({status:204,body:""})});
 const pages={};
 for(const [n,pg,sel] of S){
  if(!pages[pg]){const p=await c.newPage();await p.goto(B+pg+".html?internal=1",{waitUntil:"networkidle"});await p.waitForTimeout(400);
   await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){scrollTo({top:y,behavior:"instant"});await new Promise(r=>setTimeout(r,25))}});await p.waitForTimeout(900);pages[pg]=p;}
  const p=pages[pg];
  if(!sel)await p.evaluate(()=>scrollTo({top:0,behavior:"instant"}));
  else await p.evaluate(s=>{const e=document.querySelector(s);const r=e.getBoundingClientRect();scrollTo({top:Math.max(0,scrollY+r.top-Math.max(60,(innerHeight-Math.min(r.height,innerHeight-120))/2)),behavior:"instant"})},sel);
  await p.waitForTimeout(n.startsWith("08")?1400:700);await p.screenshot({path:DIR+"/a5v4_"+n+".jpg",type:"jpeg",quality:78});}
 await b.close()})();
