# ב110: משפך מ-05.11, לפי מכשיר (vid), בלי בדיקות פנימיות ובלי סריקות של Meta. שימוש: python3 -I funnel110.py ev.json
import json,re,sys
from collections import defaultdict,Counter
t=json.load(open(sys.argv[1]))['content'].replace('\r','').split('\n')
COLS=["ts","ev","variant","sid","sec_on_page","max_section","sections","max_scroll_pct","qs","at_section","section","name","video","cta","checkout_started","depth","vid","dev","nv","act","x"]
R=[dict(zip(COLS,l.split('\t')+['']*21)) for l in t[1:] if l.count('\t')>5]
TEST_DEALS=("267429750","270060105","265594626")
def isTest(r):
    q=(r['qs'] or '').lower()
    return bool(re.search('claude|test|nocache',q)) or bool(re.search(r'(^|;)int=1(;|$)',r['x'] or '')) or r['variant']=='test' or bool(re.search('בדיקה|בדיקת',r['name'] or '')) or r['sid']=='6ac363a1-80a1-4715-9964-0a72520b66fb' or any(d in (r['qs'] or '') for d in TEST_DEALS)
TV={r['vid'] for r in R if r['vid'] and isTest(r)}|{'77438727'}
FROM='2026-11-05'
L=[r for r in R if r['ts']>=FROM]
scan={r['sid'] for r in L if r['ev'].startswith('meta_scan')}
real_sid={r['sid'] for r in L if r['sid'] and not r['ev'].startswith('meta_scan')}
NON_SALES={'checkout','thanks','upsell','upsell-97','partner','dashboard','campaign','checkout97',''}
who=lambda r: r['vid'] or ('s:'+r['sid'])
S=defaultdict(set)
for r in L:
    if not r['sid'] or r['ev'].startswith('meta_scan') or isTest(r) or r['vid'] in TV: continue
    w=who(r); e=r['ev']; x=r['x'] or ''
    if e=='view' and r['variant'] not in NON_SALES: S['visit'].add(w)
    if e.startswith('checkout_'): S['checkout'].add(w)
    if e=='checkout_contact_started': S['started'].add(w)
    if e=='checkout_details': S['details'].add(w)
    if (e in('checkout_details','checkout_consent')) and re.search(r'(^|;)cons=1',x): S['consent'].add(w)
    if e=='checkout_validation_error':
        S['valerr'].add(w)
        if (r['name'] or '')=='phone': S['phone_only_err'].add(w)
        if 'phone' in (r['name'] or ''): S['phone_any_err'].add(w)
    if e=='checkout_payment_viewed': S['payform'].add(w)
# רכישות מאומתות (עסקה אחת פעם אחת)
seen=set(); buys=[]
for r in L:
    if r['ev']=='purchase' and r['cta'] in('cardcom_webhook','cardcom_page_webhook','manual_bank_transfer') and not re.search(r'(^|;)int=1(;|$)',r['x'] or ''):
        m=re.search(r'deal\s+(\S+)',r['qs']) if r['cta']!='manual_bank_transfer' else re.search(r'ref\s+([^\s|]+)',r['qs'])
        d=m.group(1) if m else r['sid']
        if d in seen or d in TEST_DEALS: continue
        seen.add(d); buys.append(r)
sid2vid={}
for r in L:
    if r['sid'] and r['vid'] and r['sid'] not in sid2vid: sid2vid[r['sid']]=r['vid']
for b in buys:
    S['bought'].add(sid2vid.get(b['sid']) or ('buy:'+b['ts']))
# עצרו בטלפון: שגיאת טלפון בלבד ובלי השארת פרטים אחר כך
S['stopped_at_phone']=S['phone_only_err']-S['details']
S['started_no_details']=S['started']-S['details']
order=['visit','checkout','started','details','consent','payform','bought']
lab={'visit':'מבקרים בדף מכירה','checkout':'הגיעו לסליקה','started':'התחילו למלא','details':'השאירו פרטים','consent':'סימנו הסכמה לדיוור','payform':'הגיעו לטופס התשלום','bought':'רכשו'}
base=len(S['visit'])
for k in order: print("%-22s %5d  %5.1f%%"%(lab[k],len(S[k]),100*len(S[k])/base if base else 0))
print('---')
print('שגיאת אימות כלשהי', len(S['valerr']), '| שגיאה בטלפון (כולל עם שדות אחרים)', len(S['phone_any_err']), '| רק טלפון', len(S['phone_only_err']))
print('עצרו בטלפון (שגיאת טלפון בלבד, ולא השאירו פרטים)', len(S['stopped_at_phone']))
print('התחילו למלא ולא השאירו פרטים', len(S['started_no_details']))
print('רכישות מאומתות מ-05.11:', len(buys), Counter(b['variant'] or '-' for b in buys))
print('meta_scan sessions dropped', len(scan-real_sid))
