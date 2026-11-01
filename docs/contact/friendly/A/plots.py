from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;F=P/'figures';F.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,3,figsize=(13,3.6),layout='constrained')
for i,title in enumerate(['Helicopter hover','Helicopter route','Harpoon turning route']):
 ax=axes[i]
 for tag,color in [('before','#be3535'),('after','#007f8b')]:
  d=json.loads((P/f'evidence/{tag}-{i}.json').read_text());ax.step([s['timeS']for s in d['samples']],[len(s['tracks'])for s in d['samples']],where='post',label=tag,color=color)
 ax.set(title=title,xlabel='Simulation time (s)',ylabel='Radar track files');ax.grid(alpha=.2);ax.legend()
fig.savefig(F/'track-counts.svg');plt.close(fig)
rows=json.loads((P/'analysis/ciws30.json').read_text())['rows'];fig,ax=plt.subplots(figsize=(12,3.6),layout='constrained');x=list(range(30));ax.bar([i-.18 for i in x],[r['beforeHp']for r in rows],.36,label='before',color='#b65050');ax.bar([i+.18 for i in x],[r['afterHp']for r in rows],.36,label='after',color='#007f8b');ax.set(xticks=x,xticklabels=[str(r['seed'])[-3:]for r in rows],xlabel='Seed suffix (419xxx)',ylabel='Ship HP after engagement',title='Native CIWS defense: 30 fixed-seed engagements');ax.legend();fig.savefig(F/'ciws30-hp.svg');plt.close(fig)
