from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent;O=P/'plots';O.mkdir(exist_ok=True);q=json.loads((P/'evidence/effects-summary.json').read_text());assert q['complete'];groups=q['groups'];fig,axes=plt.subplots(2,4,figsize=(15,7))
fields=[('meanPre3kmAsmKills','Actual ASM kills before 3 km'),('meanShots','5in rounds fired'),('meanCiwsUsed','CIWS rounds used'),('meanHpAfter','Own ship HP after trial')]
for i,ship in enumerate(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
 for j,(key,title)in enumerate(fields):
  ax=axes[i,j]
  for bearing,color in [(0,'#1a709c'),(90,'#c26a2c')]:
   for on,style in [(False,'--'),(True,'-')]:
    rr=sorted((r for r in groups if(r['ship'],r['bearing'],r['autoAA'])==(ship,bearing,on)),key=lambda r:r['count']);ax.plot([r['count']for r in rr],[r[key]for r in rr],style,marker='o',color=color,label=f'{bearing} deg / AutoAA '+('ON'if on else'OFF'))
  ax.set_title(('DDG-119'if i==0 else'CG-52')+' / '+title,fontsize=10);ax.set_xticks([1,2,3,4]);ax.grid(alpha=.2);ax.set_xlabel('Incoming Kh-35U count')
  if key=='meanHpAfter':ax.set_ylim(0,103)
  elif key=='meanPre3kmAsmKills':ax.set_ylim(bottom=-.05)
axes[0,0].legend(fontsize=7);fig.suptitle('GUN_B2 final native 960 trials | 30 common seeds per group\nAll B2 features ON; dashed/solid toggles AutoAA only. Physical ASM evidence, never legacy counters.',fontsize=11);fig.tight_layout()
for ext in ['png','svg']:fig.savefig(O/('g7-effects.'+ext),dpi=160)
plt.close(fig)
