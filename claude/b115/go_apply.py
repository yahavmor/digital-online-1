# ב115 ("מאשר", ראשי 21.11): go.html - 80% ל-a5v6, 20% ל-a5v7, קבוע לדפדפן. on_1711 נסגר.
# שימוש: python3 go_apply.py <שורש main>. עוצר בלי לשנות אם ה-hash של go.html לא תואם.
import sys, os, hashlib
p = os.path.join(sys.argv[1], "nlp", "go.html"); s = open(p, encoding="utf-8").read()
h = hashlib.sha256(s.encode()).hexdigest()[:16]
if h != "287fa35658be7789": sys.exit("STOP: go.html hash " + h + " - לא שיניתי כלום")
a = s.index('  var EXP="on_1711"'); b = s.index('  var q=new URLSearchParams(location.search); if(!q.has("go")) q.set("go","1");')
new = '''  /* ב115 ("מאשר" מהראשי, 21.11): on_1711 נסגר (הנתונים שלו נשארים בגיליון עם exp=on_1711). מאז on_1711: 137 מבקרים ו-0 לחיצות קנייה;
     13.11-17.11: 687 מבקרים ו-37 הגיעו לסליקה, a5v6 30 מתוך 403. ניתוב rt_2111: 80% ל-a5v6, 20% ל-a5v7, קבוע לדפדפן.
     כל דפדפן מוגרל מחדש, גם מי ששובץ ב-on_1711, on_1611, pg_1611 או ap2_0811 (השיבוצים הישנים נשארים בדפדפן ולא נקראים).
     שני הדפים עם סליקה B2 (nlp_co_ab=b2). a, pr2 ו-a5s נשארים באתר, מחוץ לניתוב. אינסטגרם אורגני בלי שינוי (ב44) */
  var EXP="rt_2111", K="nlp_go_"+EXP, v=null, ex=EXP; try{ v=localStorage.getItem(K); }catch(e){}
  if(v!=="a5v6"&&v!=="a5v7"){
    var n=0; try{ var r=new Uint32Array(1); crypto.getRandomValues(r); n=r[0]%100; }catch(e){ n=Math.floor(Math.random()*100); }
    v=(n<80?"a5v6":"a5v7");
    try{ localStorage.setItem(K,v); }catch(e){}
  }
'''
s = s[:a] + new + s[b:]
# הסליקה B2 נשמרת רק במסלול של הניתוב, אחרי הסתעפות האינסטגרם האורגני (שנשאר בלי שינוי)
c1 = '  q.set("exp",ex);\n'
assert s.count(c1) == 1; s = s.replace(c1, '  q.set("exp",ex); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){}\n')
open(p, "w", encoding="utf-8").write(s)
print("go.html", hashlib.sha256(s.encode()).hexdigest()[:16])
