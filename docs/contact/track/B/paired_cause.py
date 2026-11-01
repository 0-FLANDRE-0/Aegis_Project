"""Passive causal timeline for the ORIGINAL H4/HELI-F two raid fixtures.

Default: archived facts + frozen execution plan, NO browser. --run explicitly
executes A/SHADOW/ACTIVE after taking the shared two-browser lease. Products,
expectations and original fixture/helper modules are never written.
"""
from pathlib import Path
import argparse,ast,base64,gzip,hashlib,importlib.util,json,os,re,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3]
A=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
A_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
ORIGINAL=R/'docs/multiship/H4/regression_baseline.py'
HELI=R/'docs/helicopter/F/verify_regression.py'
ARCHIVE=P/'evidence/regression/paired-track-a/baseline-comparison.json'
HELPER=P/'paired_cause_passive.js'
SHIPS=['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']
sha=lambda b:hashlib.sha256(b).hexdigest()

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def packed_source(raw):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)</script>',raw)[1])).decode()

def original_raid_expression():
 """Extract the exact original JS constant; apply only HELI-F's existing readout."""
 values=[n.value for n in ast.walk(ast.parse(ORIGINAL.read_text()))if isinstance(n,ast.Constant)and isinstance(n.value,str)and n.value.startswith('scenario=>')]
 assert len(values)==1
 original=values[0];needle='dynamics:d.shipDynamics(),rng:'
 assert original.count(needle)==1
 expr=original.replace(needle,'dynamics:d.shipDynamics(),observers:d.observerSnapshotC(),offboard:d.offboardSnapshotC(),rng:',1)
 return original,expr

