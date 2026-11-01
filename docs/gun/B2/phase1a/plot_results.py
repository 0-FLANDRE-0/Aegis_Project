from pathlib import Path
import json,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;D=P/'plots';D.mkdir(exist_ok=True);old=json.loads((P.parent/'phase1/range-table.json').read_text());new=json.loads((P/'range-table.json').read_text());fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
for ax,(ship,bearing)in zip(axes.flat,[(s,b)for s in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for b in ['0','90']]):
 a=old['profiles'][ship]['curves'][bearing];b=new['profiles'][ship]['curves'][bearing];x=[r['interceptRangeKm']for r in b];ax.plot(x,[r['meanPk']for r in a],'o--',label='B2 historical');ax.plot(x,[r['meanPk']for r in b],'o-',label='B2A measured');ax.fill_between(x,[r['p10Pk']if r['p10Pk']is not None else float('nan')for r in b],[r['p90Pk']if r['p90Pk']is not None else float('nan')for r in b],alpha=.12,color='tab:orange',label='B2A 10-90% sample spread');ax.axhline(.05,color='black',lw=.8,ls=':');ax.set(xlabel='Planned intercept range (km)',ylabel='Mean native fragmentation Pk',ylim=(-.03,1.03),title=('CG-52'if ship.startswith('CG')else'DDG-119')+' / '+bearing+' deg');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle('B2A: fixed fuze-warhead matching + symmetric mechanical window + isotropic angular dispersion\n40 identical seeds/bin; CG front1km withheld, not counted as misses')
for ext in ['png','svg']:fig.savefig(D/('single-shot-pk.'+ext),dpi=150)
plt.close(fig)
a=json.loads((P.parent/'phase1/evidence/dispersion-final/validation.json').read_text());b=json.loads((P/'evidence/dispersion/validation.json').read_text());fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
for ax,key,title in[(axes[0],'rangeM','16459m range dispersion'),(axes[1],'crossM','Cross-range angular dispersion')]:
 for q,label in[(a,'B2'),(b,'B2A')]:
  values=[r[key]for r in q['data']['samples']];center=16459 if key=='rangeM'else 0;ax.hist([x-center for x in values],bins=30,alpha=.45,label=f'{label}: sigma={statistics.pstdev(values):.4f}m')
 ax.set(title=title,xlabel='Offset (m)',ylabel='Count');ax.legend();ax.grid(alpha=.2)
for ext in ['png','svg']:fig.savefig(D/('dispersion-anchor.'+ext),dpi=150)
plt.close(fig)
f=P/'evidence/g7-summary.json'
if f.exists():
 g=json.loads(f.read_text());fig,axes=plt.subplots(2,3,figsize=(14,7),constrained_layout=True)
 for row,ship in enumerate(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
  for col,key,label in[(0,'meanPre3kmAsmKills','Actual ASM kills before3km'),(1,'meanShots','Mean5in rounds'),(2,'meanHp','Mean ship HP')]:
   ax=axes[row,col]
   for source,tag,style in[(g['previousB2OnGroups'],'B2 ON historical','--'),(g['freshGroups'],'B2A ON','-')]:
    for bearing,color in[(0,'tab:blue'),(90,'tab:orange')]:
     rr=sorted([r for r in source if(r['ship'],r['bearing'])==(ship,bearing)],key=lambda r:r['count']);ax.plot([r['count']for r in rr],[r[key]for r in rr],style,marker='o',color=color,label=f'{tag}/{bearing}deg')
   ax.set(title=('CG-52'if ship.startswith('CG')else'DDG-119')+' / '+label,xlabel='Incoming ASM count',xticks=[1,4]);ax.grid(alpha=.2);ax.legend(fontsize=7)
 fig.suptitle('G7 paired native comparison:120 fresh B2A vs identical120 B2 cases\n15 common seeds; AutoAA ON only; physical ASM references, no legacy counters')
 for ext in ['png','svg']:fig.savefig(D/('g7-comparison.'+ext),dpi=150)
 plt.close(fig)
print('Plots written')
