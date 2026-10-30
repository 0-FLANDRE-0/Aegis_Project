"""Real manual surface release and full fixed-tick flight, separate contract."""
from pathlib import Path
import sys,json,gzip,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
files={'DZT':(R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html'),'HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])}
helper=r'''
window.__LH_SURFACE__={run(o={}){
 _wip75ResetCase(1350501);resetEngagementTransientV48Wip11A();resetOwnshipWorldWip14A(0,0);BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;engagementControlMode='MANUAL';emconActive=false;routePoints.length=0;navObjective.reached=true;
 surfaceContacts.length=0;SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A.clear();shipNav.heading=0;shipNav.previousHeadingWorld=0;shipNav.speed=25*.514444;shipNav.targetSpeedKt=25;shipNav.vx=mpsToWorldSpeed(shipNav.speed);shipNav.vy=0;shipNav.rudder=0;shipNav.targetRudder=0;shipNav.manualRudderV15=true;shipNav.manualSpeedV15=true;
 const target=spawnSurfaceTargetWip13A({entityId:'LH_SURFACE',x:aircraft.x(),y:aircraft.y()+kmToWorld(8),heading:Math.PI,speedKt:15,mobilityMode:'FREE_RUNNING'});
 for(let i=0;i<1200;i++)simulateFixedTick(SIM_FIXED_DT);
 const tr=[...tracks.values()].filter(t=>surfaceTrackWip13C5(t)&&t.confirmed).sort((a,b)=>(b.trackQuality??0)-(a.trackQuality??0))[0];if(!tr)return {error:'NO_NATIVE_SURFACE_TRACK'};
 setTrackOperatorIdentityA3(tr.trackId,'TRAINING_TARGET');selectedLockId=tr.trackId;const weapon=o.weapon??'SM2ER';vlsCells.fwd[0]=wip125MakeInstalledCell('fwd',0,weapon);shipMassMarkWeaponsV32('LH_TEST_LOADOUT');
 const assessment=surfaceMissileReleaseAssessmentWip13C4(tr,weapon,{mode:'MANUAL'});spawnMissile({automatic:false,weaponType:weapon});const m=missiles.at(-1);if(!m)return {error:'RELEASE_INHIBITED',assessment,lastError:lastErrorMsg};
 let forbiddenGateCalls=0;const gate=typeof samLaunchHandoffGateA==='function'?samLaunchHandoffGateA:null;if(gate)samLaunchHandoffGateA=function(...a){forbiddenGateCalls++;throw Error('AIR_GATE_CALLED_FOR_SURFACE');};
 const trace=[];try{for(let i=0;i<3600&&!m.dead;i++){simulateFixedTick(SIM_FIXED_DT);if(i%6===0||m.dead)trace.push({timeS:m.life,x:m.x,y:m.y,z:m.z,vx:m.vx,vy:m.vy,vz:m.vz,heading:m.heading,pitch:m.pitch,pitchover:m.pitchoverPhase,handoffAt:m._pitchoverCompleteAt??null,source:m._v1GuidanceAuthority??null,reason:m._deathReason??null});}}finally{if(gate)samLaunchHandoffGateA=gate;}
 return {weapon,assessment,trace,forbiddenGateCalls,reason:m._deathReason??'STILL_FLYING_60S',surfaceMode:!!surfaceMissileRuntimeWip13C6(m),damage:surfaceTargetSnapshotWip13A(target).damage,impact:m._surfaceImpact??null,rng:SIM_RNG_STATE,core:window.__CORE_SELFTEST_FAILURES__,fault:simRuntimeFault};
}};
''';rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  for weapon in ['SM2ER','SM6']:
   p=load_fleet(b,instrument(file.read_bytes(),helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000);q=p.evaluate('c=>__LH_SURFACE__.run(c)',{'weapon':weapon});rows.append({'variant':variant,'weapon':weapon,'result':q});p.close();print(variant,weapon,q.get('reason'),q.get('error'),q.get('forbiddenGateCalls'),flush=True)
 b.close()
checks={'pageErrors0':not errors}
for w in ['SM2ER','SM6']:
 a=next(x['result']for x in rows if x['variant']=='DZT'and x['weapon']==w);q=next(x['result']for x in rows if x['variant']=='HANDOFF'and x['weapon']==w);checks[w+'.nativeReleased']='error'not in a and'error'not in q;checks[w+'.surfaceContract']=bool(q.get('surfaceMode'));checks[w+'.airGateNeverCalled']=q.get('forbiddenGateCalls')==0;checks[w+'.trajectoryExact']=a.get('trace')==q.get('trace');checks[w+'.outcomeAndRngExact']=all(a.get(k)==q.get(k)for k in ['reason','damage','rng']);checks[w+'.core0']=not q.get('core')
o={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'elapsedS':time.perf_counter()-start};(H/'final-results/surface.json.gz').write_bytes(gzip.compress(json.dumps(o,separators=(',',':')).encode(),9,mtime=0));(H/'final-evidence/surface.json').write_text(json.dumps({'pass':o['pass'],'checks':checks,'outcomes':[{'variant':r['variant'],'weapon':r['weapon'],'reason':r['result'].get('reason'),'error':r['result'].get('error')}for r in rows]},indent=2)+'\n');print(json.dumps({'pass':o['pass'],'checks':checks}));raise SystemExit(0 if o['pass']else 1)
