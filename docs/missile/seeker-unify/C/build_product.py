#!/usr/bin/env python3
"""Build SEEKER_UNIFY_C from the pinned SEEKER_UNIFY_B product.

Stage 1 promotes U2 from diagnostic SHADOW to an ACTIVE common dispatcher.
Stage 2 applies the audited monostatic ASM beam/LOS definition while retaining
all numeric profile values, RF thresholds, RNG paths, and truth boundaries.
Stage 3 replaces point drift/gain rotation with CUE_A covariance prediction,
anonymous passive-RF angle measurements, provenance and threat-mode plumbing.
"""
from __future__ import annotations

import argparse
import base64
import difflib
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
BASE_SHA = "b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def replace_between(source: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str:
    if source.count(start_marker) != 1 or source.count(end_marker) < 1:
        raise AssertionError(f"{label}: marker mismatch")
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + replacement.rstrip() + "\n" + source[end:]


def remove_b_u2_shadow(source: str) -> str:
    start_marker = "// SEEKER_UNIFY_B U2: WIP22 ASM + SAM ARH common echo/cell SHADOW."
    end_marker = "  window.__NAVAL_SIM_DIAG__ = {"
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + source[end:]


def transform_u2_active(source: str) -> str:
    source = remove_b_u2_shadow(source)

    source = one(
        source,
        "function asmSeekerCompositeReturns(em,s,p,raw){",
        "function seekerResolveAsmCellsLegacyEquivalentU2(em,s,p,raw){",
        "rename ASM legacy-equivalent cell strategy",
    )
    source = one(
        source,
        "function _arhClusterEchoes(echoes,p=getEssmArhProfile()){",
        "function seekerResolveSamCellsLegacyEquivalentU2(echoes,p=getEssmArhProfile()){",
        "rename SAM legacy-equivalent cell strategy",
    )

    # The core contract must be initialized before the product's synchronous
    # runCoreUnitSelfTests invokes _arhNormalizedMonostaticPower. Function
    # declarations are hoisted, but this frozen option object is lexical state.
    core_layer = """// SEEKER_UNIFY_C Stage 1: U2 ACTIVE legacy-equivalent echo/cell core.
// The options document pre-existing implementation differences. They are
// LEGACY_EQUIVALENCE provenance, not hardware claims or tuned coefficients.
const SEEKER_U2_PROFILE_OPTIONS=Object.freeze({
  ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08}),
  SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING'})
});
function seekerSynthesizeMonostaticPowerU2(family,q){
  const option=SEEKER_U2_PROFILE_OPTIONS[family];if(!option)throw new Error('UNKNOWN_SEEKER_U2_PROFILE:'+family);
  if(option.beamConvention==='COMBINED_SINGLE'){
    // Preserve the WIP22 multiplication order exactly: one combined pattern,
    // one LOS factor, residual environment, then weather/path propagation.
    return (q.rcsM2/q.referenceRcsM2)
      *Math.pow(q.referenceRangeKm/Math.max(.5,q.rangeKm),4)
      *(q.losTxQ??1)*q.envQ*q.txGain*q.pathQ;
  }
  if(option.beamConvention==='TX_RX_SEPARATE'){
    // Preserve _arhNormalizedMonostaticPower operation order exactly.
    return Math.max(0,q.rcsM2)/Math.max(1e-9,q.referenceRcsM2)
      *Math.pow(q.referenceRangeKm/Math.max(.20,q.rangeKm),4)
      *Math.max(0,q.txGain)*Math.max(0,q.rxGain)*Math.max(0,q.losTxQ)*Math.max(0,q.losRxQ)*Math.max(0,q.envQ);
  }
  throw new Error('UNKNOWN_SEEKER_U2_BEAM_CONVENTION:'+option.beamConvention);
}
function seekerResolveCellsU2(family,self,args){
  const option=SEEKER_U2_PROFILE_OPTIONS[family];if(!option)throw new Error('UNKNOWN_SEEKER_U2_PROFILE:'+family);
  if(option.extentPolicy==='POWER_WEIGHTED_RMS'&&option.angularPolicy==='AXIS_SEPARATE_COMPOSITE')return seekerResolveAsmCellsLegacyEquivalentU2.apply(self,args);
  if(option.extentPolicy==='MAX_MEMBER'&&option.angularPolicy==='SPHERICAL_MEMBER_PRESERVING')return seekerResolveSamCellsLegacyEquivalentU2.apply(self,args);
  throw new Error('UNSUPPORTED_SEEKER_U2_CELL_POLICY:'+family);
}
function seekerResolvedCellStatisticsU2(members,weightOf){
  // Read-only superset for diagnostics/future adapters: both weighted RMS and
  // member maxima are available without changing either tactical return type.
  let sw=0,r2=0,c2=0,v2=0,d2=0,maxR=0,maxC=0,maxV=0,maxD=0;
  for(const m of members??[]){const w=Math.max(0,Number(weightOf?weightOf(m):1)||0);sw+=w;r2+=w*(m.rangeExtentM??m.extentRangeM??0)**2;c2+=w*(m.crossExtentM??m.extentCrossM??0)**2;v2+=w*(m.verticalExtentM??m.extentVerticalM??0)**2;d2+=w*(m.dopplerSpreadMps??0)**2;maxR=Math.max(maxR,m.rangeExtentM??m.extentRangeM??0);maxC=Math.max(maxC,m.crossExtentM??m.extentCrossM??0);maxV=Math.max(maxV,m.verticalExtentM??m.extentVerticalM??0);maxD=Math.max(maxD,m.dopplerSpreadMps??0);}
  sw=Math.max(sw,1e-18);return Object.freeze({memberCount:(members??[]).length,weightedRms:Object.freeze({rangeM:Math.sqrt(r2/sw),crossM:Math.sqrt(c2/sw),verticalM:Math.sqrt(v2/sw),dopplerMps:Math.sqrt(d2/sw)}),memberMax:Object.freeze({rangeM:maxR,crossM:maxC,verticalM:maxV,dopplerMps:maxD})});
}
"""
    source = one(
        source,
        "function seekerResolveAsmCellsLegacyEquivalentU2(em,s,p,raw){",
        core_layer + "function seekerResolveAsmCellsLegacyEquivalentU2(em,s,p,raw){",
        "U2 ACTIVE core before synchronous self-tests",
    )

    old_sam_power = """function _arhNormalizedMonostaticPower(rcsM2,rangeKm,txGain=1,rxGain=1,losQ=1,envQ=1,profile=null){
    const p=profile??getEssmArhProfile();
    return Math.max(0,rcsM2)/Math.max(1e-9,p.referenceRcsM2)
      *Math.pow(p.referenceRangeKm/Math.max(.20,rangeKm),4)
      *Math.max(0,txGain)*Math.max(0,rxGain)*Math.max(0,losQ)*Math.max(0,losQ)*Math.max(0,envQ);
  }"""
    new_sam_power = """function _arhNormalizedMonostaticPower(rcsM2,rangeKm,txGain=1,rxGain=1,losQ=1,envQ=1,profile=null){
    const p=profile??getEssmArhProfile();
    return seekerSynthesizeMonostaticPowerU2('SAM_ARH',{rcsM2,rangeKm,referenceRcsM2:p.referenceRcsM2,referenceRangeKm:p.referenceRangeKm,txGain,rxGain,losTxQ:losQ,losRxQ:losQ,envQ});
  }"""
    source = one(source, old_sam_power, new_sam_power, "SAM common monostatic synthesis")

    old_asm_power = """const weatherQ=maritimeRfWeatherPathFactorWip13A3('IJ',2*rKm),cleanSnr=(src.rcs/p.refRcsM2)*Math.pow(p.snrRefKm/Math.max(.5,rKm),4)*(src._losQ??1)*clutter*offGain*weatherQ;"""
    new_asm_power = """const weatherQ=maritimeRfWeatherPathFactorWip13A3('IJ',2*rKm),cleanSnr=seekerSynthesizeMonostaticPowerU2('ASM_WIP22',{rcsM2:src.rcs,rangeKm:rKm,referenceRcsM2:p.refRcsM2,referenceRangeKm:p.snrRefKm,txGain:offGain,rxGain:offGain,losTxQ:src._losQ??1,losRxQ:src._losQ??1,envQ:clutter*weatherQ});"""
    source = one(source, old_asm_power, new_asm_power, "ASM common monostatic synthesis")

    layer = """// SEEKER_UNIFY_C Stage 1: U2 ACTIVE public adapters.
function asmSeekerCompositeReturns(em,s,p,raw){return seekerResolveCellsU2('ASM_WIP22',this,arguments);}
function _arhClusterEchoes(echoes,p=getEssmArhProfile()){return seekerResolveCellsU2('SAM_ARH',this,arguments);}
function seekerU2ActiveSnapshot(){return {mode:'ACTIVE',profileOptions:SEEKER_U2_PROFILE_OPTIONS,shadowComputations:0,auditArrayCount:0};}
window.__SEEKER_COMMON_U2__=Object.freeze({schema:'AEGIS_SEEKER_COMMON_U2_ACTIVE_1',mode:'ACTIVE',profileOptions:SEEKER_U2_PROFILE_OPTIONS,
  synthesizeMonostaticPower:seekerSynthesizeMonostaticPowerU2,resolveCells:seekerResolveCellsU2,cellStatistics:seekerResolvedCellStatisticsU2,
  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells']),shadowComponents:Object.freeze([]),reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,
  tacticalOutputUsed:true,rngConsumed:false,truthOutput:false});
"""
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    return one(source, anchor, layer + "\n" + anchor, "U2 ACTIVE common layer")


