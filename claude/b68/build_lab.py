# ב68: מעבדת דפי מכירה. בונה 3 כיוונים מ-pr2.html (אותו קופי בדיוק, בלי טקסט חדש) לתוך nlp/lab/.
# בלי פיקסל, בלי Clarity, בלי שיוך משווקים ובלי שליחה לגיליון. הכפתורים לא מובילים לתשלום. noindex.
# v1 = שחור וזהב (עיצוב בלבד), v2 = בהיר ונקי (עיצוב בלבד), v3 = כחול לילה מעודן + סדר סקשנים חדש לפי נתוני הניסוי.
# הרצה: python3 claude/b68/build_lab.py [--artifact DIR]  (עם --artifact: עותק עם נתיבי assets/ מקומיים, לתצוגה מחוץ לאתר)
import os, re, sys, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "nlp", "pr2.html")
OUT = os.path.join(ROOT, "nlp", "lab")

SCRIPTS_DROP = ["NLP_OWNER", "clarity", "fbevents", "TRACK_ENDPOINT"]   # שיוך, Clarity, פיקסל, מדידה

LAB_JS = r"""<script>
/* ב68 מעבדה: בלי מדידה. רק sticky + הודעה שהכפתור לא מוביל לתשלום */
(function(){
  var st=document.getElementById("sticky"), zones=[].slice.call(document.querySelectorAll("[data-buyzone],#offer"));
  function sticky(){ if(!st) return; var hc=document.querySelector('[data-sec="1"] .cta'), hr=hc?hc.getBoundingClientRect():null;
    var past=hr?hr.bottom<0:scrollY>innerHeight; var inZone=zones.some(function(z){var r=z.getBoundingClientRect();return r.top<innerHeight*0.8&&r.bottom>innerHeight*0.2});
    var on=past&&!inZone; st.classList.toggle("on",on); st.setAttribute("aria-hidden",String(!on)); }
  addEventListener("scroll",sticky,{passive:true}); sticky();
  var t=document.createElement("div"); t.className="labtoast"; t.setAttribute("role","status"); document.body.appendChild(t);
  document.addEventListener("click",function(e){ var a=e.target.closest("a[data-lab-cta]"); if(!a) return; e.preventDefault();
    t.textContent="מעבדה: הכפתור לא מוביל לתשלום"; t.classList.add("on"); clearTimeout(t._h); t._h=setTimeout(function(){t.classList.remove("on")},2200); });
})();
</script>"""

BASE_LAB_CSS = """
.labtag{position:fixed;top:calc(8px + env(safe-area-inset-top,0px));inset-inline-start:8px;z-index:60;font:700 11px/1 Heebo,Arial,sans-serif;letter-spacing:.06em;padding:5px 8px;border-radius:6px;background:rgba(0,0,0,.55);color:#fff;pointer-events:none}
.labtoast{position:fixed;left:50%;bottom:calc(96px + env(safe-area-inset-bottom,0px));transform:translate(-50%,20px);opacity:0;z-index:70;background:#111;color:#fff;font:600 15px/1.4 Heebo,Arial,sans-serif;padding:10px 16px;border-radius:10px;transition:opacity .2s,transform .2s;pointer-events:none}
.labtoast.on{opacity:1;transform:translate(-50%,0)}
/* אנימציות גלילה עדינות: תמונות נכנסות בהדרגה. לא מסתיר כלום בלי JS או עם הפחתת תנועה (המחלקה rvjs נוספת רק אז) */
.rvjs figure.rv:not(.in) img,.rvjs .vid.rv:not(.in) video{transform:scale(1.04)}
.rvjs figure.rv img,.rvjs .vid.rv video{transition:transform 1.1s var(--ease)}
@media (prefers-reduced-motion:reduce){.labtoast{transition:none}}
"""

