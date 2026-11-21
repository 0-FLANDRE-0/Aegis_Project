#!/usr/bin/env python3
"""Deterministically build DEFENSE_OODA_A from INTEGRATION_BASELINE_A.

The canonical product JavaScript is gzip+base64 at data-c55-index=13. Every
mutation is count checked and gzip mtime is fixed at zero.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNTIME_MARKER = "// INTEGRATION_BASELINE_A: immutable owner-addressed observation input and advisory-only command contract."


def replace_count(text: str, old: str, new: str, count: int, label: str) -> str:
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"{label}: expected {count} occurrences, found {actual}")
    return text.replace(old, new)


def regex_replace(text: str, pattern: str, replacement: str, count: int, label: str) -> str:
    out, actual = re.subn(pattern, replacement, text, flags=re.S)
    if actual != count:
        raise SystemExit(f"{label}: expected {count} occurrences, found {actual}")
    return out


def extract(raw: bytes) -> tuple[bytes, re.Match[bytes]]:
    match = re.search(rb'(data-c55-index="13">)([^<]+)', raw)
    if not match:
        raise SystemExit("packed main data-c55-index=13 not found")
    return gzip.decompress(base64.b64decode(match.group(2))), match


LEGACY_COMMAND = r"""function defenseDecisionLegacyCommandA1(input,rows){
  const ordered=tacticalOrderH1(ACTIVE_SHIP_RUNTIME,rows),active=tacticalActiveH1(ACTIVE_SHIP_RUNTIME),priorities=rows.map(q=>({trackId:q.id,score:active?tacticalPriorityH1(ACTIVE_SHIP_RUNTIME,q.id):0}));
  return deepFreezeShipProfileV48Wip09({schema:AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1,provider:'LEGACY_H1',ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,inputStep:input.step,inputRevision:input.revision,trackOrder:ordered.map(q=>q.id),priorities,salvoOverrides:[],advisoryHold:false,deferUntilStep:null,reason:'LEGACY_H1_EXACT'});
}"""


ADAPTER = r"""
function defenseDecisionShadowCompareA(state,path,legacy,ooda,allowed=true){
  state.shadowComparisons++;if(JSON.stringify(legacy)===JSON.stringify(ooda))return;
  if(allowed){state.allowedShadowDifferenceCount=(state.allowedShadowDifferenceCount??0)+1;state.firstAllowedShadowDifference??={step:simStepCounter,path,legacy:jsonSafeCloneV48Wip11A(legacy),ooda:jsonSafeCloneV48Wip11A(ooda)};return;}
  state.shadowMismatchCount++;state.firstMismatch??={step:simStepCounter,path,direct:jsonSafeCloneV48Wip11A(legacy),provider:jsonSafeCloneV48Wip11A(ooda)};
}
function defenseDecisionAppendSalvoA(command,row){return deepFreezeShipProfileV48Wip09({...command,salvoOverrides:[...command.salvoOverrides,row]});}
function defenseDecisionLegacyBeginA1(rows){
  const r=ACTIVE_SHIP_RUNTIME,state=defenseDecisionDiagnosticStateA1(r),rngBefore=defenseDecisionRngStampA1(r),input=defenseDecisionInputSnapshotA1(),legacy=defenseDecisionLegacyCommandA1(input,rows),legacyValidation=defenseDecisionValidateCommandA1(r,input,legacy),ooda=DEFENSE_OODA_IMPLEMENTATION_MODE_A==='OFF'?null:defenseOodaCommandA(r,input),oodaValidation=ooda?defenseDecisionValidateCommandA1(r,input,ooda):{ok:false,reason:'OODA_DISABLED'};
  if(ooda&&!oodaValidation.ok){const rejected=defenseOodaEnsureStateA(r);if(rejected)rejected.diagnostics.rejected++;}
  if(ooda)defenseDecisionShadowCompareA(state,'trackOrder',legacy.trackOrder,ooda.trackOrder,true);
  let command=legacy,validation=legacyValidation,usedFallback=false;
  if(DEFENSE_OODA_IMPLEMENTATION_MODE_A==='ACTIVE'){if(oodaValidation.ok){command=ooda;validation=oodaValidation;}else{usedFallback=true;const s=defenseOodaEnsureStateA(r);if(s)s.diagnostics.fallback++;}}
  defenseDecisionValidationA1(state,validation);const rngAfter=defenseDecisionRngStampA1(r);if(rngBefore!==rngAfter)state.rngMismatchCount++;const forbidden=defenseDecisionForbiddenPathA1(input);if(forbidden)state.truthAuditFailures++;
  const byId=new Map(rows.map(q=>[q.id,q])),orderedRows=validation.ok?command.trackOrder.map(id=>byId.get(id)).filter(Boolean):[];state.builds++;state.lastStep=simStepCounter;state.lastInput=input;state.lastCommand=command;state.provider=command.provider;state.mode=DEFENSE_OODA_IMPLEMENTATION_MODE_A;
  return {input,command,legacyCommand:legacy,oodaCommand:ooda,validation,legacyValidation,oodaValidation,orderedRows,priority:new Map(command.priorities.map(q=>[q.trackId,q.score])),salvoOverrides:[],usedFallback};
}
function defenseDecisionLegacySalvoA1(session,th,weapon,native){
  const r=ACTIVE_SHIP_RUNTIME,state=defenseDecisionDiagnosticStateA1(r),rngBefore=defenseDecisionRngStampA1(r),legacyResult=tacticalSalvoH1(r,th,weapon,native),oodaResult=defenseOodaSalvoA(session.input,th.id,weapon,legacyResult),legacyRow={trackId:th.id,weapon,desiredSalvo:legacyResult.salvo,reason:legacyResult.policy??'LEGACY_H1'},oodaRow={trackId:th.id,weapon,desiredSalvo:oodaResult.salvo,reason:oodaResult.policy??'DEFENSE_OODA_A'};
  session.legacyCommand=defenseDecisionAppendSalvoA(session.legacyCommand,legacyRow);if(session.oodaCommand)session.oodaCommand=defenseDecisionAppendSalvoA(session.oodaCommand,oodaRow);if(session.oodaCommand)defenseDecisionShadowCompareA(state,'salvo:'+th.id+':'+weapon,legacyRow,oodaRow,true);
  let result=legacyResult,command=session.legacyCommand;if(DEFENSE_OODA_IMPLEMENTATION_MODE_A==='ACTIVE'&&session.oodaCommand){const v=defenseDecisionValidateCommandA1(r,session.input,session.oodaCommand);if(v.ok){result=oodaResult;command=session.oodaCommand;session.validation=v;}else{const s=defenseOodaEnsureStateA(r);if(s)s.diagnostics.fallback++;session.usedFallback=true;}}
  session.command=command;session.priority=new Map(command.priorities.map(q=>[q.trackId,q.score]));session.salvoOverrides=command.salvoOverrides;state.lastCommand=command;defenseDecisionValidationA1(state,defenseDecisionValidateCommandA1(r,session.input,command));const rngAfter=defenseDecisionRngStampA1(r);if(rngBefore!==rngAfter)state.rngMismatchCount++;return result;
}
function defenseDecisionRecommendationOrderA1(session,a,b){
  const legacy=tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b),ooda=session.oodaCommand?(new Map(session.oodaCommand.priorities.map(q=>[q.trackId,q.score])).get(b.trackId)??0)-(new Map(session.oodaCommand.priorities.map(q=>[q.trackId,q.score])).get(a.trackId)??0):0;if(session.oodaCommand)defenseDecisionShadowCompareA(defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME),'recommendationOrder',legacy,ooda,true);return session.validation.ok?((session.command.provider==='DEFENSE_OODA_A')?ooda:legacy):0;
}
function defenseDecisionLegacyFinishA1(session,recommendations){
  const state=defenseDecisionDiagnosticStateA1(ACTIVE_SHIP_RUNTIME);state.lastCommand=session.command;state.lastValidation={...session.validation};const legacy=[...recommendations].sort((a,b)=>(b.assessment==='THREAT')-(a.assessment==='THREAT')||tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b)||(b.threatScore??0)-(a.threatScore??0)).map(q=>q.trackId);defenseDecisionShadowCompareA(state,'finalRecommendationOrder',legacy,recommendations.map(q=>q.trackId),true);return session.command;
}
function wip118SalvoPolicy(th,weapon,assessment,plan,decision=null){const native=wip118SalvoPolicyNativeH1(th,weapon,assessment,plan);return decision?defenseDecisionLegacySalvoA1(decision,th,weapon,native):tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,native);}
"""


def patch(text: str, stage: str) -> str:
    mode = {"A": "OFF", "B": "OFF", "C": "SHADOW", "D": "ACTIVE"}[stage]
    runtime = (HERE / "defense_ooda_runtime.js").read_text().replace("__DEFENSE_OODA_MODE__", mode)
    text = replace_count(text, RUNTIME_MARKER, runtime.rstrip() + "\n\n" + RUNTIME_MARKER, 1, "runtime insertion")

    text = replace_count(text,
        "const AEGIS_DEFENSE_DECISION_PROVIDER_A1='LEGACY_H1';\nconst AEGIS_DEFENSE_DECISION_MODE_A1='ACTIVE';",
        "const AEGIS_DEFENSE_DECISION_PROVIDER_A1=DEFENSE_OODA_IMPLEMENTATION_MODE_A==='ACTIVE'?'DEFENSE_OODA_A':'LEGACY_H1';\nconst AEGIS_DEFENSE_DECISION_MODE_A1=DEFENSE_OODA_IMPLEMENTATION_MODE_A;",
        1, "provider mode")
    text = replace_count(text,
        "if(command.schema!==AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1||command.provider!==AEGIS_DEFENSE_DECISION_PROVIDER_A1)return bad('COMMAND_SCHEMA');",
        "if(command.schema!==AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1||!DEFENSE_OODA_PROVIDER_VALUES_A.includes(command.provider))return bad('COMMAND_SCHEMA');",
        1, "provider validator")

    ddg_profile = "defenseOodaA:Object.freeze({schema:'AEGIS_DEFENSE_OODA_PROFILE_A1',source:'SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC',baseConcurrentEvaluations:4,baseObserveSteps:12,baseOrientSteps:24,baseDecisionSteps:12,modernizationFactor:1,minimumOperationalCapacity:.2,queueLimit:64,agingStepInterval:300,urgentTgoBandsS:Object.freeze([8,15,30])}),"
    cg_profile = "defenseOodaA:Object.freeze({schema:'AEGIS_DEFENSE_OODA_PROFILE_A1',source:'SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC',baseConcurrentEvaluations:4,baseObserveSteps:18,baseOrientSteps:30,baseDecisionSteps:18,modernizationFactor:.8,minimumOperationalCapacity:.2,queueLimit:64,agingStepInterval:300,urgentTgoBandsS:Object.freeze([8,15,30])}),"
    text = replace_count(text,
        "  coordinates:{frame:'SHIP_LOCAL_METRES',longitudinal:'+X_BOW',transverse:'+Y_STARBOARD',vertical:'+Z_UP',headingRadZero:'+X_BOW'},",
        "  coordinates:{frame:'SHIP_LOCAL_METRES',longitudinal:'+X_BOW',transverse:'+Y_STARBOARD',vertical:'+Z_UP',headingRadZero:'+X_BOW'},\n  "+ddg_profile,
        1, "DDG profile")
    text = replace_count(text, "    coordinates:copy(D.coordinates),", "    coordinates:copy(D.coordinates),\n    "+cg_profile, 1, "CG profile")

    text = regex_replace(text, r"function defenseDecisionLegacyCommandA1\(input,rows\)\{.*?\n\}", LEGACY_COMMAND, 2, "legacy command")
    if stage in {"C", "D"}:
        text = regex_replace(text,
            r"function defenseDecisionLegacyBeginA1\(rows\)\{.*?function wip118SalvoPolicy\(th,weapon,assessment,plan,decision=null\)\{.*?\}",
            ADAPTER.strip(), 2, "OODA adapter")
        text = replace_count(text,
            "shadowMismatchCount:q.shadowMismatchCount,firstMismatch:",
            "shadowMismatchCount:q.shadowMismatchCount,allowedShadowDifferenceCount:q.allowedShadowDifferenceCount??0,firstAllowedShadowDifference:q.firstAllowedShadowDifference?jsonSafeCloneV48Wip11A(q.firstAllowedShadowDifference):null,firstMismatch:",
            1, "OODA diagnostic allowed difference")
        text = replace_count(text,
            "shadowMismatchCount:0,firstMismatch:null,validationFailures:",
            "shadowMismatchCount:0,allowedShadowDifferenceCount:0,firstAllowedShadowDifference:null,firstMismatch:null,validationFailures:",
            2, "OODA diagnostic allowed difference default")

    text = replace_count(text, "saveFields:0,", "saveFields:1,", 1, "public save field")
    text = replace_count(text,
        "input:defenseDecisionInputForOwnerA1,diagnostics:defenseDecisionDiagnosticsForOwnerA1,ships:",
        "input:defenseDecisionInputForOwnerA1,diagnostics:defenseDecisionDiagnosticsForOwnerA1,ooda:id=>{const r=defenseDecisionOwnerA1(id);return r?defenseOodaSnapshotA(r):null;},selfTest:defenseOodaContractSelfTestA,engineSelfTest:defenseOodaEngineSelfTestA,ships:",
        1, "public OODA API")

    # Active and foreign save/export/validation/restore. The overall operational
    # schema stays V2; this is an optional field migrated before validation.
    text = replace_count(text, "ship:{team:teamSettingsH4(ACTIVE_SHIP_RUNTIME),", "ship:{defenseOodaA:defenseOodaExportStateA(ACTIVE_SHIP_RUNTIME),team:teamSettingsH4(ACTIVE_SHIP_RUNTIME),", 1, "active export")
    text = replace_count(text, "return {entityId:r.entityId,role:r.role,faction:r.faction,team:teamSettingsH4(r),", "return {entityId:r.entityId,role:r.role,faction:r.faction,defenseOodaA:defenseOodaExportStateA(r),team:teamSettingsH4(r),", 1, "fleet export")
    text = replace_count(text,
        "migrateEmconSaveB(src,harpoonMigrations);migrateEsmSaveA(src,harpoonMigrations);",
        "migrateEmconSaveB(src,harpoonMigrations);migrateEsmSaveA(src,harpoonMigrations);defenseOodaMigrateSaveA(src,harpoonMigrations);",
        1, "save migration")
    text = replace_count(text,
        "if(!operationalRecordV48Wip11B(src.ship))operationalErrorV48Wip11B(errors,'SHIP');",
        "if(!operationalRecordV48Wip11B(src.ship))operationalErrorV48Wip11B(errors,'SHIP');else defenseOodaValidateSaveA(src.profileId,src.shipId,src.ship.defenseOodaA,errors,'ship');",
        1, "active validation")
    text = replace_count(text,
        "seen.add(q.entityId);validateEmconSaveB(q.profileId,q.emconB,errors,'fleet.'+q.entityId);",
        "seen.add(q.entityId);defenseOodaValidateSaveA(q.profileId,q.entityId,q.defenseOodaA,errors,'fleet.'+q.entityId);validateEmconSaveB(q.profileId,q.emconB,errors,'fleet.'+q.entityId);",
        1, "fleet validation")
    text = replace_count(text,
        "r.restoredElectronicF=q.ew??null;r.restoredEmconB=q.emconB??null;",
        "r.restoredDefenseOodaA=q.defenseOodaA??null;r.restoredElectronicF=q.ew??null;r.restoredEmconB=q.emconB??null;",
        1, "fleet staged restore")
    text = replace_count(text,
        "if(!r.survival)preparePhysicalShipB(r);r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';prepareObserverC(r);prepareWeaponsD(r);",
        "if(!r.survival)preparePhysicalShipB(r);r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';prepareObserverC(r);prepareWeaponsD(r);if(r.restoredDefenseOodaA){defenseOodaRestoreStateA(r,r.restoredDefenseOodaA);delete r.restoredDefenseOodaA;}",
        1, "fleet authoritative restore")
    text = replace_count(text,
        "if(src.ship.network){ACTIVE_SHIP_RUNTIME.combatSystem.networkG=null;ACTIVE_SHIP_RUNTIME.restoredNetworkG=src.ship.network;prepareNetworkG(ACTIVE_SHIP_RUNTIME);}ENGAGEMENT_RUNTIME.lifecycle=",
        "if(src.ship.network){ACTIVE_SHIP_RUNTIME.combatSystem.networkG=null;ACTIVE_SHIP_RUNTIME.restoredNetworkG=src.ship.network;prepareNetworkG(ACTIVE_SHIP_RUNTIME);}defenseOodaRestoreStateA(ACTIVE_SHIP_RUNTIME,src.ship.defenseOodaA);ENGAGEMENT_RUNTIME.lifecycle=",
        1, "active authoritative restore")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--stage", choices=["A", "B", "C", "D"], default="A")
    parser.add_argument("--js-output", type=Path)
    args = parser.parse_args()
    raw = args.baseline.read_bytes()
    js_raw, packed = extract(raw)
    candidate = patch(js_raw.decode("utf-8"), args.stage).encode("utf-8")
    if args.js_output:
        args.js_output.write_bytes(candidate)
    blob = base64.b64encode(gzip.compress(candidate, compresslevel=9, mtime=0))
    out = raw[:packed.start(2)] + blob + raw[packed.end(2):]
    args.output.write_bytes(out)
    print(f"stage={args.stage}")
    print(f"baseline_js_sha256={hashlib.sha256(js_raw).hexdigest()}")
    print(f"candidate_js_sha256={hashlib.sha256(candidate).hexdigest()}")
    print(f"candidate_html_bytes={len(out)}")
    print(f"candidate_html_sha256={hashlib.sha256(out).hexdigest()}")


if __name__ == "__main__":
    main()
