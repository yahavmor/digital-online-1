# ב68, תוכנית ראשון 15.11: v4 = v3 (סדר ומהירות) + הרשימה של בן:
#   כפתורים בולטים ומודרניים, מנעול ו"תשלום מאובטח" ליד המחיר וההצעה, סקשנים שנכנסים בעדינות בגלילה,
#   צללים ורקעים יוקרתיים, גלילה ומעברים חלקים. ובנוסף מקומות מוכנים לשלושה נכסים (slots.json).
# תנאים: המסך הראשון בלי אנימציה, אנימציות רק ב-CSS עם IntersectionObserver, כיבוי בהפחתת תנועה,
#   בלי קפיצות בפריסה, LCP במובייל עד 1.5 ש'. אותו קופי ואותה מדידה כמו v3 (ובלי טקסט חדש, חוץ מ"תשלום מאובטח").
# הרצה: python3 claude/b68/s15/build_v4.py <שורש ריפו של main> <תיקיית יעד> [--preview] [--noindex] [--slots=קובץ] [--suffix=s]
#   --preview: מסמן את המקומות הריקים במסגרת עם שם (רק למעבדה ולצילומי המסך). בלי הדגל, מקום בלי קובץ לא נכנס לדף.
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_v3

SRC = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; PREVIEW = "--preview" in sys.argv
NOINDEX = "--noindex" in sys.argv  # דפי בדיקה לבן לפני ראשון (מאשר ב68 - דפי בדיקה): noindex, לא מחוברים ל-go.html
build_v3.ROOT = SRC
ARG = dict(a[2:].split("=", 1) for a in sys.argv[3:] if a.startswith("--") and "=" in a)
SLOTS = json.load(open(ARG.get("slots", os.path.join(HERE, "slots.json")), encoding="utf8"))
SUFFIX = ARG.get("suffix", "")
FONT_DISPLAY = ARG.get("font", "optional")  # optional: אם הגופן לא הגיע לפני הציור הראשון, נשארים בגופן הגיבוי - בלי קפיצה  # לבדיקות: שם קובץ אחר (למשל a5v4s.html), אותו data-variant

LOCK = '<svg class="v4-li" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.4-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>'

