# ב93 (ראשי 15.11, בקשת בן): טבלה שבועית "מה מוכר" - ניתוח בלבד. על בסיס sales7d.
# שימוש: python3 whatsells.py <events json> <spend.tsv> <ads.tsv> "<now YYYY-MM-DD HH:MM>"
#  - שיוך: הכניסה הראשונה (האירוע המוקדם ביותר) של כל sid קובעת utm_campaign, utm_content ו-aff. בלי בדיקות, בלי סריקות Meta.
#  - שלבים לכל sid: הגיעו לדף התשלום (checkout_view), התחילו למלא (checkout_contact_started), השאירו פרטים = ליד (checkout_details),
#    רכישה מאומתת (purchase מ-cardcom_webhook / cardcom_page_webhook / manual_bank_transfer, פעם אחת לעסקה, בלי עסקאות בדיקה). נספר לפי אנשים (vid).
#  - קהל - מיפוי קבוע: שם הקמפיין מכיל warm → חם; cold / lab / ic → קר; אחרת לפי עמודת הקהל במילון המודעות (action=ads), "חם" או "קר"; אחרת "לא ידוע".
#  - הוצאה (מאגר 210972): מודעה של בן = מפתח "תאריך|utm_content" שאינו aff_ ואינו מכיל קוד של משווק. משווק = לכל יום: מודעות שהקוד שלו בשם (p25_yosef),
#    אחרת aff_<קוד> ו-aff_<קוד>_*. הוצאה של בן שלא מפורטת לפי מודעה = הסה"כ היומי (מפתח תאריך בלבד) פחות המודעות של בן באותו יום (לא פחות מ-0) - בשורה נפרדת.
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

import json,re,sys,urllib.parse as up
from datetime import datetime,timedelta
from collections import defaultdict,Counter
o=json.load(open(sys.argv[1])); t=_noscan(o["content"]).replace("\r","")
SPF,ADF=sys.argv[2],sys.argv[3]; NOW=datetime.strptime(sys.argv[4],"%Y-%m-%d %H:%M")
RANGES=[("7 ימים",NOW-timedelta(days=7),NOW),("מ-20.10",datetime(2026,10,20),NOW)]
if len(sys.argv)>5 and sys.argv[5]=="7": RANGES=RANGES[:1]  # הסיכום היומי: 7 ימים בלבד
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
        aff=re.sub(r"^aff_?(?=[a-z0-9])","",(x.get("aff") or q(r["qs"],"aff")).lower())  # ב121: affX / aff_X = X
        s=S[r["sid"]]={"t":r["t"],"vid":r["vid"] or r["sid"],"camp":(q(r["qs"],"utm_campaign") or "(בלי קמפיין)").replace("|","/"),"ad":(q(r["qs"],"utm_content") or "(בלי מודעה)").lower(),
                      "aff":aff,"src":q(r["qs"],"utm_source").lower(),"med":q(r["qs"],"utm_medium").lower(),"chk":0,"start":0,"lead":0,"buy":0,"bt":None}
    if s.get("test"): continue
    e=r["ev"]
    if e.startswith("checkout_"): s["chk"]=1
    if e=="checkout_contact_started": s["start"]=1
    if e=="checkout_details": s["lead"]=1; s["start"]=1
for sid,s in S.items():
    if not s.get("test") and sid in BUY: s["buy"]=1; s["bt"]=BUY[sid]
# ראשי 15.11 (ב93/ב94): מ-15.11 הקוד p24 ב-lenatzeach_cold הוא קמפיין הבדיקות של P24 (30 ₪ ליום, אופטימיזציה לרכישה), לא הפיילוט.
# הקישור נשאר lenatzeach_cold. בטבלאות: p24 מ-15.11 בשורה נפרדת, וגם ההוצאה של המפתח p24 מ-15.11.
P24T=datetime(2026,11,15); P24L="p24 (בדיקות P24, מ-15.11)"
for v in S.values():
    if not v.get("test") and v.get("ad")=="p24" and v["t"]>=P24T: v["ad"]=P24L
