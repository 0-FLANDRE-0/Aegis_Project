"""Plot existing isolated R2 benchmark only. No test rerun or browser.

CSV values are copied from one named raw JSON; no cross-workload mean, hidden
failure removal, or game FPS conversion is performed.
"""
from pathlib import Path
import argparse,csv,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/dev/shm/aegis-track-r2-mpl')
os.environ.setdefault('TMPDIR','/dev/shm')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

P=Path(__file__).resolve().parent;ROOT=P.parents[3]
hash_bytes=lambda value:hashlib.sha256(value).hexdigest()
FAMILIES=[('sparse_chain_clear','Clear sparse chain'),('dense_equal','Equal-cost dense'),('localized_ambiguity','Local ambiguous island'),('embedded_greedy_trap','Embedded greedy trap')]

def csv_write(path,rows):
 with path.open('w',newline='')as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,default=P/'evidence/cost-shared/cost-r2.json');ap.add_argument('--out-dir',type=Path)
 args=ap.parse_args();raw=args.input.read_bytes();data=json.loads(raw);out=args.out_dir or args.input.parent/'figures';out.mkdir(parents=True,exist_ok=True)
 source={'source_json':str(args.input.resolve().relative_to(ROOT)),'source_json_sha256':hash_bytes(raw),'host_state':data['hostState'],'r2_module_sha256':data['r2ModuleSha256']}
 rows=data['rows'];assert len(rows)==22,'Review changed sample inventory; do not silently omit workloads'
 table=[];calls=[]
 for row in rows:
  table.append({'workload':row['name'],'family':row['family'],'plots':row['plots'],'track_columns':row['trackColumns'],'eligible_edges':row['inputEdges'],'input_sha256':row['inputSha256'],'r1_updated':row['r1Updated'],'r1_held':row['r1Held'],'r2_updated':row['r2Updated'],'r2_held':row['r2Held'],'exact_updated':row['exactUpdated'],'exact_held':row['exactHeld'],'r1_single_validation_ms':row['r1SingleValidationMs'],'r1_validation_sample_count':1,'r1_native_calls':row['r1NativeCalls'],'r2_native_calls_per_run':row['r2NativeCallsPerRun'],'warmup_calls':row['warmupCalls'],'timed_samples':row['timing']['samples'],'r2_mean_ms_per_call':row['timing']['meanMs'],'r2_p95_ms_per_call':row['timing']['p95Ms'],'known_unresolved_limit':row['knownUnresolvedLimit'],'holding_cause':row['holdingCause'],'original_r1_test_status':data['oldR1Compatibility']['rawStatus'],**source})
  for run in row['timedRuns']:
   for call in run['nativeCalls']:
    calls.append({'workload':row['name'],'timed_run':run['ordinal'],'outer_solver_wall_ms':run['wallMs'],'native_call':call['ordinal'],'matrix_rows':call['rows'],'matrix_columns':call['columns'],'native_wall_ms':call['wallMs'],**source})
 csv_write(out/'r2-workloads.csv',table);csv_write(out/'r2-native-calls.csv',calls)
 text=['# Isolated R2 cost and remaining limits','',f'Source: `{source["source_json"]}`; SHA-256 `{source["source_json_sha256"]}`.',f'Host tag: **{data["hostState"]}**. Instrumented Node host proxy; this is not game FPS or a battle regression.','',f'Original unchanged R1 diagnostic status: **{data["oldR1Compatibility"]["rawStatus"]}**, exit {data["oldR1Compatibility"]["exitCode"]}. Raw failures: '+', '.join(data['oldR1Compatibility']['failedOriginalChecks'])+'.','',f'New R2 intention contracts: **{data["intendedContractStatus"]}**; official game regression count: {data["officialGameRegressionCount"]}.','', '| Workload | R1 updated/held | R2 updated/held | R2 native calls/run | Mean ms | p95 ms | Hold meaning |','|---|---:|---:|---:|---:|---:|---|']
 for row in rows:text.append(f'| {row["name"]} | {row["r1Updated"]}/{row["r1Held"]} | {row["r2Updated"]}/{row["r2Held"]} | {row["r2NativeCallsPerRun"]} | {row["timing"]["meanMs"]:.3f} | {row["timing"]["p95Ms"]:.3f} | {row["holdingCause"] or "—"} |')
 text+=['','The no-C13 input is globally unique in the exact native reference but remains held by R2. This is computational certificate incompleteness, not equal input evidence and not a resolved issue.','The captured13 workload records every internal native call shape/time; first timed run:13×26 global once plus10×20 residual eleven times. R1 single-validation times are retained separately in CSV and are not mixed into R2 timed means.']
 (out/'r2-cost-table.md').write_text('\n'.join(text)+'\n')
 plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'AEGIS_TRACK_R2_COST','savefig.facecolor':'white'})
 def save(fig,name):fig.savefig(out/name,bbox_inches='tight',metadata={'Date':None});plt.close(fig)
 sizes=[13,16,32,64,128];lookup={(r['family'],r['plots']):r for r in rows};actual=next(r for r in rows if r['family']=='actual_captured');limit=next(r for r in rows if r['family']=='no_C_unique_limit')
 fig=plt.figure(figsize=(12.8,7));grid=fig.add_gridspec(2,1,height_ratios=[4.4,1.5],hspace=.4);ax=fig.add_subplot(grid[0]);values=[[lookup[(f,n)]['r2Updated']/n for n in sizes]for f,_ in FAMILIES];ax.imshow(values,cmap=LinearSegmentedColormap.from_list('accepted',['#edf0f3','#a7d1bc','#287654']),vmin=0,vmax=1,aspect='auto')
 for y,(family,_)in enumerate(FAMILIES):
  for x,n in enumerate(sizes):
   r=lookup[(family,n)];text=f'{r["r1Updated"]}/{r["r1Held"]} → {r["r2Updated"]}/{r["r2Held"]}\n{r["r2NativeCallsPerRun"]} native call'+('s'if r['r2NativeCallsPerRun']!=1 else'')
   ax.text(x,y,text,ha='center',va='center',fontsize=9,color='white'if r['r2Updated']/n>.8 else'#26364b')
 ax.set_xticks(range(5),sizes);ax.set_yticks(range(4),[label for _,label in FAMILIES]);ax.tick_params(length=0);ax.set_xlabel('Connected-component plot count');ax.set_title('R1 → R2 updated/held counts · global optimum retained',fontsize=13,pad=12);ax.set_xticks([v-.5 for v in range(6)],minor=True);ax.set_yticks([v-.5 for v in range(5)],minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',length=0)
 lower=fig.add_subplot(grid[1]);lower.set_xlim(0,2);lower.set_ylim(0,1);lower.axis('off')
 for x,color in [(0,'#e9f4ee'),(1,'#fff0dc')]:lower.add_patch(Rectangle((x+.02,.08),.96,.85,facecolor=color,edgecolor='#c8cfd6'))
 component=actual['r2Components'][0]
 lower.text(.5,.76,'Actual native13 · step158 /86 edges',ha='center',fontsize=10,fontweight='bold');lower.text(.5,.51,f'R1 {actual["r1Updated"]}/{actual["r1Held"]} → R2 {actual["r2Updated"]}/{actual["r2Held"]}',ha='center',fontsize=12);lower.text(.5,.25,f'LB{component["lowerBoundCertifiedCount"]} + residual exact{component["exactResidualCertifiedCount"]} · {actual["r2NativeCallsPerRun"]} native calls',ha='center',fontsize=9)
 lower.text(1.5,.76,'Known remaining computational limit',ha='center',fontsize=10,fontweight='bold');lower.text(1.5,.51,f'No-C unique13: R2 {limit["r2Updated"]}/{limit["r2Held"]}; exact {limit["exactUpdated"]}/{limit["exactHeld"]}',ha='center',fontsize=11);lower.text(1.5,.25,'Globally distinguishable cost graph; certificate unavailable',ha='center',fontsize=8.7)
 fig.text(.18,.015,'Counts are pure graph results, not battle kills. Equal-cost HOLD and computationally unproved HOLD are distinct.',fontsize=9,color='#505e6e');fig.subplots_adjust(left=.19,right=.98,top=.91,bottom=.09);save(fig,'r2-updates-limits.svg')
 fig,axes=plt.subplots(2,2,figsize=(12,7.8),sharex=True)
 for ax,(family,label)in zip(axes.flat,FAMILIES):
  rr=[lookup[(family,n)]for n in sizes];ax.plot(sizes,[r['timing']['meanMs']for r in rr],marker='o',label='Recorded mean');ax.plot(sizes,[r['timing']['p95Ms']for r in rr],marker='D',linestyle='--',label='Recorded p95');ax.axhline(1000/60,color='#a22c27',linestyle=':',label='16.7 ms tick budget');ax.set_xscale('log',base=2);ax.set_xticks(sizes,[str(n)for n in sizes]);ax.grid(color='#e2e7eb',linewidth=.6);ax.set_ylabel('ms per outer solver call');ax.set_xlabel('Component plot count')
  counts=set(r['r2NativeCallsPerRun']for r in rr)
  if len(counts)==1:ax.set_title(f'{label} · {next(iter(counts))} native calls/run',fontsize=10.5)
  else:
   ax.set_title(label,fontsize=11)
   for n,r in zip(sizes,rr):ax.annotate(f'{r["r2NativeCallsPerRun"]} calls',(n,r['timing']['p95Ms']),xytext=(0,6),textcoords='offset points',ha='center',fontsize=7.5)
 handles,labels=axes.flat[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,bbox_to_anchor=(.5,.045),frameon=False,fontsize=9);fig.suptitle(f'R2 isolated Node cost · {data["hostState"]} host proxy, NOT measured game FPS',fontsize=14)
 fig.text(.10,.015,f'{data["warmupCalls"]} warmup + {data["timedCallsPerWorkload"]} timed calls/workload. Original R1 diagnostic result retained: {data["oldR1Compatibility"]["rawStatus"]}; not official game regressions.',fontsize=8.7,color='#505e6e');fig.subplots_adjust(top=.90,bottom=.16,hspace=.40,wspace=.24);save(fig,'r2-cost.svg')
 # One explicit recorded timed run, never a manufactured average of inner calls.
 inner=actual['timedRuns'][0]['nativeCalls'];assert len(inner)==12
 fig,ax=plt.subplots(figsize=(10.7,6));yy=list(range(len(inner)));ax.barh(yy,[c['wallMs']for c in inner],color=['#267354']+['#50799f']*11)
 labels=[f'{i+1}: {c["rows"]}×{c["columns"]} · '+('global'if i==0 else'residual base'if i==1 else'residual alternative')for i,c in enumerate(inner)];ax.set_yticks(yy,labels);ax.invert_yaxis();ax.set_xlim(0,max(c['wallMs']for c in inner)*1.16);ax.set_xlabel('Recorded native Hungarian ms · timed outer run0');ax.set_title('Actual13: one global + eleven bounded10-row native calls',fontsize=13);ax.grid(axis='x',color='#e3e7eb',linewidth=.6);ax.set_axisbelow(True)
 for y,c in zip(yy,inner):ax.text(c['wallMs'],y,f' {c["wallMs"]:.4f}',va='center',fontsize=8.5)
 fig.text(.22,.015,f'Outer recorded call: {actual["timedRuns"][0]["wallMs"]:.4f} ms; inner timings are instrumented host proxies, not simulation time or FPS.',fontsize=8.5,color='#505e6e');fig.subplots_adjust(left=.28,right=.95,top=.88,bottom=.13);save(fig,'actual13-call-shapes.svg')
 for path in sorted(out.iterdir()):print(path.name,hash_bytes(path.read_bytes()),path.stat().st_size)

if __name__=='__main__':main()
