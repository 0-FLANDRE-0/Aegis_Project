"""Presentation only: saved CSV, no game execution."""
from pathlib import Path
import os,csv,gzip
os.environ['MPLCONFIGDIR']='/tmp/aegis-sm6-rf-matplotlib'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
with gzip.open(H/'analysis/HANDOFF-NATIVE.csv.gz','rt')as f:rows=[r for r in csv.DictReader(f)if 147.75<=float(r['timeS'])<=148.2]
ts=[float(r['timeS'])for r in rows]
v=lambda key:[float(r[key])if r[key]else float('nan')for r in rows]
fig,axs=plt.subplots(3,1,figsize=(9,8),sharex=True)
axs[0].plot(ts,v('arhVelocityErrorRawMps'),label='ARH receiver velocity error (raw frame)',color='#bc6658')
axs[0].plot(ts,v('velocityErrorMps'),label='Consumed relative velocity error',color='#376e96',ls='--')
axs[0].set_ylabel('Velocity error (m/s)');axs[0].legend(fontsize=8)
axs[1].plot(ts,v('rawG'),label='Raw demanded G',color='#376e96');axs[1].plot(ts,v('actualNormalG'),label='Actual normal G',color='#31836b');axs[1].set_ylabel('G');axs[1].legend(fontsize=8)
axs[2].plot(ts,v('dragManeuverN'),color='#884e93');axs[2].axhline(100,color='#999999',ls=':',label='100N diagnostic reference');axs[2].set_ylabel('Native maneuver drag (N)');axs[2].legend(fontsize=8)
for ax in axs:ax.axvline(147.95,color='#333333',ls='--');ax.grid(alpha=.25)
axs[-1].set_xlabel('Life (s); dashed vertical line = ARH source adoption 147.950s')
fig.suptitle('HANDOFF onset: receiver error precedes adoption / control response')
fig.tight_layout()
for ext in ['png','svg']:fig.savefig(H/'analysis/plots'/('handoff-onset.'+ext),dpi=150)
