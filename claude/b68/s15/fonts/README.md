Heebo (Google Fonts, Version 3.100), גופן משתנה. רישיון SIL Open Font License 1.1 (https://openfontlicense.org), מותר לארח ולצמצם.
המקור: https://raw.githubusercontent.com/google/fonts/main/ofl/heebo/Heebo%5Bwght%5D.ttf
מצומצם למשקלים 400-900 (בדפים: 400, 500, 600, 700, 800, 900) ולפי טווח תווים, לא לפי מה שיש בדף היום, כדי ששינויי קופי לא ייראו בגופן אחר:
  heebo-he.woff2 (כ-11KB, עם preload): כל האותיות העבריות, ניקוד (למשל דגש ב"חיוּת", מ-11.11), מקף, גרש וגרשיים, ספרות, פיסוק ASCII, · « » © ° ×, מקפים, מרכאות, • … ‹ ›, ₪ (הטווח: he_range.txt)
  heebo-la.woff2 (14KB, בלי preload): אותיות לטיניות (A-Z, a-z, Latin-1, Latin Extended-A)
  python3 -m fontTools.varLib.instancer "Heebo[wght].ttf" wght=400:900 -o Heebo-400-900.ttf
  python3 -m fontTools.subset Heebo-400-900.ttf --unicodes="$(cat he_range.txt)" --layout-features='kern,mark,mkmk,liga,locl,ccmp' --no-hinting --desubroutinize --flavor=woff2 --output-file=heebo-he.woff2
  python3 -m fontTools.subset Heebo-400-900.ttf --unicodes="U+0041-005A,U+0061-007A,U+00C0-00D6,U+00D8-00F6,U+00F8-017F" --layout-features='kern,liga,locl,ccmp' --no-hinting --desubroutinize --flavor=woff2 --output-file=heebo-la.woff2
הטווחים זהים ל-unicode-range ב-build_v4.py (FONT_RANGES). חצים (← → ▶) אין ב-Heebo בכלל, והם מוצגים בגופן המערכת כמו היום.