# ---------- CSS משותף. צבעים לפי הדף: a5 כהה וזהב, pr2 ירוק על לבן וכחול לילה ----------
CSS_COMMON = """
/* ===== ב68 v4: שכבת פרימיום (CSS בלבד; המסך הראשון בלי אנימציה) ===== */
html{scroll-padding-top:12px}
[data-sec]{scroll-margin-top:12px}
.cta{position:relative;isolation:isolate;overflow:hidden;min-height:64px;border-radius:16px;letter-spacing:-.005em;
  transition:transform .25s var(--ease),box-shadow .25s var(--ease),filter .25s var(--ease),background-color .25s var(--ease)}
.cta::before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:-1;
  background:linear-gradient(180deg,rgba(255,255,255,.26),rgba(255,255,255,0) 55%)}
.cta::after{content:"";position:absolute;top:0;bottom:0;inset-inline-start:0;width:42%;border-radius:inherit;pointer-events:none;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.5),transparent);opacity:0}
.cta.v4-shine::after{animation:v4shine 1.15s var(--ease) .15s 1 backwards}
@keyframes v4shine{0%{opacity:0;transform:translateX(130%) skewX(-18deg)}20%{opacity:1}100%{opacity:0;transform:translateX(-260%) skewX(-18deg)}}
.cta > span:last-child,.cta .ar{transition:transform .25s var(--ease)}
.cta:hover > span:last-child,.cta:focus-visible > span:last-child,.cta:hover .ar,.cta:focus-visible .ar{transform:translateX(-5px)}
.cta:active{transform:translateY(1px) scale(.99)}
.v4-lock{display:inline-flex;align-items:center;gap:5px;font-weight:700;white-space:nowrap}
.v4-li{width:15px;height:15px;flex:none;fill:none;stroke:var(--v4-ok);stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round;vertical-align:-2px}
.secure .v4-li,.secure li svg{stroke:var(--v4-ok)}
.v4-sec{display:flex;justify-content:center;margin:12px auto 0;font-size:14px;line-height:1.4}
.v4-sec .v4-lock{padding:6px 13px;border-radius:999px;border:1px solid var(--v4-okb);background:var(--v4-okbg);color:var(--v4-okt)}
.sticky .cta{min-height:56px}
/* מקומות לנכסים: גודל קבוע מראש (aspect-ratio) - אין קפיצה כשהתמונה נטענת */
.v4-slot{margin:26px auto 0;max-width:300px;width:100%}
.v4-slot-h{margin:0 0 14px;text-align:center;font-weight:800;font-size:20px;line-height:1.4;text-wrap:balance}
@media (min-width:960px){.v4-slot{max-width:340px}}
.v4-slot.v4-img{max-width:440px}
.v4-slot .v4-box{position:relative;display:block;width:100%;padding:0;border:0;border-radius:20px;overflow:hidden;background:var(--v4-slotbg);
  box-shadow:var(--v4-card);cursor:pointer;-webkit-tap-highlight-color:transparent}
.v4-slot img,.v4-slot video{display:block;width:100%;height:100%;object-fit:cover}
.v4-slot .v4-pi{position:absolute;inset:0;margin:auto;width:68px;height:68px;border-radius:50%;display:grid;place-items:center;
  background:rgba(255,255,255,.92);box-shadow:0 10px 30px rgba(0,0,0,.35);transition:transform .25s var(--ease)}
.v4-slot .v4-pi svg{width:30px;height:30px;fill:#111;margin-inline-start:4px}
.v4-slot .v4-box:hover .v4-pi,.v4-slot .v4-box:focus-visible .v4-pi{transform:scale(1.06)}
.v4-slot .v4-box:focus-visible{outline:3px solid var(--v4-ok);outline-offset:3px}
/* חלק 5: מה יש בפנים - הטקסט של בן, הסיור, והכפתור "לכל 90 השיעורים" */
.v4-show{max-width:var(--text,640px);margin:8px auto 0;text-align:center;display:grid;gap:10px}
.v4-show h3{margin:0;font-size:24px;line-height:1.35;font-weight:900}
.v4-show p{margin:0;font-size:17px;line-height:1.7}
.v4-show .v4-show-sub{font-size:19px;font-weight:800;color:#FECF00}
.v4-show .v4-show-go{margin-top:6px;font-weight:800}
.v4-slot.v4-tour{max-width:420px}
.v4-tour.v4-auto .v4-pi{display:none}
.v4-all{width:100%;max-width:860px;margin:4px auto 0}
.v4-all>summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;min-height:52px;padding:12px 18px;border-radius:14px;
  border:1px solid rgba(254,207,0,.45);background:rgba(254,207,0,.06);font-weight:800;font-size:17px;color:#FFFFFF}
.v4-all>summary::-webkit-details-marker{display:none}
.v4-all>summary::after{content:"";width:9px;height:9px;border-inline-end:2px solid #FECF00;border-bottom:2px solid #FECF00;transform:rotate(45deg) translateY(-3px);transition:transform .25s}
.v4-all[open]>summary::after{transform:rotate(225deg) translateY(-3px)}
.v4-all-in{display:grid;gap:16px;margin-top:16px}
.v4-all .rv,.v4-all .v4r{opacity:1!important;transform:none!important;transition:none!important;animation:none!important}
/* חלק 6: כרטיסי הבונוסים */
.bx2-list{gap:16px}
.bx2{background:linear-gradient(180deg,#1A1A1E,#151518);border:1px solid rgba(254,207,0,.32);border-radius:18px;padding:18px 18px 16px;display:grid;gap:12px;
  box-shadow:0 24px 50px -34px rgba(0,0,0,.9),inset 0 1px 0 rgba(255,255,255,.05)}
.bx2-head{display:flex;gap:14px;align-items:center}
.bx2-head .bx-vis{flex:none;width:64px}
.bx2-head .bx-vis img,.bx2-head .bx-course{width:64px}
.bx2-head .bx-course{height:83px;font-size:11px;padding:6px}
.bx2-head .bx-course small{font-size:9px;margin-top:4px}
.bx2-t h3{margin:0;font-size:20px;line-height:1.3;font-weight:900;color:#FFFFFF}
.bx2-kind{margin:2px 0 0;font-size:14px;font-weight:700;color:#FECF00}
.bx2-ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.bx2-ul li{position:relative;padding-inline-start:24px;font-size:16px;line-height:1.55;color:#E6E6E6}
.bx2-ul li::before{content:"";position:absolute;inset-inline-start:2px;top:.55em;width:12px;height:7px;border-left:2px solid #FECF00;border-bottom:2px solid #FECF00;transform:rotate(-45deg)}
.bx2-more{margin:0;font-size:14.5px;line-height:1.55;color:#B8B8B8;font-style:italic}
.bx2-val{margin:4px 0 0;padding-top:12px;border-top:1px solid rgba(254,207,0,.18);display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px}
.bx2-val s{font-size:15px;color:#B8B8B8;text-decoration-thickness:1.5px}
.bx2-val b{font-size:17px;font-weight:900;color:#FECF00}
.bx2-total{margin:18px auto 0;text-align:center;font-size:20px;font-weight:900;color:#FFFFFF;max-width:560px}
/* חלק 7: קופסת ההצעה ("רגע הנוקאאוט") - נקי ויוקרתי, שורות עם קו זהב דק */
.v4-ko{width:100%;max-width:560px;margin:6px auto 0;padding:22px 20px 20px;border-radius:22px;border:1px solid rgba(254,207,0,.45);
  background:radial-gradient(420px circle at 50% 0,rgba(254,207,0,.10),transparent 70%),linear-gradient(180deg,#1A1A1E,#111114);
  box-shadow:0 40px 80px -40px rgba(0,0,0,.95),inset 0 1px 0 rgba(255,255,255,.06);display:grid;gap:14px;text-align:center}
.v4-ko-list{list-style:none;margin:0;padding:0}
.v4-ko-list li{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:11px 2px;border-bottom:1px solid rgba(254,207,0,.22);text-align:start}
.v4-ko-list li span{font-size:15.5px;line-height:1.45;color:#E6E6E6}
.v4-ko-list li b{flex:none;font-size:15.5px;font-weight:700;color:#FFFFFF;font-variant-numeric:tabular-nums}
.v4-ko-tot{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:4px 2px 0}
.v4-ko-tot span{font-size:17px;font-weight:800}
.v4-ko-tot b{font-size:22px;font-weight:900;color:#FFFFFF}
.v4-ko-price{padding:16px 0 4px;border-top:1px solid rgba(254,207,0,.45);display:grid;gap:4px}
.v4-ko-reg{margin:0;font-size:16px;color:#B8B8B8}
.v4-ko-reg s{text-decoration-thickness:1.5px}
.v4-ko-now{margin:0;display:flex;flex-direction:column;align-items:center;gap:4px}
.v4-ko-now span{font-size:16px;font-weight:800;color:#FECF00}
.v4-ko-now b{font-size:52px;line-height:1;font-weight:900;color:#FECF00;letter-spacing:-.5px;white-space:nowrap}
.v4-ko .cheap{margin:0;font-size:15px;line-height:1.65;color:#E6E6E6}
.v4-ko .cta{width:100%;margin:2px 0 0}
.v4-ko .cta-micro{margin:0}
/* 20: נגן "הצצה פנימה" */
.v4-peek{display:grid;gap:14px;justify-items:center;margin:8px auto 0;width:100%;max-width:620px}
.v4-peek-h{margin:0;font-size:24px;font-weight:900;text-align:center}
.v4-slot.v4-player{max-width:620px;margin:0;padding:10px;border-radius:22px;background:linear-gradient(180deg,#1A1A1E,#0E0E10);
  border:1px solid rgba(254,207,0,.32);box-shadow:0 30px 70px -36px rgba(0,0,0,.95),inset 0 1px 0 rgba(255,255,255,.06)}
.v4-player .v4-box,.v4-player video{border-radius:14px}
.v4-player video{background:#000;height:auto;object-fit:contain}
.v4-pl-top{display:flex;align-items:center;gap:8px;padding:2px 4px 10px;font-weight:800;font-size:14px;color:#FECF00}
.v4-pl-dot{width:8px;height:8px;border-radius:50%;background:#FECF00;box-shadow:0 0 0 4px rgba(254,207,0,.18)}
.v4-player .v4-pi{width:84px;height:84px;background:#FECF00;box-shadow:0 0 0 12px rgba(254,207,0,.18),0 14px 34px rgba(0,0,0,.5)}
.v4-player .v4-pi svg{width:36px;height:36px;fill:#000}
.v4-pl-bar{direction:ltr;height:4px;margin:12px 4px 0;border-radius:4px;background:rgba(255,255,255,.14);overflow:hidden}
.v4-pl-bar i{display:block;height:100%;width:0;background:#FECF00;border-radius:4px;transition:width .25s linear}
.v4-pl-meta{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;padding:10px 4px 2px;text-align:start}
.v4-pl-t{display:grid;gap:2px;min-width:0}
.v4-pl-t b{font-size:16px;font-weight:800;color:#FFFFFF;overflow-wrap:anywhere}
.v4-pl-t small{font-size:13px;color:#B8B8B8;font-weight:500}
.v4-pl-d{flex:none;font-size:13px;color:#B8B8B8;font-variant-numeric:tabular-nums}
.v4-peek-n{margin:2px 0 0;font-weight:800;font-size:18px;text-align:center}
.v4-peek .v4-ctab{width:100%}
.v4-ph{position:absolute;inset:0;display:grid;place-items:center;padding:18px;text-align:center;font:700 15px/1.5 var(--font,Heebo,sans-serif);
  color:var(--v4-okt);border:2px dashed var(--v4-okb);border-radius:20px}
/* כניסה עדינה בגלילה: רק מה שמתחת למסך הראשון, רק עם IntersectionObserver, ולא בהפחתת תנועה */
html.v4rv .v4r:not(.in){opacity:0;transform:translate3d(0,22px,0)}
html.v4rv .v4r{transition:opacity .6s var(--ease),transform .7s var(--ease)}
@media (prefers-reduced-motion:reduce){
  html.v4rv .v4r:not(.in){opacity:1;transform:none}
  html.v4rv .v4r,.cta,.cta > span:last-child,.cta .ar{transition:none}
  .cta.v4-shine::after{animation:none}
}
"""

