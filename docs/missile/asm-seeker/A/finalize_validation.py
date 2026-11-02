#!/usr/bin/env python3
"""Build the immutable ASM_SEEKER_A validation receipt from recorded evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
BASELINE = ROOT / "Aegis_SIM_v48_WIP_TRACK_C.html"


def load(name: str):
    return json.loads((HERE / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


build = load("BUILD.json")
scope = load("SCOPE.json")
s2 = load("S2_RESULTS.json")
s3 = load("S3_BATTLE_RESULTS.json")
root_cause = load("EGRESS_ROOT_CAUSE.json")
replay = load("REPLAY_DETERMINISM.json")
regression = load("REGRESSION_RESULTS.json")

rows = {row["suite"]: row for row in regression["rows"]}
native = regression["native13"]
product_text = PRODUCT.read_text(errors="strict")

checks = {
    "baselinePinned": sha(BASELINE) == build["baselineHtmlSha256"],
    "productHashMatchesBuild": sha(PRODUCT) == build["outputHtmlSha256"],
    "oneProductChange": scope["productChangeCount"] == 1,
    "reverseReplacementRestoresBaseline": scope["sourceTransformationProof"]["reverseReplacementRestoresBaselineMainExactly"],
    "noNewTuningConstants": scope["newTuningConstants"] == [],
    "noTruthOrEntityIdentityConsumed": scope["truthOrEntityIdentityConsumed"] is False,
    "noDiagnosticApiInProduct": "__ASM_SEEKER_A_DIAG__" not in product_text,
    "noAfterActionHelperInProduct": "afterAction" not in product_text,
    "noTargetEntityTeamIdentityTokensInProduct": all(token not in product_text for token in ("targetId", "entityId", "teamId")),
    "observerComparableJsonByteExact": replay["comparison"]["byteEqualComparableJson"] is True,
    "observerComparableShaEqual": replay["comparison"]["baselineSha256"] == replay["comparison"]["diagnosticSha256"],
    "confirmedRootCause": root_cause["status"] == "CONFIRMED_CODE_DEFECT" and root_cause["sampleCount"] == 37,
    "s2Pass": s2["status"] == "PASS" and not s2["pageErrors"],
    "s3Pass": s3["status"] == "PASS" and s3["jobs"] == s3["expectedJobs"] == 60,
    "s3PopulationConserved": sum(s3["totals"].values()) == sum(s3["baselineTotals"].values()) == 320,
    "s3ImproperEgressRemoved": s3["baselineTotals"]["egress"] == 37 and s3["totals"]["egress"] == 0,
    "native13Pass": native["suiteCount"] == 13 and native["passedAssertions"] == native["expectedAssertions"] == 364,
    "ui213Pass": rows["ui213"]["status"] == "PASS" and rows["ui213"]["passedAssertions"] == 213,
    "webgl8Pass": rows["webgl8"]["status"] == "PASS" and rows["webgl8"]["passedAssertions"] == 29,
    "noNewRegressionFailures": regression["newFailures"] == [],
    "onlyKnownRetiredIncomplete": regression["incomplete"] == ["emcon-ui"],
}

result = {
    "schema": "AEGIS_ASM_SEEKER_A_VALIDATION_1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "baselineCommit": build["baselineCommit"],
    "baselineHtml": build["baselineHtml"],
    "baselineHtmlSha256": build["baselineHtmlSha256"],
    "productHtml": build["outputHtml"],
    "productHtmlSha256": build["outputHtmlSha256"],
    "productPackedMainSha256": build["outputMainSha256"],
    "checks": checks,
    "rootCause": {
        "qualifiedEgressSamples": root_cause["sampleCount"],
        "category": root_cause["category"],
        "subtype": root_cause["subtype"],
        "firstAssociationFamilies": root_cause["firstAssociationFamilies"],
        "damageBeforeFirstTrack": root_cause["damageBeforeFirstConfirmedTrack"],
    },
    "s2": {
        "status": s2["status"],
        "elapsedS": s2["elapsedS"],
        "pageErrors": s2["pageErrors"],
        "unresolved": "45 km small-surface-target acquisition remained 0/50; RF/evidence coefficients deliberately unchanged.",
    },
    "s3": {
        "status": s3["status"],
        "battles": s3["jobs"],
        "baseline": s3["baselineTotals"],
        "product": s3["totals"],
        "elapsedS": s3["elapsedS"],
    },
    "broadRegression": {
        "native13": native,
        "ui213": {k: rows["ui213"].get(k) for k in ("status", "expectedAssertions", "executedAssertions", "passedAssertions", "wallS")},
        "webgl8": {k: rows["webgl8"].get(k) for k in ("status", "expectedAssertions", "executedAssertions", "passedAssertions", "wallS")},
        "newFailures": regression["newFailures"],
        "knownRetiredDebt": {
            "suite": "emcon-ui",
            "assertions": 14,
            "status": "INCOMPLETE",
            "reason": rows["emcon-ui"]["reason"],
        },
    },
    "releaseDecision": {
        "approvedByDirective": all(checks.values()),
        "mergeAllowed": all(checks.values()),
        "releaseOrTagAllowed": False,
    },
}

(HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"status": result["status"], "checks": checks}, indent=2, ensure_ascii=False))
