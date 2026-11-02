"""Quiescent final cost follow-up. Frozen game/original a173 fixtures unchanged.

One browser at a time; both cooperating browser leases held for all nine runs.
Only explicit passive state, existing native fixtures and CDP profiles are read.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse,fcntl,gzip,hashlib,importlib.util,json,os,time

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/cost-final'
sha=lambda x:hashlib.sha256(x).hexdigest()
PINS={'A':('Aegis_SIM_v48_WIP_TRACK_A.html','e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'),'B':('Aegis_SIM_v48_WIP_TRACK_B.html','0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6')}
FROZEN_RUNTIME='a173e069a62db844baa4d0dfd298e43209749c93dab5580deaecc30b76905523'

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
runtime=module('final_cost_original_runtime',P/'verify_runtime.py');support=runtime.support
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
def packed(path,value):
 raw=json.dumps(value,separators=(',',':')).encode();path.write_bytes(gzip.compress(raw,6,mtime=0));return {'path':str(path.relative_to(P)),'rawSha256':sha(raw),'gzipSha256':sha(path.read_bytes())}
def resource():
 out={}
 for name in ['memory.events','memory.current','memory.max']:
  try:out[name]=Path('/sys/fs/cgroup',name).read_text().strip()
  except OSError as ex:out[name]=str(ex)
 return out
def browser_mains():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');exe=(p/'exe').resolve().name.lower();stat=(p/'stat').read_text().split(') ',1)[1].split()
   if('chromium'in exe or'chrome'in exe)and'crashpad'not in exe and'--type='not in cmd:out.append({'pid':int(p.name),'ppid':int(stat[1]),'executable':exe})
  except(FileNotFoundError,PermissionError,ProcessLookupError):pass
 return out

@contextmanager
def exclusive_browser_budget():
 started=time.perf_counter();handles=[]
 while not handles:
  acquired=[]
  for slot in [0,1]:
   f=open(f'/dev/shm/aegis-track-b-browser-{slot}.lock','a+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired.append(f)
   except BlockingIOError:f.close();break
  if len(acquired)==2:handles=acquired;break
  for f in acquired:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  if time.perf_counter()-started>120:raise TimeoutError('Cannot obtain BOTH browser leases')
  time.sleep(.25)
 try:yield {'pid':os.getpid(),'slots':[0,1],'exclusiveForEntireMeasurement':True,'waitS':time.perf_counter()-started}
 finally:
  for f in handles:fcntl.flock(f,fcntl.LOCK_UN);f.close()

STATE_HELPER=r'''
// AFTER_ACTION_TEST_ONLY: original A physical/private-RNG/P schema plus scalar
// public survival snapshots. Never traverse live caches, profiles or closures.
window.__FINAL_COST_STATE__=()=>JSON.stringify({scope:'A_PASSIVE_PLUS_PUBLIC_SURVIVAL_SCALARS_AND_VECTORS',a:JSON.parse(__TRACK_RUNTIME_A__.state()),bodies:[...ENGAGEMENT_RUNTIME.ships.values()].map(r=>{const s=r.survival.snapshot(),values={},compositeFieldsNotTraversed=[];for(const[k,v]of Object.entries(s)){if(v===null||['number','boolean','string'].includes(typeof v))values[k]=v;else if(v&&['x','y','z'].every(a=>typeof v[a]==='number'))values[k]={x:v.x,y:v.y,z:v.z};else if(Array.isArray(v)&&v.length===3&&v.every(a=>typeof a==='number'))values[k]=v.slice();else compositeFieldsNotTraversed.push(k);}return {id:r.entityId,values,compositeFieldsNotTraversed};})});
'''

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');args=parser.parse_args();E.mkdir(parents=True,exist_ok=True)
 assert sha((P/'verify_runtime.py').read_bytes())==FROZEN_RUNTIME,'Frozen a173 runtime changed'
 for _,(name,pin)in PINS.items():assert sha((R/name).read_bytes())==pin,'Frozen product changed'
 cpu=[(0,'A',False),(0,'B',False),(0,'B',True),(1,'B',True),(1,'B',False),(1,'A',False)];allocation=[('A',False),('B',False),('B',True)]
 provenance={'schema':'AEGIS_TRACK_B_FINAL_COST_PROVENANCE_1','toolSha256':sha(Path(__file__).read_bytes()),'runtimeSha256':FROZEN_RUNTIME,'originalSources':runtime.provenance(),'products':PINS,'cpuOrder':cpu,'allocationOrder':allocation,'warmupSimSeconds':30,'cpuFixedTicks':2400,'ownerWarmupTicks':120,'ownerMeasuredTicks':600,'stateHelperSha256':sha(STATE_HELPER.encode()),'priorCostEvidence':'NOT_FINAL_FOR_COST_ASSESSMENT_RETAINED_UNCHANGED','estimatedWallMinutes':3.5,'productOrCoefficientChanges':False}
 save(E/'PROVENANCE.json',provenance)
 if not args.run:print(json.dumps(provenance,indent=2));return 0
 from playwright.sync_api import sync_playwright
 h=support.load_harness();helpers=(R/'docs/contact/friendly/A/repro.js').read_text()+'\n'+support.PASSIVE_HELPER+'\n'+support.ALLOCATION_HELPER+'\n'+STATE_HELPER
 raws={key:h.base.build(file=name,record=False,extra=helpers)for key,(name,_)in PINS.items()};rows=[];errors=[];start=time.perf_counter();initial_resource=resource()
 with exclusive_browser_budget()as lease:
  save(E/'LEASE.json',lease)
  for kind,configs in [('cpu',cpu),('allocation',[(0,key,on)for key,on in allocation])]:
   for repetition,product,enabled in configs:
    tag=f'{kind}-{repetition}-{product}-{"on"if enabled else"off"}';preflight={'browserMains':browser_mains(),'resource':resource(),'observedAtUnixS':time.time()};save(E/(tag+'-preflight.json'),preflight);assert not preflight['browserMains'],'Other active browser before exclusive run'
    server=None;at=time.perf_counter()
    with sync_playwright()as pw:
     browser=h.launch(pw)
     try:
      if kind=='allocation':
       from browser import load_fleet
       page=load_fleet(browser,raws[product],own='DDG_119_LATE_FLIGHT_IIA',ally='CG_52_LATE_TICONDEROGA',enemy=None,errors=errors)
      else:
       server,url=h.serve(raws[product]);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors)
      page.set_default_timeout(600000);page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear();if(window.__TRACK_B__){__TRACK_B__.configure({enabled:on,capacity:4096});__TRACK_B__.clear();}}',enabled)
      if kind=='cpu':page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',{'kind':'HELO','moving':True,'seconds':30,'observe':False,'seed':419010})
      else:page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)')
      session=page.context.new_cdp_session(page);heap_before=session.send('Runtime.getHeapUsage');sampling=None;cost=None;sample=None
      if kind=='allocation':
       sampling={'samplingInterval':32768,'includeObjectsCollectedByMajorGC':True,'includeObjectsCollectedByMinorGC':True};session.send('HeapProfiler.startSampling',sampling);page.evaluate('__TRACK_RUNTIME_A__.startCandidateCosts()')
      try:bench=page.evaluate('n=>__TRACK_RUNTIME_A__.bench(n)',2400 if kind=='cpu'else 600)
      finally:
       if kind=='allocation':cost=page.evaluate('__TRACK_RUNTIME_A__.stopCandidateCosts()')
      if kind=='allocation':
       profile=session.send('HeapProfiler.stopSampling')['profile']
       def total(node):return node.get('selfSize',0)+sum(total(c)for c in node.get('children',[]))
       sample={'sampledBytesEstimate':total(profile['head']),'sampleRecords':len(profile.get('samples',[])),'metric':'STATISTICAL_TOTAL_ALLOCATION_WITH_GC_COLLECTED_OBJECTS_INCLUDED_NOT_EXACT_BYTES','options':sampling,'profile':packed(E/(tag+'-heap-profile.json.gz'),profile)}
      heap_after=session.send('Runtime.getHeapUsage');session.detach();costs=bench.pop('costs');bench.pop('state');state_before=page.evaluate('__FINAL_COST_STATE__()');env=page.evaluate('__ENV_D__.status()');state_after=page.evaluate('__FINAL_COST_STATE__()');tick_count=bench['steps'];before,after=bench['beforeObserverTicks'],bench['afterObserverTicks'];checks={'expectedOwners':len(before)==len(after)==(1 if kind=='cpu'else 2),'ownersOncePerFixedTick':all(b['ticks']-a['ticks']==tick_count for a,b in zip(before,after)),'wrappersRestoredAndEnvStatusMatch':env['match']is True,'readOnlyQueriesPreserveState':state_before==state_after,'coreSelftestsZero':not page.evaluate('__CORE_SELFTEST_FAILURES__')}
      row={'kind':kind,'product':product,'trace':enabled,'repetition':repetition,'productSha256':PINS[product][1],'fixedTicks':tick_count,'warmupSimSeconds':30 if kind=='cpu'else 2,'meanTickMs':sum(costs)/len(costs),'medianTickMs':support.percentile(costs,.5),'p95TickMs':support.percentile(costs,.95),'costSamples':packed(E/(tag+'-tick-costs.json.gz'),costs),'stateSha256':sha(state_before.encode()),'state':packed(E/(tag+'-passive-state.json.gz'),json.loads(state_before)),'envStatus':env,'checks':checks,'timing':bench,'heapBefore':heap_before,'heapAfter':heap_after,'liveHeapDeltaBytes':heap_after['usedSize']-heap_before['usedSize'],'liveHeapMetric':'NET_LIVE_HEAP_NOT_TOTAL_CHURN','sampledAllocation':sample,'candidateKernelInclusiveCounters':cost,'kernelCounterCaveat':'Existing native calls only; nested inclusive counters/times overlap and must not be summed.','elapsedWallS':time.perf_counter()-at,'resourceAfter':resource(),'automaticApproval':False};rows.append(row);save(E/(tag+'.json'),row);print(tag,'mean',round(row['meanTickMs'],4),'p95',round(row['p95TickMs'],4),'checks',all(checks.values()),flush=True)
     finally:
      browser.close()
      if server:server.shutdown()
    assert not browser_mains(),'Browser process remains after close'
 cpu_rows=[r for r in rows if r['kind']=='cpu'];alloc_rows=[r for r in rows if r['kind']=='allocation'];checks={'allNineRunsComplete':len(rows)==9,'allNativeChecksPass':all(all(r['checks'].values())for r in rows),'cpuBodyTrackPAndPrivateRngExactAcrossAllConfigs':len({r['stateSha256']for r in cpu_rows})==1,'allocationBodyTrackPAndPrivateRngExactAcrossAllConfigs':len({r['stateSha256']for r in alloc_rows})==1,'browserErrorsZero':not errors,'browsersClosed':not browser_mains()};value={'schema':'AEGIS_TRACK_B_FINAL_COST_1','status':'PASS'if all(checks.values())else'FAIL','completionStatus':'COMPLETE','checks':checks,'exclusiveBrowserLease':lease,'records':rows,'browserErrors':errors,'initialResource':initial_resource,'finalResource':resource(),'wallS':time.perf_counter()-start,'oldCostEvidenceRetained':'NOT_FINAL_FOR_COST_ASSESSMENT','performanceApproved':False,'allocationMetric':'STATISTICAL_TOTAL_WITH_GC_COLLECTED_SAMPLES_INCLUDED','noCoefficientOrProductChanges':True,'releaseApproved':False};save(E/'SUMMARY.json',value);print(json.dumps({'status':value['status'],'checks':checks,'wallS':value['wallS']},indent=2));return 0 if value['status']=='PASS'else 1

if __name__=='__main__':raise SystemExit(main())
