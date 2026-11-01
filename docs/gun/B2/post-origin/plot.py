from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;q=json.loads((P/'evidence/summary.json').read_text());assert q['pass'];groups=q['groups'];out=P/'plots';out.mkdir(exist_ok=True)
plt.rcParams.update({'svg.fonttype':'none','font.size':9})
fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
labels=[('DDG'if g['ship'].startswith('DDG')else'CG')+' '+str(g['bearing'])+' deg'for g in groups]
for ax,metric,title in [(axes[0,0],'observationPosition.cross','Observed position error: horizontal cross'),(axes[0,1],'cpaResolvedLiveTarget.cross','CPA error: horizontal cross'),(axes[1,1],'solutionAgeS','Release solution age')]:
 for tag,dx,color in [('before',-.10,'#b86a2a'),('after',.10,'#17858f')]:
  m=[g[tag]['metrics'][metric]for g in groups];ax.errorbar([i+dx for i in range(4)],[x['mean']for x in m],yerr=[x['sigma']for x in m],fmt='o',capsize=4,color=color,label=tag)
 ax.set_title(title);ax.set_xticks(range(4),labels);ax.set_ylabel('seconds'if metric=='solutionAgeS'else'meters');ax.axhline(0,color='#888',linewidth=.7);ax.grid(axis='y',alpha=.2)
ax=axes[1,0]
for tag,dx,color in [('before',-.17,'#b86a2a'),('after',.17,'#17858f')]:ax.bar([i+dx for i in range(4)],[100*(g[tag]['etFractionResolved']or 0)for g in groups],width=.32,color=color,label=tag)
ax.set_title('ET share among resolved bursts (not miss rate)');ax.set_ylabel('percent');ax.set_xticks(range(4),labels);ax.grid(axis='y',alpha=.2)
axes[0,0].legend();fig.suptitle('GUN B2 post-origin: 15 fixed seeds/group; same native game scenario\nError bars = shot-population standard deviation; populations may differ',fontsize=11)
fig.savefig(out/'comparison.svg');fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
svg=out/'comparison.svg';svg.write_text('\n'.join(line.rstrip()for line in svg.read_text().splitlines())+'\n')
print('comparison.svg/png written')
