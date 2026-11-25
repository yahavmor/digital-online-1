# ב124 (25.11, מאשר יהב): landing_option2 - ב-marketer=amir ה-Lead נשלח גם לפיקסל NLP - Digital Online (1651086743466533),
#  כי הפיקסל של אמיר (992417836756468) לא נגיש לנו והקמפיין שלו ממטב ל-Lead בפיקסל NLP. שאר המשווקים ללא שינוי.
#  ל-NLP נשלח רק Lead (trackSingle), בלי PageView ובלי InitiateCheckout. הסרה: למחוק את השורה כשאמיר ישתף את הפיקסל שלו.
# שימוש: python3 patch_b124.py <landing_option2.html> <out>
import sys
s=open(sys.argv[1],encoding="utf8").read()
old="  try { if(typeof fbq==='function') fbq('track','Lead'); } catch(e) {}\n"
assert s.count(old)==1, s.count(old)
new=old+("  /* ב124: אמיר - ה-Lead גם לפיקסל NLP - Digital Online, עד שאמיר משתף את הפיקסל שלו. רק Lead, בלי PageView */\n"
         "  try { if(typeof fbq==='function' && mkCode==='amir'){ fbq('init','1651086743466533'); fbq('trackSingle','1651086743466533','Lead'); } } catch(e) {}\n")
s=s.replace(old,new,1)
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2])
