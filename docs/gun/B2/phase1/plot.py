from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;O=P/'plots';O.mkdir(exist_ok=True)
q=json.loads((P/'range-table.json').read_text());fig,axs=plt.subplots(2,2,figsize=(12,7.2),sharex=True,sharey=True)
for i,(ship,p)in enumerate(sorted(q['profiles'].items())):
 for j,b in enumerate(['0','90']):
  ax=axs[i,j];rows=p['curves'][b];x=[r['interceptRangeKm']for r in rows];mean=[r['meanPk']if r['meanPk']is not None else math.nan for r in rows];ax.fill_between(x,[r['p10Pk']if r['p10Pk']is not None else math.nan for r in rows],[r['p90Pk']if r['p90Pk']is not None else math.nan for r in rows],color='#2d7fb8',alpha=.2,label='10 / 90 percentile');ax.plot(x,mean,'o-',color='#176c9c',label='Mean native Pk');ax.axhline(.05,color='#bc6428',linestyle='--',label='0.05 threshold');ax.set_title(('CG-52'if ship.startswith('CG')else'DDG-119')+' / bearing '+b+' deg');ax.set_ylim(-.03,1.03);ax.set_xticks(range(1,10));ax.grid(alpha=.2)
  if i==1:ax.set_xlabel('Planned intercept distance (km)')
  if j==0:ax.set_ylabel('Single-shot native fragmentation Pk')
  if any(r['nativeReleases']==0 for r in rows):ax.annotate('1 km: native MOUNT_OCCLUDED; 0 releases',(1,.03),xytext=(1.2,.24),arrowprops={'arrowstyle':'->','color':'#777'},fontsize=8)
axs[0,1].legend(fontsize=8,loc='upper left');fig.suptitle('GUN_B2 | 40 seeds / bin | Ideal received track, Kh-35U 10 m / 280 m/s\nMeasured curve only; no coefficient fitted to hit rate. Outer threshold right-censored at 9 km.',fontsize=11);fig.tight_layout()
for suffix in ['png','svg']:fig.savefig(O/('single-shot-pk.'+suffix),dpi=160)
plt.close(fig)
a=json.loads((P/'evidence/dispersion-final/validation.json').read_text());samples=a['data']['samples'];fig,axs=plt.subplots(1,2,figsize=(11,3.8));axs[0].hist([r['rangeM']-16459 for r in samples],bins=26,color='#286d91',alpha=.8);axs[0].set_title('16,459 m anchor: range sigma = %.2f m'%a['rangeSigmaM']);axs[0].set_xlabel('Range error from anchor (m)');axs[0].set_ylabel('Shots');axs[1].hist([r['crossM']for r in samples],bins=26,color='#3c9472',alpha=.8);axs[1].set_title('Cross-range sigma = %.2f m'%a['crossSigmaM']);axs[1].set_xlabel('Cross-range deviation (m)');fig.suptitle('400 independent validation shots | actual spawn / native acceleration | no global RNG draws');fig.tight_layout()
for suffix in ['png','svg']:fig.savefig(O/('dispersion-anchor.'+suffix),dpi=160)
plt.close(fig)
