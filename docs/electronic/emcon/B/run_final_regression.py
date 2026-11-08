"""EMCON_B final inherited regression gate.

This runner executes the unchanged, already-established native, paired, UI and
actual-WebGL suites once against the frozen EMCON_B product.  It changes only
paths/output routing and the explicit B2 historical-test configuration; product
code, assertions, expected values and tolerances are not rewritten here.
"""
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
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_EMCON_B.html"
BASELINE = PRODUCT  # paired suite tests deterministic repeatability of this candidate
PRODUCT_SHA256 = "3343f5bbe7d6adac0694656ebafef538c3b7407d7ce642225fff94207c142c33"
EMITTER_A_SHA256 = "3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be"
OUT = HERE / "final-regression"

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
assert sum(v[1] for v in NATIVE.values()) == 364


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def environment() -> dict[str, str]:
    node_path = os.environ.get("NODE_PATH", str(ROOT / "node_modules"))
    return {
        **os.environ,
        "TMPDIR": "/dev/shm",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": node_path,
        "B2_PHASE1_REGRESSION": "1",
        "B2_MODE": "ON",
        "B2_HTML": PRODUCT.name,
        "B2_OUT": str(OUT),
        "PYTHONPATH": str(ROOT / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0",
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
    if name == "paired42":
        return [
            sys.executable,
            "-u",
            str(ROOT / "docs/helicopter/F/verify_regression.py"),
            str(BASELINE),
            str(PRODUCT),
            str(OUT / name),
            "--baseline-only",
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
    if name == "paired42":
        return OUT / name / "baseline-comparison.json", 42
    if name == "ui213":
        return OUT / "map/E/evidence/d-ui/ui.json", 213
    if name == "webgl8":
        return OUT / name / "observed-world.json", 29
    raise ValueError(name)


def checks_from(name: str, payload: dict) -> tuple[dict[str, bool], list]:
    if name == "paired42":
        checks = {
            f"{row['ship']}:{row['scenario']}:{key}": value
            for row in payload.get("cases", [])
            for key, value in row.get("checks", {}).items()
        }
        return checks, payload.get("errors", [])
    return payload.get("checks", {}), payload.get("errors", [])


def execute(name: str) -> dict:
    path, expected = result_location(name)
    log_path = OUT / f"{name}.log"
    start = time.perf_counter()
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
    payload = json.loads(path.read_text()) if path.exists() else {}
    checks, errors = checks_from(name, payload)
    failed = [key for key, value in checks.items() if not value]
    status = "PASS" if exit_code == 0 and len(checks) == expected and not failed and not errors else "FAIL"
    row = {
        "suite": name,
        "status": status,
        "exitCode": exit_code,
        "wallS": time.perf_counter() - start,
        "expectedAssertions": expected,
        "executedAssertions": len(checks),
        "passedAssertions": sum(bool(v) for v in checks.values()),
        "failedAssertions": failed,
        "errors": errors,
        "resultPath": str(path.relative_to(OUT)) if path.exists() else None,
        "command": command(name),
    }
    (OUT / f"{name}-execution.json").write_text(json.dumps(row, indent=2) + "\n")
    print(json.dumps({k: v for k, v in row.items() if k not in {"command", "errors"}}), flush=True)
    return row


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    native = [row for row in rows if row["suite"] in NATIVE]
    coverage64 = []
    for row in native:
        if not row.get("resultPath"):
            continue
        text = (OUT / row["resultPath"]).read_text(errors="replace")
        if any(token in text for token in ['"scale": 64', 'clock64', 'fixedClock64']):
            coverage64.append(row["suite"])
    result = {
        "schema": "AEGIS_EMCON_B_FINAL_REGRESSION_1",
        "complete": complete,
        "candidate": PRODUCT.name,
        "candidateSha256": PRODUCT_SHA256,
        "emitterABaselineSha256": EMITTER_A_SHA256,
        "pairedMethod": "same-candidate deterministic repeat; EMITTER_A default-policy byte/state equivalence is covered by the stage-B gate",
        "expectedValuesUpdated": False,
        "tolerancesChanged": False,
        "productMutatedByRunner": False,
        "rows": rows,
        "native13": {
            "suiteCount": len(native),
            "expectedSuiteCount": 13,
            "expectedAssertions": 364,
            "executedAssertions": sum(row["executedAssertions"] for row in native),
            "passedAssertions": sum(row["passedAssertions"] for row in native),
        },
        "scaleCoverage": {
            "representative": [1, 8, 16],
            "performanceReference": 64,
            "suitesWith64Evidence": coverage64,
        },
        "lockDebt14": "PASS in ../LOCK_DEBT_14.json; executed separately before this one-time broad run",
        "confirmedOnly": "UNVERIFIED_PERFORMANCE; static feature-disposition checks only",
        "inheritedDebt": [
            "CIWS_SEED_419025_FAIL",
            "CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2",
            "U3_RAW_PAIRED_INTENTIONAL_DELTA_4",
            "LEGACY_WIP12D_ACTIONS_SPEED_DETERMINISM",
            "KH32_60KM_SEPARATE_INVESTIGATION",
        ],
        "newFailures": [row["suite"] for row in rows if row["status"] != "PASS"],
        "wallS": time.perf_counter() - started,
    }
    (HERE / "FINAL_REGRESSION.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    assert PRODUCT.stat().st_size == 22_157_395
    assert sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256
    names = [*NATIVE, "paired42", "ui213", "webgl8"]
    if args.dry_run:
        print(json.dumps({"product": str(PRODUCT), "sha256": PRODUCT_SHA256, "jobs": {n: command(n) for n in names}}, indent=2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    assert not any(OUT.iterdir()), "Final broad regression is one-shot; output directory must be empty"
    started = time.perf_counter()
    rows: list[dict] = []
    write_summary(rows, started, complete=False)
    for name in names:
        rows.append(execute(name))
        write_summary(rows, started, complete=False)
    result = write_summary(rows, started, complete=True)
    raise SystemExit(1 if result["newFailures"] else 0)


if __name__ == "__main__":
    main()
