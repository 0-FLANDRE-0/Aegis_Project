"""Standalone SVG/PNG figures from the actual Phase0 shot logs. No model fit."""
from pathlib import Path
import collections,json,math,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/aegis-gun-b2/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
B=Path(__file__).resolve().parent;E=B/'evidence';P=B/'plots';P.mkdir(exist_ok=True)
rows=[]
for f in(E/'trials').glob('worker*.jsonl'):
 for line in f.read_text().splitlines():
  try:rows.append(json.loads(line))
  except ValueError:pass
corrected=[json.loads(line)for f in(E/'a-stop-corrected').glob('worker*.jsonl')for line in f.read_text().splitlines()]
replacement={r['caseId']:r for r in corrected}
assert len(corrected)==len(replacement)==480 and set(replacement)=={r['caseId']for r in rows if r['experiment']=='A'},'A_CORRECTION_INCOMPLETE'
rows=[replacement[r['caseId']]if r['experiment']=='A'else r for r in rows]
ex=['BASE','A','B','C','D'];colors={'BASE':'#455a64','A':'#1976d2','B':'#2e7d32','C':'#8e24aa','D':'#ef6c00'}
plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.2,'svg.fonttype':'none'})
def shots(e,b,ship=None):return[s for r in rows if r['experiment']==e and r['bearing']==b and(ship is None or r['ship']==ship)for s in r['data']['shots']]
def save(fig,name):
 fig.tight_layout();svg=P/(name+'.svg');fig.savefig(svg)
 svg.write_text('\n'.join(line.rstrip(' \t')for line in svg.read_text().splitlines())+'\n')
 fig.savefig(P/(name+'.png'),dpi=160);plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(11,7.5))
for bi,b in enumerate([0,90]):
 for ei,e in enumerate(ex):
  ss=shots(e,b);a=sorted(s['assignedArrivalDiagnostic']['arrivalMissM']for s in ss if s.get('burst')and s.get('assignedTargetAliveBeforeBurst'))
  if a:axs[0,bi].step(a,np.arange(1,len(a)+1)/len(a),where='post',label=e,color=colors[e])
  bursts=[s for s in ss if s.get('burst')];n=len(bursts);et=sum(s['outcome']=='MFF_ET_BACKUP'for s in bursts);live=sum(s['outcome']=='LIVE_AT_SCENARIO_END'for s in ss)
  if n:axs[1,bi].bar(ei-.17,et/n,width=.32,color=colors[e])
  else:axs[1,bi].text(ei-.17,.025,'N/A',ha='center',rotation=90,fontsize=7)
  if ss:axs[1,bi].bar(ei+.17,live/len(ss),width=.32,color=colors[e],alpha=.3,hatch='//')
  else:axs[1,bi].text(ei+.17,.025,'N/A',ha='center',rotation=90,fontsize=7)
 axs[0,bi].set(xscale='symlog',xlabel='Assigned-target fragment arrival miss (m)',ylabel='ECDF',title=f'Bearing {b} deg; target alive before burst');axs[0,bi].legend(fontsize=8)
 axs[1,bi].set(xticks=range(5),xticklabels=ex,ylim=(0,1),ylabel='Fraction',title='Solid: ET / bursts. Hatched: live-at-end / shots.')
save(fig,'arrival-and-outcomes')
fig,axs=plt.subplots(2,2,figsize=(11,7.5))
for si,ship in enumerate(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
 for bi,b in enumerate([0,90]):
  ax=axs[si,bi]
  for e in ex:
   ss=[s for s in shots(e,b,ship)if s['cpa']and s.get('burst')and s.get('assignedTargetAliveBeforeBurst')];ax.scatter([s['cpa']['resolvedM']['cross']for s in ss],[s['cpa']['resolvedM']['vertical']for s in ss],s=6,alpha=.3,c=colors[e],label=e)
  ax.set_xscale('symlog',linthresh=10);ax.set_yscale('symlog',linthresh=10);ax.set(xlabel='Horizontal transverse CPA projection (m)',ylabel='World-Z CPA projection (m)',title=f'{ship[:3]} / {b} deg, complete live-target flights');ax.legend(markerscale=2,fontsize=7)
save(fig,'cpa-projections')
fig,axs=plt.subplots(1,2,figsize=(11,4.5))
for bi,b in enumerate([0,90]):
 ax=axs[bi]
 for i,e in enumerate(ex):
  ss=[s for s in shots(e,b)if s['outcome']=='MFF_ET_BACKUP'and s.get('burst')];a=[math.hypot(s['burst']['positionM']['x']-s['trunnionM']['x'],s['burst']['positionM']['y']-s['trunnionM']['y'])/1000 for s in ss]
  if a:ax.boxplot([a],positions=[i],widths=.5,showfliers=True,patch_artist=True,boxprops={'facecolor':colors[e],'alpha':.5},medianprops={'color':'black'},flierprops={'markersize':2,'alpha':.3})
 ax.set(xticks=range(5),xticklabels=ex,xlim=(-.7,4.7),ylabel='ET burst horizontal distance from launch trunnion (km)',title=f'Bearing {b} deg; includes bursts after target loss')
save(fig,'et-distance')
print(json.dumps({'cases':len(rows),'figures':[p.name for p in P.glob('*.svg')]}))
