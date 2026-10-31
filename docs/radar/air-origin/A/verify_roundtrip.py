"""Actual RF extractor → AIR adapter → association/EKF, noiseless private inputs.
16 original DDG/CG × four SPY faces × two bearings; DDG SPQ AIR additionally.
Only diagnostic scene/RNG sources are replaced. Product gains/noise untouched.
"""
from pathlib import Path
import hashlib,json,sys,time
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
HELPER=r'''
window.__AIR_ROUNDTRIP__=()=>{
 const original={scene:shipboardRadarPhysicalSceneWip13B13,normal:observerNormalC,random:observerRandomC,bypass:BATTLESPACE_DIAG_BYPASS},rng=SIM_RNG_STATE,tick=simStepCounter,rows=[];
 const fields=['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps'];
 try{BATTLESPACE_DIAG_BYPASS=true;observerNormalC=()=>0;observerRandomC=()=>0;
 for(const face of ['F1','F2','F3','F4'])for(const bearing of [0,90]){
  const p=spySurfaceOriginWip13B9({face}),rx={x:p.x,y:p.y,z:p.z,vxMps:7,vyMps:-2,vzMps:.6};
  for(const channel of IS_BUNKER?['SPY']:['SPY','SPQ']){
   const receiver=channel==='SPY'?rx:{...wip199ShipLocalWorldPoint(WIP199_FINAL_LAYOUT.spq9b.x,WIP199_FINAL_LAYOUT.spq9b.y,WIP199_FINAL_LAYOUT.spq9b.z),vxMps:7,vyMps:-2,vzMps:.6};
   const target={x:aircraft.x()+metersToWorld(10000*Math.cos(deg(bearing))),y:aircraft.y()+metersToWorld(10000*Math.sin(deg(bearing))),z:1200,vx:mpsToWorldSpeed(-230),vy:mpsToWorldSpeed(31),vz:-3,rcsM2:100,extentRangeM:3,extentCrossM:2,extentVerticalM:1};
   shipboardRadarPhysicalSceneWip13B13=()=>[target];const dx=worldToMeters(target.x-receiver.x),dy=worldToMeters(target.y-receiver.y),dz=target.z-receiver.z;
   const dwell=shipboardRadarEchoFieldWip13B13({radarId:channel==='SPY'?'SPY1DV':'SPQ9B',band:channel==='SPY'?'S':'X',receiver,beamAz:Math.atan2(dy,dx),beamEl:Math.atan2(dz,Math.hypot(dx,dy)),beamHalfAzRad:deg(2),beamHalfElRad:deg(2),maxRangeKm:30,minRangeM:100,includeSea:false,rngState:{state:1}});
   if(dwell.echoes.length!==1)throw Error('ONE_PRIVATE_ECHO_REQUIRED');const echo=dwell.echoes[0],converted=shipboardRadarEchoToAirPlotWip13B13(echo,{air:1,missile:1,surface:0},channel==='SPY'?'SPY1DV_SEARCH_VOLUME':'SPQ9B_AIR'),plot=channel==='SPQ'?spq9bAnonymousPlotContractV34(converted):converted;
   const tr={_kfX:new Float64Array([worldToMeters(target.x),worldToMeters(target.y),target.z,worldSpeedToMps(target.vx),worldSpeedToMps(target.vy),target.vz]),_kfP:Float64Array.from({length:36},(_,i)=>i%7===0?25:0),sensorAge:0,sensorHits:10,confirmed:true,domain:'AIR'},before=Array.from(tr._kfX),prediction=trackRadarPrediction(tr,plot),measurement=[plot.rangeM,plot.azRad,plot.elRad,plot.radialMps],residual=prediction.h.map((v,i)=>i===1||i===2?angNorm(v-measurement[i]):v-measurement[i]);
   const accepted=trackEkfUpdateRadar(tr,plot),maxUpdate=Math.max(...before.map((v,i)=>Math.abs(v-tr._kfX[i]))),metadata=Object.fromEntries(fields.filter(k=>plot[k]!=null).map(k=>[k,plot[k]]));
   rows.push({face,bearing,channel,receiver,echoMetadata:Object.fromEntries(fields.filter(k=>echo[k]!=null).map(k=>[k,echo[k]])),plotMetadata:metadata,residual,accepted,maxUpdate,nis:tr._kfNis});
  }
 }
 const negative={_kfX:new Float64Array([1,2,-4,0,0,0]),_kfP:Float64Array.from({length:36},(_,i)=>i%7===0?25:0)};trackSyncLegacyFromEkf(negative);
 return {rows,rngBefore:rng,rngAfter:SIM_RNG_STATE,tickBefore:tick,tickAfter:simStepCounter,tracks:tracks.size,negativeLegacyZ:negative.z};
 }finally{shipboardRadarPhysicalSceneWip13B13=original.scene;observerNormalC=original.normal;observerRandomC=original.random;BATTLESPACE_DIAG_BYPASS=original.bypass;}
};
'''
rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 browser=launch(pw)
 for tag,name in [('MAIN','Aegis_SIM_v48_WIP_GUN_B1.html'),('AIR_ORIGIN_A','Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html')]:
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(browser,instrument((R/name).read_bytes(),HELPER),own=ship,errors=errors);q=p.evaluate('__AIR_ROUNDTRIP__()');rows.append({'tag':tag,'ship':ship,**q});p.close()
 browser.close()
new=[x for r in rows if r['tag']=='AIR_ORIGIN_A'for x in r['rows']];old=[x for r in rows if r['tag']=='MAIN'for x in r['rows']]
checks={'SPY16':sum(x['channel']=='SPY'for x in new)==16,'SPQWhitelist8':sum(x['channel']=='SPQ'for x in new)==8,'sixFieldsExact':all(x['plotMetadata']=={'sensorXWorld':x['receiver']['x'],'sensorYWorld':x['receiver']['y'],'sensorZM':x['receiver']['z'],'sensorVxMps':7,'sensorVyMps':-2,'sensorVzMps':.6}for x in new),'roundtripResidual':all(max(map(abs,x['residual']))<1e-8 for x in new),'ekfNoInnovation':all(x['accepted']and x['maxUpdate']<1e-8 for x in new),'baselineMismatchReproduced':all(max(map(abs,x['residual']))>1e-3 for x in old),'rngAndTicksUnchanged':all(r['rngBefore']==r['rngAfter']and r['tickBefore']==r['tickAfter']and r['tracks']==0 for r in rows),'negativeClampPreserved':all(r['negativeLegacyZ']==0 for r in rows),'pageErrors0':not errors}
result={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'testOnly':'Private reflector scene and zero-noise RNG stubs restored in finally; no live tracks or production coefficients changed.'};(B/'evidence/roundtrip.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':checks}));raise SystemExit(not result['pass'])
