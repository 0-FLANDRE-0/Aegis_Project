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
    parser.add_argument("--through", choices=("A",), default="A")
    parser.add_argument("--a-mode", choices=("SHADOW", "ACTIVE"), default="ACTIVE")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--diff-path", type=Path)
    args = parser.parse_args()

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError(f"baseline SHA mismatch: {sha(raw)}")
    before, match = unpack(raw)
    after = transform_a(before, args.a_mode)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    if check != after:
        raise AssertionError("repacked main script mismatch")
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="CUE_A_1/main.js", tofile=f"SEEKER_UNIFY_U3_A_{args.a_mode}/main.js"))
    diff_path = args.diff_path or HERE / f"changes-A-{args.a_mode.lower()}.diff"
    diff_path.write_text("".join("\n" if line == " \n" else line for line in diff.splitlines(True)))
    receipt = args.receipt or HERE / f"BUILD_A_{args.a_mode}.json"
    build = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_BUILD_A_1",
        "baselineCommit": "be19f46794705a18bfd69feba99d7a4b00dd4a0c",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "through": args.through,
        "harpoonU2Mode": args.a_mode,
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
        "gameplayConstantsAdded": 0,
        "rngContract": "HARPOON_EXISTING_CALL_ORDER_UNCHANGED_COMMON_LAYER_CONSUMES_ZERO",
        "truthOutput": False,
    }
    receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
