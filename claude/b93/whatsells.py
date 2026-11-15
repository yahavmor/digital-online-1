# ב93 (ראשי 15.11, בקשת בן): טבלה שבועית "מה מוכר" - ניתוח בלבד. על בסיס sales7d.
# שימוש: python3 whatsells.py <events json> <spend.tsv> <ads.tsv> "<now YYYY-MM-DD HH:MM>"
#  - שיוך: הכניסה הראשונה (האירוע המוקדם ביותר) של כל sid קובעת utm_campaign, utm_content ו-aff. בלי בדיקות, בלי סריקות Meta.
#  - שלבים לכל sid: הגיעו לדף התשלום (checkout_view), התחילו למלא (checkout_contact_started), השאירו פרטים = ליד (checkout_details),
#    רכישה מאומתת (purchase מ-cardcom_webhook / cardcom_page_webhook / manual_bank_transfer, פעם אחת לעסקה, בלי עסקאות בדיקה). נספר לפי אנשים (vid).
#  - קהל - מיפוי קבוע: שם הקמפיין מכיל warm → חם; cold / lab / ic → קר; אחרת לפי עמודת הקהל במילון המודעות (action=ads), "חם" או "קר"; אחרת "לא ידוע".
#  - הוצאה (מאגר 210972): מודעה של בן = מפתח "תאריך|utm_content" שאינו aff_ ואינו מכיל קוד של משווק. משווק = לכל יום: מודעות שהקוד שלו בשם (p25_yosef),
#    אחרת aff_<קוד> ו-aff_<קוד>_*. הוצאה של בן שלא מפורטת לפי מודעה = הסה"כ היומי (מפתח תאריך בלבד) פחות המודעות של בן באותו יום (לא פחות מ-0) - בשורה נפרדת.
import json,re,sys,urllib.parse as up
from datetime import datetime,timedelta
from collections import defaultdict,Counter
o=json.load(open(sys.argv[1])); t=o["content"].replace("\r","")
SPF,ADF=sys.argv[2],sys.argv[3]; NOW=datetime.strptime(sys.argv[4],"%Y-%m-%d %H:%M")
RANGES=[("7 ימים",NOW-timedelta(days=7),NOW),("מ-20.10",datetime(2026,10,20),NOW)]
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[]
for l in t.split("\n")[1:]:
    a=l.split("\t")
    if len(a)<5: continue
    r=dict(zip(COLS,a+[""]*(21-len(a))))
    try: r["t"]=datetime.strptime(r["ts"],"%Y-%m-%d %H:%M:%S")
    except: continue
    R.append(r)
TEST_DEALS=("267429750","270060105")
def isTest(r):
    q=(r["qs"] or "").lower()
    return bool(re.search("claude|test|nocache",q)) or bool(re.search(r"(^|;)int=1(;|$)",r["x"] or "")) or r["variant"]=="test" or bool(re.search("בדיקה|בדיקת",r["name"] or "")) \
        or any(d in (r["qs"] or "") for d in TEST_DEALS) or bool(re.search(r"(?:^|[?&])utm_campaign=x(?:&|$)",r["qs"] or ""))
TV={r["vid"] for r in R if r["vid"] and isTest(r) and r["ev"]!="purchase"}|{"77438727"}
scan={r["sid"] for r in R if r["ev"].startswith("meta_scan")}
def q(qs,k):
    m=re.search(r"(?:^|[?&])"+k+r"=([^&]*)",qs or ""); return up.unquote_plus(m.group(1)).strip() if m else ""
# רכישות מאומתות
seen=set(); BUY={}
for r in sorted(R,key=lambda r:r["t"]):
    if r["ev"]!="purchase" or r["cta"] not in("cardcom_webhook","cardcom_page_webhook","manual_bank_transfer"): continue
    if re.search(r"(^|;)int=1(;|$)",r["x"] or ""): continue
    if r["cta"]=="manual_bank_transfer":
        m=re.search(r"ref\s+([^\s|]+)",r["qs"]); d="bank_"+m.group(1) if m else r["sid"]
    else:
        m=re.search(r"deal\s+(\S+)",r["qs"]); d=m.group(1) if m else r["sid"]
    if d in seen or d in TEST_DEALS: continue
    seen.add(d); BUY.setdefault(r["sid"],r["t"])
