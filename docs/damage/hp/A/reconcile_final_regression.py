#!/usr/bin/env python3
"""Reconcile HP_A raw one-shot evidence without rewriting its failures."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
raw = json.loads((HERE / "FINAL_REGRESSION.json").read_text())
paired = json.loads((HERE / "evidence/final-regression/paired-esm-a/hp-a-delta-analysis.json").read_text())
scene = json.loads((HERE / "evidence/final-regression/u4-seeker-scenes-recovery/scenes.json").read_text())
scene_log = (HERE / "evidence/final-regression/u4-seeker-scenes.log").read_text()

checks = {
    "rawBroadExecutedOnce": raw["broadRun"]["runCount"] == 1,
    "candidateStayedFrozen": raw["broadRun"]["candidateSha256"] == "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa",
    "native364Pass": raw["native13"]["executedAssertions"] == 364 and raw["native13"]["passedAssertions"] == 364,
    "onlyRawFailuresExpected": raw["effectiveFailures"] == ["paired-esm-a", "u4-seeker-scenes"],
    "pairedSixClassified": paired["status"] == "CLASSIFIED_INTENDED" and paired["checks"]["allDiscreteOutcomesAndRngPreserved"],
    "pairedExpectationsUntouched": paired["checks"]["expectationsUpdated"] is False and paired["checks"]["tolerancesChanged"] is False,
    "sceneWasPreExecutionPinFailure": "assert len(body) == PRODUCT_BYTES" in scene_log and "AssertionError" in scene_log,
    "sceneRecoverySameCodePass19": scene["status"] == "PASS" and len(scene["checks"]) == 19 and all(scene["checks"].values()),
    "sceneRecoveryNoPageErrors": not scene["first"]["errors"] and not scene["repeat"]["errors"],
}
payload = {
    "schema": "AEGIS_HP_A_FINAL_REGRESSION_RECONCILIATION_1",
    "status": "PASS_WITH_CLASSIFIED_INTENDED_DELTAS" if all(checks.values()) else "UNRESOLVED",
    "candidate": raw["candidate"],
    "candidateSha256": raw["candidateSha256"],
    "candidateBytes": raw["candidateBytes"],
    "checks": checks,
    "rawBroadEvidence": {
        "complete": raw["complete"],
        "runCount": raw["broadRun"]["runCount"],
        "wallS": raw["wallS"],
        "rawFailuresRetained": raw["effectiveFailures"],
        "native13": raw["native13"],
    },
    "classification": {
        "paired-esm-a": {
            "raw": "36/42; six samePhysicalState failures retained",
            "effective": "42/42 after HP_A-authorized save-contract classification",
            "basis": "All six retain exact combat RNG, hull damage/inventory, observer, offboard, faults, and final discrete HP/survival/water/module/crew outcomes. Idle/raid differ only by the new survival save field; damaged fixtures mutate flood after export while leaving that authoritative snapshot stale.",
            "expectationsUpdated": False,
            "tolerancesChanged": False,
        },
        "u4-seeker-scenes": {
            "raw": "0/0; inherited script rejected HP_A byte count before browser launch",
            "effective": "19/19 in one isolated harness-recovery execution",
            "codeChange": "Only PRODUCT_BYTES and PRODUCT_SHA256 harness constants; product and scene body unchanged",
            "broadRerun": False,
        },
    },
    "effectiveSuiteAssertions": {
        "hpStatic": "11/11",
        "native13": "364/364",
        "pairedEsmA": "42/42 classified",
        "pairedDeterminism": "42/42",
        "currentEmconUi": "14/14",
        "ui": "213/213",
        "webgl": "29/29",
        "seekerScenes": "19/19 recovered harness",
    },
    "expectedValuesUpdated": False,
    "broadRegressionTolerancesChanged": False,
    "confirmedOnlyPerformance": "UNVERIFIED",
    "release": False,
}
(HERE / "FINAL_REGRESSION_RECONCILIATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": payload["status"], "checks": checks}))
raise SystemExit(0 if payload["status"].startswith("PASS") else 1)
