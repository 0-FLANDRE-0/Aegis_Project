#!/usr/bin/env python3
"""Build SEEKER_UNIFY_U3 incrementally from the pinned CUE_A-1 product."""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
BASE_SHA = "0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script not found")
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def exact(source: str, old: str, new: str, count: int, label: str) -> str:
    actual = source.count(old)
    if actual != count:
        raise AssertionError(f"{label}: expected {count} anchors, got {actual}")
    return source.replace(old, new)


def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf"function\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise AssertionError(f"function missing: {name}")
    paren = source.find("(", match.start())
    depth = 0
    quote = None
    escaped = False
    close = -1
    for index in range(paren, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                close = index
                break
    brace = source.find("{", close + 1)
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return match.start(), index + 1
    raise AssertionError(f"unterminated function: {name}")


def transform_a(source: str, mode: str) -> str:
    """Connect Harpoon power/pre-resolved cells to U2 without changing behavior."""
    source = one(
        source,
        "  SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING',rangeFloorKm:.20,rangeFloorProvenance:'LEGACY_EQUIVALENCE'})\n});",
        "  SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING',rangeFloorKm:.20,rangeFloorProvenance:'LEGACY_EQUIVALENCE'}),\n  HARPOON:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'HARPOON_NATIVE_MONOSTATIC',extentPolicy:'PRE_RESOLVED_ANONYMOUS',angularPolicy:'BODY_RELATIVE_MEASUREMENT',maxCells:96})\n});",
        "U2 Harpoon profile option",
    )
    source = one(
        source,
        "  if(option.beamConvention==='COMBINED_SINGLE'){",
        "  if(option.beamConvention==='HARPOON_NATIVE_MONOSTATIC'){\n    // Preserve the RGM-84D multiplication order exactly; referenceSnr is part\n    // of the legacy Harpoon profile rather than a normalized unit-power path.\n    return q.referenceSnr*(q.rcsM2/q.referenceRcsM2)*(q.referenceRangeM/q.rangeM)**4*q.txRxGain*q.losQ*q.pathQ;\n  }\n  if(option.beamConvention==='COMBINED_SINGLE'){",
        "U2 Harpoon monostatic power",
    )
    source = one(
        source,
        "  if(option.extentPolicy==='POWER_WEIGHTED_RMS'&&option.angularPolicy==='AXIS_SEPARATE_COMPOSITE')return seekerResolveAsmCellsLegacyEquivalentU2.apply(self,args);",
        "  if(option.extentPolicy==='PRE_RESOLVED_ANONYMOUS'&&option.angularPolicy==='BODY_RELATIVE_MEASUREMENT')return seekerResolveHarpoonCellsLegacyEquivalentU3.apply(self,args);\n  if(option.extentPolicy==='POWER_WEIGHTED_RMS'&&option.angularPolicy==='AXIS_SEPARATE_COMPOSITE')return seekerResolveAsmCellsLegacyEquivalentU2.apply(self,args);",
        "U2 Harpoon pre-resolved cells",
    )
    insert_anchor = "function seekerResolvedCellStatisticsU2(members,weightOf){"
    insert = f"""// SEEKER_UNIFY_U3 Commit A: Harpoon uses the U2 common profile contract.
const SEEKER_U3_HARPOON_RF_MODE_A='{mode}';
const SEEKER_U3_HARPOON_AUDIT_A={{powerComparisons:0,powerMismatches:0,cellComparisons:0,cellMismatches:0,maxAbsPowerDifference:0}};
function seekerResolveHarpoonCellsLegacyEquivalentU3(observations,maxCells=96){{return observations.sort((a,b)=>b.snr-a.snr).slice(0,maxCells);}}
function seekerU3HarpoonCompareNumberA(kind,legacy,common){{
  if(kind==='power'){{SEEKER_U3_HARPOON_AUDIT_A.powerComparisons++;const d=Math.abs(legacy-common);SEEKER_U3_HARPOON_AUDIT_A.maxAbsPowerDifference=Math.max(SEEKER_U3_HARPOON_AUDIT_A.maxAbsPowerDifference,d);if(!Object.is(legacy,common))SEEKER_U3_HARPOON_AUDIT_A.powerMismatches++;}}
}}
function seekerU3HarpoonCompareCellsA(legacy,common){{SEEKER_U3_HARPOON_AUDIT_A.cellComparisons++;if(JSON.stringify(legacy)!==JSON.stringify(common))SEEKER_U3_HARPOON_AUDIT_A.cellMismatches++;}}
function seekerU3HarpoonSnapshotA(){{return Object.freeze({{mode:SEEKER_U3_HARPOON_RF_MODE_A,...SEEKER_U3_HARPOON_AUDIT_A,rngConsumedByCommonLayer:false,truthOutput:false,tacticalOutputUsed:SEEKER_U3_HARPOON_RF_MODE_A==='ACTIVE'}});}}

"""
    source = one(source, insert_anchor, insert + insert_anchor, "U3 A adapter insertion")

    start = source.find("function harpoonRfObservationsA(m,beamAz,beamEl){")
    end = source.find("// Independent RF seeker.", start)
    if start < 0 or end < 0:
        raise AssertionError("Harpoon RF function anchors missing")
    replacement = (HERE / "harpoon_rf_a.js").read_text().rstrip() + "\n"
    source = source[:start] + replacement + source[end:]

    source = one(
        source,
        "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells']),shadowComponents:Object.freeze([]),reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,\n  tacticalOutputUsed:true,rngConsumed:false,truthOutput:false});",
        "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON']),reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,\n  harpoonMode:SEEKER_U3_HARPOON_RF_MODE_A,harpoonSnapshot:seekerU3HarpoonSnapshotA,\n  tacticalOutputUsed:true,rngConsumed:false,truthOutput:false});",
        "U2 public Harpoon contract",
    )
    return source


def transform_b(source: str) -> str:
    """Route observed-track memory through CUE_A; preserve route prior at 4 km."""
    anchor = "function runCoreUnitSelfTests(){"
    source = one(source, anchor, (HERE / "harpoon_cue_b.js").read_text().rstrip() + "\n" + anchor, "B cue adapter")
    source = one(
        source,
        "stateEpoch:'RELEASE_CURRENT_EKF',stateAgeS:0,observationAgeS:Math.max(0,Number(tr.sensorAge)||0),launchStep:simStepCounter,identity:normalizeTrackOperatorIdentityA3(tr._operatorIdentity),\n    truthUsed:false,updatesAfterRelease:false});",
        "stateEpoch:'RELEASE_CURRENT_EKF',stateAgeS:0,observationAgeS:Math.max(0,Number(tr.sensorAge)||0),launchStep:simStepCounter,identity:normalizeTrackOperatorIdentityA3(tr._operatorIdentity),\n    cueSource:'LOCAL_SURFACE_OBSERVATION',positionVelocityOwner:'SHIP_EKF_RELEASE_SNAPSHOT',covarianceOwner:'SHIP_EKF_RELEASE_SNAPSHOT',timeOwner:'SIM_FIXED_STEP_RELEASE',\n    truthUsed:false,updatesAfterRelease:false});",
        "B observed memory ownership",
    )
    source = one(
        source,
        "searchCenterM,routeLengthM:pathM,plannedLengthM:pathM+cfg.routeSearchAheadM+cfg.routeTurnReserveM,\n    seekerActivation:'AFTER_FINAL_INS_WAYPOINT_PLANE',dataLink:false,updatesAfterRelease:false,truthUsed:false});",
        "searchCenterM,routeLengthM:pathM,plannedLengthM:pathM+cfg.routeSearchAheadM+cfg.routeTurnReserveM,\n    cueSource:'ROUTE_PLAN_PRIOR',observationUpdate:false,planSearchRadiusM:cfg.seekerSearchBasketM,\n    seekerActivation:'AFTER_FINAL_INS_WAYPOINT_PLANE',dataLink:false,updatesAfterRelease:false,truthUsed:false});",
        "B route-program provenance",
    )
    source = exact(
        source,
        "launchStep:simStepCounter,identity:'COORDINATE_SEARCH',truthUsed:false,updatesAfterRelease:false});",
        "launchStep:simStepCounter,identity:'COORDINATE_SEARCH',cueSource:'ROUTE_PLAN_PRIOR',observationUpdate:false,\n    positionVelocityOwner:'OPERATOR_ROUTE_PLAN',covarianceOwner:'NONE_NOT_A_MEASUREMENT',timeOwner:'RELEASE_FIXED_COORDINATE',truthUsed:false,updatesAfterRelease:false});",
        3,
        "B route-memory provenance copies",
    )
    source = exact(
        source,
        "return {ok:true,reason:null,trackId:tr?.trackId??null,tubeId,rangeKm:program.plannedLengthM/1000,memory,routeProgram:program,\n    muzzleM:muzzle,axis,authority:{ok:true,mode:'MANUAL_COORDINATE_SEARCH'},truthUsed:false};",
        "const cueHandoff=harpoonCueHandoffB(memory,0);\n  return {ok:true,reason:null,trackId:tr?.trackId??null,tubeId,rangeKm:program.plannedLengthM/1000,memory,routeProgram:program,\n    predictionSigmaM:cueHandoff.predictionSigmaM,searchBasketM:cueHandoff.searchBasketM,cueHandoff,\n    muzzleM:muzzle,axis,authority:{ok:true,mode:'MANUAL_COORDINATE_SEARCH'},truthUsed:false};",
        3,
        "B route gate copies",
    )
    source = exact(
        source,
        "const P=tr._kfP,t=Math.max(0,(readiness.rangeKm*1000-cfg.seekerActivationRangeM)/cfg.cruiseSpeedMps),\n    sigma=2*Math.sqrt(Math.max(P[0]+t*(P[3]+P[18])+t*t*P[21],P[7]+t*(P[10]+P[25])+t*t*P[28],0)+80**2+(t*t*.04)**2);\n  if(!Number.isFinite(sigma)||sigma>cfg.acquisitionBasketM)return bad('INS_PREDICTION_BASKET_INSUFFICIENT',{predictionSigmaM:sigma});",
        "const memory=harpoonMemoryA(tr),t=Math.max(0,(readiness.rangeKm*1000-cfg.seekerActivationRangeM)/cfg.cruiseSpeedMps),cueHandoff=harpoonCueHandoffB(memory,t),\n    sigma=cueHandoff.predictionSigmaM,searchBasketM=cueHandoff.searchBasketM;\n  if(!cueHandoff.feasible)return bad(cueHandoff.reason,{predictionSigmaM:sigma,searchBasketM,physicalSearchLimitM:cueHandoff.physicalSearchLimitM,cueSource:cueHandoff.source});",
        3,
        "B track gate copies",
    )
    source = exact(
        source,
        "const result={ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,rangeKm:readiness.rangeKm,\n    memory:harpoonMemoryA(tr),muzzleM:muzzle,axis,authority,truthUsed:false};",
        "const result={ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,searchBasketM,cueHandoff,rangeKm:readiness.rangeKm,\n    memory,muzzleM:muzzle,axis,authority,truthUsed:false};",
        3,
        "B track result copies",
    )
    source = exact(
        source,
        "route:gate.routeProgram?{program:gate.routeProgram,index:0,completed:false,passes:[],previousInsM:{x:pos.x,y:pos.y}}:null,\n    memory:gate.memory,massKg:HARPOON_PROFILE_A.public.launchMassKg",
        "route:gate.routeProgram?{program:gate.routeProgram,index:0,completed:false,passes:[],previousInsM:{x:pos.x,y:pos.y}}:null,\n    memory:gate.memory,cueHandoff:gate.cueHandoff,massKg:HARPOON_PROFILE_A.public.launchMassKg",
        2,
        "B missile cue ownership",
    )
    source = one(
        source,
        "cueGate=m.route?cfg.seekerSearchBasketM:Math.min(cfg.seekerSearchBasketM,Math.max(250,3*Math.sqrt(lambda+75**2+(t*t*.04)**2))),",
        "cueHandoff=m.route?harpoonCueHandoffB(m.memory,0):(m.cueHandoff??=harpoonCueHandoffB(m.memory,time+Math.max(0,(rangeToBasket-cfg.seekerActivationRangeM)/cfg.cruiseSpeedMps))),\n    cueGate=m.route?cfg.seekerSearchBasketM:cueHandoff.searchBasketM,",
        "B runtime dynamic basket",
    )
    source = one(
        source,
        "const P=m.memory.covariance,t=time,cxx=Math.max(0,P[0]+t*(P[3]+P[18])+t*t*P[21]),cyy=Math.max(0,P[7]+t*(P[10]+P[25])+t*t*P[28]),\n    cxy=P[1]+t*(P[4]+P[19])+t*t*P[22],lambda=(cxx+cyy+Math.hypot(cxx-cyy,2*cxy))*.5,\n    cueHandoff=",
        "const cueHandoff=",
        "B remove legacy covariance shortcut",
    )
    source = one(
        source,
        "terminal<HARPOON_PROFILE_A.sim.seekerSearchBasketM+ATTACK_POLICY_H3.protectedMarginM+sigma",
        "terminal<(gate.searchBasketM??HARPOON_PROFILE_A.sim.seekerSearchBasketM)+ATTACK_POLICY_H3.protectedMarginM+sigma",
        "B protected-zone consumer",
    )
    source = one(
        source,
        "predictionSigmaM:gate.predictionSigmaM??null,launchEmcon:",
        "predictionSigmaM:gate.predictionSigmaM??null,searchBasketM:gate.searchBasketM??null,cueSource:gate.cueHandoff?.source??null,launchEmcon:",
        "B journal consumer",
    )
    source = one(
        source,
        "predictionSigmaM:gate.predictionSigmaM??null,...(path.ok?",
        "predictionSigmaM:gate.predictionSigmaM??null,searchBasketM:gate.searchBasketM??null,...(path.ok?",
        "B AI diagnostic consumer",
    )
    return source


def transform_c(source: str, mode: str) -> str:
    """Move HOJ angular tracking behind a common port and add Harpoon policy."""
    source = one(
        source,
        "  'Kh-32':Object.freeze({passiveRfBearingElevation:'ASSUMED_THREAT'})\n});",
        "  'Kh-32':Object.freeze({passiveRfBearingElevation:'ASSUMED_THREAT'}),\n  'RGM-84D':Object.freeze({terminalHoj:'ASSUMED_THREAT'})\n});",
        "C Harpoon capability provenance",
    )
    start, end = function_span(source, "asmUpdateHojTrack")
    original = source[start:end]
    legacy = original.replace("function asmUpdateHojTrack(", "function asmUpdateHojTrackLegacyU3(", 1)
    common = (HERE / "hoj_common_c.js").read_text().replace("__MODE__", mode).rstrip()
    source = source[:start] + legacy + "\n" + common + source[end:]
    anchor = "function runCoreUnitSelfTests(){"
    source = one(source, anchor, (HERE / "harpoon_hoj_c.js").read_text().rstrip() + "\n" + anchor, "C Harpoon HOJ adapter")
    source = exact(
        source,
        "candidate:null,lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0},history:[],outcome:null,rcsM2:.06};",
        "candidate:null,lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0,hoj:null},history:[],outcome:null,rcsM2:.06};",
        2,
        "C Harpoon state ownership copies",
    )
    source = one(
        source,
        "if(!s.active)return;\n  const cueHandoff=",
        "if(!s.active)return;\n  harpoonUpdateHojC(m,dt);\n  const cueHandoff=",
        "C terminal-only Harpoon HOJ update",
    )
    source = one(
        source,
        "const lock=m.seeker.lock,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),terminal=lock&&['TRACK','COAST'].includes(m.seeker.mode),\n    tgo=terminal?Math.hypot(lock.x-m.navPositionM.x,lock.y-m.navPositionM.y)/Math.max(50,Math.hypot(m.ins.velocityMps.x,m.ins.velocityMps.y)):pred.tgoS,\n    aim=terminal?{x:lock.x+lock.vx*(tgo+m.seeker.missedS),y:lock.y+lock.vy*(tgo+m.seeker.missedS)}:harpoonRouteAimE(m,pred),\n    targetYaw=Math.atan2(aim.y-m.navPositionM.y,aim.x-m.navPositionM.x),",
        "const lock=m.seeker.lock,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),rfTerminal=lock&&['TRACK','COAST'].includes(m.seeker.mode),hojTerminal=harpoonHojGuidanceActiveC(m),terminal=rfTerminal||hojTerminal,\n    tgo=rfTerminal?Math.hypot(lock.x-m.navPositionM.x,lock.y-m.navPositionM.y)/Math.max(50,Math.hypot(m.ins.velocityMps.x,m.ins.velocityMps.y)):pred.tgoS,\n    aim=rfTerminal?{x:lock.x+lock.vx*(tgo+m.seeker.missedS),y:lock.y+lock.vy*(tgo+m.seeker.missedS)}:harpoonRouteAimE(m,pred),\n    targetYaw=hojTerminal?seekerEnsureHojStateU3(m.seeker).worldAz:Math.atan2(aim.y-m.navPositionM.y,aim.x-m.navPositionM.x),",
        "C Harpoon guidance source",
    )
    source = one(
        source,
        "m.phase=terminal?'TERMINAL_ARH':(m.seeker.active?'INS_SEARCH':'INS_CRUISE');",
        "m.phase=hojTerminal?'TERMINAL_HOJ':(rfTerminal?'TERMINAL_ARH':(m.seeker.active?'INS_SEARCH':'INS_CRUISE'));",
        "C Harpoon phase",
    )
    source = one(
        source,
        "guidanceState:m.phase,guidanceAuthority:['TRACK','COAST'].includes(m.seeker.mode)?'ARH':'INS'",
        "guidanceState:m.phase,guidanceAuthority:harpoonHojGuidanceActiveC(m)?'HOJ':(['TRACK','COAST'].includes(m.seeker.mode)?'ARH':'INS')",
        "C render guidance source",
    )
    return source


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    if not meta:
        raise AssertionError("packed record metadata not found")
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + out[meta.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--through", choices=("A", "B", "C"), default="A")
    parser.add_argument("--a-mode", choices=("SHADOW", "ACTIVE"), default="ACTIVE")
    parser.add_argument("--c-mode", choices=("SHADOW", "ACTIVE"), default="ACTIVE")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--diff-path", type=Path)
    args = parser.parse_args()

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError(f"baseline SHA mismatch: {sha(raw)}")
    before, match = unpack(raw)
    after_a = transform_a(before, args.a_mode)
    after = after_a
    if args.through in ("B", "C"):
        if args.a_mode != "ACTIVE":
            raise AssertionError("B requires Commit A ACTIVE")
        after = transform_b(after)
    after_b = after
    if args.through == "C":
        after = transform_c(after, args.c_mode)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    if check != after:
        raise AssertionError("repacked main script mismatch")
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="CUE_A_1/main.js", tofile=f"SEEKER_UNIFY_U3_A_{args.a_mode}/main.js"))
    diff_path = args.diff_path or HERE / f"changes-A-{args.a_mode.lower()}.diff"
    diff_path.write_text("".join("\n" if line == " \n" else line for line in diff.splitlines(True)))
    stage_diff_path = None
    if args.through in ("B", "C"):
        stage_before = after_a if args.through == "B" else after_b
        stage_diff = "".join(difflib.unified_diff(stage_before.splitlines(True), after.splitlines(True), fromfile=f"SEEKER_UNIFY_U3_{chr(ord(args.through)-1)}/main.js", tofile=f"SEEKER_UNIFY_U3_{args.through}/main.js"))
        stage_diff_path = HERE / f"changes-{args.through}.diff"
        stage_diff_path.write_text("".join("\n" if line == " \n" else line for line in stage_diff.splitlines(True)))
    receipt = args.receipt or HERE / f"BUILD_A_{args.a_mode}.json"
    build = {
        "schema": f"AEGIS_SEEKER_UNIFY_U3_BUILD_{args.through}_1",
        "baselineCommit": "be19f46794705a18bfd69feba99d7a4b00dd4a0c",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "through": args.through,
        "harpoonU2Mode": args.a_mode,
        "harpoonCueMode": "CUE_A_ACTIVE" if args.through in ("B", "C") else "NOT_CONNECTED",
        "hojCommonMode": args.c_mode if args.through == "C" else "NOT_CONNECTED",
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
        "stageDiff": str(stage_diff_path.relative_to(ROOT)) if stage_diff_path else None,
        "gameplayConstantsAdded": 0,
        "rngContract": ("ASM_GLOBAL_STREAM_LEGACY_EQUIVALENT__HARPOON_MISSILE_OWNED_STREAM_ONLY_WHEN_ASSUMED_HOJ_SIGNAL_ACCEPTED" if args.through == "C" else "HARPOON_EXISTING_CALL_ORDER_UNCHANGED_COMMON_LAYER_CONSUMES_ZERO"),
        "truthOutput": False,
    }
    receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
