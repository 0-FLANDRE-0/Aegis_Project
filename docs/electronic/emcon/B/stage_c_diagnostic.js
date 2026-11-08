// EMCON_B Commit C — disposable runtime probes. Never shipped in the product.
function emconCStableB(value){return JSON.parse(JSON.stringify(value));}
function emconCRfRngB(){return {state:{...SHIPBOARD_RADAR_RF_RNG_WIP13B13},spare:{...SHIPBOARD_RADAR_RF_SPARE_WIP13B13}};}
function emconCOwnSensorProbeB(){
  const r=ACTIVE_SHIP_RUNTIME,id=r.entityId,o=observerC(r),originalEcho=shipboardRadarEchoFieldWip13B13;
  const saved={emconActive,state:structuredClone(prepareEmconB(r)),enabled:{...o.enabled},rf:emconCRfRngB(),spyAccumulator:spyScheduler.accumulatorS,
    spqRotorAngle:spq9bRotorAngle,spqPrevRotorAngle:spq9bPrevRotorAngle,spqTimeS:spq9bTimeS,
    navRotorAngle:bridgeMasterERotorAngle,navPrevRotorAngle:bridgeMasterEPrevRotorAngle,navTimeS:bridgeMasterETimeS,
    shore:bridgeMasterEShoreEchoes.map(q=>({...q}))};
  const calls={SPY1DV:0,SPQ9B:0,BRIDGEMASTER_E:0,other:0};
  shipboardRadarEchoFieldWip13B13=opts=>{const key=Object.hasOwn(calls,opts?.radarId)?opts.radarId:'other';calls[key]++;return originalEcho(opts);};
  const restoreRng=()=>{Object.assign(SHIPBOARD_RADAR_RF_RNG_WIP13B13,saved.rf.state);Object.assign(SHIPBOARD_RADAR_RF_SPARE_WIP13B13,saved.rf.spare);};
  const reset=()=>{emconActive=false;Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});r.combatSystem.emconB=structuredClone(saved.state);restoreRng();
    spyScheduler.accumulatorS=0;spq9bRotorAngle=0;spq9bPrevRotorAngle=0;bridgeMasterERotorAngle=0;bridgeMasterEPrevRotorAngle=0;
    bridgeMasterEShoreEchoes.length=0;for(const key of Object.keys(calls))calls[key]=0;};
  const one=(category,radarId,run,readLifecycle)=>{
    reset();emconCommandB(id,{category,policy:'SILENT'},'DIAGNOSTIC');const rngBeforeSilent=emconCRfRngB(),lifeBefore=readLifecycle();run();
    const silent={calls:{...calls},rngBefore:rngBeforeSilent,rngAfter:emconCRfRngB(),lifecycleBefore:lifeBefore,lifecycleAfter:readLifecycle(),physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>q.family)};
    reset();const rngBeforeActive=emconCRfRngB();run();
    const active={calls:{...calls},rngBefore:rngBeforeActive,rngAfter:emconCRfRngB(),lifecycleAfter:readLifecycle(),physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>q.family)};
    return {category,radarId,silent,active};
  };
  let result;
  try{
    result={schema:'AEGIS_EMCON_B_C_OWN_SENSOR_PROBE_1',
      air:one('AIR_SEARCH','SPY1DV',()=>updateSpyScheduler(Math.max(.1,SENSOR_MODEL.spy1dv.schedulerCycleS*1.1)),()=>({accumulatorS:spyScheduler.accumulatorS,cycleCounter:spyScheduler.cycleCounter})),
      surface:one('SURFACE_SEARCH','SPQ9B',()=>updateSpq9bRadar(.5),()=>({rotor:spq9bRotorAngle,timeS:spq9bTimeS})),
      nav:one('NAV','BRIDGEMASTER_E',()=>updateBridgeMasterERadar(.5),()=>({rotor:bridgeMasterERotorAngle,timeS:bridgeMasterETimeS,shoreCount:bridgeMasterEShoreEchoes.length}))};
  }finally{
    shipboardRadarEchoFieldWip13B13=originalEcho;emconActive=saved.emconActive;r.combatSystem.emconB=saved.state;Object.assign(o.enabled,saved.enabled);restoreRng();
    spyScheduler.accumulatorS=saved.spyAccumulator;spq9bRotorAngle=saved.spqRotorAngle;spq9bPrevRotorAngle=saved.spqPrevRotorAngle;spq9bTimeS=saved.spqTimeS;
    bridgeMasterERotorAngle=saved.navRotorAngle;bridgeMasterEPrevRotorAngle=saved.navPrevRotorAngle;bridgeMasterETimeS=saved.navTimeS;
    bridgeMasterEShoreEchoes.length=0;bridgeMasterEShoreEchoes.push(...saved.shore);
  }
  return result;
}
function emconCObserverSensorProbeB(allyProfileId){
  const scene=emitterABaselineFleetSceneA({allyProfileId}),r=electronicShipsF().find(q=>q.role==='ALLY'),id=r.entityId,o=observerC(r),originalExtract=observerExtractC;
  const saved={state:structuredClone(prepareEmconB(r)),emcon:o.emcon,enabled:{...o.enabled},rng:structuredClone(o.rng),rotors:{...o.rotors}};
  let calls=0;observerExtractC=(...args)=>{calls++;return originalExtract(...args);};
  const reset=()=>{r.combatSystem.emconB=structuredClone(saved.state);o.emcon=false;Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});Object.assign(o.rng,structuredClone(saved.rng));Object.assign(o.rotors,saved.rotors);calls=0;};
  const one=(category,run,rotorKey)=>{reset();emconCommandB(id,{category,policy:'SILENT'},'DIAGNOSTIC');const rngBefore=structuredClone(o.rng),rotorBefore=rotorKey?o.rotors[rotorKey]:null;run();
    const silent={calls,rngBefore,rngAfter:structuredClone(o.rng),rotorBefore,rotorAfter:rotorKey?o.rotors[rotorKey]:null};
    reset();const activeRngBefore=structuredClone(o.rng);run();const active={calls,rngBefore:activeRngBefore,rngAfter:structuredClone(o.rng),rotorAfter:rotorKey?o.rotors[rotorKey]:null};return {category,silent,active};};
  let result;
  try{result={schema:'AEGIS_EMCON_B_C_OBSERVER_SENSOR_PROBE_1',profileId:allyProfileId,entityId:id,
    air:one('AIR_SEARCH',()=>observerSpyCycleC(r),null),surface:one('SURFACE_SEARCH',()=>observerAuxStepC(r,.5,'SPQ'),'SPQ'),nav:one('NAV',()=>observerAuxStepC(r,.5,'NAV'),'NAV')};}
  finally{observerExtractC=originalExtract;r.combatSystem.emconB=saved.state;o.emcon=saved.emcon;Object.assign(o.enabled,saved.enabled);Object.assign(o.rng,saved.rng);Object.assign(o.rotors,saved.rotors);}
  return result;
}
function emconCEcmProbeB(){
  const r=ACTIVE_SHIP_RUNTIME,id=r.entityId,original={state:structuredClone(prepareEmconB(r)),emconActive,noiseJamActive,deceptJamActive,jammerAutoTrack,jammerBearing,allocator:{...slq32EaState}};
  let result;
  try{
    r.combatSystem.emconB=emconDefaultStateB(r);emconActive=false;noiseJamActive=true;deceptJamActive=false;jammerAutoTrack=false;jammerBearing=0;
    Object.assign(slq32EaState,{noiseShare:.75,targetNoiseShare:.75,deceptionShare:0,targetDeceptionShare:0,resourceUsed:.75,policy:'MANUAL_NOISE'});
    const before={request:{noiseJamActive,deceptJamActive},allocator:{...slq32EaState},physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>q.family)};
    const commandSilent=emconCommandB(id,{category:'ECM',policy:'SILENT'},'DIAGNOSTIC');
    const em={seekerOn:true,x:r.navigation.positionWorld.x+metersToWorld(5000),y:r.navigation.positionWorld.y,z:100,heading:Math.PI,flight:{bodyPitch:0}},s={gimbalAz:0,gimbalEl:0},p={hojEnabled:true,rfBandTag:'IJ',receiverNoiseBandwidthHz:12e6,receiverNoiseFigureDb:6};
    const silent={request:{noiseJamActive,deceptJamActive},allocator:{...slq32EaState},physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>q.family),sample:electronicJammerSampleF(r,em,p,'NOISE'),hoj:electronicHojF(em,s,p)};
    const commandRadiate=emconCommandB(id,{category:'ECM',policy:'RADIATE'},'DIAGNOSTIC');updateSlq32EaAllocator(1);
    const resumed={request:{noiseJamActive,deceptJamActive},allocator:{...slq32EaState},physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>q.family)};
    result={schema:'AEGIS_EMCON_B_C_ECM_PROBE_1',before,commandSilent,silent,commandRadiate,resumed};
  }finally{r.combatSystem.emconB=original.state;emconActive=original.emconActive;noiseJamActive=original.noiseJamActive;deceptJamActive=original.deceptJamActive;jammerAutoTrack=original.jammerAutoTrack;jammerBearing=original.jammerBearing;Object.assign(slq32EaState,original.allocator);}
  return result;
}
window.__EMCON_B_C_DIAG__=Object.freeze({ownSensors:emconCOwnSensorProbeB,observerSensors:emconCObserverSensorProbeB,ecm:emconCEcmProbeB});
