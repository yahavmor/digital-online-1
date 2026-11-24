# ב121 (24.11): הסקריפטים היומיים - קוד משווק נקי: "aff=affX" ו-"aff=aff_X" נקראים X. שימוש: python3 patch_daily_b121.py <claude/daily dir>
import sys, os
d = sys.argv[1]
def patch(f, reps):
    p = os.path.join(d, f); s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) >= 1, (f, a[:60]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s); print("ok", f)
patch("aff_daily.py", [('m=re.search(r"(?:^|;)aff=([a-z0-9_-]+)",x) or re.search(r"[?&]aff=([a-z0-9_-]+)",a[8])',
                       'm=re.search(r"(?:^|;)aff=(?:aff_?(?=[a-z0-9]))?([a-z0-9_-]+)",x) or re.search(r"[?&]aff=(?:aff_?(?=[a-z0-9]))?([a-z0-9_-]+)",a[8])  # ב121: affX / aff_X = X')])
patch("daily_0811.py", [('re.search(r"(?:^|;)aff=([^;]+)",r["x"] or "") or next((re.search(r"(?:^|;)aff=([^;]+)",x["x"] or "")',
                        're.search(r"(?:^|;)aff=(?:aff_?(?=[a-z0-9]))?([^;]+)",r["x"] or "") or next((re.search(r"(?:^|;)aff=(?:aff_?(?=[a-z0-9]))?([^;]+)",x["x"] or "")')])
patch("sales7d.py", [('x = f["x"] or ""; m = re.search(r"(?:^|;)aff=([a-z0-9_-]+)", x)',
                     'x = f["x"] or ""; m = re.search(r"(?:^|;)aff=(?:aff_?(?=[a-z0-9]))?([a-z0-9_-]+)", x)  # ב121: affX / aff_X = X')])
patch("whatsells.py", [('aff=(x.get("aff") or q(r["qs"],"aff")).lower()',
                       'aff=re.sub(r"^aff_?(?=[a-z0-9])","",(x.get("aff") or q(r["qs"],"aff")).lower())  # ב121: affX / aff_X = X')])
