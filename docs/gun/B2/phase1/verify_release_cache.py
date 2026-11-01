"""Input-revision contract using actual product helper + bound native AIR solver."""
import json
from playwright.sync_api import sync_playwright
from harness import P,build,serve,load_http,launch
E=P/'evidence/release-cache';E.mkdir(parents=True,exist_ok=True)
js=r'''
window.__B2_CACHE_UNIT__=()=>{
 __GB_TEST__.reset(592001);const scene=_wip75CreateTarget({rangeKm:5,bearingDeg:0,altM:10,speedMps:280}),tr=scene.tr,id=scene.trackId;
 Object.assign(tr,{classification:'ASM',domain:'AIR',isASM:true,identity:'HOSTILE',_operatorIdentity:'HOSTILE',confirmed:true,sensorAge:0,_lastMeasurementStep:simStepCounter});tr._kfX=new Float64Array([worldToMeters(tr.x),worldToMeters(tr.y),tr.z,worldSpeedToMps(tr.vx),worldSpeedToMps(tr.vy),tr.vz]);tr._kfP=new Float64Array(36);
 const g=gunB1OwnGuns()[0][1];g.selectAmmo('MFF_127_SIM');const q=g.command(id,'MFF_127_SIM');if(!q.ok)throw Error(q.reason);for(let i=0;i<600;i++)g.step(SIM_FIXED_DT);
 const ss=g.snapshot(),hp={...ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId]},state={solution:ss.solution,bodyAzRad:ss.bodyAzRad,elevationRad:ss.elevationRad,revision:0},originalEnv=maritimeEnvironmentSnapshotWip13A3;let calls=0,envOffset=0;const solve=(...args)=>{calls++;return g.solveAirTrack(...args);},counts=[],record=(name)=>{const f=gunB2PrepareRelease(state,id,'MFF_127_SIM',solve,g.spec,hp);if(f)throw Error(name+':'+f.reason);counts.push({name,calls});};
 const rng=simRngState;try{
 record('initial');record('identical');tr._kfX[0]+=.01;record('observation');tr._kfP[0]+=.01;record('covariance');hp.x+=.01;record('trunnion');
 maritimeEnvironmentSnapshotWip13A3=function(){const v=originalEnv();return {...v,wind:{...v.wind,speedMps:v.wind.speedMps+envOffset}};};envOffset=.01;record('weather');simStepCounter++;record('tick');
 }finally{maritimeEnvironmentSnapshotWip13A3=originalEnv;}
 return {counts,expected:[1,1,2,3,4,5,6],globalRngUnchanged:rng===simRngState,finalSolutionCurrentTick:state.solution.computedStep===simStepCounter};
};
'''
# Read exact RNG identifier from native core rather than creating a test stream.
from pathlib import Path
source=Path('/tmp/aegis-gun-b2/phase1-current.js').read_text()
# The public deterministic snapshot is already the native fixture's RNG getter.
js=js.replace('simRngState','SIM_RNG_STATE')
raw=build(record=False,extra=js);server,url=serve(raw);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(600000);q=p.evaluate('__B2_CACHE_UNIT__()');b.close()
server.shutdown();checks={'inputRevisionInvalidates':[x['calls']for x in q['counts']]==q['expected'],'globalRngUnchanged':q['globalRngUnchanged'],'currentTick':q['finalSolutionCurrentTick'],'pageErrors0':not errors};out={'pass':all(checks.values()),'checks':checks,'unit':q,'errors':errors};(E/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit(not out['pass'])
