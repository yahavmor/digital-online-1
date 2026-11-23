# ב117 (23.11): יהודית בלשונית 10 (השוואת קהלים) של הדשבורד - כדי ש-aff_yehudit יופיע בטופס ההוצאה היומית ושהיא תיספר כמו רמי וקרלין.
# יעד הדף הקצר a5s (aff בקישור), מימון שלה. התקציב לא נמסר (budget:null כמו רמי וקרלין בהתחלה). סופרים מ-23.11 16:00.
# שימוש: python3 patch_b117.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os, hashlib
root, day, hm = sys.argv[1:4]
H = lambda s: hashlib.sha256(s.encode()).hexdigest()[:16]
OLD = '''{code:"karlin",lbl:"קרלין",aud:"קהל קר, נשים 40-60",copy:"",budget:30,from:"2026-11-18T16:00:00",day0:"2026-11-18",sw:null,noSwitch:"דף קצר (a5s)"}]};'''
NEW = '''{code:"karlin",lbl:"קרלין",aud:"קהל קר, נשים 40-60",copy:"",budget:30,from:"2026-11-18T16:00:00",day0:"2026-11-18",sw:null,noSwitch:"דף קצר (a5s)"},
 /* ב117 (23.11): יהודית - קמפיין הסליקות עם הדף הקצר a5s (aff בקישור), במימון שלה. התקציב לא נמסר. הוצאה במפתח aff_yehudit */
 {code:"yehudit",lbl:"יהודית",aud:"קהל קר",copy:"",budget:null,from:"2026-11-23T16:00:00",day0:"2026-11-23",sw:null,noSwitch:"דף קצר (a5s)"}]};'''
LOG = '["%s","%s - ב117 (\\"מאשר ב117\\" מיהב): יהודית בלשונית 10 (יעד הדף הקצר a5s, מימון שלה, תקציב לא נמסר). aff_yehudit ברשימה של טופס ההוצאה היומית לקמפיין. הרשומה במאגר המשווקים נוספה באותו יום."],\n' % (day, hm)
for f, reps in [("nlp/dashboard.html", [(OLD, NEW), ('const CHANGELOG=[\n', 'const CHANGELOG=[\n' + LOG)]),
                ("nlp/campaign.html", [('const CHANGELOG=[\n', 'const CHANGELOG=[\n' + LOG)])]:
    p = os.path.join(root, f); s = open(p, encoding="utf-8").read(); h0 = H(s)
    for a, b in reps:
        assert s.count(a) == 1, (f, a[:60], s.count(a)); s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s); print(f, h0, "->", H(s))
