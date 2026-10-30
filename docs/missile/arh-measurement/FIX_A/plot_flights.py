"""Plot the frozen 240 km N/A/U/AU terminal comparison."""
from pathlib import Path
import csv
import matplotlib.pyplot as plt

H=Path(__file__).resolve().parent
rows=[]
with (H/'flight-timeseries.csv').open() as f:
    for r in csv.DictReader(f):
        r={k:(float(v) if k not in {'variant','mode','source'} and v else v) for k,v in r.items()}
        rows.append(r)

colors={'N':'#d62728','A':'#ff7f0e','U':'#1f77b4','AU':'#2ca02c'}
fields=[
    ('rawVelErrorMps','Raw observed velocity error (m/s)'),
    ('selectedVelErrorMps','Guidance-consumed velocity error (m/s)'),
    ('commandG','Command magnitude (g)'),
    ('maneuverDragN','Maneuver drag (N)'),
]
fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
for ax,(field,label) in zip(axes.flat,fields):
    for variant in ['N','A','U','AU']:
        rr=[r for r in rows if r['variant']==variant and r[field]!='']
        ax.plot([r['timeS'] for r in rr],[r[field] for r in rr],label=variant,color=colors[variant],linewidth=1.15)
    ax.set_ylabel(label);ax.grid(True,alpha=.25);ax.set_xlim(145,164)
for ax in axes[-1]:ax.set_xlabel('Flight time (s)')
axes[0,0].legend(ncol=4,loc='upper left')
fig.suptitle('SM-6 240 km / 5 km / inbound 250 m/s / seed 12001')
fig.tight_layout()
fig.savefig(H/'sm6-240km-naau.png',dpi=160)