SS={k:v for k,v in S.items() if not v.get("test")}
nobuy=[sid for sid in BUY if sid not in SS]
# מילון המודעות - קהל
ADA={}
for l in open(ADF,encoding="utf8").read().split("\n")[1:]:
    a=l.split("\t")
    if len(a)>4 and a[0].strip(): ADA[a[0].strip().lower()]=a[4].strip()
AFFS=sorted({s["aff"] for s in SS.values() if s["aff"]})
AUD_FIX={"w1_trust_b":"חם","car4_warm_a":"חם"}  # ראשי 15.11: בקבוצה החמה
AFF_AUD={"amir":"חם"}  # ראשי 15.11: אצל אמיר שתי הקבוצות חמות
def aud(camp,ad,aff=""):
    if aff in AFF_AUD: return AFF_AUD[aff]
    if ad in AUD_FIX: return AUD_FIX[ad]
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
for (d,k) in list(SP):
    if k=="p24" and d>="2026-11-15": SP[(d,P24L)]+=SP.pop((d,k))
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
# ראשי 15.11: לטווח מ-20.10 - סכומים כוללים עד תאריך (בלי השורות היומיות של אותם ימים), ומשם השורות היומיות
OVR={"p25":(1780.0,"2026-11-14","P25 בפיילוט עד 14.11"),"p24":(838.73+27.09,"2026-11-14","P24v2 838.73 + 27.09 במעבדה"),"t9_motivation_b":(101.51,"2026-11-10","עד 10.11")}
def itemized(d):  # יום שההוצאה של בן בו מפורטת כמעט כולה לפי מודעה
    tot=ben_total(d)
    return tot is None or ben_unalloc(d)<=max(5.0,0.03*tot)
def ad_spend(ad,D,L,use_ovr):
    """(הוצאה, ימים עם שורה, מכסה את כל הטווח?)"""
    days_vis={s["t"].strftime("%Y-%m-%d") for s in L}
    sp=0.0; nd=0; full=True; cut=None
    if use_ovr and ad in OVR: sp,cut=OVR[ad][0],OVR[ad][1]
    for d in D:
        if cut and d<=cut: continue
        if (d,ad) in SP: sp+=SP[(d,ad)]; nd+=1 if SP[(d,ad)]>0 else 0; continue
        if itemized(d) or d not in days_vis: continue
        full=False
    return sp,nd,full,cut
