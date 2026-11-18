# מ53/ב109 (18.11): רמי וקרלין בלשונית 10 (השוואת קהלים) - כדי ש-aff_rami ו-aff_karlin יופיעו ברשימה של טופס ההוצאה היומית לקמפיין.
# הקמפיינים: קהל קר 45-65+ (התבנית של מ52/מ53), יעד הדף הקצר a5s. התקציב עוד לא ידוע. סופרים מ-18.11 16:00 (לפני כן אין כניסות עם הקודים).
# שימוש: python3 patch_m53_spend.py <repo root> "<YYYY-MM-DD>" "<HH:MM>"
import sys, os
root, day, hm = sys.argv[1:4]
p = os.path.join(root, "nlp/dashboard.html"); s = open(p, encoding="utf-8").read()
for a, b in [
 ('''{code:"shira",lbl:"שירה",aud:"קהל קר",copy:"p25_brain_c2",budget:40,from:"2026-11-16T20:05:00",day0:"2026-11-16",sw:null,noSwitch:"מ-16.11 20:05"}]};''',
  '''{code:"shira",lbl:"שירה",aud:"קהל קר",copy:"p25_brain_c2",budget:40,from:"2026-11-16T20:05:00",day0:"2026-11-16",sw:null,noSwitch:"מ-16.11 20:05"},
 /* מ53/ב109 (18.11): רמי וקרלין - קהל קר 45-65+, מודעת רכישה, יעד הדף הקצר a5s (aff בקישור). הוצאה במפתחות aff_rami ו-aff_karlin */
 {code:"rami",lbl:"רמי",aud:"קהל קר 45-65+",copy:"",budget:null,from:"2026-11-18T16:00:00",day0:"2026-11-18",sw:null,noSwitch:"דף קצר (a5s)"},
 {code:"karlin",lbl:"קרלין",aud:"קהל קר 45-65+",copy:"",budget:null,from:"2026-11-18T16:00:00",day0:"2026-11-18",sw:null,noSwitch:"דף קצר (a5s)"}]};'''),
 ('const CHANGELOG=[\n', 'const CHANGELOG=[\n["%s","%s - מ53/ב109: רמי וקרלין בלשונית 10 (קהל קר 45-65+, יעד הדף הקצר a5s). aff_rami ו-aff_karlin ברשימה של טופס ההוצאה היומית לקמפיין."],\n' % (day, hm)),
]:
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s); print("ok")
