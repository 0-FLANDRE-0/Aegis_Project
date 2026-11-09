/* HP_A: one-way ship outcome projection. No damage, survival or RNG ownership. */
const HP_OUTCOME_SCHEMA_A='AEGIS_SHIP_OUTCOME_A_1';
const HP_OUTCOME_PROVENANCE_A=Object.freeze({
  physicalSurvival:'createShipSurvivalV1.snapshot',
  damageSeverity:'computeShipStatus.overall (exact compatibility alias)',
  mission:'shipEquipmentOfflineV1 + existing crew.combatUnavailable gate',
  displayHp:'ONE_WAY_DERIVED_PROJECTION_MIN_ONE_WHILE_REVERSIBLE'
});
const hpOutcomeEventStateA=new WeakMap(),hpOutcomeRestoreAuditA=[];

function shipOutcomeFromInputsA(survival,status,crew,equipmentOffline){
  const damageSeverityPct=clamp(Number(status?.damageSeverityPct??status?.overall??0),0,100),irreversible=!!survival?.irreversible,lost=!!survival?.lost;
  const missionState=(irreversible||lost)?'LOST':(equipmentOffline||crew?.combatUnavailable)?'MISSION_KILL':(damageSeverityPct>0||survival?.state!=='NORMAL')?'DEGRADED':'OPERATIONAL';
  return Object.freeze({
    schema:HP_OUTCOME_SCHEMA_A,
    displayHp:(irreversible||lost)?0:clamp(100-damageSeverityPct,1,100),
    damageSeverityPct,
    survivalState:String(survival?.state??'NORMAL'),
    afloatState:lost?'LOST':irreversible?'IRREVERSIBLE_LOSS':'AFLOAT',
    missionState,
    irreversible,
    lost,
    equipmentOffline:!!equipmentOffline,
    provenance:HP_OUTCOME_PROVENANCE_A
  });
}

function shipOutcomeA(runtime=ACTIVE_SHIP_RUNTIME){
  const survival=shipSurvivalB(runtime).snapshot(),status=computeShipStatus(runtime),crew=runtime===ACTIVE_SHIP_RUNTIME?getShipCrewV21().snapshot():runtime.crew.snapshot();
  return shipOutcomeFromInputsA(survival,status,crew,shipEquipmentOfflineV1(runtime));
}

function shipOutcomeEventRecordA(runtime,outcome,reason,emit){
  let record=hpOutcomeEventStateA.get(runtime);
  if(!record){record={previous:null,counts:{missionKill:0,irreversibleLoss:0,sunk:0},events:[]};hpOutcomeEventStateA.set(runtime,record);}
  const previous=record.previous;
  if(emit&&previous){
    if(previous.missionState!=='MISSION_KILL'&&outcome.missionState==='MISSION_KILL'){record.counts.missionKill++;record.events.push({kind:'MISSION_KILL',step:simStepCounter,reason});}
    if(!previous.irreversible&&outcome.irreversible){record.counts.irreversibleLoss++;record.events.push({kind:'IRREVERSIBLE_LOSS',step:simStepCounter,reason});}
    if(!previous.lost&&outcome.lost){record.counts.sunk++;record.events.push({kind:'SUNK',step:simStepCounter,reason});}
    if(record.events.length>32)record.events.splice(0,record.events.length-32);
  }
  record.previous=outcome;
  return record;
}

function shipOutcomeWriteDisplayA(runtime,outcome){
  if(runtime===ACTIVE_SHIP_RUNTIME)shipHP=outcome.displayHp;
  else {if(!runtime.health)runtime.health={};runtime.health.shipHP=outcome.displayHp;}
  return outcome;
}

function shipOutcomeProjectA(runtime=ACTIVE_SHIP_RUNTIME,reason='PROJECTION'){
  const outcome=shipOutcomeA(runtime);shipOutcomeEventRecordA(runtime,outcome,reason,true);return shipOutcomeWriteDisplayA(runtime,outcome);
}