ORG=("(בלי קמפיין)","launch_oct","manychat","guide")
def per2(sp,n,full): return per(sp,n) if full else "חלקי"
HEAD="| %s | קהל | הוצאה ₪ | אנשים | הגיעו לתשלום | התחילו למלא | לידים | רכישות | ₪ לליד | ₪ לרכישה |"
SEP="|---|---|---|---|---|---|---|---|---|---|"
for lab,A,B in RANGES:
    D=days_in(A,B); use_ovr=A<=datetime(2026,10,20,0,1); E=[s for s in SS.values() if A<=s["t"]<B]
    ben=[s for s in E if not s["aff"]]; affs=[s for s in E if s["aff"]]
    print("\n## %s (%s - %s, שעון ישראל)"%(lab,A.strftime("%d.%m %H:%M"),B.strftime("%d.%m %H:%M")))
    tb=agg(E); print("סה\"כ: אנשים %d, הגיעו לתשלום %d, התחילו %d, לידים %d, רכישות %d"%tuple(tb))
    # בן - לפי מודעה
    print("\n### התנועה של בן - לפי מודעה (utm_content)\n"); print(HEAD%"מודעה (קמפיינים: אנשים)"); print(SEP)
    G=defaultdict(list)
    for s in ben: G[s["ad"]].append(s)
    rows=[]; alloc=0.0
    for ad,L in G.items():
        sp,nd,full,cut=ad_spend(ad,D,L,use_ovr); alloc+=sp
        if all(x["camp"] in ORG for x in L) and not sp: full=True  # אורגני / מייל / ManyChat - אין הוצאה, לא "חלקי"
        n=agg(L); cc=Counter(s["camp"] for s in L)
        auds=sorted({aud(s["camp"],ad) for s in L}); au=auds[0] if len(auds)==1 else "/".join(auds)
        spt=(f0(sp)+(" <small>(סה\"כ %s%s)</small>"%(OVR[ad][2],(" + %d ימים אחריו"%nd) if nd else "") if cut else (" (%d ימים)"%nd if nd else ""))+("" if full else " <small>חלקי</small>")) if sp else ("-" if full else "- <small>חלקי</small>")
        rows.append((n[4],n[0],"| %s <small>(%s)</small> | %s | %s | %d | %d | %d | %d | %d | %s | %s |"%(ad,", ".join("%s: %d"%(c,v) for c,v in cc.most_common(3))+(" …" if len(cc)>3 else ""),au,spt,*n,per2(sp,n[3],full),per2(sp,n[4],full)),n,sp,au,full))
    # מודעות עם הוצאה בלי כניסות
    for ad in sorted({k for (d,k) in SP if k and not is_aff_key(k) and d in D}-set(G)):
        sp,nd,full,cut=ad_spend(ad,D,[],use_ovr); alloc+=sp
        if sp: rows.append((0,0,"| %s <small>(בלי כניסות)</small> | %s | %s | 0 | 0 | 0 | 0 | 0 | אין | אין |"%(ad,aud("",ad),f0(sp)),[0]*5,sp,aud("",ad),True))
    big=[r for r in rows if r[1]>=10 or r[3][1]>0 or r[3][4]>0 or r[4]>=20]; small=[r for r in rows if r not in big]
    for r in sorted(big,key=lambda x:(-x[0],-x[1])): print(r[2])
    if small:
        ssp=sum(r[4] for r in small); sn=[sum(r[3][i] for r in small) for i in range(5)]; sa=sorted({r[5] for r in small}); sf=all(r[6] for r in small)
        print("| שאר המודעות <small>(%d מודעות, כל אחת פחות מ-10 אנשים ובלי סליקה)</small> | %s | %s | %d | %d | %d | %d | %d | %s | %s |"%(len(small),"/".join(sa),(f0(ssp) if ssp else "-")+("" if sf else " <small>חלקי</small>"),*sn,per2(ssp,sn[3],sf),per2(ssp,sn[4],sf)))
    tot_ben=sum((ben_total(d) or 0) for d in D)
    nofull=[d for d in D if not itemized(d)]
    print("| **הוצאה של בן שלא משויכת למודעה** <small>(הסה\"כ פחות ההוצאה בשורות שלמעלה; ימים בלי פירוט מלא: %s)</small> | | %s | | | | | | | |"%(", ".join(d[8:10]+"."+d[5:7] for d in nofull) if len(nofull)<=8 else "%d ימים, %s-%s"%(len(nofull),nofull[0][8:10]+"."+nofull[0][5:7],nofull[-1][8:10]+"."+nofull[-1][5:7]),f0(tot_ben-alloc)))
    nb=agg(ben)
    print("| **סה\"כ בן** | | %s | %d | %d | %d | %d | %d | %s | %s |"%(f0(tot_ben),*nb,per(tot_ben,nb[3]),per(tot_ben,nb[4])))
    # בן - לפי קמפיין (בלי הוצאה - ההוצאה במאגר רק לפי מודעה)
    print("\n### התנועה של בן - לפי קמפיין (utm_campaign; ההוצאה במאגר לא לפי קמפיין)\n"); print("| קמפיין | קהל | אנשים | הגיעו לתשלום | התחילו למלא | לידים | רכישות |"); print("|---|---|---|---|---|---|---|")
    G=defaultdict(list)
    def clab(s):
        if s["camp"]=="lenatzeach_lab": return "lenatzeach_lab · "+aud(s["camp"],s["ad"])
        if s["camp"]!="lenatzeach_cold": return s["camp"]
        return "lenatzeach_cold · " + ("p25 (פיילוט)" if s["ad"]=="p25" else "p24 (בדיקות P24, מ-15.11)" if s["ad"]==P24L else "p24 (עד 14.11)" if s["ad"]=="p24" else "מודעות אחרות")
    for s in ben: G[clab(s)].append(s)
    if B>P24T: G.setdefault("lenatzeach_cold · p24 (בדיקות P24, מ-15.11)",[])  # מוצג גם כשעוד אין כניסות
    for c,L in sorted(G.items(),key=lambda kv:(-(agg(kv[1])[4] if kv[1] else 0),-(agg(kv[1])[0] if kv[1] else 0))):
        n=agg(L) if L else [0]*5; auds=sorted({aud(s["camp"],s["ad"]) for s in L}) or ["קר"]
        print("| %s | %s | %d | %d | %d | %d | %d |"%(c,auds[0] if len(auds)==1 else "/".join(auds),*n))
    # משווקים
    print("\n### משווקים (aff)\n"); print(HEAD%"משווק (קמפיינים)"); print(SEP)
    G=defaultdict(list)
    for s in affs: G[s["aff"]].append(s)
    for f in sorted(set(G)|{k[4:].split("_")[0] for (d,k) in SP if k.startswith("aff_") and d in D},key=lambda f:(-agg(G.get(f,[]))[4],-agg(G.get(f,[]))[0])):
        L=G.get(f,[]); sp=sum(aff_day(d,f) for d in D); nd=sum(1 for d in D if aff_day(d,f)>0); n=agg(L) if L else [0]*5
        cc=Counter(s["camp"] for s in L); auds=sorted({aud(s["camp"],s["ad"],s["aff"]) for s in L}) or ["-"]
        print("| %s <small>(%s)</small> | %s | %s | %d | %d | %d | %d | %d | %s | %s |"%(f,", ".join(c for c,v in cc.most_common(2)) or "-",auds[0] if len(auds)==1 else "/".join(auds),(f0(sp)+" (%d ימים)"%nd) if sp else "-",*n,per(sp,n[3]),per(sp,n[4])))
    na=agg(affs); spa=sum(aff_day(d,f) for d in D for f in set(G)|{k[4:].split("_")[0] for (dd,k) in SP if k.startswith("aff_") and dd in D})
    print("| **סה\"כ משווקים** | | %s | %d | %d | %d | %d | %d | %s | %s |"%(f0(spa),*na,per(spa,na[3]),per(spa,na[4])))
