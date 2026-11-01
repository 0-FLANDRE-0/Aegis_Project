"""Plot recorded direct native ingress results; never run a game/kernel/model.

Only the final baseline-off.json and active-on.json are data sources. Their
reported/estimated values and native results are not natural-RF performance or
physical-target truth. SVG and CSV contain complete input provenance hashes.
"""
from pathlib import Path
import csv,hashlib,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

P=Path(__file__).resolve().parent;E=P/'evidence/native-integration';F=P/'evidence/figures'
CLASSIFICATION='DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF'
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def main():
 F.mkdir(parents=True,exist_ok=True);data={};sources={}
 for mode,name in [('A','baseline-off.json'),('B','active-on.json')]:
  raw=(E/name).read_bytes();d=json.loads(raw)
  assert d['classification']==CLASSIFICATION and d['naturalRfOrWeaponEvidence']is False
  assert not d['fixturePreconditionOrRuntimeFailures']
  data[mode]=d;sources[mode]={'dataFile':'native-integration/'+name,'dataSha256':sha(raw),'product':d['product'],'productSha256':d['productSha256'],'fixtureSourceSha256':d['fixtureSourceSha256'],'helpers':d['helpers']}
 assert sources['A']['fixtureSourceSha256']==sources['B']['fixtureSourceSha256']
 assert sources['A']['helpers']==sources['B']['helpers']
 records={k:d['nativeResult']['records']for k,d in data.items()};rows=[]
 assert records['A']['ownDopplerCrossing']['assignment']==records['B']['ownDopplerCrossing']['assignment']
 assert len({q['trackId']for _,q in records['B']['ownDopplerCrossing']['assignment']})==2
 assert len(records['A']['ownExactAmbiguity']['assignment'])==1 and not records['B']['ownExactAmbiguity']['assignment']
 assert len(records['A']['hugeCovarianceDistanceSanity']['assignment'])==1 and not records['B']['hugeCovarianceDistanceSanity']['assignment']
 def add(mode,case,metric,value,unit='',index=None,track_id=None,path='',detail=None):
  src=sources[mode];rows.append({'classification':CLASSIFICATION,'variant':mode,'case':case,'metric':metric,'index':index,'track_id':track_id,'value_json':dump(value),'unit':unit,'source_json':src['dataFile'],'source_json_sha256':src['dataSha256'],'product':src['product'],'product_sha256':src['productSha256'],'fixture_source_sha256':src['fixtureSourceSha256'],'helper_source_shas_json':dump(src['helpers']),'source_pointer':path,'details_json':dump(detail)})
 # Record exact values plotted; no reassociation or likelihood calculation.
 for mode,r in records.items():
  c=r['ownDopplerCrossing']
  for i,p in enumerate(c['anonymousInputs']):add(mode,'ownDopplerCrossing','observed_radial_velocity',p['radialMps'],'m/s',i,path=f'/nativeResult/records/ownDopplerCrossing/anonymousInputs/{i}/radialMps')
  for i,t in enumerate(c['before']):add(mode,'ownDopplerCrossing','filter_estimated_vx',t['x'][3],'m/s',i,t['id'],f'/nativeResult/records/ownDopplerCrossing/before/{i}/x/3')
  for i,q in c['assignment']:add(mode,'ownDopplerCrossing','native_assignment',q['trackId'],'tactical_track_id',i,q['trackId'],'/nativeResult/records/ownDopplerCrossing/assignment',{'nis':q['nis']})
  c=r['ownExactAmbiguity'];add(mode,'ownExactAmbiguity','native_assignment_count',len(c['assignment']),'files',path='/nativeResult/records/ownExactAmbiguity/assignment')
  for i,q in c['assignment']:add(mode,'ownExactAmbiguity','native_selected_id',q['trackId'],'tactical_track_id',i,q['trackId'],'/nativeResult/records/ownExactAmbiguity/assignment',{'nis':q['nis']})
  c=r['hugeCovarianceDistanceSanity'];add(mode,'hugeCovarianceDistanceSanity','native_nis',c['nativeNis'],'NIS',path='/nativeResult/records/hugeCovarianceDistanceSanity/nativeNis');add(mode,'hugeCovarianceDistanceSanity','native_assignment_count',len(c['assignment']),'files',path='/nativeResult/records/hugeCovarianceDistanceSanity/assignment')
  c=r['hawklinkHugeMeasurementCovariance'];add(mode,'hawklinkHugeMeasurementCovariance','native_nis',c['nativeNis'],'NIS',path='/nativeResult/records/hawklinkHugeMeasurementCovariance/nativeNis')
  existing=next(t for t in c['after']if t['id']==c['before']['id'])
  assert existing['hits']-c['before']['hits']==(1 if mode=='A' else 0)
  add(mode,'hawklinkHugeMeasurementCovariance','existing_file_hit_increment',existing['hits']-c['before']['hits'],'hits',track_id=existing['id'],path='/nativeResult/records/hawklinkHugeMeasurementCovariance',detail={'beforeHits':c['before']['hits'],'afterHits':existing['hits'],'fileCountAfter':len(c['after'])})
  c=r['ownTwoHundredFiftySevenPlotSafety']
  for key in ['plotCount','assignedCount','afterFileCount']:add(mode,'ownTwoHundredFiftySevenPlotSafety',key,c[key],'files'if key!='plotCount'else'plots',path='/nativeResult/records/ownTwoHundredFiftySevenPlotSafety/'+key)
  add(mode,'ownTwoHundredFiftySevenPlotSafety','native_caller_hits',c['result']['hits'],'hits',path='/nativeResult/records/ownTwoHundredFiftySevenPlotSafety/result/hits')
  add(mode,'ownTwoHundredFiftySevenPlotSafety','original_file_hits',c['afterOriginalFile']['hits'],'hits',track_id=c['afterOriginalFile']['id'],path='/nativeResult/records/ownTwoHundredFiftySevenPlotSafety/afterOriginalFile/hits')
 # The native trace records the actual position sanity result. No world pose,
 # filter prediction, covariance inversion or RF calculation is recomputed.
 trace=data['B']['traceB']['records'];sanity=[]
 for case,route,nis in [('hugeCovarianceDistanceSanity','OWN_SPY_GLOBAL',records['B']['hugeCovarianceDistanceSanity']['nativeNis']),('hawklinkHugeMeasurementCovariance','HAWKLINK_COHORT',records['B']['hawklinkHugeMeasurementCovariance']['nativeNis'])]:
  found=[q for q in trace if q['route']==route and q.get('decision')=='SANITY_REJECT'and q.get('reason')=='INDEPENDENT_POSITION_SANITY'and math.isclose(q.get('nis',-1),nis,rel_tol=1e-12,abs_tol=1e-12)]
  assert len(found)==1,(case,len(found));q=found[0];sanity.append(q)
  for key,unit in [('distanceM','m'),('distanceGateM','m'),('gate','NIS')]:add('B',case,'recorded_'+key,q[key],unit,track_id=q['trackId'],path='/traceB/records',detail={'traceSerial':q['serial'],'route':route,'reason':q['reason']})
 c55_equal=[]
 for owner,cases in records['A']['c55BothNativeContexts']['records'].items():
  other=records['B']['c55BothNativeContexts']['records'][owner]
  for case,value in cases['cases'].items():
   equal=value==other['cases'][case];assert equal,(owner,case);c55_equal.append(equal)
   add('B','c55BothNativeContexts/'+owner+'/'+case,'native_case_exact_equal_to_A',equal,'boolean',path='/nativeResult/records/c55BothNativeContexts/records/'+owner+'/cases/'+case,detail={'livePolicyChanged':records['B']['c55BothNativeContexts']['liveC55PolicyChanged'],'sourceType':'DIRECT_NATIVE_POST_RF_C55_FIXTURE_NOT_NATURAL_RF'})
 assert records['B']['c55BothNativeContexts']['liveC55PolicyChanged']is False
 assert data['B']['nativeResult']['checks']['ownAmbiguity.assignmentWithheld']and data['B']['nativeResult']['checks']['ownAmbiguity.existingFilesUnchanged']
 add('B','ownExactAmbiguity','recorded_policy_assignment_withheld',True,'boolean',path='/nativeResult/checks/ownAmbiguity.assignmentWithheld')
 csv_path=F/'native-association.csv'
 with csv_path.open('w',newline='')as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
 provenance={'classification':CLASSIFICATION,'dataSources':sources,'plotScriptSha256':sha(Path(__file__).read_bytes()),'csvSha256':sha(csv_path.read_bytes()),'physicalTruthUsed':False,'kernelsExecuted':False,'naturalRfPerformanceClaimed':False}
 plt.rcParams.update({'font.size':10,'svg.hashsalt':'AEGIS_TRACK_B_RECORDED_NATIVE_ASSOCIATION_1','svg.fonttype':'none'})
 fig,axes=plt.subplots(2,2,figsize=(15,9));fig.subplots_adjust(left=.13,right=.97,bottom=.16,top=.86,hspace=.54,wspace=.35)
 color={'A':'#777777','B':'#007e87'}
 ax=axes[0,0];c=records['B']['ownDopplerCrossing'];right={t['id']:1-i for i,t in enumerate(c['before'])}
 for mode in ['A','B']:
  for i,q in records[mode]['ownDopplerCrossing']['assignment']:
   ax.plot([.12,.88],[1-i,right[q['trackId']]],color=color[mode],ls='--'if mode=='A'else'-',lw=3.4 if mode=='A' else 1.5,zorder=1 if mode=='A' else 2)
 for i,p in enumerate(c['anonymousInputs']):ax.scatter(.12,1-i,s=65,c='#d08a16',zorder=3);ax.text(.1,1-i+.12,f"plot {i}: measured rdot {p['radialMps']:+.3f} m/s",ha='left',fontsize=8)
 for i,t in enumerate(c['before']):ax.scatter(.88,1-i,s=65,c='#245989',zorder=3);ax.text(.94,1-i,f"T{t['id']}\nfilter vx {t['x'][3]:+.3f} m/s",va='center',fontsize=8)
 ax.set(xlim=(0,1.58),ylim=(-.3,1.4),title='Same pose, opposite measured Doppler\nBoth variants retain two one-to-one assignments');ax.axis('off');ax.legend(handles=[Line2D([0],[0],color=color['A'],ls='--',lw=3,label='A native'),Line2D([0],[0],color=color['B'],lw=1.5,label='B ACTIVE')],loc='lower center',ncol=2,frameon=False,fontsize=8)
 ax=axes[0,1];counts=[len(records[m]['ownExactAmbiguity']['assignment'])for m in ['A','B']];ax.bar(['A native','B ACTIVE'],counts,color=[color['A'],color['B']],width=.5);ax.set(ylim=(0,1.45),yticks=[0,1],ylabel='Assigned existing files',title='Exact ambiguity: equal filter states / P')
 chosen=records['A']['ownExactAmbiguity']['assignment'][0][1]['trackId'];ax.text(0,1.05,f'Numeric-ID tie chooses\nT{chosen}',ha='center',fontsize=8);ax.text(1,.08,'HOLD\nNo existing-file update',ha='center',fontsize=9,color=color['B']);ax.grid(axis='y',alpha=.2)
 ax=axes[1,0]
 for i,(q,label)in enumerate(zip(sanity,['Large filter P','Large reported R'])):
  y=1-i;ax.scatter(q['distanceM']/1000,y,s=75,color=color['B'],marker='o');ax.scatter(q['distanceGateM']/1000,y,s=75,color='#d08a16',marker='|');ax.plot([q['distanceGateM']/1000,q['distanceM']/1000],[y,y],color=color['B'],alpha=.45)
  ax.text(4,y+.12,f"native NIS {q['nis']:.4g} < {q['gate']:g}\nA associates; B rejects distant pair",fontsize=8);ax.text(q['distanceM']/1000,y-.18,f"innovation {q['distanceM']/1000:g} km",ha='center',fontsize=8);ax.text(q['distanceGateM']/1000,y-.18,f"limit {q['distanceGateM']/1000:g} km",ha='center',fontsize=8,color='#96600b')
 ax.set(xscale='log',xlim=(1,180),ylim=(-.4,1.45),yticks=[1,0],yticklabels=['Large filter P','Large reported R'],xlabel='Recorded position innovation / sanity limit (km)',title='Distant association: measured/reported vs filter state\nNo physical-target truth or accuracy claim');ax.grid(axis='x',alpha=.2)
 ax=axes[1,1];file_counts=[records[m]['ownTwoHundredFiftySevenPlotSafety']['afterFileCount']for m in ['A','B']];bars=ax.bar(['A native','B ACTIVE'],file_counts,color=[color['A'],color['B']],width=.5);ax.set(ylim=(0,310),ylabel='Files after native caller',title='257 post-RF input plots: file-count difference\nNot a claim about 257 physical targets / RF resolution')
 for bar,n in zip(bars,file_counts):ax.text(bar.get_x()+bar.get_width()/2,n+7,str(n),ha='center')
 ax.text(.5,-.24,f'C55: {sum(c55_equal)}/{len(c55_equal)} native case states unchanged (player + NPC).\nC55 proposals remain shadow only; the bars concern own SPY.',transform=ax.transAxes,ha='center',fontsize=8);ax.grid(axis='y',alpha=.2)
 fig.suptitle('TRACK-B recorded native association evidence',fontsize=15,y=.98);fig.text(.5,.935,CLASSIFICATION,ha='center',fontsize=9,family='monospace');fig.text(.5,.906,'Direct anonymous ingress fixtures and existing native game methods; not natural RF or weapon-performance measurements.',ha='center',fontsize=9)
 fig.text(.07,.065,'Input SHA-256 A: '+sources['A']['dataSha256']+'\nInput SHA-256 B: '+sources['B']['dataSha256'],fontsize=6.7,family='monospace')
 fig.text(.07,.025,'Full product / fixture / helper source hashes and exact JSON pointers are in the companion CSV and SVG description metadata.',fontsize=8)
 svg=F/'native-association.svg';fig.savefig(svg,metadata={'Date':None,'Creator':'AEGIS TRACK-B plot_association.py','Title':CLASSIFICATION,'Description':dump(provenance)});plt.close(fig)
 # Matplotlib path formatting contains cosmetic trailing spaces; remove them
 # without changing numbers, labels or SVG geometry.
 svg.write_text('\n'.join(line.rstrip()for line in svg.read_text().splitlines())+'\n')
 print(json.dumps({'classification':CLASSIFICATION,'figure':str(svg.relative_to(P)),'svgSha256':sha(svg.read_bytes()),'csv':str(csv_path.relative_to(P)),'csvSha256':sha(csv_path.read_bytes()),'csvRows':len(rows),'dataSha256':{k:s['dataSha256']for k,s in sources.items()},'c55NativeCasesEqual':len(c55_equal),'kernelsExecuted':False}))

if __name__=='__main__':main()
