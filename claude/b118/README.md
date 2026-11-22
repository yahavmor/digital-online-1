# ב118: החזרת משפך הלידים (בן 22.11). שלב בדיקה בלבד, לא שונה כלום.
המפרט `claude/leads-funnel-4videos-2211.md` לא נמצא בריפו (בשום ענף) ולא ב-Drive.

## 1. הכתובות (נבדק 22.11)
| כתובת | מצב חי |
|---|---|
| `/landing_option2.html` | 404 |
| `/landing-pages/landing_option2.html` | 200, עובד |
| `/` (index.html) | מפנה ל-`marketers/client1.html`, שמחזיר 404 |
| `/funnels/two-page-funnel/two-page-funnel-1.html` (פאנל 6) | 200 |

**היסטוריית הריפו:**
- `landing_option2.html` הועבר מהשורש ל-`landing-pages/` ב-27.06 (commit c0dc70f8). מאז לא קיים בשורש.
- `index.html` מפנה ל-`marketers/client1.html` מאז 25.10 (d43e717a). הקובץ הזה לא היה קיים אף פעם.
- מאז 25.10 לא השתנה שום קובץ ב-`landing-pages/`, ב-`funnels/two-page-funnel/` וב-`marketers/`.
- אין workflow של Pages שמעתיק קבצים לשורש.
- **מסקנה:** בריפו אין גרסה מ-14.11 עם landing_option2 בשורש. ה-404 בכתובת השורש לא נוצר ב-14.11.

**מה כן נעצר ב-14.11:** Lead Journey - Ingest (6589166), הליד האחרון ב-14.11 22:54 UTC. ב-1.11 עד 14.11 היו כ-50 ריצות. זה מתאים לעצירה של תנועה, למשל מודעות שכובו או קישור שהוחלף, ולא לשינוי בדף.

**פאנל 6:** אחרי הטופס, landing_option2 (PANEL 2) מעביר ל-`funnels/two-page-funnel/two-page-funnel-1.html?panel=6`.

## 2. שיוך משווק היום
- **הדף מזהה משווק לפי `marketer`** בכתובת, מול `marketers/marketers.json`, ולא לפי `aff`.
- **מה הוא שולח:**
  - `supplier` (lm_supplier) ל-LeadManager (relay 6599073) ולהוק `jp6uk…`.
  - ל-148094 (דרך 6589166) נשמרים רק name, email, phone, page ו-stage. לא נשמר משווק.
- **ההוק `jp6uk…`** (event=lead_form עם supplier, כנראה ההתראה) לא קיים ברשימת ה-webhooks של הצוות. לכן הקריאה הזו לא מגיעה לשום תרחיש.
- **שמות לא תואמים:** קודי המשווקים ב-marketers.json (yahav, amir, rachel, galba, rami, karlen ועוד) שונים מקודי ה-aff של המשפך הנמכר (gal, rachel, amir, rami, karlin).

## 3. פיקסל Lead
- `shared/pixels.js` טוען פיקסל לפי `marketer`. בלי marketer, או עם marketer לא מוכר, נטען הפיקסל של yahav.
- בשליחת הטופס: `fbq('track','Lead')` על הפיקסל שנטען (ו-InitiateCheckout בפתיחת הטופס).

| marketer | פיקסל |
|---|---|
| yahav (ברירת מחדל) | 2401943686950969 |
| rachel | 2599105640487498 |
| amir | 992417836756468 |
| galba (גל) | 2132624993950622 |

- **אם הקישור של המשווק משתמש ב-`aff=` ולא ב-`marketer=`,** ה-Lead נשלח לפיקסל של yahav.
- **דף פאנל 6** (two-page-funnel-1) טוען פיקסל קבוע אחר: 10211443525862398.

## 4. טריגרים (בלי הרצה; היסטוריה ורשימת תרחישים בלבד)
| תרחיש | פעיל | ריצה אחרונה |
|---|---|---|
| 6589166 Lead Journey - Ingest | כן | 14.11 22:54 UTC |
| 6589194 Lead Journey - Lookup | כן | 15.11 14:23 |
| 6672065 Email Journey - Progress Ingest | כן | אין ריצות מ-15.11 |
| 6758356 WhatsApp Cloud API - Webhook | כן | אין ריצות מ-19.11 |
| 6829358 Daily Leads Report - Send | כן | אין ריצות מ-15.11 (מופעל מהוק; לא נמצא מי קורא לו) |

- ben_welcome_v1 (תבנית וואטסאפ) לא נבדקה, כי צריך גישה ל-Meta.
- ליד בדיקה מקצה לקצה: רק אחרי "מאשר" של יהב, עם הפרטים של יהב.
