# ב126 (ראשי 26.11; פריסה אחרי "מאשר ב126"): js_error - שומרים הודעה + קובץ + שורה:עמודה (עד 150 תווים) בשדה name,
#  ו-LP_js_error לא נשלח יותר ל-Meta (רק לגיליון, ל-Clarity ול-dataLayer). אותו שינוי בחמשת הדפים: a5s, a5v6, a5v7, a, pr2.
# שימוש: python3 patch_b126.py <in.html> <out.html>
import sys
s=open(sys.argv[1],encoding="utf8").read()
def rep(old,new):
    global s
    assert s.count(old)==1,(sys.argv[1],old[:60],s.count(old)); s=s.replace(old,new,1)
rep('addEventListener("error",e=>{ if(errs++>=3) return; send("js_error",{name:String(e.message||"error").slice(0,90)}); });',
    'addEventListener("error",e=>{ if(errs++>=3) return; let f=""; try{ f=String(e.filename||"").split("?")[0].split("/").pop(); }catch(x){} send("js_error",{name:(String(e.message||"error")+(f||e.lineno?" @"+f+":"+(e.lineno||0)+":"+(e.colno||0):"")).slice(0,150)}); }); /* ב126: הודעה + קובץ + שורה:עמודה, עד 150 תווים */')
rep('try{ if(window.fbq) fbq("trackCustom","LP_"+ev,{variant:V}); }catch(e){}',
    'try{ if(window.fbq&&ev!=="js_error") fbq("trackCustom","LP_"+ev,{variant:V}); }catch(e){} /* ב126: שגיאות JS רק לגיליון, לא ל-Meta */')
open(sys.argv[2],"w",encoding="utf8").write(s); print("ok",sys.argv[2])
