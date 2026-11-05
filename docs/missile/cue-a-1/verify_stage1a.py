#!/usr/bin/env python3
"""Verify the profile-specific seeker range floor without broad regression."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCOPE_TOOL = ROOT / "docs/missile/seeker-unify/C/verify_stage3_scope.py"


def unpack(path: Path) -> str:
    raw = path.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script not found")
    return gzip.decompress(base64.b64decode(match[1])).decode()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def load_scope_tool():
    spec = importlib.util.spec_from_file_location("cue_a_1_scope_tool", SCOPE_TOOL)
    if not spec or not spec.loader:
        raise RuntimeError("scope tool unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def browser_rows(path: Path, cases: list[dict]) -> dict:
    harness_root = Path("/workspace/aegis-ui-a")
    sys.path.insert(0, str(harness_root / "docs/multiship/G"))
    from browser_g import launch, load_fleet

    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = launch(playwright)
        page = load_fleet(browser, path.read_bytes(), own="DDG_119_LATE_FLIGHT_IIA", ally=None, enemy=None, errors=errors)
        result = page.evaluate(
            """cases=>{
              const bits=value=>{const b=new ArrayBuffer(8),v=new DataView(b);v.setFloat64(0,value,false);return v.getBigUint64(0,false).toString(16).padStart(16,'0');};
              const api=window.__SEEKER_COMMON_U2__;
              return {core:[...(window.__CORE_SELFTEST_FAILURES__??[])],options:JSON.parse(JSON.stringify(api.profileOptions)),rows:cases.map(row=>{const value=api.synthesizeMonostaticPower(row.family,row.q);return {...row,value,bits:bits(value)};})};
            }""",
            cases,
        )
        page.close()
        browser.close()
    result["errors"] = errors
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html")
    parser.add_argument("--candidate", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html")
    args = parser.parse_args()

    ranges = (0.05, 0.10, 0.19, 0.20, 0.25, 0.49, 0.50, 0.75, 1.0, 5.0, 60.0, 130.0)
    templates = (
        {"rcsM2": 1.3, "referenceRcsM2": 2.1, "referenceRangeKm": 35, "txGain": 0.7, "rxGain": 0.8, "losTxQ": 0.9, "losRxQ": 0.85, "envQ": 0.75},
        {"rcsM2": 0.2, "referenceRcsM2": 1.0, "referenceRangeKm": 10, "txGain": 0.08, "rxGain": 0.12, "losTxQ": 0.3, "losRxQ": 0.4, "envQ": 0.2},
    )
    cases = [
        {"id": f"{family}-{template_index}-{range_km}", "family": family, "rangeKm": range_km, "q": {**template, "rangeKm": range_km}}
        for family in ("SAM_ARH", "ASM_WIP22")
        for template_index, template in enumerate(templates)
        for range_km in ranges
    ]
    before_runtime = browser_rows(args.baseline, cases)
    after_runtime = browser_rows(args.candidate, cases)
    before_by_id = {row["id"]: row for row in before_runtime["rows"]}
    after_by_id = {row["id"]: row for row in after_runtime["rows"]}
    rows = []
    for case in cases:
        before = before_by_id[case["id"]]
        after = after_by_id[case["id"]]
        bit_equal = before["bits"] == after["bits"]
        expected_equal = case["family"] == "SAM_ARH" or case["rangeKm"] >= 0.5
        rows.append({
            "id": case["id"],
            "family": case["family"],
            "rangeKm": case["rangeKm"],
            "before": before["value"],
            "after": after["value"],
            "beforeBits": before["bits"],
            "afterBits": after["bits"],
            "bitEqual": bit_equal,
            "expectedEqual": expected_equal,
            "pass": bit_equal == expected_equal,
        })

    before_source, after_source = unpack(args.baseline), unpack(args.candidate)
    scope = load_scope_tool()
    changed_function = "seekerSynthesizeMonostaticPowerU2"
    protected = (
        "_arhNormalizedMonostaticPower",
        "asmSeekerCompositeReturns",
        "updateAsmSeeker",
        "buildEssmArhEchoPool",
        "arhRfTargetEvidenceWip13B12",
        "arhRfCandidateAcceptedWip13B12",
        "seekerResolveCellsU2",
        "seekerResolvedCellStatisticsU2",
    )
    changed_before = scope.function_source(before_source, changed_function)
    changed_after = scope.function_source(after_source, changed_function)
    protected_rows = [
        {
            "name": name,
            "beforeSha256": sha_text(scope.function_source(before_source, name)),
            "afterSha256": sha_text(scope.function_source(after_source, name)),
            "byteEqual": scope.function_source(before_source, name) == scope.function_source(after_source, name),
        }
        for name in protected
    ]
    reverted = after_source.replace(
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08,rangeFloorKm:.5,rangeFloorProvenance:'LEGACY_EQUIVALENCE'}),",
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08}),",
        1,
    ).replace(
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING',rangeFloorKm:.20,rangeFloorProvenance:'LEGACY_EQUIVALENCE'})",
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING'})",
        1,
    ).replace(
        "*Math.pow(q.referenceRangeKm/Math.max(option.rangeFloorKm,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        "*Math.pow(q.referenceRangeKm/Math.max(.20,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        1,
    )
    options = after_runtime["options"]
    checks = {
        "baselineCorePass": not before_runtime["core"],
        "candidateCorePass": not after_runtime["core"],
        "pageErrorsZero": not before_runtime["errors"] and not after_runtime["errors"],
        "samAllBitExact": all(row["bitEqual"] for row in rows if row["family"] == "SAM_ARH"),
        "asmAtOrAboveHalfKmBitExact": all(row["bitEqual"] for row in rows if row["family"] == "ASM_WIP22" and row["rangeKm"] >= 0.5),
        "asmDifferencesOnlyBelowHalfKm": all(row["pass"] for row in rows),
        "asmBelowHalfKmActuallyChanged": any(not row["bitEqual"] for row in rows if row["family"] == "ASM_WIP22" and row["rangeKm"] < 0.5),
        "profileFloorsAndProvenanceExact": options["ASM_WIP22"].get("rangeFloorKm") == 0.5
        and options["SAM_ARH"].get("rangeFloorKm") == 0.2
        and options["ASM_WIP22"].get("rangeFloorProvenance") == options["SAM_ARH"].get("rangeFloorProvenance") == "LEGACY_EQUIVALENCE",
        "synthesisFunctionChanged": changed_before != changed_after,
        "protectedFunctionsByteEqual": all(row["byteEqual"] for row in protected_rows),
        "revertingThreeIntendedEditsRestoresMainExactly": reverted == before_source,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE1A_RANGE_FLOOR_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "caseCounts": {"SAM_ARH": 24, "ASM_WIP22": 24},
        "rows": rows,
        "function": {
            "name": changed_function,
            "beforeSha256": sha_text(changed_before),
            "afterSha256": sha_text(changed_after),
        },
        "protectedFunctions": protected_rows,
        "options": options,
        "errors": {"baseline": before_runtime["errors"], "candidate": after_runtime["errors"]},
    }
    (HERE / "RANGE_FLOOR_STAGE1A.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "caseCounts": result["caseCounts"]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
