# ב114 המשך, מסלול תקלה: מסתיר את כפתור "תשלום בביט" שלנו ב-checkout.html (הכפתור בתוך דף קארדקום נשאר).
# שימוש: python3 patch_hide_bitbtn.py <checkout.html> <out.html>
import sys
s=open(sys.argv[1],encoding="utf8").read()
old='if(TB.checked && /^https:\\/\\/[^\\/]*cardcom\\.solutions\\//i.test(bu)){'
assert s.count(old)==1,s.count(old)
s=s.replace(old,'const BIT_BTN_OFF=true; /* ב114 המשך (24.11): כפתור הביט שלנו מוסתר עד שההתראה והאימות של עסקת ביט מאומתים */\n          if(!BIT_BTN_OFF && TB.checked && /^https:\\/\\/[^\\/]*cardcom\\.solutions\\//i.test(bu)){',1)
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2])
