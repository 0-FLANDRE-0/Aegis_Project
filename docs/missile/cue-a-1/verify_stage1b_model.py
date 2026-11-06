#!/usr/bin/env python3
"""Verify Singer dt-independence, fixed-tick tables, bounds, and cap references."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HARNESS_ROOT = Path("/workspace/aegis-ui-a")
sys.path[:0] = [
    str(HARNESS_ROOT / "docs/pip/B"),
    str(HARNESS_ROOT / "docs/helicopter/H"),
    str(HARNESS_ROOT / "docs/multiship/G"),
    str(HARNESS_ROOT / "docs/bunkerhill/K"),
]
import browser_backend

browser_backend.install()
from browser_i import launch, load


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html")
    parser.add_argument("--diagnostic", type=Path, default=Path("/dev/shm/cue-a1-stage1b-diag.html"))
    parser.add_argument("--out", type=Path, default=HERE / "CUE_FILTER_SINGER_MODEL.json")
    args = parser.parse_args()
    started = time.monotonic()
    options = [
        {"label": label, "known": known, "seconds": seconds, "rangeM": 100000, "speedMps": 15}
        for label in ("Kh-35U", "Kh-32") for known in (False, True) for seconds in (60, 120, 180)
    ]
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, args.diagnostic.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        payload = page.evaluate(
            """options=>{
              const api=window.__ASM_CUE_A__,pure=(velocitySigmaMps,stepS)=>api.singerDiagnostic({positionSigmaM:300,velocitySigmaMps,accelerationSigmaMps2:.3,durationS:180,stepS});
              const rows=window.__CUE_A1_STAGE1B_DIAG__.runDeterministicBatch(options),repeat=window.__CUE_A1_STAGE1B_DIAG__.runDeterministicBatch(options);
              return {core:[...(window.__CORE_SELFTEST_FAILURES__??[])],spec:api.spec,
                dt:{one0:pure(0,180),tick0:pure(0,1/60),one9:pure(9,180),tick9:pure(9,1/60)},
                rows,repeat,capReference:window.__CUE_A1_STAGE1B_DIAG__.runCapReferenceCase()};
            }""",
            options,
        )
        page.close()
        browser.close()
    dt = payload["dt"]
    rel0 = abs(dt["one0"]["positionSigmaM"] - dt["tick0"]["positionSigmaM"]) / dt["one0"]["positionSigmaM"]
    rel9 = abs(dt["one9"]["positionSigmaM"] - dt["tick9"]["positionSigmaM"]) / dt["one9"]["positionSigmaM"]
    cap = payload["capReference"]
    checks = {
        "corePass": not payload["core"],
        "pageErrorsZero": not errors,
        "zeroVelocityAnchor3529_28": abs(dt["one0"]["positionSigmaM"] - 3529.28) <= 0.01,
        "unknownVelocityAnchor3883_33": abs(dt["one9"]["positionSigmaM"] - 3883.33) <= 0.01,
        "zeroVelocityDtRelativeErrorLe1e6": rel0 <= 1e-6,
        "unknownVelocityDtRelativeErrorLe1e6": rel9 <= 1e-6,
        "fixedTickCaseCount12": len(payload["rows"]) == 12,
        "velocityVarianceCapped81": all(row["final"]["covariance"][14] <= 81.000000001 and row["final"]["covariance"][21] <= 81.000000001 for row in payload["rows"]),
        "capFormulaExact": all(abs(row["basket"]["capM"] - (18 * row["setup"]["seconds"] + 900)) <= 1e-7 for row in payload["rows"]),
        "deterministicExact": payload["rows"] == payload["repeat"],
        "passiveDoesNotMoveCapReference": cap["initial"]["capRefTimeS"] == cap["passive"]["capRefTimeS"] and cap["initial"]["capRefSigmaM"] == cap["passive"]["capRefSigmaM"],
        "dlPositionMovesCapReference": cap["dl"]["capRefTimeS"] == 10 and cap["dl"]["capRefSigmaM"] == 75,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_SINGER_MODEL_RESULTS_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "input": str(args.html),
        "inputSha256": hashlib.sha256(args.html.read_bytes()).hexdigest(),
        "diagnostic": str(args.diagnostic),
        "diagnosticSha256": hashlib.sha256(args.diagnostic.read_bytes()).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "checks": checks,
        "relativeErrors": {"velocitySigma0": rel0, "velocitySigma9": rel9},
        "dt": dt,
        "velocityTable": payload["rows"],
        "capReference": cap,
        "spec": payload["spec"],
        "pageErrors": errors,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "relativeErrors": result["relativeErrors"], "elapsedS": result["elapsedS"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
