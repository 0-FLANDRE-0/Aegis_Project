"""Separate offline 120/124/130 km route missions; no launch override or synthetic track."""
import argparse,base64,gzip,hashlib,json,re,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load,served_bytes
BRIDGE=r'''// DIAGNOSTIC_ONLY scenario/probe bridge. Production flight, INS, gate, RF and contact unchanged.
window.__HARPOON_RANGE_TEST__={
 setup:(o)=>{
  const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.resetEntireSessionV48Wip11A();d.ciwsB1Closure.setPaused(true);d.setTerrainDiagBypass(true);
  setControlDeckTabWip13C('ARM');h.forgetCombatTracksDiagnostic();
  window.__HARPOON_RANGE_TEST__.probe={closest:null,rngChangingTicks:{environment:0,target:0,harpoon:0},earlySearchTicks:0,modeEvents:[],lastMode:null};
  const truth=o.targetPresent===false?null:d.createWip13aSurfaceTargetFixture({rangeKm:o.rangeKm,bearingDeg:0,headingDeg:90,speedKt:o.speedKt});
  tracks.clear();selectedLockId=null;h.routeToggle();
  const inputs=[{x:o.rangeKm*500,y:-7000},{x:o.rangeKm*1000-8000,y:0}],adds=inputs.map(p=>h.routeAdd(p)),gate=h.autoTube(),request=h.fire();h.focusedTicks(12);tracks.clear();selectedLockId=null;
  return {declaredWaypointsM:inputs,adds,gate,request,truthFixture:truth,core:window.__CORE_SELFTEST_FAILURES__};
 },
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
   if(after.seeker.active&&!after.route.completed)probe.earlySearchTicks++;
   if(after.seeker.mode!==probe.lastMode){probe.modeEvents.push({ageS:after.ageS,mode:after.seeker.mode,rangeM:range});probe.lastMode=after.seeker.mode;}
  }
  const m=harpoonWorldA()[0],target=surfaceContacts.find(s=>s.targetRuntime);
  if(!m)return {count,missile:null};
  return {count,missile:{id:m.id,alive:m.alive,ageS:m.ageS,positionM:{...m.positionM},navPositionM:{...m.navPositionM},phase:m.phase,speedMps:m.speedMps,
   route:harpoonCopyA(m.route),fuelKg:m.fuelKg,massKg:m.massKg,pathM:m.pathM,outcome:m.outcome,impact:m.impact??null,fuelOutAgeS:m.fuelOutAgeS??null,
   insErrorM:Math.hypot(m.navPositionM.x-m.positionM.x,m.navPositionM.y-m.positionM.y,m.navPositionM.z-m.positionM.z),
   seeker:{active:m.seeker.active,mode:m.seeker.mode,observations:m.seeker.observations,scanReversals:m.seeker.scanReversals,lockCount:m.seeker.lockCount,
    lock:m.seeker.lock?{x:m.seeker.lock.x,y:m.seeker.lock.y,vx:m.seeker.lock.vx,vy:m.seeker.lock.vy}:null},history:harpoonCopyA(m.history)},
   target:target?{positionM:{x:worldToMeters(target.x),y:worldToMeters(target.y),z:target.z??0},velocityMps:{x:worldSpeedToMps(target.vx),y:worldSpeedToMps(target.vy)},
    damage:surfaceTargetSnapshotWip13A(target).damage,afloatState:target.targetRuntime.afloatState}:null,
   worldRng:SIM_RNG_STATE,shipTrackCount:tracks.size,memory:harpoonCopyA(m.memory),picture:harpoonOperatorPictureC(),probe:harpoonCopyA(window.__HARPOON_RANGE_TEST__.probe)};
 }
};
'''
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');ap.add_argument('--ranges',default='120,124,130');a=ap.parse_args()
source=Path(a.html);raw=source.read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);js=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',raw.decode(),re.S)[1])).decode()
anchor='window.__HARPOON_DIAG_A__=harpoonDiagnosticsA();';assert js.count(anchor)==1;injected=js.replace(anchor,anchor+'\n'+BRIDGE);assert injected.replace('\n'+BRIDGE,'')==js
main=out/'diagnostic-main.js';main.write_text(injected);body=served_bytes(source,main);errors=[];console=[];cases=[];began=time.monotonic()
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors);p.on('console',lambda m:console.append(m.text)if m.type=='error'else None)
 for r in [float(x)for x in a.ranges.split(',')]:
  for speed in [0,15]:
   setup=p.evaluate('o=>window.__HARPOON_RANGE_TEST__.setup(o)',{'rangeKm':r,'speedKt':speed});record={'rangeKm':r,'speedKt':speed,'setup':setup,'samples':[]};cases.append(record)
   assert setup['request']['ok'],setup
   initial=p.evaluate('window.__HARPOON_RANGE_TEST__.step(0)');record['frozenMemory']=initial['memory'];record['frozenProgram']=initial['missile']['route']['program'];state=initial
   for k in range(123):
    state=p.evaluate('window.__HARPOON_RANGE_TEST__.step(300)');record['samples'].append(state['missile'])
    if k%24==0:print(json.dumps({'rangeKm':r,'speedKt':speed,'ageS':state['missile']['ageS'],'mode':state['missile']['seeker']['mode']}),flush=True)
    if not state['missile']['alive']:break
   record['final']=state;record['outcome']=state['missile']['outcome'];missile=state['missile'];events=state['probe']['modeEvents'];activation=next((e['ageS']for e in events if e['mode']!='OFF'),None)
   record['checks']={'normalManualCoordinateGateAccepted':setup['gate']['ok']and setup['request']['ok'],
    'allWaypointsPassedInOrder':missile['route']['completed']and [q['index']for q in missile['route']['passes']]==[0,1],
    'finalWaypointUsesPlaneCrossing':missile['route']['passes'][-1]['method']=='INS_PLANE_CROSSING',
    'noSeekerBeforeFinalWaypoint':state['probe']['earlySearchTicks']==0 and activation is not None and activation>=missile['route']['completedAgeS'],
    'independentPhysicalRfTrackAcquired':any(e['mode']=='TRACK'for e in events),
    'frozenProgramAndMemoryNeverUpdated':missile['route']['program']==record['frozenProgram']and state['memory']==record['frozenMemory'],
    'noShipTrackOrDatalinkTelemetry':state['shipTrackCount']==0 and all(q['trackId']is None for q in state['picture']['launches']),
    'fixedTickGuidanceDoesNotConsumeGlobalRng':all(v==0 for v in state['probe']['rngChangingTicks'].values()),
    'corePassAndMissionTerminates':setup['core']==[]and not missile['alive']}
   print(json.dumps({'rangeKm':r,'speedKt':speed,'outcome':record['outcome'],'ageS':missile['ageS'],'pathKm':missile['pathM']/1000,'fuelKg':missile['fuelKg'],'checks':record['checks']}),flush=True)
 # Empty-water negative control: same declared route; no fixture vessel and no track.
 setup=p.evaluate('o=>window.__HARPOON_RANGE_TEST__.setup(o)',{'rangeKm':120,'speedKt':0,'targetPresent':False})
 assert setup['request']['ok'];negative_initial=p.evaluate('window.__HARPOON_RANGE_TEST__.step(0)');negative_state=negative_initial
 for k in range(123):
  negative_state=p.evaluate('window.__HARPOON_RANGE_TEST__.step(300)')
  if not negative_state['missile']['alive']:break
 empty_water={'setup':setup,'final':negative_state,'checks':{
  'noTargetDoesNotBecomeForcedHit':negative_state['missile']['outcome']!='SURFACE_CONTACT',
  'emptySeaHasNoConfirmedSeekerTrack':not any(e['mode']=='TRACK'for e in negative_state['probe']['modeEvents']),
  'lastWaypointStillRequiredWithEmptySea':negative_state['probe']['earlySearchTicks']==0 and negative_state['missile']['route']['completed']}}
 print(json.dumps({'emptyWater':empty_water['checks'],'outcome':negative_state['missile']['outcome']}),flush=True)
 b.close()
