#!/usr/bin/env python3
"""Build SEEKER_UNIFY_B from the pinned SEEKER_UNIFY_A product.

U0 can be built in SHADOW mode (legacy gate remains authoritative while both
gates are counted) or ACTIVE mode.  The committed product is ACTIVE only after
the U0 gates pass.  Later U1/U2 transformations are appended in this same
single-pass builder so every anchor remains pinned and auditable.
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
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html"
BASE_SHA = "53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8"


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


def transform_u0(source: str, mode: str) -> str:
    mode = mode.upper()
    if mode not in {"SHADOW", "ACTIVE"}:
        raise ValueError(mode)

    target_cue = f"""// SEEKER_UNIFY_B U0: cue uncertainty grows only from information age.
// These are the three frozen SIM_TUNED constants committed before effect tests;
// no target truth, target identity, target profile, or target velocity is read.
const ASM_CUE_BASKET_U0=Object.freeze({{
  schema:'AEGIS_ASM_CUE_BASKET_U0_1',source:'SIM_TUNED',resultFitting:false,
  assumedMaxTargetSpeedMps:18.0,minAcqRangeFloorM:1500,minAcqRangeFrac:0.5,
  mode:'{mode}'
}});
function asmTargetCueStateU0(em){{
  // em.life is missile age, hence launch is time zero in this clock domain.
  return em._targetCueU0??(em._targetCueU0={{schema:'AEGIS_TARGET_CUE_U0_1',rangeRefTimeS:0,bearingRefTimeS:0,source:'LAUNCH',passiveCorrectionAttempts:0,passiveBearingClockUpdates:0}});
}}
function asmTargetCueU0(em){{
  const q=asmTargetCueStateU0(em);
  return {{positionM:{{x:worldToMeters(em.insTgtX),y:worldToMeters(em.insTgtY),z:ASM_SEEKER_PROFILES[em.label]?.aimHeightM??5}},velocityMps:null,
    rangeRefTimeS:q.rangeRefTimeS,bearingRefTimeS:q.bearingRefTimeS,source:q.source}};
}}
function asmTargetCuePassiveBearingUpdateU0(em,measurement,profile,correctedBearingRad){{
  const q=asmTargetCueStateU0(em);q.passiveCorrectionAttempts++;
  const sigma=Math.max(1e-9,Number(profile?.bearingErrorRad)||0),residual=Math.abs(angNorm(measurement.bearingRad-correctedBearingRad));
  q.lastPassiveBearingResidualRad=residual;q.lastPassiveBearingConverged=residual<=3*sigma;
  if(q.lastPassiveBearingConverged){{q.bearingRefTimeS=Math.max(0,Number(em.life)||0);q.source='PASSIVE_BEARING';q.passiveBearingClockUpdates++;}}
  return q.lastPassiveBearingConverged;
}}
function asmCueBasketU0(em,own,p){{
  const cue=asmTargetCueU0(em),now=Math.max(0,Number(em.life)||0),rangeAgeS=Math.max(0,now-cue.rangeRefTimeS),bearingAgeS=Math.max(0,now-cue.bearingRefTimeS);
  const dx=cue.positionM.x-worldToMeters(own.x),dy=cue.positionM.y-worldToMeters(own.y),dz=cue.positionM.z-(own.z??0),rangeM=Math.max(1,Math.hypot(dx,dy,dz)),horizontalM=Math.max(1,Math.hypot(dx,dy));
  const rangeUncertaintyM=ASM_CUE_BASKET_U0.assumedMaxTargetSpeedMps*rangeAgeS,bearingUncertaintyM=ASM_CUE_BASKET_U0.assumedMaxTargetSpeedMps*bearingAgeS,rangeHalfM=Math.max(1200,.12*rangeM,rangeUncertaintyM);
  return {{cue,rangeM,azRad:Math.atan2(dy,dx),elRad:Math.atan2(dz,horizontalM),rangeLowM:Math.max(rangeM-rangeHalfM,ASM_CUE_BASKET_U0.minAcqRangeFloorM,ASM_CUE_BASKET_U0.minAcqRangeFrac*rangeM),rangeHighM:rangeM+rangeHalfM,azHalfRad:Math.max(deg(5),Math.atan(bearingUncertaintyM/Math.max(rangeM,1))),elHalfRad:deg(4),rangeAgeS,bearingAgeS}};
}}
"""
    source = one(
        source,
        "function createAsmSeekerState(label){",
        target_cue + "function createAsmSeekerState(label){",
        "U0 TargetCue and frozen basket insertion",
    )
    source = one(
        source,
        "      deception:null,hoj:null};",
        "      lastCueBasketU0:null,cueLegacyPassCountU0:0,cueExpandedPassCountU0:0,cueExpandedOnlyCountU0:0,\n      deception:null,hoj:null};",
        "U0 seeker diagnostics",
    )

    old_association = """    if(!s._kfX){
      const dx=worldToMeters(em.insTgtX-own.x),dy=worldToMeters(em.insTgtY-own.y),dz=(p.aimHeightM??5)-(own.z??0),cueRange=Math.max(1,Math.hypot(dx,dy,dz)),cueAz=Math.atan2(dy,dx),cueEl=Math.atan2(dz,Math.max(1,Math.hypot(dx,dy)));
      for(const m of measurements){const evidence=clamp(Number(m.targetEvidence)||0,0,1);if(!arhRfCandidateAcceptedWip13B12(s.mode,evidence)){s.lastRejectedLowEvidence++;s.lowEvidenceRejectTotal=(s.lowEvidenceRejectTotal??0)+1;continue;}s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),cueRangeScaleM=Math.max(1200,cueRange*.12),cueAzScaleRad=deg(5),cueElScaleRad=deg(4);
        // ASM_SEEKER_A: before an EKF exists, the launch cue is an acquisition
        // basket, not merely a soft score. Reuse the existing residual scales;
        // no RF/Pd/noise/beam/gimbal or guidance coefficient changes.
        if(rangeErr>cueRangeScaleM||azErr>cueAzScaleRad||elErr>cueElScaleRad)continue;
        const score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/cueRangeScaleM,0,4)-5*clamp(azErr/cueAzScaleRad,0,4)-3*clamp(elErr/cueElScaleRad,0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});}
