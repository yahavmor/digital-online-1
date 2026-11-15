# ב92: איפה עוזבים בדף התשלום (ניתוח בלבד). אנשים אמיתיים (מזהה מבקר), בלי בדיקות וסריקות, מ-08.11.
# שימוש: python3 co_drop.py <events json> "<from YYYY-MM-DD HH:MM>" "<to>"
import json,re,sys,statistics as st
from collections import Counter,defaultdict
from datetime import datetime
t=json.load(open(sys.argv[1]))["content"].replace("\r","")
A=datetime.strptime(sys.argv[2],"%Y-%m-%d %H:%M"); B=datetime.strptime(sys.argv[3],"%Y-%m-%d %H:%M")
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[]
for l in t.split("\n")[1:]:
    a=l.split("\t")
    if len(a)<5: continue
    r=dict(zip(COLS,a+[""]*(21-len(a))))
    try: r["t"]=datetime.strptime(r["ts"],"%Y-%m-%d %H:%M:%S")
    except: continue
    R.append(r)
def isTest(r):
    q=r["qs"].lower()
    return bool(re.search("claude|test|nocache",q)) or bool(re.search(r"(^|;)int=1(;|$)",r["x"] or "")) or r["variant"]=="test" or bool(re.search("בדיקה|בדיקת",r["name"] or "")) or r["sid"]=="6ac363a1-80a1-4715-9964-0a72520b66fb" or any(d in r["qs"] for d in ("267429750","270060105")) or bool(re.search(r"(?:^|[?&])utm_campaign=x(?:&|$)",r["qs"] or ""))
TV={r["vid"] for r in R if r["vid"] and isTest(r)}|{"77438727"}
scan={r["sid"] for r in R if r["ev"].startswith("meta_scan")}
X=lambda r:dict(kv.split("=",1) for kv in (r["x"] or "").split(";") if "=" in kv)
def src(q):
    q=q.lower()
    if "aff=" in q or "utm_medium=affiliate" in q: return "aff"
    if re.search("utm_medium=(paid|cpc|paid_social)",q) or "utm_id=" in q: return "paid"
    return "other"
buys={}
for r in R:
    if r["ev"]=="purchase" and r["cta"] in("cardcom_webhook","cardcom_page_webhook","manual_bank_transfer") and not isTest(r): buys[r["sid"]]=1
CS=defaultdict(list)
for r in R:
    if not (A<=r["t"]<B) or not r["sid"] or r["sid"] in scan or isTest(r) or r["vid"] in TV: continue
    CS[r["sid"]].append(r)
P={}  # person -> aggregated
for sid,L in CS.items():
    if not any(r["ev"]=="checkout_view" for r in L): continue
    L.sort(key=lambda r:r["t"]); v0=[r for r in L if r["ev"]=="checkout_view"][0]
    k=v0["vid"] or sid
    o=P.setdefault(k,{"dev":v0["dev"],"co":X(v0).get("co",""),"cx":X(v0).get("cx",""),"src":src(v0["qs"]),"page":v0["variant"],"t":v0["t"],"sess":0,"start":0,"det":0,"pay":0,"buy":0,"fail":0,"val":0,"wallet":0,"terms":0,"leaves":[],"err":[],"payms":[]})
    o["sess"]+=1
    ch=[r for r in L if r["t"]>=v0["t"]]
    for r in ch:
        e=r["ev"]
        if e=="checkout_contact_started": o["start"]=1
        if e=="checkout_details": o["det"]=1
        if e=="checkout_payment_viewed": o["pay"]=1; o["payms"].append(int(X(r).get("pay_load_ms","0") or 0))
        if e=="checkout_failed": o["fail"]+=1
        if e=="checkout_validation_error": o["val"]+=1
        if e=="checkout_wallet_tap": o["wallet"]+=1
        if e.startswith("checkout_terms"): o["terms"]+=1
        if e=="checkout_leave": o["leaves"].append((int(r["sec_on_page"] or 0),X(r)))
        if e in("js_error","load_error"): o["err"].append((e,(r["name"] or r["section"] or "")[:70]))
    if sid in buys: o["buy"]=1
def browser(d):
    return "in-app IG" if d.endswith("-ig") else "in-app FB" if d.endswith("-fb") else ("desktop" if d.startswith("d") else "mobile web")
