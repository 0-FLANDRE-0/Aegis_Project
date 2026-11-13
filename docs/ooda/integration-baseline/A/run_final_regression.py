#!/usr/bin/env python3
"""One-shot MAX_THREAT broad regression for INTEGRATION_BASELINE_A."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html"
BASELINE = ROOT / "Aegis_SIM_v48_WIP_HP_A.html"
PRODUCT_BYTES = 22_212_299
PRODUCT_SHA256 = "655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0"
BASELINE_BYTES = 22_200_135
BASELINE_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"
HELI_CG_A = ROOT / "archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html"
HELI_CG_A_BYTES = 16_078_336
HELI_CG_A_SHA256 = "c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3"
PREVIOUS_STOP = HERE / "evidence" / "final-correction" / "final-regression" / "BROAD_RUN_STOP.json"
OUT = HERE / "evidence" / "final-correction" / "final-regression-attempt-2"
SUMMARY = HERE / "FINAL_CORRECTION_REGRESSION_ATTEMPT_2.json"

NATIVE = {
    "helicopter-flight": ("native.json", 85), "aps153": ("native.json", 20),
    "isar-native": ("native.json", 36), "isar-classes": ("classes.json", 8),
    "isar-clock": ("clock.json", 12), "isar-ui": ("ui.json", 38),
    "emcon-native": ("native.json", 27), "harpoon-f1": ("native.json", 46),
    "harpoon-clock": ("ui-clock.json", 24), "sov-native": ("native.json", 30),
    "sov-casualty": ("casualty.json", 13), "sov-deployment": ("deployment.json", 15),
    "sov-visual": ("visual.json", 10),
}
assert sum(value[1] for value in NATIVE.values()) == 364


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def environment() -> dict[str, str]:
    return {
        **os.environ, "TMPDIR": "/dev/shm", "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": os.environ.get("NODE_PATH", str(ROOT / "node_modules")),
        "B2_PHASE1_REGRESSION": "1", "B2_MODE": "ON", "B2_HTML": str(PRODUCT),
        "B2_OUT": str(OUT), "PYTHONPATH": str(ROOT / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0", "THREAT_ASSUMPTION_MODE": "MAX_THREAT",
    }


def command(name: str) -> list[str]:
    if name in NATIVE:
        return [sys.executable, "-u", str(ROOT / "docs/pip/B/run_domain.py"), str(PRODUCT), str(OUT / name), "--only", name]
    if name == "paired-hp-a":
        return [sys.executable, "-u", str(ROOT / "docs/helicopter/F/verify_regression.py"), str(BASELINE), str(PRODUCT), str(OUT / name), "--baseline-only"]
    if name == "paired-determinism":
        return [sys.executable, "-u", str(ROOT / "docs/helicopter/F/verify_regression.py"), str(PRODUCT), str(PRODUCT), str(OUT / name), "--baseline-only"]
    if name == "current-emcon-ui":
        return [sys.executable, "-u", str(ROOT / "docs/map/E/verify_emcon_ui.py"), str(PRODUCT), str(OUT / name)]
    if name == "ui213":
        return [sys.executable, "-u", str(ROOT / "docs/contact/friendly/A/cpu2d_ui.py")]
    if name == "webgl8":
        return [sys.executable, "-u", str(ROOT / "docs/envelope/D/run_observed_webgl.py"), str(PRODUCT), str(OUT / name)]
    if name == "u4-seeker-scenes":
        return [sys.executable, "-u", str(HERE / "run_u4_scenes_candidate.py"), str(PRODUCT), str(OUT / name / "scenes.json")]
    if name == "hp-contract":
        return [sys.executable, "-u", str(ROOT / "docs/damage/hp/A/run_contract_gate.py"), str(PRODUCT), str(OUT / name / "contract-gate.json")]
    if name == "seeker-close":
        return [sys.executable, "-u", str(HERE / "run_seeker_close_candidate.py"), str(PRODUCT), str(OUT / name)]
    raise ValueError(name)


def result_location(name: str) -> tuple[Path, int]:
    if name in NATIVE:
        return OUT / name / NATIVE[name][0], NATIVE[name][1]
    if name in {"paired-hp-a", "paired-determinism"}:
        return OUT / name / "baseline-comparison.json", 42
    if name == "current-emcon-ui":
        return OUT / name / "ui.json", 14
    if name == "ui213":
        return OUT / "map/E/evidence/d-ui/ui.json", 213
    if name == "webgl8":
        return OUT / name / "observed-world.json", 29
    if name == "u4-seeker-scenes":
        return OUT / name / "scenes.json", 19
    if name == "hp-contract":
        return OUT / name / "contract-gate.json", 19
    if name == "seeker-close":
        return OUT / name / "SUMMARY.json", 26
    raise ValueError(name)


def paired_checks(payload: dict) -> dict[str, bool]:
    return {f"{row['ship']}:{row['scenario']}:{key}": bool(value) for row in payload.get("cases", []) for key, value in row.get("checks", {}).items()}


def extract(name: str, exit_code: int) -> dict:
    path, expected = result_location(name)
    payload = json.loads(path.read_text()) if path.exists() else {}
    errors = payload.get("errors", [])
    checks = paired_checks(payload) if name.startswith("paired-") else payload.get("checks", {})
    failed = [key for key, value in checks.items() if not value]
    passed = sum(bool(value) for value in checks.values())
    status = "PASS" if exit_code == 0 and len(checks) == expected and not failed and not errors else "FAIL"
    return {"status": status, "expectedAssertions": expected, "executedAssertions": len(checks), "passedAssertions": passed, "failedAssertions": failed, "errors": errors, "resultPath": str(path.relative_to(OUT)) if path.exists() else None}


def execute(name: str) -> dict:
    assert PRODUCT.stat().st_size == PRODUCT_BYTES and sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    started = time.perf_counter()
    log_path = OUT / f"{name}.log"
    with log_path.open("w") as log:
        try:
            result = subprocess.run(command(name), cwd=ROOT, env=environment(), stdout=log, stderr=subprocess.STDOUT, timeout=1_800)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            exit_code = 124
    row = {"suite": name, "command": command(name), "exitCode": exit_code, "wallS": time.perf_counter() - started, **extract(name, exit_code)}
    (OUT / f"{name}-execution.json").write_text(strict(row))
    print(strict({key: value for key, value in row.items() if key not in {"command", "errors"}}), flush=True)
    return row


def static_integrity() -> dict:
    correction = HERE / "evidence" / "final-correction"
    hash_gate = json.loads((correction / "commit-b" / "FUNCTION_HASH_GATE.json").read_text())
    boundary_gate = json.loads((correction / "commit-b" / "BOUNDARY_STATIC_GATE.json").read_text())
    baseline_oracle = json.loads((correction / "oracles" / "BASELINE_ORACLE.json").read_text())
    candidate_oracle = json.loads((correction / "oracles" / "CANDIDATE_ORACLE.json").read_text())
    contract = json.loads((correction / "oracles" / "CONTRACT_ORACLE.json").read_text())
    repeat = json.loads((correction / "oracles" / "CONTRACT_ORACLE_REPEAT.json").read_text())
    crew = json.loads((correction / "commit-a" / "CREW_CONTRACT_ORACLE.json").read_text())
    crew_repeat = json.loads((correction / "commit-a" / "CREW_CONTRACT_ORACLE_REPEAT.json").read_text())
    baseline_hashes = json.loads((correction / "commit-b" / "FUNCTION_HASHES_BASELINE.json").read_text())["functions"]
    candidate_hashes = json.loads((correction / "commit-b" / "FUNCTION_HASHES_CANDIDATE.json").read_text())["functions"]
    common = set(baseline_hashes) & set(candidate_hashes)
    changed = sorted(name for name in common if baseline_hashes[name] != candidate_hashes[name])
    new = sorted(set(candidate_hashes) - set(baseline_hashes))
    checks = {
        "productBytesPinned": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "baselineBytesPinned": BASELINE.stat().st_size == BASELINE_BYTES,
        "baselineShaPinned": sha256(BASELINE.read_bytes()) == BASELINE_SHA256,
        "functionHashGatePass": hash_gate.get("status") == "PASS",
        "boundaryStaticGatePass": boundary_gate.get("status") == "PASS",
        "baselineCandidateOracleExact": baseline_oracle["deterministicDigest"] == candidate_oracle["deterministicDigest"],
        "contractRepeatExact": contract["deterministicDigest"] == repeat["deterministicDigest"],
        "crewContractRepeatExact": crew["deterministicDigest"] == crew_repeat["deterministicDigest"],
        "crewContractAllPass": bool(crew.get("checks")) and all(crew["checks"].values()),
        "shadowMismatchZero": all((row[side]["diagnostics"]["shadowMismatchCount"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "rngMismatchZero": all((row[side]["diagnostics"]["rngMismatchCount"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "truthAuditZero": all((row[side]["diagnostics"]["truthAuditFailures"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "readOnlyInputExact": all(row["readOnly"]["rngExact"] and row["readOnly"]["saveExact"] for row in contract["owners"]),
        "protectedHashesExact": changed == ["wip118BuildEngagementControl"] and hash_gate.get("protectedCount") == 31 and len(hash_gate.get("protectedExact", [])) == 30,
        "newContractFunctionsExact": len(new) == 11 and set(new) == set(hash_gate.get("newBoundaryFunctions", [])),
        "noSaveSchemaFields": all(row["provider"]["saveFields"] == 0 for row in contract["owners"]),
    }
    failed = [key for key, value in checks.items() if not value]
    payload = {"schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_CORRECTION_STATIC_1", "checks": checks, "intentionalChangedFunctions": changed, "newFunctions": new, "errors": []}
    path = OUT / "static-integrity.json"; path.write_text(strict(payload))
    return {"suite": "static-integrity", "status": "PASS" if not failed else "FAIL", "exitCode": 0 if not failed else 1, "wallS": 0, "expectedAssertions": len(checks), "executedAssertions": len(checks), "passedAssertions": sum(checks.values()), "failedAssertions": failed, "errors": [], "resultPath": str(path.relative_to(OUT))}


def source_provenance() -> None:
    files = [
        ROOT / "docs/pip/B/run_domain.py", ROOT / "docs/map/E/verify_emcon_ui.py",
        ROOT / "docs/contact/friendly/A/cpu2d_ui.py", ROOT / "docs/envelope/D/run_observed_webgl.py",
        ROOT / "docs/helicopter/F/verify_regression.py", ROOT / "docs/damage/hp/A/run_contract_gate.py",
        ROOT / "docs/missile/seeker-close/A/run_diagnostics.py", HERE / "run_u4_scenes_candidate.py",
        HERE / "run_seeker_close_candidate.py", HERE / "build_seeker_close_diagnostic.py",
    ]
    payload = {"schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_CORRECTION_ATTEMPT_2_SOURCE_PROVENANCE_1", "attempt": 2, "authorizedRerun": True, "candidateSha256": PRODUCT_SHA256, "candidateBytes": PRODUCT_BYTES, "baselineSha256": BASELINE_SHA256, "threatMode": "MAX_THREAT", "expectedValuesUpdated": False, "tolerancesChanged": False, "gameConstantsChanged": False, "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes())} for path in files]}
    (OUT / "source-provenance.json").write_text(strict(payload))


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    native = [row for row in rows if row["suite"] in NATIVE]
    result = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_CORRECTION_REGRESSION_ATTEMPT_2_1", "complete": complete,
        "candidate": PRODUCT.name, "candidateSha256": PRODUCT_SHA256, "candidateBytes": PRODUCT_BYTES,
        "baseline": BASELINE.name, "baselineSha256": BASELINE_SHA256, "threatAssumptionMode": "MAX_THREAT",
        "broadRun": {"attempt": 2, "authorizedRerun": True, "runCountThisAttempt": 1, "previousAttemptReceipt": str(PREVIOUS_STOP.relative_to(HERE)), "candidateFrozen": True, "candidateSha256": PRODUCT_SHA256},
        "expectedValuesUpdated": False, "tolerancesChanged": False, "gameConstantsChanged": False, "rows": rows,
        "native13": {"suiteCount": len(native), "expectedSuiteCount": 13, "expectedAssertions": 364, "executedAssertions": sum(row["executedAssertions"] for row in native), "passedAssertions": sum(row["passedAssertions"] for row in native)},
        "coverage": {"decisionContract": "static-integrity + contract oracle", "hpOutcomeSave": "hp-contract", "seekerCloseNineteenShots": "seeker-close", "representativeRealFlights": ["u4-seeker-scenes", "harpoon-f1"], "pairedDdgCg": ["paired-hp-a", "paired-determinism"], "emconAndEsm": ["current-emcon-ui", "seeker-close"], "browserUi": "ui213", "actualWebgl": "webgl8"},
        "confirmedOnly": {"staticAndLimitedFeatureOffEvidence": "INHERITED_PASS", "performance": "UNVERIFIED"},
        "effectiveFailures": failures, "wallS": time.perf_counter() - started, "release": False,
    }
    SUMMARY.write_text(strict(result)); return result


def tracked_paths(prefix: str) -> list[Path]:
    output = subprocess.check_output(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", prefix], cwd=ROOT)
    return [ROOT / value.decode("utf-8") for value in output.split(b"\0") if value]


def preflight() -> dict:
    native_sources = [ROOT / path for path in [
        "docs/helicopter/J/verify_native.py", "docs/helicopter/G/verify_native.py",
        "docs/helicopter/L/verify_native.py", "docs/helicopter/L/verify_classes.py",
        "docs/helicopter/L/verify_clock.py", "docs/helicopter/L/verify_ui.py",
        "docs/helicopter/K/verify_native.py", "docs/helicopter/H/verify_native.py",
        "docs/helicopter/H/verify_ui_clock.py", "docs/sovremenny/A/verify_native.py",
        "docs/sovremenny/A/verify_casualty.py", "docs/sovremenny/A/verify_deployment.py",
        "docs/sovremenny/A/verify_visual.py",
    ]]
    required = [
        PRODUCT, BASELINE, HELI_CG_A, PREVIOUS_STOP,
        ROOT / "docs/multiship/G/browser_g.py",
        ROOT / "docs/missile/fuze-zem/A/browser_tools.py",
        ROOT / "docs/pip/B/run_domain.py",
        ROOT / "docs/pip/B/browser_backend.py",
        ROOT / "docs/map/A/verify_regressions.py",
        ROOT / "docs/viewport/A/verify_regressions.py",
        ROOT / "docs/helicopter/H/browser.py",
        ROOT / "docs/map/E/verify_emcon_ui.py",
        ROOT / "docs/contact/friendly/A/cpu2d_ui.py",
        ROOT / "docs/envelope/D/run_observed_webgl.py",
        ROOT / "docs/helicopter/F/verify_regression.py",
        ROOT / "docs/damage/hp/A/run_contract_gate.py",
        HERE / "run_u4_scenes_candidate.py",
        HERE / "run_seeker_close_candidate.py",
        HERE / "build_seeker_close_diagnostic.py",
        *native_sources,
    ]
    tracked_docs = tracked_paths("docs")
    tracked_tests = tracked_paths("tests")
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    missing_tracked = [str(path.relative_to(ROOT)) for path in [*tracked_docs, *tracked_tests] if not path.exists()]
    previous = json.loads(PREVIOUS_STOP.read_text()) if PREVIOUS_STOP.is_file() else {}
    sparse = subprocess.check_output(["git", "sparse-checkout", "list"], cwd=ROOT, text=True).splitlines()
    suite_inputs = {}
    for name in [*NATIVE, "paired-hp-a", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes", "hp-contract", "seeker-close"]:
        script = next(Path(value) for value in command(name)[1:] if str(value).endswith(".py"))
        inputs = [PRODUCT, script]
        if name in NATIVE:
            inputs.extend([ROOT / "docs/pip/B/browser_backend.py", ROOT / "docs/map/A/verify_regressions.py", ROOT / "docs/viewport/A/verify_regressions.py", native_sources[list(NATIVE).index(name)]])
        if name == "helicopter-flight":
            inputs.append(HELI_CG_A)
        if name == "paired-hp-a":
            inputs.append(BASELINE)
        suite_inputs[name] = sorted({str(path.relative_to(ROOT)) for path in inputs})
    checks = {
        "productBytesPinned": PRODUCT.is_file() and PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": PRODUCT.is_file() and sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "baselineBytesPinned": BASELINE.is_file() and BASELINE.stat().st_size == BASELINE_BYTES,
        "baselineShaPinned": BASELINE.is_file() and sha256(BASELINE.read_bytes()) == BASELINE_SHA256,
        "heliCgFixtureBytesPinned": HELI_CG_A.is_file() and HELI_CG_A.stat().st_size == HELI_CG_A_BYTES,
        "heliCgFixtureShaPinned": HELI_CG_A.is_file() and sha256(HELI_CG_A.read_bytes()) == HELI_CG_A_SHA256,
        "previousAttemptPreserved": previous.get("classification") == "ZERO_ASSERTION_HARNESS_STOP" and previous.get("attempt") == 1,
        "allExplicitInputsPresent": not missing,
        "allTrackedDocsMaterialized": not [path for path in missing_tracked if path.startswith("docs/")],
        "allTrackedTestsMaterialized": not [path for path in missing_tracked if path.startswith("tests/")],
        "heliCgFixtureInSparseCheckout": "/archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html" in sparse,
        "suiteCountExact": len(suite_inputs) == 21,
    }
    payload = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_ATTEMPT_2_PREFLIGHT_1",
        "attempt": 2,
        "authorizedRerun": True,
        "checks": checks,
        "candidate": {"path": str(PRODUCT.relative_to(ROOT)), "bytes": PRODUCT_BYTES, "sha256": PRODUCT_SHA256},
        "baseline": {"path": str(BASELINE.relative_to(ROOT)), "bytes": BASELINE_BYTES, "sha256": BASELINE_SHA256},
        "indirectFixture": {"path": str(HELI_CG_A.relative_to(ROOT)), "bytes": HELI_CG_A_BYTES, "sha256": HELI_CG_A_SHA256},
        "sparseCheckoutPatterns": sparse,
        "trackedMaterialization": {"docsCount": len(tracked_docs), "testsCount": len(tracked_tests), "missing": missing_tracked},
        "explicitInputs": [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())} for path in sorted(set(required)) if path.is_file()],
        "suiteInputs": suite_inputs,
        "missingExplicitInputs": missing,
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "gameConstantsChanged": False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"attempt-2 preflight failed: {failed}; missing={missing}; tracked={missing_tracked[:20]}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
    preflight_result = preflight()
    names = [*NATIVE, "paired-hp-a", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes", "hp-contract", "seeker-close"]
    if args.dry_run:
        print(strict({"product": str(PRODUCT), "productBytes": PRODUCT_BYTES, "productSha256": PRODUCT_SHA256, "output": str(OUT), "attempt": 2, "authorizedRerun": True, "oneShot": True, "preflight": preflight_result, "jobs": {name: command(name) for name in names}, "broadRunCountOnDryRun": 0})); return
    OUT.mkdir(parents=True, exist_ok=True)
    assert not any(OUT.iterdir()), "final broad regression is one-shot; output directory must be empty"
    (OUT / "preflight-inputs.json").write_text(strict(preflight_result))
    started = time.perf_counter(); rows = [static_integrity()]; source_provenance(); write_summary(rows, started, False)
    for name in names:
        row = execute(name); rows.append(row); write_summary(rows, started, False)
        if row["executedAssertions"] == 0:
            raise SystemExit(f"zero-assertion suite: {name}")
        if row["status"] != "PASS":
            raise SystemExit(f"broad regression stopped on failure: {name}")
    result = write_summary(rows, started, True)
    raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__ == "__main__":
    main()
