"""Offline range fixtures only; unmodified D flight/RF/contact functions, no production injection."""
import argparse,base64,gzip,hashlib,json,re,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load,served_bytes
BRIDGE=r'''
// DIAGNOSTIC_ONLY. One-time synthetic external targeting estimate, not real ship radar.
// Scenario truth and the independent estimate are initialized from declared inputs.
// Never installed into the deliverable. Actual RF receiver/contact/flight are unchanged.
window.__HARPOON_RANGE_TEST__={
 setup:(o)=>{
  window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);
  window.__NAVAL_SIM_DIAG__.setTerrainDiagBypass(true);window.__NAVAL_SIM_DIAG__.setEmcon(false);
  window.__HARPOON_RANGE_TEST__.probe={closest:null,rngChangingTicks:{environment:0,target:0,harpoon:0},modeEvents:[],lastMode:null};
  const heading=deg(o.headingDeg??90),speed=(o.speedKt??0)*.514444,bearing=deg(o.bearingDeg??0);
  const truth=window.__NAVAL_SIM_DIAG__.createWip13aSurfaceTargetFixture({rangeKm:o.rangeKm,bearingDeg:o.bearingDeg??0,headingDeg:o.headingDeg??90,speedKt:o.speedKt??0});
  tracks.clear();const tr=makeSurfaceMissileFixtureTrackWip13C4({trackId:8490001,rangeKm:o.rangeKm,bearingRad:bearing,
   vxMps:Math.cos(heading)*speed+(o.velocityErrorX??0),vyMps:Math.sin(heading)*speed+(o.velocityErrorY??0),
   identity:'TRAINING_TARGET',posSigmaM:o.positionSigmaM??50,velSigmaMps:o.velocitySigmaMps??.5,maneuverProbability:0});
  tr.sensorSource='DIAGNOSTIC_EXTERNAL_ESTIMATE';tr._surfaceSensorContributorsWip13B9={};tr._surfaceExtentEstimateWip13B8.source='DIAGNOSTIC_EXTERNAL_ESTIMATE';
  tr.x+=metersToWorld(o.positionErrorX??0);tr.y+=metersToWorld(o.positionErrorY??0);
  tr._kfX[0]+=o.positionErrorX??0;tr._kfX[1]+=o.positionErrorY??0;
  tracks.set(tr.trackId,tr);selectedLockId=tr.trackId;
  const gate=harpoonAutoTubeGateD(),singleTubeGate=harpoonGateA(tr.trackId,harpoonRuntimeA().tubes[0].id);
  return {truthFixture:truth,gate,singleTubeGate,trackEstimate:{x:Array.from(tr._kfX),P:Array.from(tr._kfP)},core:window.__CORE_SELFTEST_FAILURES__};
 },
 start:(flightOnly=false)=>{
  const tr=tracks.get(selectedLockId),gate=harpoonAutoTubeGateD();
  if(gate.ok){const request=harpoonRequestFireA();window.__HARPOON_DIAG_A__.focusedTicks(12);return {request,gate,diagnosticGateBypass:false};}
  if(!flightOnly||gate.reason!=='INS_PREDICTION_BASKET_INSUFFICIENT')return {gate,request:gate,diagnosticGateBypass:false};
  // Isolated propulsion/navigation/seeker envelope test, not a permitted UI launch.
  // Shadow ONLY the release gate in the exact release constructor's lexical closure.
  // No target truth read, no guidance/RF/contact replacement or flight-time correction.
  const r=harpoonRuntimeA(),tube=r.tubes.find(t=>t.loaded),spec=harpoonTubeSpecA(tube.id),frame=shipGameFrameV1(),
   approved={ok:true,reason:null,trackId:tr.trackId,tubeId:tube.id,memory:harpoonMemoryA(tr),muzzleM:frame.pointToWorld(spec.muzzle),
    axis:frame.vectorToWorld(spec.axis),rangeKm:horizDistKm(aircraft.x(),aircraft.y(),tr.x,tr.y),authority:surfaceMissileIdentityPolicyWip13C4(tr._operatorIdentity,'MANUAL',false),truthUsed:false};
  const release=(function(harpoonGateA){return eval('('+harpoonReleaseA.toString()+')');})(()=>approved);
  release({trackId:tr.trackId,tubeId:tube.id});return {request:{ok:true,tubeId:tube.id},gate,diagnosticGateBypass:true};
 },
 removeShipTracks:()=>{tracks.clear();selectedLockId=null;return {remainingTracks:tracks.size};},
 step:(n=300)=>{
  let count=0;
  for(;count<n;count++){const m=harpoonWorldA()[0];if(!m?.alive)break;
   const probe=window.__HARPOON_RANGE_TEST__.probe,r0=SIM_RNG_STATE;
   updateMaritimeEnvironmentWip13A3(SIM_FIXED_DT);const r1=SIM_RNG_STATE;
   updateSurfaceContacts(SIM_FIXED_DT);const r2=SIM_RNG_STATE;
   harpoonStepA(SIM_FIXED_DT);const r3=SIM_RNG_STATE;simStepCounter++;
   probe.rngChangingTicks.environment+=r0!==r1;probe.rngChangingTicks.target+=r1!==r2;probe.rngChangingTicks.harpoon+=r2!==r3;
   const after=harpoonWorldA()[0],target=surfaceContacts.find(s=>s.targetRuntime),range=target?Math.hypot(after.positionM.x-worldToMeters(target.x),after.positionM.y-worldToMeters(target.y)):null;
   if(range!=null&&(!probe.closest||range<probe.closest.rangeM))probe.closest={ageS:after.ageS,rangeM:range,positionM:{...after.positionM},seekerMode:after.seeker.mode,
    targetPositionM:{x:worldToMeters(target.x),y:worldToMeters(target.y)},navPositionM:{...after.navPositionM},lock:harpoonCopyA(after.seeker.lock)};
   if(after.seeker.mode!==probe.lastMode){probe.modeEvents.push({ageS:after.ageS,mode:after.seeker.mode,rangeM:range});probe.lastMode=after.seeker.mode;}
  }
  const m=harpoonWorldA()[0],target=surfaceContacts.find(s=>s.targetRuntime);
  if(!m)return {count,missile:null};
  return {count,missile:{id:m.id,alive:m.alive,ageS:m.ageS,positionM:{...m.positionM},navPositionM:{...m.navPositionM},phase:m.phase,speedMps:m.speedMps,
   fuelKg:m.fuelKg,massKg:m.massKg,pathM:m.pathM,outcome:m.outcome,impact:m.impact??null,fuelOutAgeS:m.fuelOutAgeS??null,
   insErrorM:Math.hypot(m.navPositionM.x-m.positionM.x,m.navPositionM.y-m.positionM.y,m.navPositionM.z-m.positionM.z),
   seeker:{active:m.seeker.active,mode:m.seeker.mode,observations:m.seeker.observations,scanReversals:m.seeker.scanReversals,lockCount:m.seeker.lockCount,
    lock:m.seeker.lock?{x:m.seeker.lock.x,y:m.seeker.lock.y,vx:m.seeker.lock.vx,vy:m.seeker.lock.vy}:null},history:harpoonCopyA(m.history)},
   target:target?{positionM:{x:worldToMeters(target.x),y:worldToMeters(target.y),z:target.z??0},velocityMps:{x:worldSpeedToMps(target.vx),y:worldSpeedToMps(target.vy)},
    damage:surfaceTargetSnapshotWip13A(target).damage,afloatState:target.targetRuntime.afloatState}:null,
   worldRng:SIM_RNG_STATE,shipTrackCount:tracks.size,memory:harpoonCopyA(m.memory),picture:harpoonOperatorPictureC(),probe:harpoonCopyA(window.__HARPOON_RANGE_TEST__.probe)};
 }
};
'''
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');ap.add_argument('--ranges',default='60,100,120');ap.add_argument('--speeds',default='0,15');ap.add_argument('--flight-only',action='store_true');a=ap.parse_args()
source=Path(a.html);raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
js=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',raw.decode(),re.S)[1])).decode()
anchor='window.__HARPOON_DIAG_A__=harpoonDiagnosticsA();';assert js.count(anchor)==1
injected=js.replace(anchor,anchor+'\n'+BRIDGE);assert injected.replace('\n'+BRIDGE,'')==js
main=out/'diagnostic-main.js';main.write_text(injected);body=served_bytes(source,main)
results=[];errors=[];console=[];began=time.monotonic()
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors)
 p.on('console',lambda m:console.append(m.text[:1500])if m.type=='error'else None)
 for r in [float(x)for x in a.ranges.split(',')]:
  for speed in [float(x)for x in a.speeds.split(',')]:
   case={'rangeKm':r,'speedKt':speed,'bearingDeg':0,'headingDeg':90,'positionSigmaM':50,'velocitySigmaMps':.5}
   setup=p.evaluate('o=>window.__HARPOON_RANGE_TEST__.setup(o)',case);start=p.evaluate('v=>window.__HARPOON_RANGE_TEST__.start(v)',a.flight_only)
   record={'input':case,'setup':setup,'start':start,'samples':[],'seekerTransitions':[]};results.append(record)
   if not start['request']['ok']:
    record['outcome']='LAUNCH_DENIED';print(json.dumps({'rangeKm':r,'speedKt':speed,'outcome':record['outcome'],'reason':start['gate']['reason'],'predictionSigmaM':setup['singleTubeGate'].get('predictionSigmaM')},ensure_ascii=False),flush=True);continue
   p.evaluate('window.__HARPOON_RANGE_TEST__.removeShipTracks()');initial=p.evaluate('window.__HARPOON_RANGE_TEST__.step(0)');record['frozenMemory']=initial['memory'];record['initialRng']=initial['worldRng'];last_mode=None;state=initial
   for k in range(123):
    state=p.evaluate('window.__HARPOON_RANGE_TEST__.step(300)');m=state['missile'];m['worldRngAtSample']=state['worldRng'];record['samples'].append(m)
    mode=m['seeker']['mode']
    if mode!=last_mode:
     record['seekerTransitions'].append({'ageS':m['ageS'],'mode':mode,'rangeToTargetM':((m['positionM']['x']-state['target']['positionM']['x'])**2+(m['positionM']['y']-state['target']['positionM']['y'])**2)**.5});last_mode=mode
    if k%12==0:print(json.dumps({'rangeKm':r,'speedKt':speed,'ageS':round(m['ageS'],2),'phase':m['phase'],'fuelKg':round(m['fuelKg'],2),'seeker':mode}),flush=True)
    if not m['alive']:break
   record['final']=state;record['outcome']=state['missile']['outcome']or'UNFINISHED'
   record['checks']={'corePass':setup['core']==[],'shipTracksRemainAbsent':state['shipTrackCount']==0,'noShipGuidanceUpdates':state['memory']==record['frozenMemory'],
    'flightRngIndependentPerFixedTick':all(v==0 for v in state['probe']['rngChangingTicks'].values()),'finishedWithin600Seconds':not state['missile']['alive'],
    'shipPictureHasNoMissilePositionWithoutObservation':all(q['trackId']is None for q in state['picture']['launches']),
    'independentArhAcquired':any(q['seeker']['mode']=='TRACK'for q in record['samples']),
    'physicalTargetContact':record['outcome']=='SURFACE_CONTACT'}
   print(json.dumps({'rangeKm':r,'speedKt':speed,'outcome':record['outcome'],'timeS':round(state['missile']['ageS'],3),'pathKm':round(state['missile']['pathM']/1000,3),'fuelKg':round(state['missile']['fuelKg'],3),'insErrorM':round(state['missile']['insErrorM'],3),'checks':record['checks']},ensure_ascii=False),flush=True)
 b.close()
report={'schema':'HARPOON_D_OFFLINE_LONG_RANGE','source':source.name,'originalHtmlSha256':sha,'originalMainSha256':hashlib.sha256(js.encode()).hexdigest(),'servedDiagnosticHtmlSha256':hashlib.sha256(body).hexdigest(),
 'fixtureBridgeSha256':hashlib.sha256(BRIDGE.encode()).hexdigest(),'testScriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'fixtureBridgeOnlyChange':True,'flightSeekerRfContactSourceUnchanged':True,'externalCueFixtureNotProductionCapability':True,'terrainBypass':True,'clock':'FOCUSED_FULL_60HZ_HARPOON_AND_PHYSICAL_TARGET_NOT_ALL_SHIP_SUBSYSTEMS',
 'flightOnlyBypassRequested':a.flight_only,'seed':'0x6d2b79f5','cases':results,'errors':errors,'console':console,'wallSeconds':time.monotonic()-began}
(out/'range.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'report':str(out/'range.json'),'cases':len(results),'errors':errors,'console':console},ensure_ascii=False))
raise SystemExit(0 if not errors and not console else 1)
