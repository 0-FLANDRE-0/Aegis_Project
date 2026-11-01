"""TRACK-B runtime controller over original A/friendly native game fixtures.

Default is a read-only plan. Workers require pinned ACTIVE and SHADOW products.
Original scripts/assertions are never edited; raw native observations are saved
before strict comparisons. Differences are evidence, never automatic approval.
All private state below is AFTER_ACTION_TEST_ONLY and never a live input.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,os,re,runpy,subprocess,sys,time,traceback

P=Path(__file__).resolve().parent;R=P.parents[3];A=P.parent/'A';F=R/'docs/contact/friendly/A'
ROOT_E=P/'evidence/runtime';REFERENCE=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
REFERENCE_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
sha=lambda value:hashlib.sha256(value).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
support=module('track_b_original_runtime_helpers',A/'verify_runtime.py')
slots=module('track_b_runtime_browser_lease',P/'regression_runner.py')
TASKS=['d1','repro','trace','auto-iff','idle','clocks','performance','allocation']
CASES=[('helo-hover',{'kind':'HELO','moving':False,'seconds':60}),('helo-route',{'kind':'HELO','moving':True,'seconds':120}),('harpoon-route',{'kind':'HARPOON','seconds':75})]

def read(path):return json.loads(path.read_text())
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,separators=(',',':'))+'\n')
def compressed(path,value):
 raw=json.dumps(value,separators=(',',':')).encode();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(raw,6,mtime=0));return {'path':str(path.relative_to(P)),'sha256':sha(raw),'gzipSha256':sha(path.read_bytes())}
def differences(before,after):
 """Full JSON differences; no observer/physical/covariance fields excluded."""
 missing=object();out=[]
 def item(a,b,path):
  out.append({'path':path,'beforePresent':a is not missing,'afterPresent':b is not missing,'before':None if a is missing else a,'after':None if b is missing else b,
   'hostTimingOrHeapField':path.endswith(('/elapsedMs','/wallS','/meanTickMs','/medianTickMs','/p95TickMs','/usedSize','/totalSize'))})
 def walk(a,b,path=''):
  if a is missing or b is missing:
   if (a is not missing and isinstance(a,(dict,list))and not a)or(b is not missing and isinstance(b,(dict,list))and not b):item(a,b,path)
   elif isinstance(a,dict)or isinstance(b,dict):
    for k in sorted(a if a is not missing else b):walk(a.get(k,missing)if a is not missing else missing,b.get(k,missing)if b is not missing else missing,path+'/'+str(k).replace('~','~0').replace('/','~1'))
   elif isinstance(a,list)or isinstance(b,list):
    for i in range(len(a if a is not missing else b)):walk(a[i]if a is not missing else missing,b[i]if b is not missing else missing,path+'/'+str(i))
   else:item(a,b,path)
  elif type(a)is not type(b):item(a,b,path)
  elif isinstance(a,dict):
   for k in sorted(set(a)|set(b)):walk(a.get(k,missing),b.get(k,missing),path+'/'+str(k).replace('~','~0').replace('/','~1'))
  elif isinstance(a,list):
   if len(a)!=len(b):item(len(a),len(b),path+'/~length')
   for i in range(max(len(a),len(b))):walk(a[i]if i<len(a)else missing,b[i]if i<len(b)else missing,path+'/'+str(i))
  elif a!=b:item(a,b,path)
 walk(before,after);return out

FULL_STATE_HELPER=r'''
// AFTER_ACTION_TEST_ONLY. Recursively copy every own enumerable track/observer
// field, in addition to the unchanged A passive physical/private-RNG snapshot.
// No values are supplied to the simulation; diagnostics themselves excluded.
function tbFullTree(o,ancestors=new Set(),depth=0){
 if(o===null||['string','boolean'].includes(typeof o))return o;
 if(typeof o==='number')return Number.isFinite(o)?o:String(o);
 if(typeof o==='undefined')return '[UNDEFINED]';
 if(typeof o==='function')return '[FUNCTION_NOT_EVALUATED]';
 if(depth>20)return '[DEPTH_LIMIT_20]';
 if(ancestors.has(o))return '[CYCLE]';
 const next=new Set(ancestors);next.add(o);
 if(ArrayBuffer.isView(o))return Array.from(o,x=>tbFullTree(x,next,depth+1));
 if(o instanceof Map)return {map:[...o].map(([k,v])=>[tbFullTree(k,next,depth+1),tbFullTree(v,next,depth+1)])};
 if(o instanceof Set)return {set:[...o].map(v=>tbFullTree(v,next,depth+1))};
 if(Array.isArray(o))return o.map(v=>tbFullTree(v,next,depth+1));
 return Object.fromEntries(Object.keys(o).sort().map(k=>[k,tbFullTree(o[k],next,depth+1)]));
}
window.__TRACK_RUNTIME_B_TEST__={state:()=>JSON.stringify({tag:'AFTER_ACTION_TEST_ONLY',scope:'Original A passive physics/private RNG plus ALL enumerable local track/observer fields; depth/cycle markers explicit',a:JSON.parse(__TRACK_RUNTIME_A__.state()),tracks:[...tracks].map(([id,tr])=>[id,tbFullTree(tr)]),owners:[...ENGAGEMENT_RUNTIME.ships].map(([id,r])=>({id,observer:tbFullTree(r.combatSystem.observerC)}))})};
'''

def state(page):return page.evaluate('__TRACK_RUNTIME_B_TEST__.state()')
def configure_trace(page,label,enabled):
 return page.evaluate('c=>{__TRACK_A__.configure({enabled:c.enabled,capacity:4096});__TRACK_A__.clear();if(window.__TRACK_B__){__TRACK_B__.configure({enabled:c.enabled,capacity:4096});__TRACK_B__.clear();}return {a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null}}',{'enabled':enabled,'label':label})
def privacy(value):
 forbidden={'truthRef','objectId','entityId','rfId','_truthObject','_physicsKind','_sourceSeed','faction','owner','ownerSide','ownerEntityId','truth','alive','dead','seeker','ins','navPositionM','actualPositionM','targetId','targetEntityId','truthTrack'}
 if isinstance(value,dict):
  for key,val in value.items():
   if key in forbidden:raise AssertionError('Diagnostic forbidden field '+key)
   privacy(val)
 elif isinstance(value,list):
  for val in value:privacy(val)
def query(page,out,name):
 before=state(page);one=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})');two=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})');after=state(page)
 privacy(one);raw=compressed(out/(name+'-diagnostic.json.gz'),one)
 checks={'snapshotRepeatedExact':one==two,'gameAndPrivateStateUnchanged':before==after,'forbiddenFieldsAbsent':True,'aSinkErrorsZero':one['a']['stats']['errors']==0,'bSinkErrorsZero':one['b']is None or one['b']['stats']['errors']==0}
 return {'checks':checks,'status':'PASS'if all(checks.values())else'FAIL','raw':raw,'aRecords':len(one['a']['records']),'bRecords':len(one['b']['records'])if one['b']else 0,'aStats':one['a']['stats'],'bMode':one['b']['mode']if one['b']else None,'bDropped':one['b']['stats']['dropped']if one['b']else None}

def original_script(task,label,file,out):
 """Verbatim friendly scripts with only HTML/evidence path redirection."""
 support.E=out;support.CANDIDATE=file
 support.redirect_existing();sys.path.insert(0,str(F));name={'d1':'ciws.py','auto-iff':'auto_iff.py','idle':'idle_and_dom.py'}[task]
 path=F/name;sys.argv=[str(path),*(['d1']if task=='d1'else[])];exit_code=0
 try:runpy.run_path(str(path),run_name='__main__')
 except SystemExit as ex:exit_code=ex.code or 0
 # Preserve original output before comparisons, including every failed check.
 baseline=A/'evidence/candidate/friendly'
 if task=='d1':
  before=support.json_lines(baseline/'ciws-d1.jsonl');after=support.json_lines(out/'friendly/ciws-d1.jsonl');rows=[]
  for old,new in zip(before,after):
   rows.append({'seed':new['case']['seed'],'sameSignature':old['signatureSha256']==new['signatureSha256'],'beforeSignature':old['signatureSha256'],'afterSignature':new['signatureSha256'],'fullRawDifferences':differences(old,new),'shipHits':new['result']['shipHits'],'hpAfter':new['result']['hpAfter']})
  execution=read(out/'friendly/ciws-d1-execution.json')
  checks={'thirtyOriginalCases':len(before)==len(after)==30,'sameSeeds':all(a['case']==b['case']for a,b in zip(before,after)),'allOriginalSignaturesExact':all(r['sameSignature']for r in rows),'inherited419025ShipHitRetained':next((r for r in rows if r['seed']==419025),{}).get('shipHits')==1,'browserErrorsZero':not execution['errors']}
  value={'checks':checks,'rows':rows,'419025ReleaseApproval':False,'referenceEvidence':'HASH_VERIFIED_FINAL_TRACK_A_PUBLISHED_NATIVE_RESULTS','hostElapsedFieldsRetainedButNotAddedToOriginalSignatureAssertion':True}
 elif task=='auto-iff':
  before=read(baseline/'auto-iff.json');after=read(out/'friendly/auto-iff.json');checks={'originalChecksPassed':all(after['checks'].values()),'originalChecksExact':before['checks']==after['checks'],'originalNativeResultExact':before['result']==after['result'],'browserErrorsZero':not after['errors']}
  value={'checks':checks,'allRawDifferences':differences(before,after),'nativeResult':after}
 else:
  before=read(baseline/'idle-and-dom.json');after=read(out/'friendly/idle-and-dom.json');checks={'originalChecksPassed':all(after['checks'].values()),'originalChecksExact':before['checks']==after['checks'],'originalRowsExact':before['rows']==after['rows'],'browserErrorsZero':not after['errors']}
  value={'checks':checks,'allRawDifferences':differences(before,after),'nativeResult':after}
 value.update(status='PASS'if exit_code==0 and all(value['checks'].values())else'FAIL',originalExitCode=exit_code,product=label,productSha256=sha(file.read_bytes()),assertionsOrExpectedValuesChanged=False,releaseApproved=False)
 save(out/(task+'-comparison.json'),value)
 return 0 if value['status']=='PASS'else 1

def natural(label,file,out,trace):
 from playwright.sync_api import sync_playwright
 h=support.load_harness();extra=(R/'docs/ciws/dmg/A/diagnostic.js').read_text()+'\n'+(F/'repro.js').read_text()+'\n'+support.PASSIVE_HELPER+'\n'+FULL_STATE_HELPER
 raw=h.base.build(file=file.name,record=False,extra=extra);server,url=h.serve(raw);errors=[];rows=[];tag='on'if trace else'off';started=time.perf_counter();special_ok=True;special=None
 try:
  with sync_playwright()as pw:
   browser=h.launch(pw)
   for name,case in CASES:
    page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000)
    defaults=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})');configure_trace(page,label,trace)
    result=page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',case);passive=state(page);state_value=json.loads(passive)
    save(out/(name+'-'+tag+'.json'),result);raw_state=compressed(out/(name+'-'+tag+'-full-state.json.gz'),state_value)
    expected=read(A/'evidence/candidate'/(name+'-off.json'));original_match=result==expected
    comparisons={'originalTrackAResultExact':original_match,'defaultADiagnosticsOff':not defaults['a']['enabled'],'defaultBDiagnosticsOff':defaults['b']is None or not defaults['b']['enabled'],'coreSelftestsZero':not page.evaluate('__CORE_SELFTEST_FAILURES__'),'envHashMatch':page.evaluate('__ENV_D__.status().match')is True}
    if trace:
     before=read(out/(name+'-off.json'));off_state=json.loads(gzip.decompress((out/(name+'-off-full-state.json.gz')).read_bytes()))
     comparisons.update(traceResultExact=result==before,traceFullGameAndPrivateStateExact=state_value==off_state)
     delta=differences(off_state,state_value);against='SAME_PRODUCT_TRACE_OFF'
    else:
     ref=ROOT_E/'baseline'/(name+'-off-full-state.json.gz')
     delta=differences(json.loads(gzip.decompress(ref.read_bytes())),state_value)if ref.exists()else[];against='FRESH_TRACK_A'if ref.exists()else'REFERENCE_FULL_STATE_NOT_YET_CAPTURED'
     if label=='shadow':comparisons['shadowFullStateExactlyTrackA']=ref.exists()and not delta
    detail=compressed(out/(name+'-'+tag+'-deltas.json.gz'),{'against':against,'stateDifferences':delta,'originalFixtureDifferences':differences(expected,result),'automaticApproval':False})
    diagnostic=query(page,out,name+'-'+tag);comparisons.update({'query.'+k:v for k,v in diagnostic['checks'].items()})
    quiet=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})')
    if not trace:comparisons['defaultOffNoRecords']=quiet['a']['stats']['recorded']==0 and not quiet['a']['records']and(quiet['b']is None or not quiet['b']['records'])
    row={'name':name,'trace':trace,'product':label,'productSha256':sha(file.read_bytes()),'checks':comparisons,'status':'PASS'if all(comparisons.values())else'FAIL','stateSha256':sha(passive.encode()),'fullStateEvidence':raw_state,'fullStateDifferenceCount':len(delta),'differences':detail,'diagnostic':diagnostic,'nativeBirths':sum(x['requested']is None and x['id']is not None for x in result['births']),'maxFiles':max(len(x['tracks'])for x in result['samples']),'finalFiles':len(result['final'])}
    rows.append(row);save(out/('trace-on.json'if trace else'reproduction-off.json'),{'status':'PASS'if all(r['status']=='PASS'for r in rows)and not errors else'FAIL','records':rows,'errors':errors,'wallS':time.perf_counter()-started,'productSha256':sha(file.read_bytes()),'allThreeCasesComplete':len(rows)==3,'releaseApproved':False});page.context.close();print(label,name,tag,row['status'],len(delta),round(time.perf_counter()-started,1),flush=True)
   if trace:
    pair=[]
    for enabled in [False,True]:
     page=h.load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(600000);configure_trace(page,label,enabled)
     result=page.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419025});signature=result.pop('equivalenceSignature');passive=state(page)
     evidence={'signatureSha256':sha(signature.encode()),'fullStateSha256':sha(passive.encode()),'nativeResult':result,'diagnostic':query(page,out,'ciws419025-'+('on'if enabled else'off')),'fullState':compressed(out/('ciws419025-'+('on'if enabled else'off')+'-full-state.json.gz'),json.loads(passive))};pair.append(evidence);save(out/('ciws419025-'+('on'if enabled else'off')+'.json'),evidence);page.context.close()
    checks={'sameSignature':pair[0]['signatureSha256']==pair[1]['signatureSha256'],'sameFullStateAndPrivateRng':pair[0]['fullStateSha256']==pair[1]['fullStateSha256'],'inherited419025ShipHitRetained':pair[0]['nativeResult']['result']['shipHits']==1,'diagnosticQueryPure':all(all(r['diagnostic']['checks'].values())for r in pair)}
    special_ok=all(checks.values());special={'status':'PASS'if special_ok else'FAIL','checks':checks,'records':pair,'releaseApproved':False,'inheritedCombatFailureNotSolvedByTraceEquivalence':True};save(out/'ciws419025-trace-comparison.json',special)
   browser.close()
 finally:server.shutdown()
 passed=all(r['status']=='PASS'for r in rows)and not errors and special_ok
 save(out/('trace-on.json'if trace else'reproduction-off.json'),{'status':'PASS'if passed else'FAIL','records':rows,'ciws419025':special,'errors':errors,'wallS':time.perf_counter()-started,'productSha256':sha(file.read_bytes()),'allThreeCasesComplete':len(rows)==3,'releaseApproved':False})
 return 0 if passed else 1

def clocks(label,file,out):
 env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':file.name,'B2_OUT':str(out),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'}
 return subprocess.run([sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(file),str(out/'harpoon-clock'),'--only','harpoon-clock'],cwd=R,env=env).returncode

def measured(label,file,out,owners=False):
 """Original A setups/bench helpers, preserving changed owner states for review."""
 from playwright.sync_api import sync_playwright
 h=support.load_harness();extra=(F/'repro.js').read_text()+'\n'+support.PASSIVE_HELPER+'\n'+support.ALLOCATION_HELPER+'\n'+FULL_STATE_HELPER
 rows=[];errors=[];started=time.perf_counter()
 configurations=[(0,False),(0,True)]if owners else[(0,False),(0,True),(1,True),(1,False)]
 for repetition,enabled in configurations:
  raw=h.base.build(file=file.name,record=False,extra=extra)
  with sync_playwright()as pw:
   browser=h.launch(pw)
   if owners:
    from browser import load_fleet
    page=load_fleet(browser,raw,own='DDG_119_LATE_FLIGHT_IIA',ally='CG_52_LATE_TICONDEROGA',enemy=None,errors=errors);server=None
   else:
    server,url=h.serve(raw);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors)
   try:
    page.set_default_timeout(600000);configure_trace(page,label,enabled)
    if owners:page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)')
    else:page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',{'kind':'HELO','moving':True,'seconds':30,'observe':False,'seed':419010})
    ticks=600 if owners else 2400;session=page.context.new_cdp_session(page);heap_before=session.send('Runtime.getHeapUsage');sampling=None
    if owners:
     sampling={'samplingInterval':32768};session.send('HeapProfiler.startSampling',sampling);page.evaluate('__TRACK_RUNTIME_A__.startCandidateCosts()')
    result=page.evaluate('n=>__TRACK_RUNTIME_A__.bench(n)',ticks);costs=result.pop('costs');result.pop('state');native_cost=None;allocation=None
    if owners:
     native_cost=page.evaluate('__TRACK_RUNTIME_A__.stopCandidateCosts()');profile=session.send('HeapProfiler.stopSampling')['profile']
     def sample_bytes(node):return node.get('selfSize',0)+sum(sample_bytes(c)for c in node.get('children',[]))
     allocation={'sampledBytesEstimate':sample_bytes(profile['head']),'sampleRecords':len(profile.get('samples',[])),'raw':compressed(out/f'alloc-{repetition}-{enabled}.json.gz',profile),'metric':'STATISTICAL_HEAP_SAMPLING_NOT_EXACT_ALLOCATION_COUNT'}
    heap_after=session.send('Runtime.getHeapUsage');session.detach();passive=state(page);env=page.evaluate('__ENV_D__.status()');before=result['beforeObserverTicks'];after=result['afterObserverTicks'];checks={'ownerCountExact':len(before)==len(after)==(2 if owners else 1),'ownersEachExactlyOncePerFixedTick':all(a['id']==b['id']and(a['ticks']is None or b['ticks']-a['ticks']==ticks)for a,b in zip(before,after)),'nativeFunctionsRestoredAndEnvHashMatch':env['match']is True,'coreSelftestsZero':not page.evaluate('__CORE_SELFTEST_FAILURES__')}
    row={'product':label,'productSha256':sha(file.read_bytes()),'trace':enabled,'repetition':repetition,'steps':ticks,'meanTickMs':sum(costs)/len(costs),'medianTickMs':support.percentile(costs,.5),'p95TickMs':support.percentile(costs,.95),'allCosts':compressed(out/f'tick-costs-{repetition}-{enabled}.json.gz',costs),'heapBefore':heap_before,'heapAfter':heap_after,'liveHeapDeltaBytes':heap_after['usedSize']-heap_before['usedSize'],'heapMetric':'LIVE_HEAP_DELTA_NOT_TOTAL_ALLOCATION; may be negative due GC','sampledAllocation':allocation,'kernelInclusiveCounters':native_cost,'nestedCostWarning':'Nested calls overlap; do not sum as unique candidates or total CPU.','checks':checks,'stateSha256':sha(passive.encode()),'fullState':compressed(out/f'measured-{owners}-{repetition}-{enabled}-state.json.gz',json.loads(passive)),'timing':result,'query':query(page,out,f'measured-{owners}-{repetition}-{enabled}')};rows.append(row);save(out/('allocation-and-owners.json'if owners else'performance.json'),{'status':'PENDING','records':rows,'errors':errors,'releaseApproved':False});print(label,'owners'if owners else'performance',repetition,enabled,round(row['meanTickMs'],3),flush=True)
   finally:
    page.context.close();browser.close()
    if server:server.shutdown()
 checks={'allNativeChecksPassed':all(all(r['checks'].values())and all(r['query']['checks'].values())for r in rows),'sameProductTraceFullStateExact':len({r['stateSha256']for r in rows})==1,'browserErrorsZero':not errors};comparisons=[]
 baseline=ROOT_E/'baseline'/('allocation-and-owners.json'if owners else'performance.json')
 if label!='baseline'and baseline.exists():
  base=read(baseline)['records']
  for row in rows:
   match=next((r for r in base if r['trace']==row['trace']and r['repetition']==row['repetition']),None)
   if match:
    left=json.loads(gzip.decompress((P/match['fullState']['path']).read_bytes()));right=json.loads(gzip.decompress((P/row['fullState']['path']).read_bytes()));delta=differences(left,right)
    comparisons.append({'trace':row['trace'],'repetition':row['repetition'],'sameState':not delta,'fullDelta':compressed(out/f'measured-{owners}-{row["repetition"]}-{row["trace"]}-delta.json.gz',delta),'differingLeaves':len(delta),'automaticApproval':False})
 if label=='shadow':checks['shadowFullStateExactlyTrackA']=bool(comparisons)and all(r['sameState']for r in comparisons)
 result={'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'records':rows,'versusFreshTrackA':comparisons,'crossProductStateDifferencesApproved':False,'errors':errors,'wallS':time.perf_counter()-started,'releaseApproved':False,'costAcceptance':'MEASURED_ONLY_NOT_AUTOMATIC_APPROVAL','limitations':['All samples/outliers retained. Concurrent host load can reverse timing signs; no reliable speedup conclusion.','Live heap delta is not allocation count. Heap sampling is a statistical estimate.','Original association kernels are wrapped exactly once; inclusive nested timers/counters overlap.','Foreign/NPC association changes remain raw deltas, not an automatic full-state PASS or ignored fields.']}
 save(out/('allocation-and-owners.json'if owners else'performance.json'),result);return 0 if result['status']=='PASS'else 1

def provenance():
 files=[A/'verify_runtime.py',F/'harness.py',F/'ciws.py',F/'repro.py',F/'repro.js',F/'auto_iff.py',F/'idle_and_dom.py',R/'docs/ciws/dmg/A/diagnostic.js',R/'docs/ciws/dmg/A/protection-trace.js']
 rows=[];head=slots.source_head()
 for path in files:
  relative=str(path.relative_to(R));current=sha(path.read_bytes());old=sha(subprocess.check_output(['git','show',head+':'+relative],cwd=R));rows.append({'path':relative,'sha256':current,'referenceSha256':old,'unchanged':current==old})
 return {'status':'PASS'if all(r['unchanged']for r in rows)else'INCOMPLETE','files':rows,'controllerSha256':sha(Path(__file__).read_bytes()),'sharedRegressionRunnerSha256':sha((P/'regression_runner.py').read_bytes()),'AReadOnlyPassiveHelperSha256':sha(support.PASSIVE_HELPER.encode()),'BTestOnlyFullStateHelperSha256':sha(FULL_STATE_HELPER.encode()),'assertionChanges':False,'expectedValuesUpdated':False}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B.html');ap.add_argument('--sha');ap.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html');ap.add_argument('--shadow-sha');ap.add_argument('--products',nargs='+',choices=['baseline','shadow','active'],default=['baseline','shadow','active']);ap.add_argument('--only',nargs='+',choices=TASKS);ap.add_argument('--worker',choices=TASKS);ap.add_argument('--product',choices=['baseline','shadow','active']);ap.add_argument('--run',action='store_true');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
 products={'baseline':(REFERENCE,REFERENCE_SHA),'shadow':(args.shadow.resolve(),args.shadow_sha),'active':(args.candidate.resolve(),args.sha)};reference=slots.reference_evidence();sources=provenance();jobs=args.only or TASKS
 if not args.run and not args.worker:
  print(json.dumps({'dryRun':True,'browserProcessesStarted':0,'referenceStatus':reference['status'],'sourceProvenance':sources,'products':[{'label':p,'file':str(products[p][0]),'requiredSha256':products[p][1]}for p in args.products],'tasks':jobs,'globalBrowserLimit':2,'thisControllerParallel':1,'releaseApproved':False},indent=2));return
 for label,(file,pinned)in products.items():assert pinned and sha(file.read_bytes())==pinned,(label,'Frozen product SHA mismatch')
 assert reference['status']=='PASS'and sources['status']=='PASS','Reference or original fixture provenance mismatch'
 if args.worker:
  assert args.product;label=args.product;file,pinned=products[label];out=ROOT_E/label;out.mkdir(parents=True,exist_ok=True)
  if args.worker in ['d1','auto-iff','idle']:code=original_script(args.worker,label,file,out)
  elif args.worker in ['repro','trace']:code=natural(label,file,out,args.worker=='trace')
  elif args.worker=='clocks':code=clocks(label,file,out)
  elif args.worker in ['performance','allocation']:code=measured(label,file,out,args.worker=='allocation')
  assert sha(file.read_bytes())==pinned,'Product changed during runtime worker';raise SystemExit(code)
 ROOT_E.mkdir(parents=True,exist_ok=True);save(ROOT_E/'source-provenance.json',sources);save(ROOT_E/'reference-evidence.json',reference);rows=[];started=time.perf_counter();destination=ROOT_E/'execution.json'
 if args.resume and destination.exists():
  old=read(destination);assert old['candidateSha256']==args.sha and old['shadowSha256']==args.shadow_sha;rows=old['rows']
 for product in args.products:
  for task in jobs:
   if any(r['product']==product and r['task']==task for r in rows):continue
   at=time.perf_counter();command=[sys.executable,'-u',str(Path(__file__).resolve()),'--candidate',str(args.candidate.resolve()),'--sha',args.sha,'--shadow',str(args.shadow.resolve()),'--shadow-sha',args.shadow_sha,'--product',product,'--worker',task]
   with slots.heavy_browser_slot()as lease:
    with(ROOT_E/(product+'-'+task+'.log')).open('w')as log:
     try:result=subprocess.run(command,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=1800);code=result.returncode
     except subprocess.TimeoutExpired:code=124
   row={'product':product,'task':task,'exitCode':code,'status':'PASS'if code==0 else'INCOMPLETE'if code==124 else'FAIL','command':command,'wallS':time.perf_counter()-at,'lease':lease,'candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'deltaApproved':False};rows.append(row)
   summary={'schema':'AEGIS_TRACK_B_RUNTIME_EXECUTION_1','candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'referenceSha256':REFERENCE_SHA,'rows':rows,'allRequestedTasksExecuted':len(rows)==len(args.products)*len(jobs),'status':'PASS'if all(r['status']=='PASS'for r in rows)else'FAIL','wallS':time.perf_counter()-started,'releaseApproved':False,'inherited419025AndPairedDifferencesNotApproved':True,'assertionsChanged':False,'expectedValuesUpdated':False};save(destination,summary);print(json.dumps(row),flush=True)
 # Continue after strict failures so all independent raw observations survive.
 raise SystemExit(1 if any(r['status']!='PASS'for r in rows)else 0)

if __name__=='__main__':main()
