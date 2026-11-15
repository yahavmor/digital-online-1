# ב93: השוואת הלשונית בדשבורד (t_ws.js) מול whatsells.py. שימוש: python3 cmp_ws.py <ws_res.json> <whatsells out.md>
import json,re,sys
r=json.load(open(sys.argv[1])); md=open(sys.argv[2],encoding='utf8').read()
num=lambda x:int(re.sub(r"[^\d]","",x) or 0)
secs=md.split("\n## ")[1:]; bad=0; n=0
for per,sec in zip(("7","2010"),secs):
    py={}
    for line in sec.split("\n"):
        if not line.startswith("| ") or line.startswith("|---") or "קהל |" in line: continue
        c=[x.strip() for x in line.strip("|").split("|")]
        key=re.sub(r"<small>.*?</small>","",c[0]).replace("**","").strip()
        py.setdefault(key,c)
    for t in ("wsAd","wsCamp","wsAff"):
        for row in r[per][t][1:]:
            k=row[0]; kk=k.split(" ")[0] if t!="wsCamp" else k
            names={"רחל":"rachel","אמיר":"amir","גל":"gal","יהל":"yahel","שחר":"shahar","יוסף":"yosef"}
            kk=names.get(kk,kk)
            m=[v for key,v in py.items() if key==kk or key.split(" ")[0]==kk or (t=="wsCamp" and key==k)]
            if k.startswith("הוצאה של בן"): continue
            if k.startswith("סה\"כ") or k.startswith("שאר"): 
                m=[v for key,v in py.items() if key.startswith(k.split(" ")[0]+" "+k.split(" ")[1]) ] if not k.startswith("שאר") else [v for key,v in py.items() if key.startswith("שאר")]
            if not m: print("no py row",per,t,k[:40]); bad+=1; continue
            pc=m[0]
            if t=="wsCamp": a=[num(x) for x in row[2:7]]; b=[num(x) for x in pc[2:7]]
            else: a=[num(x) for x in row[3:8]]; b=[num(x) for x in pc[3:8]]
            sa=num(row[2].split("₪")[0]) if "₪" in row[2] else 0; sb=num(pc[2].split(" ")[0]) if pc[2] and pc[2][0].isdigit() else 0
            n+=1
            if a!=b or (t!="wsCamp" and abs(sa-sb)>1): bad+=1; print("DIFF",per,t,k[:40],a,b,sa,sb)
print("compared",n,"rows, diffs",bad); sys.exit(1 if bad else 0)
