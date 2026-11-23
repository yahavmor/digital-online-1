import json,base64,re,sys,urllib.parse as up
from datetime import datetime
from collections import defaultdict,Counter
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
T0=datetime.strptime(sys.argv[2],"%Y-%m-%d %H:%M"); T1=datetime.strptime(sys.argv[3],"%Y-%m-%d %H:%M")
def isTest(r):
    q=r["qs"].lower()
    return bool(re.search("claude|test|nocache",q)) or bool(re.search(r"(^|;)int=1(;|$)",r["x"] or "")) or r["variant"]=="test" or bool(re.search("בדיקה|בדיקת",r["name"] or "")) or r["sid"].startswith("6ac363a1")
TV={r["vid"] for r in R if r["vid"] and isTest(r)}|{"77438727"}
ev_by=defaultdict(list)
for r in R:
    if T0<=r["t"]<=T1 and r["sid"]: ev_by[r["sid"]].append(r)
# purchases (verified) by sid
buy={}
for r in R:
    if r["ev"]=="purchase" and r["cta"] in("cardcom_webhook","cardcom_page_webhook","manual_bank_transfer") and r["t"]>=T0:
        m=re.search(r"deal\s+(\S+)",r["qs"]); d=(m.group(1) if m else "")
        if d=="267429750": continue
        buy[r["sid"]]=r["cta"]
out=[]
for sid,evs in ev_by.items():
    evs.sort(key=lambda r:r["t"])
    if all(e["ev"].startswith("meta_scan") for e in evs): continue
    if any(isTest(e) for e in evs) or any(e["vid"] in TV for e in evs if e["vid"]): continue
    co=[e for e in evs if e["ev"].startswith("checkout_")]
    if not co: continue
    dev=next((e["dev"] for e in co if e["dev"]),"")
    rows=[]
    for e in co:
        x=e["x"] or ""
        x=";".join(kv for kv in x.split(";") if kv.split("=")[0] in("len","p","via","pay_load_ms","co","cx","cons","code"))
        rc=""
        if e["ev"]=="checkout_failed":
            q=up.parse_qs(e["qs"]); rc=(q.get("ResponseCode") or [""])[0]+"/"+(q.get("Operation") or [""])[0]
        nm=e["name"] if e["ev"] in("checkout_validation_error","checkout_terms_open","checkout_email_suggest","checkout_load_error") else ""
        rows.append((e["ts"][5:16],e["ev"].replace("checkout_",""),e["sec_on_page"],nm,x,rc,e["cta"] if e["ev"]=="checkout_load_error" else ""))
    out.append((co[0]["t"],sid,dev,evs[0]["variant"],co[0]["variant"],rows,buy.get(sid,"")))
out.sort()
for t0,sid,dev,v0,v,rows,b in out:
    print(f"== {t0:%m-%d %H:%M} sid={sid[:8]} dev={dev} lp={v0} buy={b}")
    for r in rows: print("   ",*[c for c in r if c!=""])
print("sessions with checkout:",len(out))
