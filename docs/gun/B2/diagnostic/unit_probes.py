"""Native launch arithmetic, per-tick proximity semantics and surface staleness.
These are isolated diagnostic pages, not changes to the product or G7 fixtures.
"""
from pathlib import Path
import json,sys,time
from playwright.sync_api import sync_playwright
from build_fixture import build,R,B
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
helper=r'''
window.__G2_UNIT__=()=>{
 const launchRows=[];__GB_TEST__.reset(419010);const id=__GB_TEST__.air({rangeKm:5,altM:30,speedMps:0});
 for(const[key,g]of gunB1OwnGuns())for(const ammoId of ['HE_127_SIM','SAP_127_SIM','MFF_127_SIM']){const s=g.solveAirTrack(id,ammoId);if(!s.ok){launchRows.push({key,ammoId,reason:s.reason});continue;}const q={module:g.spec,ammo:g.spec.ammunition[ammoId],ammoId,trackId:id,bodyAzRad:s.bodyAzRad,elevationRad:s.bodyElevationRad,hardpoint:ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],solution:s},before=SIM_RNG_STATE,states=[];for(let i=0;i<32;i++){const p=spawnMainGunProjectileWip13B3(q);states.push({positionM:{...p.positionM},velocityMps:{...p.velocityMps}});}launchRows.push({key,ammoId,states,rngBefore:before,rngAfter:SIM_RNG_STATE,allExact:states.every(x=>JSON.stringify(x)===JSON.stringify(states[0]))});resetMainGunProjectilesWip13B3();}
 __GB_TEST__.reset(419010);const p={id:'MK45-99',ammoId:'MFF_127_SIM',massKg:31.75,trackId:-1,alive:true,solutionTimeOfFlightS:100,ageS:1,flightDistanceM:1000,positionM:{x:0,y:0,z:100},velocityMps:{x:600,y:0,z:0}};gunB1ArmShell(p);targetPool.push({id:419,x:metersToWorld(105),y:0,z:100,vx:0,vy:0,vz:0,alive:true});const endpointEvent=gunB1ShellEvent(p,{x:0,y:0,z:100},{x:100,y:0,z:100},1/6);
 const surface=[];
 for(const rangeKm of [5,10,15])for(const movement of ['ALONG','CROSS']){__MD_TEST__.reset();const id=__MD_TEST__.surface({rangeKm,bearingDeg:0});const tr=tracks.get(id),v=movement==='ALONG'?{x:10,y:0}:{x:0,y:10};tr.vx=mpsToWorldSpeed(v.x);tr.vy=mpsToWorldSpeed(v.y);tr._kfX[3]=v.x;tr._kfX[4]=v.y;
  for(const[key,g]of gunB1OwnGuns()){const old=g.solveTrack(id,'HE_127_SIM');if(!old.ok){surface.push({rangeKm,movement,key,reason:old.reason});continue;}tr.x+=metersToWorld(v.x);tr.y+=metersToWorld(v.y);tr._kfX[0]+=v.x;tr._kfX[1]+=v.y;const fresh=g.solveTrack(id,'HE_127_SIM',{seedSolution:old}),hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],off=g.spec.mount.trunnionOffsetM,az=g.snapshot().bodyAzRad,origin=shipGamePointStateV1({x:hp.x+off.x*Math.cos(az)-off.y*Math.sin(az),y:hp.y+off.x*Math.sin(az)+off.y*Math.cos(az),z:hp.z+off.z});
   const results={};if(fresh.ok)for(const[name,s]of [['age1s',old],['fresh',fresh]]){const q=wip13b1IntegrateToDownrange(g.spec,g.spec.ammunition.HE_127_SIM,{originM:{x:origin.xM,y:origin.yM,z:origin.zM},platformVelocityMps:{x:origin.vxMps,y:origin.vyMps,z:origin.vzMps},environment:maritimeEnvironmentSnapshotWip13A3(),azimuthRad:s.azimuthRad,elevationRad:s.elevationRad,referenceAzimuthRad:Math.atan2(fresh.predictedAimPointM.y-origin.yM,fresh.predictedAimPointM.x-origin.xM)},Math.hypot(fresh.predictedAimPointM.x-origin.xM,fresh.predictedAimPointM.y-origin.yM));results[name]=q.ok?{timeS:q.timeS,missVectorM:{x:worldToMeters(tr.x)+v.x*q.timeS-q.positionM.x,y:worldToMeters(tr.y)+v.y*q.timeS-q.positionM.y,z:g.spec.fireControl.defaultAimHeightM-q.positionM.z}}:q;}
   surface.push({rangeKm,movement,key,freshOk:fresh.ok,reason:fresh.reason??null,observedSpeedMps:10,observationAdvanceS:1,results});tr.x-=metersToWorld(v.x);tr.y-=metersToWorld(v.y);tr._kfX[0]-=v.x;tr._kfX[1]-=v.y;}
 }
 return {launchRows,endpointEvent,surface};
};
'''
out=B/'evidence/unit-probes';out.mkdir(parents=True,exist_ok=True);errors=[];rows=[];raw=build(False,helper);start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,raw,own=ship,errors=errors);p.set_default_timeout(600000);q=p.evaluate('__G2_UNIT__()');rows.append({'ship':ship,'result':q});p.close()
 b.close()
checks={'launchDispersionZero':all(q['allExact']for r in rows for q in r['result']['launchRows']if'allExact'in q),'launchGlobalRngUnchanged':all(q['rngBefore']==q['rngAfter']for r in rows for q in r['result']['launchRows']if'allExact'in q),'proxAtTickEndpointBeforeGlobalCpa':all(r['result']['endpointEvent']['t']==1 and r['result']['endpointEvent']['missM']==5 for r in rows),'errors0':not errors}
result={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start};(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':checks,'elapsedS':result['elapsedS']}));raise SystemExit(not result['pass'])
