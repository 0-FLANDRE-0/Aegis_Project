"""Render existing saturation JSON only; no game, test rerun or browser.

Every CSV row names and hashes its original JSON. The baseline has28 cases;
the candidate has32 (four explicit129/257 bound cases have no measured B row).
No cross-family mean or invented per-call sample is constructed.
"""
from pathlib import Path
import csv,hashlib,json,os

os.environ.setdefault('MPLCONFIGDIR','/dev/shm/aegis-track-saturation-mpl')
os.environ.setdefault('TMPDIR','/dev/shm')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.patches import Rectangle
from matplotlib.ticker import PercentFormatter

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';OUT=E/'figures'
sha=lambda data:hashlib.sha256(data).hexdigest()

def read(name):
 path=E/name;raw=path.read_bytes();return json.loads(raw),{'source_json':str(path.relative_to(R)),'source_json_sha256':sha(raw)}

def write_csv(path,rows):
 keys=list(rows[0])
 with path.open('w',newline='')as stream:
  writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows(rows)

FAMILIES=[
 ('sparse_chain_clear','Clear sparse chain'),
 ('dense_equal','Equal dense · intended HOLD'),
 ('dense_diagonal_clear','Clear diagonal · dense'),
 ('covariance_quality_gap','Covariance gap · native NIS'),
 ('localized_ambiguity','Local tie · 2 unresolved'),
 ('embedded_greedy_trap','Embedded greedy trap'),
 ('unbalanced_equal','Equal rows > track count'),
]