"""
    new_association = """    if(!s._kfX){
      const basket=asmCueBasketU0(em,own,p),cueRange=basket.rangeM,cueAz=basket.azRad,cueEl=basket.elRad;
      s.lastCueBasketU0={rangeLowM:basket.rangeLowM,rangeHighM:basket.rangeHighM,azHalfDeg:basket.azHalfRad*180/Math.PI,rangeAgeS:basket.rangeAgeS,bearingAgeS:basket.bearingAgeS,source:basket.cue.source};
      for(const m of measurements){const evidence=clamp(Number(m.targetEvidence)||0,0,1);if(!arhRfCandidateAcceptedWip13B12(s.mode,evidence)){s.lastRejectedLowEvidence++;s.lowEvidenceRejectTotal=(s.lowEvidenceRejectTotal??0)+1;continue;}s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),cueRangeScaleM=Math.max(1200,cueRange*.12),cueAzScaleRad=deg(5),cueElScaleRad=deg(4);
        // U0 changes only the hard pre-EKF basket. Legacy scales below remain
        // authoritative for scoring, preserving score ordering and RNG use.
        const legacyPass=rangeErr<=cueRangeScaleM&&azErr<=cueAzScaleRad&&elErr<=cueElScaleRad,expandedPass=m.rangeM>=basket.rangeLowM&&m.rangeM<=basket.rangeHighM&&azErr<=basket.azHalfRad&&elErr<=basket.elHalfRad;
        if(legacyPass)s.cueLegacyPassCountU0++;if(expandedPass)s.cueExpandedPassCountU0++;if(expandedPass&&!legacyPass)s.cueExpandedOnlyCountU0++;
        if((ASM_CUE_BASKET_U0.mode==='ACTIVE'?!expandedPass:!legacyPass))continue;
        const score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/cueRangeScaleM,0,4)-5*clamp(azErr/cueAzScaleRad,0,4)-3*clamp(elErr/cueElScaleRad,0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});}
"""
    source = one(source, old_association, new_association, "U0 pre-EKF basket")

    old_passive = """    const r=Math.hypot(dx,dy),az=Math.atan2(dy,dx),corrected=az+angNorm(meas.bearingRad-az)*p.correctionGain*meas.confidence*dt;
    em.insTgtX=o.x+Math.cos(corrected)*r;em.insTgtY=o.y+Math.sin(corrected)*r;return true;"""
    new_passive = """    const r=Math.hypot(dx,dy),az=Math.atan2(dy,dx),corrected=az+angNorm(meas.bearingRad-az)*p.correctionGain*meas.confidence*dt;
    em.insTgtX=o.x+Math.cos(corrected)*r;em.insTgtY=o.y+Math.sin(corrected)*r;asmTargetCuePassiveBearingUpdateU0(em,meas,p,corrected);return true;"""
    source = one(source, old_passive, new_passive, "U0 passive bearing clock")
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
    parser.add_argument("--mode", choices=("SHADOW", "ACTIVE"), default="ACTIVE")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path, default=HERE / "BUILD.json")
    args = parser.parse_args()

    raw = BASE.read_bytes()
    assert sha(raw) == BASE_SHA
    before, match = unpack(raw)
    after = transform_u0(before, args.mode)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    assert check == after
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="SEEKER_UNIFY_A/main.js", tofile="SEEKER_UNIFY_B/main.js"))
    if args.mode == "ACTIVE":
        (HERE / "changes.diff").write_text(diff)
    build = {
        "schema": "AEGIS_SEEKER_UNIFY_B_BUILD_1",
        "baselineCommit": "ba9bc114485838b52450164d5af026fd3d8f5e88",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "mode": args.mode,
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
        "u0Constants": json.loads((HERE / "U0_FROZEN_CONSTANTS.json").read_text()),
    }
    args.receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
