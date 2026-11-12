#!/usr/bin/env python3
"""Build INTEGRATION_BASELINE_A from the frozen HP_A packed product.

The product stores its canonical JavaScript as gzip+base64 in data-c55-index=13.
Every replacement below is count-checked so a changed baseline fails closed.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import re
from pathlib import Path


GLOBAL_MARKER = "// LIVE_CANONICAL. Deterministic, owner-local utility decisions over observations."

GLOBAL_CONTRACT = r"""
// INTEGRATION_BASELINE_A: immutable owner-addressed observation input and advisory-only command contract.
// This layer owns no ROE, FCS, reservation, release, navigation, attack, team, or immediate CIWS authority.
const AEGIS_DEFENSE_DECISION_INPUT_SCHEMA_A1='AEGIS_DEFENSE_DECISION_INPUT_A1';
const AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1='AEGIS_DEFENSE_DECISION_COMMAND_A1';
const AEGIS_DEFENSE_DECISION_PROVIDER_A1='LEGACY_H1';
const AEGIS_DEFENSE_DECISION_MODE_A1='ACTIVE';
const AEGIS_DEFENSE_DECISION_ALLOWED_WEAPONS_A1=Object.freeze(['SM2','SM2ER','SM6','ESSM','RAM','PHALANX']);
const AEGIS_DEFENSE_DECISION_COMMAND_KEYS_A1=Object.freeze(['schema','provider','ownerEntityId','inputStep','inputRevision','trackOrder','priorities','salvoOverrides','advisoryHold','deferUntilStep','reason']);
const AEGIS_DEFENSE_DECISION_DIAGNOSTICS_A1=new WeakMap();
function defenseDecisionDiagnosticStateA1(r){
  let q=AEGIS_DEFENSE_DECISION_DIAGNOSTICS_A1.get(r);if(q)return q;
  q={provider:AEGIS_DEFENSE_DECISION_PROVIDER_A1,mode:AEGIS_DEFENSE_DECISION_MODE_A1,builds:0,shadowComparisons:0,shadowMismatchCount:0,firstMismatch:null,validationFailures:0,firstValidationFailure:null,rngMismatchCount:0,truthAuditFailures:0,lastInput:null,lastCommand:null,lastValidation:null,lastStep:-1};
  AEGIS_DEFENSE_DECISION_DIAGNOSTICS_A1.set(r,q);return q;
}
function defenseDecisionRngStampA1(r){
  const o=r?.combatSystem?.observerC,e=r?.weapons?.executionD;
  return JSON.stringify({global:typeof SIM_RNG_STATE==='number'?SIM_RNG_STATE>>>0:null,observer:o?.rng??null,weapon:e?.weaponRng??null});
}
function defenseDecisionForbiddenPathA1(value,path='$',seen=new WeakSet()){
  if(!value||typeof value!=='object'||seen.has(value))return null;seen.add(value);
  for(const [key,child] of Object.entries(value)){
    const next=path+'.'+key;
    if(/(^|_)(truth|truthobject|truthid|renderer|threejs|actualenemy|actualtarget|hostiletruth|faction)(_|$)/i.test(key))return next;
    const nested=defenseDecisionForbiddenPathA1(child,next,seen);if(nested)return nested;
  }return null;
}
function defenseDecisionFrozenA1(value,seen=new WeakSet()){
  if(!value||typeof value!=='object'||seen.has(value))return true;seen.add(value);
  if(!Object.isFrozen(value))return false;return Object.values(value).every(q=>defenseDecisionFrozenA1(q,seen));
}
function defenseDecisionValidateCommandA1(r,input,command,currentStep=simStepCounter){
  const bad=reason=>({ok:false,reason,ownerEntityId:r?.entityId??null,inputStep:input?.step??null});
  if(!r||!input||input.schema!==AEGIS_DEFENSE_DECISION_INPUT_SCHEMA_A1)return bad('INPUT_SCHEMA');
  if(!command||typeof command!=='object'||Array.isArray(command))return bad('COMMAND_OBJECT');
  const keys=Object.keys(command);if(keys.length!==AEGIS_DEFENSE_DECISION_COMMAND_KEYS_A1.length||keys.some(k=>!AEGIS_DEFENSE_DECISION_COMMAND_KEYS_A1.includes(k)))return bad('COMMAND_FIELDS');
  if(command.schema!==AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1||command.provider!==AEGIS_DEFENSE_DECISION_PROVIDER_A1)return bad('COMMAND_SCHEMA');
  if(command.ownerEntityId!==r.entityId||command.ownerEntityId!==input.ownerEntityId)return bad('OWNER_MISMATCH');
  if(!Number.isInteger(command.inputStep)||command.inputStep!==input.step||command.inputStep!==currentStep)return bad('STALE_STEP');
  if(!Number.isInteger(command.inputRevision)||command.inputRevision!==input.revision)return bad('STALE_REVISION');
  if(typeof command.advisoryHold!=='boolean'||command.deferUntilStep!==null&&(!Number.isInteger(command.deferUntilStep)||command.deferUntilStep<command.inputStep))return bad('HOLD_FIELDS');
  if(typeof command.reason!=='string'||command.reason.length<1||command.reason.length>96)return bad('REASON');
  const ids=new Set(input.tracks.map(q=>q.trackId)),order=new Set();
  if(!Array.isArray(command.trackOrder)||command.trackOrder.length>ids.size)return bad('TRACK_ORDER');
  for(const id of command.trackOrder){if(!Number.isInteger(id)||!ids.has(id)||order.has(id))return bad('TRACK_ORDER_ID');order.add(id);}
  const priorityIds=new Set();if(!Array.isArray(command.priorities)||command.priorities.length>ids.size)return bad('PRIORITIES');
  for(const q of command.priorities){if(!q||Object.keys(q).length!==2||!Object.hasOwn(q,'trackId')||!Object.hasOwn(q,'score')||!Number.isInteger(q.trackId)||!ids.has(q.trackId)||priorityIds.has(q.trackId)||!Number.isFinite(q.score))return bad('PRIORITY_ROW');priorityIds.add(q.trackId);}
  const salvoKeys=new Set();if(!Array.isArray(command.salvoOverrides)||command.salvoOverrides.length>ids.size*AEGIS_DEFENSE_DECISION_ALLOWED_WEAPONS_A1.length)return bad('SALVO_OVERRIDES');
  for(const q of command.salvoOverrides){const qKeys=q&&Object.keys(q);if(!q||qKeys.length!==4||!['trackId','weapon','desiredSalvo','reason'].every(k=>Object.hasOwn(q,k))||!Number.isInteger(q.trackId)||!ids.has(q.trackId)||!AEGIS_DEFENSE_DECISION_ALLOWED_WEAPONS_A1.includes(q.weapon)||!Number.isInteger(q.desiredSalvo)||q.desiredSalvo<0||q.desiredSalvo>4||typeof q.reason!=='string')return bad('SALVO_ROW');const key=q.trackId+':'+q.weapon;if(salvoKeys.has(key))return bad('SALVO_DUPLICATE');salvoKeys.add(key);}
  const forbidden=defenseDecisionForbiddenPathA1(command);if(forbidden)return bad('COMMAND_FORBIDDEN_FIELD:'+forbidden);
  if(!defenseDecisionFrozenA1(command))return bad('COMMAND_MUTABLE');
  return {ok:true,reason:null,ownerEntityId:r.entityId,inputStep:input.step,inputRevision:input.revision};
}
function defenseDecisionMismatchA1(state,path,direct,provider){
  state.shadowComparisons++;if(JSON.stringify(direct)===JSON.stringify(provider))return;
  state.shadowMismatchCount++;state.firstMismatch??={step:simStepCounter,path,direct:jsonSafeCloneV48Wip11A(direct),provider:jsonSafeCloneV48Wip11A(provider)};
}
function defenseDecisionValidationA1(state,result){
  state.lastValidation={...result};if(result.ok)return true;state.validationFailures++;state.firstValidationFailure??={step:simStepCounter,...result};return false;
}
function defenseDecisionDiagnosticsViewA1(r){
  const q=AEGIS_DEFENSE_DECISION_DIAGNOSTICS_A1.get(r);return q?{provider:q.provider,mode:q.mode,builds:q.builds,shadowComparisons:q.shadowComparisons,shadowMismatchCount:q.shadowMismatchCount,firstMismatch:q.firstMismatch?jsonSafeCloneV48Wip11A(q.firstMismatch):null,validationFailures:q.validationFailures,firstValidationFailure:q.firstValidationFailure?{...q.firstValidationFailure}:null,rngMismatchCount:q.rngMismatchCount,truthAuditFailures:q.truthAuditFailures,lastStep:q.lastStep,lastInput:q.lastInput,lastCommand:q.lastCommand,lastValidation:q.lastValidation?{...q.lastValidation}:null}:{provider:AEGIS_DEFENSE_DECISION_PROVIDER_A1,mode:AEGIS_DEFENSE_DECISION_MODE_A1,builds:0,shadowComparisons:0,shadowMismatchCount:0,firstMismatch:null,validationFailures:0,firstValidationFailure:null,rngMismatchCount:0,truthAuditFailures:0,lastStep:-1,lastInput:null,lastCommand:null,lastValidation:null};
}
"""


LOCAL_ADAPTER = r"""
// INTEGRATION_BASELINE_A owner-local read-only input builder and LEGACY_H1 advisory adapter.
function defenseDecisionCrewInputA1(r){
  const source=getShipCrewV21(r)?.snapshot?.()??null,finite=value=>Number.isFinite(value)?value:null,department=role=>{
    const row=Array.isArray(source?.departments)?source.departments.find(q=>q?.role===role):null;
    return {duty:finite(row?.duty),fit:finite(row?.fit),availability:finite(row?.availability)};
  };
  return {mode:typeof source?.mode==='string'?source.mode:null,combatUnavailable:typeof source?.combatUnavailable==='boolean'?source.combatUnavailable:null,
    totals:{total:finite(source?.total),fit:finite(source?.fit),injured:finite(source?.injured),dead:finite(source?.dead),evacuated:finite(source?.evacuated)},
    departments:{COMBAT:department('COMBAT'),OPERATIONS:department('OPERATIONS')}};
}
function defenseDecisionTrackInputA1(id,tr,assessment,network,nowS){
  const live=!!tr,observed=live?wip118TrackStateSI(tr):assessment?.lastObservation?.si??null,cov=live&&tr?._kfP&&tr._kfP.length===36?Array.from(tr._kfP):null,
    last=assessment?.lastObservation??null,lastStep=live&&Number.isFinite(Number(tr._lastMeasurementStep))?Number(tr._lastMeasurementStep):Number.isFinite(Number(last?.lastObservedStep))?Number(last.lastObservedStep):null,
    ageS=lastStep==null?null:Math.max(0,(simStepCounter-lastStep)*SIM_FIXED_DT),lease=network?.leases?.get(id)??null,
    file=network?.files?[...network.files.values()].find(q=>q.localTrackId===id)??null:null,
    sources=file?[...file.sources.values()].map(q=>({origin:q.senderId===ACTIVE_SHIP_RUNTIME.entityId?'LOCAL':'REMOTE',senderEntityId:q.senderId??null,fileId:q.fileId??null,kind:q.kind??null,measuredAtS:Number.isFinite(q.measuredAtS)?q.measuredAtS:null,ageS:Number.isFinite(q.measuredAtS)?Math.max(0,nowS-q.measuredAtS):null,assessment:q.assessment??null})):[],
    existing=hardKillExistingEngagementCounts(id);
  return {trackId:id,trackNumber:tr?.trackNumber??last?.trackNumber??id,measurement:{positionM:observed?{x:observed.x,y:observed.y,z:observed.z}:null,velocityMps:observed?{x:observed.vx,y:observed.vy,z:observed.vz}:null,covariance:cov,measuredAtStep:lastStep,measuredAtS:lastStep==null?null:lastStep*SIM_FIXED_DT,ageS,sensorSource:tr?.sensorSource??last?.sensorSource??null},
    lifecycle:{confirmed:tr?.confirmed??assessment?.state==='LOST',sensorDetected:tr?.sensorDetected??false,coasting:assessment?.state==='LOST'||tr?.lastUpdateSeen===false,reacquiring:!!tr?.reacquiring,memory:!!tr?.memActive,assessmentState:assessment?.state??tr?.threatStatus??'UNASSESSED',lostAgeS:Number.isFinite(assessment?.lostAgeS)?assessment.lostAgeS:null},
    identification:{classification:tr?.classification??last?.classification??'UNKNOWN',identity:tr?.identity??last?.trackMetadata?.identity??'UNKNOWN',threatStatus:tr?.threatStatus??last?.trackMetadata?.threatStatus??assessment?.state??'UNASSESSED',engagementAuthority:tr?.engagementAuthority??last?.trackMetadata?.engagementAuthority??'WITHHELD'},
    assessment:assessment?{state:assessment.state??null,cpaM:Number.isFinite(assessment.cpaM)?assessment.cpaM:null,cpaTimeS:Number.isFinite(assessment.cpaTimeS)?assessment.cpaTimeS:null,closureTgoS:Number.isFinite(assessment.closureTgoS)?assessment.closureTgoS:null,liveEngagement:Number(assessment.liveEngagement)||0,reengageRequired:!!assessment.reengageRequired,trackPresent:!!assessment.trackPresent,coastFireControlUsable:!!assessment.coastFireControlUsable}:null,
    engagements:{sm2:Number(existing.sm2)||0,sm2er:Number(existing.sm2er)||0,sm6:Number(existing.sm6)||0,essm:Number(existing.essm)||0,ram:Number(existing.ram)||0,phalanx:Number(existing.phalanx)||0},
    network:{assignment:lease?{primaryEntityId:lease.primary??null,issuerEntityId:lease.issuer??null,untilS:Number.isFinite(lease.untilS)?lease.untilS:null,localOwner:lease.primary===ACTIVE_SHIP_RUNTIME.entityId}:null,sources,fcsSource:'LOCAL_ONLY'}};
}
function defenseDecisionInputSnapshotA1(){
  const r=ACTIVE_SHIP_RUNTIME,nowS=simStepCounter*SIM_FIXED_DT,network=r.combatSystem.networkG??null,damage=getShipDamageEffects(),counts=getVlsCounts(),available=wip14a14DecisionInventory(counts),tactical=r.combatSystem.tacticalH1,ids=new Set([...tracks.keys(),...wip118ControlState.assessments.keys()]),rows=[];
  for(const id of [...ids].sort((a,b)=>a-b))rows.push(defenseDecisionTrackInputA1(id,tracks.get(id)??null,wip118ControlState.assessments.get(id)??null,network,nowS));
  const ew=r.ew?.executionF,esmCues=ew?[...ew.contacts.values()].filter(q=>q.emitterClass==='ACTIVE_SEEKER').map(q=>({contactId:q.id??q.contactId??null,emitterClass:q.emitterClass,band:q.band??null,bearingRad:Number.isFinite(q.bearingRad)?q.bearingRad:null,bearingSigmaRad:Number.isFinite(q.bearingSigmaRad)?q.bearingSigmaRad:null,quality:Number.isFinite(q.quality)?q.quality:null,measuredAtS:Number.isFinite(q.measuredAtS)?q.measuredAtS:null,ageS:Number.isFinite(q.measuredAtS)?Math.max(0,nowS-q.measuredAtS):null,source:q.source??'OWNER_ESM'})):[];
  const outcome=shipOutcomeA(r),crew=defenseDecisionCrewInputA1(r),input={schema:AEGIS_DEFENSE_DECISION_INPUT_SCHEMA_A1,ownerEntityId:r.entityId,profileId:r.profileId,step:simStepCounter,simulationTimeS:nowS,revision:wip118ControlState.revision,mode:engagementControlMode,tracks:rows,
    inventory:{installed:{sm2:Number(counts.sm2Total)||0,sm2er:Number(counts.sm2erTotal)||0,sm6:Number(counts.sm6Total)||0,essm:Number(counts.essmTotal)||0,ram:Number(ciws.find(q=>q.type==='RAM')?.ammo)||0,phalanx:Number(ciws.find(q=>q.type==='GUN')?.ammo)||0},afterReserve:{sm2:available.sm2,sm2er:available.sm2er,sm6:available.sm6,essm:available.essm,ram:available.ram}},
    support:{channels:SPG62_ILLUMINATORS.map(q=>({id:q.id,moduleName:q.moduleName,health01:observerHealthC(r,q.moduleName),assignedTrackId:[...SPG62_ENGAGEMENT_STATE].find(([,v])=>v.illId===q.id)?.[0]??null,reservationCount:(SPG62_RESERVATIONS.get(q.id)??[]).length})),activeAssignments:SPG62_ENGAGEMENT_STATE.size,plannedReservations:SPG62_RESERVATION_STATE.size},
    ship:{equipmentOffline:shipEquipmentOfflineV1(r),missionState:outcome.missionState,afloatState:outcome.afloatState,displayHp:outcome.displayHp,crew,damage:{combatEff:damage.combatEff??0,radarPowerFac:damage.radarPowerFac??0,ciwsPowerFac:damage.ciwsPowerFac??0,vlsPowerFac:damage.vlsPowerFac??0,steerFac:damage.steerFac??0,propulsionFac:damage.propulsionFac??0,maxSpeedKt:damage.maxSpeedKt??0}},
    network:{enabled:!!network?.settings?.enabled,shareTracks:!!network?.settings?.shareTracks,cooperativeDefense:!!network?.settings?.cooperativeDefense,remoteFireControl:false},esmCues,
    operatorOverrides:{tacticalEnabled:!!tactical?.settings?.enabled,manualRadar:!!tactical?.settings?.manualRadar,manualEw:!!tactical?.settings?.manualEw,emcon:!!emconActive}};
  return deepFreezeShipProfileV48Wip09(input);
}
function defenseDecisionLegacyCommandA1(input,rows){
  const ordered=tacticalOrderH1(ACTIVE_SHIP_RUNTIME,rows),active=tacticalActiveH1(ACTIVE_SHIP_RUNTIME),priorities=rows.map(q=>({trackId:q.id,score:active?tacticalPriorityH1(ACTIVE_SHIP_RUNTIME,q.id):0}));
  return deepFreezeShipProfileV48Wip09({schema:AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1,provider:AEGIS_DEFENSE_DECISION_PROVIDER_A1,ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,inputStep:input.step,inputRevision:input.revision,trackOrder:ordered.map(q=>q.id),priorities,salvoOverrides:[],advisoryHold:false,deferUntilStep:null,reason:'LEGACY_H1_EXACT'});
}
function defenseDecisionLegacyBeginA1(rows){
  const state=defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME),rngBefore=defenseDecisionRngStampA1(ACTIVE_SHIP_RUNTIME),input=defenseDecisionInputSnapshotA1(),direct=tacticalOrderH1(ACTIVE_SHIP_RUNTIME,rows).map(q=>q.id),command=defenseDecisionLegacyCommandA1(input,rows),validation=defenseDecisionValidateCommandA1(ACTIVE_SHIP_RUNTIME,input,command);
  defenseDecisionMismatchA1(state,'trackOrder',direct,command.trackOrder);defenseDecisionValidationA1(state,validation);
  const rngAfter=defenseDecisionRngStampA1(ACTIVE_SHIP_RUNTIME);if(rngBefore!==rngAfter)state.rngMismatchCount++;
  const forbidden=defenseDecisionForbiddenPathA1(input);if(forbidden)state.truthAuditFailures++;
  const byId=new Map(rows.map(q=>[q.id,q])),orderedRows=validation.ok?command.trackOrder.map(id=>byId.get(id)).filter(Boolean):[];
  state.builds++;state.lastStep=simStepCounter;state.lastInput=input;state.lastCommand=command;
  return {input,command,validation,orderedRows,priority:new Map(command.priorities.map(q=>[q.trackId,q.score])),salvoOverrides:[]};
}
function defenseDecisionLegacySalvoA1(session,th,weapon,native){
  const state=defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME),rngBefore=defenseDecisionRngStampA1(ACTIVE_SHIP_RUNTIME),direct=tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,native),provider=tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,native);
  defenseDecisionMismatchA1(state,'salvo:'+th.id+':'+weapon,direct,provider);
  const row={trackId:th.id,weapon,desiredSalvo:provider.salvo,reason:provider.policy??'LEGACY_H1'},overrides=[...session.salvoOverrides,row],command=deepFreezeShipProfileV48Wip09({...session.command,salvoOverrides:overrides}),validation=defenseDecisionValidateCommandA1(ACTIVE_SHIP_RUNTIME,session.input,command);
  if(defenseDecisionValidationA1(state,validation)){session.salvoOverrides=overrides;session.command=command;state.lastCommand=command;}
  const rngAfter=defenseDecisionRngStampA1(ACTIVE_SHIP_RUNTIME);if(rngBefore!==rngAfter)state.rngMismatchCount++;
  return validation.ok?provider:native;
}
function defenseDecisionRecommendationOrderA1(session,a,b){
  const direct=tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b),provider=tacticalActiveH1(ACTIVE_SHIP_RUNTIME)?(session.priority.get(b.trackId)??0)-(session.priority.get(a.trackId)??0):0;
  defenseDecisionMismatchA1(defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME),'recommendationOrder',direct,provider);return session.validation.ok?provider:0;
}
function defenseDecisionLegacyFinishA1(session,recommendations){
  const state=defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME);state.lastCommand=session.command;state.lastValidation={...session.validation};
  defenseDecisionMismatchA1(state,'finalRecommendationOrder',recommendations.map(q=>q.trackId),[...recommendations].sort((a,b)=>(b.assessment==='THREAT')-(a.assessment==='THREAT')||tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b)||(b.threatScore??0)-(a.threatScore??0)).map(q=>q.trackId));
  return session.command;
}
function wip118SalvoPolicy(th,weapon,assessment,plan,decision=null){const native=wip118SalvoPolicyNativeH1(th,weapon,assessment,plan);return decision?defenseDecisionLegacySalvoA1(decision,th,weapon,native):tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,native);}
"""


PUBLIC_API = r"""