CSS_PAGE = {
"a5": """
:root{--v4-ok:#43C08A;--v4-okb:rgba(67,192,138,.38);--v4-okbg:rgba(67,192,138,.08);--v4-okt:#CDEFDF;--v4-slotbg:#111319;
  --v4-card:0 0 0 1px rgba(211,183,122,.22),0 30px 70px -30px rgba(0,0,0,.85)}
.cta{background:linear-gradient(180deg,#F0E2BE 0%,#D9BE83 48%,#C6A266 100%);
  box-shadow:0 1px 0 rgba(255,255,255,.55) inset,0 -2px 0 rgba(120,90,40,.25) inset,0 0 0 1px rgba(234,219,181,.4),0 16px 36px -14px rgba(211,183,122,.75),0 4px 10px rgba(0,0,0,.35)}
.cta:hover{filter:brightness(1.05);box-shadow:0 1px 0 rgba(255,255,255,.55) inset,0 -2px 0 rgba(120,90,40,.25) inset,0 0 0 1px rgba(234,219,181,.55),0 22px 46px -14px rgba(211,183,122,.9),0 6px 14px rgba(0,0,0,.4)}
.pcard{border-radius:28px;border-color:rgba(211,183,122,.42);
  background:radial-gradient(120% 60% at 50% 0%,rgba(211,183,122,.12),transparent 60%),linear-gradient(180deg,rgba(211,183,122,.07),rgba(255,255,255,.015));
  box-shadow:0 0 0 1px rgba(234,219,181,.08) inset,0 1px 0 rgba(255,255,255,.08) inset,0 70px 130px -50px rgba(0,0,0,.95),0 0 80px -30px rgba(211,183,122,.25)}
section[data-sec]+section[data-sec]{box-shadow:0 1px 0 rgba(211,183,122,.07) inset}
section.alt{background-image:radial-gradient(700px circle at 88% 0%,rgba(201,169,110,.07),transparent 60%),radial-gradient(640px circle at 12% 100%,rgba(201,169,110,.05),transparent 62%)}
.sticky{-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
/* המסך הראשון מוצג מיד: בלי אנימציית הכניסה של הפתיחה (בדף החי הכותרת, הכפתור והתמונה נכנסים בהדרגה) */
.hero8 .copy>*,.hero8 .visual,.hero9 .copy>*{animation:none}
/* ===== הערות בן 11.11 (ב68): יותר יוקרה ועומק. הרקע השחור נשאר; קווי זהב דקים, הדרגות וצללים. CSS בלבד ===== */
.v4-ctab{display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:30px;text-align:center}
.v4-ctab .cta{max-width:470px}
.v4-ctab .cta-micro{margin:0;font-size:14px;color:var(--muted)}
/* כרטיסים: קו זהב דק למעלה, הדרגה עדינה וצל עמוק (שכבות רקע, בלי pseudo, כדי לא לשבור עיטורים קיימים) */
.card,.reality .r,.six>div,.wins li,.fitlist li,.bonus8,.module,.faq details,.bought li,.split>div,.ba>div,.outcomes>div,.car-slide,.toolbox,.bx{
  background:linear-gradient(90deg,transparent 8%,rgba(234,219,181,.55) 50%,transparent 92%) top center/100% 1px no-repeat,
             linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,0) 55%),var(--card,#111319);
  border-color:rgba(211,183,122,.24);
  box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 28px 56px -30px rgba(0,0,0,.95),0 0 0 1px rgba(0,0,0,.25)}
.toolbox{background:linear-gradient(90deg,transparent 8%,rgba(234,219,181,.55) 50%,transparent 92%) top center/100% 1px no-repeat,linear-gradient(180deg,rgba(211,183,122,.10),rgba(211,183,122,.03))}
.ctab .box{border-color:rgba(211,183,122,.45);box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 40px 90px -40px rgba(0,0,0,.95),0 0 60px -28px rgba(211,183,122,.30)}
.pcard{box-shadow:0 0 0 1px rgba(234,219,181,.10) inset,0 1px 0 rgba(255,255,255,.10) inset,0 80px 140px -50px rgba(0,0,0,.95),0 0 110px -30px rgba(211,183,122,.32)}
/* כפתור הקנייה: ברק עדין שעובר כל כמה שניות כשהכפתור במסך (transform/opacity בלבד; כבוי בהפחתת תנועה) */
.cta.v4-shine::after{animation:v4shine2 5.5s var(--ease) .2s infinite backwards}
@keyframes v4shine2{0%{opacity:0;transform:translateX(130%) skewX(-18deg)}4%{opacity:1}20%{opacity:0;transform:translateX(-260%) skewX(-18deg)}100%{opacity:0;transform:translateX(-260%) skewX(-18deg)}}
@media (prefers-reduced-motion:reduce){.cta.v4-shine::after{animation:none}}
/* ===== הערות בן 11.11 חלק 2 ===== */
/* 14: ניגודיות AA - המחיר המחוק בכפתור ועל רקע כהה, והתוויות הקטנות על ערכות העבודה הלבנות */
.cta .was{opacity:.72}
.was{opacity:.78}
.bx-course.bx-kit small{color:#6B5500}
.faq .was{opacity:1}
/* 13: "תשלום מאובטח" עם מנעול בתוך הכפתור - שורה שנייה קטנה באמצע למטה */
.cta{flex-wrap:wrap;row-gap:2px}
.cta .v4-pay{flex-basis:100%;order:9;display:flex;align-items:center;justify-content:center;gap:5px;font-size:12.5px;font-weight:700;line-height:1.1;color:rgba(0,0,0,.78)}
.cta .v4-pay .v4-li{stroke:currentColor;width:13px;height:13px}
/* חלק 4: בלוק האחריות בקטן בקופסת הכפתור */
.v4-guar{display:flex;gap:12px;align-items:flex-start;margin:14px auto 0;max-width:520px;padding:14px 16px;border-radius:14px;
  border:1px solid rgba(254,207,0,.32);background:linear-gradient(180deg,rgba(254,207,0,.07),rgba(254,207,0,.02));text-align:start}
.v4-guar .v4-shield{flex:none;width:26px;height:26px;margin-top:2px;fill:none;stroke:#FECF00;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.v4-guar p{margin:0 0 6px;font-size:14px;line-height:1.55;color:#E6E6E6}
.v4-guar p:last-child{margin:0}
.v4-guar p b{color:#FFFFFF}
.v4-guar .v4-guar-h{font-size:15.5px}
.v4-guar .v4-guar-h b{color:#FECF00}
.sticky .cta .st-txt{flex:0 1 auto;max-width:calc(100% - 34px)}
.sticky .cta .v4-pay{font-size:11.5px}
.cta .ct-t{flex:0 1 auto;max-width:calc(100% - 34px)}
.cta:hover > span:nth-last-child(2),.cta:focus-visible > span:nth-last-child(2){transform:translateX(-5px)}
.cta:hover > .v4-pay,.cta:focus-visible > .v4-pay{transform:none}
/* 10: "רגע לפני" - שורה קטנה, שתי פסקאות וכותרת */
.pause .q small{margin-bottom:0}
.pause .a{margin-block:0}
/* 11: "מה אם..." */
.v4-belief .wrap{max-width:760px}
.v4-belief p{max-width:var(--text);color:var(--ink2);font-size:18px;line-height:1.75}
.v4-belief .lead{color:var(--muted)}
.v4-quotes{list-style:none;margin:4px 0;padding:0;display:grid;gap:10px}
.v4-quotes li{font-size:clamp(20px,5.6vw,26px);font-weight:800;color:var(--ink);padding:12px 18px;border-inline-start:3px solid var(--gold);background:rgba(211,183,122,.06);border-radius:0 12px 12px 0}
.v4-ask{font-weight:800;color:var(--gold2)!important;font-size:20px!important}
.v4-big{font-weight:800;color:var(--ink)!important;font-size:clamp(20px,5.4vw,26px)!important;line-height:1.45!important}
/* 12: "לא עוד קורס" - תת-כותרת */
.notcourse .v4-nc-sub{font-weight:800;color:var(--gold2);font-size:18px}
#offer .secure{margin-top:14px}
""",
"pr2": """
:root{--v4-ok:#1F9A68;--v4-okb:rgba(24,132,90,.30);--v4-okbg:rgba(24,132,90,.07);--v4-okt:#17694A;--v4-slotbg:#EEF0EC;
  --v4-card:0 1px 2px rgba(16,24,39,.06),0 12px 28px rgba(16,24,39,.10),0 34px 70px -20px rgba(16,24,39,.22)}
.dark{--v4-ok:#43C08A;--v4-okb:rgba(67,192,138,.38);--v4-okbg:rgba(67,192,138,.08);--v4-okt:#CDEFDF;--v4-slotbg:#172235}
.cta{background:linear-gradient(180deg,#22A570 0%,#18845A 55%,#136B49 100%);
  box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.14) inset,0 14px 30px -12px rgba(24,132,90,.65),0 3px 8px rgba(16,24,39,.16)}
.cta:hover{background:linear-gradient(180deg,#25B07A 0%,#1A8E61 55%,#147350 100%);box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.14) inset,0 20px 40px -12px rgba(24,132,90,.75),0 5px 12px rgba(16,24,39,.2)}
.dark .cta{box-shadow:0 1px 0 rgba(255,255,255,.28) inset,0 -2px 0 rgba(0,0,0,.18) inset,0 0 0 1px rgba(67,192,138,.35),0 18px 40px -12px rgba(31,154,104,.6)}
.offer .pricebox{border-top-color:rgba(216,166,78,.28)}
.white{background:radial-gradient(900px 420px at 100% 0%,rgba(216,166,78,.06),transparent 60%),var(--paper)}
main > section:not(.white):not(.dark){background-image:radial-gradient(800px 380px at 0% 0%,rgba(16,24,39,.035),transparent 60%)}
""",
}

