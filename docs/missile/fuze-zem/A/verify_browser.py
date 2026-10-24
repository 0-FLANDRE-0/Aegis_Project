from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
from browser_tools import H,launch,load_fleet,instrument
helper=r"""
window.__FZ_SURFACE_PROBE_A__=()=>{
 surfaceContacts.length=0;SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A.clear();
 const t=spawnSurfaceTargetWip13A({entityId:'FZ_SIGNAL_PROX',x:kmToWorld(20),y:0,heading:0,speedKt:0,mobilityMode:'DEAD_IN_WATER'}),p=surfaceTargetProfileWip13A(t.profileId),beam=p.geometry.beamM,L=p.geometry.lengthM;
 const m={id:981,x:0,y:0,z:5,life:18,dead:false,vlsPhase:false,guidanceCore:'v1',weaponType:'SM2ER',isESSM:false,isSM6:false,_v1Profile:SAM_MISSILE_PROFILES.SM2ER_BLKIV_SIM,speed:mpsToWorldSpeed(700),massKg:620,_surfaceSarh:{schema:'AEGIS_SM2_SURFACE_SARH_RUNTIME_V48_WIP13C5',trackId:null,aimHeightM:5,truthUsed:false}};
 const a=surfaceTargetLocalToWorldSimWip13A(t,{x:-L,y:beam/2+3,z:5}),b=surfaceTargetLocalToWorldSimWip13A(t,{x:L,y:beam/2+3,z:5}),lenM=worldToMeters(Math.hypot(b.x-a.x,b.y-a.y)),n=Math.ceil(lenM/(700*SIM_FIXED_DT));m.heading=Math.atan2(b.y-a.y,b.x-a.x);m.pitch=0;m.vx=mpsToWorldSpeed(Math.cos(m.heading)*700);m.vy=mpsToWorldSpeed(Math.sin(m.heading)*700);m.vz=0;Object.assign(m,a);
 const draw=_wip99FuzeDetectionDraw;let forbidden=0;
 if(typeof samFuzeSignalSweepA==='function')_wip99FuzeDetectionDraw=function(){forbidden++;throw Error('SAM_SURFACE_DETECTION_DRAW');};
 let result=null;try{for(let i=0;i<n&&!m.dead;i++){const prev={x:m.x,y:m.y,z:m.z};if(typeof samFuzeSignalBeginA==='function')samFuzeSignalBeginA(m,SIM_FIXED_DT);m.life+=SIM_FIXED_DT;m.x+=m.vx*SIM_FIXED_DT;m.y+=m.vy*SIM_FIXED_DT;result=surfaceMissileSweptContactWip13C5(m,prev);simStepCounter++;}}
 finally{_wip99FuzeDetectionDraw=draw;}
 return {reason:m._deathReason??null,dead:m.dead,prox:m.proxDetonated??false,forbiddenDrawCalls:forbidden,signal:m._fuzeSignalLastA??null,sense:m._surfaceFuzeSenseWip13C22??null,result,profile:p.geometry};
};
"""
checks={};rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for v in ['BASE','DZT']:
  raw=Path('/tmp/aegis-fuze-zem/builds/Aegis_SIM_v48_WIP_FUZE_ZEM_A_'+v+'.html').read_bytes();p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);checks[v+'.cleanCore']=not p.evaluate('__CORE_SELFTEST_FAILURES__');s=p.evaluate('__ENV_D__.status()');checks[v+'.rangeTableMarkedHistorical']=(s['match']if v=='BASE'else not s['match']and s['recalculationRequired']);rows.append({'variant':v,'status':s});p.screenshot(path=str(H/'evidence'/('clean-'+v+'.png')));p.close()
  p=load_fleet(b,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);q=p.evaluate('__FZ_SURFACE_PROBE_A__()');rows.append({'variant':v,'surface':q});checks[v+'.surfaceProximity']=q['dead']and q['reason']=='SURFACE_TARGET_PROXIMITY';checks[v+'.surfaceNoForbiddenDraw']=q['forbiddenDrawCalls']==0
  if v=='DZT':checks['surfaceUsesAccumulatedSignal']=q['signal']and q['signal']['model']=='SAM_SIGNAL_A'and q['signal']['detected']
  print(v,q['reason'],q['signal'],flush=True);p.close()
 b.close()
checks['pageErrors0']=not errors;out={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors};(H/'evidence/browser.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v]}))
