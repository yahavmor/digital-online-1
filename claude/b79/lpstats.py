import json,base64,re,sys
from datetime import datetime,timedelta
o=json.load(open(sys.argv[1])); c=o["content"]
try: t=base64.b64decode(c).decode()
except Exception: t=c
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[]
for l in t.replace("\r","").split("\n")[1:]:
    a=l.split("\t")
    if len(a)<5: continue
    r=dict(zip(COLS,a+[""]*(21-len(a))))
    try: r["t"]=datetime.strptime(r["ts"],"%Y-%m-%d %H:%M:%S")
    except: continue
    R.append(r)
groups={"left":sys.argv[2].split(","),"started":sys.argv[3].split(",")}
for g,ps in groups.items():
    print("##",g)
    for p in ps:
        ev=sorted([r for r in R if r["sid"].startswith(p)],key=lambda r:r["t"])
        cv=next(r for r in ev if r["ev"]=="checkout_view")
        cl=[r for r in ev if r["ev"]=="cta_click" and r["t"]<=cv["t"]]
        cl=cl[-1] if cl else None
        x=dict(kv.split("=",1) for kv in (cl["x"] if cl else "").split(";") if "=" in kv)
        m=re.search(r'co=(\w)',cv['x']); co=m.group(1) if m else ''
        sl=cl['sec_on_page'] if cl else '?'; sc=cl['max_scroll_pct'] if cl else '?'; ct=cl['cta'] if cl else '?'
        print('  %s %-14s lp=%-4s co=%s sec_lp=%4s scroll=%3s%% cta=%-10s lcp=%s load=%s'%(p,cv['dev'],ev[0]['variant'],co,sl,sc,ct,x.get('lcp',''),x.get('load','')))
