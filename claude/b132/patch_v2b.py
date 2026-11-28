#!/usr/bin/env python3
# ב132 חלק ב: הטקסטים המאושרים (מסמך "טקסטים מאושרים לבנייה - גרסה 2 וב135", 28.11, בן אישר). רץ על התוצאה של patch_v2.py.
# usage: patch_v2b.py <a5s2 skeleton> <out>
import sys
src = open(sys.argv[1], encoding="utf8").read()
def rep(old, new, cnt=1):
    global src
    assert src.count(old) == cnt, ("anchor", old[:60], src.count(old))
    src = src.replace(old, new)
# תיבת ההסכמה (א34)
rep('<span data-v2text="consent">אני מסכים/ה שבן ישלח לי מיילים והודעות וואטסאפ עם תוכן והצעות. לא חובה לרכישה, ואפשר להסיר בכל רגע.</span>',
    '<span data-v2text="consent">אני מאשר/ת לקבל מבן נחום תוכן שיווקי והצעות במייל ובוואטסאפ. אפשר להסיר בכל רגע.</span>', 2)
# מתחת לכפתור: אחריות (נוסח ב), שורת התשלום, התקנון כשורת טקסט
rep('<p class="lpf-guar" data-v2text="guar">7 ימי אחריות עם החזר מלא<span>בלחיצה על הכפתור את/ה מאשר/ת את <a href="terms.html" target="_blank" rel="noopener">התקנון</a> ו<a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a>.</span></p>',
    '<p class="lpf-guar" data-v2text="guar">החזר מלא תוך 7 ימים. בלי ויכוחים ובלי אותיות קטנות.<span>תשלום מאובטח · אפשר לשלם ב-<bdi>Apple Pay</bdi>, <bdi>Google Pay</bdi>, ביט או אשראי · החזר מלא תוך 7 ימים</span><span>בלחיצה על הכפתור אני מאשר/ת את <a href="terms.html" target="_blank" rel="noopener">התקנון</a> ואת <a href="privacy.html" target="_blank" rel="noopener">מדיניות הפרטיות</a>.</span></p>', 2)
# שאלות ותשובות (6)
rep('<details><summary>כבר קראתי ספרים או עשיתי קורסים. זה עדיין רלוונטי בשבילי?</summary><div class="a"><p>כן. המטרה היא לא רק לתת עוד ידע, אלא לעזור לך לקחת את הדברים שאתה אולי כבר יודע, ולהתחיל לזהות וליישם אותם בתוך החיים עצמם.</p></div></details>',
    '<details><summary>זה באמת עובד?</summary><div class="a"><p>לא עוד ידע שנשאר בראש. כל סרטון קצר נותן לך כלי אחד, פרקטי וממשי, שאתה יכול להתחיל להטמיע כבר בסיום הצפייה. מאחורי השיטה 15+ שנות ניסיון ב-NLP ומאות אנשים בליווי אישי, ולמטה תלמידים מספרים במילים שלהם מה השתנה אצלם.</p></div></details>'
    '<details><summary>כבר קראתי ספרים ועשיתי קורסים, וזה לא החזיק. מה שונה כאן?</summary><div class="a"><p>הבעיה היא לא מה שאתה יודע. הבעיה היא מה שאתה עושה באופן אוטומטי. כשצורכים ידע ולא מטמיעים אותו, שום דבר לא זז. לכן כאן לא צוברים ידע, מתרגלים: עוגנים קטנים שמתחברים לפעולות שאתה כבר עושה בכל יום.</p></div></details>'
    '<details><summary>אין לי זמן.</summary><div class="a"><p>צופים 5-10 דקות ביום ומיישמים כלי אחד, בתוך השגרה שכבר יש לך. בלי להוסיף שעות ליום שלך.</p></div></details>')
rep('<details><summary>צריך לראות את כל 90 השיעורים?</summary><div class="a"><p>לא. זו ספריית כלים. מתחילים בחלק 1, ומשם נכנסים לפי הנושא שאתה עובד עליו עכשיו.</p></div></details>',
    '<details><summary>עוד קורס שלא אסיים?</summary><div class="a"><p>לא צריך לראות את כל 90 השיעורים. זו ספריית כלים: מתחילים בחלק 1, ומשם נכנסים לפי הנושא שאתה עובד עליו עכשיו. המטרה היא לא שתסיים עוד קורס ותדע יותר. המטרה היא שהחיים שלך ימשיכו לאמן אותך גם הרבה אחרי שסיימת ללמוד.</p></div></details>'
    '<details><summary>זו עוד "חשיבה חיובית"?</summary><div class="a"><p>לא רק לומדים לחשוב חיובי. יוצרים עוגנים בתוך פעולות שאתה כבר עושה בכל יום, שמאפשרים לך לצאת לרגע מהחשיבה האוטומטית, לבחור מחשבה חדשה ולתרגל אותה שוב ושוב.</p></div></details>')
rep('<details><summary>מה בדיוק כוללת האחריות?</summary><div class="a"><p>יש לך 7 ימים. אם עברת על התוכן, נתת לו הזדמנות אמיתית והרגשת שהוא לא בשבילך, שולחים לנו מייל ומקבלים החזר מלא.</p></div></details>',
    '<details><summary>ומה אם זה לא בשבילי?</summary><div class="a"><p>יש לך 7 ימים. אם עברת על התוכן, נתת לו הזדמנות אמיתית והרגשת שהוא לא בשבילך, שולחים לנו מייל ומקבלים החזר מלא. בלי ויכוחים ובלי אותיות קטנות.</p></div></details>')
# עדויות ליד ההצעה (טקסט בלבד, שם פרטי), אחרי הטופס הראשון ולפני הלוגואים
rep('</form>\n<div class="paylogos" data-paylogos="offer">',
    '</form>\n<div class="v2-quotes" aria-label="מה אומרים תלמידים"><blockquote>"זה ממש פשוט וממש מורגש השינוי"<cite>צילה</cite></blockquote><blockquote>"אני ממש מרגיש שאני יותר שם לב למחשבות שלי ויותר שולט בהם"<cite>גלעד</cite></blockquote><blockquote>"בול מה שהייתי צריך כלים פרקטיים"<cite>דורון</cite></blockquote><p class="v2-q2">"תמיד הייתי נתקעת איפשהו... אני באמת יכולה לתת ערך ולהשפיע על אנשים."<cite>תלמידה בקורס</cite></p></div>\n<div class="paylogos" data-paylogos="offer">')
rep('.v2-slot p{font-size:13.5px;color:var(--ink2,#ccc);text-align:center;margin:6px 0 0}\n',
    '.v2-slot p{font-size:13.5px;color:var(--ink2,#ccc);text-align:center;margin:6px 0 0}\n'
    '.v2-quotes{margin:14px 0 0;display:grid;gap:8px}.v2-quotes blockquote{margin:0;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(254,207,0,.18);font-size:15px;line-height:1.5;color:var(--ink,#fff)}.v2-quotes cite{display:block;font-style:normal;font-size:12.5px;color:#FECF00;margin-top:4px}.v2-quotes .v2-q2{margin:0;font-size:13.5px;color:var(--ink2,#ccc);line-height:1.5}.v2-quotes .v2-q2 cite{display:inline;font-style:normal;color:var(--ink2,#ccc)}\n')
open(sys.argv[2], "w", encoding="utf8").write(src); print("ok texts", len(src))