// INTEGRATION_BASELINE_A read-only reusable diagnostic surface. No automatic execution or truth oracle.
function defenseDecisionOwnerA1(id){return id==null?ACTIVE_SHIP_RUNTIME:ENGAGEMENT_RUNTIME.ships.get(String(id))??null;}
function defenseDecisionInputForOwnerA1(id){const r=defenseDecisionOwnerA1(id);if(!r)return null;return r===ACTIVE_SHIP_RUNTIME?defenseDecisionInputSnapshotA1():r.weapons.executionD?.context?.defenseDecisionInputA1?.()??null;}
function defenseDecisionDiagnosticsForOwnerA1(id){const r=defenseDecisionOwnerA1(id);return r?defenseDecisionDiagnosticsViewA1(r):null;}
window.__DEFENSE_DECISION_A1__=Object.freeze({schema:AEGIS_DEFENSE_DECISION_INPUT_SCHEMA_A1,commandSchema:AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1,provider:AEGIS_DEFENSE_DECISION_PROVIDER_A1,mode:AEGIS_DEFENSE_DECISION_MODE_A1,authority:'ADVISORY_ONLY',truthUsed:false,rngConsumed:false,saveFields:0,
  input:defenseDecisionInputForOwnerA1,diagnostics:defenseDecisionDiagnosticsForOwnerA1,ships:()=>[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>({ownerEntityId:r.entityId,profileId:r.profileId,input:defenseDecisionInputForOwnerA1(r.entityId),diagnostics:defenseDecisionDiagnosticsForOwnerA1(r.entityId)})),
  validate:(id,command)=>{const r=defenseDecisionOwnerA1(id),input=r?defenseDecisionInputForOwnerA1(r.entityId):null;return defenseDecisionValidateCommandA1(r,input,command);},
  audit:(id)=>{const r=defenseDecisionOwnerA1(id),input=r?defenseDecisionInputForOwnerA1(r.entityId):null,diag=r?defenseDecisionDiagnosticsViewA1(r):null;return {ownerEntityId:r?.entityId??null,inputFrozen:!!input&&defenseDecisionFrozenA1(input),forbiddenPath:input?defenseDecisionForbiddenPathA1(input):'NO_INPUT',shadowMismatchCount:diag?.shadowMismatchCount??null,rngMismatchCount:diag?.rngMismatchCount??null,validationFailures:diag?.validationFailures??null,portOwnsSafety:false,portOwnsExecution:false,portOwnsImmediateCiws:false};}});
