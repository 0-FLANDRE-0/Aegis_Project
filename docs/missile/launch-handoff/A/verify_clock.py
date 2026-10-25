"""Actual frame accumulator + full fixed ticks at 1/8/16; 64 separately.
Rendering stays active but the autonomous simulation clock is paused between
controlled frame batches. Presentation switching cannot add physics ticks.
"""
from pathlib import Path
import sys,json,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=Path(json.loads((H/'build.json').read_text())['file']).read_bytes();helper=(R/'docs/missile/termination/A/live-fixture.js').read_text()+r'''
window.__LH_DAMAGE_FCS__=()=>SPG62_ILLUMINATORS.map(i=>{addModuleDmg(i.moduleName,100);return {name:i.moduleName,damage:getModuleDmg(i.moduleName)};});
window.__LH_CLOCK_STATE__=()=>{const m=TERM_LIVE_LAST_MISSILE_A;return {step:simStepCounter,control:{selectedLockId,radarMode:radar.mode,pdTracking:radar.pdTracking,emcon:emconActive},missile:m?{life:m.life,x:m.x,y:m.y,z:m.z,vx:m.vx,vy:m.vy,vz:m.vz,pitch:m.pitch,heading:m.heading,dead:m.dead,reason:m._deathReason??null,pitchover:m.pitchoverPhase,handoffAt:m._pitchoverCompleteAt??null,gate:m._launchHandoffA??null}:null,targets:targetPool.map(t=>({x:t.x,y:t.y,z:t.z,vx:t.vx,vy:t.vy,vz:t.vz,alive:t.alive})),rng:SIM_RNG_STATE};};
''';errors=[];rows=[];checks={};start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw,True)
 for damage in [False,True]:
  for scale in [1,8,16,64]:
   p=load_fleet(b,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
   c={'weapon':'SM2ER','rangeKm':30,'bearingDeg':45,'enabled':True};p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);p.evaluate('__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');release=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c);assert release.get('launched'),release
   damageState=p.evaluate('__LH_DAMAGE_FCS__()')if damage else [];p.evaluate('__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');batches=[];viewChanges=[]
   # 1280 is divisible by 64. Standard multipliers have no partial tick issue.
   for i in range(3):
    batchStart=time.perf_counter();batch=p.evaluate('s=>__NAVAL_SIM_DIAG__.runFramesToTicks(60,s,1280)',scale);batch['wallS']=time.perf_counter()-batchStart;batches.append(batch)
    if scale==1:
     before=p.evaluate('__LH_CLOCK_STATE__()')
     if i%2==0:
      p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50)
     else:p.evaluate('__WIP148_3D_VIEW__.close()')
     viewChanges.append({'before':before,'after':p.evaluate('__LH_CLOCK_STATE__()')})
   state=p.evaluate('__LH_CLOCK_STATE__()');row={'damage':damage,'timeScale':scale,'release':release,'damageState':damageState,'batches':batches,'state':state,'stateSha256':hashlib.sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'viewChanges':viewChanges,'core':p.evaluate('__CORE_SELFTEST_FAILURES__')};rows.append(row);p.close();print(damage,scale,row['stateSha256'],state['missile']['reason'],flush=True)
 b.close()
for damage in [False,True]:
 rr=[x for x in rows if x['damage']==damage];base=rr[0];checks[str(damage)+'.oneEightSixteenExact']=all(x['state']==base['state']for x in rr if x['timeScale']in[1,8,16]);checks[str(damage)+'.viewReadOnly']=all(v['before']==v['after']for x in rr for v in x['viewChanges']);checks[str(damage)+'.fixedTicks']=all(sum(b['steps']for b in x['batches'])==3840 for x in rr);checks[str(damage)+'.64PhysicalExact']=rr[-1]['state']==base['state']
checks['damageApplied']=all(all(m['damage']>=100 for m in x['damageState'])and x['damageState']for x in rows if x['damage']);checks['core0']=all(not x['core']for x in rows);checks['pageErrors0']=not errors;o={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'method':__doc__};(H/'final-evidence/clock-view-damage.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'pass':o['pass'],'checks':checks}));raise SystemExit(0 if o['pass']else 1)
