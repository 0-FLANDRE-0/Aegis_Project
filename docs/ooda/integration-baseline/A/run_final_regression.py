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
PRODUCT_BYTES = 22_211_451
PRODUCT_SHA256 = "baf96f9a1350973d045c9ad4f9025a86c10eaeda3c1924ad52498c45b90d0b5b"
BASELINE_BYTES = 22_200_135
BASELINE_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"
OUT = HERE / "evidence" / "final-regression"
SUMMARY = HERE / "FINAL_REGRESSION.json"

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
    c_gate = json.loads((HERE / "C_GATE.json").read_text())
    baseline_oracle = json.loads((HERE / "BASELINE_ORACLE.json").read_text())
    candidate_oracle = json.loads((HERE / "CANDIDATE_ORACLE.json").read_text())
    contract = json.loads((HERE / "CONTRACT_ORACLE.json").read_text())
    repeat = json.loads((HERE / "CONTRACT_ORACLE_REPEAT.json").read_text())
    baseline_hashes = json.loads((HERE / "FUNCTION_HASHES.json").read_text())["functions"]
    candidate_hashes = json.loads((HERE / "FUNCTION_HASHES_CANDIDATE.json").read_text())["functions"]
    common = set(baseline_hashes) & set(candidate_hashes)
    changed = sorted(name for name in common if baseline_hashes[name] != candidate_hashes[name])
    new = sorted(set(candidate_hashes) - set(baseline_hashes))
    checks = {
        "productBytesPinned": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "baselineBytesPinned": BASELINE.stat().st_size == BASELINE_BYTES,
        "baselineShaPinned": sha256(BASELINE.read_bytes()) == BASELINE_SHA256,
        "commitCGatePass": c_gate.get("status") == "PASS",
        "baselineCandidateOracleExact": baseline_oracle["deterministicDigest"] == candidate_oracle["deterministicDigest"],
        "contractRepeatExact": contract["deterministicDigest"] == repeat["deterministicDigest"],
        "shadowMismatchZero": all((row[side]["diagnostics"]["shadowMismatchCount"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "rngMismatchZero": all((row[side]["diagnostics"]["rngMismatchCount"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "truthAuditZero": all((row[side]["diagnostics"]["truthAuditFailures"] == 0) for row in contract["owners"] for side in ("active", "foreign")),
        "readOnlyInputExact": all(row["readOnly"]["rngExact"] and row["readOnly"]["saveExact"] for row in contract["owners"]),
        "protectedHashesExact": changed == ["wip118BuildEngagementControl"],
        "newContractFunctionsExact": len(new) == 6 and all(name.startswith("defenseDecision") for name in new),
        "noSaveSchemaFields": all(row["provider"]["saveFields"] == 0 for row in contract["owners"]),
    }
    failed = [key for key, value in checks.items() if not value]
    payload = {"schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_STATIC_1", "checks": checks, "intentionalChangedFunctions": changed, "newFunctions": new, "errors": []}
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
    payload = {"schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_SOURCE_PROVENANCE_1", "candidateSha256": PRODUCT_SHA256, "candidateBytes": PRODUCT_BYTES, "baselineSha256": BASELINE_SHA256, "threatMode": "MAX_THREAT", "expectedValuesUpdated": False, "tolerancesChanged": False, "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes())} for path in files]}
    (OUT / "source-provenance.json").write_text(strict(payload))


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    native = [row for row in rows if row["suite"] in NATIVE]
    result = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_FINAL_REGRESSION_1", "complete": complete,
        "candidate": PRODUCT.name, "candidateSha256": PRODUCT_SHA256, "candidateBytes": PRODUCT_BYTES,
        "baseline": BASELINE.name, "baselineSha256": BASELINE_SHA256, "threatAssumptionMode": "MAX_THREAT",
        "broadRun": {"runCount": 1, "candidateFrozen": True, "candidateSha256": PRODUCT_SHA256},
        "expectedValuesUpdated": False, "tolerancesChanged": False, "rows": rows,
        "native13": {"suiteCount": len(native), "expectedSuiteCount": 13, "expectedAssertions": 364, "executedAssertions": sum(row["executedAssertions"] for row in native), "passedAssertions": sum(row["passedAssertions"] for row in native)},
        "coverage": {"decisionContract": "static-integrity + contract oracle", "hpOutcomeSave": "hp-contract", "seekerCloseNineteenShots": "seeker-close", "representativeRealFlights": ["u4-seeker-scenes", "harpoon-f1"], "pairedDdgCg": ["paired-hp-a", "paired-determinism"], "emconAndEsm": ["current-emcon-ui", "seeker-close"], "browserUi": "ui213", "actualWebgl": "webgl8"},
        "confirmedOnly": {"staticAndLimitedFeatureOffEvidence": "INHERITED_PASS", "performance": "UNVERIFIED"},
        "effectiveFailures": failures, "wallS": time.perf_counter() - started, "release": False,
    }
    SUMMARY.write_text(strict(result)); return result


def preflight() -> None:
    assert PRODUCT.stat().st_size == PRODUCT_BYTES and sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    assert BASELINE.stat().st_size == BASELINE_BYTES and sha256(BASELINE.read_bytes()) == BASELINE_SHA256


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
    preflight()
    names = [*NATIVE, "paired-hp-a", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes", "hp-contract", "seeker-close"]
    if args.dry_run:
        print(strict({"product": str(PRODUCT), "productBytes": PRODUCT_BYTES, "productSha256": PRODUCT_SHA256, "output": str(OUT), "oneShot": True, "jobs": {name: command(name) for name in names}, "broadRunCountOnDryRun": 0})); return
    OUT.mkdir(parents=True, exist_ok=True)
    assert not any(OUT.iterdir()), "final broad regression is one-shot; output directory must be empty"
    started = time.perf_counter(); rows = [static_integrity()]; source_provenance(); write_summary(rows, started, False)
    for name in names:
        rows.append(execute(name)); write_summary(rows, started, False)
    result = write_summary(rows, started, True)
    raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__ == "__main__":
    main()
