"""Before/after game envelope only; no real weapon performance data."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='ALL4_ENV_COMPARISON'
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
H=Path(__file__).resolve().parent;R=H.parents[2];old=json.loads((R/'docs/envelope/A/ENVELOPE_TABLE_A.json').read_text());new=json.loads((H/'ENVELOPE_TABLE_B.json').read_text());fig,axes=plt.subplots(2,2,figsize=(13,9),sharex=True,sharey=True);colors={0:'#146da0',250:'#168340',680:'#a54242',-250:'#c47714'}
for ax,weapon in zip(axes.flat,['SM2','SM2ER','SM6','ESSM']):
 for data,style,alpha in [(old,'--',.65),(new,'-',1)]:
  for speed,color in colors.items():
   rows=sorted([q for q in data['rows']if q['weapon']==weapon and q['targetSpeedMps']==speed],key=lambda q:q['altM']);ax.plot([q['altM']/1000 for q in rows],[q['maxRangeKm']for q in rows],linestyle=style,color=color,alpha=alpha,linewidth=1.6)
   clipped=[q for q in rows if q['upperCapReached']];ax.scatter([q['altM']/1000 for q in clipped],[300]*len(clipped),color=color,marker='^',s=20,alpha=alpha)
 ax.set_title(weapon);ax.grid(alpha=.25);ax.axhline(300,color='#666',linewidth=.6,linestyle=':');ax.set(xlim=(0,20),ylim=(0,312))
for ax in axes[1]:ax.set_xlabel('Target altitude MSL (km)')
for ax in axes[:,0]:ax.set_ylabel('Maximum initial firing range on 1 km grid (km)')
legend=[Line2D([0],[0],color=c,label={0:'Stationary',250:'Approach 250 m/s',680:'Approach 680 m/s',-250:'Retreat 250 m/s'}[v])for v,c in colors.items()]+[Line2D([0],[0],color='#333',linestyle='--',label='ENV_A archived'),Line2D([0],[0],color='#333',label='ENV_B cumulative'),Line2D([0],[0],color='#555',marker='^',linestyle='',label='At least 300 km (test cap)')]
fig.legend(handles=legend,ncol=4,loc='lower center',fontsize=8);fig.suptitle('Game-engine envelope comparison — not real-weapon performance');fig.tight_layout(rect=(0,.09,1,.95));fig.savefig(H/'results/envelope-before-after.svg',metadata={'Date':None});fig.savefig(H/'results/envelope-before-after.png',dpi=140)
