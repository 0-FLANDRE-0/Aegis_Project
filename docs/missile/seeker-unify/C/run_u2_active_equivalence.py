#!/usr/bin/env python3
"""Stage 1 U2 ACTIVE representative-scene bit-equivalence gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = [
    "/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
    "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
    "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
    "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K",
]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def matrices() -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = {"ASM": [], "CUE": [], "SAM": []}
    seed = 910000
    for control, kind in (("TARGET", "DDG"), ("TARGET", "CG"), ("TARGET", "SOV"), ("CHAFF", "DDG"), ("NO_TARGET", "DDG")):
        for range_km in (10, 30, 50):
            for altitude_m in (15, 200):
                rows["ASM"].append({"seed": seed, "control": control, "kind": kind, "rangeKm": range_km, "altM": altitude_m, "speedKt": 15})
                seed += 1
    for label in ("Kh-35U", "Kh-32"):
        for range_km in (60, 130):
            for turn_deg in (0, 30, 90):
                rows["CUE"].append({"seed": seed, "label": label, "rangeKm": range_km, "speedKt": 30, "turnDeg": turn_deg, "emcon": False})
                seed += 1
    for path in ("ESSM_BLOCK2_AIR", "SM6_BLOCK_IA_AIR", "SM6_BLOCK_IA_SURFACE"):
        for target_kind in ("AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF"):
            for range_km in (10, 30, 50):
                rows["SAM"].append({"seed": seed, "path": path, "targetKind": target_kind, "rangeKm": range_km})
                seed += 1
    return rows


EXPRESSIONS = {
    "ASM": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))",
    "CUE": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))",
    "SAM": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runSamArhCase(o))",
}


def run_build(pw, path: Path, rows: dict[str, list[dict]], inspect_contract: bool) -> dict:
    body = path.read_bytes()
    browser = launch(pw)
    errors: list[str] = []
    output: dict[str, list] = {}
    for group, cases in rows.items():
        values = []
        for start in range(0, len(cases), 12):
            page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            values.extend(page.evaluate(EXPRESSIONS[group], cases[start:start + 12]))
            page.close()
        output[group] = values
    contract = None
    if inspect_contract:
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        contract = page.evaluate("""()=>{const a=window.__SEEKER_COMMON_U2__;if(!a)return null;const snap=a.snapshot();return {
          schema:a.schema,mode:a.mode,profileOptions:a.profileOptions,activeComponents:a.activeComponents,shadowComponents:a.shadowComponents,
          tacticalOutputUsed:a.tacticalOutputUsed,rngConsumed:a.rngConsumed,truthOutput:a.truthOutput,snapshot:snap,
          dynamicAuditArrays:Object.entries(a).filter(([k,v])=>Array.isArray(v)&&!['activeComponents','shadowComponents'].includes(k)).map(([k])=>k)
        };}""")
        page.close()
    browser.close()
    return {"sha256": hashlib.sha256(body).hexdigest(), "groups": output, "contract": contract, "pageErrors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = matrices()
    started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_build(pw, args.baseline, rows, False)
        candidate = run_build(pw, args.candidate, rows, True)
    differences = {
        group: [
            {"index": index, "baseline": before, "candidate": after}
            for index, (before, after) in enumerate(zip(baseline["groups"][group], candidate["groups"][group]))
            if before != after
        ]
        for group in rows
    }
    differences = {key: value for key, value in differences.items() if value}
    contract = candidate["contract"]
    contract_ok = bool(
        contract
        and contract["mode"] == "ACTIVE"
        and contract["activeComponents"] == ["synthesizeEchoes", "resolveCells"]
        and contract["shadowComponents"] == []
        and contract["tacticalOutputUsed"] is True
        and contract["rngConsumed"] is False
        and contract["truthOutput"] is False
        and contract["dynamicAuditArrays"] == []
        and contract["snapshot"]["shadowComputations"] == 0
        and contract["snapshot"]["auditArrayCount"] == 0
    )
    status = "PASS" if not differences and not baseline["pageErrors"] and not candidate["pageErrors"] and contract_ok else "FAIL"
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_U2_ACTIVE_EQUIVALENCE_1",
        "status": status,
        "elapsedS": time.monotonic() - started,
        "caseCounts": {key: len(value) for key, value in rows.items()},
        "totalCases": sum(map(len, rows.values())),
        "bitEqual": not differences,
        "differences": differences,
        "pageErrors": {"baseline": baseline["pageErrors"], "candidate": candidate["pageErrors"]},
        "activeContract": contract,
        "contractPass": contract_ok,
        "inputs": {"baselineSha256": baseline["sha256"], "candidateSha256": candidate["sha256"]},
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "elapsedS", "caseCounts", "totalCases", "bitEqual", "differences", "pageErrors", "activeContract", "contractPass")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()

