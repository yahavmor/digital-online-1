# ב127.1 (ראשי 26.11, בן ויהב אישרו; פריסה אחרי "מאשר ב127.1"): a5s - לוגו ביט בשלוש שורות הלוגואים הקיימות
#  (מתחת לכפתור הראשי, מתחת לטופס בכרטיס ההצעה, ומתחת לטופס האחרון), ליד Apple Pay, Google Pay וכרטיס אשראי שכבר שם.
#  הטקסט הופך ל"אפשר לשלם ב-Apple Pay, Google Pay, ביט או אשראי". שינוי של שורה אחת: PAYLOGO_BIT=true (ביט פעיל בקארדקום, אומת ב-ב114).
# שימוש: python3 patch_paylogos_a5s.py <a5s.html> <out>
import sys
s=open(sys.argv[1],encoding="utf8").read()
old="(function(){var PAYLOGO_BIT=false;"; assert s.count(old)==1
s=s.replace(old,"(function(){var PAYLOGO_BIT=true; /* ב127.1 (26.11): ביט פעיל בקארדקום, אומת ב-ב114 */",1)
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2])