# sid -> הכניסה הראשונה + שלבים
S={}
for r in sorted(R,key=lambda r:r["t"]):
    if not r["sid"] or r["sid"] in scan or r["ev"]=="purchase" or r["ev"].startswith("meta_scan"): continue
    if isTest(r) or r["vid"] in TV:
        S.setdefault(r["sid"],{"test":1}); S[r["sid"]]["test"]=1; continue
    s=S.get(r["sid"])
    if s is None:
        x=dict(kv.split("=",1) for kv in (r["x"] or "").split(";") if "=" in kv)
        aff=(x.get("aff") or q(r["qs"],"aff")).lower()
        s=S[r["sid"]]={"t":r["t"],"vid":r["vid"] or r["sid"],"camp":(q(r["qs"],"utm_campaign") or "(בלי קמפיין)").replace("|","/"),"ad":(q(r["qs"],"utm_content") or "(בלי מודעה)").lower(),
                      "aff":aff,"src":q(r["qs"],"utm_source").lower(),"med":q(r["qs"],"utm_medium").lower(),"chk":0,"start":0,"lead":0,"buy":0,"bt":None}
    if s.get("test"): continue
    e=r["ev"]
    if e.startswith("checkout_"): s["chk"]=1
    if e=="checkout_contact_started": s["start"]=1
    if e=="checkout_details": s["lead"]=1; s["start"]=1
for sid,s in S.items():
    if not s.get("test") and sid in BUY: s["buy"]=1; s["bt"]=BUY[sid]
SS={k:v for k,v in S.items() if not v.get("test")}
nobuy=[sid for sid in BUY if sid not in SS]
# מילון המודעות - קהל
ADA={}
for l in open(ADF,encoding="utf8").read().split("\n")[1:]:
    a=l.split("\t")
    if len(a)>4 and a[0].strip(): ADA[a[0].strip().lower()]=a[4].strip()
AFFS=sorted({s["aff"] for s in SS.values() if s["aff"]})
def aud(camp,ad):
    v=ADA.get(ad,"")  # מילון המודעות קודם (הקהל שבן הגדיר למודעה), ואז שם הקמפיין
    if v in("חם",): return "חם"
    if v in("קר","קר (מעבדה)"): return "קר"
    c=camp.lower()
    if "warm" in c: return "חם"
    if re.search(r"cold|lab|(^|[/ _])ic([/ _]|$)",c): return "קר"
    if "חם" in v and "קר" not in v: return "חם"
    if "קר" in v and "חם" not in v: return "קר"
    return "לא ידוע"
# הוצאה
SP=defaultdict(float)   # (day,key)->amount
for l in open(SPF,encoding="utf8").read().replace("\r","").split("\n")[1:]:
    a=l.split("\t")
    if len(a)<2 or not a[0].strip(): continue
    try: SP[(a[0].split("|")[0].strip(), (a[0].split("|",1)[1].strip().lower() if "|" in a[0] else ""))]+=float(a[1])
    except: pass
DAYS=sorted({d for d,k in SP})
def is_aff_key(k): return k.startswith("aff_") or any(f in k for f in AFFS if len(f)>2)
def ben_ad(d,ad): return SP.get((d,ad),0.0) if not is_aff_key(ad) else 0.0
def ben_total(d): return SP.get((d,""),None)
def ben_unalloc(d):
    tot=ben_total(d)
    if tot is None: return 0.0
    return max(0.0,tot-sum(v for (dd,k),v in SP.items() if dd==d and k and not is_aff_key(k)))
