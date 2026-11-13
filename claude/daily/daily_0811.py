import os,json,base64,urllib.parse as up,random,re,sys
from datetime import datetime
from collections import Counter,defaultdict
o=json.load(open(sys.argv[1])); c=o["content"]
try: t=base64.b64decode(c).decode()
except Exception: t=c
t=t.replace("\r","")
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[]
for l in t.split("\n")[1:]:
    a=l.split("\t")
    if len(a)<5: continue
    r=dict(zip(COLS,a+[""]*(21-len(a))))
    try: r["t"]=datetime.strptime(r["ts"],"%Y-%m-%d %H:%M:%S")
    except: continue
    R.append(r)
print("rows",len(R),"last",max(r["ts"] for r in R))
PREV=datetime.strptime(sys.argv[2],"%Y-%m-%d %H:%M")
X0=datetime(2026,11,5,6,55); SW=datetime(2026,11,8,14,19); CO54=datetime(2026,11,8,9,58)
V6=datetime(2026,11,12,11,54)  # ב85: go.html מפנה את הזרוע a5 ל-a5v6 (פריסה 11:45, ועוד עד 10 דקות מטמון)
def isTest(r):
    q=r["qs"].lower()
    return bool(re.search("claude|test|nocache",q)) or bool(re.search(r"(^|;)int=1(;|$)",r["x"] or "")) or r["variant"]=="test" or bool(re.search("בדיקה|בדיקת",r["name"] or "")) or r["sid"]=="6ac363a1-80a1-4715-9964-0a72520b66fb" or "267429750" in r["qs"]
TV={r["vid"] for r in R if r["vid"] and isTest(r)}|{"77438727"}
def src(p):
    s=(p.get("utm_source") or [""])[0].lower(); m=(p.get("utm_medium") or [""])[0].lower()
    if p.get("aff") or m=="affiliate": return "aff"
    if re.search("meta|facebook|fb|ig|instagram",s) and re.search("paid|cpc|ads?$|social_paid|paid_social",m): return "paid"
    if re.search("manychat",(p.get("utm_campaign") or [""])[0]) or m=="dm": return "manychat"
    if re.search("email|responder",s+m): return "mail"
    if re.search("instagram|ig",s): return "ig_org"
    return "other"
L=[r for r in R if r["t"]>=datetime(2026,11,4) and not r["ev"].startswith("meta_scan:")]
secn=defaultdict(dict)
for r in L:
    if r["ev"]=="section" and r["section"].isdigit(): secn[r["variant"]][int(r["section"])]=r["name"]
offk={v:min([k for k,n in d.items() if "הצעה" in n] or [99]) for v,d in secn.items()}
print("offer section idx:",{v:offk[v] for v in ("a","a5","a5v6","pr","pr2") if v in offk})
S={}
for r in L:
    if not r["sid"] or isTest(r) or r["vid"] in TV: continue
    s=S.get(r["sid"])
    if not s:
        p=up.parse_qs(r["qs"]); s=S[r["sid"]]={"v":r["variant"],"t":r["t"],"exp":(p.get("exp") or [""])[0],"vid":r["vid"],"qs":r["qs"],"src":src(p),"route":(p.get("route") or [""])[0],"uc":(p.get("utm_content") or [""])[0],"chk":0,"cta":0,"ctas":[],"maxsec":0,"pay":0,"cx":"","co":"","failed":0,"det":0}
    s["t"]=min(s["t"],r["t"]); s["vid"]=s["vid"] or r["vid"]
    x=dict(kv.split("=",1) for kv in (r["x"] or "").split(";") if "=" in kv)
    if x.get("cx") and not s["cx"]: s["cx"]=x["cx"]
    if x.get("co") and not s["co"]: s["co"]=x["co"]
    e=r["ev"]
    if e.startswith("checkout_"): s["chk"]=1
    if e in("checkout_details","checkout_contact_started"): s["det"]=1
    if e=="checkout_payment_viewed": s["pay"]=1
    if e=="checkout_failed": s["failed"]+=1
    if e=="cta_click": s["cta"]=1; s["ctas"].append(r["cta"])
    try: s["maxsec"]=max(s["maxsec"],int(r["max_section"] or 0))
    except: pass
