# שורת המשווקים בסיכום היומי: כניסות לפי aff, בלי סריקות Meta (ביקור שכל האירועים בו meta_scan - כמו בדשבורד, ב71)
# שימוש: python3 aff_daily.py <json מ-download_file_content> "<מ- YYYY-MM-DD HH:MM>"
import json,base64,re,sys
from collections import defaultdict
o=json.load(open(sys.argv[1]));c=o["content"]
try:t=base64.b64decode(c).decode()
except Exception:t=c
FROM=sys.argv[2]
sess=defaultdict(lambda:{"aff":None,"evs":[],"t":None,"v":set(),"cr":set()})
for l in t.replace("\r","").split("\n")[1:]:
    a=l.split("\t")
    if len(a)<9 or a[0]<FROM or not a[3]:continue
    x=a[20] if len(a)>20 else ""
    m=re.search(r"(?:^|;)aff=([a-z0-9_-]+)",x) or re.search(r"[?&]aff=([a-z0-9_-]+)",a[8])
    s=sess[a[3]];s["evs"].append(a[1]);s["t"]=min(s["t"] or a[0],a[0]);s["v"].add(a[2])
    cm=re.search(r"utm_content=([^&]*)",a[8])
    if cm:s["cr"].add(cm.group(1))
    if m:s["aff"]=m.group(1)
out=defaultdict(lambda:{"all":0,"scan":0,"real":0,"first":None,"cr":set(),"v":defaultdict(int)})
for s in sess.values():
    if not s["aff"]:continue
    o2=out[s["aff"]];o2["all"]+=1
    if all(e.startswith("meta_scan") for e in s["evs"]):o2["scan"]+=1;continue
    o2["real"]+=1;o2["first"]=min(o2["first"] or s["t"],s["t"]);o2["cr"]|=s["cr"]
    for v in s["v"]:o2["v"][v]+=1
for k,o2 in sorted(out.items(),key=lambda kv:-kv[1]["real"]):
    print(k,"real",o2["real"],"(meta_scan dropped",o2["scan"],") first real",o2["first"],"pages",dict(o2["v"]),"utm_content",sorted(o2["cr"]))
