# ב83: מדידת שלבים - section_view פעם אחת לכל שלב בביקור, עם מזהה השלב (name) ומיקומו בדף (section).
# a5v5: התגיות נכתבות בבנייה (build_v5.reorder). a5v4: אותן תגיות על הסקשנים המקבילים - תגיות מדידה בלבד, בלי שינוי תוכן.
import re

JS = r"""<script>/* ב83: section_view לכל שלב (data-stage), פעם אחת בביקור. section = מיקום השלב בדף */
(function(){var els=[].slice.call(document.querySelectorAll("[data-stage]"));if(!els.length)return;var order=[],done={};
 els.forEach(function(e){var s=e.getAttribute("data-stage");if(order.indexOf(s)<0)order.push(s);});
 function hit(s){if(done[s])return;done[s]=1;try{window.__lpSend&&window.__lpSend("section_view",{name:s,section:order.indexOf(s)+1});}catch(e){}}
 if(!("IntersectionObserver" in window)){hit(order[0]);return;}
 var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){hit(x.target.getAttribute("data-stage"));io.unobserve(x.target);}});},{rootMargin:"0px 0px -30% 0px"});
 els.forEach(function(e){io.observe(e);});
})();</script>"""

def tag(p, start, stage):
    # מוסיף data-stage לתגית הפותחת שמתחילה ב-start
    e = p.index(">", start)
    assert "data-stage=" not in p[start:e], p[start:e]
    return p[:e] + ' data-stage="%s"' % stage + p[e:]

def open_tag(p, name):
    i = p.index('data-name="%s"' % name)
    return p.rindex("<", 0, i)

A5V4 = [("פתיחה", "hook"), ("למי מתאים", "pain"), ("רגע לפני", "pain"), ("מה אם", "cause"), ("לדעת או להטמיע", "old"),
        ('<div class="v4-show"', "solution"), ("איך מתחילים", "method"), ("איך נראית המציאות", "result"), ("עם מה תצא", "result"),
        ("מה אומרים", "proof"), ("תוצאות אמיתיות", "proof"), ("למה בניתי", "proof"), ("מה יש בפנים", "course"),
        ("בונוסים", "offer"), ("ההצעה", "offer"), ("שאלות", "objections"), ('<section class="guar"', "guarantee"), ('<div class="close11"', "close")]

def tag_a5v4(p):
    for k, st in A5V4:
        if k.startswith("<"):
            assert p.count(k) == 1, k; i = p.index(k)
        else:
            assert p.count('data-name="%s"' % k) == 1, k; i = open_tag(p, k)
        p = tag(p, i, st)
    i = p.rindex("</body>"); p = p[:i] + JS + p[i:]
    return p
