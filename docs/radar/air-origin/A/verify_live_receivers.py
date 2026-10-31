"""Natural onboard SPY/SPQ AIR routing, independently isolated, full fixed ticks."""
from pathlib import Path
import json,sys,time
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
helper=r'''
window.__AIR_LIVE_RECEIVERS__=channel=>{
 _wip75ResetCase(971912);BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;engagementControlMode='MANUAL';gunB1AutoState().enabled=false;emconActive=false;
 const fields=['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps'],old={radar:updateRadar,spq:updateSpq9bRadar,echo:shipboardRadarEchoFieldWip13B13,ekf:trackEkfUpdateRadar},expected=new Map(),records=[];
 try{
  if(channel==='SPQ9B')updateRadar=()=>{};else updateSpq9bRadar=()=>{};
  shipboardRadarEchoFieldWip13B13=function(opts){const q=old.echo(...arguments),r=opts.receiver;
   expected.set(opts.radarId,{sensorXWorld:Number(r.x)||0,sensorYWorld:Number(r.y)||0,sensorZM:Math.max(.2,Number(r.z)||5),sensorVxMps:Number(r.vxMps)||0,sensorVyMps:Number(r.vyMps)||0,sensorVzMps:Number(r.vzMps)||0});return q;};
  trackEkfUpdateRadar=function(tr,m){const q=old.ekf(...arguments);if((m.source??'').includes(channel==='SPQ9B'?'SPQ9B_AIR':'SPY1DV_')&&!surfaceSensorFamilyWip13B9(m.source))records.push({step:simStepCounter,source:m.source,metadata:Object.fromEntries(fields.filter(k=>m[k]!=null).map(k=>[k,m[k]])),expected:{...expected.get(channel)},accepted:q,nis:tr._kfNis});return q;};
  const h=deg(30),r=kmToWorld(8);spawnEnemyMissile({id:1,x:aircraft.x()+r*Math.cos(h),y:aircraft.y()+r*Math.sin(h),z:20,vx:mpsToWorldSpeed(-280*Math.cos(h)),vy:mpsToWorldSpeed(-280*Math.sin(h)),heading:h+Math.PI,asmType:'Kh-35U',lastKnownShipX:aircraft.x(),lastKnownShipY:aircraft.y()});
  const initialTracks=tracks.size;for(let i=0;i<360;i++)simulateFixedTick(SIM_FIXED_DT);
  return {channel,initialTracks,records,tracks:[...tracks].map(([id,t])=>({id,source:t.sensorSource,z:t.z,age:t.sensorAge})),core:window.__CORE_SELFTEST_FAILURES__};
 }finally{updateRadar=old.radar;updateSpq9bRadar=old.spq;shipboardRadarEchoFieldWip13B13=old.echo;trackEkfUpdateRadar=old.ekf;}
};
'''
rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for tag,file in [('MAIN','Aegis_SIM_v48_WIP_GUN_B1.html'),('AIR_ORIGIN_A','Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html')]:
  for channel in ['SPY1DV','SPQ9B']:
   p=load_fleet(b,instrument((R/file).read_bytes(),helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(600000);q=p.evaluate('c=>__AIR_LIVE_RECEIVERS__(c)',channel);rows.append({'tag':tag,**q});p.close()
 b.close()
new=[q for q in rows if q['tag']=='AIR_ORIGIN_A'];checks={'bothChannelsObserved':all(q['records']for q in new),'actualReceiverAtEkf':all(r['metadata']==r['expected']for q in new for r in q['records']),'noInjectedTracks':all(q['initialTracks']==0 for q in rows),'coreAndErrors0':not errors and all(not q['core']for q in rows)}
(B/'evidence/live-receivers.json').write_text(json.dumps({'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'isolation':'Other onboard radar update disabled only in diagnostic page; no plot insertion or forced detection. Actual RF noise/Pd preserved.'},indent=2)+'\n');print(json.dumps({'pass':all(checks.values()),'checks':checks,'recordCounts':[(q['tag'],q['channel'],len(q['records']))for q in rows]}));raise SystemExit(not all(checks.values()))