"""


def replace_count(text: str, old: str, new: str, count: int, label: str) -> str:
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"{label}: expected {count} occurrences, found {actual}")
    return text.replace(old, new)


def extract(raw: bytes) -> tuple[bytes, re.Match[bytes]]:
    match = re.search(rb'(data-c55-index="13">)([^<]+)', raw)
    if not match:
        raise SystemExit("packed main data-c55-index=13 not found")
    return gzip.decompress(base64.b64decode(match.group(2))), match


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--js-output", type=Path)
    args = parser.parse_args()
    raw = args.baseline.read_bytes()
    js_raw, packed = extract(raw)
    text = js_raw.decode("utf-8")

    text = replace_count(text, GLOBAL_MARKER, GLOBAL_CONTRACT + "\n" + GLOBAL_MARKER, 1, "global contract marker")
    old_salvo = "function wip118SalvoPolicy(th,weapon,assessment,plan){return tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,wip118SalvoPolicyNativeH1(th,weapon,assessment,plan));}"
    text = replace_count(text, old_salvo, LOCAL_ADAPTER.strip(), 2, "owner-local H1 adapter")
    old_begin = "const started=performance.now();wip118UpdateKillAssessment(!!opts.force);const counts=getVlsCounts(),inventory=wip14a14DecisionInventory(counts),ctx={provisionalReservations:[]},recs=[];tacticalEvaluateH1(ACTIVE_SHIP_RUNTIME,wip118ControlState,inventory,getShipDamageEffects());\n    for(const th of tacticalOrderH1(ACTIVE_SHIP_RUNTIME,wip118ThreatRows())){"
    new_begin = "const started=performance.now();wip118UpdateKillAssessment(!!opts.force);const counts=getVlsCounts(),inventory=wip14a14DecisionInventory(counts),ctx={provisionalReservations:[]},recs=[];tacticalEvaluateH1(ACTIVE_SHIP_RUNTIME,wip118ControlState,inventory,getShipDamageEffects());\n    const decision=defenseDecisionLegacyBeginA1(wip118ThreatRows());\n    for(const th of decision.orderedRows){"
    text = replace_count(text, old_begin, new_begin, 2, "provider begin")
    text = replace_count(text, "const sal=wip118SalvoPolicy(th,weapon,assessment,plan),existing=", "const sal=wip118SalvoPolicy(th,weapon,assessment,plan,decision),existing=", 2, "provider salvo consume")
    old_sort = "recs.sort((a,b)=>(b.assessment==='THREAT')-(a.assessment==='THREAT')||tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b)||(b.threatScore??0)-(a.threatScore??0));"
    new_sort = "recs.sort((a,b)=>(b.assessment==='THREAT')-(a.assessment==='THREAT')||defenseDecisionRecommendationOrderA1(decision,a,b)||(b.threatScore??0)-(a.threatScore??0));"
    text = replace_count(text, old_sort, new_sort, 2, "provider recommendation sort")
    text = replace_count(text, "if(opts.commit!==false){wip118ControlState.recommendations=recs;", "defenseDecisionLegacyFinishA1(decision,recs);if(opts.commit!==false){wip118ControlState.recommendations=recs;", 2, "provider finish")
    foreign_return = "return {localDefenseGuardProbeH4A,localDefenseCuesH4A:defenseLocalCuesH4A,attackPreviewH3:"
    foreign_new = "return {defenseDecisionInputA1:defenseDecisionInputSnapshotA1,defenseDecisionDiagnosticsA1:()=>defenseDecisionDiagnosticsViewA1(ACTIVE_SHIP_RUNTIME),localDefenseGuardProbeH4A,localDefenseCuesH4A:defenseLocalCuesH4A,attackPreviewH3:"
    text = replace_count(text, foreign_return, foreign_new, 1, "foreign context diagnostic bridge")
    api_marker = "  window.__NAVAL_SIM_DIAG__ = {"
    text = replace_count(text, api_marker, PUBLIC_API + "\n" + api_marker, 1, "public API marker")

    candidate = text.encode("utf-8")
    if args.js_output:
        args.js_output.write_bytes(candidate)
    blob = base64.b64encode(gzip.compress(candidate, compresslevel=9, mtime=0))
    out = raw[: packed.start(2)] + blob + raw[packed.end(2) :]
    args.output.write_bytes(out)
    print(f"baseline_js_sha256={hashlib.sha256(js_raw).hexdigest()}")
    print(f"candidate_js_sha256={hashlib.sha256(candidate).hexdigest()}")
    print(f"candidate_html_bytes={len(out)}")
    print(f"candidate_html_sha256={hashlib.sha256(out).hexdigest()}")


if __name__ == "__main__":
    main()
