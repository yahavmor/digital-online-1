# ב93 המשך (ראשי 15.11): בלשונית 13 - שם המודעה מהמילון (עמודה "שם") ליד הקוד, כי בן רואה את הדשבורד. פריסה אחרי "מאשר".
# שימוש: python3 patch_ws_names.py <dashboard.html> <out> "<YYYY-MM-DD>" "<HH:MM>"
import sys
src, out, day, hm = sys.argv[1:5]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old)); s = s.replace(old, new, 1)
rep('''function renderWs(){''', '''function wsName(ad){const k=ad===WS_P24L?"p24":ad,d=(typeof ADS!=="undefined"&&ADS[k])||null,n=d&&d.name?d.name:"";
 return n?'<b>'+esc(n)+(ad===WS_P24L?" - קמפיין הבדיקות, מ-15.11":"")+'</b> <small class="mono" dir="ltr">'+esc(k)+'</small>':'<b>'+esc(ad)+'</b>'}
function renderWs(){''')
rep('''html:'<tr><td><b>'+esc(ad)+'</b> <small>'+esc(Object.entries(cc)''', '''html:'<tr><td>'+wsName(ad)+' <small>'+esc(Object.entries(cc)''')
rep(''''<tr><td><b>'+esc(ad)+'</b> <small>בלי כניסות</small>''', ''''<tr><td>'+wsName(ad)+' <small>בלי כניסות</small>''')
rep('''if(Object.keys(m).length){ADS=m;ADS_SRC="הלשונית Ads (חי)";if(screen==="snap")render();}''', '''if(Object.keys(m).length){ADS=m;ADS_SRC="הלשונית Ads (חי)";if(screen==="snap"||screen==="ws")render();}''')
rep('''const CHANGELOG=[
''', '''const CHANGELOG=[
["%s","%s - ב93 המשך: בלשונית 13 ליד כל מודעה השם שלה מהמילון (הלשונית Ads, עמודה \\"שם\\"), והקוד לידו בקטן. מודעה שאין לה שם במילון מוצגת בקוד."],
''' % (day, hm))
open(out, "w", encoding="utf8").write(s); print("ok")
