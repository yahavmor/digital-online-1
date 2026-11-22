# ב116 (החלטת בן 22.11, "מאשר"): תנועה קרה מהסרטונים של בן -> הדף הקצר a5s עם סליקה B2, כמו הקמפיין לנשים.
# קר = utm_campaign=lenatzeach_cold, או קמפיין שמתחיל ב-"NLP | Cold", בלי aff ובלי utm_medium=affiliate.
# משווקים, הקרוסלה החמה וכל השאר - בלי שינוי (rt_2111). שימוש: python3 go_cold_apply.py <שורש main>
import sys, os, hashlib
p = os.path.join(sys.argv[1], "nlp", "go.html"); s = open(p, encoding="utf-8").read()
h = hashlib.sha256(s.encode()).hexdigest()[:16]
if h != "06f071d19c04e673": sys.exit("STOP: go.html hash " + h + " - לא שיניתי כלום")
a = '  q.set("exp",ex); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){}\n'
assert s.count(a) == 1
new = ('  /* ב116 (החלטת בן 22.11, "מאשר"): תנועה קרה מהסרטונים של בן (utm_campaign=lenatzeach_cold, או קמפיין שמתחיל ב-"NLP | Cold"),\n'
       '     בלי aff ובלי utm_medium=affiliate -> הדף הקצר a5s עם סליקה B2, כמו הקמפיין לנשים. exp=cold_2211. השיבוץ של rt_2111 בדפדפן לא משתנה */\n'
       '  var c0=(q.get("utm_campaign")||"").toLowerCase().trim();\n'
       '  if(!q.get("aff")&&m0!=="affiliate"&&(c0==="lenatzeach_cold"||/^nlp\\s*\\|\\s*cold\\b/.test(c0))){ q.set("exp","cold_2211"); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){} location.replace("a5s.html?"+q.toString()); return; }\n')
s = s.replace(a, new + a)
open(p, "w", encoding="utf-8").write(s)
print("go.html", hashlib.sha256(s.encode()).hexdigest()[:16])
