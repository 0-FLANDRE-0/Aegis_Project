#!/usr/bin/env python3
"""Execute HP_A's one and only frozen-candidate MAX_THREAT broad regression."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_HP_A.html"
PRODUCT_BYTES = 22_200_135
PRODUCT_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"
OUT = HERE / "evidence" / "final-regression"
SUMMARY = HERE / "FINAL_REGRESSION.json"
U4_RUNNER = ROOT / "docs/missile/seeker-unify/U4/run_final_regression.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


spec = importlib.util.spec_from_file_location("hp_a_inherited_u4_final", U4_RUNNER)
assert spec and spec.loader
u4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u4)
u4.PRODUCT = PRODUCT
u4.PRODUCT_BYTES = PRODUCT_BYTES
u4.PRODUCT_SHA256 = PRODUCT_SHA256
u4.OUT = OUT
u4.SUMMARY = SUMMARY


def hp_static_integrity() -> dict:
    build = json.loads((HERE / "evidence/commit-c/build-receipt.json").read_text())
    audit = json.loads((HERE / "evidence/commit-c/candidate-audit.json").read_text())
    contract = json.loads((HERE / "evidence/commit-c/contract-gate.json").read_text())
    u4_build = json.loads((ROOT / "docs/missile/seeker-unify/U4/BUILD_FINAL.json").read_text())
    u4_gates = {
        name: json.loads((ROOT / f"docs/missile/seeker-unify/U4/{name}_GATE.json").read_text())
        for name in ("A", "B", "C")
    }
    u3_c = json.loads((ROOT / "docs/missile/seeker-unify/U3/C_CORRECTION_GATE.json").read_text())
    u3_d = json.loads((ROOT / "docs/missile/seeker-unify/U3/D_CORRECTION_GATE.json").read_text())
    checks = {
        "productBytesPinned": PRODUCT.stat().st_size == PRODUCT_BYTES,
        "productShaPinned": sha256(PRODUCT.read_bytes()) == PRODUCT_SHA256,
        "buildPhaseC": build.get("phase") == "C",
        "buildOutputPinned": build.get("outputBytes") == PRODUCT_BYTES and build.get("outputSha256") == PRODUCT_SHA256,
        "protectedPhysicsHashesExact": build.get("protectedFunctionHashesExact") is True,
        "candidateAuthorityAuditPass": audit.get("status") == "PASS" and audit.get("candidateInvalidAuthorityUseCount") == 0,
        "boundedContractGatePass": contract.get("status") == "PASS" and not contract.get("errors"),
        "u4BaseBuildInheritedPass": u4_build.get("outputSha256") == "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498",
        "u4LimitedGatesInheritedPass": all(gate.get("status") == "PASS" for gate in u4_gates.values()),
        "u4LimitedGatesDidNotRunBroad": all(gate.get("broadRegressionRun") is False for gate in u4_gates.values()),
        "confirmedOnlyStaticInherited": u3_c.get("status") == "PASS" and u3_d.get("status") == "PASS"
        and str(u3_c.get("confirmedOnlyPerformance", "")).startswith("UNVERIFIED")
        and str(u3_d.get("confirmedOnlyPerformance", "")).startswith("UNVERIFIED"),
    }
    failed = [key for key, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_HP_A_FINAL_STATIC_1",
        "checks": checks,
        "candidateAudit": str((HERE / "evidence/commit-c/candidate-audit.json").relative_to(ROOT)),
        "boundedContractGate": str((HERE / "evidence/commit-c/contract-gate.json").relative_to(ROOT)),
        "protectedFunctionHashes": build.get("protectedFunctionHashesAfter"),
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


def hp_source_provenance() -> None:
    inherited = [
        ROOT / "docs/pip/B/run_domain.py",
        ROOT / "docs/map/E/verify_emcon_ui.py",
        ROOT / "docs/contact/friendly/A/cpu2d_ui.py",
        ROOT / "docs/envelope/D/run_observed_webgl.py",
        ROOT / "docs/helicopter/F/verify_regression.py",
        ROOT / "docs/missile/seeker-unify/U4/run_u4_final_scenes.py",
        U4_RUNNER,
    ]
    local = [
        HERE / "build_product.py",
        HERE / "outcome_contract_a.js",
        HERE / "audit_candidate.py",
        HERE / "run_contract_gate.py",
    ]
    payload = {
        "schema": "AEGIS_HP_A_FINAL_SOURCE_PROVENANCE_1",
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "baseMain": "82617839e64ea6b70d33ca55b13b3114cca62f3e",
        "baseProductSha256": "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498",
        "threatMode": "MAX_THREAT",
        "expectedValuesUpdated": False,
        "broadRegressionTolerancesChanged": False,
        "files": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes()), "role": "HP_A" if path in local else "INHERITED_U4"}
            for path in [*local, *inherited]
        ],
    }
    (OUT / "source-provenance.json").write_text(strict(payload))


def hp_write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    native = [row for row in rows if row["suite"] in u4.NATIVE]
    result = {
        "schema": "AEGIS_HP_A_FINAL_REGRESSION_1",
        "complete": complete,
        "candidate": PRODUCT.name,
        "candidateSha256": PRODUCT_SHA256,
        "candidateBytes": PRODUCT_BYTES,
        "base": "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html",
        "baseSha256": "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498",
        "threatAssumptionMode": "MAX_THREAT",
        "broadRun": {"runCount": 1, "candidateFrozen": True, "candidateSha256": PRODUCT_SHA256},
        "expectedValuesUpdated": False,
        "broadRegressionTolerancesChanged": False,
        "rows": rows,
        "native13": {
            "suiteCount": len(native), "expectedSuiteCount": 13, "expectedAssertions": 364,
            "executedAssertions": sum(row["executedAssertions"] for row in native),
            "passedAssertions": sum(row["passedAssertions"] for row in native),
        },
        "coverage": {
            "hpAuthorityContract": "static-integrity + commit-c/contract-gate.json",
            "representativeRealFlights": ["u4-seeker-scenes", "harpoon-f1"],
            "pairedDdgCgIdleRaidDamaged": ["paired-esm-a", "paired-determinism"],
            "saveLoadResetDestroyRetire": ["helicopter-flight", "harpoon-f1", "sov-native", "u4-seeker-scenes"],
            "emconAndEsmUi": ["current-emcon-ui", "ui213", "u4-seeker-scenes"],
            "clock": ["isar-clock", "harpoon-clock", "u4-seeker-scenes"],
            "actualWebgl": "webgl8",
        },
        "confirmedOnly": {"staticAndLimitedFeatureOffEvidence": "INHERITED_PASS", "performance": "UNVERIFIED"},
        "effectiveFailures": failures,
        "wallS": time.perf_counter() - started,
        "release": False,
    }
    SUMMARY.write_text(strict(result))
    return result


u4.static_integrity = hp_static_integrity
u4.source_provenance = hp_source_provenance
u4.write_summary = hp_write_summary


if __name__ == "__main__":
    u4.main()
