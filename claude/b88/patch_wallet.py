# ב41/ב62 (ראשי 13.11): הורדת הודעות הארנק בדף התשלום (A ו-B, אותו קובץ checkout.html).
#  1. ההודעה הקבועה "כרגע Apple Pay ו-Google Pay לא זמינים" (ב41).
#  2. השורה על הארנק בהודעת הכשל הכללית.
#  3. הנוסח המיוחד לדחייה 60000303 (ב62) - אחרי ההסרה, דחייה כזו מקבלת את הודעת הכשל הכללית כמו כל דחייה אחרת.
# פריסה רק אחרי שרכישת הבדיקה של בן ב-Apple Pay עוברת ואחרי "מאשר".
# שימוש: python3 patch_wallet.py <checkout.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)
rep('<p class="walnote" id="walNote">כרגע Apple Pay ו-Google Pay לא זמינים. אפשר לשלם בכרטיס אשראי כרגיל.</p><!-- ב41: הודעה זמנית בגרסאות A ו-B. להסיר כשכאל מסיימים את המעבר למסוף אינטרנטי -->',
    '<!-- ב41: ההודעה הזמנית על Apple Pay ו-Google Pay הוסרה אחרי שכאל השלימו את המעבר למסוף אינטרנטי -->')
rep(' <b class="wal">התשלום בארנק (Apple Pay / Google Pay) לא עבר? הקלידו את פרטי הכרטיס בטופס למטה.</b>', ' ')
import re
i = s.index('  /* ב62 (תיקון 06.11): דחייה 60000303')
j = s.index('כל הכרטיסים עובדים."); }', i) + len('כל הכרטיסים עובדים."); }')
s = s[:i] + '  /* ב62: הנוסח המיוחד לדחייה 60000303 (כשל ארנק) הוסר יחד עם ב41 - דחייה כזו מקבלת את הודעת הכשל הכללית */' + s[j:]
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