def os_(d): return "iOS" if "ios" in d else "Android" if "android" in d else "desktop" if d.startswith("d") else d
pp=list(P.values())
print("people reached checkout:",len(pp),"| started",sum(o["start"] for o in pp),"| details",sum(o["det"] for o in pp),"| payment form",sum(o["pay"] for o in pp),"| bought",sum(o["buy"] for o in pp))
def tab(title,key):
    print("\n--",title,"-- reached / started / payment form / bought")
    G=defaultdict(list)
    for o in pp: G[key(o)].append(o)
    for g,L in sorted(G.items(),key=lambda kv:-len(kv[1])):
        print("  %-22s %3d / %d / %d / %d"%(g,len(L),sum(o["start"] for o in L),sum(o["pay"] for o in L),sum(o["buy"] for o in L)))
tab("browser",lambda o:browser(o["dev"])); tab("OS",lambda o:os_(o["dev"])); tab("dev",lambda o:o["dev"])
tab("checkout version (co)",lambda o:o["co"]+" "+o["cx"]); tab("source",lambda o:o["src"]); tab("sales page",lambda o:o["page"])
NS=[o for o in pp if not o["start"]]
print("\n== did NOT start filling:",len(NS))
L1=[o["leaves"][-1] for o in NS if o["leaves"]]  # last leave per person
print("with leave event:",len(L1),"| without (closed tab / app killed, no beacon):",len(NS)-len(L1))
secs=[s for s,x in L1]; scr=[int(x.get("scr","0") or 0) for s,x in L1]; touch=[x.get("touch","") for s,x in L1]
if secs:
    print("seconds on page: median",st.median(secs),"| buckets",Counter("0-5" if s<=5 else "6-15" if s<=15 else "16-30" if s<=30 else "31-60" if s<=60 else "60+" for s in secs))
    print("scroll %: median",st.median(scr),"| buckets",Counter("0-25" if v<=25 else "26-50" if v<=50 else "51-75" if v<=75 else "76-100" for v in scr))
    print("touched page:",Counter(touch))
    for k in ("ttfb","dcl","load","lcp"):
        v=[int(x[k]) for s,x in L1 if x.get(k,"").isdigit()]
        if v: print(k,"ms: n",len(v),"median",st.median(v),"p75",sorted(v)[int(len(v)*.75)] if len(v)>3 else "-","max",max(v),"| >3000ms:",sum(1 for z in v if z>3000))
    print("\nper person (no PII): dev | co | src | page | sec | scr | touch | load | lcp")
    for o in sorted(NS,key=lambda o:o["t"]):
        s,x=(o["leaves"][-1] if o["leaves"] else (None,{}))
        print("  ",o["t"].strftime("%d.%m %H:%M"),o["dev"],o["co"] or "-",o["src"],o["page"],s,x.get("scr","-"),x.get("touch","-"),x.get("load","-"),x.get("lcp","-"),("ERR "+str(o["err"])) if o["err"] else "")
ST=[o for o in pp if o["start"]]
print("\n== started filling:",len(ST))
for o in ST: print("  ",o["t"].strftime("%d.%m %H:%M"),o["dev"],o["co"],o["src"],"det",o["det"],"payform",o["pay"],"pay_load_ms",o["payms"],"buy",o["buy"],"fail",o["fail"],"val",o["val"],"wallet",o["wallet"],"leave",[(s,x.get("scr"),x.get("payv")) for s,x in o["leaves"]][-1:])
print("\nerrors on checkout sessions:",Counter(e for o in pp for e,_ in o["err"]),Counter(m for o in pp for _,m in o["err"]).most_common(5))
print("checkout_failed:",sum(o["fail"] for o in pp),"validation_error:",sum(o["val"] for o in pp),"wallet taps:",sum(o["wallet"] for o in pp))
# איזה כפתור הביא לדף התשלום, וכמה זמן היו בדף המכירה לפני הלחיצה
print("\n== which button led to checkout (sales page, same sid)")
CT=Counter(); CTs=defaultdict(Counter); SEC=defaultdict(list)
for sid,L in CS.items():
    v=[r for r in L if r["ev"]=="checkout_view"]
    if not v: continue
    c=[r for r in L if r["ev"]=="cta_click" and r["t"]<=v[0]["t"]]
    k=c[-1]["cta"] if c else "(no click in sid)"
    o=P[v[0]["vid"] or sid]; CT[k]+=1; CTs[k]["started" if o["start"] else "no"]+=1
    if c: SEC[k].append(int(c[-1]["sec_on_page"] or 0))
for k,n in CT.most_common(): print("  %-18s %d  %s  sec on sales page before click: %s"%(k,n,dict(CTs[k]),sorted(SEC[k])))
