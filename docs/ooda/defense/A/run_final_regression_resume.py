#!/usr/bin/env python3
"""Resume the interrupted DEFENSE_OODA_A one-shot broad regression.

Completed suites are verified from their receipts and are never executed again.
The raw paired-integration failure remains FAIL; its section 9.4 classification
is a separate effective release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNNER = HERE / "run_final_regression.py"
spec = importlib.util.spec_from_file_location("defense_final_runner", RUNNER)
stage = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(stage)

OUT = stage.OUT
SUMMARY = stage.SUMMARY
STOP_RECEIPT = HERE / "FINAL_REGRESSION_STOP_AFTER_PAIRED.json"
CLASSIFICATION = HERE / "evidence/active-delta/PAIRED_ACTIVE_DELTA_CLASSIFICATION.json"
TERMINAL = HERE / "evidence/active-terminal/NATURAL_TERMINAL_GATE.json"
COMPLETED = ["static-integrity", *stage.NATIVE, "paired-integration"]
REMAINING = ["paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes", "hp-contract", "seeker-close"]
EXPECTED_PAIRED_FAILURES = {
    f"{profile}:raid:{check}"
    for profile in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")
    for check in ("samePhysicalState", "sameCombatRng", "raidInventoryDeltaBounded", "sameExistingObserverState")
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def receipt(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": sha256(raw)}


def existing_summary() -> dict:
    value = json.loads(SUMMARY.read_text())
    assert value["schema"] == "AEGIS_DEFENSE_OODA_A_FINAL_REGRESSION_1"
    assert value["candidateSha256"] == stage.PRODUCT_SHA256
    assert value["complete"] is False
    assert [row["suite"] for row in value["rows"]] == COMPLETED
    return value


def remaining_outputs() -> list[str]:
    paths: list[Path] = []
    for name in REMAINING:
        result, _expected = stage.result_location(name)
        paths.extend([OUT / f"{name}.log", OUT / f"{name}-execution.json", result])
        if name not in {"ui213"}:
            paths.append(OUT / name)
    return sorted({str(path.relative_to(ROOT)) for path in paths if path.exists()})


def preflight() -> tuple[dict, dict]:
    previous = existing_summary()
    classification = json.loads(CLASSIFICATION.read_text())
    terminal = json.loads(TERMINAL.read_text())
    rows = previous["rows"]
    paired = rows[-1]
    original_preflight = json.loads((OUT / "preflight-inputs.json").read_text())
    existing_receipts: list[dict] = []
    for row in rows:
        result = OUT / row["resultPath"]
        assert result.is_file(), f"missing completed result {result}"
        existing_receipts.append(receipt(result))
        if row["suite"] != "static-integrity":
            execution = OUT / f"{row['suite']}-execution.json"
            log = OUT / f"{row['suite']}.log"
            assert execution.is_file() and log.is_file()
            existing_receipts.extend([receipt(execution), receipt(log)])
    expected_remaining = sum(stage.result_location(name)[1] for name in REMAINING)
    checks = {
        "branchExact": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == "defense-ooda-a",
        "candidatePinned": stage.PRODUCT.stat().st_size == stage.PRODUCT_BYTES and sha256(stage.PRODUCT.read_bytes()) == stage.PRODUCT_SHA256,
        "baselinePinned": stage.BASELINE.stat().st_size == stage.BASELINE_BYTES and sha256(stage.BASELINE.read_bytes()) == stage.BASELINE_SHA256,
        "originalPreflightPass": bool(original_preflight.get("checks")) and all(original_preflight["checks"].values()),
        "completedOrderExact": [row["suite"] for row in rows] == COMPLETED,
        "native13Pass": all(row["status"] == "PASS" for row in rows if row["suite"] in stage.NATIVE),
        "nativeAssertions364": sum(row["executedAssertions"] for row in rows if row["suite"] in stage.NATIVE) == 364,
        "pairedRawFailurePreserved": paired["status"] == "FAIL" and set(paired["failedAssertions"]) == EXPECTED_PAIRED_FAILURES and paired["errors"] == [],
        "pairedClassificationPass": classification.get("classification") == "EXPECTED_ACTIVE_DIAGNOSTIC_DELTA" and classification.get("effectiveReleaseGate") == "PASS" and all(classification.get("checks", {}).values()),
        "naturalTerminalPass": terminal.get("pass") is True and all(terminal.get("checks", {}).values()),
        "remainingSuiteCount": len(REMAINING) == 7,
        "remainingAssertions362": expected_remaining == 362,
        "remainingOutputsUnused": not remaining_outputs(),
        "expectationsUntouched": classification.get("expectationsUpdated") is False,
        "tolerancesUntouched": classification.get("tolerancesChanged") is False,
        "gameConstantsUntouched": classification.get("gameConstantsChanged") is False,
    }
    missing = [key for key, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_FINAL_RESUME_PREFLIGHT_1",
        "checks": checks,
        "failed": missing,
        "continuationOfRunCount": 1,
        "completedSuitesNotRerun": COMPLETED,
        "remainingSuites": REMAINING,
        "remainingExpectedAssertions": expected_remaining,
        "completedEvidenceReceipts": existing_receipts,
        "pairedClassification": receipt(CLASSIFICATION),
        "naturalTerminalGate": receipt(TERMINAL),
        "unusedOutputConflicts": remaining_outputs(),
    }
    if missing:
        raise AssertionError(f"resume preflight failed: {missing}")
    return payload, previous


def write_summary(rows: list[dict], previous_wall_s: float, resume_started: float, complete: bool) -> dict:
    classification = json.loads(CLASSIFICATION.read_text())
    raw_failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    allowed_raw = {"paired-integration"} if classification.get("effectiveReleaseGate") == "PASS" else set()
    effective_failures = [name for name in raw_failures if name not in allowed_raw]
    native = [row for row in rows if row["suite"] in stage.NATIVE]
    result = {
        "schema": "AEGIS_DEFENSE_OODA_A_FINAL_REGRESSION_2",
        "complete": complete,
        "candidate": stage.PRODUCT.name,
        "candidateSha256": stage.PRODUCT_SHA256,
        "candidateBytes": stage.PRODUCT_BYTES,
        "baseline": stage.BASELINE.name,
        "baselineSha256": stage.BASELINE_SHA256,
        "threatAssumptionMode": "MAX_THREAT",
        "broadRun": {
            "runCount": 1,
            "oneShot": True,
            "candidateFrozen": True,
            "continuedAfterPolicyClassification": True,
            "completedSuitesRerun": [],
            "resumeReceipt": "evidence/final-regression/resume-preflight.json",
        },
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "gameConstantsChanged": False,
        "rows": rows,
        "rawFailures": raw_failures,
        "pairedActiveDelta": {
            "rawStatus": "FAIL",
            "classification": classification["classification"],
            "effectiveReleaseGate": classification["effectiveReleaseGate"],
            "evidence": str(CLASSIFICATION.relative_to(HERE)),
        },
        "native13": {
            "suiteCount": len(native),
            "expectedSuiteCount": 13,
            "expectedAssertions": 364,
            "executedAssertions": sum(row["executedAssertions"] for row in native),
            "passedAssertions": sum(row["passedAssertions"] for row in native),
        },
        "assertions": {
            "expectedRaw": 788,
            "executedRaw": sum(row["executedAssertions"] for row in rows),
            "passedRaw": sum(row["passedAssertions"] for row in rows),
            "failedRaw": sum(len(row["failedAssertions"]) for row in rows),
        },
        "coverage": {
            "defenseOoda": "static-integrity + D ACTIVE/contract/engine + natural terminal gates",
            "pairedDdgCg": ["paired-integration (raw observational delta)", "paired-determinism"],
            "hpOutcomeSave": "hp-contract",
            "seekerCloseNineteenShots": "seeker-close",
            "representativeRealFlights": ["u4-seeker-scenes", "harpoon-f1"],
            "emconAndEsm": ["current-emcon-ui", "seeker-close"],
            "browserUi": "ui213",
            "actualWebgl": "webgl8",
        },
        "confirmedOnly": {"staticAndLimitedFeatureOffEvidence": "INHERITED_PASS", "performance": "UNVERIFIED"},
        "inheritedDebt": [
            "CIWS_SEED_419025_FAIL", "CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2",
            "WIP12D_CIWS_FIXED_STEP_SCALE_DEBT", "CHROMIUM_MEMORY_CRASH_AND_CHECKOUT_TIMEOUT_DEBT",
            "KH32_60KM_POPULATION_NOT_RUN", "CONFIRMED_ONLY_PERFORMANCE_UNVERIFIED",
            "LEGACY_SARH_SELFTEST_DIAGNOSTIC_DEBT",
        ],
        "effectiveFailures": effective_failures,
        "wallS": previous_wall_s + (time.perf_counter() - resume_started),
        "release": False,
    }
    SUMMARY.write_text(strict(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    resume, previous = preflight()
    if args.dry_run:
        print(strict(resume))
        return
    if not STOP_RECEIPT.exists():
        STOP_RECEIPT.write_text(strict(previous))
    (OUT / "resume-preflight.json").write_text(strict(resume))
    rows = list(previous["rows"])
    started = time.perf_counter()
    previous_wall_s = float(previous.get("wallS", 0))
    write_summary(rows, previous_wall_s, started, False)
    for name in REMAINING:
        row = stage.base.execute(name)
        rows.append(row)
        write_summary(rows, previous_wall_s, started, False)
        if row["executedAssertions"] == 0:
            raise SystemExit(f"zero-assertion suite: {name}")
        if row["status"] != "PASS":
            raise SystemExit(f"continued broad regression stopped on failure: {name}")
    result = write_summary(rows, previous_wall_s, started, True)
    raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__ == "__main__":
    main()
