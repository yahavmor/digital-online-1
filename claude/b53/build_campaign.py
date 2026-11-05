# ב53: builds nlp/campaign.html from campaign.src.html + the data logic of nlp/dashboard.html (same rules, same names)
import re,os
R=os.path.dirname(os.path.abspath(__file__))+'/../../nlp/'
d=open(R+'dashboard.html',encoding='utf8').read()
def blk(start,end):
    i=d.index(start); j=d.index(end,i); return d[i:j]
CORE=blk('const COLS=','/* spend for a period */')
NAMES=blk('const VIDEO_NAMES=','function crLabel')
LABB=blk('const LAB=','function renderLab')
src=open(os.path.dirname(os.path.abspath(__file__))+'/campaign.src.html',encoding='utf8').read()
for k,v in dict(CORE=CORE,NAMES=NAMES,LAB=LABB).items():
    assert '/*{{'+k+'}}*/' in src,k; src=src.replace('/*{{'+k+'}}*/',v)
open(R+'campaign.html','w',encoding='utf8').write(src); print('ok',len(src))
