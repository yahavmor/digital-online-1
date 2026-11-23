# מחיר מחוק 1,290 ₪ במקום 2,411 ₪ (יהב 20.11: "המחיר המחוק 2411 קצת מוגזם", בחר: 1,290 = קורס הליבה, בכל 15 הדפים).
# שימוש: python3 price_apply.py <שורש main>   - עוצר בלי לשנות כלום אם hash של קובץ לא תואם או שמחרוזת לא נמצאה בדיוק.
#  - 10 דפים (a, a1-a5, b, b2, c, c2): המחיר המחוק כבר 1,290. רק שורת "שווי כולל עם הבונוסים: 2,411 ₪" יורדת.
#  - 5 דפים (a5s, a5v4-a5v7): שורת "שווי כולל: 2,411 ₪" יורדת, ו"מחיר כולל הבונוסים 2,411" -> "מחיר הקורס 1,290".
#  - a5v5: אנימציית המחיר נשענה על שורת הסכום. בלעדיה המחיר המחוק וה-297 מוצגים מיד (אחרת היו נשארים מוסתרים).
# לא נוגע בשום דבר אחר: רשימת הפריטים, שווי הבונוסים, 297, הכפתורים, הסליקה.
import sys, os, hashlib
ROOT = sys.argv[1]
H = {"a": "020e5d005a9f664d", "a1": "1f971c315f62ef51", "a2": "a0e2978768812752", "a3": "ba76a6c58205a399", "a4": "bacf1cc981cc8823",
     "a5": "17286b821903f23a", "b": "37c3c479c9210b08", "b2": "717615b8568e822a", "c": "a65d0af359405044", "c2": "488b29715ce1ef7c",
     "a5s": "2a94a2e48dd8b0f2", "a5v4": "e83d19583f98924f", "a5v5": "fa24c3b1aab32258", "a5v6": "85a45bedcc793af2", "a5v7": "46d83d6b8b8b5b06"}
TOT_A = '<div class="tot"><span>שווי כולל עם הבונוסים:</span><span>2,411 ₪</span></div>'
TOT_B = '<div class="v4-ko-tot"><span>שווי כולל:</span><b>2,411 ₪</b></div>'
REG_B = ('<p class="v4-ko-reg">מחיר כולל הבונוסים <s>2,411 ₪</s></p>', '<p class="v4-ko-reg">מחיר הקורס <s>1,290 ₪</s></p>')
# בלי שורת הסכום היה קו כפול (הקו התחתון של הפריט האחרון + הקו העליון של המחיר) - הקו של הפריט האחרון יורד
LAST = ('.v4-ko-list{list-style:none;margin:0;padding:0}', '.v4-ko-list{list-style:none;margin:0;padding:0}.v4-ko-list li:last-child{border-bottom:0}')
ANIM = ('requestAnimationFrame(f);};io.observe(tw);}', 'requestAnimationFrame(f);};io.observe(tw);}else{if(reg)reg.classList.add("in");if(now)now.classList.add("in");}')
out = {}
for f, h in H.items():
    p = os.path.join(ROOT, "nlp", f + ".html"); s = open(p, encoding="utf-8").read()
    got = hashlib.sha256(s.encode()).hexdigest()[:16]
    if got != h: sys.exit("STOP: %s.html hash %s != %s - הקובץ השתנה, לא שיניתי כלום" % (f, got, h))
    reps = [(TOT_A, "")] if f in ("a", "a1", "a2", "a3", "a4", "a5", "b", "b2", "c", "c2") else [(TOT_B, ""), REG_B, LAST]
    if f == "a5v5": reps.append(ANIM)
    for a, b in reps:
        if s.count(a) != 1: sys.exit("STOP: %s.html: %r נמצא %d פעמים - לא שיניתי כלום" % (f, a[:60], s.count(a)))
        s = s.replace(a, b)
    if "2,411" in s.replace("2,411 נספר", ""): sys.exit("STOP: %s.html: 2,411 נשאר" % f)
    out[p] = s
for p, s in out.items(): open(p, "w", encoding="utf-8").write(s)
for p, s in out.items(): print(os.path.basename(p), hashlib.sha256(s.encode()).hexdigest()[:16])
print("OK", len(out), "files")
