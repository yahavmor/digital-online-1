# ב69 (ראשי 13.11): דליפת CAPI ברכישת בדיקה. דף התשלום שולח ל-7827398 test=1 כשהביקור מסומן פנימי (INT: test/claude/internal בכתובת, או nlp_int בדפדפן),
# כדי ש-7827398 יוסיף אותו ל-ReturnValue ו-7827404 ידלג על CAPI ועל עמלה (השינוי ב-Make - יהב והראשי בממשק, אחרי "מאשר").
# בלי סימון פנימי - שום שינוי בבקשה.
# שימוש: python3 patch_testflag.py <checkout.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
old = '{ const ow=window.NLP_OWNER?NLP_OWNER():""; if(ow) body.set("aff", ow); }\n'
assert s.count(old) == 1
s = s.replace(old, old + '    if(INT) body.set("test","1"); /* ב69: ביקור פנימי - 7827398 מעביר ל-ReturnValue, ו-7827404 מדלג על CAPI ועל עמלה */\n', 1)
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
