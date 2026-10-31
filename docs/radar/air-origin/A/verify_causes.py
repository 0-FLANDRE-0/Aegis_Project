"""Read-only per-tick causality traces. No reference updates or product edits.

Wrap the real fixed-tick function in a disposable page, then retain primitives
from the mass ledger's pure peek and the dynamics' pure snapshot. Do not call
snapshot on the mass ledger (it can rebuild or change diagnostic counters).
"""
from pathlib import Path
import argparse, hashlib, json, re, sys, time
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent; R=B.parents[3]
sys.path[:0]=[str(R/'docs/missile/fuze-zem/A'),str(R/'docs/bunkerhill/K'),str(R/'docs/missile/termination/A')]
from browser_tools import instrument as append_helper
from browser_i import launch, load
from browser_tools import load_fleet
from verify_live import instrument as live_instrument

HELPER=r'''
window.__AIR_CAUSES__={rows:[],launches:[]};
{const real=simulateFixedTick,seen=new WeakSet();
 simulateFixedTick=function(...args){const value=real(...args),log=window.__AIR_CAUSES__;
  if(!log.enabled)return value;
  const mass=shipMassLedgerV32?.peek(),dyn=shipDynamicsV15?.snapshot();
  for(const m of missiles)if(!seen.has(m)){seen.add(m);log.launches.push({tick:simStepCounter,id:m.id,type:m.weaponType,life:m.life,trackId:m.targetId??m.trackId??null,x:m.x,y:m.y,z:m.z});}
  log.rows.push({tick:simStepCounter,rng:SIM_RNG_STATE,massKg:mass?.massKg,cgM:mass?.cgM,massRevision:mass?.revision,massDirty:mass?.performance?.dirty,massReason:mass?.performance?.lastDirtyReason,heel:dyn?.rollRateRadS,trim:dyn?.trimRateRadS,draft:dyn?.draftM,
   tracks:[...tracks].map(([id,t])=>[id,t.z,t.sensorSource]),
   target:targetPool[0]?{id:targetPool[0].id,x:targetPool[0].x,y:targetPool[0].y,z:targetPool[0].z,heading:targetPool[0].heading,threatened:targetPool[0].threatened,patrolTurnTimer:targetPool[0].patrolTurnTimer,turnIntent:targetPool[0].turnIntent}:null,
   missiles:missiles.map(m=>({id:m.id,state:m.state,seeker:m.essmActiveSeeker,reason:m._deathReason,dead:m.dead,life:m.life}))});
  return value;
 };
}
'''
p=argparse.ArgumentParser();p.add_argument('mode',choices=['raid','world']);a=p.parse_args()
errors=[];rows=[];started=time.perf_counter()
state_source=(R/'docs/envelope/D/verify_world120.py').read_text();STATE=re.search("STATE='''([\\s\\S]*?)'''",state_source)[1]
with sync_playwright() as pw:
 browser=launch(pw)
 for ship in (['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']if a.mode=='raid'else['DDG_119_LATE_FLIGHT_IIA']):
  for tag,file in [('MAIN','Aegis_SIM_v48_WIP_GUN_B1.html'),('AIR_ORIGIN_A','Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html')]:
   raw=(R/file).read_bytes()
   if a.mode=='world':raw=live_instrument(raw)
   raw=append_helper(raw,HELPER)
   page=load(browser,raw,ship=ship,errors=errors)if a.mode=='raid'else load_fleet(browser,raw,own=ship,errors=errors)
   page.set_default_timeout(600000)
   if a.mode=='raid':
    q=page.evaluate('''()=>{const d=__NAVAL_SIM_DIAG__;__AIR_CAUSES__.enabled=true;d.setTerrainDiagBypass(true);d.wip119DiagSpawnRealAsms({count:8,label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]});d.wip119SetMode('AUTO');d.runFramesToTicks(60,8,1920);return {trace:__AIR_CAUSES__,state:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),rng:__HARPOON_DIAG_A__.snapshot().rng};}''')
   else:
    c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True}
    page.evaluate('c=>{__AIR_CAUSES__.enabled=true;__TERM_LIVE_TEST__.prepareObserved(c);}',c);page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');ticks=900;release=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
    while not release.get('launched')and ticks<3600:
     page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');ticks+=300;release=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
    assert release.get('launched');page.evaluate('n=>__NAVAL_SIM_DIAG__.stepTicks(n)',7200-ticks)
    state=page.evaluate(STATE);q={'trace':page.evaluate('__AIR_CAUSES__'),'state':json.loads(state),'stateSha256':hashlib.sha256(state.encode()).hexdigest(),'release':release}
   rows.append({'mode':a.mode,'ship':ship,'tag':tag,'result':q});page.close();print(a.mode,ship,tag,len(q['trace']['rows']),flush=True)
 browser.close()
out={'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-started,'policy':'Read-only diagnostic wrappers; compare final physical snapshot to the original uninstrumented regression before trusting trace.'}
(B/'evidence'/f'causes-{a.mode}.json').write_text(json.dumps(out,indent=2)+'\n')
assert not errors