# ראשי 15.11: שורה יומית לקמפיין הבדיקות של P24 (utm_content=p24 מ-15.11): הוצאה, אנשים, לידים, רכישות
T24=[s for s in SS.values() if s["ad"]==P24L and s["t"]<NOW]
if NOW>P24T:
    print("\n### קמפיין הבדיקות של P24 (p24 מ-15.11) - לפי יום\n"); print("| יום | הוצאה ₪ | אנשים | לידים | רכישות |"); print("|---|---|---|---|---|")
    days=sorted({d for (d,k) in SP if k==P24L}|{s["t"].strftime("%Y-%m-%d") for s in T24}|{NOW.strftime("%Y-%m-%d")})
    for d in [d for d in days if d>="2026-11-15"]:
        L=[s for s in T24 if s["t"].strftime("%Y-%m-%d")==d]; n=agg(L) if L else [0]*5; sp=SP.get((d,P24L))
        print("| %s | %s | %d | %d | %d |"%(d[8:10]+"."+d[5:7],f0(sp) if sp is not None else "אין במאגר",n[0],n[3],n[4]))
    n=agg(T24) if T24 else [0]*5; sp=sum(v for (d,k),v in SP.items() if k==P24L)
    print("| **מ-15.11** | %s | %d | %d | %d |"%(f0(sp),n[0],n[3],n[4]))
print("\nרכישות מאומתות שלא נמצא להן sid עם כניסה (למשל העברה בנקאית בלי ביקור): %d"%len([b for b in nobuy]))
