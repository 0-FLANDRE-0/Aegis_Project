from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P=Path(__file__).resolve().parent;D=P/'plots';D.mkdir(exist_ok=True)
bins=list(csv.DictReader((P/'mott-bins.csv').open()))
labels=[f"B{x['index']}" for x in bins];counts=[float(x['count']) for x in bins];masses=[float(x['massKg']) for x in bins]
fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
axes[0].bar(labels,counts);axes[0].set(title='Expected fragment count by Mott mass bin',ylabel='Expected count',xlabel='Log-mass bin')
axes[1].bar(labels,masses,color='tab:orange');axes[1].set(title='Case-mass conservation by bin',ylabel='Mass (kg)',xlabel='Log-mass bin')
for ax in axes: ax.grid(axis='y',alpha=.25)
fig.suptitle('GUN_B2B 5-inch Mott distribution: 2903.101749 fragments / 25.000000 kg')
for ext in ('png','svg'):
 fig.savefig(D/f'mott-bins.{ext}',dpi=150)
 if ext=='svg':
  p=D/f'mott-bins.{ext}';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
plt.close(fig)

rows=list(csv.DictReader((P/'unit-pk.csv').open()));fig,ax=plt.subplots(figsize=(7,4),constrained_layout=True)
for target in sorted({r['target'] for r in rows}):
 q=[r for r in rows if r['target']==target];ax.plot([float(r['distanceM']) for r in q],[float(r['pk']) for r in q],marker='o',label=target)
ax.set(title='Deterministic 5-inch fragmentation Pk unit curve',xlabel='Fragment travel distance (m)',ylabel='Pk',ylim=(0,1.03),xticks=[5,10,15,20,25]);ax.grid(alpha=.25);ax.legend()
for ext in ('png','svg'):
 fig.savefig(D/f'unit-pk.{ext}',dpi=150)
 if ext=='svg':
  p=D/f'unit-pk.{ext}';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
plt.close(fig)
