# ב86 - גל לפני ואחרי ("מאשר ב86 - גל", ראשי 13.11): לפי היסטוריית הפעילות, הקבוצה הישנה "Cold IL 25-55 | gal" כובתה ב-11.11 07:52, וסדרת ה-IC פעילה מ-10.11 09:16.
#  - "לפני": עד 10.11 09:16. הוצאה aff_gal (כל הימים, כולל ההוצאה של הקבוצה הישנה ב-10.11 וב-11.11).
#  - "חפיפה": 10.11 09:16 עד 11.11 07:52, שורה נפרדת עם הערה. בלי הוצאה משלה - ההוצאה נשארת בשורות "לפני" ו"אחרי".
#  - "אחרי": מ-11.11 07:52. הוצאה aff_gal_ic מ-10.11 (כל ההוצאה של הסדרה).
#  aff_gal_ic כבר לא נספרת בשורת "לפני" של גל (מבטל את הכלל הזמני מ-12.11).
# שימוש: python3 patch_gal.py <dashboard.html> <out>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf8").read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new, 1)

rep('''{code:"gal",lbl:"גל",aud:"קהל קר",copy:"p25_brain_c3",budget:40,from:"2026-11-09T21:00:00",day0:"2026-11-09",sw:null},''',
    '''{code:"gal",lbl:"גל",aud:"קהל קר",copy:"p25_brain_c3",budget:40,from:"2026-11-09T21:00:00",day0:"2026-11-09",sw:"2026-11-11T07:52:00",ovl:"2026-11-10T09:16:00",
  ovlNote:"שתי הקבוצות רצו יחד (סדרת IC מ-10.11 09:16, הישנה כובתה 11.11 07:52). הכניסות כאן לא נספרות ב\\"לפני\\" ולא ב\\"אחרי\\", וההוצאה נשארת בשורות שלהן (aff_gal, aff_gal_ic). לפי utm_term, כל הכניסות בחלון הזה הגיעו מהסדרה החדשה"},''')
rep('''גל: השעה תימסר (sw:null = עדיין לפני).''',
    '''גל (ב86, 13.11): הישנה כובתה 11.11 07:52 וה-IC פעילה מ-10.11 09:16 - "אחרי" מ-11.11 07:52, והחפיפה בשורה נפרדת (ovl) בלי הוצאה משלה.''')
rep(''' AUD.seg.push(pre);if(swT)AUD.seg.push(Object.assign({},c,c.post||{},{key:c.code+"|post",ph:"post",phl:"אחרי · מעבר לתשלום",fromT:swT,toT:null,spk:"aff_"+c.code+"_ic",sday:dayKey(swT)}))});''',
    ''' const ovT=c.ovl?new Date(c.ovl):null;if(ovT)pre.toT=ovT;
 AUD.seg.push(pre);if(ovT&&swT)AUD.seg.push(Object.assign({},c,{key:c.code+"|ovl",ph:"ovl",phl:"חפיפה · שתי הקבוצות",fromT:ovT,toT:swT,spk:null,nospend:true,note:c.ovlNote||""}));
 if(swT)AUD.seg.push(Object.assign({},c,c.post||{},{key:c.code+"|post",ph:"post",phl:"אחרי · מעבר לתשלום",fromT:swT,toT:null,spk:"aff_"+c.code+"_ic",sday:dayKey(ovT||swT)}))});''')
# הכלל הזמני מ-12.11 (gal_ic בשורת "לפני") מבוטל
rep('''{key:"gal|pre",spk:"aff_gal_ic",lbl:"גל",phl:"סדרת IC (מעבר לתשלום)",aud:"נספרת בשורה של גל עד שתימסר שעת המעבר"},''', '')
# חפיפה: בלי הוצאה, עם הערה; תווית זמן; לא בטופס
rep('''function audSpend(g){''', '''function audSpend(g){if(g.nospend)return null;''')
rep('''const per=o=>o.c.ph==="post"?'מ-'+hm2(o.c.fromT):''', '''const per=o=>o.c.ph==="ovl"?hm2(o.c.fromT)+' עד '+hm2(o.c.toT):o.c.ph==="post"?'מ-'+hm2(o.c.fromT):''')
rep('''L.map(o=>'<tr><td>'+nm(o)+'</td><td>'+cpCell(o)+'</td><td>'+(o.sp?''', '''L.map(o=>'<tr><td>'+nm(o)+'</td><td>'+cpCell(o)+'</td><td>'+(o.c.ph==="ovl"?'<small>'+esc(o.c.note)+'</small>':o.sp?''')
rep('''OPT=AUD.seg.concat(AUD_X,AUD_ADS);''', '''OPT=AUD.seg.filter(g=>g.spk).concat(AUD_X,AUD_ADS);''')
open(out, "w", encoding="utf8").write(s)
print("ok", len(s))
