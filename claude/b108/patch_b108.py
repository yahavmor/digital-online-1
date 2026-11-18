# ב108 ("מאשר ב108", אפשרות 2): ערוצים של בן ב-NLP_OWNER (שיוך למשווקים, ב25) - utm_medium group/story/page/page_post ו-utm_source whatsapp.
# כניסה מהם מאפסת את השיוך הקודם למשווק (הקליק האחרון שייך לבן). בלי שינוי ניתוב ובלי שינוי בניסוי on_1711.
# מחליף את אותה שורה בכל דף שבו היא מופיעה. שימוש: python3 patch_b108.py <repo root>
import sys, os, glob
root = sys.argv[1]
OLD = 'if(a)wr(a);else if(m!=="affiliate"&&(q.get("utm_id")||/^(paid|paid_social|cpc|responder|email|bio|dm|manychat)$/.test(m)||/^(email|responder|manychat)$/.test(s)))wr("");else cur=rd()'
NEW = 'if(a)wr(a);else if(m!=="affiliate"&&(q.get("utm_id")||/^(paid|paid_social|cpc|responder|email|bio|dm|manychat|group|story|page|page_post)$/.test(m)||/^(email|responder|manychat|whatsapp)$/.test(s)))wr("");else cur=rd()'
done = []
for p in sorted(glob.glob(os.path.join(root, "nlp", "*.html"))):
    s = open(p, encoding="utf-8").read()
    n = s.count(OLD)
    if not n: continue
    assert n == 1, (p, n)
    open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW)); done.append(os.path.basename(p))
left = [os.path.basename(p) for p in glob.glob(os.path.join(root, "nlp", "*.html")) if "manychat)$/.test(m)" in open(p, encoding="utf-8").read()]
assert not left, left
print(len(done), "files:", " ".join(done))