def aff_day(d,f):
    ad=[v for (dd,k),v in SP.items() if dd==d and k and f in k and not k.startswith("aff_")]
    if ad: return sum(ad)
    return sum(v for (dd,k),v in SP.items() if dd==d and (k=="aff_"+f or k.startswith("aff_"+f+"_")))
def days_in(a,b): return [d for d in DAYS if a.date()<=datetime.strptime(d,"%Y-%m-%d").date()<b.date()+timedelta(days=0 if b.hour==0 and b.minute==0 else 1)]
def f0(v): return "-" if v is None else ("%.0f"%v)
def per(sp,n): return "-" if (sp is None or not sp) else ("אין" if not n else "%.0f"%(sp/n))
def agg(L):
    P=defaultdict(lambda:[0,0,0,0,0])
    for s in L:
        o=P[s["vid"]]; o[0]=1; o[1]|=s["chk"]; o[2]|=s["start"]; o[3]|=s["lead"]; o[4]|=s["buy"]
    return [sum(o[i] for o in P.values()) for i in range(5)]
HEAD="| %s | קהל | הוצאה ₪ | אנשים | הגיעו לתשלום | התחילו למלא | לידים | רכישות | ₪ לליד | ₪ לרכישה |"
SEP="|---|---|---|---|---|---|---|---|---|---|"
for lab,A,B in RANGES:
    D=days_in(A,B); E=[s for s in SS.values() if A<=s["t"]<B]
    ben=[s for s in E if not s["aff"]]; affs=[s for s in E if s["aff"]]
    print("\n## %s (%s - %s, שעון ישראל)"%(lab,A.strftime("%d.%m %H:%M"),B.strftime("%d.%m %H:%M")))
    tb=agg(E); print("סה\"כ: אנשים %d, הגיעו לתשלום %d, התחילו %d, לידים %d, רכישות %d"%tuple(tb))
    # בן - לפי מודעה
    print("\n### התנועה של בן - לפי מודעה (utm_content)\n"); print(HEAD%"מודעה (קמפיינים: אנשים)"); print(SEP)
    G=defaultdict(list)
    for s in ben: G[s["ad"]].append(s)
    rows=[]; alloc=0.0
    for ad,L in G.items():
        sp=sum(ben_ad(d,ad) for d in D); nd=sum(1 for d in D if ben_ad(d,ad)>0); alloc+=sp
        n=agg(L); cc=Counter(s["camp"] for s in L)
        auds=sorted({aud(s["camp"],ad) for s in L}); au=auds[0] if len(auds)==1 else "/".join(auds)
        rows.append((n[4],n[0],"| %s <small>(%s)</small> | %s | %s | %d | %d | %d | %d | %d | %s | %s |"%(ad,", ".join("%s: %d"%(c,v) for c,v in cc.most_common(3))+(" …" if len(cc)>3 else ""),au,(f0(sp)+(" (%d ימים)"%nd if nd else "")) if sp else "-",*n,per(sp,n[3]),per(sp,n[4])),n,sp))
    # מודעות עם הוצאה בלי כניסות
    for ad in sorted({k for (d,k) in SP if k and not is_aff_key(k) and d in D}-set(G)):
        sp=sum(ben_ad(d,ad) for d in D); alloc+=sp
        if sp: rows.append((0,0,"| %s <small>(בלי כניסות)</small> | %s | %s | 0 | 0 | 0 | 0 | 0 | אין | אין |"%(ad,aud("",ad),f0(sp)),[0]*5,sp))
    big=[r for r in rows if r[1]>=10 or r[3][1]>0 or r[3][4]>0 or r[4]>=20]; small=[r for r in rows if r not in big]
    for r in sorted(big,key=lambda x:(-x[0],-x[1])): print(r[2])
    if small:
        ssp=sum(r[4] for r in small); sn=[sum(r[3][i] for r in small) for i in range(5)]
        print("| שאר המודעות <small>(%d מודעות, כל אחת פחות מ-10 אנשים ובלי סליקה)</small> | קר | %s | %d | %d | %d | %d | %d | %s | %s |"%(len(small),f0(ssp) if ssp else "-",*sn,per(ssp,sn[3]),per(ssp,sn[4])))
    tot_ben=sum((ben_total(d) or 0) for d in D)
    full=[d for d in D if ben_total(d) is not None and not any(k and not is_aff_key(k) for (dd,k) in SP if dd==d)]
    part=[d for d in D if d not in full and ben_unalloc(d)>0.5]
    if full: print("| **הוצאה של בן - רק סה\"כ יומי, בלי פירוט לפי מודעה** <small>(%d ימים: %s-%s)</small> | | %s | | | | | | | |"%(len(full),full[0][8:10]+"."+full[0][5:7],full[-1][8:10]+"."+full[-1][5:7],f0(sum(ben_unalloc(d) for d in full))))
    if part: print("| **הוצאה של בן - הפרש בין הסה\"כ היומי למודעות** <small>(%d ימים: %s)</small> | | %s | | | | | | | |"%(len(part),", ".join(d[8:10]+"."+d[5:7] for d in part),f0(sum(ben_unalloc(d) for d in part))))
    nb=agg(ben)
    print("| **סה\"כ בן** | | %s | %d | %d | %d | %d | %d | %s | %s |"%(f0(tot_ben),*nb,per(tot_ben,nb[3]),per(tot_ben,nb[4])))
    # בן - לפי קמפיין (בלי הוצאה - ההוצאה במאגר רק לפי מודעה)
    print("\n### התנועה של בן - לפי קמפיין (utm_campaign; ההוצאה במאגר לא לפי קמפיין)\n"); print("| קמפיין | קהל | אנשים | הגיעו לתשלום | התחילו למלא | לידים | רכישות |"); print("|---|---|---|---|---|---|---|")
    G=defaultdict(list)
    for s in ben: G[s["camp"]].append(s)
    for c,L in sorted(G.items(),key=lambda kv:(-agg(kv[1])[4],-agg(kv[1])[0])):
        n=agg(L); auds=sorted({aud(c,s["ad"]) for s in L})
        print("| %s | %s | %d | %d | %d | %d | %d |"%(c,auds[0] if len(auds)==1 else "/".join(auds),*n))
    # משווקים
    print("\n### משווקים (aff)\n"); print(HEAD%"משווק (קמפיינים)"); print(SEP)
    G=defaultdict(list)
    for s in affs: G[s["aff"]].append(s)
    for f in sorted(set(G)|{k[4:].split("_")[0] for (d,k) in SP if k.startswith("aff_") and d in D},key=lambda f:(-agg(G.get(f,[]))[4],-agg(G.get(f,[]))[0])):
        L=G.get(f,[]); sp=sum(aff_day(d,f) for d in D); nd=sum(1 for d in D if aff_day(d,f)>0); n=agg(L) if L else [0]*5
        cc=Counter(s["camp"] for s in L); auds=sorted({aud(s["camp"],s["ad"]) for s in L}) or ["-"]
        print("| %s <small>(%s)</small> | %s | %s | %d | %d | %d | %d | %d | %s | %s |"%(f,", ".join(c for c,v in cc.most_common(2)) or "-",auds[0] if len(auds)==1 else "/".join(auds),(f0(sp)+" (%d ימים)"%nd) if sp else "-",*n,per(sp,n[3]),per(sp,n[4])))
    na=agg(affs); spa=sum(aff_day(d,f) for d in D for f in set(G)|{k[4:].split("_")[0] for (dd,k) in SP if k.startswith("aff_") and dd in D})
    print("| **סה\"כ משווקים** | | %s | %d | %d | %d | %d | %d | %s | %s |"%(f0(spa),*na,per(spa,na[3]),per(spa,na[4])))
print("\nרכישות מאומתות שלא נמצא להן sid עם כניסה (למשל העברה בנקאית בלי ביקור): %d"%len([b for b in nobuy]))
