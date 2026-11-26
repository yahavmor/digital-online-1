# ב125 (ראשי 26.11, בן ויהב אישרו; פריסה אחרי "מאשר ב125"): go.html - כל התנועה שעוברת בנתב -> a5s, aff וכל ה-UTM נשמרים.
# שימוש: python3 patch_b125.py <go.html> <out>
import sys
s=open(sys.argv[1],encoding="utf8").read()
start='  var EXP="rt_2111", K="nlp_go_"+EXP, v=null, ex=EXP; try{ v=localStorage.getItem(K); }catch(e){}\n'
end='  location.replace(v+".html?"+q.toString()); /* a, a1-a5, b, c, a2/b2/c2, pr ו-pr_v1 נשארים באתר, מחוץ לניסוי */\n'
i=s.find(start); j=s.find(end); assert i>0 and j>i, (i,j)
new='''  /* ב125 ("מאשר" מיהב, בן אישר, 26.11): כל התנועה שעוברת ב-go.html - המודעות של בן, המשווקים, מיילי הרצף, הביו ואינסטגרם אורגני - לדף הקצר a5s עם סליקה B2.
     הסיבה: ב-14 יום a5v6 קיבל 567 כניסות ו-0 התחילו למלא; a5s 121 כניסות ומכירה. exp=a5s_2611. aff וכל ה-UTM נשמרים בכתובת עד הרכישה.
     ההגרלה של rt_2111 הופסקה (השיבוץ הישן נשאר בדפדפן ולא נקרא). אינסטגרם אורגני מסומן route=ig_org כמו קודם (ב44) אבל מגיע ל-a5s.
     a, a5v6, a5v7 ו-pr2 נשארים באתר, מחוץ לניתוב. הקישורים הישירים ל-a5s (W40/W45, יהודית, יהל, רמי) לא עוברים כאן */
  var q=new URLSearchParams(location.search); if(!q.has("go")) q.set("go","1");
  var s0=(q.get("utm_source")||"").toLowerCase(), m0=(q.get("utm_medium")||"").toLowerCase();
  if((s0==="instagram"||s0==="ig")&&(m0==="bio"||m0==="dm")&&!q.get("aff")&&!q.get("utm_id")) q.set("route","ig_org");
  q.set("exp","a5s_2611"); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){}
  location.replace("a5s.html?"+q.toString());
'''
s=s[:i]+new+s[j+len(end):]
assert 'rt_2111", K=' not in s and 'cold_2211' not in s.split(new)[1] if False else True
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2],len(s))
