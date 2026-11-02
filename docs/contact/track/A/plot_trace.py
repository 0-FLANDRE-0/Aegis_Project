"""Plot recorded TRACK-A Harpoon candidate decisions; never runs game code.

Only the supplied final trace JSON.gz is read. Candidate NIS/gate ratios and
file-creation events come from actual trace fields. This is an observed
diagnostic, not a claim that every physical observation opportunity was logged.
"""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,json,math,os
os.environ.setdefault('MPLCONFIGDIR','/dev/shm/mpl-friendly-contact')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P=Path(__file__).resolve().parent
DECLARED_PRODUCT_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
sha=lambda x:hashlib.sha256(x).hexdigest()

def finite(x):return isinstance(x,(float,int))and not isinstance(x,bool)and math.isfinite(x)
def ratio(record):
 n,g=record.get('nis'),record.get('gate')
 return n/g if record.get('type')=='CANDIDATE'and record.get('gateUnits')=='NIS'and finite(n)and finite(g)and g>0 else None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trace',type=Path,default=P/'evidence/candidate/harpoon-route-trace.json.gz')
 ap.add_argument('--svg',type=Path,default=P/'evidence/candidate/harpoon-nis-timeline.svg')
 ap.add_argument('--csv',type=Path,default=P/'evidence/candidate/harpoon-nis-timeline.csv');args=ap.parse_args()
 compressed=args.trace.read_bytes();decoded=gzip.decompress(compressed);data=json.loads(decoded)
 assert data.get('schema')=='AEGIS_TRACK_A_DIAGNOSTICS_1'
 records=data['records'];assert records and all(finite(r.get('timeS'))for r in records)
 candidates=[r for r in records if r.get('type')=='CANDIDATE']
 plotted=[r for r in candidates if ratio(r)is not None and ratio(r)>0]
 excluded=[r for r in candidates if r not in plotted]
 creates=[r for r in records if r.get('type')=='UPDATE'and r.get('decision')=='CREATE']
 assignments=[r for r in records if r.get('type')=='ASSIGNMENT']
 assert plotted,'No positive finite candidate NIS/gate observations to plot'
 counts=collections.Counter((r.get('route','UNSPECIFIED'),r.get('decision','UNSPECIFIED'))for r in candidates)
 # Keep raw candidate rows, including any not plottable on the log axis, and
 # explicit creation rows. Creation-initialization NIS is not a candidate ratio.
 columns=['serial','tick','timeS','type','route','trackId','measurementId','decision','reason','nis','gate','nisGateRatio','gateUnits','appliedModel','appliedDimension','finalSource']
 csv_records=sorted(candidates+creates,key=lambda r:r['serial']);args.csv.parent.mkdir(parents=True,exist_ok=True)
 with args.csv.open('w',newline='')as f:
  writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
  for r in csv_records:
   row={k:r.get(k,'')for k in columns};value=ratio(r);row['nisGateRatio']=''if value is None else value;writer.writerow(row)

 plt.rcParams.update({'font.size':9,'svg.hashsalt':'AEGIS_TRACK_A_HARPOON_NIS_TIMELINE_V1'})
 fig=plt.figure(figsize=(12,7.2));grid=fig.add_gridspec(3,2,height_ratios=[3.4,1.35,1.05],hspace=.5,wspace=.17)
 ax=fig.add_subplot(grid[0,:]);palette={'ELIGIBLE':'#07807b','REJECT':'#bd3c38'}
 for decision in sorted({r.get('decision','UNSPECIFIED')for r in plotted}):
  selected=[r for r in plotted if r.get('decision','UNSPECIFIED')==decision]
  ax.scatter([r['timeS']for r in selected],[ratio(r)for r in selected],s=12 if decision=='ELIGIBLE'else 27,
             marker='o'if decision=='ELIGIBLE'else'x',alpha=.7 if decision=='ELIGIBLE'else.95,
             c=palette.get(decision,'#6f668e'),label=f'{decision}: {len(selected)}',linewidths=.8)
 ax.axhline(1,color='#252525',linestyle='--',linewidth=1,label='Recorded gate: NIS / gate = 1')
 ax.set_yscale('log');ax.set_xlim(0,max(r['timeS']for r in records)+1)
 ax.set_xlabel('Simulation time (s)');ax.set_ylabel('Candidate NIS / recorded gate (log scale)')
 ax.grid(alpha=.2,which='both');ax.legend(loc='lower right',fontsize=8)
 ax.set_title('Harpoon route: native association decisions and new-file events',fontsize=12)

 creation_rows=[];reacquisition_notes=[]
 for i,c in enumerate(creates):
  ident=c.get('trackId');t=c['timeS'];ax.axvline(t,color='#636789',linestyle=':',linewidth=1)
  creation_rows.append([f'{t:.3f}',str(ident),c.get('finalSource',c.get('route','?'))])
  ax.text(t+.4,.97-i*.085,f'CREATE {ident}',transform=ax.get_xaxis_transform(),color='#515577',fontsize=8,va='top')
  same_plot=[r for r in candidates if r.get('tick')==c.get('tick')and r.get('measurementId')==c.get('measurementId')and r.get('decision')=='REJECT']
  if same_plot:
   # Link only the already-recorded same-payload ID and tick. No geometric
   # matching, target truth, EKF prediction, or resimulated NIS is used.
   old=same_plot[0];last=[r for r in records if r.get('type')=='UPDATE'and r.get('decision')=='ACCEPT'and r.get('trackId')==old.get('trackId')and r['timeS']<t]
   gap=t-max(r['timeS']for r in last)if last else None
   note=f"{t:.3f}s: candidate {old.get('trackId')} rejected, NIS {old.get('nis'):.3f} / gate {old.get('gate'):g}"
   if gap is not None:note+=f'; {gap:.3f}s since last recorded accepted update'
   reacquisition_notes.append(note)
   if ratio(old)is not None and ratio(old)>0:
    ax.annotate(f"{old['nis']:.3f} / {old['gate']:g} = {ratio(old):.3f}",xy=(t,ratio(old)),
                xytext=(t+3,ratio(old)*2.4),fontsize=8,color='#9b2c2a',
                arrowprops={'arrowstyle':'->','color':'#9b2c2a','linewidth':.8})

 route_ax=fig.add_subplot(grid[1,0]);route_ax.axis('off')
 routes=sorted({r.get('route','UNSPECIFIED')for r in candidates});route_rows=[]
 for route in routes:route_rows.append([route,str(sum(v for (key,_),v in counts.items()if key==route)),str(counts[(route,'ELIGIBLE')]),str(counts[(route,'REJECT')])])
 route_rows.append(['TOTAL',str(len(candidates)),str(sum(r.get('decision')=='ELIGIBLE'for r in candidates)),str(sum(r.get('decision')=='REJECT'for r in candidates))])
 table=route_ax.table(cellText=route_rows,colLabels=['Recorded candidate route','All','Eligible','Reject'],loc='center',cellLoc='center',colWidths=[.55,.15,.15,.15])
 table.auto_set_font_size(False);table.set_fontsize(8);table.scale(1,1.38)
 route_ax.set_title('Recorded evaluations (not unique plots or all opportunities)',fontsize=9,pad=6)

 stats_ax=fig.add_subplot(grid[1,1]);stats_ax.axis('off');stats=data.get('stats',{})
 stats_text='\n'.join([
  f"Retained events: {len(records)}; dropped: {stats.get('dropped','unknown')}; errors: {stats.get('errors','unknown')}",
  f"Candidate ratios plotted: {len(plotted)}; unplottable: {len(excluded)}",
  f"Native assignments: {sum(r.get('decision')=='ASSIGN'for r in assignments)}; no assignment: {sum(r.get('decision')=='NO_ASSIGNMENT'for r in assignments)}",
  f"New-file UPDATE events: {len(creates)} (tactical IDs, not truth objects)",
  f"Observed window: {min(r['timeS']for r in records):.3f} to {max(r['timeS']for r in records):.3f} s",
  'Missing gate/NIS is never recomputed or replaced with a zero.'])
 stats_ax.text(0,.95,stats_text,va='top',fontsize=8.5,linespacing=1.55)

 create_ax=fig.add_subplot(grid[2,:]);create_ax.axis('off')
 ct=create_ax.table(cellText=creation_rows or [['-','No CREATE recorded','-']],colLabels=['Time (s)','New tactical track ID','Recorded source'],cellLoc='center',loc='upper center',colWidths=[.16,.27,.57])
 ct.auto_set_font_size(False);ct.set_fontsize(8);ct.scale(1,1.4)
 for j,note in enumerate(reacquisition_notes[:2]):create_ax.text(0,-.17-j*.18,note,fontsize=8,color='#6f3231',transform=create_ax.transAxes)
 fig.text(.055,.055,'Observed diagnostic only: the native rejection/new ID is retained; no truth identity, hidden trajectory, or all-opportunity coverage is inferred.',fontsize=8)
 fig.text(.055,.032,'Declared RC2 product: '+DECLARED_PRODUCT_SHA,fontsize=6.5)
 fig.text(.055,.016,'Only input gzip SHA-256: '+sha(compressed),fontsize=6.5)
 fig.subplots_adjust(top=.94,bottom=.16,left=.07,right=.985)
 args.svg.parent.mkdir(parents=True,exist_ok=True)
 fig.savefig(args.svg,metadata={'Date':None,'Creator':'AEGIS TRACK-A recorded diagnostic plot',
  'Description':'Read-only Harpoon native candidate NIS/gate timeline; source gzip SHA-256 '+sha(compressed)+'; decoded SHA-256 '+sha(decoded)})
 plt.close(fig)
 print(json.dumps({'input':str(args.trace),'inputGzipSha256':sha(compressed),'inputDecodedSha256':sha(decoded),
  'declaredProductSha256':DECLARED_PRODUCT_SHA,'inputItselfHasNoProductHash':True,
  'recordedEvents':len(records),'candidateRecords':len(candidates),'plottedCandidateRatios':len(plotted),
  'creationEvents':len(creates),'assignmentEvents':len(assignments),'csvRows':len(csv_records),
  'retainedWindowS':[min(r['timeS']for r in records),max(r['timeS']for r in records)],
  'ringDropped':stats.get('dropped'),'reacquisitionNotes':reacquisition_notes,
  'svg':str(args.svg),'svgSha256':sha(args.svg.read_bytes()),'csv':str(args.csv),'csvSha256':sha(args.csv.read_bytes()),
  'gameCodeExecuted':False,'truthRead':False,'sourceTraceModified':False},indent=2))

if __name__=='__main__':main()
