#!/usr/bin/env python3
"""Fail-closed static candidate gate for the final ESM_A product."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_ESM_A.html"
PRODUCT_SHA = "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7"
PRODUCT_BYTES = 22_182_527


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "AEGIS_CURRENT_PRODUCT.json").read_text())
    build = json.loads((HERE / "BUILD_E.json").read_text())
    final = json.loads((HERE / "FINAL_REGRESSION_CORRECTED.json").read_text())
    gates = {
        name: json.loads((HERE / filename).read_text())
        for name, filename in {
            "B": "B_GATE.json",
            "C": "C_GATE.json",
            "D": "D_GATE.json",
            "D_PREDECESSOR": "D_PREDECESSOR_RECHECK.json",
            "E": "E_GATE.json",
        }.items()
    }
    product_text = PRODUCT.read_text(errors="ignore")
    paired = next((row for row in final.get("rows", []) if row.get("suite") == "paired-compatibility"), {})
    current_emcon = next((row for row in final.get("rows", []) if row.get("suite") == "current-emcon-ui"), {})
    checks = {
        "manifestStage": manifest.get("stage") == "ESM_A",
        "manifestProduct": manifest.get("path") == PRODUCT.name,
        "manifestSha": manifest.get("sha256") == PRODUCT_SHA,
        "manifestBytes": manifest.get("bytes") == PRODUCT_BYTES,
        "productSha": digest(PRODUCT) == PRODUCT_SHA,
        "productBytes": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "buildReceipt": build.get("outputSha256") == PRODUCT_SHA and build.get("outputBytes") == PRODUCT_BYTES,
        "sourceModules": all(digest(HERE / name) == expected for name, expected in build.get("sourceModules", {}).items()),
        "protectedFunctions": all(row.get("same") is True for row in build.get("unchangedFunctions", {}).values()),
        "limitedGates": all(gate.get("status") == "PASS" for gate in gates.values()),
        "eGateCandidate": gates["E"].get("inputs", {}).get("productSha256") == PRODUCT_SHA,
        "truthAuthority": gates["E"].get("checks", {}).get("truthAndAuthorityZero") is True,
        "saveLifecycle": gates["E"].get("checks", {}).get("saveLifecyclePass") is True,
        "sovInactive": gates["E"].get("checks", {}).get("sovCandidatePass") is True
        and gates["E"].get("checks", {}).get("sovBaselineExact") is True,
        "finalBroadComplete": final.get("complete") is True and not final.get("effectiveFailures"),
        "finalBroadCandidate": final.get("candidateSha256") == PRODUCT_SHA,
        "finalBroadOneRun": final.get("replacementBroadRun", {}).get("runCount") == 1,
        "native364": final.get("native13", {}).get("passedAssertions") == 364,
        "approvedSchemaDelta": paired.get("status") == "APPROVED_SCHEMA_DELTA"
        and paired.get("rawPassedAssertions") == 36
        and paired.get("effectivePassedAssertions") == 42,
        "currentEmconUi14": current_emcon.get("status") == "PASS"
        and current_emcon.get("rawPassedAssertions") == 14,
        "expectationsUnchanged": final.get("expectedValuesUpdated") is False,
        "tolerancesUnchanged": final.get("tolerancesChanged") is False,
        "diagnosticAdaptersAbsent": "__ESM_A_E_DIAG__" not in product_text
        and "__ESM_A_E_BASELINE__" not in product_text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema": "AEGIS_ESM_A_CANDIDATE_STATIC_1",
        "status": "PASS" if not failed else "FAIL",
        "candidate": PRODUCT.name,
        "candidateSha256": PRODUCT_SHA,
        "checks": checks,
        "failed": failed,
        "release": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