THEMES = {
 "v1": {"name": "שחור וזהב", "font": "Frank+Ruhl+Libre:wght@700;900", "theme_color": "#0A0A0B", "css": """
:root{--navy:#0A0A0B;--navy1:#111113;--navy2:#19191C;--cream:#0E0E10;--paper:#141416;--gold:#CDA85F;--gold2:#E9D2A0;--gold-t:#D9B672;
 --ink:#F3EEE4;--sub:#B8B0A2;--line:rgba(205,168,95,.16);--line-d:rgba(205,168,95,.22);
 --sh:0 1px 0 rgba(255,255,255,.04) inset,0 18px 40px rgba(0,0,0,.45);--sh-up:0 1px 0 rgba(255,255,255,.06) inset,0 26px 60px rgba(0,0,0,.55)}
body{background:var(--cream);color:var(--ink)}
h1,h2,.price b{font-family:"Frank Ruhl Libre",Georgia,serif;font-weight:700;letter-spacing:0}
h1{font-weight:900}
.hero,.dark,.offer{background:radial-gradient(70% 40% at 50% 0%,rgba(205,168,95,.10) 0%,rgba(10,10,11,0) 70%),var(--navy)}
.white,section:not(.dark):not(.hero){background:var(--paper);color:var(--ink)}
section:not(.dark)+section.dark,section.dark+section:not(.dark){box-shadow:0 -1px 0 rgba(205,168,95,.28)}
mark,.dark mark{color:var(--gold2)}
.sub,.muted{color:var(--sub)}
.cta{background:linear-gradient(180deg,#EBD39E 0%,#CDA85F 55%,#B88F45 100%);color:#17120A;box-shadow:0 1px 0 rgba(255,255,255,.5) inset,0 10px 26px -10px rgba(205,168,95,.7)}
.cta:hover{filter:brightness(1.05)}
.bcard,.bs,.path,.faq details,.bonus,.slide figcaption{background:#18181B;border-color:var(--line);color:var(--ink)}
.bcard p,.bs p{color:var(--sub)}
.price s{color:#8E8778}
.chips span{border-color:rgba(205,168,95,.35);color:var(--gold2)}
.sticky{background:rgba(10,10,11,.95);border-top-color:rgba(205,168,95,.45)}
.brand{color:var(--gold2)}
"""},
 "v2": {"name": "בהיר ונקי", "font": "Rubik:wght@600;800", "theme_color": "#F4F6F5", "css": """
:root{--navy:#F4F6F5;--navy1:#FFFFFF;--navy2:#E9EEEC;--cream:#FFFFFF;--paper:#F4F6F5;--gold:#0F6B4E;--gold2:#0F6B4E;--gold-t:#0F6B4E;
 --green:#0F6B4E;--green-d:#0B523C;--ink:#14201B;--sub:#55625C;--line:rgba(20,32,27,.10);--line-d:rgba(20,32,27,.10);
 --sh:0 1px 2px rgba(20,32,27,.05),0 10px 30px rgba(20,32,27,.07);--sh-up:0 2px 4px rgba(20,32,27,.06),0 18px 44px rgba(20,32,27,.12)}
body{background:#fff;color:var(--ink)}
h1,h2{font-family:Rubik,Heebo,Arial,sans-serif;font-weight:800;letter-spacing:-.015em}
.hero,.dark,.offer{background:linear-gradient(180deg,#F4F6F5 0%,#FFFFFF 100%);color:var(--ink)}
.white{background:#fff} section:not(.dark):not(.hero):not(.white){background:var(--paper)}
section:not(.dark)+section.dark,section.dark+section:not(.dark){box-shadow:0 -1px 0 var(--line)}
.hero .sub,.dark .sub,.dark .muted,.hero .hook,.hero .intro,.dark p{color:var(--sub)}
.hero h1 .l2{color:var(--green)}
mark,.dark mark{color:var(--green)}
.dark svg [stroke="#fff"],.dark svg[stroke="#fff"]{stroke:var(--ink)}
.dark svg [fill="#fff"]{fill:var(--ink)}
.hphoto img,.story figure img{border-radius:22px}
.hphoto figcaption{color:var(--sub)}
.cta{background:var(--green);color:#fff;border-radius:999px;box-shadow:0 12px 28px -12px rgba(15,107,78,.65)}
.cta:hover{background:var(--green-d)}
.bcard,.bs,.path,.faq details,.bonus,.slide figcaption{background:#fff;border:1px solid var(--line);color:var(--ink)}
.dark .bcard,.dark .bonus,.dark .path,.dark .st>div,.dark .scene{background:#fff;color:var(--ink);border-color:var(--line)}
.price s{color:#8A948F} .price b{color:var(--ink)}
.chips span{background:#fff;border-color:var(--line);color:var(--ink)}
.brand{color:var(--green)}
.kicker,.dark .kicker,.launch{color:var(--green)}
.sticky{background:rgba(255,255,255,.96);border-top:1px solid var(--line);color:var(--ink)}
.labtag{background:rgba(20,32,27,.7)}
/* טקסט שהיה לבן על כהה: בכיוון הבהיר הכול בצבע הדיו, חוץ מהדגשות, תוויות, מספרי שלבים והכפתור */
.dark :not(mark,.l2,.kicker,.launch,.lbl,.n,.cta,.cta *,.ar,.labtag){color:var(--ink)!important}
.dark .sub,.dark .muted,.dark .hook,.dark .intro,.dark .note,.dark .meta,.dark .micro,.dark figcaption span,.dark .price s{color:var(--sub)!important}
.dark mark,.dark .l2,.dark .kicker,.dark .launch,.dark .lbl{color:var(--green)!important}
.dark .hphoto figcaption,.dark .hphoto figcaption *{color:#fff!important}
"""},
 "v3": {"name": "כחול לילה + סדר חדש", "font": None, "theme_color": "#081020", "css": """
:root{--navy:#081020;--navy1:#0D1730;--navy2:#13213F;--gold:#E2B565;--gold2:#F0D193;--r:20px}
.hero{background:radial-gradient(80% 50% at 80% 0%,rgba(226,181,101,.14) 0%,rgba(8,16,32,0) 60%),radial-gradient(90% 60% at 10% 10%,#16264a 0%,rgba(8,16,32,0) 70%),var(--navy)}
.dark,.offer{background:radial-gradient(80% 45% at 50% 0%,#14244a 0%,rgba(8,16,32,0) 72%),var(--navy)}
.dark .bcard,.dark .bonus,.offer .card,.dark .path{background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));border:1px solid rgba(255,255,255,.10);backdrop-filter:blur(6px)}
.cta{border-radius:16px;box-shadow:0 0 0 1px rgba(255,255,255,.08) inset,0 14px 34px -12px rgba(24,132,90,.75)}
.price b{text-shadow:0 0 24px rgba(226,181,101,.35)}
.hero .buy{margin-top:20px;margin-bottom:22px}
"""},
}

