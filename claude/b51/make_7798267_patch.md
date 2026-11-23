# ב51 - שינויים בתרחיש 7798267 (Tracking Ingest) ובמאגר 210989

מוחלים רק בפריסה, אחרי "מאשר ב51". לפני כן מייצאים גיבוי של ה-blueprint.

## מבנה הנתונים 624218 (מאגר 210989)
מוסיפים שדות, ולא משנים את השדות הקיימים:

| שדה | סוג | ערכים |
|---|---|---|
| consent | text | "1" (סימן) / "0" |
| pay_failed | text | "1" אחרי חזרה עם status=failed |
| stop | text | wa_not_now / unsubscribed - עוצר את כל השלבים האוטומטיים |
| rec1_at | date | מתי יצא מייל 1 |
| rec2_at | date | מתי יצא מייל 2 |
| rec3_at | date | מתי יצא מייל 3 |

## 7798267 - מסלול 9 (checkout details -> leads store)
מוסיפים לשדות של AddRecord:
```
"consent": "{{if(1.lead_consent = \"1\"; \"1\"; \"0\")}}"
```
(השמירה ממשיכה להחליף את הרשומה, כמו היום. פרטים חדשים = נטישה חדשה)

## 7798267 - מסלול חדש: שינוי הסכמה אחרי הפרטים
```json
{"flow":[{"id":11,"module":"datastore:UpdateRecord","version":1,"parameters":{"datastore":210989},
  "filter":{"name":"ב51: שינוי הסכמה אחרי הפרטים","conditions":[[{"a":"{{1.ev}}","b":"checkout_consent","o":"text:equal"},{"a":"{{1.lead_email}}","o":"exist"}]]},
  "mapper":{"key":"{{lower(trim(1.lead_email))}}","data":{"consent":"{{if(1.lead_consent = \"1\"; \"1\"; \"0\")}}"},"insertMissing":false},
  "onerror":[{"id":12,"module":"builtin:Ignore","version":1,"mapper":{}}]}]}
```

## 7798267 - מסלול חדש: נכשל בתשלום (ב50 סעיף 2)
```json
{"flow":[
  {"id":13,"module":"datastore:SearchRecord","version":1,"parameters":{"limit":1,"datastore":210989},
   "filter":{"name":"ב50/ב51: נכשל בתשלום","conditions":[[{"a":"{{1.ev}}","b":"checkout_failed","o":"text:equal"},{"a":"{{1.sid}}","o":"exist"}]]},
   "mapper":{"filter":[[{"a":"sid","b":"{{1.sid}}","o":"text:equal"}]]},"onerror":[{"id":14,"module":"builtin:Ignore","version":1,"mapper":{}}]},
  {"id":15,"module":"datastore:UpdateRecord","version":1,"parameters":{"datastore":210989},
   "mapper":{"key":"{{13.key}}","data":{"pay_failed":"1"},"insertMissing":false},
   "onerror":[{"id":16,"module":"builtin:Ignore","version":1,"mapper":{}}]}]}
```

## בדיקה אחרי ההחלה (בלי רכישה)
שולחים ל-hook של המעקב 3 אירועים עם `int=1`:
1. `checkout_details` עם מייל בדיקה של יהב ועם `lead_consent=1`.
2. `checkout_consent` עם `lead_consent=0`.
3. `checkout_failed` עם אותו sid.

בכל שלב בודקים ש-210989 מתעדכן: `consent` הופך ל-0, ו-`pay_failed` הופך ל-1. בסוף מוחקים את רשומת הבדיקה.
