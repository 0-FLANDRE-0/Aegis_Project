"""TRACK-A: unchanged existing broad regressions, bounded browser lanes.

Native scripts/assertions and the existing retired-node/CPU2D adapters remain
unchanged. Paths/output/configuration only. No approved expectation replacement.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,os,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression'
HTML=R/'Aegis_SIM_v48_WIP_TRACK_A.html';BASE=R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'
EXPECTED='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
BASE_SHA='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'
sha=lambda b:hashlib.sha256(b).hexdigest()
NATIVE={
 'helicopter-flight':('docs/helicopter/J/verify_native.py','native.json',85),
 'aps153':('docs/helicopter/G/verify_native.py','native.json',20),
 'isar-native':('docs/helicopter/L/verify_native.py','native.json',36),
 'isar-classes':('docs/helicopter/L/verify_classes.py','classes.json',8),
 'isar-clock':('docs/helicopter/L/verify_clock.py','clock.json',12),
 'isar-ui':('docs/helicopter/L/verify_ui.py','ui.json',38),
 'emcon-native':('docs/helicopter/K/verify_native.py','native.json',27),
 'harpoon-f1':('docs/helicopter/H/verify_native.py','native.json',46),
 'harpoon-clock':('docs/helicopter/H/verify_ui_clock.py','ui-clock.json',24),
 'sov-native':('docs/sovremenny/A/verify_native.py','native.json',30),
 'sov-casualty':('docs/sovremenny/A/verify_casualty.py','casualty.json',13),
 'sov-deployment':('docs/sovremenny/A/verify_deployment.py','deployment.json',15),
 'sov-visual':('docs/sovremenny/A/verify_visual.py','visual.json',10),
}
assert sum(x[2]for x in NATIVE.values())==364

def environment():return {**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1',
 'NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules',
 'B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':HTML.name,'B2_OUT':str(E),
 'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'}

def job(name):
 if name in NATIVE or name=='emcon-ui':
  return [sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(HTML),str(E/name),'--only',name]
 if name=='paired-friendly':return [sys.executable,'-u',str(R/'docs/helicopter/F/verify_regression.py'),str(BASE),str(HTML),str(E/name),'--baseline-only']
 if name=='ui213':return [sys.executable,'-u',str(R/'docs/contact/friendly/A/cpu2d_ui.py')]
 if name=='webgl8':return [sys.executable,'-u',str(R/'docs/envelope/D/run_observed_webgl.py'),str(HTML),str(E/name)]
 raise ValueError(name)

def extract(name,code):
 if name in NATIVE:relative=Path(name)/NATIVE[name][1];expected=NATIVE[name][2]
 elif name=='emcon-ui':relative=Path(name)/'ui.json';expected=14
 elif name=='webgl8':relative=Path(name)/'observed-world.json';expected=29
 elif name=='paired-friendly':relative=Path(name)/'baseline-comparison.json';expected=42
 else:relative=Path('map/E/evidence/d-ui/ui.json');expected=213
 path=E/relative;checks={};errors=[]
 if path.exists():
  data=json.loads(path.read_text());errors=data.get('errors',[])
  if name=='paired-friendly':checks={r['ship']+':'+r['scenario']+':'+k:v for r in data['cases']for k,v in r['checks'].items()}
  else:checks=data.get('checks',{})
 log=(E/(name+'.log')).read_text(errors='replace');failed=[k for k,v in checks.items()if not v]
 if code==0 and len(checks)==expected and not failed and not errors:status='PASS';reason=None
 elif name=='emcon-ui'and code!=0 and '#lockBtn'in log and ('Locator.bounding_box'in log or 'locator("#lockBtn")'in log):status='INCOMPLETE';reason='Existing retired EMCON UI requires absent #lockBtn; original 14 assertions not approved or waived'
 elif code==124:status='INCOMPLETE';reason='Bounded worker timeout'
 elif 'Target crashed'in log or 'Target closed'in log:status='INCOMPLETE';reason='Chromium process crash; not counted PASS'
 else:status='FAIL';reason='Original assertion/worker failure or incomplete output'
 return {'status':status,'reason':reason,'expectedAssertions':expected,'executedAssertions':len(checks),
  'passedAssertions':sum(bool(v)for v in checks.values())if status!='INCOMPLETE'else 0,
  'failedAssertions':failed,'errors':errors,'resultPath':str(relative)if path.exists()else None}

def run(name):
 assert sha(HTML.read_bytes())==EXPECTED,'Candidate changed after freeze'
 assert sha(BASE.read_bytes())==BASE_SHA,'Original friendly baseline changed'
 cmd=job(name);start=time.perf_counter();timeout=150 if name=='emcon-ui'else 1000
 with(E/(name+'.log')).open('w')as f:
  try:q=subprocess.run(cmd,cwd=R,env=environment(),stdout=f,stderr=subprocess.STDOUT,timeout=timeout);code=q.returncode
  except subprocess.TimeoutExpired:code=124
 row={'suite':name,'command':cmd,'exitCode':code,'wallS':time.perf_counter()-start,**extract(name,code)}
 (E/(name+'-execution.json')).write_text(json.dumps(row,indent=2)+'\n')
 print(json.dumps({k:v for k,v in row.items()if k not in ['command','errors']}),flush=True);return row

def report(rows,start):
 native=[r for r in rows if r['suite']in NATIVE];pair=next((r for r in rows if r['suite']=='paired-friendly'),None);legacy=next((r for r in rows if r['suite']=='emcon-ui'),None)
 result={'schema':'AEGIS_TRACK_A_EXISTING_REGRESSIONS_1','candidate':HTML.name,'candidateSha256':EXPECTED,
  'baseline':BASE.name,'baselineSha256':BASE_SHA,'pairedReference':'FRIENDLY_CONTACT_A_NOT_CG_TURRET_A',
  'defaultDiagnostic':'OFF','assertionChanges':False,'expectedValuesUpdated':False,
  'adapters':'Unchanged existing B2 test_support retired-node/output paths; existing CPU Canvas2D+real WebGL backend',
  'gunConfiguration':'Existing non-gun regression policy: GUN_B2 flags ON, AutoAA OFF through historical test-only configuration; same as friendly baseline',
  'rows':rows,'wallS':time.perf_counter()-start,'native13':{'suiteCount':len(native),'expectedSuiteCount':13,'assertionCount':sum(r['executedAssertions']for r in native),'passedAssertions':sum(r['passedAssertions']for r in native),'expectedAssertions':364},
  'currentVsFriendlyDomain':{'totalExpected':420,'passed':sum(r['passedAssertions']for r in native)+(pair['passedAssertions']if pair else 0),'legacyUiIncomplete':14 if legacy and legacy['status']=='INCOMPLETE'else None,'pairedExpected':42,'pairedPassed':pair['passedAssertions']if pair else None},
  'inheritedCgVsFriendlyDomain':{'passed':404,'observerKnownDeltaUnapproved':2,'legacyUiIncomplete':14,'total':420,'reference':'docs/contact/friendly/A/VALIDATION.json'},
  'releaseApproved':False,'inheritedUnresolved':['CIWS_SEED_419025_FAIL','CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2','LEGACY_EMCON_UI_14_INCOMPLETE'],
  'newFailures':[r['suite']for r in rows if r['status']=='FAIL'],'incomplete':[r['suite']for r in rows if r['status']=='INCOMPLETE']}
 (P/'REGRESSION_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='+');ap.add_argument('--resume',action='store_true');ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 E.mkdir(parents=True,exist_ok=True);assert sha(HTML.read_bytes())==EXPECTED;assert sha(BASE.read_bytes())==BASE_SHA
 names=a.only or [*NATIVE,'paired-friendly','ui213','webgl8']
 if a.dry_run:print(json.dumps({'jobs':[{name:job(name)}for name in names],'candidateSha256':EXPECTED,'browserConcurrency':1,'optionalTailConcurrencyFlag':str(E/'allow-two-browser-jobs.flag')},indent=2));return
 paths=[R/'docs/pip/B/run_domain.py',R/'docs/map/A/verify_regressions.py',R/'docs/viewport/A/verify_regressions.py',R/'docs/gun/B2/phase1b/test_support/sitecustomize.py',R/'docs/map/E/legacy_test_adapter.py',R/'docs/pip/B/browser_backend.py',R/'docs/contact/friendly/A/cpu2d_ui.py',R/'docs/envelope/D/run_observed_webgl.py',R/'docs/missile/termination/A/verify_observed_world.py',R/'docs/helicopter/F/verify_regression.py',*[R/x[0]for x in NATIVE.values()]]
 (E/'source-provenance.json').write_text(json.dumps({'originalSourceFilesUnchanged':[{'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}for p in paths],'environment':{k:v for k,v in environment().items()if k.startswith('B2_')or k in ['TMPDIR','PYTHONDONTWRITEBYTECODE','PYTHONPATH','NODE_PATH']},'candidateSha256':EXPECTED,'baselineSha256':BASE_SHA},indent=2)+'\n')
 start=time.perf_counter();rows=[];prior_wall=0
 # A retired UI debt is not a passing test or fresh candidate result. Keep the
 # single bounded original attempt explicitly attached rather than rerunning it.
 if not a.only or 'emcon-ui' not in a.only:
  rows.append({'suite':'emcon-ui','status':'INCOMPLETE','expectedAssertions':14,
   'executedAssertions':0,'passedAssertions':0,'failedAssertions':[],'errors':[],
   'reason':'Existing retired EMCON UI requires absent #lockBtn; original 14 assertions not approved or waived. Prior bounded RC1 attempt retained; no RC2 assertions executed.',
   'evidenceScope':'LEGACY_DEBT_NOT_RC2_PASS','priorAttemptPath':'RC1/emcon-ui-execution.json',
   'priorCandidateSha256':'2fbe5392ac5f69fb2c2b4a42efd76eb7a3fc1ec0b4d8253748c1fb0be4caded5'})
 if a.resume and(P/'REGRESSION_RESULTS.json').exists():
  old=json.loads((P/'REGRESSION_RESULTS.json').read_text());assert old['candidateSha256']==EXPECTED;rows=old['rows'];prior_wall=old.get('wallS',0);names=[n for n in names if not any(r['suite']==n for r in rows)]
 start-=prior_wall
 report(rows,start)
 mains=[n for n in names if n not in ['ui213','webgl8']];tails=[n for n in names if n in ['ui213','webgl8']];running={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  def submit(name):running[pool.submit(run,name)]=name
  while mains or tails or running:
   done=[f for f in running if f.done()]
   for future in done:
    rows.append(future.result());del running[future];report(rows,start)
   active=set(running.values());native_running=any(n not in ['ui213','webgl8']for n in active);tail_running=any(n in ['ui213','webgl8']for n in active)
   parallel=(E/'allow-two-browser-jobs.flag').exists()
   if not running:
    if mains:submit(mains.pop(0));native_running=True
    elif tails:submit(tails.pop(0));tail_running=True
   if parallel and len(running)<2:
    if not tail_running and tails:submit(tails.pop(0))
    elif not native_running and mains:submit(mains.pop(0))
    elif not mains and tails:submit(tails.pop(0))
   if running:concurrent.futures.wait(running,timeout=2,return_when=concurrent.futures.FIRST_COMPLETED)
 final=report(rows,start);raise SystemExit(1 if final['newFailures']else 0)

if __name__=='__main__':main()
