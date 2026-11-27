# שורת המשווקים בסיכום היומי: כניסות לפי aff, בלי סריקות Meta (ביקור שכל האירועים בו meta_scan - כמו בדשבורד, ב71)
# שימוש: python3 aff_daily.py <json מ-download_file_content> "<מ- YYYY-MM-DD HH:MM>"
# ב131: בלי ביקורי סורק הקישורים של מערכת המייל - ביקור עם variant=undefined שכולו ממכשיר m-win-web, או עד 5 שניות בלי גלילה (רץ בשעת שליחת המיילים). כל השורות של הביקור מוסרות.
def _noscan(c):
    L=c.split("\n"); H={k:i for i,k in enumerate(L[0].split("\t"))}
    iv,isd,isec,isc=H.get("variant"),H.get("sid"),H.get("sec_on_page"),H.get("max_scroll_pct")
    if iv is None or isd is None: return c
    bad=set()
    for l in L[1:]:
        r=l.split("\t")
        if len(r)<=max(iv,isd) or r[iv]!="undefined" or not r[isd]: continue
        dev=r[17] if len(r)>17 else ""
        def num(i):
            try: return float(r[i] or 0)
            except Exception: return 0.0
        if dev.startswith("m-win") or (num(isec)<=5 and num(isc)<=0): bad.add(r[isd])
    if not bad: return c
    out=[L[0]]
    for l in L[1:]:
        r=l.split("\t")
        if len(r)>isd and r[isd] in bad: continue
        out.append(l)
    return "\n".join(out)

import json,base64,re,sys
from collections import defaultdict
o=json.load(open(sys.argv[1])); c=_noscan(o["content"])
try:t=base64.b64decode(c).decode()
except Exception:t=c
FROM=sys.argv[2]
sess=defaultdict(lambda:{"aff":None,"evs":[],"t":None,"v":set(),"cr":set()})
for l in t.replace("\r","").split("\n")[1:]:
    a=l.split("\t")
    if len(a)<9 or a[0]<FROM or not a[3]:continue
    x=a[20] if len(a)>20 else ""
    m=re.search(r"(?:^|;)aff=(?:aff_?(?=[a-z0-9]))?([a-z0-9_-]+)",x) or re.search(r"[?&]aff=(?:aff_?(?=[a-z0-9]))?([a-z0-9_-]+)",a[8])  # ב121: affX / aff_X = X
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
