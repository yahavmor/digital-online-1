# ב101: בונה את הקלט ל-8627262 - קוד אקראי (32 hex) לכל רכישת קורס אמיתית בכרטיס, מהגיליון.
# שימוש (אחרי "מאשר ב101" בלבד): python3 -I make_pairs.py <events.json> [מתאריך YYYY-MM-DD, ברירת מחדל 2026-10-20] > /dev/null 2> pairs.txt
# 9 הרוכשים לפי הראשי = מ-20.10 (8 בכרטיס + 1 בהעברה בנקאית). רכישה מ-08.10 (דף b) לא נכללת - לשאלת יהב
# stderr: pairs (עסקה:קוד,...) ו-bank_tok - **לא לשמור בריפו ולא במסמך**. הקישורים רק בצ'אט.
# stdout: טבלה מוסתרת (תאריך, דף, 4 ספרות אחרונות) לבדיקה.
import sys, json, csv, io, re, secrets
TEST = {"267429750", "270060105"}  # עסקאות הבדיקה של בן
FROM = sys.argv[2] if len(sys.argv) > 2 else "2026-10-20"
t = json.load(open(sys.argv[1]))["content"]; R = list(csv.reader(io.StringIO(t), delimiter="\t"))
seen, card, bank = set(), [], []
for r in R[1:]:
    if len(r) < 14 or r[0] < FROM or r[1] != "purchase" or r[13] not in ("cardcom_webhook", "manual_bank_transfer"): continue
    if "int=1" in "\t".join(r): continue
    m = re.search(r"deal (\d+)", r[8]); b = re.search(r"ref\s+([^\s|]+)", r[8])
    k = m.group(1) if m else ("bank_" + b.group(1) if b else "")
    if not k or k in seen or k in TEST: continue
    seen.add(k); (bank if k.startswith("bank_") else card).append((r[0][:16], r[2] or "-", k))
pairs = [(k, secrets.token_hex(16)) for _, _, k in card]
for d, v, k in card: print(d, v, "…" + k[-4:])
for d, v, k in bank: print(d, v, "העברה בנקאית (מסלול ידני)")
print("סה\"כ", len(card), "בכרטיס +", len(bank), "בהעברה בנקאית")
sys.stderr.write(json.dumps({"pairs": ",".join(k + ":" + t for k, t in pairs), "bank_tok": secrets.token_hex(16) if bank else ""}) + "\n")