def transform_cue_a(source: str) -> str:
    core = (HERE / "cue_a_core.js").read_text()
    passive = (HERE / "cue_a_passive.js").read_text()
    ui = (HERE / "cue_a_ui.js").read_text()

    source = replace_between(
        source,
        "// SEEKER_UNIFY_B U0: cue uncertainty grows only from information age.",
        "function createAsmSeekerState(label){",
        core,
        "CUE_A core",
    )
    source = replace_between(
        source,
        "  const ASM_PASSIVE_RF_B2_PROFILES=Object.freeze({",
        "  function missileNavB2Init(m,force=false){",
        passive,
        "CUE_A passive RF",
    )
    source = one(source, "function heloMountUiA(){", ui + "\nfunction heloMountUiA(){", "CUE_A UI definitions")
    source = one(
        source,
        "apsMountPerformanceUiF(panel);isarMountUiF2(panel);harpoonJournalMountF1(panel);",
        "apsMountPerformanceUiF(panel);isarMountUiF2(panel);harpoonJournalMountF1(panel);cueAMountUiC(panel);",
        "CUE_A debug UI mount",
    )

    source = one(
        source,
        "    em.flight=createAsmFlightState(em.label,em.speedMps,em.vz,em.heading);\n    if(!isSupersonic)em.kh35=em.flight;",
        "    em.flight=createAsmFlightState(em.label,em.speedMps,em.vz,em.heading);\n"
        "    if(!isSupersonic)em.kh35=em.flight;\n"
        "    em._cueLaunchA={source:'AIRCRAFT_LAST_KNOWN_UNRESOLVED',positionM:{x:worldToMeters(em.insTgtX),y:worldToMeters(em.insTgtY)},velocityMps:null,covariance:{positionSigmaM:worldToMeters(insErrWorld),velocitySigmaMps:ASM_CUE_A_SPEC.vmaxMps},timeS:0};",
        "launch cue metadata",
    )
    source = one(
        source,
        "    missileNavB2Update(em,dt);\n    const _w113=wip113RefreshBehavior(em);",
        "    missileNavB2Update(em,dt);\n    asmTargetCuePredictA(em);\n    const _w113=wip113RefreshBehavior(em);",
        "fixed-step cue prediction",
    )

    source = one(
        source,
        "return {schema:OPERATIONAL_STATE_SCHEMA_V48_WIP11A,schemaVersion:2,worldFrame:",
        "return {schema:OPERATIONAL_STATE_SCHEMA_V48_WIP11A,schemaVersion:2,threatAssumptionMode:THREAT_ASSUMPTION_MODE,worldFrame:",
        "save threat mode",
    )
    source = one(
        source,
        "    if(src.shipId!==ACTIVE_SHIP_RUNTIME.entityId)operationalErrorV48Wip11B(errors,'SHIP_ID');",
        "    if(src.shipId!==ACTIVE_SHIP_RUNTIME.entityId)operationalErrorV48Wip11B(errors,'SHIP_ID');\n"
        "    if(!ASM_CUE_THREAT_MODES_A.includes(src.threatAssumptionMode))operationalErrorV48Wip11B(errors,'THREAT_ASSUMPTION_MODE');",
        "validate threat mode",
    )
    source = one(
        source,
        "    const harpoonMigrations=[];gunB1MigrateSave(src,harpoonMigrations);",
        "    const harpoonMigrations=[];if(!Object.hasOwn(src,'threatAssumptionMode')){src.threatAssumptionMode='MAX_THREAT';harpoonMigrations.push({id:'LEGACY_THREAT_ASSUMPTION_MODE_C',policy:'DEFAULT_MAX_THREAT'});}\n"
        "    gunB1MigrateSave(src,harpoonMigrations);",
        "migrate threat mode",
    )
    source = one(
        source,
        "  function applyPreparedOperationalStateV48Wip11B(src,validation,options={}){\n    gunB1ResetAuto();",
        "  function applyPreparedOperationalStateV48Wip11B(src,validation,options={}){\n    setThreatAssumptionModeC(src.threatAssumptionMode);gunB1ResetAuto();",
        "restore threat mode",
    )

    old_boundary = "const payload=asmPassiveRfMeasurementB2(em),allowed=['source','sequence','sampleTimeS','available','bearingRad','confidence'];"
    new_boundary = "const payload=asmPassiveRfMeasurementB2(em),allowed=['source','sequence','sampleTimeS','available','bearingRad','elevationRad','snr','bearingSigmaRad','elevationSigmaRad','confidence','emitterClass','band','directRangeEstimateM','directRangeSigmaM'];"
    source = one(source, old_boundary, new_boundary, "anonymous passive payload fields")
    source = one(
        source,
        "passivePayloadNoPositionOrRange:Object.keys(payload??{}).every(k=>allowed.includes(k))",
        "passivePayloadNoTruthOrIdentity:Object.keys(payload??{}).every(k=>allowed.includes(k))",
        "boundary semantic name",
    )

    # CUE_A adds launch-memory metadata to spawnEnemyMissile, which is one of
    # ENV_D's conservative profile-hash inputs.  The added field does not alter
    # the frozen straight/constant-velocity ENV_D target, any SAM flight
    # function, or a measured range cell.  Keep those measured rows and update
    # only their exact integrity expectation to the Stage-3 function hash.
    # This is the directive's pre-approved seeker-path expectation update; no
    # acceptance tolerance or envelope value is changed.
    source = one(
        source,
        '"profileHash":"fa87852960ef276597cd43653d3d112da07cd844448d5ee6ad703c4791043121"',
        '"profileHash":"06b12b074b8a7461e121a00c109b41fa085510de0ab25654b78f2dd2b9f591e8"',
        "ENV_D CUE_A profile-hash expectation",
    )
    old_spawn_hash = '"spawnEnemyMissile":"464f1388a3e2b53ca6de34b2d7915434d4b11e0cf9619ea61f0ef8eddc29021f"'
    new_spawn_hash = '"spawnEnemyMissile":"cc18263e2b72d6a8ac7b5c49b492e65891a03012b56b41de170f1c37498327ec"'
    # The same exact expectation is stored once in the published table and
    # once in ENV_D.capture()'s runtime fingerprint input.  They must advance
    # together; historical nested tables do not contain this key.
    spawn_hash_occurrences = source.count(old_spawn_hash)
    if spawn_hash_occurrences != 2:
        raise AssertionError(f"ENV_D CUE_A native source expectation: expected 2 anchors, got {spawn_hash_occurrences}")
    source = source.replace(old_spawn_hash, new_spawn_hash)
    return source


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    assert meta
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + out[meta.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path, default=HERE / "BUILD.json")
    args = parser.parse_args()

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError(f"baseline SHA mismatch: {sha(raw)}")
    before, match = unpack(raw)
    after = transform_cue_a(transform_u2_active(before))
    output = repack(raw, after, match)
    check, _ = unpack(output)
    assert check == after
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="SEEKER_UNIFY_B/main.js", tofile="SEEKER_UNIFY_C/main.js"))
    (HERE / "changes.diff").write_text(diff)
    profile_options = json.loads((HERE / "U2_FROZEN_PROFILE_OPTIONS.json").read_text())
    build = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BUILD_3",
        "baselineCommit": "052846b10199e0b198be574d339b552bd7484658",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "completedStage": 3,
        "u2Mode": "ACTIVE",
        "stage1ProfileOptions": profile_options,
        "activeProfileOptions": json.loads((HERE / "BEAM_STAGE2_OPTIONS.json").read_text()),
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "envDProfileHashExpectationUpdate": {
            "before": "fa87852960ef276597cd43653d3d112da07cd844448d5ee6ad703c4791043121",
            "after": "06b12b074b8a7461e121a00c109b41fa085510de0ab25654b78f2dd2b9f591e8",
            "nativeFunction": "spawnEnemyMissile",
            "nativeFunctionBefore": "464f1388a3e2b53ca6de34b2d7915434d4b11e0cf9619ea61f0ef8eddc29021f",
            "nativeFunctionAfter": "cc18263e2b72d6a8ac7b5c49b492e65891a03012b56b41de170f1c37498327ec",
            "cause": "CUE_A launch-memory metadata in spawnEnemyMissile; no measured row, flight coefficient, or tolerance changed",
        },
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
    }
    args.receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()

