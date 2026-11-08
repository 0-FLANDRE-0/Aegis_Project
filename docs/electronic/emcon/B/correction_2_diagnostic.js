// TEST_ONLY: PR74 correction-2 hard-silent and selective-breakout probes.
// This module is injected only into disposable diagnostic HTML.
function emconCorr2CloneB(v){return structuredClone(v);}
function emconCorr2RuntimeB(id){const r=ENGAGEMENT_RUNTIME.ships.get(String(id));if(!r)throw Error('EMCON_CORR2_OWNER');return r;}
function emconCorr2EntriesB(r){return (shipEmitterRegistryA(r)?.entries??[]).filter(q=>q.installed!==false&&q.physicalEmission!==false&&q.outputKind!=='REGISTERED_INACTIVE');}
function emconCorr2LinkB(r){
  const n=prepareNetworkG(r);return {enabled:n.settings.enabled,shareTracks:n.settings.shareTracks,cooperativeDefense:n.settings.cooperativeDefense,
    peers:[...n.peers].map(([id,p])=>({id,connected:!!p.connected,reason:p.reason??null})).sort((a,b)=>a.id.localeCompare(b.id))};
}
function emconCorr2RngB(r){
  if(r===ACTIVE_SHIP_RUNTIME)return {rf:{...SHIPBOARD_RADAR_RF_RNG_WIP13B13},spare:{...SHIPBOARD_RADAR_RF_SPARE_WIP13B13}};
  return emconCorr2CloneB(observerC(r).rng);
}
function emconCorr2AllocatorB(r){return emconCorr2CloneB(r===ACTIVE_SHIP_RUNTIME?slq32EaState:r.ew.slq32Allocator);}
function emconCorr2PrimeEcmB(r){
  const bearing=0,command=electronicCommandF(r.entityId,{noiseRequested:true,deceptionRequested:true,auto:false,autoAim:false,bearingRad:bearing},'DIAGNOSTIC');
  if(!command.ok)throw Error('EMCON_CORR2_ECM_COMMAND:'+command.reason);
  if(r===ACTIVE_SHIP_RUNTIME){jammerBearing=bearing;updateSlq32EaAllocator(10);}
  else prepareElectronicF(r).context.step(10);
  return {settings:electronicSettingsF(r),allocator:emconCorr2AllocatorB(r)};
}
function emconCorr2SignalsB(r){
  const x=r.navigation.positionWorld.x+metersToWorld(5000),y=r.navigation.positionWorld.y,z=100,rx={x,y,z},p={hojEnabled:true,rfBandTag:'IJ',receiverNoiseBandwidthHz:12e6,receiverNoiseFigureDb:6,receiveApertureM2:.006,noiseJamBandCoupling:1,deceptionJamBandCoupling:1},em={seekerOn:true,x,y,z,heading:Math.PI,flight:{bodyPitch:0}},s={gimbalAz:0,gimbalEl:0};
  return {noise:electronicJammerSampleF(r,rx,p,'NOISE'),deception:electronicJammerSampleF(r,rx,p,'DECEPTION'),hoj:electronicHojF(em,s,p)};
}
function emconCorr2ForceRadiateB(r){
  for(const other of electronicShipsF())if(other!==r&&shipEmitterRegistryA(other)?.entries?.some(q=>q.category==='ECM'&&q.outputKind==='ECM'))emconCommandB(other.entityId,{category:'ECM',policy:'SILENT'},'DIAGNOSTIC');
  networkSetRadarG(r,false);emconCommandB(r.entityId,{reset:true},'DIAGNOSTIC');
  for(const q of emconCorr2EntriesB(r)){const result=emconCommandB(r.entityId,{equipmentId:q.id,override:'FORCE_RADIATE'},'DIAGNOSTIC');if(!result.ok)throw Error('EMCON_CORR2_FORCE:'+q.id+':'+result.reason);}
  const ecm=emconCorr2PrimeEcmB(r);return {state:emconExportStateB(r),masterSilent:emconMasterSilentB(r),ecm};
}
function emconCorr2SensorPassB(r){
  const calls={SPY:0,SPQ:0,NAV:0},rngBefore=emconCorr2RngB(r),trackBefore=observerC(r).tracks.size;
  if(r===ACTIVE_SHIP_RUNTIME){
    const original=shipboardRadarEchoFieldWip13B13;shipboardRadarEchoFieldWip13B13=opts=>{const k=opts?.radarId==='SPY1DV'?'SPY':opts?.radarId==='SPQ9B'?'SPQ':opts?.radarId==='BRIDGEMASTER_E'?'NAV':null;if(k)calls[k]++;return original(opts);};
    try{spyScheduler.accumulatorS=0;spq9bRotorAngle=spq9bPrevRotorAngle=0;bridgeMasterERotorAngle=bridgeMasterEPrevRotorAngle=0;updateSpyScheduler(Math.max(.1,SENSOR_MODEL.spy1dv.schedulerCycleS*1.1));updateSpq9bRadar(.5);updateBridgeMasterERadar(.5);}
    finally{shipboardRadarEchoFieldWip13B13=original;}
  }else{
    const original=observerExtractC;observerExtractC=(owner,opts,meta)=>{const k=opts?.radarId==='SPY1DV'?'SPY':opts?.radarId==='SPQ9B'?'SPQ':opts?.radarId==='BRIDGEMASTER_E'?'NAV':null;if(k)calls[k]++;return original(owner,opts,meta);};
    try{observerSpyCycleC(r);observerAuxStepC(r,.5,'SPQ');observerAuxStepC(r,.5,'NAV');}
    finally{observerExtractC=original;}
  }
  return {calls,rngBefore,rngAfter:emconCorr2RngB(r),trackBefore,trackAfter:observerC(r).tracks.size};
}
function emconCorr2SnapshotB(r){
  return {masterSilent:emconMasterSilentB(r),state:emconExportStateB(r),decisions:emconCorr2EntriesB(r).map(q=>emconEquipmentDecisionB(r,q.id)),physical:electronicShipPhysicalEmittersDeclaredA(r).map(q=>({family:q.family,equipmentId:q.equipmentId??null})),settings:electronicSettingsF(r),allocator:emconCorr2AllocatorB(r),signals:emconCorr2SignalsB(r),link:emconCorr2LinkB(r)};
}
function emconCorr2HardSilentB(id){
  const r=emconCorr2RuntimeB(id),primed=emconCorr2ForceRadiateB(r),before=emconCorr2SnapshotB(r),command=emconGlobalCommandB(r.entityId,true,'DIAGNOSTIC'),after=emconCorr2SnapshotB(r),sensors=emconCorr2SensorPassB(r);
  return {schema:'AEGIS_EMCON_B_CORRECTION_2_HARD_SILENT_1',ownerEntityId:r.entityId,profileId:r.profileId,primed,before,command,after,sensors};
}
function emconCorr2BreakoutB(id,kind,value){
  const r=emconCorr2RuntimeB(id);emconCorr2ForceRadiateB(r);const silent=emconGlobalCommandB(r.entityId,true,'DIAGNOSTIC');if(!silent.ok)throw Error('EMCON_CORR2_GLOBAL:'+silent.reason);
  const before={tick:simStepCounter,state:emconExportStateB(r)};let command;if(kind==='CATEGORY')command=emconCategoryToggleB(r.entityId,value,'DIAGNOSTIC');else if(kind==='EQUIPMENT')command=emconEquipmentToggleB(r.entityId,value,'DIAGNOSTIC');else throw Error('EMCON_CORR2_BREAKOUT_KIND');
  if(value==='ECM'||emconRegistryEntryB(r,value)?.category==='ECM'){if(r===ACTIVE_SHIP_RUNTIME)updateSlq32EaAllocator(10);else prepareElectronicF(r).context.step(10);}
  return {schema:'AEGIS_EMCON_B_CORRECTION_2_BREAKOUT_1',ownerEntityId:r.entityId,profileId:r.profileId,kind,value,before,afterCommand:{tick:simStepCounter,state:emconExportStateB(r)},command,after:emconCorr2SnapshotB(r),sensors:emconCorr2SensorPassB(r)};
}
function emconCorr2BlockedB(id,equipmentId){
  const r=emconCorr2RuntimeB(id),entry=emconRegistryEntryB(r,equipmentId);if(!entry)throw Error('EMCON_CORR2_BLOCKED_EQUIPMENT');emconCorr2ForceRadiateB(r);emconGlobalCommandB(r.entityId,true,'DIAGNOSTIC');
  const offlineOriginal=shipEquipmentOfflineV1;let offline;try{shipEquipmentOfflineV1=owner=>(owner??ACTIVE_SHIP_RUNTIME)===r?true:offlineOriginal(owner);offline={decision:emconEquipmentDecisionB(r,equipmentId),command:emconEquipmentToggleB(r.entityId,equipmentId,'DIAGNOSTIC'),state:emconExportStateB(r)};}finally{shipEquipmentOfflineV1=offlineOriginal;}
  emconCorr2ForceRadiateB(r);emconGlobalCommandB(r.entityId,true,'DIAGNOSTIC');const healthOriginal=observerHealthC;let damage;try{observerHealthC=(owner,name)=>owner===r?0:healthOriginal(owner,name);damage={decision:emconEquipmentDecisionB(r,equipmentId),command:emconEquipmentToggleB(r.entityId,equipmentId,'DIAGNOSTIC'),state:emconExportStateB(r)};}finally{observerHealthC=healthOriginal;}
  return {offline,damage};
}
window.__EMCON_B_CORRECTION_2__=Object.freeze({hardSilent:emconCorr2HardSilentB,breakout:emconCorr2BreakoutB,blocked:emconCorr2BlockedB,forceRadiate:id=>emconCorr2ForceRadiateB(emconCorr2RuntimeB(id)),snapshot:id=>emconCorr2SnapshotB(emconCorr2RuntimeB(id)),link:id=>emconCorr2LinkB(emconCorr2RuntimeB(id)),connect:(a,b)=>{emconEConnectB(emconCorr2RuntimeB(a),emconCorr2RuntimeB(b));return {a:emconCorr2LinkB(emconCorr2RuntimeB(a)),b:emconCorr2LinkB(emconCorr2RuntimeB(b))};}});
