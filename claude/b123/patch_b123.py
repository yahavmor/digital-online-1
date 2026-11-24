# ב123 (24.11): קרלין (marketer=karlen) במשפך הלידים.
#  1. marketers/marketers.json: הפיקסל של karlen -> 1653243919627695 (pixels.js טוען אותו לפי marketer=, ואירוע Lead נשלח אליו בשליחת הטופס, כמו rachel ו-galba).
#  2. claude/b119/agg.js (הקוד של מודול 9 ב-8745278): karlen / karlin / קרלין -> "karlen" במקום "other".
#  3. dashboard.html (דשבורד הלידים של בן): כרטיס "קרלין".
# שימוש: python3 patch_b123.py <marketers.json in> <out> | agg <in> <out> | dash <in> <out>
import sys, json, re
what, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new, 1)
if what == "json":
    j = json.loads(s)
    assert j["karlen"]["fb_pixel"] == "1394111825895083", j["karlen"]
    rep('"karlen": {\n    "lm_supplier": 43121,\n    "fb_pixel": "1394111825895083"', '"karlen": {\n    "lm_supplier": 43121,\n    "fb_pixel": "1653243919627695"')
    j2 = json.loads(s); assert j2["karlen"]["fb_pixel"] == "1653243919627695" and {k: v for k, v in j2.items() if k != "karlen"} == {k: v for k, v in j.items() if k != "karlen"}
elif what == "agg":
    rep('if (m === "galba" || m === "gal" || m === "גל") return "gal"; return "other"; };',
        'if (m === "galba" || m === "gal" || m === "גל") return "gal";\n  if (m === "karlen" || m === "karlin" || m === "קרלין") return "karlen"; /* ב123 */ return "other"; };')
elif what == "dash":
    rep('var MK=[["rachel","רחל"],["amir","אמיר"],["gal","גל"]];', 'var MK=[["rachel","רחל"],["amir","אמיר"],["gal","גל"],["karlen","קרלין"]]; /* ב123: קרלין */')
else: raise SystemExit("what?")
open(out, "w", encoding="utf8").write(s); print("ok", what, out)
