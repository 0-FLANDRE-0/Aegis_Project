"""Fresh TRACK-A baseline: original commands/assertions, output-only redirection.

Does not modify the friendly-contact HTML, old evidence, fixture, or expectation.
The workers run the existing scripts verbatim via runpy. Only writes beneath
friendly/A/evidence are redirected into this task's baseline directory.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3]
FRIENDLY=R/'docs/contact/friendly/A';E=P/'evidence/baseline'
HTML=R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'
EXPECTED='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'
sha=lambda data:hashlib.sha256(data).hexdigest()

def redirect():
 old=(FRIENDLY/'evidence').absolute();new=(E/'friendly').absolute()
 native_open=Path.open;native_mkdir=Path.mkdir
 def mapped(path):
  path=Path(path)
  try:return new/path.absolute().relative_to(old)
  except ValueError:return path
 def opening(path,mode='r',*args,**kwargs):
  dst=mapped(path)
  if dst!=path:
   if any(x in mode for x in 'wax+'):
    native_mkdir(dst.parent,parents=True,exist_ok=True)
   elif not dst.exists():dst=path
  return native_open(dst,mode,*args,**kwargs)
 def mkdir(path,*args,**kwargs):return native_mkdir(mapped(path),*args,**kwargs)
 Path.open=opening;Path.mkdir=mkdir

def worker(task):
 assert sha(HTML.read_bytes())==EXPECTED
 E.mkdir(parents=True,exist_ok=True);redirect();sys.path.insert(0,str(FRIENDLY))
 sources={'d1':('ciws.py',['d1']),'repro':('repro.py',['--current']),
          'contracts':('contracts.py',[]),'auto-iff':('auto_iff.py',[]),
          'idle':('idle_and_dom.py',[])}
 if task in sources:
  name,args=sources[task];file=FRIENDLY/name;sys.argv=[str(file),*args]
  runpy.run_path(str(file),run_name='__main__');return
 if task in ['trace419025','trace419025-cg']:
  # Additional read-only trace, same native D1 fixture and fixed seed/conditions.
  import harness
  from playwright.sync_api import sync_playwright
  rng_trace=r'''
// AFTER_ACTION_TRUTH_TEST_ONLY. Passive observer, never a command input.
function baselineRngSnapshotA(){return {tag:'AFTER_ACTION_TRUTH_TEST_ONLY',global:SIM_RNG_STATE,mounts:ciws.map(m=>({id:m.id,sensor:cdCopy(CIWS_C55.banks.get(m.id)?.rng??null),aim:m._gunAimRngState??null,shot:m._gunShotRngState??null}))};}
function baselineTargetPhysicalA(em){return {tag:'AFTER_ACTION_TRUTH_TEST_ONLY',id:em?.id,structDmg:em?._structDmg??0,systems:cdCopy(em?._systemDamage??null),behavior:cdCopy(em?._wip113Behavior??null),position:em?{x:em.x,y:em.y,z:em.z,vx:em.vx,vy:em.vy,vz:em.vz}:null,flight:em?.flight?Object.fromEntries(['speedMps','flightPath','flightPathYaw','cmdFlightPath','cmdFlightPathYaw','_wip113GuidanceMode','_wip113EngineStopped','_wip113AvailableG'].filter(k=>k in em.flight).map(k=>[k,em.flight[k]])):null};}
const baselineEmitA=cdEmit;
cdEmit=function(){const n=CD_A.events.length,r=baselineEmitA.apply(this,arguments);if(CD_A.active&&CD_A.events.length>n)CD_A.events[CD_A.events.length-1].afterActionRng=baselineRngSnapshotA();return r;};
cdInstall();
const baselinePhalanxA=applyPhalanxProjectileHit;
applyPhalanxProjectileHit=function(){if(CD_A.active)cdEmit('RNG_PHALANX_BEFORE',{targetId:arguments[0]?.id,rng:baselineRngSnapshotA(),targetPhysical:baselineTargetPhysicalA(arguments[0])});const r=baselinePhalanxA.apply(this,arguments);if(CD_A.active)cdEmit('RNG_PHALANX_AFTER',{targetId:arguments[0]?.id,result:r,rng:baselineRngSnapshotA(),targetPhysical:baselineTargetPhysicalA(arguments[0])});return r;};
function baselineObserveRamA(native,kind){return function(rm,dt){const enabled=CD_A.active&&simStepCounter*SIM_FIXED_DT>=30,before=enabled?baselineRngSnapshotA():null,result=native.apply(this,arguments);if(enabled)cdEmit('RAM_MEASUREMENT_RNG',{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',sensor:kind,ramId:rm.id,lifeS:rm.life,measurement:result?Object.fromEntries(['azRad','elRad','snr','signal','quality','compositeCount'].filter(k=>k in result).map(k=>[k,result[k]])):null,before,after:baselineRngSnapshotA(),authority:rm._ramSeekerAuthority});return result;};}
ramRfMeasurement=baselineObserveRamA(ramRfMeasurement,'RF');ramIrMeasurement=baselineObserveRamA(ramIrMeasurement,'IR');
const baselinePhysicalTickA=updateEnemyMissileBaseC52;
updateEnemyMissileBaseC52=function(em,dt){const t=simStepCounter*SIM_FIXED_DT,record=CD_A.active&&t>=34.45&&t<=34.75,before=record?{rng:baselineRngSnapshotA(),targetPhysical:baselineTargetPhysicalA(em)}:null,r=baselinePhysicalTickA.apply(this,arguments);if(record)cdEmit('ASM_PHYSICAL_RNG_TRANSITION',{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',before,after:{rng:baselineRngSnapshotA(),targetPhysical:baselineTargetPhysicalA(em)}});return r;};
const baselineRandomA=simRandom;
simRandom=function(){const before=SIM_RNG_STATE,r=baselineRandomA.apply(this,arguments),t=simStepCounter*SIM_FIXED_DT;if(CD_A.active&&t>=34.45&&t<=34.65)cdEmit('RNG_CALL_SITE',{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',before,after:SIM_RNG_STATE,value:r,stack:String(new Error().stack)});return r;};
'''
  (E/(task+'-hooks.js')).write_text(rng_trace)
  extra=(R/'docs/ciws/dmg/A/diagnostic.js').read_text()+'\n'+(R/'docs/ciws/dmg/A/protection-trace.js').read_text()+'\n'+rng_trace
  raw=harness.build(task!='trace419025-cg',extra=extra);server,url=harness.serve(raw);errors=[];start=time.perf_counter()
  try:
   with sync_playwright()as pw:
    b=harness.launch(pw);p=harness.load_fast_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(600000)
    result=p.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419025})
    signature=result.pop('equivalenceSignature');result.update(signatureSha256=sha(signature.encode()),errors=errors,wallS=time.perf_counter()-start,sourceProduct='CG_TURRET_A'if task.endswith('-cg')else'FRIENDLY_CONTACT_A')
    (E/(task+'.json')).write_text(json.dumps(result,separators=(',',':'))+'\n');b.close()
  finally:server.shutdown()
  print(json.dumps({task:result['result'],'signatureSha256':result['signatureSha256'],'errors':errors}),flush=True);return
 if task in ['paired-current','harpoon-clock']:
  env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':HTML.name,'B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'}
  if task=='paired-current':cmd=[sys.executable,'-u',str(R/'docs/helicopter/F/verify_regression.py'),str(R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html'),str(HTML),str(E/task),'--baseline-only']
  else:cmd=[sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(HTML),str(E/task),'--only','harpoon-clock']
  raise SystemExit(subprocess.run(cmd,cwd=R,env=env).returncode)
 raise ValueError(task)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--worker');ap.add_argument('--only',nargs='+');a=ap.parse_args()
 if a.worker:return worker(a.worker)
 assert sha(HTML.read_bytes())==EXPECTED
 E.mkdir(parents=True,exist_ok=True);jobs=a.only or ['d1','repro','trace419025','contracts','auto-iff','idle','paired-current','harpoon-clock']
 start=time.perf_counter();rows=[]
 for task in jobs:
  at=time.perf_counter();cmd=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker',task]
  with(E/(task+'.log')).open('w')as log:
   try:q=subprocess.run(cmd,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=1200);code=q.returncode
   except subprocess.TimeoutExpired:code=124
  product=R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html'if task.endswith('-cg')else HTML
  row={'task':task,'command':cmd,'exitCode':code,'wallS':time.perf_counter()-at,'product':product.name,'productSha256':sha(product.read_bytes()),'historicalComparator':task.endswith('-cg')};rows.append(row)
  out={'schema':'AEGIS_TRACK_A_FRESH_BASELINE_1','html':HTML.name,'htmlSha256':EXPECTED,'baselineHead':'4ba64ba0cace9124497a710d00df1b174984ffdc','outputAdapterOnly':True,'fixtureOrAssertionChanges':False,'rows':rows,'wallS':time.perf_counter()-start,'releaseApproved':False}
  destination=E/'additional-execution.json'if a.only else P/'baseline-execution.json'
  destination.write_text(json.dumps(out,indent=2)+'\n');print(row,flush=True)
 raise SystemExit(any(r['exitCode']for r in rows))

if __name__=='__main__':main()
