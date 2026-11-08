#!/usr/bin/env python3
"""One-shot replacement MAX_THREAT broad regression for corrected ESM_A.

The raw EMCON_B -> ESM_A paired comparison is preserved. The only accepted
non-exact assertions are the six user-approved ``state.esmA`` save-schema
additions; this runner proves that removing only that field restores exact
physical state and does not rewrite an expectation or tolerance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_ESM_A.html"
BASELINE = ROOT / "Aegis_SIM_v48_WIP_EMCON_B.html"
HELI_CG_A_BASELINE = ROOT / "archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html"
MULTISHIP_H4_SOURCE = ROOT / "docs/multiship/H4/regression_baseline.py"
GUN_B1_UI_SOURCE = ROOT / "docs/gun/B1/run_test_migrations.py"
TEST_SUPPORT = ROOT / "docs/gun/B2/phase1b/test_support/sitecustomize.py"
PRODUCT_SHA256 = "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7"
PRODUCT_BYTES = 22_182_527
BASELINE_SHA256 = "50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee"
HELI_CG_A_BASELINE_SHA256 = "c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3"
MULTISHIP_H4_SOURCE_SHA256 = "9c1c7239f31e9a0a15f3d752ab9a2925729758fd0f23fb879d5b7ec6e90479e0"
GUN_B1_UI_SOURCE_SHA256 = "b8a05458a594a45fb4b91abceda5a0be782c195f722179d800f0e4e8a76b4a75"
TEST_SUPPORT_SHA256 = "522af70b9d84a5595187a285d29182bf1b277837b579e6f917d14f3f61750be5"
OUT = HERE / "evidence" / "final-regression-corrected"
SUMMARY = HERE / "FINAL_REGRESSION_CORRECTED.json"

NATIVE = {
    "helicopter-flight": ("native.json", 85),
    "aps153": ("native.json", 20),
    "isar-native": ("native.json", 36),
    "isar-classes": ("classes.json", 8),
    "isar-clock": ("clock.json", 12),
    "isar-ui": ("ui.json", 38),
    "emcon-native": ("native.json", 27),
    "harpoon-f1": ("native.json", 46),
    "harpoon-clock": ("ui-clock.json", 24),
    "sov-native": ("native.json", 30),
    "sov-casualty": ("casualty.json", 13),
    "sov-deployment": ("deployment.json", 15),
    "sov-visual": ("visual.json", 10),
}
assert sum(value[1] for value in NATIVE.values()) == 364


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def environment() -> dict[str, str]:
    return {
        **os.environ,
        "TMPDIR": "/dev/shm",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": os.environ.get("NODE_PATH", str(ROOT / "node_modules")),
        "B2_PHASE1_REGRESSION": "1",
        "B2_MODE": "ON",
        "B2_HTML": str(PRODUCT),
        "B2_OUT": str(OUT),
        "PYTHONPATH": str(TEST_SUPPORT.parent),
        "B2_ALLOW_AUTO": "0",
        "THREAT_ASSUMPTION_MODE": "MAX_THREAT",
    }


def command(name: str) -> list[str]:
    if name in NATIVE:
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/pip/B/run_domain.py"),
            str(PRODUCT),
            str(OUT / name),
            "--only",
            name,
        ]
    if name == "paired-compatibility":
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/helicopter/F/verify_regression.py"),
            str(BASELINE),
            str(PRODUCT),
            str(OUT / name),
            "--baseline-only",
        ]
    if name == "paired-determinism":
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/helicopter/F/verify_regression.py"),
            str(PRODUCT),
            str(PRODUCT),
            str(OUT / name),
            "--baseline-only",
        ]
    if name == "current-emcon-ui":
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/map/E/verify_emcon_ui.py"),
            str(PRODUCT),
            str(OUT / name),
        ]
    if name == "ui213":
        return [sys.executable, "-u", str(ROOT / "docs/contact/friendly/A/cpu2d_ui.py")]
    if name == "webgl8":
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/envelope/D/run_observed_webgl.py"),
            str(PRODUCT),
            str(OUT / name),
        ]
    raise ValueError(name)


def result_location(name: str) -> tuple[Path, int]:
    if name in NATIVE:
        return OUT / name / NATIVE[name][0], NATIVE[name][1]
    if name in {"paired-compatibility", "paired-determinism"}:
        return OUT / name / "baseline-comparison.json", 42
    if name == "current-emcon-ui":
        return OUT / name / "ui.json", 14
    if name == "ui213":
        return OUT / "map/E/evidence/d-ui/ui.json", 213
    if name == "webgl8":
        return OUT / name / "observed-world.json", 29
    raise ValueError(name)


def paired_checks(payload: dict) -> dict[str, bool]:
    return {
        f"{row['ship']}:{row['scenario']}:{key}": bool(value)
        for row in payload.get("cases", [])
        for key, value in row.get("checks", {}).items()
    }


def approved_schema_delta(payload: dict) -> dict:
    cases = payload.get("cases", [])
    rows = []
    for case in cases:
        checks = case.get("checks", {})
        baseline_state = copy.deepcopy(case.get("pair", {}).get("baseline", {}).get("state", {}))
        candidate_state = copy.deepcopy(case.get("pair", {}).get("candidate", {}).get("state", {}))
        baseline_esm = baseline_state.pop("esmA", None)
        candidate_esm = candidate_state.pop("esmA", None)
        false_checks = sorted(key for key, value in checks.items() if not value)
        row = {
            "ship": case.get("ship"),
            "scenario": case.get("scenario"),
            "rawFalseChecks": false_checks,
            "baselineEsmAAbsent": baseline_esm is None,
            "candidateEsmASchema": candidate_esm.get("schema") if isinstance(candidate_esm, dict) else None,
            "physicalExactAfterRemovingOnlyStateEsmA": baseline_state == candidate_state,
            "combatRngExact": checks.get("sameCombatRng") is True,
            "damageAndFixedLayoutExact": checks.get("sameHullDamageAndFixedLayout") is True,
            "inventoryExactOrBoundedByOriginalContract": checks.get("raidInventoryDeltaBounded") is True,
            "observerExact": checks.get("sameExistingObserverState") is True,
            "offboardExact": checks.get("sameExistingOffboardPorts") is True,
            "faultFree": checks.get("bothFaultFree") is True,
        }
        row["approved"] = (
            row["rawFalseChecks"] == ["samePhysicalState"]
            and row["baselineEsmAAbsent"]
            and row["candidateEsmASchema"] == "AEGIS_ESM_SAVE_A_1"
            and all(
                row[key]
                for key in (
                    "physicalExactAfterRemovingOnlyStateEsmA",
                    "combatRngExact",
                    "damageAndFixedLayoutExact",
                    "inventoryExactOrBoundedByOriginalContract",
                    "observerExact",
                    "offboardExact",
                    "faultFree",
                )
            )
        )
        rows.append(row)
    exact_expected_cases = {
        (ship, scenario)
        for ship in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")
        for scenario in ("idle", "raid", "damaged")
    }
    return {
        "decision": "USER_APPROVED_STATE_ESMA_SCHEMA_ADDITION",
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "cases": rows,
        "pass": len(rows) == 6
        and {(row["ship"], row["scenario"]) for row in rows} == exact_expected_cases
        and all(row["approved"] for row in rows),
    }


def extract(name: str, exit_code: int) -> dict:
    path, expected = result_location(name)
    payload = json.loads(path.read_text()) if path.exists() else {}
    errors = payload.get("errors", [])
    checks = paired_checks(payload) if name.startswith("paired-") else payload.get("checks", {})
    failed = [key for key, value in checks.items() if not value]
    approval = approved_schema_delta(payload) if name == "paired-compatibility" else None
    raw_passed = sum(bool(value) for value in checks.values())
    if name == "paired-compatibility" and approval and approval["pass"]:
        status = "APPROVED_SCHEMA_DELTA"
        effective_passed = expected
        reason = "Six raw samePhysicalState failures are solely the user-approved state.esmA save-schema field; raw output is preserved."
    elif exit_code == 0 and len(checks) == expected and not failed and not errors:
        status = "PASS"
        effective_passed = raw_passed
        reason = None
    else:
        status = "FAIL"
        effective_passed = raw_passed
        reason = "Original assertion/worker failure or incomplete output"
    return {
        "status": status,
        "reason": reason,
        "expectedAssertions": expected,
        "executedAssertions": len(checks),
        "rawPassedAssertions": raw_passed,
        "effectivePassedAssertions": effective_passed,
        "failedAssertions": failed,
        "errors": errors,
        "resultPath": str(path.relative_to(OUT)) if path.exists() else None,
        "approvedDelta": approval,
    }


def execute(name: str) -> dict:
    assert PRODUCT.stat().st_size == PRODUCT_BYTES
    assert sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    assert sha256(BASELINE.read_bytes()) == BASELINE_SHA256
    log_path = OUT / f"{name}.log"
    started = time.perf_counter()
    with log_path.open("w") as log:
        try:
            proc = subprocess.run(
                command(name),
                cwd=ROOT,
                env=environment(),
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=1_500,
            )
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            exit_code = 124
    row = {
        "suite": name,
        "command": command(name),
        "exitCode": exit_code,
        "wallS": time.perf_counter() - started,
        **extract(name, exit_code),
    }
    (OUT / f"{name}-execution.json").write_text(strict(row))
    print(strict({key: value for key, value in row.items() if key not in {"command", "errors", "approvedDelta"}}), flush=True)
    return row


def static_integrity() -> dict:
    build = json.loads((HERE / "BUILD_E.json").read_text())
    gates = {
        name: json.loads((HERE / filename).read_text())
        for name, filename in {
            "B": "B_GATE.json",
            "C": "C_GATE.json",
            "D": "D_GATE.json",
            "D_predecessor": "D_PREDECESSOR_RECHECK.json",
            "E": "E_GATE.json",
        }.items()
    }
    product_text = PRODUCT.read_text(errors="ignore")
    source = (HERE / "esm_core.js").read_text()
    module_hashes = {name: sha256((HERE / name).read_bytes()) for name in build.get("sourceModules", {})}
    checks = {
        "productBytesPinned": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "baselineShaPinned": sha256(BASELINE.read_bytes()) == BASELINE_SHA256,
        "buildOutputPinned": build.get("outputSha256") == PRODUCT_SHA256 and build.get("outputBytes") == PRODUCT_BYTES,
        "sourceModulesPinned": module_hashes == build.get("sourceModules"),
        "unchangedFunctionHashesExact": all(row.get("same") is True for row in build.get("unchangedFunctions", {}).values()),
        "limitedGatesPass": all(gate.get("status") == "PASS" for gate in gates.values()),
        "correctedEGateBoundToProduct": gates["E"].get("inputs", {}).get("productSha256") == PRODUCT_SHA256,
        "diagnosticAdaptersAbsent": "__ESM_A_E_DIAG__" not in product_text and "__ESM_A_E_BASELINE__" not in product_text,
        "commonEstimatorOwnsSeparateMap": "function esmCommonContactsA(r){return prepareEsmA(r).contacts;}" in source,
        "legacyProjectionRemainsExplicit": "function esmLegacyProjectionA(r,rows)" in source,
        "localAcceptUpdatesBothExplicitly": "esmLegacyProjectionA(r,plots);return common" in source,
        "truthAuthorityGatePass": gates["E"].get("checks", {}).get("truthAndAuthorityZero") is True,
        "saveLifecycleGatePass": gates["E"].get("checks", {}).get("saveLifecyclePass") is True,
        "deterministicLimitedGatePass": gates["E"].get("checks", {}).get("repeatDeterministic") is True,
        "sovReceiverRemainsInactive": gates["E"].get("checks", {}).get("sovCandidatePass") is True
        and gates["E"].get("checks", {}).get("sovBaselineExact") is True,
        "performanceBudgetPass": gates["E"].get("checks", {}).get("performanceBudget") is True,
    }
    failed = [key for key, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_ESM_A_FINAL_STATIC_1",
        "checks": checks,
        "moduleHashes": module_hashes,
        "unchangedFunctions": build.get("unchangedFunctions", {}),
        "limitedGateStatus": {name: gate.get("status") for name, gate in gates.items()},
        "errors": [],
    }
    path = OUT / "static-integrity.json"
    path.write_text(strict(payload))
    return {
        "suite": "static-integrity",
        "status": "PASS" if not failed else "FAIL",
        "reason": None if not failed else "Pinned/static contract failure",
        "exitCode": 0 if not failed else 1,
        "wallS": 0,
        "expectedAssertions": len(checks),
        "executedAssertions": len(checks),
        "rawPassedAssertions": sum(checks.values()),
        "effectivePassedAssertions": sum(checks.values()),
        "failedAssertions": failed,
        "errors": [],
        "resultPath": str(path.relative_to(OUT)),
    }


def source_provenance() -> None:
    files = [
        ROOT / "docs/pip/B/run_domain.py",
        ROOT / "docs/map/E/verify_emcon_ui.py",
        ROOT / "docs/map/A/verify_regressions.py",
        ROOT / "docs/viewport/A/verify_regressions.py",
        ROOT / "docs/contact/friendly/A/cpu2d_ui.py",
        ROOT / "docs/envelope/D/run_observed_webgl.py",
        ROOT / "docs/helicopter/F/verify_regression.py",
        HELI_CG_A_BASELINE,
        MULTISHIP_H4_SOURCE,
        GUN_B1_UI_SOURCE,
        TEST_SUPPORT,
    ]
    payload = {
        "schema": "AEGIS_ESM_A_FINAL_SOURCE_PROVENANCE_1",
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "baselineSha256": BASELINE_SHA256,
        "helicopterCgABaselineSha256": HELI_CG_A_BASELINE_SHA256,
        "multishipH4SourceSha256": MULTISHIP_H4_SOURCE_SHA256,
        "gunB1UiSourceSha256": GUN_B1_UI_SOURCE_SHA256,
        "testSupportSha256": TEST_SUPPORT_SHA256,
        "threatMode": "MAX_THREAT",
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "files": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes())}
            for path in files
        ],
    }
    (OUT / "source-provenance.json").write_text(strict(payload))


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    effective_failures = [
        row["suite"]
        for row in rows
        if row["status"] not in {"PASS", "APPROVED_SCHEMA_DELTA", "INHERITED_DEBT"}
    ]
    native = [row for row in rows if row["suite"] in NATIVE]
    interruption_path = OUT / "infrastructure-interruptions.json"
    interruptions = json.loads(interruption_path.read_text()).get("interruptions", []) if interruption_path.exists() else []
    result = {
        "schema": "AEGIS_ESM_A_FINAL_REGRESSION_CORRECTED_1",
        "complete": complete,
        "candidate": PRODUCT.name,
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "baseline": BASELINE.name,
        "baselineSha256": BASELINE_SHA256,
        "threatAssumptionMode": "MAX_THREAT",
        "replacementBroadRun": {
            "authorizedByUser": True,
            "runCount": 1,
            "candidateSha256": PRODUCT_SHA256,
            "resumedAfterZeroAssertionInfrastructureFailure": bool(interruptions),
        },
        "infrastructureInterruptions": interruptions,
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "rawFailuresPreserved": True,
        "rows": rows,
        "native13": {
            "suiteCount": len(native),
            "expectedSuiteCount": 13,
            "expectedAssertions": 364,
            "executedAssertions": sum(row["executedAssertions"] for row in native),
            "passedAssertions": sum(row["rawPassedAssertions"] for row in native),
        },
        "coverage": {
            "static": "static-integrity",
            "determinism": ["paired-determinism", "E_GATE.repeatDeterministic"],
            "saveLoadReset": ["helicopter-flight", "harpoon-f1", "sov-native", "E_GATE.saveLifecyclePass"],
            "ui": ["ui213", "current-emcon-ui"],
            "webgl": "webgl8",
            "timeScale": ["isar-clock", "harpoon-clock"],
            "battle": ["paired-compatibility raid scenarios", "paired-determinism raid scenarios", "webgl8"],
        },
        "retiredEmconMapping": {
            "currentSuite": "current-emcon-ui: docs/map/E/verify_emcon_ui.py, 14 assertions",
            "retiredSuite": "docs/helicopter/K/verify_ui.py direct legacy controls (#lockBtn / external3D*)",
            "policy": "Retired suite not revived; adapter retains 14 current-contract assertions and records the control migration.",
            "inheritedDebt": "LEGACY_EMCON_UI_DIRECT_RUN_RETIRED",
        },
        "effectiveFailures": effective_failures,
        "wallS": time.perf_counter() - started,
        "release": False,
    }
    SUMMARY.write_text(strict(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    assert PRODUCT.stat().st_size == PRODUCT_BYTES
    assert sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    assert sha256(BASELINE.read_bytes()) == BASELINE_SHA256
    assert HELI_CG_A_BASELINE.exists(), "Required archived helicopter baseline is absent from the sparse checkout"
    assert sha256(HELI_CG_A_BASELINE.read_bytes()) == HELI_CG_A_BASELINE_SHA256
    assert MULTISHIP_H4_SOURCE.exists(), "Required paired-regression source is absent from the sparse checkout"
    assert sha256(MULTISHIP_H4_SOURCE.read_bytes()) == MULTISHIP_H4_SOURCE_SHA256
    assert GUN_B1_UI_SOURCE.exists(), "Required UI-regression source is absent from the sparse checkout"
    assert sha256(GUN_B1_UI_SOURCE.read_bytes()) == GUN_B1_UI_SOURCE_SHA256
    assert TEST_SUPPORT.exists(), "Required B2 test support is absent from the sparse checkout"
    assert sha256(TEST_SUPPORT.read_bytes()) == TEST_SUPPORT_SHA256
    names = [*NATIVE, "paired-compatibility", "paired-determinism", "current-emcon-ui", "ui213", "webgl8"]
    if args.dry_run:
        print(strict({
            "product": str(PRODUCT),
            "productBytes": PRODUCT_BYTES,
            "productSha256": PRODUCT_SHA256,
            "baselineSha256": BASELINE_SHA256,
            "helicopterCgABaselineSha256": HELI_CG_A_BASELINE_SHA256,
            "multishipH4SourceSha256": MULTISHIP_H4_SOURCE_SHA256,
            "gunB1UiSourceSha256": GUN_B1_UI_SOURCE_SHA256,
            "testSupportSha256": TEST_SUPPORT_SHA256,
            "output": str(OUT),
            "oneShot": True,
            "jobs": {name: command(name) for name in names},
            "staticSuite": "static-integrity",
            "retiredEmconUiExecuted": False,
        }))
        return
    if args.resume:
        assert OUT.exists() and SUMMARY.exists(), "No interrupted broad run is available to resume"
        old = json.loads(SUMMARY.read_text())
        assert old.get("candidateSha256") == PRODUCT_SHA256
        rows = old.get("rows", [])
        retryable = [row for row in rows if row.get("status") == "FAIL" and row.get("executedAssertions") == 0]
        assert retryable and all(row.get("suite") in names for row in retryable), "Only zero-assertion infrastructure failures may be resumed"
        interruption_path = OUT / "infrastructure-interruptions.json"
        interruptions = json.loads(interruption_path.read_text()).get("interruptions", []) if interruption_path.exists() else []
        for row in retryable:
            index = 1 + sum(item.get("suite") == row["suite"] for item in interruptions)
            for suffix in (".log", "-execution.json"):
                source = OUT / f"{row['suite']}{suffix}"
                if source.exists():
                    source.rename(OUT / f"{row['suite']}-startup-failure-{index}{suffix}")
            interruptions.append({
                "suite": row["suite"],
                "executedAssertions": 0,
                "exitCode": row.get("exitCode"),
                "reason": row.get("reason"),
                "classification": "SPARSE_CHECKOUT_TEST_INPUT_MISSING; PRODUCT_NOT_EXECUTED",
            })
        interruption_path.write_text(strict({"schema": "AEGIS_ESM_A_INFRASTRUCTURE_INTERRUPTION_1", "interruptions": interruptions}))
        rows = [row for row in rows if row not in retryable]
        started = time.perf_counter() - float(old.get("wallS", 0))
        completed = {row["suite"] for row in rows if row.get("status") in {"PASS", "APPROVED_SCHEMA_DELTA"}}
        names = [name for name in names if name not in completed]
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        assert not any(OUT.iterdir()), "Replacement broad regression is one-shot; output directory must be empty"
        started = time.perf_counter()
        rows = [static_integrity()]
        rows.append({
            "suite": "retired-emcon-ui",
            "status": "INHERITED_DEBT",
            "reason": "Direct legacy controls are retired; the current 14-assertion adapter is executed separately in this run.",
            "exitCode": None,
            "wallS": 0,
            "expectedAssertions": 0,
            "executedAssertions": 0,
            "rawPassedAssertions": 0,
            "effectivePassedAssertions": 0,
            "failedAssertions": [],
            "errors": [],
            "resultPath": None,
        })
    source_provenance()
    write_summary(rows, started, complete=False)
    for name in names:
        rows.append(execute(name))
        result = write_summary(rows, started, complete=False)
        if result["effectiveFailures"]:
            # Stop immediately on the first unexplained regression, as directed.
            write_summary(rows, started, complete=True)
            raise SystemExit(1)
    result = write_summary(rows, started, complete=True)
    raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__ == "__main__":
    main()
