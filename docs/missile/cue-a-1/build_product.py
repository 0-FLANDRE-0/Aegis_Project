#!/usr/bin/env python3
"""Build CUE_A-1 incrementally from the pinned SEEKER_UNIFY_C product."""
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
ROOT = HERE.parents[2]
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"
BASE_SHA = "efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7"


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


def transform_stage1a(source: str) -> str:
    """Restore the legacy ASM floor while preserving the SAM floor."""
    source = one(
        source,
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08}),",
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08,rangeFloorKm:.5,rangeFloorProvenance:'LEGACY_EQUIVALENCE'}),",
        "ASM U2 range floor profile",
    )
    source = one(
        source,
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING'})",
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING',rangeFloorKm:.20,rangeFloorProvenance:'LEGACY_EQUIVALENCE'})",
        "SAM U2 range floor profile",
    )
    source = one(
        source,
        "*Math.pow(q.referenceRangeKm/Math.max(.20,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        "*Math.pow(q.referenceRangeKm/Math.max(option.rangeFloorKm,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        "profile-specific TX/RX range floor",
    )
    return source


def transform_stage1b(source: str) -> str:
    """Replace the 4-state white-acceleration cue with the frozen Singer model."""
    start_anchor = "  // SEEKER_UNIFY_C Stage 3: CUE_A target-memory filter."
    end_anchor = "function createAsmSeekerState(label){"
    start = source.find(start_anchor)
    end = source.find(end_anchor, start)
    if start < 0 or end < 0:
        raise AssertionError("CUE_A core anchors missing")
    core = (HERE / "cue_a_1_core.js").read_text().rstrip() + "\n"
    source = source[:start] + "  " + core + source[end:]
    source = one(
        source,
        "covariance:{positionSigmaM:worldToMeters(insErrWorld),velocitySigmaMps:ASM_CUE_A_SPEC.vmaxMps},timeS:0",
        "covariance:{positionSigmaM:worldToMeters(insErrWorld),velocitySigmaMps:ASM_CUE_A_SPEC.unknownVelocityAxisSigmaMps},timeS:0",
        "unknown-velocity launch covariance",
    )
    source = one(
        source,
        "const dx=q.x[0]-own.posM.x,dy=q.x[1]-own.posM.y,r2=Math.max(1,dx*dx+dy*dy),r=Math.sqrt(r2),Re=ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM,zEff=ASM_CUE_A_SPEC.assumedEmitterHeightM-own.posM.z-r2/(2*Re),el=Math.atan2(zEff,r),Haz=[-dy/r2,dx/r2,0,0],dhdr=(r*(-r/Re)-zEff)/Math.max(1,r2+zEff*zEff),Hel=[dhdr*dx/r,dhdr*dy/r,0,0];\n  const variance=H=>{let v=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++)v+=H[i]*q.P[i*4+j]*H[j];return Math.max(0,v);};",
        "const dx=q.x[0]-own.posM.x,dy=q.x[1]-own.posM.y,r2=Math.max(1,dx*dx+dy*dy),r=Math.sqrt(r2),Re=ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM,zEff=ASM_CUE_A_SPEC.assumedEmitterHeightM-own.posM.z-r2/(2*Re),el=Math.atan2(zEff,r),Haz=[-dy/r2,dx/r2,0,0,0,0],dhdr=(r*(-r/Re)-zEff)/Math.max(1,r2+zEff*zEff),Hel=[dhdr*dx/r,dhdr*dy/r,0,0,0,0];\n  const variance=H=>{let v=0;for(let i=0;i<6;i++)for(let j=0;j<6;j++)v+=H[i]*q.P[i*6+j]*H[j];return Math.max(0,v);};",
        "six-state passive-angle covariance",
    )
    source = one(
        source,
        "  passiveProfile:label=>ASM_PASSIVE_RF_B2_PROFILES[label]?{...ASM_PASSIVE_RF_B2_PROFILES[label]}:null,\n  truthOutput:false",
        "  passiveProfile:label=>ASM_PASSIVE_RF_B2_PROFILES[label]?{...ASM_PASSIVE_RF_B2_PROFILES[label]}:null,\n  singerDiagnostic:options=>asmCueSingerPredictDiagnosticA(options),\n  truthOutput:false",
        "read-only Singer diagnostic API",
    )
    return source


def transform_stage2(source: str) -> str:
    """Restrict passive RF to ship radars and apply the frozen band/beam model."""
    start_anchor = "// SEEKER_UNIFY_C Stage 3: anonymous passive-RF bearing/elevation measurements."
    end_anchor = "  function missileNavB2Init(m,force=false){"
    start = source.find(start_anchor)
    end = source.find(end_anchor, start)
    if start < 0 or end < 0:
        raise AssertionError("passive RF anchors missing")
    passive = (HERE / "cue_a_1_passive.js").read_text().rstrip() + "\n"
    source = source[:start] + passive + source[end:]
    source = one(
        source,
        "if(o.enabled.SPY&&spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:'S',power:2500,family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null});",
        "if(o.enabled.SPY&&spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:'S',frequencyMHz:Number.isFinite(p.sensors.spy1dv.frequencyMHz)?p.sensors.spy1dv.frequencyMHz:null,frequencyProvenance:Number.isFinite(p.sensors.spy1dv.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:2500,family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null});",
        "SPY passive emitter metadata",
    )
    source = one(
        source,
        "for(const [key,hp]of [['SPQ','spq9b'],['NAV','bridgeMasterE']])if(o.enabled[key]&&observerHealthC(r,p.geometry.hardpoints[hp].name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,p.geometry.hardpoints[hp]),band:key==='SPQ'?'IJ':electronicBandF(p.sensors.bridgeMasterE.band),power:key==='SPQ'?650:120,family:key==='SPQ'?'SURFACE SEARCH RADAR':'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',beamAz:r.navigation.heading+(own?(key==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[key]),double:key==='SPQ'});",
        "for(const [key,hp]of [['SPQ','spq9b'],['NAV','bridgeMasterE']]){const spec=p.sensors[hp];if(o.enabled[key]&&observerHealthC(r,p.geometry.hardpoints[hp].name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,p.geometry.hardpoints[hp]),band:key==='SPQ'?'IJ':electronicBandF(spec.band),frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:key==='SPQ'?650:120,family:key==='SPQ'?'SURFACE SEARCH RADAR':'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',beamAz:r.navigation.heading+(own?(key==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[key]),beamwidthDeg:key==='SPQ'?.6:spec.horizontalBeamwidthDeg,beamwidthProvenance:key==='SPQ'?'SIM_TUNED_EXISTING_OBSERVATION_MODEL':String(spec.performanceBasis||spec.source||'EXISTING_EMITTER_PROFILE'),rpm:Number(spec.rpm??spec.nominalRpm),double:key==='SPQ'});}",
        "rotating ship-radar passive metadata",
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
    parser.add_argument("--through", choices=("stage1a", "stage1b", "stage2"), default="stage1a")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError(f"baseline SHA mismatch: {sha(raw)}")
    before, match = unpack(raw)
    after_stage1a = transform_stage1a(before)
    after_stage1b = transform_stage1b(after_stage1a) if args.through in ("stage1b", "stage2") else None
    after = transform_stage2(after_stage1b) if args.through == "stage2" else (after_stage1b if args.through == "stage1b" else after_stage1a)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    if check != after:
        raise AssertionError("repacked main script mismatch")
    args.out.write_bytes(output)

    if args.through == "stage1a":
        diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="SEEKER_UNIFY_C/main.js", tofile="CUE_A_1_STAGE1A/main.js"))
        diff_path = HERE / "changes-stage1a.diff"
        receipt = args.receipt or HERE / "BUILD_STAGE1A.json"
    elif args.through == "stage1b":
        diff = "".join(difflib.unified_diff(after_stage1a.splitlines(True), after.splitlines(True), fromfile="CUE_A_1_STAGE1A/main.js", tofile="CUE_A_1_STAGE1B/main.js"))
        diff_path = HERE / "changes-stage1b-implementation.diff"
        receipt = args.receipt or HERE / "BUILD_STAGE1B_IMPLEMENTATION.json"
    else:
        diff = "".join(difflib.unified_diff(after_stage1b.splitlines(True), after.splitlines(True), fromfile="CUE_A_1_STAGE1B/main.js", tofile="CUE_A_1_STAGE2/main.js"))
        diff_path = HERE / "changes-stage2-implementation.diff"
        receipt = args.receipt or HERE / "BUILD_STAGE2_IMPLEMENTATION.json"
    # A unified diff uses a single-space prefix for an empty context line. This
    # artifact is for review rather than patch application, so remove only that
    # prefix to keep the repository whitespace audit clean.
    diff_path.write_text("".join("\n" if line == " \n" else line for line in diff.splitlines(True)))
    build = {
        "schema": {"stage1a": "AEGIS_CUE_A_1_BUILD_STAGE1A_1", "stage1b": "AEGIS_CUE_A_1_BUILD_STAGE1B_IMPLEMENTATION_1", "stage2": "AEGIS_CUE_A_1_BUILD_STAGE2_IMPLEMENTATION_1"}[args.through],
        "baselineCommit": "4faeb4e079b7baddcb1e1b8c1b892af804565938",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "through": args.through,
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "rangeFloors": {
            "ASM_WIP22": {"km": 0.5, "provenance": "LEGACY_EQUIVALENCE"},
            "SAM_ARH": {"km": 0.20, "provenance": "LEGACY_EQUIVALENCE"},
        },
        "singer": ({
            "stateOrder": ["px", "py", "vx", "vy", "ax", "ay"],
            "accelerationSigmaMps2": 0.3,
            "tauS": 60,
            "unknownVelocityAxisSigmaMps": 9,
            "velocityVarianceCapM2ps2": 81,
            "discretization": "VAN_LOAN_HIGHAM_PADE13",
            "constantsFrozenBeforeEffectTests": True,
        } if args.through in ("stage1b", "stage2") else None),
        "passiveRf": ({
            "allowedFamilies": ["SHIP SEARCH RADAR", "SURFACE SEARCH RADAR", "NAVIGATION RADAR"],
            "maxThreatMHz": [2000, 18000],
            "confirmedOnlyMHz": [8000, 12000],
            "bandCenterMHz": {"S": 3000, "IJ": 10000},
            "accuracyReferenceMHz": 10000,
            "rotatingBeam": "SWEPT_GAUSSIAN_MINUS_3DB_FULL_WIDTH",
            "constantsFrozenBeforeEffectTests": True,
        } if args.through == "stage2" else None),
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
    }
    if build["singer"] is None:
        del build["singer"]
    if build["passiveRf"] is None:
        del build["passiveRf"]
    receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
