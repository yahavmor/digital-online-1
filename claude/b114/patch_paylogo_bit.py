# ב114 המשך: הלוגו של ביט בשורת אמצעי התשלום. PAYLOGO_BIT=false -> true, בקובץ אחד.
# שימוש: python3 patch_paylogo_bit.py <in.html> <out.html>
import sys
s=open(sys.argv[1],encoding="utf8").read()
old="(function(){var PAYLOGO_BIT=false;"
assert s.count(old)==1,(sys.argv[1],s.count(old))
s=s.replace(old,"(function(){var PAYLOGO_BIT=true; /* ב114 המשך (24.11): ביט פעיל במסוף, אומת ברכישת בדיקה */",1)
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2])