# ---------- JS: כניסה עדינה לסקשנים שאין בהם עדיין אנימציה, ברק אחד על כפתור כשהוא נכנס למסך, וטעינת משקלי הגופן מראש ----------
JS = """<script>/* ב68 v4: (1) כניסה עדינה בגלילה למה שמתחת למסך הראשון ועוד לא מונפש בדף - רק IntersectionObserver ו-CSS, לא בהפחתת תנועה.
   מה שכבר במסך בטעינה לא מוסתר בכלל. (2) ברק אחד על כפתור כשהוא נכנס במלואו למסך (CSS). (3) המקומות לסרטונים: הסרטון נטען רק בלחיצה. */
(function(){var RM=matchMedia("(prefers-reduced-motion: reduce)").matches,IO="IntersectionObserver" in window,root=document.documentElement;
 if(IO&&!RM){var vh=innerHeight,els=[];
  document.querySelectorAll("[data-sec]").forEach(function(s){if(s.dataset.sec==="1")return;
   [].forEach.call(s.querySelectorAll(":scope > .wrap > *, :scope > div > .wrap > *, :scope > .wrap > .stack > *"),function(e){
    if(e.closest(".rv,.v4r")||e.querySelector(".rv,.in")||/^(SCRIPT|STYLE)$/.test(e.tagName)||e.classList.contains("rv"))return;
    if(e.getBoundingClientRect().top<vh*0.98)return; e.classList.add("v4r");els.push(e);});});
  root.classList.add("v4rv");
  var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting||x.boundingClientRect.top<0){x.target.classList.add("in");io.unobserve(x.target);}});},{rootMargin:"0px 0px -6% 0px"});
  els.forEach(function(e){io.observe(e);});
  /* גלילה מהירה או קפיצה לעוגן (#offer): מה שכבר מעל תחתית המסך נחשף, כדי ששום דבר לא יישאר מוסתר */
  /* חל גם על אנימציות הכניסה שכבר קיימות בדף (.rv, נחשפות עם אותו קלאס in) */
  var pend=false;addEventListener("scroll",function(){if(pend)return;pend=true;requestAnimationFrame(function(){pend=false;var h=innerHeight;
   [].forEach.call(document.querySelectorAll(".v4r:not(.in),.rv:not(.in)"),function(e){if(e.getBoundingClientRect().top<h){e.classList.add("in");io.unobserve(e);}});});},{passive:true});
  var io2=new IntersectionObserver(function(es){es.forEach(function(x){if(x.intersectionRatio>=.95){x.target.classList.add("v4-shine");io2.unobserve(x.target);}});},{threshold:[.95]});
  document.querySelectorAll("a.cta").forEach(function(b){if(b.dataset.cta!=="sticky")io2.observe(b);});}
 /* תמונות שמחכות לתמונה הראשית (data-v4src על img) */
 (function(){var done=false;function rel(){if(done)return;done=true;[].forEach.call(document.querySelectorAll("img[data-v4src]"),function(i){i.src=i.dataset.v4src;i.removeAttribute("data-v4src");});}
  var h=document.querySelector('[data-sec="1"] img[fetchpriority="high"]');
  if(!h||h.complete)rel();else{h.addEventListener("load",rel);h.addEventListener("error",rel);}
  addEventListener("scroll",rel,{once:true,passive:true});addEventListener("touchstart",rel,{once:true,passive:true});setTimeout(rel,4000);})();
 document.querySelectorAll(".v4-slot [data-v4src]").forEach(function(b){b.addEventListener("click",function(){
  var v=document.createElement("video");v.src=b.dataset.v4src;v.controls=true;v.playsInline=true;v.setAttribute("playsinline","");v.poster=b.dataset.v4poster||"";
  var f=b.closest(".v4-slot"),k=f.dataset.slot,bar=f.querySelector(".v4-pl-bar i");v.style.aspectRatio=b.style.aspectRatio;
  if(bar)v.addEventListener("timeupdate",function(){if(v.duration)bar.style.width=(100*v.currentTime/v.duration).toFixed(1)+"%";});
  b.replaceWith(v);v.play().catch(function(){});
  try{window.__lpSend&&window.__lpSend("video_play",{video:"slot_"+k});}catch(e){}});});
 document.querySelectorAll("[data-v4tour]").forEach(function(b){var f=b.closest(".v4-slot"),k=f.dataset.slot;
  function mk(auto){var v=document.createElement("video");v.src=b.dataset.v4tour;v.poster=b.dataset.v4poster||"";v.playsInline=true;v.setAttribute("playsinline","");v.style.aspectRatio=b.style.aspectRatio;
   if(auto){v.muted=true;v.setAttribute("muted","");v.loop=true;v.preload="auto";}else{v.controls=true;}b.replaceWith(v);return v;}
  b.addEventListener("click",function(){var v=mk(false);v.play().catch(function(){});try{window.__lpSend&&window.__lpSend("video_play",{video:"slot_"+k});}catch(e){}});
  if(RM||!IO)return; f.classList.add("v4-auto");
  var v=null,near=new IntersectionObserver(function(es){if(es[0].isIntersecting&&!v){v=mk(true);near.disconnect();vis.observe(f);}},{rootMargin:"300px 0px"});
  var vis=new IntersectionObserver(function(es){if(!v)return;if(es[0].intersectionRatio>=.5)v.play().catch(function(){});else v.pause();},{threshold:[0,.5]});
  near.observe(f);});
})();</script>
"""


# ---------- הגופן: Heebo מהאתר עצמו (עברית ולטינית, גופן משתנה), עם preload, במקום ה-CSS של Google שחוסם את הציור ----------
# בלי זה הכותרת הראשית קופצת פעמיים כשהגופן מגיע (פעם לעברית ופעם לפיסוק), ובדף החי זה מוסתר רק בזכות אנימציית הכניסה של הפתיחה
# שני קבצים מ-Heebo המלא (גופן משתנה, מצומצם למשקלים 400-900 שבשימוש), לפי טווח ולא לפי התווים שבדף היום,
# כדי ששינויי קופי לא יציגו תו בגופן אחר: "he" = כל האותיות העבריות, ספרות, פיסוק ו-₪ (10KB, עם preload);
# "la" = אותיות לטיניות (NLP, WhatsApp...; 12KB, בלי preload). ראו fonts/README.md
FONT_RANGES = {"he": "U+0020-0040, U+005B-0060, U+007B-007E, U+00A0, U+00A9, U+00AB, U+00B0, U+00B7, U+00BB, U+00D7, U+05B0-05C7, U+05D0-05EA, U+05F0-05F4, U+200C-200F, U+2010-2014, U+2018-201E, U+2022, U+2026, U+2030, U+2039-203A, U+20AA",
               "la": "U+0041-005A, U+0061-007A, U+00C0-00D6, U+00D8-00F6, U+00F8-017F"}
