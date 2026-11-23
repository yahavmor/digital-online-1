# ב117 (23.11) - יהודית, משווקת חדשה בקמפיין הסליקות (הדף הקצר a5s, מימון שלה)

אושר: "ב117 - מאשר" (יהב, 23.11).

## מה היה קיים (לפני)
- מאגר המשווקים 237596: 10 רשומות (claude_test כבוי, שחר, שירה, רחל, גל, אמיר, יהל, יוסף, רמי, קרלין). יהודית לא היתה.
- a5s.html: השיוך לפי aff בקישור הוא כללי (NLP_OWNER, ב25) - כל קוד נשמר 30 יום בעוגייה וב-localStorage, ונשלח בכל אירוע (x=aff=...) ובבקשת דף התשלום. לא נדרש שינוי בדף.
- גיליון האירועים: מקבל את aff מהאירועים כמו שהוא. הסקריפטים היומיים (aff_daily, whatsells, a5s_line) מזהים משווקים מהנתונים.
- דשבורד: לשונית המשווקים ("מה מוכר") סופרת לפי aff אוטומטית. לשונית 10 (השוואת קהלים) וטופס ההוצאה היומית לקמפיין מכירים רק משווקים שרשומים ב-AUD.camps - יהודית לא היתה שם, ולכן aff_yehudit לא היה בטופס.
- אזור המשווקים (partner.html): קישור אישי = partner.html#t=<token>, הטוקן נבדק בצד Make מול 237596.

## מה נוסף
1. **237596**: רשומה yehudit - code yehudit, שם יהודית, active true, fee 220, pct 0, note עם ב117. טוקן אקראי (40 תווים) בשדה token. בלי budget (התקציב היומי לא נמסר).
2. **dashboard.html + campaign.html** (`patch_b117.py`, main commit לפי הסטטוס במסמך): יהודית ב-AUD.camps (קהל קר, budget null, מ-23.11 16:00, יעד a5s), שורת changelog בשני הדפים. aff_yehudit בטופס ההוצאה היומית.
3. **הלינק האישי** נמסר ליהב בצ'אט בלבד. אומת מול ה-hook של אזור המשווקים: מחזיר me / yehudit / יהודית / 220; טוקן שגוי נדחה.

## בדיקות
- `node t_b117_dash.js <new root> <old root>` - 18/18: aff_yehudit בטופס, השמירה שולחת creative=aff_yehudit, 12 מסכים אחרים לא השתנו.
- `node t_a5s_yehudit.js <root>` - 9/9: NLP_OWNER, עוגייה 30 יום, view / form_submit / checkout_details עם aff=yehudit, בקשת דף התשלום עם aff=yehudit, ביקור חוזר בלי aff נשאר yehudit.
- t_aff_yehudit.js (העתק של t_aff_rami מב109) לא מתאים יותר ל-a5s של ב110 (אין data-cta="offer") - הוחלף ב-t_a5s_yehudit.js.

## נשאר ליהב
- למסור ליהודית את הלינק האישי ואת קישור המודעה: https://funnel.digitalonline.co.il/nlp/a5s.html?aff=yehudit&utm_source=facebook&utm_medium=affiliate&utm_campaign={{campaign.name}}&utm_content={{ad.name}}
- תקציב יומי: כשיימסר - לעדכן budget ב-237596 וב-AUD.camps (לבדיקת 120%).
- להוסיף את aff_yehudit לשגרת ההוצאה של הממומן (מ35).
