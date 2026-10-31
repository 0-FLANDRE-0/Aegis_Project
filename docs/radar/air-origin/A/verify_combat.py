"""Unchanged EW/H3 fixtures and an additional unforced-RF CIWS whole-world case."""
from pathlib import Path
import argparse,ast,hashlib,json,sys,time
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--only-ciws',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[];start=time.perf_counter()
def fixture(path):
 t=ast.parse((R/path).read_text());return ast.literal_eval(next(n.value for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='FIXTURE'for x in n.targets)))
helper=r'''
window.__AIR_CIWS__=()=>{
 _wip75ResetCase(971910);_wip103ResetCiwsForCase();BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
 engagementControlMode='MANUAL';gunB1AutoState().enabled=false;emconActive=false;softKillAutoDoctrine=false;
 for(const b of [45,135]){const h=deg(b),x=aircraft.x()+kmToWorld(5)*Math.cos(h),y=aircraft.y()+kmToWorld(5)*Math.sin(h);
 spawnEnemyMissile({id:1,x,y,z:15,vx:mpsToWorldSpeed(-300*Math.cos(h)),vy:mpsToWorldSpeed(-300*Math.sin(h)),heading:angNorm(h+Math.PI),asmType:'Kh-35U',lastKnownShipX:aircraft.x(),lastKnownShipY:aircraft.y()});}
 const diagnosticTargets=enemyMissiles.slice();
 const initialTracks=tracks.size,before=ciws.map(m=>({id:m.id,ammo:m.ammo})),samples=[],gunSerialBefore=mainGunProjectileSerialWip13B3;
 for(let i=0;i<2100&&enemyMissiles.some(m=>m.alive);i++){simulateFixedTick(SIM_FIXED_DT);if(i%60===0)samples.push({step:simStepCounter,tracks:[...tracks].map(([id,t])=>({id,source:t.sensorSource,z:t.z,identity:t.identity})),mounts:ciws.map(m=>({id:m.id,ammo:m.ammo,state:m.state,source:m._ciwsTrackSource,trackId:m.trackingTrackId}))});}
 return {initialTracks,before,after:ciws.map(m=>({id:m.id,ammo:m.ammo})),rounds:before.reduce((n,m,i)=>n+m.ammo-ciws[i].ammo,0),samLaunches:missiles.length,gunShots:mainGunProjectileSerialWip13B3-gunSerialBefore,actualShipHits:shipHitHistory.filter(h=>!h.miss).length,samples,hp:shipHP,targets:diagnosticTargets.map(m=>({id:m.id,alive:m.alive,reason:m._deathReason??null,retirement:m._wip11cRetirementQueued?.cause??null})),rng:SIM_RNG_STATE,core:window.__CORE_SELFTEST_FAILURES__};
};
'''
with sync_playwright()as pw:
 b=launch(pw)
 for name,path in [('ew','docs/multiship/F/verify.py'),('h3','docs/multiship/H3/verify_attack.py'),('ciws',None)]:
  if a.only_ciws and name!='ciws':continue
  script=fixture(path)if path else '__AIR_CIWS__()'
  if name=='h3':
   old="checks.currentStrictSchema=current.fleet.schema==='AEGIS_NAVAL_PHYSICAL_FLEET_H3_1'";assert script.count(old)==1;script=script.replace(old,"checks.currentStrictSchema=current.fleet.schema==='AEGIS_NAVAL_PHYSICAL_FLEET_H4_1'")
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   page=load_fleet(b,instrument(raw,helper)if name=='ciws'else raw,own=ship,ally=None if name=='ciws'else('CG_52_LATE_TICONDEROGA'if ship.startswith('DDG')else'DDG_119_LATE_FLIGHT_IIA'),enemy=None if name=='ciws'else'CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000);q=page.evaluate(script);page.close();rows.append({'suite':name,'ship':ship,'result':q});print(name,ship,'checks',len(q.get('checks',{})),'rounds',q.get('rounds'),flush=True)
 b.close()
(a.out/'results.json').write_text(json.dumps({'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start,'ciwsNatural':'No track insertion/sync or forced lock. Existing target AI/full fixed tick. SAM MANUAL and 5in Auto OFF.','inheritedTestMigration':'H3 fixture current schema H4, identical to existing verify_ew_h3 migration; no new expected values.'},indent=2)+'\n');raise SystemExit(bool(errors))
