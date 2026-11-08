#!/usr/bin/env python3
"""Execute the one and only final MAX_THREAT broad regression for U4."""
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
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html"
BASELINE = ROOT / "Aegis_SIM_v48_WIP_ESM_A.html"
HELI_CG_A_BASELINE = ROOT / "archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html"
MULTISHIP_H4_SOURCE = ROOT / "docs/multiship/H4/regression_baseline.py"
GUN_B1_UI_SOURCE = ROOT / "docs/gun/B1/run_test_migrations.py"
TEST_SUPPORT = ROOT / "docs/gun/B2/phase1b/test_support/sitecustomize.py"
PRODUCT_SHA256 = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"
PRODUCT_BYTES = 22_195_923
BASELINE_SHA256 = "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7"
BASELINE_BYTES = 22_182_527
HELI_CG_A_BASELINE_SHA256 = "c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3"
MULTISHIP_H4_SOURCE_SHA256 = "9c1c7239f31e9a0a15f3d752ab9a2925729758fd0f23fb879d5b7ec6e90479e0"
GUN_B1_UI_SOURCE_SHA256 = "b8a05458a594a45fb4b91abceda5a0be782c195f722179d800f0e4e8a76b4a75"
TEST_SUPPORT_SHA256 = "522af70b9d84a5595187a285d29182bf1b277837b579e6f917d14f3f61750be5"
OUT = HERE / "evidence" / "final-regression"
SUMMARY = HERE / "FINAL_REGRESSION.json"

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
        return [sys.executable, "-u", str(ROOT / "docs/pip/B/run_domain.py"), str(PRODUCT), str(OUT / name), "--only", name]
    if name == "paired-esm-a":
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
        return [sys.executable, "-u", str(HERE / "run_u4_final_scenes.py"), str(PRODUCT), str(OUT / name / "scenes.json")]
    raise ValueError(name)


def result_location(name: str) -> tuple[Path, int]:
    if name in NATIVE:
        return OUT / name / NATIVE[name][0], NATIVE[name][1]
    if name in {"paired-esm-a", "paired-determinism"}:
        return OUT / name / "baseline-comparison.json", 42
    if name == "current-emcon-ui":
        return OUT / name / "ui.json", 14
    if name == "ui213":
        return OUT / "map/E/evidence/d-ui/ui.json", 213
    if name == "webgl8":
        return OUT / name / "observed-world.json", 29
    if name == "u4-seeker-scenes":
        return OUT / name / "scenes.json", 19
    raise ValueError(name)


def paired_checks(payload: dict) -> dict[str, bool]:
    return {
        f"{row['ship']}:{row['scenario']}:{key}": bool(value)
        for row in payload.get("cases", [])
        for key, value in row.get("checks", {}).items()
    }


def extract(name: str, exit_code: int) -> dict:
    path, expected = result_location(name)
    payload = json.loads(path.read_text()) if path.exists() else {}
    errors = payload.get("errors", [])
    if name.startswith("paired-"):
        checks = paired_checks(payload)
    else:
        checks = payload.get("checks", {})
    failed = [key for key, value in checks.items() if not value]
    passed = sum(bool(value) for value in checks.values())
    status = "PASS" if exit_code == 0 and len(checks) == expected and not failed and not errors else "FAIL"
    return {
        "status": status,
        "expectedAssertions": expected,
        "executedAssertions": len(checks),
        "passedAssertions": passed,
        "failedAssertions": failed,
        "errors": errors,
        "resultPath": str(path.relative_to(OUT)) if path.exists() else None,
    }