FONT_PRELOAD = ("he",)
def self_font(p):
    n0 = len(p)
    p = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"(?: crossorigin)?>', "", p)
    m = re.search(r'\s*<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=Heebo[^"]*">', p); assert m, "heebo link"
    # preload רק לעברית (10KB), כדי שעם font-display optional היא תגיע לפני הציור הראשון אצל רוב הגולשים
    pre = "".join('\n<link rel="preload" as="font" type="font/woff2" href="assets/fonts/heebo-%s.woff2" crossorigin>' % k for k in FONT_PRELOAD)
    ff = "".join('@font-face{font-family:"Heebo";font-style:normal;font-weight:400 900;font-display:%s;src:url(assets/fonts/heebo-%s.woff2) format("woff2");unicode-range:%s}' % (FONT_DISPLAY, k, r) for k, r in FONT_RANGES.items())
    p = p[:m.start()] + pre + "\n<style>" + ff + "</style>" + p[m.end():]
    assert "fonts.googleapis" not in p and len(p) != n0
    return p

# ---------- תמונות מתחת לפתיחה מחכות לתמונה הראשית ----------
# ב-v3 צילומי הוואטסאפ עלו לסקשן 2, צמוד לפתיחה, והדפדפן מוריד אותם מיד (גם עם loading=lazy) במקביל לתמונה הראשית.
# ב-3G זה דוחה את התמונה הראשית (LCP) בשנייה. לכן תמונה עצלה עם רוחב וגובה אחרי סקשן 1 מקבלת data-v4src במקום src,
# ונטענת אחרי שהתמונה הראשית נטענה, בגלילה הראשונה, או אחרי 4 שניות. הגודל קבוע מראש (width/height) - אין קפיצה.
def defer_imgs(p):
    m = re.search(r'<(header|section)\b[^>]*data-sec="1"', p); assert m
    end = p.index("</%s>" % m.group(1), m.end())
    head, tail = p[:end], p[end:]
    n = [0]
    def f(mm):
        t = mm.group(0)
        if 'loading="lazy"' not in t or ' width="' not in t or ' height="' not in t or ' src="' not in t: return t
        n[0] += 1; return t.replace(' src="', ' data-v4src="', 1)
    tail = re.sub(r"<img\b[^>]*>", f, tail)
    return head + tail, n[0]