def instrument(raw):
 """Expose caches, not snapshots. Native tick body and original funcs preserved."""
 html=raw.decode();packed=re.search(r'data-c55-index="13">([^<]+)</script>',html);s=packed_source(raw);before=s
 changes=[
  ('return {basis,peek:(options={})=>cache?', 'return {__pairedCauseRead:()=>({dirty,revision,rebuilds,cacheHits,dirtyMarks,lastDirtyReason,massKg:cache?.massKg??null,cgX:cache?.cgM?.x??null,cgY:cache?.cgM?.y??null,cgZ:cache?.cgM?.z??null}),basis,peek:(options={})=>cache?'),
  ('reset();return {config:cfg,reset,haltHorizontalContact:', 'reset();return {__pairedCauseRead:()=>({massKg:diagnostic.massKg,loadedMassKg:diagnostic.loadedMassKg,ledgerRevision:diagnostic.ledgerRevision,waterMassKg:diagnostic.waterMassKg,cgX:diagnostic.cgM?.x??null,cgY:diagnostic.cgM?.y??null,cgZ:diagnostic.cgM?.z??null,draftM:diagnostic.draftM,gm0M:diagnostic.gm0M,effectiveGMM:diagnostic.effectiveGMM,buoyancyN:diagnostic.buoyancyN,weightN:diagnostic.weightN,rollRateRadS:diagnostic.rollRateRadS,trimRateRadS:diagnostic.trimRateRadS,draftRateMps:diagnostic.draftRateMps,rightingArmM:diagnostic.rightingArmM,hydroAge,stabilityAge,stabilityReferenceMassKg:stabilityReference?.massKg??null,stabilityReferenceDraftM:stabilityReference?.draftM??null}),config:cfg,reset,haltHorizontalContact:'),
  ('reset();return {config,reset,step,snapshot,restorePhysical};', 'reset();return {__pairedCauseRead:()=>({heelRad:pose.heelRad,trimRad:pose.trimRad,draftM:pose.draftM,state,timeS,phaseS,capTimer,sinkTimer,waterM3,imbalance}),config,reset,step,snapshot,restorePhysical};')]
 counts=[]
 for anchor,replacement in changes:
  assert s.count(anchor)==1,('Cache accessor anchor not unique',anchor,s.count(anchor))
  s=s.replace(anchor,replacement,1);counts.append({'anchor':anchor,'count':1,'kind':'TEST_ONLY_CACHE_REFERENCE_ACCESSOR'})
 base_anchor='  function simulateFixedTick(dt){';assert s.count(base_anchor)==1
 s=s.replace(base_anchor,'  window.__TRACK_B_PAIRED_CAUSE_BASE_FN__=simulateFixedTick; // TEST ONLY: retain reference, never invoke it separately.\n'+base_anchor,1)
 # MAP_D.mount executes after the MAP_B constructor: its wrapper is the
 # original fixture's final installed wrapper, despite earlier source position.
 wrapper=re.search(r'const native=simulateFixedTick;simulateFixedTick=(function\(dt\)\{step\(\);const value=native\(dt\);afterTick\(\);return value;\});',before)
 assert wrapper,'Existing mounted MAP_D native fixed-tick wrapper anchor changed'
 mark='\n  completeShipStartup();';assert s.count(mark)==1
 s=s.replace(mark,mark+'\n'+HELPER.read_text(),1)
 # All native simulateFixedTick body bytes are the same; only its caller binding
 # is wrapped after startup. The function is executed once with original args.
 native=lambda t:t[t.index('  function simulateFixedTick(dt){'):t.index('\n  // ===== WIP150 RUNTIME FAULT CONTAINMENT =====')].strip()
 assert native(before)==native(s),'Native fixed-tick body changed'
 gz=gzip.compress(s.encode(),9,mtime=0);html=html[:packed.start(1)]+base64.b64encode(gz).decode()+html[packed.end(1):]
 metadata=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(metadata[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(gz),sha256=sha(s.encode()))
 return (html[:metadata.start(1)]+json.dumps(records,separators=(',',':'))+html[metadata.end(1):]).encode(),{'accessors':counts,'nativeFixedTickBodyUnchanged':True,'existingNativeWrapperUnchanged':True,'sourceSha256':sha(before.encode()),'instrumentedSourceSha256':sha(s.encode()),'nativeFixedTickSha256':sha(native(before).encode()),'nativePipelineWrapperSha256':sha(wrapper[1].encode())}

def diffs(x,y,path=''):
 if type(x)!=type(y):yield {'path':path,'before':x,'after':y}
 elif isinstance(x,dict):
  for k in sorted(x.keys()|y.keys()):
   if k in ['performance','aviation']:continue
   if k not in x or k not in y:yield {'path':path+'/'+k,'beforePresent':k in x,'afterPresent':k in y,'before':x.get(k),'after':y.get(k)}
   else:yield from diffs(x[k],y[k],path+'/'+k)
 elif isinstance(x,list):
  if len(x)!=len(y):yield {'path':path+'/~length','before':len(x),'after':len(y)}
  for i in range(min(len(x),len(y))):yield from diffs(x[i],y[i],path+'/'+str(i))
 elif x!=y:yield {'path':path,'before':x,'after':y}

def archived_facts():
 if not ARCHIVE.exists():return {'status':'MISSING_ARCHIVE','causalProof':False}
 d=json.loads(ARCHIVE.read_text());rows=[]
 for case in d['cases']:
  if case['scenario']!='raid':continue
  a,b=case['pair']['baseline'],case['pair']['candidate'];dyn=list(diffs(a['dynamics'],b['dynamics']));obs=list(diffs(a['observers'],b['observers']))
  inventory_equal=a['state']['inventory']==b['state']['inventory']
  count=lambda r:sum(c['type']!='EMPTY'for cells in r['state']['inventory']['vls'].values()for c in cells)
  rows.append({'ship':case['ship'],'classification':'ARCHIVED_FINAL_STATE_NOT_TIMELINE','strictChecks':case['checks'],'run':[a['run'],b['run']],
   'rng':[a['rng'],b['rng']],'hp':[a['state']['shipHP'],b['state']['shipHP']],'loadedVls':[count(a),count(b)],'fullInventoryExact':inventory_equal,
   'afterActionTruth':{'baseline':a.get('afterActionTruth'),'candidate':b.get('afterActionTruth')},
   'physics':{k:[a['dynamics']['physics'].get(k),b['dynamics']['physics'].get(k)]for k in ['massKg','loadedMassKg','ledgerRevision','cgM','effectiveGMM','gm0M','stabilityReferenceMassKg','stabilityReferenceAgeS']},
   'pose':{'baseline':a['dynamics']['pose'],'candidate':b['dynamics']['pose']},'dynamicsDeltas':dyn,'observerDeltaCount':len(obs),'observerDeltaExamples':obs[:15],
   'firstChangedFixedTick':None,'causeConfirmed':False,'releaseApproved':False})
 return {'schema':'AEGIS_TRACK_B_PAIRED_CAUSE_ARCHIVED_FACTS_1','source':str(ARCHIVE.relative_to(R)),'sourceSha256':sha(ARCHIVE.read_bytes()),'baselineSha256':d['baselineSha256'],'candidateSha256':d['candidateSha256'],'rows':rows,'status':'STRICT_PAIRED_FAIL_UNAPPROVED','causalProof':False}

def timeline_comparison(rows_a,rows_b):
 by_a={r['ordinal']:r for r in rows_a};by_b={r['ordinal']:r for r in rows_b};categories=['rng','own','inventory','tracks','c55','missiles','observers'];first={};launches=[]
 for n in sorted(by_a.keys()&by_b.keys()):
  a,b=by_a[n],by_b[n]
  assert(a['step'],a['phase'])==(b['step'],b['phase']),('unaligned fixed ticks',n)
  for key in categories:
   if key not in first and a[key]!=b[key]:first[key]={'ordinal':n,'step':a['step'],'timeS':a['timeS'],'deltas':list(diffs(a[key],b[key]))[:32]}
  if n:
   previous_a=by_a[n-1];previous_b=by_b[n-1]
   for label,row,prev in [('baseline',a,previous_a),('candidate',b,previous_b)]:
    for key in ['newSam','newRam']:
     new=row['missiles'][key]
     if new:launches.append({'version':label,'step':row['step'],'timeS':row['timeS'],'collection':key,'newMissiles':new,'physics':row['own']['physics'],'mass':row['own']['mass']})
 return {'allTimelineGameplayFieldsExact':not first,'firstDifferentByCategory':first,'launchEvents':launches,'rowsCompared':len(by_a.keys()&by_b.keys()),'causalClaim':'Temporal precedence is evidence; not proof of a sole cause. Track changes are post-update estimates, not newly invented RF measurements.','releaseApproved':False}

def physical(v):
 if isinstance(v,dict):
  out={k:physical(x)for k,x in v.items()if k not in ['performance','aviation']}
  if v.get('schema')=='AEGIS_OFFBOARD_PORT_C_1':out.pop('helicopterImplemented',None);out['sources']=[x for x in out.get('sources',[])if x.get('sourceId')not in ['H1','H2']]
  if v.get('schema')=='AEGIS_SHIP_OBSERVER_C_1'and'deferred'in out:out['deferred']=[x for x in out['deferred']if x!='helicopterFlightAndSensors']
  return out
 if isinstance(v,list):return [physical(x)for x in v]
 return v

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B.html');p.add_argument('--candidate-sha');p.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html');p.add_argument('--shadow-sha');p.add_argument('--trace-b',action='store_true');p.add_argument('--only',choices=['baseline','shadow','active']);p.add_argument('--out',type=Path,default=P/'evidence/paired-cause');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 original,expr=original_raid_expression();products=[('baseline',A,A_SHA),('shadow',a.shadow,a.shadow_sha),('active',a.candidate,a.candidate_sha)]
 products=[x for x in products if not a.only or x[0]==a.only]
 provenance=[{'path':str(q.relative_to(R)),'sha256':sha(q.read_bytes())}for q in [ORIGINAL,HELI,R/'docs/bunkerhill/K/browser_i.py',R/'docs/gun/B2/phase1b/test_support/sitecustomize.py',HELPER,Path(__file__)]]
 facts=archived_facts();(a.out/'ARCHIVED_FACTS.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
 plan={'schema':'AEGIS_TRACK_B_PAIRED_CAUSE_PLAN_1','execution':'RUN_REQUESTED'if a.run else'DRY_RUN_NO_BROWSER','runs':len(products)*2,'products':[{'label':label,'path':str(file),'sha256':sha(file.read_bytes()),'requiredSha256':pinned}for label,file,pinned in products],'ships':SHIPS,'scenario':'raid','seed':0x6d2b79f5,'settings':{'viewport':[1000,760],'terrainBypass':True,'count':8,'label':'Kh-32','rangeKm':16,'bearingsDeg':[-60,-20,20,60],'mode':'AUTO','fps':60,'scale':8,'ticks':1920,'traceB':a.trace_b},'originalFixtureExpressionSha256':sha(original.encode()),'heliFReadoutExpressionSha256':sha(expr.encode()),'files':provenance,'originalFixtureCommandsChanged':False,'expectedValuesUpdated':False,'releaseApproved':False}
 (a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
 if not a.run:print(json.dumps({'status':'READY_NOT_EXECUTED','plan':str(a.out/'PLAN.json'),'archive':facts['status'],'browserStarted':False}));return 0
 assert os.environ.get('B2_PHASE1_REGRESSION')=='1','Run under the SAME original regression environment; see plan'
 assert sha(A.read_bytes())==A_SHA,'TRACK-A reference changed'
 for label,file,pinned in products:assert pinned and sha(file.read_bytes())==pinned,(label,'Frozen product SHA required')
 # Import the original loader after the identical sitecustomize environment.
 sys.path.insert(0,str(R/'docs/bunkerhill/K'));from browser_i import launch,load
 from playwright.sync_api import sync_playwright
 slots=module('paired_cause_shared_slots',P/'regression_runner.py');summaries=[];timelines={};errors=[];started=time.perf_counter()
 print(json.dumps({'startedPid':os.getpid(),'runs':len(products)*2,'traceB':a.trace_b,'fixture':'ORIGINAL_H4_HELI_F_RAID','productShas':{label:pinned for label,file,pinned in products}}),flush=True)
 for label,file,pinned in products:
  raw,instrumentation=instrument(file.read_bytes())
  for ship in SHIPS:
   with slots.heavy_browser_slot()as lease:
    with sync_playwright()as pw:
     browser=launch(pw);page=load(browser,raw,ship=ship,errors=errors);page.set_default_timeout(1200000)
     # Only diagnostic recording is configured; no live gate/mode changes.
     if label!='baseline':page.evaluate('on=>{__TRACK_B__.configure({enabled:on,capacity:4096});__TRACK_B__.clear()}',a.trace_b)
     ready=page.evaluate('__TRACK_B_PAIRED_CAUSE__.start()')
     preflight=page.evaluate('__TRACK_B_PAIRED_CAUSE__.info()')
     preflight_proof={'pipelineWrapperSha256':sha(preflight['nativeFixedTickSource'].encode()),'baseFixedTickSha256':sha(preflight['nativeBaseFixedTickSource'].encode()),'expected':instrumentation,'ready':ready}
     (a.out/(label+'-'+ship+'-PREFLIGHT_SOURCE_PROOF.json')).write_text(json.dumps(preflight_proof,indent=2)+'\n')
     assert preflight_proof['pipelineWrapperSha256']==instrumentation['nativePipelineWrapperSha256'],'Preflight: actual outer native pipeline wrapper differs'
     assert preflight_proof['baseFixedTickSha256']==instrumentation['nativeFixedTickSha256'],'Preflight: actual native base fixed tick differs'
     result=page.evaluate(expr,'raid')
     stopped=page.evaluate('__TRACK_B_PAIRED_CAUSE__.stop()');timeline=page.evaluate('__TRACK_B_PAIRED_CAUSE__.info()');native_sha=sha(timeline.pop('nativeFixedTickSource').encode());base_sha=sha(timeline.pop('nativeBaseFixedTickSource').encode());timeline['rows']=[]
     for start in range(0,timeline['count'],120):timeline['rows'].extend(json.loads(page.evaluate('args=>JSON.stringify(__TRACK_B_PAIRED_CAUSE__.read(args.start,args.count))',{'start':start,'count':120})))
     proof={'pipelineWrapperSha256':native_sha,'baseFixedTickSha256':base_sha,'expected':instrumentation,'stopped':stopped}
     (a.out/(label+'-'+ship+'-SOURCE_PROOF.json')).write_text(json.dumps(proof,indent=2)+'\n')
     assert native_sha==instrumentation['nativePipelineWrapperSha256'],'Actual invoked native pipeline wrapper differs'
     assert base_sha==instrumentation['nativeFixedTickSha256'],'Actual native base fixed-tick body differs'
     assert not timeline['faults']and not stopped['faults'],timeline['faults']
     assert len(timeline['rows'])==1921,(label,ship,'tick capture count',len(timeline['rows']))
     assert result['run']['steps']==1920
     archived=next(c for c in json.loads(ARCHIVE.read_text())['cases']if c['ship']==ship and c['scenario']=='raid')
     ref=archived['pair']['baseline'if label=='baseline'else'candidate']if label!='shadow'else None
     archive_match=None if ref is None else {k:physical(result[k])==physical(ref[k])for k in ['state','dynamics','observers','offboard','rng']}
     tag=label+'-'+ship;path=a.out/(tag+'.json.gz');path.write_bytes(gzip.compress(json.dumps(timeline,separators=(',',':')).encode(),6,mtime=0));(a.out/(tag+'-result.json')).write_text(json.dumps(result,indent=2)+'\n');timelines[(label,ship)]=timeline['rows']
     cache=timeline['rows'][-1]['own']['physics'];native=result['dynamics']['physics'];cache_match=all(cache[k]==native.get(k)for k in cache if k not in ['cgX','cgY','cgZ','hydroAge','stabilityAge'])and all(cache['cg'+axis.upper()]==native['cgM'][axis]for axis in ['x','y','z'])
     summaries.append({'label':label,'ship':ship,'productSha256':pinned,'instrumentation':instrumentation,'nativePipelineInvokedSourceSha256':native_sha,'nativeBaseFixedTickSourceSha256':base_sha,'ready':ready,'stopped':stopped,'timeline':path.name,'uncompressedTimelineBytes':len(json.dumps(timeline,separators=(',',':')).encode()),'traceB':a.trace_b,'originalArchivedFinalFieldsExact':archive_match,'cachedBoundaries':{'initial':timeline['rows'][0]['own'],'end':timeline['rows'][-1]['own']},'cachedEndMatchesOriginalFinalPhysics':cache_match,'lease':lease,'resultSha256':sha(json.dumps(physical({k:result[k]for k in ['state','dynamics','observers','offboard','rng']}),sort_keys=True,separators=(',',':')).encode())})
     page.context.close();browser.close();print(json.dumps({'label':label,'ship':ship,'rows':1921,'archiveMatch':archive_match,'elapsedS':time.perf_counter()-started}),flush=True)
   assert sha(file.read_bytes())==pinned,'Product changed during execution'
 comparisons=[]
 for ship in SHIPS:
  for before,after in [('baseline','shadow'),('baseline','active'),('shadow','active')]:
   if(before,ship)in timelines and(after,ship)in timelines:comparisons.append({'ship':ship,'before':before,'after':after,**timeline_comparison(timelines[(before,ship)],timelines[(after,ship)])})
 report={'schema':'AEGIS_TRACK_B_PAIRED_CAUSE_RESULTS_1','status':'CAUSAL_EVIDENCE_NOT_APPROVAL'if not errors else'INCOMPLETE','runs':summaries,'comparisons':comparisons,'errors':errors,'wallS':time.perf_counter()-started,'expectedValuesUpdated':False,'strictPairedFailureApproved':False,'releaseApproved':False}
 (a.out/'SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'wallS':report['wallS'],'releaseApproved':False}));return 0 if not errors else 1

if __name__=='__main__':raise SystemExit(main())