# v3: סדר חדש. 75% עוזבים בפתיחה, ורק 4% ב-pr2 (13% ב-a5) מגיעים להצעה בסקשן 8 - ההצעה עוברת למקום 3, אחרי עדות קצרה.
V3_ORDER = ["1", "4", "8", "2", "3", "6", "7", "5", "9", "10"]

def build(art_dir=None):
    t = open(SRC, encoding="utf8").read()
    # 1. בלי מדידה
    def drop(m):
        body = m.group(0)
        return "" if any(k in body for k in SCRIPTS_DROP) else body
    t = re.sub(r"<script[^>]*>.*?</script>", drop, t, flags=re.S)
    t = re.sub(r"<link[^>]*connect\.facebook[^>]*>", "", t)
    t = re.sub(r"<noscript>.*?</noscript>", "", t, flags=re.S)
    assert "TRACK_ENDPOINT" not in t and "fbq(" not in t and "clarity(" not in t, "tracking left in page"
    # 2. כפתורים לא מובילים לתשלום
    t = re.sub(r'href="checkout\.html[^"]*"', 'href="#" data-lab-cta', t)
    t = t.replace(" data-checkout", "")
    pages = {}
    for key, th in THEMES.items():
        p = t.replace('data-variant="pr2"', 'data-variant="lab_%s"' % key)
        p = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="%s">' % th["theme_color"], p)
        p = re.sub(r"<title>.*?</title>", "<title>מעבדה %s · %s</title>" % (key, th["name"]), p, flags=re.S)
        if th["font"]:
            p = p.replace("family=Heebo:wght@400;500;700;800&display=swap", "family=Heebo:wght@400;500;700;800&family=%s&display=swap" % th["font"])
        p = p.replace("</style>", BASE_LAB_CSS + th["css"] + "</style>", 1)
        p = p.replace("<body>", '<body>\n<div class="labtag" aria-hidden="true">מעבדה · %s</div>' % key, 1)
        p = p.replace("</body>", LAB_JS + "\n</body>", 1)
        if key == "v3":
            blocks = {}
            pat = re.compile(r'(<!--[^>]*-->\s*)?<(header|section)\b[^>]*data-sec="(\d+)".*?</\2>', re.S)
            ms = list(pat.finditer(p))
            assert [m.group(3) for m in ms] == [str(i) for i in range(1, 11)], [m.group(3) for m in ms]
            for m in ms: blocks[m.group(3)] = m.group(0)
            new = "\n\n".join(blocks[k] for k in V3_ORDER)
            p = p[:ms[0].start()] + new + p[ms[-1].end():]
            # מספור הסקשנים לפי הסדר החדש (data-sec משמש את ה-sticky בלבד, אין מדידה)
            for i, k in enumerate(V3_ORDER, 1):
                p = p.replace('data-sec="%s" data-name=' % k, 'data-sec="n%d" data-name=' % i, 1)
            p = re.sub(r'data-sec="n(\d+)"', r'data-sec="\1"', p)
            # בתוך הפתיחה: המחיר והכפתור עולים מיד אחרי תת-הכותרת, לפני התמונה (75% עוזבים בלי לגלול מעבר לפתיחה)
            mb = re.search(r'\n <div class="buy">.*?\n </div>\n', p, re.S)
            assert mb, "buy block"
            buy = mb.group(0); p = p.replace(buy, "\n", 1)
            msub = re.search(r'<p class="sub">.*?</p>\n', p, re.S)
            p = p[:msub.end()] + buy.lstrip("\n") + p[msub.end():]
        pages[key] = p
    os.makedirs(OUT, exist_ok=True)
    for key, p in pages.items():
        q = re.sub(r'(src|href|poster)="(assets/|privacy\.html|terms\.html)', r'\1="../\2', p)
        open(os.path.join(OUT, key + ".html"), "w", encoding="utf8").write(q)
    if art_dir:
        os.makedirs(art_dir, exist_ok=True)
        for key, p in pages.items():
            q = re.sub(r'href="(privacy|terms)\.html"', r'href="https://funnel.digitalonline.co.il/nlp/\1.html"', p)
            open(os.path.join(art_dir, key + ".html"), "w", encoding="utf8").write(q)
        for a in sorted(set(re.findall(r'(?:src|href|poster)="(assets/[^"]+)"', "".join(pages.values())))):
            if a.endswith(".mp4"): continue
            os.makedirs(os.path.join(art_dir, os.path.dirname(a)), exist_ok=True)
            shutil.copy(os.path.join(ROOT, "nlp", a), os.path.join(art_dir, a))
    return pages

if __name__ == "__main__":
    art = sys.argv[sys.argv.index("--artifact") + 1] if "--artifact" in sys.argv else None
    for k, p in build(art).items(): print(k, len(p))