function shipOutcomeResetA(runtime=ACTIVE_SHIP_RUNTIME,reason='RESET'){
  const outcome=shipOutcomeA(runtime),record={previous:outcome,counts:{missionKill:0,irreversibleLoss:0,sunk:0},events:[{kind:'BASELINE',step:simStepCounter,reason}]};
  hpOutcomeEventStateA.set(runtime,record);return shipOutcomeWriteDisplayA(runtime,outcome);
}

function shipOutcomeRestoreCompatibilityA(runtime,savedHp,reason){
  const outcome=shipOutcomeResetA(runtime,reason),audit={entityId:runtime.entityId,savedHp:Number(savedHp),derivedHp:outcome.displayHp,mismatch:Math.abs(Number(savedHp)-outcome.displayHp)>1e-9,reason,step:simStepCounter};
  hpOutcomeRestoreAuditA.push(audit);if(hpOutcomeRestoreAuditA.length>32)hpOutcomeRestoreAuditA.shift();return outcome;
}

function shipOutcomeEventsA(runtime=ACTIVE_SHIP_RUNTIME){
  const q=hpOutcomeEventStateA.get(runtime);return q?{counts:{...q.counts},events:q.events.map(e=>({...e}))}:{counts:{missionKill:0,irreversibleLoss:0,sunk:0},events:[]};
}

function shipOutcomeMissionLabelA(state){return ({OPERATIONAL:'작전 가능',DEGRADED:'성능 저하',MISSION_KILL:'임무 불능',LOST:'함선 상실'})[state]??state;}

function shipOutcomeSelfTestA(){
  const normal={state:'NORMAL',irreversible:false,lost:false},critical={state:'CRITICAL',irreversible:false,lost:false},lost={state:'LOST',irreversible:true,lost:true};
  const rows={
    normal:shipOutcomeFromInputsA(normal,{overall:0},{combatUnavailable:false},false),
    falseZeroGuard:shipOutcomeFromInputsA(critical,{overall:100},{combatUnavailable:false},false),
    missionKill:shipOutcomeFromInputsA(critical,{overall:72},{combatUnavailable:true},false),
    irreversible:shipOutcomeFromInputsA({...critical,irreversible:true},{overall:25},{combatUnavailable:false},true),
    lost:shipOutcomeFromInputsA(lost,{overall:0},{combatUnavailable:false},true)
  };
  const checks={
    normal:rows.normal.displayHp===100&&rows.normal.missionState==='OPERATIONAL',
    reversibleNeverZero:rows.falseZeroGuard.displayHp===1&&!rows.falseZeroGuard.irreversible,
    missionSeparated:rows.missionKill.displayHp>0&&rows.missionKill.missionState==='MISSION_KILL'&&!rows.missionKill.irreversible,
    irreversibleZero:rows.irreversible.displayHp===0&&rows.irreversible.missionState==='LOST',
    lostZero:rows.lost.displayHp===0&&rows.lost.lost,
    exactAlias:rows.falseZeroGuard.damageSeverityPct===100
  };
  return {schema:'AEGIS_HP_A_SELFTEST_1',pass:Object.values(checks).every(Boolean),checks,rows};
}

window.__HP_A__=Object.freeze({
  schema:HP_OUTCOME_SCHEMA_A,
  snapshot:()=>shipOutcomeA(ACTIVE_SHIP_RUNTIME),
  runtimeSnapshot:id=>{const r=ENGAGEMENT_RUNTIME.ships.get(id);return r?shipOutcomeA(r):null;},
  events:()=>shipOutcomeEventsA(ACTIVE_SHIP_RUNTIME),
  runtimeEvents:id=>{const r=ENGAGEMENT_RUNTIME.ships.get(id);return r?shipOutcomeEventsA(r):null;},
  project:reason=>shipOutcomeProjectA(ACTIVE_SHIP_RUNTIME,String(reason??'DIAGNOSTIC_PROJECTION')),
  restoreAudit:()=>hpOutcomeRestoreAuditA.map(q=>({...q})),
  selfTest:shipOutcomeSelfTestA
});