checks={name:all(c['checks'][name]for c in cases)for name in cases[0]['checks']};checks.update(empty_water['checks']);checks.update(pageErrorsZero=not errors,consoleErrorsZero=not console)
report={'schema':'HARPOON_E_OFFLINE_ROUTE_RANGE','source':source.name,'sha256':hashlib.sha256(raw).hexdigest(),'originalMainSha256':hashlib.sha256(js.encode()).hexdigest(),
 'fixtureBridgeOnlyChange':True,'servedDiagnosticSha256':hashlib.sha256(body).hexdigest(),'bridgeSha256':hashlib.sha256(BRIDGE.encode()).hexdigest(),
 'noGateOverride':True,'syntheticTrack':False,'terrainBypass':True,'seed':'0x6d2b79f5','clock':'FOCUSED_60HZ_ENVIRONMENT_TARGET_ORDNANCE_NOT_FULL_SHIP_OR_NATIVE_RAF',
 'checks':checks,'cases':cases,'emptyWaterNegativeControl':empty_water,'physicalContacts':sum(c['outcome']=='SURFACE_CONTACT'for c in cases),'physicalContactCountSeparateFromContractChecks':True,
 'errors':errors,'console':console,'wallSeconds':time.monotonic()-began,'pass':all(checks.values())}
(out/'range.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'physicalContacts':report['physicalContacts'],'cases':len(cases),'pass':report['pass']}));raise SystemExit(0 if report['pass']else 1)