seen=set(); B={}
for r in R:
    if r["ev"]=="purchase" and r["cta"] in("cardcom_webhook","cardcom_page_webhook","manual_bank_transfer") and r["t"]>=datetime(2026,11,4):
        if r["cta"]=="manual_bank_transfer":  # ב64: bank transfer = verified purchase, key bank_<ref>
            m=re.search(r"ref\s+([^\s|]+)",r["qs"]); d="bank_"+m.group(1) if m else r["sid"]
        else:
            m=re.search(r"deal\s+(\S+)",r["qs"]); d=m.group(1) if m else r["sid"]
        if d in seen or d=="267429750": continue
        seen.add(d); B[r["sid"]]=(r["ts"],r["variant"],d,"bank" if r["cta"]=="manual_bank_transfer" else "card")
print("verified purchases since 4.11:",[(v[0],v[1],v[3]) for v in B.values()], "sids in S:",sum(1 for k in B if k in S))
for s_id,s in S.items(): s["buy"]=1 if s_id in B else 0
EXPID="ap2_0811"
def report(lo,hi,arms,label,only_paid=True,since=None):
    E=[s for s in S.values() if s["exp"]==EXPID and s["v"] in arms and lo<=s["t"]<hi and (not only_paid or s["src"]=="paid")]
    print("==",label,"sessions",len(E))
    A={}
    for v in arms:
        ss=[s for s in E if s["v"]==v]; P=defaultdict(lambda: defaultdict(int))
        for s in ss:
            k=s["vid"] or s["v"]+s["t"].isoformat(); o=P[k]
            for f in ("cta","chk","det","pay","buy"): o[f]|=s[f]
            o["fs"]|=int(s["maxsec"]>=2); o["off"]|=int(s["maxsec"]>=offk.get(v,99) or "offer" in s["ctas"])
        n=len(P); A[v]={"visits":len(ss),"people":n,**{f:sum(o[f] for o in P.values()) for f in ("fs","off","cta","chk","det","pay","buy")}}
        A[v]["ctapos"]=dict(Counter(c for s in ss for c in s["ctas"]))
    random.seed(611); N=20000
    for key in ("chk","buy"):
        best=Counter(); worst=Counter()
        for _ in range(N):
            x={v:random.betavariate(1+A[v][key],1+max(0,A[v]["people"]-A[v][key])) for v in arms}
            best[max(x,key=x.get)]+=1; worst[min(x,key=x.get)]+=1
        for v in arms: A[v]["P_"+key]="%d%%/%d%%"%(best[v]*100/N,worst[v]*100/N)
    for v in arms: print(" ",v,A[v])