def execute(name: str) -> dict:
    assert PRODUCT.stat().st_size == PRODUCT_BYTES
    assert sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    log_path = OUT / f"{name}.log"
    started = time.perf_counter()
    with log_path.open("w") as log:
        try:
            proc = subprocess.run(
                command(name), cwd=ROOT, env=environment(), stdout=log,
                stderr=subprocess.STDOUT, timeout=1_800,
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
    print(strict({k: v for k, v in row.items() if k not in {"command", "errors"}}), flush=True)
    return row


def static_integrity() -> dict:
    build = json.loads((HERE / "BUILD_FINAL.json").read_text())
    gates = {name: json.loads((HERE / f"{name}_GATE.json").read_text()) for name in ("A", "B", "C")}
    u3_c = json.loads((HERE.parent / "U3/C_CORRECTION_GATE.json").read_text())
    u3_d = json.loads((HERE.parent / "U3/D_CORRECTION_GATE.json").read_text())
    module_paths = {
        "A": HERE / "sarh_adapter_a.js",
        "B": HERE / "ram_adapter_b.js",
        "C": HERE / "association_state_c.js",
    }
    module_hashes = {key: sha256(path.read_bytes()) for key, path in module_paths.items()}
    build_source = (HERE / "build_product.py").read_text()
    checks = {
        "productBytesPinned": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "baselineBytesPinned": BASELINE.stat().st_size == BASELINE_BYTES,
        "baselineShaPinned": sha256(BASELINE.read_bytes()) == BASELINE_SHA256,
        "buildOutputPinned": build.get("outputSha256") == PRODUCT_SHA256 and build.get("outputBytes") == PRODUCT_BYTES,
        "buildActiveThroughC": build.get("through") == "C" and build.get("mode") == "ACTIVE",
        "moduleHashesPinned": module_hashes == build.get("moduleSha256"),
        "unchangedFunctionsExact": all(row.get("same") is True for row in build.get("unchangedFunctions", {}).values()),
        "limitedGatesPass": all(gate.get("status") == "PASS" for gate in gates.values()),
        "limitedGatesDidNotRunBroad": all(gate.get("broadRegressionRun") is False for gate in gates.values()),
        "commonAssociationActive": build.get("mode") == "ACTIVE"
        and "commonStateMode:'ACTIVE'" in build_source,
        "noU4SaveSchemaMarker": gates["C"].get("checks", {}).get("rngAndSavePreserved") is True,
        "u3ConfirmedOnlyStaticInherited": u3_c.get("status") == "PASS" and u3_d.get("status") == "PASS"
        and str(u3_c.get("confirmedOnlyPerformance", "")).startswith("UNVERIFIED")
        and str(u3_d.get("confirmedOnlyPerformance", "")).startswith("UNVERIFIED"),
    }
    failed = [key for key, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_FINAL_STATIC_1",
        "checks": checks,
        "moduleHashes": module_hashes,
        "unchangedFunctions": build.get("unchangedFunctions", {}),
        "limitedGateStatus": {name: gate.get("status") for name, gate in gates.items()},
        "confirmedOnlyPerformance": "UNVERIFIED",
        "errors": [],
    }
    path = OUT / "static-integrity.json"
    path.write_text(strict(payload))
    return {
        "suite": "static-integrity",
        "status": "PASS" if not failed else "FAIL",
        "exitCode": 0 if not failed else 1,
        "wallS": 0,
        "expectedAssertions": len(checks),
        "executedAssertions": len(checks),
        "passedAssertions": sum(checks.values()),
        "failedAssertions": failed,
        "errors": [],
        "resultPath": str(path.relative_to(OUT)),
    }


def source_provenance() -> None:
    files = [
        ROOT / "docs/pip/B/run_domain.py",
        ROOT / "docs/map/E/verify_emcon_ui.py",
        ROOT / "docs/contact/friendly/A/cpu2d_ui.py",
        ROOT / "docs/envelope/D/run_observed_webgl.py",
        ROOT / "docs/helicopter/F/verify_regression.py",
        HERE / "run_u4_final_scenes.py",
        HELI_CG_A_BASELINE,
        MULTISHIP_H4_SOURCE,
        GUN_B1_UI_SOURCE,
        TEST_SUPPORT,
    ]
    payload = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_FINAL_SOURCE_PROVENANCE_1",
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "baselineSha256": BASELINE_SHA256,
        "threatMode": "MAX_THREAT",
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes())} for path in files],
    }
    (OUT / "source-provenance.json").write_text(strict(payload))


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    native = [row for row in rows if row["suite"] in NATIVE]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_FINAL_REGRESSION_1",
        "complete": complete,
        "candidate": PRODUCT.name,
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "baseline": BASELINE.name,
        "baselineSha256": BASELINE_SHA256,
        "threatAssumptionMode": "MAX_THREAT",
        "broadRun": {"runCount": 1, "candidateFrozen": True, "candidateSha256": PRODUCT_SHA256},
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "rows": rows,
        "native13": {
            "suiteCount": len(native), "expectedSuiteCount": 13, "expectedAssertions": 364,
            "executedAssertions": sum(row["executedAssertions"] for row in native),
            "passedAssertions": sum(row["passedAssertions"] for row in native),
        },
        "coverage": {
            "representativeRealFlights": ["u4-seeker-scenes", "harpoon-f1"],
            "pairedDdgCgIdleRaidDamaged": ["paired-esm-a", "paired-determinism"],
            "saveLoadResetDestroyRetire": ["helicopter-flight", "harpoon-f1", "sov-native", "u4-seeker-scenes"],
            "emconAndEsmUi": ["current-emcon-ui", "ui213", "u4-seeker-scenes"],
            "clock": ["isar-clock", "harpoon-clock", "u4-seeker-scenes"],
            "chromiumUi": ["ui213", "current-emcon-ui"],
            "actualWebgl": "webgl8",
        },
        "confirmedOnly": {"staticAndLimitedFeatureOffEvidence": "INHERITED_PASS", "performance": "UNVERIFIED"},
        "effectiveFailures": failures,
        "wallS": time.perf_counter() - started,
        "release": False,
    }
    SUMMARY.write_text(strict(result))
    return result


def preflight() -> None:
    assert PRODUCT.stat().st_size == PRODUCT_BYTES
    assert sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    assert BASELINE.stat().st_size == BASELINE_BYTES
    assert sha256(BASELINE.read_bytes()) == BASELINE_SHA256
    assert sha256(HELI_CG_A_BASELINE.read_bytes()) == HELI_CG_A_BASELINE_SHA256
    assert sha256(MULTISHIP_H4_SOURCE.read_bytes()) == MULTISHIP_H4_SOURCE_SHA256
    assert sha256(GUN_B1_UI_SOURCE.read_bytes()) == GUN_B1_UI_SOURCE_SHA256
    assert sha256(TEST_SUPPORT.read_bytes()) == TEST_SUPPORT_SHA256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    preflight()
    names = [*NATIVE, "paired-esm-a", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes"]
    if args.dry_run:
        print(strict({
            "product": str(PRODUCT), "productBytes": PRODUCT_BYTES, "productSha256": PRODUCT_SHA256,
            "baselineSha256": BASELINE_SHA256, "output": str(OUT), "oneShot": True,
            "jobs": {name: command(name) for name in names}, "staticSuite": "static-integrity",
            "broadRunCountOnDryRun": 0,
        }))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    assert not any(OUT.iterdir()), "U4 final broad regression is one-shot; output directory must be empty"
    started = time.perf_counter()
    rows = [static_integrity()]
    source_provenance()
    write_summary(rows, started, complete=False)
    # Deliberately execute every suite once. A failing row blocks packaging, but
    # cannot be repaired by rerunning or weakening the remaining broad evidence.
    for name in names:
        rows.append(execute(name))
        write_summary(rows, started, complete=False)
    result = write_summary(rows, started, complete=True)
    raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__ == "__main__":
    main()
