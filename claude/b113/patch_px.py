# ב113 (2): px_status נשלח מיד אחרי ה-Purchase מהדפדפן, ולא רק אחרי 12 שניות (קונה שעוזב מהר לא השאיר אבחון, כמו ב-05.11).
# האבחון נשלח פעם אחת בביקור: מיד אחרי Purchase (at=pur), או אחרי 12 שניות אם לא נשלח Purchase (at=12s). שום שינוי ב-Purchase עצמו.
# שימוש: python3 patch_px.py <nlp/thanks.html> <יעד>
import sys
s = open(sys.argv[1], encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
rep('fbq("track", "Purchase", {value:297, currency:"ILS", content_name:"השיטה - הקורס המלא"}, {eventID: id}); window.__pur = 1; }catch(e){ return; }',
    'fbq("track", "Purchase", {value:297, currency:"ILS", content_name:"השיטה - הקורס המלא"}, {eventID: id}); window.__pur = 1; }catch(e){ return; }\n      try{ if(window.__pxSend) window.__pxSend("pur"); else window.__pxPending = 1; }catch(e){} /* ב113: האבחון מיד אחרי ה-Purchase */')
rep('''  setTimeout(function(){ try{ if(window.self !== window.top || TRACK_ENDPOINT[0]==="%") return;
    const st''', '''  /* ב113: אותו אבחון, פעם אחת בביקור - מיד אחרי Purchase (at=pur), אחרת אחרי 12 שניות (at=12s) */
  window.__pxSend = function(at){ try{ if(window.__pxSent || window.self !== window.top || TRACK_ENDPOINT[0]==="%") return; window.__pxSent = 1;
    const st''')
rep('''x:"px="+st+";pur="+(window.__pur?1:0), name''', '''x:"px="+st+";pur="+(window.__pur?1:0)+";at="+at, name''')
rep('''    if(!(navigator.sendBeacon&&navigator.sendBeacon(TRACK_ENDPOINT,g))) fetch(TRACK_ENDPOINT,{method:"POST",body:g,mode:"no-cors"});
  }catch(e){} }, 12000);''', '''    if(!(navigator.sendBeacon&&navigator.sendBeacon(TRACK_ENDPOINT,g))) fetch(TRACK_ENDPOINT,{method:"POST",body:g,mode:"no-cors"});
  }catch(e){} };
  if(window.__pxPending) window.__pxSend("pur");
  setTimeout(function(){ window.__pxSend("12s"); }, 12000);''')
open(sys.argv[2], "w", encoding="utf-8").write(s); print("ok")
