from pathlib import Path
import json,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;D=P/'plots';D.mkdir(exist_ok=True);old=json.loads((P.parent/'phase1a/range-table.json').read_text());new=json.loads((P/'range-table.json').read_text());fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
for ax,(ship,bearing)in zip(axes.flat,[(s,b)for s in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for b in ['0','90']]):
 a=old['profiles'][ship]['curves'][bearing];b=new['profiles'][ship]['curves'][bearing];x=[r['interceptRangeKm']for r in b];ax.plot(x,[r['meanPk']for r in a],'o--',label='B2A');ax.plot(x,[r['meanPk']for r in b],'o-',label='B2B');ax.fill_between(x,[r['p10Pk']if r['p10Pk']is not None else float('nan')for r in b],[r['p90Pk']if r['p90Pk']is not None else float('nan')for r in b],alpha=.12,color='tab:orange',label='B2B 10-90% sample spread');ax.axhline(.05,color='black',lw=.8,ls=':');ax.set(xlabel='Planned intercept range (km)',ylabel='Mean native fragmentation Pk',ylim=(-.03,1.03),title=('CG-52'if ship.startswith('CG')else'DDG-119')+' / '+bearing+' deg');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle('B2B: Mott mass bins + mass-dependent penetration\n40 identical seeds/bin; CG front1km withheld, not counted as misses')
for ext in ['png','svg']:
 fig.savefig(D/('single-shot-pk.'+ext),dpi=150)
 if ext=='svg':
  p=D/('single-shot-pk.'+ext);p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
plt.close(fig)
f=P/'evidence/g7-summary.json'
if f.exists():
 g=json.loads(f.read_text());fig,axes=plt.subplots(2,3,figsize=(14,7),constrained_layout=True)
 for row,ship in enumerate(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
  for col,key,label in[(0,'meanPre3kmAsmKills','Actual ASM kills before3km'),(1,'meanShots','Mean5in rounds'),(2,'meanHp','Mean ship HP')]:
   ax=axes[row,col]
   for source,tag,style in[(g['previousB2AOnGroups'],'B2A','--'),(g['freshGroups'],'B2B','-')]:
    for bearing,color in[(0,'tab:blue'),(90,'tab:orange')]:
     rr=sorted([r for r in source if(r['ship'],r['bearing'])==(ship,bearing)],key=lambda r:r['count']);ax.plot([r['count']for r in rr],[r[key]for r in rr],style,marker='o',color=color,label=f'{tag}/{bearing}deg')
   ax.set(title=('CG-52'if ship.startswith('CG')else'DDG-119')+' / '+label,xlabel='Incoming ASM count',xticks=[1,4]);ax.grid(alpha=.2);ax.legend(fontsize=7)
 fig.suptitle('G7 paired native comparison:120 fresh B2B vs identical120 B2A cases\n15 common seeds; AutoAA ON only; physical ASM references, no legacy counters')
 for ext in ['png','svg']:
  fig.savefig(D/('g7-comparison.'+ext),dpi=150)
  if ext=='svg':
   p=D/('g7-comparison.'+ext);p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
 plt.close(fig)
print('Plots written')
