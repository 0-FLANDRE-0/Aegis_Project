from pathlib import Path
import gzip,json,math
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;q=json.loads(gzip.decompress((H/'near-vertical-results.json.gz').read_bytes()));colors={'BASE':'#d95f5f','MIN':'#e6a23c','FINAL':'#44bba4'}
fig,(a,b)=plt.subplots(2,1,figsize=(10,8),sharex=True)
for variant in colors:
 r=next(x['result']for x in q['rows']if x['variant']==variant and x['seedIndex']==1);s=r['samples'];a.plot([x['timeS']for x in s],[x['altitudeM']/1000 for x in s],label=variant,color=colors[variant],linewidth=2);ticks=r['telemetry']['ticks'];t=[];g=[]
 for tick in ticks:
  z=tick.get('pre')or tick.get('post')or{};cmd=(((z.get('chain')or{}).get('autopilot')or{}).get('command')or{});p=z.get('positionM');pip=cmd.get('pip')
  if cmd.get('gammaFDeg')is not None and p and pip:t.append(z['lifeS']);g.append(cmd['gammaFDeg'])
 b.plot(t,g,label=variant,color=colors[variant],linewidth=1.7)
a.axhline(20,color='#777',linestyle='--',linewidth=1);a.set_ylabel('Altitude (km)');a.set_title('SM-6 near-vertical seed 1 — live extracted game functions');a.grid(alpha=.25);a.legend()
b.axhline(60,color='#d95f5f',linestyle=':',linewidth=1);b.set_ylabel('Used terminal path angle (deg)');b.set_xlabel('Flight time (s)');b.grid(alpha=.25);b.legend();fig.tight_layout();fig.savefig(H/'near-vertical-path-comparison.png',dpi=170);plt.close(fig)
