# ביט (ראשי 13.11): כפתור "תשלום בביט" בדף התשלום (A ו-B, אותו קובץ checkout.html).
#  מופיע רק אחרי סימון התיבה של קארדקום (רק אז נוצר דף התשלום) ורק כשתשובת 7827398 כוללת bit_url
#  (מ-UrlToBit של LowProfile/Create; לפי התיעוד: https://secure.cardcom.solutions/api/LPC5/Bit?...).
#  בלי bit_url - שום שינוי בדף. ביטול הסימון מסתיר את הכפתור יחד עם טופס התשלום.
#  לחיצה: אירוע checkout_bit_click ומעבר לדף הביט של קארדקום באותו חלון. זה אותו דף תשלום (LowProfile),
#  ולכן אותן כתובות חזרה (הצלחה/כשל), אותו webhook ל-7827404, ו-thanks.html מוצא את העסקה לפי cc_lp או lowprofilecode.
# שימוש: python3 patch_bit.py <checkout.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)
rep('<div class="frame">',
    '<div class="bitwrap" id="bitWrap" hidden><a class="bitbtn" id="bitBtn" href="#" rel="noopener">תשלום בביט</a><span class="bitor">או</span></div><!-- ביט: מעל טופס הכרטיס, כדי שייראה בלי לגלול; רק אחרי סימון התיבה ורק כש-7827398 מחזיר bit_url -->\n<div class="frame">')
rep('.frame{position:relative;', '.bitwrap{margin:0 0 10px;text-align:center}.bitwrap[hidden]{display:none}.bitor{display:block;color:var(--muted);font-size:14px;margin:8px 0 0}\n.bitbtn{display:flex;justify-content:center;align-items:center;width:100%;min-height:52px;border:1.5px solid var(--ink);border-radius:14px;background:#fff;color:var(--ink);font-weight:800;font-size:17px;text-decoration:none}\n.bitbtn:focus-visible{outline:3px solid var(--gold2);outline-offset:2px}\n.frame{position:relative;')
rep('function lockPay(){ const f=$("cc");', 'function lockPay(){ $("bitWrap").hidden=true; const f=$("cc");')
rep('const f = $("cc"); f.src = d.url; f.hidden = false; const tl=Date.now();',
    '''{ const bu=String(d.bit_url||""); /* ביט: רק כתובת https של קארדקום, ורק כשהתיבה מסומנת */
          if(TB.checked && /^https:\\/\\/[^\\/]*cardcom\\.solutions\\//i.test(bu)){ const b=$("bitBtn"); b.href=bu; $("bitWrap").hidden=false;
            if(!b.__nlp){ b.__nlp=1; b.addEventListener("click",()=>{ track("checkout_bit_click"); }); } } else $("bitWrap").hidden=true; }
        const f = $("cc"); f.src = d.url; f.hidden = false; const tl=Date.now();''')
rep('function load(){\n    if(!TB.checked){ lockPay(); return; } $("tLock").hidden=true;', 'function load(){\n    if(!TB.checked){ lockPay(); return; } $("tLock").hidden=true; $("bitWrap").hidden=true;')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