# ---------- הערות בן 11.11 (ב68, מאושר ע"י הראשי): טקסט מילה במילה ושני כפתורים חדשים, רק ב-a5v4 ----------
# הטקסטים לא מופיעים ב-pr2, ולכן pr2v4 לא משתנה. הנוסחים ב-ben_1111.json (גם t_v4.js קורא אותם)
BEN = json.load(open(os.path.join(HERE, "ben_1111.json"), encoding="utf8"))
def ben_a5(p):
    for pair in BEN["a5"]:
        old, new = pair[0], pair[1]; allm = len(pair) > 2 and pair[2] == "all"
        n = p.count(old); assert (n >= 1 if allm else n == 1), ("ben_1111", old[:60], n)
        p = p.replace(old, new)
    for rx, _item in BEN["a5_regex_remove"]:
        p, n = re.subn(rx, "", p, count=1, flags=re.S); assert n == 1, rx
    for b in BEN["a5_buttons"]:
        btn = ('\n<div class="v4-ctab"><a class="cta" data-cta="%s" data-checkout href="#"><span class="ct-t">%s</span> <span>←</span></a>'
               '<p class="cta-micro">%s</p></div>') % (b["cta"], b["text"], b["micro"])
        a, z = sec_bounds(p, b["section"])
        if b.get("after"):
            i = p.index(b["after"], a); assert i < z; at = i + len(b["after"])
        else:  # אחרי המפתח האחרון: אחרי רשימת המפתחות, לפני סגירת ה-wrap של הסקשן
            at = p.rindex("</div>", a, z)
        p = p[:at] + btn + p[at:]
    # 11: סקשן חדש מיד אחרי "רגע לפני"
    for ins in BEN["a5_insert_after"]:
        a, z = sec_bounds(p, ins["after_section"]); at = z + len("</section>")
        p = p[:at] + "\n\n" + ins["html"] + p[at:]
    # 13: "תשלום מאובטח" עם מנעול בתוך כל כפתור קנייה (שורה שנייה קטנה, באמצע למטה), חוץ מהדביק
    def inbtn(m):
        if 'data-cta="sticky"' in m.group(1): return m.group(0)
        body = m.group(2)
        # טקסט חשוף (בלי ct-t, למשל cta_bonus): עוטפים כדי שלא יגלוש לשורה נוספת בגופן החלופי באנדרואיד
        mt = re.match(r'([^<]+?)( <span>←</span>)$', body)
        if mt: body = '<span class="ct-t">%s</span>%s' % (mt.group(1), mt.group(2))
        return m.group(1) + body + '<span class="v4-pay">%sתשלום מאובטח</span></a>' % LOCK
    p = re.sub(r'(<a class="cta"[^>]*data-checkout[^>]*>)(.*?)</a>', inbtn, p, flags=re.S)
    # חלק 4 (1): סקשנים שיוצאים מהדף, כולל מה שבתוכם
    for name, _why in BEN.get("a5_remove_sections", []):
        a, z = sec_bounds(p, name); a = p.rindex("<section", 0, a); z += len("</section>")
        while p[z:z + 1] == "\n": z += 1
        p = p[:a] + p[z:]
    # חלק 4 (2): בלוק האחריות בקופסת הכפתור, במקום השורה "החזר מלא" שמתחת לו
    g = BEN.get("a5_guarantee")
    if g:
        i = p.index('data-cta="%s"' % g["cta"]); k = p.index(g["micro_old"], i); assert k - i < 1500
        p = p[:k] + g["micro_new"] + g["html"] + p[k + len(g["micro_old"]):]
    # ראשי 11.11: בלי קווים ארוכים בטקסט (מחוץ ל-script/style)
    nd = lambda t: t.replace(" — ", " - ").replace("—", "-").replace("–", "-")
    out, last = [], 0
    for m in re.finditer(r'<(script|style)\b.*?</\1>', p, flags=re.S):
        out.append(nd(p[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(nd(p[last:])); p = "".join(out)
    # ראשי 11.11: "תשלום מאובטח" גם בכפתור הצמוד (שורה שנייה, כמו בשאר הכפתורים)
    p, n = re.subn(r'(<a class="cta" data-cta="sticky"[^>]*>.*?)</a>', lambda m: m.group(1) + '<span class="v4-pay">%sתשלום מאובטח</span></a>' % LOCK, p, count=1, flags=re.S)
    assert n == 1
    # מספור מחדש אחרי הוספת הסקשן: data-sec ברצף (max_section/at_section ממשיכים לתאר עומק), והמספרים הגדולים 01, 02...
    n = iter(range(1, 999)); p = re.sub(r'(<(?:header|section)\b[^>]*?)data-sec="\d+"', lambda m: m.group(1) + 'data-sec="%d"' % next(n), p)
    k = iter(range(1, 99)); p = re.sub(r'data-num="\d+"', lambda m: 'data-num="%02d"' % next(k), p)
    return p

# 14: הצבעים של בן מהסרטונים (סגנון הזהב של P25): רקע #0E0E10, טקסט לבן, הדגשה צהוב-זהב #FECF00, כפתור צהוב וטקסט שחור.
# מחליף כל צבע בז'/קרם/זהב-חום של a5 (גם בשכבת v4) בגוון המקביל. רק ב-a5v4
COLOR_MAP_HEX = {"#D3B77A": "#FECF00", "#C9A96E": "#E6B800", "#EADBB5": "#FFE14D", "#F0E2BE": "#FFE14D", "#D9BE83": "#FECF00",
                 "#C6A266": "#E6B800", "#F3EDE2": "#FFFFFF", "#DCD5C8": "#E6E6E6", "#A8A296": "#B8B8B8", "#7D786F": "#8E8E8E",
                 "#08090C": "#0E0E10", "#0C0D12": "#0E0E10", "#111319": "#151518", "#060708": "#0A0A0B", "#0A0B0F": "#0E0E10",
                 "#1A1C24": "#1A1A1E", "#1B1C22": "#1A1A1E", "#1B1D22": "#1A1A1E", "#121318": "#000000", "#8A6A2F": "#B38F00",
                 "#9A7B3F": "#B38F00", "#F5F3EE": "#FFFFFF", "#E4DCCB": "#E6E6E6", "#F0D193": "#FFE14D", "#14161B": "#151518"}
COLOR_MAP_RGB = {"211,183,122": "254,207,0", "201,169,110": "254,207,0", "234,219,181": "255,225,77", "243,237,226": "255,255,255",
                 "8,9,12": "14,14,16", "12,13,18": "14,14,16", "120,90,40": "120,96,0", "168,162,150": "184,184,184",
                 "6,7,10": "10,10,11", "4,5,7": "8,8,9"}
def ben_colors(p):
    for a_, b_ in COLOR_MAP_HEX.items():
        p = re.sub(re.escape(a_) + r"\b", b_, p, flags=re.I)
    for a_, b_ in COLOR_MAP_RGB.items():
        p = re.sub(r"(rgba?\()\s*" + a_.replace(",", r",\s*") + r"\b", r"\g<1>" + b_, p)
    return p

def sec_bounds(p, name):
    m = re.search(r'<(header|section)\b[^>]*data-name="%s"[^>]*>' % re.escape(name), p); assert m, name
    end = p.index("</%s>" % m.group(1), m.end())
    return m.end(), end

def player_html(key, cfg):
    # 20 (בן 11.11): "הצצה פנימה" - מסגרת נגן כמו בקורס: תווית, תמונת פתיחה עם כפתור הפעלה גדול, פס התקדמות,
    # שם השיעור + החלק והשיעור + משך. מתחת: "זה שיעור אחד מתוך 90" וכפתור קנייה. הסרטון נטען רק בלחיצה, עם קול
    has = bool(cfg.get("src")); poster = cfg.get("poster") or ""
    ar = "%d/%d" % (cfg["w"], cfg["h"])
    if has:
        inner = ('<img src="%s" alt="" loading="lazy" decoding="async" width="%d" height="%d">' % (poster, cfg["w"], cfg["h"]) if poster else "")
        inner += '<span class="v4-pi">%s</span>' % PLAY
        box = ('<button type="button" class="v4-box" style="aspect-ratio:%s" aria-label="%s" data-v4src="%s" data-v4poster="%s">%s</button>'
               % (ar, cfg.get("aria", "הפעלת השיעור"), cfg["src"], poster, inner))
    else:
        box = '<div class="v4-box" style="aspect-ratio:%s;cursor:auto"><span class="v4-ph">%s</span></div>' % (ar, cfg["label"])
    lesson = cfg.get("lesson") or "שם השיעור (מהעריכה)"
    meta = " · ".join(x for x in (cfg.get("part"), cfg.get("num")) if x)
    btn = ('<div class="v4-ctab"><a class="cta" data-cta="peek" data-checkout href="#"><span class="ct-t">כן, אני רוצה להתחיל עכשיו '
           '<span class="pgrp">ב-<s class="was">1,290</s> 297 ₪</span></span> <span>←</span><span class="v4-pay">%sתשלום מאובטח</span></a>'
           '<p class="cta-micro"><b class="launch">מחיר השקה לזמן מוגבל</b> · גישה מיידית לקורס ולבונוסים · החזר מלא תוך 7 ימים</p></div>') % LOCK
    return ('<div class="v4-peek"><h3 class="v4-peek-h">הצצה פנימה</h3>'
            '<figure class="v4-slot v4-player" data-slot="%s"><div class="v4-pl-top"><span class="v4-pl-dot"></span>שיעור אמיתי מתוך הקורס</div>'
            '%s<div class="v4-pl-bar" aria-hidden="true"><i></i></div>'
            '<figcaption class="v4-pl-meta"><span class="v4-pl-t"><b>%s</b><small>%s</small></span><span class="v4-pl-d">%s</span></figcaption></figure>'
            '<p class="v4-peek-n">זה שיעור אחד מתוך 90</p>%s</div>') % (key, box, lesson, meta, cfg.get("dur", ""), btn)

def slot_html(key, cfg):
    has = bool(cfg.get("src"))
    if not has and not PREVIEW: return ""
    if cfg.get("player"): return player_html(key, cfg)
    ar = "%d/%d" % (cfg["w"], cfg["h"])
    poster = cfg.get("poster") or ""
    if cfg["kind"] == "video":
        inner = ('<img src="%s" alt="" loading="lazy" decoding="async" width="%d" height="%d">' % (poster, cfg["w"], cfg["h"]) if poster else "")
        inner += '<span class="v4-pi">%s</span>' % PLAY if has else '<span class="v4-ph">%s</span>' % cfg["label"]
        attrs = ' data-v4src="%s" data-v4poster="%s"' % (cfg["src"], poster) if has else ""
        box = '<button type="button" class="v4-box" style="aspect-ratio:%s" aria-label="%s"%s>%s</button>' % (ar, cfg.get("aria", "הפעלת הסרטון"), attrs, inner)
    else:
        inner = ('<img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">' % (cfg["src"], cfg.get("alt", ""), cfg["w"], cfg["h"])) if has else '<span class="v4-ph">%s</span>' % cfg["label"]
        box = '<div class="v4-box" style="aspect-ratio:%s;cursor:auto">%s</div>' % (ar, inner)
    # כותרת מעל הנכס (למשל סרטון ההמלצות, בנוסח של בן), רק כשהנכס עצמו בדף
    head = '<p class="v4-slot-h">%s</p>' % cfg["title"] if cfg.get("title") else ""
    return '<figure class="v4-slot%s" data-slot="%s">%s%s</figure>' % (" v4-img" if cfg["kind"] == "image" else "", key, head, box)

def _block(p, start):
    # הבלוק המלא (div/details/article...) שמתחיל ב-start, לפי ספירת עומק של אותה תגית
    tag = re.match(r'<(\w+)', p[start:]).group(1); depth = 0
    for m in re.compile(r'<(/?)%s\b[^>]*>' % tag).finditer(p, start):
        depth += -1 if m.group(1) else 1
        if depth == 0: return start, m.end()
    raise AssertionError(tag)

def tour_html(key, cfg):
    # חלק 5 סעיף 4: סיור בקורס. אין <video> ב-HTML (כדי שמספרי הסרטונים במדידה לא יזוזו) - JS יוצר אותו כשמתקרבים
    if not cfg.get("src"):
        return ('<figure class="v4-slot v4-tour" data-slot="%s"><div class="v4-box" style="aspect-ratio:%d/%d;cursor:auto"><span class="v4-ph">%s</span></div></figure>' % (key, cfg["w"], cfg["h"], cfg["label"])) if PREVIEW else ""
    poster = cfg.get("poster") or ""
    img = '<img src="%s" alt="" loading="lazy" decoding="async" width="%d" height="%d">' % (poster, cfg["w"], cfg["h"]) if poster else ""
    return ('<figure class="v4-slot v4-tour" data-slot="%s"><button type="button" class="v4-box" style="aspect-ratio:%d/%d" aria-label="%s" data-v4tour="%s" data-v4poster="%s">%s<span class="v4-pi">%s</span></button></figure>'
            % (key, cfg["w"], cfg["h"], cfg.get("aria", "הפעלת הסרטון"), cfg["src"], poster, img, PLAY))

def ben_inside(p):
    # בן 11.11 חלק 5-6: "לא לספר מה יש בפנים - להראות". בחלק 6 נשארים רק:
    # כותרת + "כל חלק הוא צעד" / "לא עוד קורס שרואים ושוכחים" / הטקסט של בן / סיור (ע21) / נגן ע20 / "קורס הליבה: 90 שיעורים" / כפתור "לכל 90 השיעורים"
    cfg = BEN["a5_inside"]
    a, z = sec_bounds(p, "מה יש בפנים"); sec = p[a:z]
    def take(rx):
        nonlocal sec
        m = re.search(rx, sec); assert m, rx
        i, j = _block(sec, m.start()); blk = sec[i:j]; sec = sec[:i] + sec[j:]; return blk.strip()
    def take_p(rx):
        nonlocal sec
        m = re.search(rx, sec, re.S); assert m, rx
        sec = sec[:m.start()] + sec[m.end():]; return m.group(0).strip()
    nc = take(r'<div class="notcourse">')
    peek = take(r'<div class="v4-peek">') if '<div class="v4-peek">' in sec else take(r'<div class="peek">')
    mods = take(r'<div class="mods">')
    tool = take_p(r'<p class="toolbox">.*?</p>')
    start = take_p(r'<p class="lead">לא יודעים מאיפה להתחיל\?.*?</p>')
    m = re.search(r'<p class="lead">.*?</p>', sec, re.S); assert m and "כל חלק הוא צעד" in m.group(0)
    head = sec[:m.end()]; rest = sec[m.end():].strip()
    assert re.fullmatch(r'(\s|</div>)*', rest), rest[:200]
    tour = tour_html("t21", SLOTS["t21"]) if "t21" in SLOTS else ""
    # חלק 6: הקופסה "לא עוד קורס", "קורס הליבה: 90 שיעורים", "לא יודעים מאיפה להתחיל" וכרטיסי החלקים יוצאים
    new = "\n".join(x for x in (head, cfg["html"], tour, peek) if x) + "\n" + rest
    return p[:a] + "\n" + new + p[z:]

def ben_bonus(p):
    # בן 11.11 חלק 6: הבונוסים מיד אחרי שני הסרטונים, כרטיס לכל בונוס, סיכום מקוצר
    cfg = BEN["a5_bonus"]
    # הכפתור cta3 שהיה בין "מה יש בפנים" לבונוסים עובר אל אחרי הבונוסים
    a0, z0 = sec_bounds(p, "מה יש בפנים"); z0 += len("</section>")
    m = re.compile(r'\s*<section class="ctab" data-buyzone>.*?</section>', re.S).match(p, z0); assert m and 'data-cta="cta3"' in m.group(0)
    ctab = m.group(0); p = p[:m.start()] + p[m.end():]
    a, z = sec_bounds(p, "בונוסים"); sec = p[a:z]
    # כרטיסים
    i = sec.index('<div class="bx-list">'); i, j = _block(sec, i); old = sec[i:j]
    vis = []
    for mm in re.finditer(r'<div class="bx-vis">', old):
        x, y = _block(old, mm.start()); vis.append(old[x:y])
    assert len(vis) == len(cfg["cards"]) == 5, len(vis)
    cards = []
    for v, c in zip(vis, cfg["cards"]):
        lis = "".join("<li>%s</li>" % t for t, _src in c["bullets"])
        cards.append('<article class="bx2"><div class="bx2-head">%s<div class="bx2-t"><h3>בונוס %d: %s</h3><p class="bx2-kind">%s</p></div></div>'
                     '<ul class="bx2-ul">%s</ul>%s<p class="bx2-val"><s>שווי: %d ₪</s><b>%s</b></p></article>' % (v, c["n"], c["name"], c["kind"], lis, ('<p class="bx2-more">%s</p>' % c["close"]) if c.get("close") else "", c["value"], cfg["free"]))
    new_list = '<div class="bx-list bx2-list">%s</div>' % "".join(cards)
    sec = sec[:i] + new_list + sec[j:]
    # הסיכום הישן יוצא: "תחשבו רגע מה אתם מקבלים" (3 עולמות) וטבלת "סיכום חבילת הבונוסים"
    for cls in ("bx-worlds", "bx-sum"):
        k = sec.index('<div class="%s">' % cls); x, y = _block(sec, k); sec = sec[:x] + sec[y:]
    # חלק 7: הסיכום שבסוף הבונוסים (המחיר, "קורס הליבה + ...", הכפתור) יוצא - עובר לקופסת ההצעה
    k = sec.index('<div class="bx-final">'); x, y = _block(sec, k); sec = sec[:x] + sec[y:]
    # חלק 7: כותרת חדשה
    sec, n = re.subn(r'<h2>[^\n]*?</h2>', '<h2>%s</h2>' % cfg["h2"], sec, count=1); assert n == 1
    p = p[:a] + sec + p[z:]
    # cta3 (כפתור ביניים) עובר אל אחרי "איך מתחילים", כדי שהבונוסים וההצעה יהיו צמודים בלי כפתור כפול
    a2, z2 = sec_bounds(p, "איך מתחילים"); z2 += len("</section>")
    return p[:z2] + ctab + p[z2:]

def ben_offer(p):
    # בן 11.11 חלק 7: "רגע הנוקאאוט" - #offer עובר אל מיד אחרי הבונוסים, במבנה חדש
    cfg = BEN["a5_offer"]
    m = re.search(r'<section id="offer"[^>]*>', p); a = m.start(); z = p.index("</section>", a) + len("</section>")
    old = p[a:z]; tag = m.group(0)
    cheap = re.search(r'<p class="cheap">.*?</p>', old, re.S).group(0)  # הנוסח של בן מתחת למחיר (חלק 1 סעיף 2) נשאר
    btn = re.search(r'<a class="cta" data-cta="offer".*?</a>', old, re.S).group(0)
    if cfg.get("btn_text"):  # חלק 9: בכפתור של הקופסה בלבד - בלי המחיר המחוק
        btn, k = re.subn(r'<span class="ct-t">.*?</span></span>', '<span class="ct-t">%s</span>' % cfg["btn_text"], btn, count=1, flags=re.S); assert k == 1
    p = p[:a] + p[z:]
    while p[a:a + 1] == "\n" and p[a - 1:a] == "\n": p = p[:a] + p[a + 1:]
    rows = "".join('<li><span>%s</span><b>%s</b></li>' % (n, v) for n, v in cfg["rows"])
    html = ('%s<div class="wrap stack">\n<h2>%s</h2>\n<div class="v4-ko">'
            '<ul class="v4-ko-list">%s</ul>'
            '<div class="v4-ko-tot"><span>%s</span><b>%s</b></div>'
            '<div class="v4-ko-price"><p class="v4-ko-reg">%s <s>%s</s></p><p class="v4-ko-now"><span>%s</span> <b>%s</b></p></div>'
            '%s\n<p class="cta-micro">%s</p>\n%s'
            '</div>\n</div></section>') % (tag, cfg["h2"], rows, cfg["total"][0], cfg["total"][1], cfg["regular"][0], cfg["regular"][1],
                                            cfg["launch"][0], cfg["launch"][1], btn, cfg["micro"], cheap)
    a2, z2 = sec_bounds(p, "בונוסים"); z2 += len("</section>")
    p = p[:z2] + "\n\n" + html + p[z2:]
    # מספור מחדש (data-sec לפי הסדר החדש; המספרים הגדולים 01.. לא משתנים בסדרם)
    n = iter(range(1, 999)); p = re.sub(r'(<(?:header|section)\b[^>]*?)data-sec="\d+"', lambda m: m.group(1) + 'data-sec="%d"' % next(n), p)
    return p

def place_slots(p, page):
    for key, cfg in SLOTS.items():
        if key.startswith("_"): continue
        where = cfg["where"].get(page)
        if not where: continue
        has = bool(cfg.get("src"))
        a, b = sec_bounds(p, where["section"])
        at_ = where["at"]
        if at_ == "replace_vid":
            # 15 (a5): ע15 מחליף את סרטון ההמלצות הקיים באותו מקום (אותה מדידה של video_play). בלי קובץ - הישן נשאר
            m = re.compile(r'<figure class="vid">(.*?)</figure>', re.S).search(p, a, b); assert m, (key, page)
            if has:
                fig = m.group(0)
                fig = re.sub(r'poster="[^"]*"', 'poster="%s"' % (cfg.get("poster") or ""), fig, count=1)
                fig = re.sub(r'(<video[^>]*?) src="[^"]*"', r'\1 src="%s"' % cfg["src"], fig, count=1)
                if cfg.get("play_label"): fig = re.sub(r'<span>[^<]*</span></button>', '<span>%s</span></button>' % cfg["play_label"], fig, count=1)
                head = '<p class="v4-slot-h">%s</p>\n' % cfg["title"] if cfg.get("title") else ""
                fig = fig.replace('<figure class="vid">', '<figure class="vid" data-slot="%s">' % key, 1)
                p = p[:m.start()] + head + fig + p[m.end():]
            elif PREVIEW:
                p = p[:m.end()] + '\n<figure class="v4-slot" data-slot="%s"><div class="v4-box" style="aspect-ratio:16/5;cursor:auto"><span class="v4-ph">%s</span></div></figure>' % (key, cfg["label"]) + p[m.end():]
            continue
        if at_ == "carousel":
            # 16 (a5): צילום הוואטסאפ נכנס לקרוסלת הודעות הוואטסאפ הקיימת, כשקופית ראשונה (לא בלוק נפרד)
            m = re.compile(r'<div class="car-track">').search(p, a, b); assert m, (key, page)
            if has:
                cap = ('<figcaption class="car-q"><q>%s</q>%s</figcaption>' % (cfg["quote"], ("<span>%s</span>" % cfg["who"]) if cfg.get("who") else "")) if cfg.get("quote") else ""
                sl = '<figure class="car-slide" data-slot="%s">%s<img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d"></figure>' % (key, cap, cfg["src"], cfg.get("alt", ""), cfg["w"], cfg["h"])
            elif PREVIEW:
                sl = '<figure class="car-slide v4-slot" data-slot="%s"><div class="v4-box" style="aspect-ratio:%d/%d;cursor:auto"><span class="v4-ph">%s</span></div></figure>' % (key, cfg["w"], cfg["h"], cfg["label"])
            else:
                continue
            p = p[:m.end()] + sl + p[m.end():]
            # נקודה נוספת לקופית החדשה (הנקודות קבועות ב-HTML, וכפתור "הבא" מוגבל למספר שלהן)
            k = p.index('<div class="car-dots">', m.end()); assert k < b + len(sl) + 50
            p = p[:k] + '<div class="car-dots"><i></i>' + p[k + len('<div class="car-dots">'):]
            continue
        if at_ == "inside_tour":
            continue  # חלק 5: ben_inside() מציב אותו בסדר החדש
        if at_ == "replace_peek":
            # 17 (a5): ע20 (הצצה של כחצי דקה מתוך הקורס) במקום תיבת ההצצה; בלי קובץ - התיבה נשארת
            i = p.index('<div class="peek">', a); j = p.index('<div class="notcourse">', i); assert j < b
            h = slot_html(key, cfg)
            if has: p = p[:i] + h + p[j:]
            elif h: p = p[:i] + h + "\n" + p[i:]
            continue
        h = slot_html(key, cfg)
        if not h: continue
        if at_ == "after_h2":
            m = re.compile(r"</h2>").search(p, a, b); assert m, (key, page)
            # אחרי הכותרת ואחרי פסקת הפתיחה שצמודה לה, אם יש
            m2 = re.compile(r"\s*<p class=\"(?:lead|sub|offer-lead)\">.*?</p>", re.S).match(p, m.end())
            at = m2.end() if m2 else m.end()
        elif at_ == "end":
            at = p.rfind("</div>", a, b); assert at > a
        p = p[:at] + "\n" + h + p[at:]
    return p

def lock_everywhere(p, add_lines=True):
    # "תשלום מאובטח" עם מנעול אחיד (SVG במקום אימוג'י), בכל מקום שהוא כבר מופיע ליד כפתור או מחיר
    p = p.replace("🔒 תשלום מאובטח", '<span class="v4-lock">%sתשלום מאובטח</span>' % LOCK)
    p = re.sub(r'(?<![>"])(?<!</svg>)תשלום מאובטח(?![^<]*</span>)', '<span class="v4-lock">%sתשלום מאובטח</span>' % LOCK, p)
    # כפתור (חוץ מהדביק) שאין אחריו "תשלום מאובטח" קרוב: מוסיפים שורה קטנה עם מנעול מתחת לכפתור
    if not add_lines: return p
    out, last = [], 0
    for m in re.finditer(r'<a class="cta[^"]*" data-cta="([a-z_0-9]+)"[^>]*>.*?</a>', p, re.S):
        if m.group(1) == "sticky": continue
        near = p[m.end():m.end() + 900]
        near = near[:near.find("<a class=\"cta")] if "<a class=\"cta" in near else near
        if "תשלום מאובטח" in near: continue
        out.append(p[last:m.end()]); out.append('\n<p class="v4-sec"><span class="v4-lock">%sתשלום מאובטח</span></p>' % LOCK); last = m.end()
    out.append(p[last:]); return "".join(out)

def v4(p, page, old, new):
    assert p.count('data-variant="%s"' % old) == 1
    p = p.replace('data-variant="%s"' % old, 'data-variant="%s"' % new)
    if page == "a5":
        # בהצעה: רשימת "תשלום מאובטח / גישה מיידית" עוברת אל מתחת לכפתור, לפני הקישור לוואטסאפ (אותו טקסט)
        ms = re.search(r'\s*<ul class="secure">.*?</ul>', p, re.S); assert ms
        sec = ms.group(0); p = p.replace(sec, "", 1)
        a, b = sec_bounds(p, "ההצעה")
        mc = re.compile(r'<a class="cta"[^>]*data-cta="offer"[^>]*>.*?</a>', re.S).search(p, a, b); assert mc
        p = p[:mc.end()] + sec + p[mc.end():]
        p = ben_a5(p)
    p = self_font(p)
    p = lock_everywhere(p, add_lines=(page != "a5"))
    p = place_slots(p, page)
    if page == "a5":
        p = ben_inside(p)
        p = ben_bonus(p)
        p = ben_offer(p)
    p, nd = defer_imgs(p); assert nd >= 3, nd
    # בלוק נפרד בסוף ה-head, אחרי ה-CSS של הדף, כדי שהשכבה של v4 תגבר עליו
    assert p.count("</head>") == 1
    p = p.replace("</head>", "<style>" + CSS_COMMON + CSS_PAGE[page] + "</style>\n</head>", 1)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    if page == "a5":
        p = ben_colors(p)
    if NOINDEX:
        assert 'name="robots"' not in p
        p = p.replace('<meta name="viewport"', '<meta name="robots" content="noindex,nofollow"><meta name="viewport"', 1); assert 'name="robots"' in p
    for k in ("TRACK_ENDPOINT", "fbq(", "clarity", "NLP_OWNER", "InitiateCheckout"):
        assert k in p, "measurement missing: " + k
    return p

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    import shutil; os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    for k in FONT_RANGES: shutil.copy(os.path.join(HERE, "fonts", "heebo-%s.woff2" % k), os.path.join(OUT, "assets", "fonts"))
    for page, fn, old in (("pr2", build_v3.build_pr2, "pr2v3"), ("a5", build_v3.build_a5, "a5v3")):
        new = page + "v4"; p = v4(fn(), page, old, new)
        open(os.path.join(OUT, new + SUFFIX + ".html"), "w", encoding="utf8").write(p)
        print(new, len(p), "slots:", re.findall(r'data-slot="(\w+)"', p), "locks:", p.count('class="v4-lock"'), "added lines:", p.count('class="v4-sec"'))
