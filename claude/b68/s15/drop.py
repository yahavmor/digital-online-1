# ב68 תוכנית ראשון: איפה עוזבים בכל דף בניסוי ap2_0811 (רק ממומן, בלי סריקות ובדיקות). שימוש: python3 drop.py events.tsv [all]
import sys,re,urllib.parse as up
from datetime import datetime
from collections import Counter,defaultdict
t=open(sys.argv[1],encoding="utf8").read().replace("\r","")
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[]
for l in t.split("\n")[1:]:
    a=l.split("\t")
    if len(a)<5: continue
    r=dict(zip(COLS,a+[""]*(21-len(a))))
    try: r["t"]=datetime.strptime(r["ts"],"%Y-%m-%d %H:%M:%S")
    except: continue
    R.append(r)
SW=datetime(2026,11,8,14,19); ALL=len(sys.argv)>2
def isTest(r):
    q=r["qs"].lower()
    return bool(re.search("claude|test|nocache",q)) or bool(re.search(r"(^|;)int=1(;|$)",r["x"] or "")) or r["variant"]=="test" or bool(re.search("בדיקה|בדיקת",r["name"] or "")) or "267429750" in r["qs"]
def paid(p):
    s=(p.get("utm_source") or [""])[0].lower(); m=(p.get("utm_medium") or [""])[0].lower()
    if p.get("aff") or m=="affiliate": return False
    return bool(re.search("meta|facebook|fb|ig|instagram",s) and re.search("paid|cpc|ads?$|social_paid|paid_social",m))
scan={r["sid"] for r in R if r["ev"].startswith("meta_scan")}
TV={r["vid"] for r in R if r["vid"] and isTest(r)}
S={}; names=defaultdict(dict)
for r in R:
    if r["t"]<SW or r["variant"] not in("a5","pr2") or not r["sid"] or r["sid"] in scan: continue
    if r["ev"]=="section" and r["section"].isdigit(): names[r["variant"]][int(r["section"])]=r["name"]
    if isTest(r) or r["vid"] in TV: continue
    s=S.get(r["sid"])
    if not s:
        p=up.parse_qs(r["qs"])
        s=S[r["sid"]]={"utm_campaign":(p.get("utm_campaign") or [""])[0],"utm_content":(p.get("utm_content") or [""])[0],"v":r["variant"],"exp":(p.get("exp") or [""])[0],"paid":paid(p),"ms":0,"sc":0,"sec":0,"cta":[],"chk":0,"dev":"","n":0,"reached":{},"tot":0}
    s["n"]+=1; s["dev"]=s["dev"] or r["dev"]
    f=lambda k: int(r[k]) if r[k].lstrip("-").isdigit() else 0
    s["ms"]=max(s["ms"],f("max_section")); s["sc"]=max(s["sc"],f("max_scroll_pct")); s["sec"]=max(s["sec"],f("sec_on_page")); s["tot"]=max(s["tot"],f("sections"))
    if r["ev"]=="section" and r["section"].isdigit(): k=int(r["section"]); s["reached"].setdefault(k,f("max_scroll_pct")); s["ms"]=max(s["ms"],k)
    if r["ev"]=="cta_click": s["cta"].append((r["cta"],r["at_section"]))
    if r["ev"].startswith("checkout_"): s["chk"]=1
    if r["ev"]=="view": s["ms"]=max(s["ms"],1)
out=[]
for v in ("a5","pr2"):
    E=[s for s in S.values() if s["v"]==v and s["exp"]=="ap2_0811" and (ALL or s["paid"])]
    n=len(E); ms=Counter(max(1,s["ms"]) for s in E); N=max(names[v]) if names[v] else 0
    clk=[s for s in E if s["cta"] or s["chk"]]
    out.append("## %s - %d ביקורים (%s), %d לחצו או הגיעו לסליקה"%(v,n,"כל המקורות" if ALL else "ממומן",len(clk)))
    out.append("סקשן | שם | הגיעו | % מהביקורים | עזבו כאן (בלי לחיצה) | % מאלה שהגיעו | גלילה חציונית בכניסה לסקשן | לחיצות שיצאו מהסקשן")
    for k in range(1,N+1):
        reach=[s for s in E if max(1,s["ms"])>=k]; left=[s for s in E if max(1,s["ms"])==k and not s["cta"] and not s["chk"]]
        sc=sorted(s["reached"][k] for s in E if k in s["reached"]); med=sc[len(sc)//2] if sc else ""
        cl=sum(1 for s in E for c in s["cta"] if c[1]==str(k))
        out.append("%d | %s | %d | %d%% | %d | %d%% | %s | %d"%(k,names[v].get(k,"?"),len(reach),100*len(reach)//max(1,n),len(left),100*len(left)//max(1,len(reach)),med,cl))
    s1=[s for s in E if max(1,s["ms"])==1 and not s["cta"]]
    sec1=sorted(s["sec"] for s in s1); 
    out.append("מסך ראשון: %d עזבו בסקשן 1 בלי לחיצה; זמן חציוני %s ש'; גלילה חציונית %s%%; טלפון %d מתוך %d"%(len(s1),sec1[len(sec1)//2] if sec1 else "-",sorted(s["sc"] for s in s1)[len(s1)//2] if s1 else "-",sum(1 for s in s1 if re.search("mob|ios|android|iphone",s["dev"].lower())),len(s1)))
    out.append("לחיצות לפי מיקום: "+str(Counter(c[0] for s in E for c in s["cta"]).most_common()))
    out.append("")
print("\n".join(out))
# פירוק המסך הראשון: כמה זמן נשארו, לפי דפדפן ולפי מודעה
for v in ("a5","pr2"):
    E=[s for s in S.values() if s["v"]==v and s["exp"]=="ap2_0811" and (ALL or s["paid"])]
    s1=[s for s in E if max(1,s["ms"])==1 and not s["cta"]]
    b=Counter("0-2" if s["sec"]<=2 else "3-5" if s["sec"]<=5 else "6-10" if s["sec"]<=10 else "11-30" if s["sec"]<=30 else "30+" for s in s1)
    print(v,"first-screen leavers by seconds:",[(k,b[k]) for k in ("0-2","3-5","6-10","11-30","30+")])
    print(v,"  stayed 11+ s and scrolled <10%:",sum(1 for s in s1 if s["sec"]>10 and s["sc"]<10))
    d=Counter(s["dev"].split("-")[-1] for s in E); d1=Counter(s["dev"].split("-")[-1] for s in s1)
    print(v,"  bounce by browser:",{k:"%d/%d"%(d1[k],d[k]) for k in d})
# לפי קמפיין ומודעה (ממומן, שני הדפים יחד): ביקורים, עזיבה במסך הראשון, יציאה מהירה (עד 2 ש'), לחיצות
print()
for key in ("utm_campaign","utm_content"):
    G=defaultdict(list)
    for s in S.values():
        if s["exp"]=="ap2_0811" and s["v"] in("a5","pr2") and (ALL or s["paid"]): G[s.get(key) or "-"].append(s)
    print(key,"| visits | first-screen bounce | <=2s | clicks")
    for k,ss in sorted(G.items(),key=lambda x:-len(x[1]))[:12]:
        print(" ",k[:40],len(ss),"%d%%"%(100*sum(1 for s in ss if max(1,s["ms"])==1 and not s["cta"])//len(ss)),"%d%%"%(100*sum(1 for s in ss if max(1,s["ms"])==1 and s["sec"]<=2)//len(ss)),sum(1 for s in ss if s["cta"] or s["chk"]))