def saturation():
 baseline,bmeta=read('saturation-baseline.json');candidate,cmeta=read('saturation-candidate.json')
 assert len(baseline['rows'])==28 and len(candidate['rows'])==32,'Raw case inventory changed; review instead of silently omitting cases'
 old={r['name']:r for r in baseline['rows']};new={r['name']:r for r in candidate['rows']};sizes=[13,16,32,64]
 data=[]
 for label,source,meta in [('Frozen B',baseline,bmeta),('Candidate',candidate,cmeta)]:
  for row in source['rows']:
   data.append({'product':label,'case_name':row['name'],'family':row['family'],'plot_count':row['n'],'track_columns':row['columns'],'candidate_edges':row['inputEdgeCount'],'updated_count':len(row['actual']['pairs']),'held_count':len(row['actual']['heldPlots']),'native_hungarian_calls':row['nativeHungarianCalls'],'paired_baseline_case_available':row['name']in old,'fixture_kind':'native_cartesian_NIS_covariance_fixture'if row['covarianceFixture']else'explicit_cost_graph_fixture','module_sha256':source['moduleSha256'],**meta})
 write_csv(OUT/'saturation.csv',data)
 cmap=LinearSegmentedColormap.from_list('updates',['#eef0f3','#b9d9c7','#287a55'])
 fig=plt.figure(figsize=(13.2,8.4));grid=fig.add_gridspec(3,2,height_ratios=[6,1.2,.45],hspace=.34,wspace=.10)
 axes=[fig.add_subplot(grid[0,0]),fig.add_subplot(grid[0,1])]
 for ax,label,rows in zip(axes,['Frozen B · 28 common cases','Candidate · same 28 cases'],[old,new]):
  values=[]
  for family,_ in FAMILIES:
   line=[]
   for n in sizes:
    name=f'{family}_{n}';row=rows[name];reference=old[name]
    assert row['inputEdgeCount']==reference['inputEdgeCount']and row['columns']==reference['columns'],'Compared fixture graphs differ'
    line.append(len(row['actual']['pairs'])/row['n'])
   values.append(line)
  image=ax.imshow(values,cmap=cmap,vmin=0,vmax=1,aspect='auto')
  for y,(family,_)in enumerate(FAMILIES):
   for x,n in enumerate(sizes):
    row=rows[f'{family}_{n}'];u=len(row['actual']['pairs']);h=len(row['actual']['heldPlots'])
    ax.text(x,y,f'{u} / {h}',ha='center',va='center',fontsize=10,color='white'if u/n>.75 else'#253247')
  ax.set_xticks(range(len(sizes)),[str(n)for n in sizes]);ax.set_xlabel('Connected component: plot count',fontsize=10)
  ax.set_yticks(range(len(FAMILIES)),[label for _,label in FAMILIES]if ax is axes[0]else[])
  ax.tick_params(axis='y',length=0,labelsize=10);ax.tick_params(axis='x',length=0,labelsize=10)
  ax.set_xticks([v-.5 for v in range(5)],minor=True);ax.set_yticks([v-.5 for v in range(8)],minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',length=0)
  ax.set_title(label,fontsize=12,pad=10)
 extra=fig.add_subplot(grid[1,:]);extra.set_xlim(0,4);extra.set_ylim(0,1);extra.axis('off')
 cap=[r for r in candidate['rows']if r['n']in [129,257]];assert len(cap)==4
 extra.set_title('Four additional candidate-only bound cases · baseline not measured',fontsize=10,loc='left',pad=5)
 for i,row in enumerate(cap):
  extra.add_patch(Rectangle((i+.025,.08),.95,.80,facecolor='#edf0f4',edgecolor='#c4cbd4'))
  short='Clear chain'if row['family']=='sparse_chain_clear'else'Equal dense'
  extra.text(i+.5,.67,f'{row["n"]} plots · {short}',ha='center',va='center',fontsize=9)
  extra.text(i+.5,.36,f'{len(row["actual"]["pairs"])} updated / {len(row["actual"]["heldPlots"])} held',ha='center',va='center',fontsize=10)
 proof=candidate['lowerBoundProof'];foot=fig.add_subplot(grid[2,:]);foot.axis('off')
 foot.text(0,.62,f'Certificate audit: {proof["actualLargeGraphs"]} embedded graphs · {proof["nearOptimalAssignmentsEnumerated"]} near-optimal assignments · {proof["actualLargeEdgesChecked"]:,} returned edges checked · {len(proof["errors"])} unsound.',fontsize=9,color='#315c43')
 foot.text(0,.03,'HOLD is intentional for unresolved ties. Isolated graph/native-kernel evidence; no natural RF or gameplay/FPS claim.',fontsize=8.8,color='#4f5968')
 fig.suptitle('Saturation: clear updates resume; unresolved ambiguity remains held',fontsize=15,x=.52,y=.98)
 fig.subplots_adjust(left=.23,right=.87,top=.91,bottom=.065)
 box=axes[1].get_position();cax=fig.add_axes([.90,box.y0,.015,box.height]);cb=fig.colorbar(image,cax=cax);cb.ax.yaxis.set_major_formatter(PercentFormatter(xmax=1));cb.set_label('Updated fraction; cell = updated / held',fontsize=10)
 fig.savefig(OUT/'saturation.svg',format='svg',bbox_inches='tight',metadata={'Date':None})
 plt.close(fig)

def cost128():
 source,meta=read('saturation-128.json');rows=source['rows'];assert len(rows)==4 and all(r['n']==128 for r in rows)
 labels={'sparse_chain_clear':'Clear sparse chain','dense_diagonal_clear':'Clear dense diagonal','dense_equal':'Equal dense · all HOLD','weak_ambiguity':'Weak island · 2 HOLD'}
 data=[]
 for row in rows:
  timing=row['timing'];assert timing['warmupCalls']==2 and timing['samples']==5
  data.append({'case_name':row['name'],'family':row['family'],'plot_count':128,'candidate_edges':row['inputEdgeCount'],'updated_count':len(row['actual']['pairs']),'held_count':len(row['actual']['heldPlots']),'native_hungarian_calls':row['nativeHungarianCalls'],'warmup_calls':timing['warmupCalls'],'timed_calls':timing['samples'],'mean_ms_per_call':timing['meanMs'],'p95_ms_per_call':timing['p95Ms'],'native_first_validation_ms':timing['nativeWallMs'],'budget_ms':1000/60,'mean_exceeds_budget':timing['meanMs']>1000/60,'p95_exceeds_budget':timing['p95Ms']>1000/60,'module_sha256':source['moduleSha256'],'node_version':source['host']['node'],**meta})
 write_csv(OUT/'cost128.csv',data)
 fig,ax=plt.subplots(figsize=(11.6,5.6));ys=list(range(len(rows)));means=[r['timing']['meanMs']for r in rows];tails=[r['timing']['p95Ms']for r in rows];budget=1000/60
 xmax=max(tails)*1.29;ax.axvspan(budget,xmax,color='#fff1ec',zorder=0);ax.barh(ys,means,height=.48,color=['#3a8664'if v<=budget else'#b65c3d'for v in means],label='Recorded mean',zorder=2)
 ax.scatter(tails,ys,s=50,marker='D',color='#26354a',label='Recorded p95',zorder=4)
 for y,m,p in zip(ys,means,tails):
  ax.plot([m,p],[y,y],color='#26354a',linewidth=1.1,zorder=3);ax.text(max(m,p)+.6,y,f'{m:.2f} / {p:.2f} ms',va='center',fontsize=10,color='#26354a')
 ax.axvline(budget,color='#a32726',linestyle='--',linewidth=1.5,label='16.7 ms · 60 Hz tick budget')
 ax.set_yticks(ys,[labels[r['family']]for r in rows]);ax.invert_yaxis();ax.set_xlim(0,xmax);ax.set_xlabel('Node host time per solver call (ms) · NOT measured game FPS',fontsize=10)
 ax.grid(axis='x',color='#e1e5ea',linewidth=.7,zorder=1);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0,labelsize=10);ax.spines[['top','right','left']].set_visible(False)
 ax.set_title('128-row bound: dense single-call latency exceeds the tick budget',fontsize=14,pad=16)
 ax.legend(loc='upper left',bbox_to_anchor=(0,-.18),ncol=3,frameon=False,fontsize=9)
 fig.text(.18,.045,'2 warmup + 5 timed calls/family; nearest-rank p95 is the largest sample. Exactly one native Hungarian per call.',fontsize=8.7,color='#515c6b')
 fig.text(.18,.012,'Source aggregates are plotted unchanged; concurrent host work may affect timings. No cross-family averaging or FPS conversion.',fontsize=8.7,color='#515c6b')
 fig.subplots_adjust(left=.20,right=.98,top=.86,bottom=.26);fig.savefig(OUT/'cost128.svg',format='svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

def main():
 OUT.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'AEGIS_TRACK_B_STABILIZATION_SATURATION','axes.unicode_minus':False,'savefig.facecolor':'white'})
 saturation();cost128()
 for name in ['saturation.svg','saturation.csv','cost128.svg','cost128.csv']:
  path=OUT/name;print(name,sha(path.read_bytes()),path.stat().st_size)

if __name__=='__main__':main()
