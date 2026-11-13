#!/usr/bin/env python3
"""Offline reconciliation of raw broad and zero-execution recovery receipts."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> None:
    raw = json.loads((HERE / "FINAL_REGRESSION_RAW.json").read_text())
    recovery = json.loads((HERE / "ZERO_EXECUTION_RECOVERY.json").read_text())
    recovered = {row["suite"]: row for row in recovery["recoveredSuites"]}
    rows = []
    for row in raw["rows"]:
        if row["status"] == "PASS":
            if row["suite"] in recovered:
                raise AssertionError(f"executed PASS suite was repeated: {row['suite']}")
            rows.append({**row, "rawStatus": "PASS", "effectiveStatus": "PASS", "evidenceSource": "RAW_ONE_SHOT_BROAD"})
            continue
        if row["executedAssertions"] != 0 or row.get("resultPath") is not None:
            raise AssertionError(f"nonzero raw failure cannot be recovered: {row['suite']}")
        replacement = recovered.pop(row["suite"], None)
        if replacement is None:
            raise AssertionError(f"missing recovery: {row['suite']}")
        rows.append({**replacement, "rawStatus": "FAIL_PRE_BROWSER_ZERO_EXECUTION", "effectiveStatus": replacement["status"], "evidenceSource": "ZERO_EXECUTION_FIRST_ACTUAL_RUN", "rawWallS": row["wallS"]})
    if recovered:
        raise AssertionError(f"unexpected recovery suites: {sorted(recovered)}")
    failures = [row["suite"] for row in rows if row["effectiveStatus"] != "PASS"]
    result = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_REGRESSION_EFFECTIVE_1",
        "candidate": raw["candidate"], "candidateSha256": raw["candidateSha256"], "candidateBytes": raw["candidateBytes"],
        "threatAssumptionMode": raw["threatAssumptionMode"],
        "rawBroad": {"runCount": 1, "receipt": "FINAL_REGRESSION_RAW.json", "wallS": raw["wallS"], "passedAssertions": sum(row["passedAssertions"] for row in raw["rows"]), "executedAssertions": sum(row["executedAssertions"] for row in raw["rows"]), "preBrowserZeroExecutionSuites": [row["suite"] for row in raw["rows"] if row["status"] != "PASS"]},
        "recovery": {"broadRerun": False, "receipt": "ZERO_EXECUTION_RECOVERY.json", "reason": recovery["reason"], "wallS": recovery["wallS"], "passedAssertions": sum(row["passedAssertions"] for row in recovery["recoveredSuites"]), "executedAssertions": sum(row["executedAssertions"] for row in recovery["recoveredSuites"])},
        "rows": rows,
        "totalAssertions": sum(row["executedAssertions"] for row in rows),
        "passedAssertions": sum(row["passedAssertions"] for row in rows),
        "effectiveFailures": failures,
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "candidateMutatedAfterFreeze": False,
        "confirmedOnlyPerformance": "UNVERIFIED",
        "complete": True,
        "release": False,
    }
    (HERE / "FINAL_REGRESSION_EFFECTIVE.json").write_text(strict(result))
    d_gate = {
        "schema": "AEGIS_INTEGRATION_BASELINE_GATE_A_1", "commit": "D", "status": "PASS" if not failures else "FAIL",
        "candidateSha256": raw["candidateSha256"], "rawBroadRunCount": 1, "rawBroadRerun": False,
        "rawBroadPassedAssertions": result["rawBroad"]["passedAssertions"], "zeroExecutionRecoveryPassedAssertions": result["recovery"]["passedAssertions"],
        "effectiveAssertions": result["totalAssertions"], "effectivePassed": result["passedAssertions"], "effectiveFailures": failures,
        "expectedValuesUpdated": False, "tolerancesChanged": False, "release": False,
    }
    (HERE / "D_GATE.json").write_text(strict(d_gate))


if __name__ == "__main__":
    main()
