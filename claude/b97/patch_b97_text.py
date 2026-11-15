# ב97 שלב 2: הטקסט "או 3 תשלומים של 99 ₪" ליד המחיר בדף התשלום (B ו-B2, מחשב ומובייל).
# לפרוס רק אחרי ש-3 התשלומים עובדים בטופס של קארדקום (רשימת תשלומים 1-3 מופיעה ועסקת בדיקה בתשלומים עברה) ואחרי "מאשר".
# שימוש: python3 patch_b97_text.py <repo root>
import sys, os
root = sys.argv[1]
p = os.path.join(root, "nlp/checkout.html"); s = open(p, encoding="utf8").read()
pairs = [
 ('<p class="price"><s class="was b2xi">1,290 ₪</s><b>297</b><span>₪</span></p>\n',
  '<p class="price"><s class="was b2xi">1,290 ₪</s><b>297</b><span>₪</span></p>\n<p class="pay3">או 3 תשלומים של 99 ₪</p><!-- ב97: רק אחרי ש-3 תשלומים עובדים בקארדקום -->\n'),
 ('<p class="one1">הקורס המלא + 5 בונוסים · <span class="pgrp">297 ₪</span> חד-פעמי</p>',
  '<p class="one1">הקורס המלא + 5 בונוסים · <span class="pgrp">297 ₪</span> חד-פעמי<small class="pay3m">או 3 תשלומים של 99 ₪</small></p>'),
 ('.one1,.incl-end{display:none}', '.one1,.incl-end{display:none}\n.pay3{margin:2px 0 0;text-align:center;font-size:15px;font-weight:700;color:var(--ink2)}\n.one1 .pay3m{display:block;font-size:13.5px;font-weight:600;color:var(--ink2)}'),
]
for o, n in pairs:
    assert s.count(o) == 1, (o[:60], s.count(o)); s = s.replace(o, n, 1)
open(p, "w", encoding="utf8").write(s); print("ok")