EXPID="aap_0511"
report(datetime(2026,11,5,13,56),SW,["a","a5","pr2"],"OLD aap_0511 final (05.11 13:56 - 08.11 09:58), paid only")
EXPID="ap2_0811"
report(SW,V6,["a5","pr2"],"ap2_0811 phase 1: a5 vs pr2 (08.11 14:19 - 12.11 11:54), paid only")
report(SW,V6,["a5","pr2"],"ap2_0811 phase 1 ALL sources (incl aff)",only_paid=False)
report(V6,datetime(2100,1,1),["a5v6","pr2"],"ap2_0811 phase 2: a5v6 vs pr2 (from 12.11 11:54, b85), paid only")
report(V6,datetime(2100,1,1),["a5v6","pr2"],"ap2_0811 phase 2 ALL sources (incl aff)",only_paid=False)
if PREV<V6: report(max(PREV,SW),V6,["a5","pr2"],"since last summary until the switch, paid only")
report(max(PREV,V6),datetime(2100,1,1),["a5v6","pr2"],"since last summary (phase 2), paid only")
E=[s for s in S.values() if s["exp"]=="ap2_0811" and s["t"]>=SW]
print("ap2_0811 sources since SW:",Counter(s["src"] for s in E))
print("ap2_0811 aff/non-paid sessions since SW:",Counter((s["v"],s["src"]) for s in E if s["src"]!="paid"))
print("SRM people per arm (paid) phase 1:",Counter(s["v"] for s in {(s["vid"] or s["t"].isoformat()):s for s in E if s["src"]=="paid" and s["t"]<V6}.values()))
print("SRM people per arm (paid) phase 2 (a5v6 vs pr2):",Counter(s["v"] for s in {(s["vid"] or s["t"].isoformat()):s for s in E if s["src"]=="paid" and s["t"]>=V6}.values()))
print("a5 (old page) visits with exp=ap2_0811 after the switch (should be ~0):",sum(1 for s in E if s["v"]=="a5" and s["t"]>=V6))
print("arms seen with exp=ap2_0811 since SW:",Counter(s["v"] for s in E))
old=[s for s in S.values() if s["exp"]=="aa5_0411" and s["t"]>=X0]
print("aa5_0411 since 05.11 06:55: sessions",len(old),Counter(s["v"] for s in old),"chk",sum(s["chk"] for s in old),"buy",sum(s["buy"] for s in old))
print("go=1 to out-of-exp pages since X0:",[(s["v"],s["t"].strftime("%d %H:%M")) for s in S.values() if "go=1" in s["qs"] and s["t"]>=X0 and s["v"] in("a","a1","a3","a4","b","c","pr") and s["t"]>=SW])
igo=[s for s in S.values() if s["route"]=="ig_org" and s["t"]>=X0]
print("route=ig_org since X0:",Counter((s["v"],s["exp"] or "-") for s in igo))
print("other exp keys since X0:",Counter((s["v"],s["exp"]) for s in S.values() if s["t"]>=X0 and s["exp"] and s["exp"] not in("ap2_0811",) and s["t"]>=SW))
m2=[s for s in S.values() if s["uc"]=="mail2" and s["t"]>=PREV]
print("mail2 since prev:",len(m2),Counter(s["v"] for s in m2),"chk",sum(s["chk"] for s in m2))
print("checkout_failed since prev:",[(s["v"],s["t"].strftime("%d %H:%M"),s["failed"],s["co"]) for s in S.values() if s["failed"] and s["t"]>=PREV])
for cx,co in (("co_0511","a"),("co_0511","b"),("co_b_0811","b")):
    for lab,only in (("paid",True),("all",False)):
        ss=[s for s in S.values() if s["cx"]==cx and s["co"]==co and s["chk"] and (not only or s["src"]=="paid")]
        P={}
        for s in ss:
            k=s["vid"] or s["t"].isoformat(); o=P.setdefault(k,{"det":0,"pay":0,"buy":0})
            for f in o: o[f]|=s[f]
        print("checkout",cx,co.upper(),lab,"people reached",len(P),"filled",sum(o["det"] for o in P.values()),"payment form",sum(o["pay"] for o in P.values()),"bought",sum(o["buy"] for o in P.values()))
print("chk sessions without cx since CO54:",Counter((s["v"],s["co"] or "-") for s in S.values() if s["chk"] and s["t"]>=CO54 and s["cx"]!="co_b_0811"))
print("cta/chk sessions since prev:",[(s["v"],s["t"].strftime("%d %H:%M"),s["ctas"],s["chk"],s["co"],s["src"],s["exp"]) for s in S.values() if (s["cta"] or s["chk"]) and s["t"]>=PREV])
FB=datetime(2026,10,28,13,15)
SS=defaultdict(list)
for r in R:
    if r["t"]>=PREV and r["sid"] and not isTest(r): SS[r["sid"]].append(r)
scan=[rs for rs in SS.values() if any(x["ev"].startswith("meta_scan:") for x in rs)]
print("b22 since prev: sessions",len(SS),"with meta_scan",len(scan),"by device",Counter(next((x["dev"] for x in rs if x["dev"]),"?") for rs in scan).most_common(6))
print("b22 desktop non-scan sessions since prev:",Counter((next((x["dev"] for x in rs if x["dev"]),"?"),src(up.parse_qs(rs[0]["qs"]))) for rs in SS.values() if rs not in scan and next((x["dev"] for x in rs if x["dev"]),"").startswith("d-")).most_common(6))
# ב86: קודי מודעה בלי שם במילון המודעות (לשונית Ads, עותק ב-claude/b86/ads_dict.json) - נכנסים לסיכום היומי כ"לא מזוהה"
_AD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","b86","ads_dict.json")
KNOWN={a[0].lower() for a in json.load(open(_AD,encoding="utf8"))} if os.path.exists(_AD) else set()
unk=Counter()
for s in S.values():
    if s["t"]<PREV or (s.get("vid") or "") in TV or (s.get("vid") or "").startswith(("fead4466","77438727")): continue
    c=(up.parse_qs(s["qs"]).get("utm_content",[""])[0] or "").strip().lower()
    if c and c not in KNOWN and not re.match(r"^lp_[abc]$",c): unk[c]+=1
if KNOWN: print("b86 unknown ad codes since prev (not in Ads dictionary):",unk.most_common(15) if unk else "none")
else: print("b86 unknown ad codes: SKIPPED - ads_dict.json not next to the script; check these codes against the live dictionary (dashboard API action=ads):",unk.most_common(15))
