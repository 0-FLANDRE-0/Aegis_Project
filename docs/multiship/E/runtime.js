// Owner-specific defense, no world entity/identity lookup in the controller port.
function ownerVlsRegistryE(){return WIP119_VLS_WEAPON_REGISTRY;}
function defenseSnapshotE(){return {schema:'AEGIS_NAVAL_DEFENSE_E_1',ships:physicalShipsB().map(r=>({entityId:r.entityId,profileId:r.profileId,...r.weapons.executionD.context.defenseSnapshot()}))};}
function defenseCommandE(shipId,command){
  const r=ENGAGEMENT_RUNTIME.ships.get(String(shipId));if(!r||r===ACTIVE_SHIP_RUNTIME||r.executionState!=='PHYSICAL_ACTIVE')return {ok:false,reason:'PHYSICAL_NONPLAYER_REQUIRED'};
  if(!command||Object.keys(command).some(k=>k!=='mode'))return {ok:false,reason:'INVALID_DEFENSE_COMMAND'};
  return r.weapons.executionD.context.defenseMode(command.mode);
}
// DIAGNOSTIC_ONLY: explicit observation/effect fixtures never query an entity.
function defenseFixtureE(shipId,options){
  const r=ENGAGEMENT_RUNTIME.ships.get(shipId);if(!r||r===ACTIVE_SHIP_RUNTIME||!r.weapons.executionD)return {ok:false,reason:'NONPLAYER_REQUIRED'};
  if(options?.action==='effect'){
    if(Object.keys(options).some(k=>!['action','trackId','evidence','positionM','velocityMps','key'].includes(k))||!Number.isInteger(options.trackId)||!['FUZE_DETONATION','DIRECT_BREAKUP'].includes(options.evidence))return {ok:false,reason:'INVALID_EFFECT_REPORT'};
    for(const p of [options.positionM,options.velocityMps])if(p&&!['x','y','z'].every(k=>Number.isFinite(p[k])))return {ok:false,reason:'INVALID_EFFECT_REPORT'};
    const report={key:options.key??'DIAG_E:'+simStepCounter,effectStep:simStepCounter,evidence:options.evidence,source:'DIAGNOSTIC_MEASURED_EFFECT',weapon:'SM2',terminalReport:options.positionM?{positionM:{...options.positionM},velocityMps:{...options.velocityMps}}:null};
    return {ok:true,event:jsonSafeCloneV48Wip11A(r.weapons.executionD.context.effectReport(options.trackId,report))};
  }
  const tr=r.combatSystem.trackManager.tracks.get(options?.trackId);
  if(!tr||Object.keys(options).some(k=>!['action','trackId','remove','classification','classificationConfidence','sensorAge','confirmed','sensorDetected','memActive','reacquiring','measurementStep','velocityMps'].includes(k)))return {ok:false,reason:'INVALID_MEASURED_FIXTURE'};
  if(options.remove){r.combatSystem.trackManager.tracks.delete(options.trackId);return {ok:true};}
  for(const key of ['classification','classificationConfidence','sensorAge','confirmed','sensorDetected','memActive','reacquiring'])if(key in options)tr[key]=options[key];
  if(options.measurementStep!=null)tr._lastMeasurementStep=options.measurementStep;
  if(options.velocityMps){const v=options.velocityMps;tr.vx=mpsToWorldSpeed(v.x);tr.vy=mpsToWorldSpeed(v.y);tr.vz=v.z;tr._kfX.set([v.x,v.y,v.z],3);}
  return {ok:true};
}
