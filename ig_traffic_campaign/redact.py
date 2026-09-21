# -*- coding: utf-8 -*-
"""
מנקה access_token מתגובות API לפני הדפסה - Meta כוללת את הטוקן בתוך URLs של
עימוד (paging.next/previous) בגוף התשובה עצמו, אז גם הדפסת JSON "תמים" חושפת
אותו במלואו בטרמינל (קרה בפועל פעמיים בפרויקט הזה). כל סקריפט debug/check
שמדפיס תגובת API גולמית צריך לעבור דרך redact() קודם.
"""

import re

_TOKEN_PARAM_RE = re.compile(r"([?&]access_token=)[^&\s\"]+")


def redact(obj):
    """מחזיר עותק של obj (dict/list/str/כל דבר אחר) עם access_token=... מוחלף ב-REDACTED."""
    if isinstance(obj, dict):
        return {k: redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    if isinstance(obj, str):
        return _TOKEN_PARAM_RE.sub(r"\1REDACTED", obj)
    return obj
