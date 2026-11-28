#!/usr/bin/env python3
# ב132 (מאשר יהב 28.11, מ-1.12): חלוקה 50/50 בין a5s (exp=a5s_v1) ל-a5s2 (exp=a5s_v2), דביקה לדפדפן (localStorage nlp_v2).
# usage: patch_router.py go <go.html> <out> | a5s <a5s.html> <out>
import sys
mode, inp, out = sys.argv[1:4]
src = open(inp, encoding="utf8").read()
def rep(old, new):
    global src
    assert src.count(old) == 1, ("anchor", old[:60], src.count(old))
    src = src.replace(old, new)
if mode == "go":
    rep('  q.set("exp","a5s_2611"); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){}\n  location.replace("a5s.html?"+q.toString());',
        '  /* ב132 ("מאשר" מיהב 28.11, מ-1.12): חלוקה 50/50 דביקה בין a5s (exp=a5s_v1) ל-a5s2 (exp=a5s_v2). v2=0/1 בכתובת כופה שיבוץ (לבדיקות) */\n'
        '  var v2=null; try{ v2=localStorage.getItem("nlp_v2"); }catch(e){} var fv=q.get("v2"); if(fv==="0"||fv==="1") v2=fv;\n'
        '  if(v2!=="0"&&v2!=="1") v2=Math.random()<0.5?"1":"0"; try{ localStorage.setItem("nlp_v2",v2); }catch(e){} q.delete("v2");\n'
        '  q.set("exp",v2==="1"?"a5s_v2":"a5s_v1"); try{ localStorage.setItem("nlp_co_ab","b2"); }catch(e){}\n'
        '  location.replace((v2==="1"?"a5s2.html?":"a5s.html?")+q.toString());')
elif mode == "a5s":
    rep('<meta charset="utf-8"><script>/* ב25:',
        '<meta charset="utf-8"><script>/* ב132 ("מאשר" מיהב 28.11, מ-1.12): גם הקישורים הישירים (W40/W45, משווקים, מיילים) נכנסים לחלוקה 50/50 מול a5s2, דביק לדפדפן (nlp_v2). רץ לפני הכול, לפני ציור הדף */\n'
        '(function(){try{var q=new URLSearchParams(location.search),fv=q.get("v2"),v=null;try{v=localStorage.getItem("nlp_v2")}catch(e){}if(fv==="0"||fv==="1")v=fv;if(v!=="0"&&v!=="1")v=Math.random()<.5?"1":"0";try{localStorage.setItem("nlp_v2",v)}catch(e){}q.delete("v2");\n'
        'var ex=q.get("exp");if(!ex||ex==="a5s_2611"||ex==="a5s_v1"||ex==="a5s_v2")q.set("exp",v==="1"?"a5s_v2":"a5s_v1");\n'
        'if(v==="1"){location.replace("a5s2.html?"+q.toString())}else if("?"+q.toString()!==location.search){history.replaceState(null,"",location.pathname+"?"+q.toString())}}catch(e){}})();</script><script>/* ב25:')
open(out, "w", encoding="utf8").write(src); print("ok", mode, len(src))
