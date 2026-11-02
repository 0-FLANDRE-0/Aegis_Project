"""TRACK-A actual-product equivalence, passive trace, clock and cost checks.

Original friendly scripts/fixtures are invoked without changed assertions. The
only adapters select the HTML and redirect evidence writes. Private helpers below
read game state AFTER_ACTION_TEST_ONLY; they never feed it to a live consumer.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,importlib.util,json,os,re,runpy,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];F=R/'docs/contact/friendly/A'
E=P/'evidence/candidate';BASE=R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html';CANDIDATE=R/'Aegis_SIM_v48_WIP_TRACK_A.html';B=P/'evidence/baseline/friendly'
sha=lambda b:hashlib.sha256(b).hexdigest()
BASE_SHA='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'

def read_json(path):return json.loads(path.read_text())
def json_lines(path):
 if not path.exists():path=Path(str(path)+'.gz')
 with(gzip.open(path,'rt')if path.suffix=='.gz'else path.open())as f:return [json.loads(l)for l in f]
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,separators=(',',':'))+'\n')
def load_harness():
 spec=importlib.util.spec_from_file_location('track_a_friendly_native_harness',F/'harness.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);return h

def redirect_existing():
 old=(F/'evidence').absolute();new=(E/'friendly').absolute();original_open=Path.open;original_mkdir=Path.mkdir
 def mapped(p):
  p=Path(p)
  try:return new/p.absolute().relative_to(old)
  except ValueError:return p
 def opening(p,mode='r',*a,**kw):
  p=Path(p)
  if p.absolute()==BASE.absolute()and not any(x in mode for x in 'wax+'):p=CANDIDATE
  else:
   dst=mapped(p)
   if dst!=p:
    if any(x in mode for x in 'wax+'):original_mkdir(dst.parent,parents=True,exist_ok=True)
    elif not dst.exists():dst=p
   p=dst
  return original_open(p,mode,*a,**kw)
 def mkdir(p,*a,**kw):return original_mkdir(mapped(p),*a,**kw)
 Path.open=opening;Path.mkdir=mkdir

PASSIVE_HELPER=r'''
// AFTER_ACTION_TEST_ONLY. Explicit passive reads, never control inputs.
function taPrimitiveTree(o,depth=0){
 if(o==null||['number','string','boolean'].includes(typeof o))return o;
 if(depth>4)return null;
 if(ArrayBuffer.isView(o))return Array.from(o);
 if(Array.isArray(o))return o.map(x=>taPrimitiveTree(x,depth+1));
 if(o instanceof Map)return Array.from(o,([k,v])=>[k,taPrimitiveTree(v,depth+1)]);
 const keys=['id','kind','type','label','weaponType','guidanceCore','ownerSide','alive','dead','x','y','z','vx','vy','vz','heading','speed','speedMps','pitch','roll','life','maxLife','boosterSeparated','fuel','age','ageS','state','spare','onboard','positionM','velocityMps','groundVelocityMps','navPositionM','targetAltitudeM','rng','rngState','_rng','_rngState','seed','stateTick','rotor01','engine01','iffOn','radarMode'];
 return Object.fromEntries(keys.filter(k=>k in o).map(k=>[k,taPrimitiveTree(o[k],depth+1)]));
}
function taTrackState(t){return {id:t.trackId,number:t.trackNumber,state:t._kfX?Array.from(t._kfX):null,P:t._kfP?Array.from(t._kfP):null,age:t.sensorAge,hits:t.sensorHits,confirmed:t.confirmed,domain:t.domain,classification:t.classification,identity:t.identity,operator:t._operatorIdentity??null,authority:t.engagementAuthority,source:t.sensorSource,ttl:t.ttl,memory:t.memActive,iff:t.iffF?{...t.iffF}:null,surfacePrior:t._surfaceMotionPriorWip13B13??null,air3dStep:t._radar3dAirStepFC??null};}
function taPassiveState(){
 const ships=Array.from(ENGAGEMENT_RUNTIME.ships.values()).map(r=>{const o=r.combatSystem.observerC;return {id:r.entityId,navigation:JSON.parse(JSON.stringify(r.navigation)),observer:o?{rng:JSON.parse(JSON.stringify(o.rng)),ticks:o.tickCount,lastTick:o.lastTick,cycles:o.cycles,rotors:{...o.rotors},stats:{...o.stats},tracks:[...o.tracks.values()].map(taTrackState),iff:o.heloIffE?taPrimitiveTree(o.heloIffE):null}:null};});
 return JSON.stringify({tag:'AFTER_ACTION_TEST_ONLY',step:simStepCounter,rng:{global:SIM_RNG_STATE,visual:VIS_RNG_STATE,battlespace:BATTLESPACE_RNG_STATE,bme:BRIDGEMASTER_E_RNG_STATE,chaff:AIR_CHAFF_RNG_STATE,spySurface:SPY_SURFACE_RNG_STATE_WIP13B9,spySpare:SPY_SURFACE_RNG_SPARE_WIP13B9,spqSurface:SPQ9B_SURFACE_RNG_STATE_WIP13B1,rf:{...SHIPBOARD_RADAR_RF_RNG_WIP13B13}},shipHP,vls:vlsCells,ships,tracks:[...tracks.values()].map(taTrackState),ciws:ciws.map(m=>({id:m.id,ammo:m.ammo,state:m.state,trackId:m.trackingTrackId,sensorRng:CIWS_C55.banks.get(m.id)?.rng??null,aimRng:m._gunAimRngState??null,shotRng:m._gunShotRngState??null})),entities:Object.fromEntries(Object.entries(ENGAGEMENT_RUNTIME.world.entities).map(([k,v])=>[k,taPrimitiveTree(v)]))});
}
window.__TRACK_RUNTIME_A__={state:taPassiveState,
 observerTicks:()=>Array.from(ENGAGEMENT_RUNTIME.ships.values()).map(r=>({id:r.entityId,ticks:r.combatSystem.observerC?.tickCount??null,lastTick:r.combatSystem.observerC?.lastTick??null})),
 bench(n=2400){const costs=[],counts=[],start=performance.now(),before=this.observerTicks();for(let i=0;i<n;i++){const t=performance.now();simulateFixedTick(SIM_FIXED_DT);costs.push(performance.now()-t);if(i%60===59)counts.push(tracks.size);}return {costs,counts,steps:n,wallMs:performance.now()-start,beforeObserverTicks:before,afterObserverTicks:this.observerTicks(),state:taPassiveState()};}
};
'''

TRACE_WATCH_HELPER=r'''
// TEST-ONLY overflow coverage. Read each ALREADY-created diagnostic record,
// never rerun an association/gate or sample a physical/RNG function.
const taTraceWatch={total:0,types:{},kinds:{},decisions:{},gates:0,nisRejects:0,states:0,finalSources:0,examples:[],rejectedExamples:[]};
const taNativeTraceEvent=trackATraceEventA;
trackATraceEventA=function(){const before=TRACK_A_DIAG.serial,q=taNativeTraceEvent.apply(this,arguments);if(TRACK_A_DIAG.serial>before&&TRACK_A_DIAG.size){const r=TRACK_A_DIAG.ring[(TRACK_A_DIAG.head-1+TRACK_A_DIAG.capacity)%TRACK_A_DIAG.capacity];if(r){taTraceWatch.total++;taTraceWatch.types[r.type]=(taTraceWatch.types[r.type]??0)+1;if(r.measurement){const k=r.measurement.kind;taTraceWatch.kinds[k]=(taTraceWatch.kinds[k]??0)+1;}if(r.decision!=null)taTraceWatch.decisions[r.decision]=(taTraceWatch.decisions[r.decision]??0)+1;if(r.nis!=null||r.gate!=null)taTraceWatch.gates++;if(r.before||r.after)taTraceWatch.states++;if(r.finalSource!=null)taTraceWatch.finalSources++;if(taTraceWatch.examples.length<20)taTraceWatch.examples.push(JSON.parse(JSON.stringify(r)));if(Number.isFinite(r.nis)&&Number.isFinite(r.gate)&&r.nis>r.gate){taTraceWatch.nisRejects++;if(taTraceWatch.rejectedExamples.length<24)taTraceWatch.rejectedExamples.push(JSON.parse(JSON.stringify(r)));}}}return q;};
__TRACK_RUNTIME_A__.traceSummary=()=>JSON.parse(JSON.stringify(taTraceWatch));
'''

ALLOCATION_HELPER=r'''
// TEST-ONLY pass-through counters around exactly one ORIGINAL evaluation.
// Inclusive nested timings are reported separately, never summed as CPU totals.
const taCostOriginals={air:trackRadarAssociationNisV31,surface:trackSurfaceRadarAssociationNisV35,surfacePosition:trackSurfacePositionAssociationNisWip13B9,cartesian:trackCartesianAssociationNisV33};
const taCostStats={};
function taCountKernel(name,original){taCostStats[name]={calls:0,totalInclusiveMs:0,maxInclusiveMs:0};return function(){const at=performance.now();try{return original.apply(this,arguments);}finally{const dt=performance.now()-at,s=taCostStats[name];s.calls++;s.totalInclusiveMs+=dt;s.maxInclusiveMs=Math.max(s.maxInclusiveMs,dt);}};}
__TRACK_RUNTIME_A__.startCandidateCosts=()=>{trackRadarAssociationNisV31=taCountKernel('air',taCostOriginals.air);trackSurfaceRadarAssociationNisV35=taCountKernel('surface',taCostOriginals.surface);trackSurfacePositionAssociationNisWip13B9=taCountKernel('surfacePosition',taCostOriginals.surfacePosition);trackCartesianAssociationNisV33=taCountKernel('cartesian',taCostOriginals.cartesian);};
__TRACK_RUNTIME_A__.stopCandidateCosts=()=>{trackRadarAssociationNisV31=taCostOriginals.air;trackSurfaceRadarAssociationNisV35=taCostOriginals.surface;trackSurfacePositionAssociationNisWip13B9=taCostOriginals.surfacePosition;trackCartesianAssociationNisV33=taCostOriginals.cartesian;return JSON.parse(JSON.stringify(taCostStats));};
'''

def digest_state(page):return sha(page.evaluate('__TRACK_RUNTIME_A__.state()').encode())
def capture_trace(page,name,game_before):
 first=page.evaluate('__TRACK_A__.snapshot()');second=page.evaluate('__TRACK_A__.snapshot()');game_after=digest_state(page)
 assert first==second,'snapshot query changed diagnostics'
 assert game_before==game_after,'snapshot query changed game state'
 assert len(first['records'])<=first['capacity']<=4096
 assert first['stats']['errors']==0,'trace sink failed'
 forbidden={'truthRef','objectId','entityId','rfId','_truthObject','_physicsKind','_sourceSeed','faction','owner','ownerSide','ownerEntityId','truth','alive','dead','seeker','ins','navPositionM','actualPositionM','targetId','targetEntityId','truthTrack'}
 def privacy(value,at='$'):
  if isinstance(value,dict):
   for k,v in value.items():assert k not in forbidden,(at,k);privacy(v,at+'.'+k)
  elif isinstance(value,list):
   for i,x in enumerate(value):privacy(x,at+f'[{i}]')
 privacy(first)
 all_records=page.evaluate('__TRACK_RUNTIME_A__.traceSummary()');privacy(all_records)
 rows=first['records'];kinds=sorted({r.get('measurement',{}).get('kind')for r in rows if r.get('measurement')});decisions=sorted({str(r.get('decision'))for r in rows if r.get('decision')is not None});routes=sorted({str(r.get('route'))for r in rows if r.get('route')is not None})
 gates=[r for r in rows if 'nis'in r or 'gate'in r];states=[r for r in rows if 'before'in r or 'after'in r]
 applied=[r for r in rows+all_records.get('examples',[])+all_records.get('rejectedExamples',[])if 'appliedFields'in r]
 for r in applied:
  assert len(r['appliedFields'])==r.get('appliedDimension'),('applied dimension mismatch',r)
  if r.get('gateUnits')=='METERS':assert 'nis'not in r,('distance gate mislabeled NIS',r)
  if r.get('gateUnits')=='NIS'and 'nis'in r:assert r['nis']>=0,('negative NIS',r)
 raw=json.dumps(first,separators=(',',':')).encode();path=E/(name+'-trace.json.gz');path.write_bytes(gzip.compress(raw,6,mtime=0))
 save(E/(name+'-all-trace-summary.json'),all_records)
 assert all_records['total']>0 and all_records['gates']>0 and all_records['states']>0 and all_records['finalSources']>0,(name,'incomplete native trace coverage',all_records)
 return {'path':str(path.relative_to(P)),'records':len(rows),'capacity':first['capacity'],'stats':first['stats'],'kinds':kinds,'decisions':decisions,'routes':routes,'gateRecords':len(gates),'stateRecords':len(states),'appliedDimensionConsistentRecords':len(applied),'allRecordCoverage':{k:v for k,v in all_records.items()if k not in ['examples','rejectedExamples']},'snapshotExact':True,'gameStateQueryUnchanged':True,'forbiddenFields':0,'sha256':sha(raw)}

def native_cases(trace=False):
 from playwright.sync_api import sync_playwright
 h=load_harness();errors=[];extra=(R/'docs/ciws/dmg/A/diagnostic.js').read_text()+'\n'+(F/'repro.js').read_text()+'\n'+PASSIVE_HELPER+'\n'+TRACE_WATCH_HELPER
 raw=h.base.build(file=CANDIDATE.name,record=False,extra=extra);server,url=h.serve(raw);records=[];start=time.perf_counter()
 try:
  with sync_playwright()as pw:
   browser=h.launch(pw)
   cases=[('helo-hover',{'kind':'HELO','moving':False,'seconds':60},'CG_52_LATE_TICONDEROGA'),('helo-route',{'kind':'HELO','moving':True,'seconds':120},'CG_52_LATE_TICONDEROGA'),('harpoon-route',{'kind':'HARPOON','seconds':75},'CG_52_LATE_TICONDEROGA')]
   for i,(name,c,ship)in enumerate(cases):
    page=h.load_fast_http(browser,url,own=ship,errors=errors);page.set_default_timeout(600000);initial=page.evaluate('__TRACK_A__.snapshot()');assert initial['enabled']is False
    if trace:page.evaluate('__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear()')
    result=page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',c);game=digest_state(page);tag='on'if trace else'off';save(E/(name+'-'+tag+'.json'),result)
    if trace:
     before=read_json(E/(name+'-off.json'));assert result==before,(name,'trace changed native result');off_state=read_json(E/(name+'-off-state.json'));assert game==off_state['sha256'],(name,'private RNG/physical state changed')
     diagnostic=capture_trace(page,name,game)
    else:
     baseline=read_json(B/f'after-{i}.json');assert result==baseline,(name,'candidate changed fresh baseline reproduction');save(E/(name+'-off-state.json'),{'sha256':game,'tag':'AFTER_ACTION_TEST_ONLY'});diagnostic={'defaultOff':initial['enabled']is False,'baselineExact':True}
    if not trace:
     quiet=page.evaluate('__TRACK_A__.snapshot()');assert quiet['stats']['recorded']==0 and quiet['records']==[],'default-OFF producer allocated trace records'
    core=page.evaluate('__CORE_SELFTEST_FAILURES__');assert not core
    env=page.evaluate('__ENV_D__.status()');assert env['match']is True
    row={'name':name,'trace':trace,'stateSha256':game,'core':core,'envMatch':env['match'],'diagnostic':diagnostic};records.append(row);page.context.close();print(name,tag,'exact',round(time.perf_counter()-start,1),flush=True)
   if trace:
    page=h.load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(600000);page.evaluate('__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear()');r=page.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419025});sig=r.pop('equivalenceSignature');sig_sha=sha(sig.encode());ordinary=next(x for x in json_lines(E/'friendly/ciws-d1.jsonl')if x['case']['seed']==419025);assert sig_sha==ordinary['signatureSha256'];game=digest_state(page);diag=capture_trace(page,'ciws419025',game);save(E/'trace419025-on.json',{'case':{'seed':419025},'signatureSha256':sig_sha,'passiveStateSha256':game,**r});page.context.close()
    off=h.load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);off.set_default_timeout(600000);r_off=off.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419025});off_signature=sha(r_off.pop('equivalenceSignature').encode());off_state=digest_state(off);assert off_signature==sig_sha and off_state==game,'419025 trace changed RF/private RNG/physical state';save(E/'trace419025-off.json',{'case':{'seed':419025},'signatureSha256':off_signature,'passiveStateSha256':off_state,**r_off});off.context.close()
    records.append({'name':'ciws419025','trace':True,'signatureSha256':sig_sha,'passiveStateSha256':game,'offSignatureExact':True,'offPrivateRngAndPhysicalStateExact':True,'diagnostic':diag,'result':r['result']});print('ciws419025 on exact',round(time.perf_counter()-start,1),flush=True)
   browser.close()
 finally:server.shutdown()
 assert not errors,errors
 save(E/('trace-on.json'if trace else'reproduction-off.json'),{'status':'PASS','records':records,'errors':errors,'wallS':time.perf_counter()-start,'productSha256':sha(CANDIDATE.read_bytes()),'usesActualProductFunctions':True,'changedFixtureAssertions':False})

def percentile(a,p):
 a=sorted(a);return a[min(len(a)-1,max(0,int((len(a)-1)*p)))]
def performance():
 from playwright.sync_api import sync_playwright
 h=load_harness();rows=[];errors=[];start=time.perf_counter()
 # Every page gets the same original native moving-helicopter setup/warmup.
 for repetition in [0,1]:
  order=[('baseline',False),('candidate',False),('candidate',True)]if repetition==0 else[('candidate',True),('candidate',False),('baseline',False)]
  for product,trace in order:
   file=BASE if product=='baseline'else CANDIDATE;raw=h.base.build(file=file.name,record=False,extra=(F/'repro.js').read_text()+'\n'+PASSIVE_HELPER);server,url=h.serve(raw)
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000)
     if product=='candidate':page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear()}',trace)
     page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',{'kind':'HELO','moving':True,'seconds':30,'observe':False,'seed':419010})
     session=page.context.new_cdp_session(page);heap_before=session.send('Runtime.getHeapUsage');result=page.evaluate('__TRACK_RUNTIME_A__.bench(2400)');heap_after=session.send('Runtime.getHeapUsage');session.detach()
     costs=result.pop('costs');state=result.pop('state');state_sha=sha(state.encode());core=page.evaluate('__CORE_SELFTEST_FAILURES__');assert not core
     for a,b in zip(result['beforeObserverTicks'],result['afterObserverTicks']):
      if a['ticks']is not None:assert b['ticks']-a['ticks']==2400,(product,trace,a,b)
     summary={'repetition':repetition,'product':product,'trace':trace,'productSha256':sha(file.read_bytes()),'steps':2400,'warmupS':30,'meanTickMs':sum(costs)/len(costs),'medianTickMs':percentile(costs,.5),'p95TickMs':percentile(costs,.95),'heapBefore':heap_before,'heapAfter':heap_after,'liveHeapDeltaBytes':heap_after['usedSize']-heap_before['usedSize'],'heapMetric':'CDP live JS heap delta; NOT total allocations; GC can make this negative','stateSha256':state_sha,'observerOncePerTick':True,'trackCountMin':min(result['counts']),'trackCountMax':max(result['counts']),'core':core,'timing':result}
     rows.append(summary);save(E/f'performance-{repetition}-{product}-{"on"if trace else"off"}.json',summary);page.context.close();browser.close();print('performance',repetition,product,trace,summary['meanTickMs'],summary['p95TickMs'],flush=True)
   finally:server.shutdown()
  hashes={r['stateSha256']for r in rows if r['repetition']==repetition};assert len(hashes)==1,('performance state/RNG mismatch',hashes)
 assert not errors
 means={}
 for key in ['baseline-off','candidate-off','candidate-on']:
  product,mode=key.split('-');selected=[r for r in rows if r['product']==product and r['trace']==(mode=='on')];means[key]={'meanTickMs':sum(r['meanTickMs']for r in selected)/len(selected),'p95TickMs':sum(r['p95TickMs']for r in selected)/len(selected),'liveHeapDeltasBytes':[r['liveHeapDeltaBytes']for r in selected]}
 baseline=means['baseline-off']['meanTickMs'];means['candidateOffMeanOverheadPercent']=(means['candidate-off']['meanTickMs']/baseline-1)*100;means['candidateOnMeanOverheadPercent']=(means['candidate-on']['meanTickMs']/baseline-1)*100
 save(E/'performance.json',{'status':'PASS','equivalentState':True,'costAcceptance':'MEASURED_FOR_REVIEW_NOT_AUTOMATICALLY_APPROVED','summary':means,'records':rows,'errors':errors,'wallS':time.perf_counter()-start,'notes':['Two fresh-page repetitions, 30 native seconds warmup per page,2400 timed native fixed ticks.','Order reversed on repetition2. Timers and heap reads are test-only.','CDP live heap deltas are NOT allocation counts; no claim of exact allocation rate.']})

def allocation_and_owners():
 from playwright.sync_api import sync_playwright
 h=load_harness()
 # Existing original deployment UI loader supports a native allied ship choice.
 from browser import load_fleet
 rows=[];errors=[];start=time.perf_counter()
 for product,trace in [('baseline',False),('candidate',False),('candidate',True)]:
  file=BASE if product=='baseline'else CANDIDATE;raw=h.base.build(file=file.name,record=False,extra=PASSIVE_HELPER+'\n'+ALLOCATION_HELPER)
  with sync_playwright()as pw:
   browser=h.launch(pw);page=load_fleet(browser,raw,own='DDG_119_LATE_FLIGHT_IIA',ally='CG_52_LATE_TICONDEROGA',enemy=None,errors=errors);page.set_default_timeout(600000)
   if product=='candidate':page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear()}',trace)
   page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)');before=page.evaluate('__TRACK_RUNTIME_A__.observerTicks()');assert len(before)==2,('native allied deployment failed',before)
   session=page.context.new_cdp_session(page);sampling={'samplingInterval':32768,'includeObjectsCollectedByMajorGC':True,'includeObjectsCollectedByMinorGC':True}
   try:session.send('HeapProfiler.startSampling',sampling)
   except Exception as ex:
    sampling={'samplingInterval':32768};sampling['unsupportedCollectionOptions']=str(ex)
    session.send('HeapProfiler.startSampling',{'samplingInterval':32768})
   page.evaluate('__TRACK_RUNTIME_A__.startCandidateCosts()')
   try:bench=page.evaluate('__TRACK_RUNTIME_A__.bench(600)')
   finally:cost=page.evaluate('__TRACK_RUNTIME_A__.stopCandidateCosts()')
   profile=session.send('HeapProfiler.stopSampling')['profile'];session.detach();after=page.evaluate('__TRACK_RUNTIME_A__.observerTicks()')
   assert len(after)==len(before)==2
   for a,b in zip(before,after):assert a['id']==b['id']and b['ticks']-a['ticks']==600,('observer did not advance exactly once per native tick',a,b)
   restored=page.evaluate('__ENV_D__.status()');assert restored['match']is True,'native wrappers were not restored'
   state=bench.pop('state');bench.pop('costs');state_sha=sha(state.encode());profile_path=E/f'alloc-{product}-{"on"if trace else"off"}.json.gz';profile_raw=json.dumps(profile,separators=(',',':')).encode();profile_path.write_bytes(gzip.compress(profile_raw,6,mtime=0))
   def profile_bytes(node):return node.get('selfSize',0)+sum(profile_bytes(c)for c in node.get('children',[]))
   row={'product':product,'trace':trace,'productSha256':sha(file.read_bytes()),'fixture':'NATIVE_PREDEPARTURE_UI_DDG_PLUS_ALLIED_CG_NO_FORCED_WORLD_INSERTION','warmupTicks':120,'profiledNativeTicks':600,'observerBefore':before,'observerAfter':after,'observerOncePerTick':True,'stateSha256':state_sha,'allocationMetric':'STATISTICAL_ESTIMATE_FROM_CHROMIUM_HEAP_SAMPLING_NOT_EXACT_ALLOCATION_COUNT','allocationSampling':sampling,'sampledAllocationBytesEstimate':profile_bytes(profile['head']),'samplingRecords':len(profile.get('samples',[])),'samplingProfile':str(profile_path.relative_to(P)),'nativeCandidateKernels':cost,'kernelTimingNote':'Inclusive wall CPU proxy around one original call. Nested kernel timings overlap and are not additive. Separate from primary unwrapped CPU benchmark.','nativeFunctionsRestored':True,'envMatch':restored['match'],'trackCountMin':min(bench['counts']),'trackCountMax':max(bench['counts'])}
   rows.append(row);page.context.close();browser.close();print('allocation/owners',product,trace,'exact2owners',row['sampledAllocationBytesEstimate'],cost,round(time.perf_counter()-start,1),flush=True)
 assert len({r['stateSha256']for r in rows})==1,'allocation/cost observer changed physical/private RNG state'
 assert not errors,errors
 save(E/'allocation-and-owners.json',{'status':'PASS','records':rows,'equivalentPhysicalAndPrivateRngState':True,'twoOwnersEachOncePerTick':True,'measurementsApproved':False,'metricLimitations':['Heap sampling is a statistical estimate, not an exact count of allocated bytes.','Pass-through kernel counter/timers add observer cost; primary CPU benchmark excludes them.','Single short sample per configuration; do not approve performance or tune coefficients from these numbers alone.'],'errors':errors,'wallS':time.perf_counter()-start})

def native_ingress():
 from playwright.sync_api import sync_playwright
 h=load_harness();helper=P/'native_ingress.js';assert helper.exists(),'native ingress helper not available';source=helper.read_text();rows=[];errors=[];start=time.perf_counter()
 for product,trace in [('baseline',False),('candidate',False),('candidate',True)]:
  file=BASE if product=='baseline'else CANDIDATE;extra=source+'\n'+PASSIVE_HELPER+('\n'+TRACE_WATCH_HELPER if product=='candidate'else'');raw=h.base.build(file=file.name,record=False,extra=extra);server,url=h.serve(raw)
  try:
   with sync_playwright()as pw:
    browser=h.launch(pw);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000)
    if product=='candidate':page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear()}',trace)
    result=page.evaluate('__TRACK_NATIVE_INGRESS_A__.run()');save(E/f'ingress-{product}-{"on"if trace else"off"}.json',result);assert result['pass']and all(result['checks'].values())and not result['errors']and not result['core'],('native ingress fixture failed',product,trace,result['checks'],result['errors']);state_hash=digest_state(page)
    observed={k:v for k,v in result.items()if k!='traceSnapshot'}
    if rows:assert observed==rows[0]['nativeOutputs'],'native ingress changed baseline outputs';assert state_hash==rows[0]['stateSha256'],'native ingress changed game/private RNG state'
    diagnostic=capture_trace(page,'native-ingress',state_hash)if trace else{'enabled':False}
    row={'product':product,'trace':trace,'sourceSha256':sha(source.encode()),'productSha256':sha(file.read_bytes()),'classification':'DIRECT_NATIVE_ANONYMOUS_INGRESS_FIXTURE_NOT_NATURAL_RF','nativeOutputs':observed,'stateSha256':state_hash,'traceEvidence':diagnostic,'pass':True};rows.append(row);page.context.close();browser.close();print('native-ingress',product,trace,len(result['checks']),'exact',round(time.perf_counter()-start,1),flush=True)
  finally:server.shutdown()
 assert not errors,errors
 save(E/'native-ingress.json',{'status':'PASS','fixtureOnly':True,'naturalRfOrWeaponEvidence':False,'records':rows,'sourceSha256':sha(source.encode()),'errors':errors,'wallS':time.perf_counter()-start,'unchangedNativeOutputs':True,'unchangedPhysicalAndPrivateRngState':True})

def worker(task):
 E.mkdir(parents=True,exist_ok=True)
 if task in ['d1','repro-original','auto-iff','idle']:
  redirect_existing();sys.path.insert(0,str(F));file=F/({'d1':'ciws.py','repro-original':'repro.py','auto-iff':'auto_iff.py','idle':'idle_and_dom.py'}[task]);sys.argv=[str(file),*(['d1']if task=='d1'else['--current']if task=='repro-original'else[])];runpy.run_path(str(file),run_name='__main__');return
 if task=='repro':return native_cases(False)
 if task=='trace':return native_cases(True)
 if task=='performance':return performance()
 if task=='allocation':return allocation_and_owners()
 if task=='ingress':return native_ingress()
 if task=='clocks':
  env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':CANDIDATE.name,'B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'}
  raise SystemExit(subprocess.run([sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(CANDIDATE),str(E/'harpoon-clock'),'--only','harpoon-clock'],cwd=R,env=env).returncode)
 raise ValueError(task)

def compare_d1():
 baseline=json_lines(B/'ciws-d1.jsonl');candidate=json_lines(E/'friendly/ciws-d1.jsonl');assert len(baseline)==len(candidate)==30;rows=[]
 for a,b in zip(baseline,candidate):
  assert a['case']['seed']==b['case']['seed'];same=a['signatureSha256']==b['signatureSha256'];rows.append({'seed':b['case']['seed'],'sameSignature':same,'baseline':a['signatureSha256'],'candidate':b['signatureSha256'],'shipHits':b['result']['shipHits'],'hp':b['result']['hpAfter'],'result':b['result']})
 out={'status':'PASS'if all(r['sameSignature']for r in rows)else'FAIL','rows':rows,'freshBaseline':True,'unapproved419025Preserved':next(r for r in rows if r['seed']==419025)['shipHits']==1,'expectedValuesChanged':False};save(E/'d1-equivalence.json',out);assert out['status']=='PASS'

def compare_control(task):
 if task=='auto-iff':
  a=read_json(B/'auto-iff.json');b=read_json(E/'friendly/auto-iff.json');assert a['checks']==b['checks']and a['result']==b['result']and not b['errors'];checks=b['checks'];same=True
 elif task=='idle':
  a=read_json(B/'idle-and-dom.json');b=read_json(E/'friendly/idle-and-dom.json');assert a['checks']==b['checks']and a['rows']==b['rows']and not b['errors'];checks=b['checks'];same=True
 else:return
 save(E/(task+'-equivalence.json'),{'status':'PASS','freshBaselineExact':same,'checks':checks,'newFixtureAssertions':0,'source':'original friendly/A script with HTML/output selection only'})

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sha',required=True,help='Root-frozen candidate SHA, prevents unreviewed live changes');ap.add_argument('--worker');ap.add_argument('--only',nargs='+');a=ap.parse_args();assert BASE.exists()and sha(BASE.read_bytes())==BASE_SHA;assert CANDIDATE.exists()and sha(CANDIDATE.read_bytes())==a.sha,'candidate not frozen at requested SHA'
 if a.worker:return worker(a.worker)
 E.mkdir(parents=True,exist_ok=True);rows=[];start=time.perf_counter()
 jobs=a.only or ['d1','repro','trace','auto-iff','idle','clocks','performance']
 destination=E/('additional-'+'-'.join(jobs)+'-execution.json')if a.only else E/'execution.json'
 for task in jobs:
  at=time.perf_counter();command=[sys.executable,'-u',str(Path(__file__).resolve()),'--sha',a.sha,'--worker',task]
  with(E/(task+'.log')).open('w')as log:
   try:r=subprocess.run(command,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=1500);code=r.returncode
   except subprocess.TimeoutExpired:code=124
  row={'task':task,'exitCode':code,'wallS':time.perf_counter()-at,'command':command};rows.append(row)
  assert sha(CANDIDATE.read_bytes())==a.sha,'product changed while tests were running'
  if task=='d1'and code==0:
   try:compare_d1()
   except Exception as ex:row['exitCode']=1;row['comparisonError']=repr(ex)
  if task in ['auto-iff','idle']and code==0:
   try:compare_control(task)
   except Exception as ex:row['exitCode']=1;row['comparisonError']=repr(ex)
  save(destination,{'schema':'AEGIS_TRACK_A_CANDIDATE_RUNTIME_1','candidateSha256':a.sha,'rows':rows,'wallS':time.perf_counter()-start,'releaseApproved':False,'existingUnapprovedDeltasNotWaived':True});print(row,flush=True)
  if row['exitCode']:raise SystemExit(row['exitCode'])
 raise SystemExit(0)

if __name__=='__main__':main()
