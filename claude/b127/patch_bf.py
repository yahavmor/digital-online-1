# ב127.2 (ראשי 26.11): טיוטת בלאק פריידיי. עלייה רק אחרי אישור בן + "מאשר ב127.2". a5s: באנר + ספירה לאחור עד שני 30.11 23:59 + תיבת "מתנה כפולה"
#  ליד המחיר. thanks: בתקופה בלי הצעת האפסייל, ובמקום זה הודעת המתנה הכפולה (הגישה לאפליקציה נפתחת ידנית בצ'אט האפליקציה, החלטת יהב 26.11). חזרה אוטומטית אחרי 30.11 23:59
#  (שעון ישראל, UTC+2): הכול לפי השעון בדפדפן, בלי פריסה נוספת. הנוסחים: מיהב (26.11), מחכים לאישור סופי של בן.
# שימוש: python3 patch_bf.py a5s <in> <out> | thanks <in> <out>
import sys
what,src,out=sys.argv[1:4]; s=open(src,encoding="utf8").read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,(what,old[:60],s.count(old)); s=s.replace(old,new,1)
BF_JS='''var BF_START=Date.parse("2026-11-26T00:00:00+02:00"), BF_END=Date.parse("2026-11-30T23:59:59+02:00"); /* ב127.2: חלון בלאק פריידיי, שעון ישראל */
function bfOn(){ var n=Date.now(); return n>=BF_START&&n<=BF_END; }'''
if what=="a5s":
    rep("<header class=\"hero9\" data-sec=\"1\"",
        '<div class="bf-bar" id="bfBar" hidden role="status"><b>בלאק פריידיי עד שני 30.11 בחצות</b><span class="bf-txt">מצטרפים ומקבלים מתנה כפולה - האפליקציה "האוטומט החדש שלי" (97 ₪) ומפגש הטמעה אישי.</span><span class="bf-cd" id="bfCd"></span></div>\n<header class="hero9" data-sec="1"')
    rep('<p class="v4-ko-now"><span>מחיר השקה לזמן מוגבל</span> <b>297 ₪</b></p></div>',
        '<p class="v4-ko-now"><span>מחיר השקה לזמן מוגבל</span> <b>297 ₪</b></p></div><div class="bf-gift" id="bfGift" hidden><b>🎁 מתנה כפולה למצטרפים עד שני 30.11 בחצות:</b><ol><li>האפליקציה "האוטומט החדש שלי" - אימון יומי אישי ו-SOS לרגעים הקשים. 12 חודשי גישה. שווי 97 ₪.</li><li>מפגש הטמעה אישי כשבוע אחרי ההצטרפות - בודקים איפה אתם עומדים ובונים יחד תוכנית תרגול.</li></ol><p class="bf-until">המחיר נשאר 297 ₪. 7 ימי אחריות עם החזר מלא.</p></div>')
    rep(".paylogos{margin:10px auto 0;text-align:center;max-width:420px}",
        ".paylogos{margin:10px auto 0;text-align:center;max-width:420px}\n"
        "/* ב127.2: בלאק פריידיי */.bf-bar{position:sticky;top:0;z-index:60;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:6px 12px;padding:8px 12px;background:#111;color:#fff;border-bottom:2px solid var(--gold2,#e7b94c);font-size:14px;line-height:1.35;text-align:center}.bf-bar[hidden]{display:none}.bf-bar b{color:var(--gold2,#e7b94c);font-weight:900;letter-spacing:.02em}.bf-cd{font-variant-numeric:tabular-nums;font-weight:800;background:rgba(255,255,255,.1);border-radius:8px;padding:2px 8px}\n"
        ".bf-gift{margin:10px 0 2px;padding:12px 14px;border:1.5px dashed var(--gold2,#e7b94c);border-radius:14px;background:rgba(231,185,76,.08);text-align:right}.bf-gift[hidden]{display:none}.bf-gift b{display:block;font-size:17px;margin-bottom:4px}.bf-gift p{margin:0;font-size:14.5px;line-height:1.5}.bf-gift ol{margin:4px 0 0;padding:0 18px 0 0;font-size:14.5px;line-height:1.5}.bf-gift li{margin:0 0 4px}.bf-gift .bf-until{margin-top:6px;font-size:13px;opacity:.75}")
    rep("(function(){var PAYLOGO_BIT=",
        "(function(){ "+BF_JS+'''
  var bar=document.getElementById("bfBar"), gift=document.getElementById("bfGift"), cd=document.getElementById("bfCd");
  function pad(x){ return (x<10?"0":"")+x; }
  function tick(){ var on=bfOn(); if(bar) bar.hidden=!on; if(gift) gift.hidden=!on; if(!on){ clearInterval(iv); return; }
    var ms=BF_END-Date.now(), d=Math.floor(ms/864e5), h=Math.floor(ms%864e5/36e5), m=Math.floor(ms%36e5/6e4), sec=Math.floor(ms%6e4/1e3);
    if(cd){ cd.textContent=""; if(d>0){ cd.appendChild(document.createTextNode(d+(d===1?" יום ו-":" ימים ו-"))); } var t=document.createElement("bdi"); t.textContent=pad(h)+":"+pad(m)+":"+pad(sec); cd.appendChild(t); } }
  var iv=setInterval(tick,1000); tick(); })();
(function(){var PAYLOGO_BIT=''')
elif what=="thanks":
    rep('<p class="sent2" id="sent" data-clarity-mask="True" hidden>',
        '<div class="sent2 bf-note" id="bfNote" hidden><b>🎁 קיבלת מתנה כפולה:</b><ol><li>הגישה לאפליקציה "האוטומט החדש שלי" תגיע במייל תוך 24 שעות.</li><li>כשבוע מהיום ניצור קשר לתיאום מפגש ההטמעה.</li></ol></div>\n<p class="sent2" id="sent" data-clarity-mask="True" hidden>')
    rep('    const UPSELL_ISSUE = "https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd"; /* ב74: 8463664 - קוד חד-פעמי לאפסייל אחרי תשלום מאומת */',
        '    const UPSELL_ISSUE = "https://hook.eu1.make.com/qhq5knj8mf2npzvmn4wufssrsk7uzyqd"; /* ב74: 8463664 - קוד חד-פעמי לאפסייל אחרי תשלום מאומת */\n'
        '    '+BF_JS+' /* ב127.2: בתקופה הגישה לאפליקציה נפתחת ידנית דרך צ\'אט האפליקציה (החלטת יהב 26.11), בדף רק הודעת המתנה */')
    rep('      upsell(0);\n      survey(d);',
        '      if(bfOn()) bfAccess(); else upsell(0); /* ב127.2: בבלאק פריידיי בלי הצעת האפסייל; הגישה לאפליקציה נפתחת לכל רוכש */\n      survey(d);')
    rep('    function ask(n){',
        '''    /* ב127.2: בתקופת בלאק פריידיי - הודעת המתנה הכפולה במקום הצעת האפסייל. הגישה לאפליקציה נפתחת ידנית (צ'אט האפליקציה), אין קריאה לשרת */
    function bfAccess(){ if(framed) return; const note = el("bfNote"); if(note) note.hidden = false; }
    function ask(n){''')
open(out,"w",encoding="utf8").write(s); print("ok",what,out)
