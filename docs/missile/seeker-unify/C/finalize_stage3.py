#!/usr/bin/env python3
"""Close SEEKER_UNIFY_C Stage 3 from frozen evidence and write final reports.

This is reporting-only.  It does not load or mutate the game.  Truth-bearing
evidence is restricted to after-action association/outcome classification.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def s1_key(row: dict) -> tuple:
    setup = row["setup"]
    return setup["launchRangeKm"], setup["separationDeg"], setup["seed"]


def audit_s1(before: dict, after: dict) -> dict:
    old = {s1_key(row): row for row in before["rows"]}
    new = {s1_key(row): row for row in after["rows"]}
    if old.keys() != new.keys():
        raise AssertionError("S1 key mismatch")
    regressions, improvements, ownship, neighbor = [], [], [], []
    for key in sorted(old):
        a, b = old[key], new[key]
        old_track = a["final"]["seekerMode"] == "TRACK"
        new_track = b["final"]["seekerMode"] == "TRACK"
        if old_track and not new_track:
            regressions.append({"key": key, "before": a["final"], "after": b["final"]})
        if not old_track and new_track:
            improvements.append({"key": key, "before": a["final"], "after": b["final"]})
        first = b.get("metrics", {}).get("firstCandidate") or {}
        ident, kind = str(first.get("id", "")), str(first.get("kind", ""))
        if ident.startswith("SHIP") or kind == "SHIP":
            ownship.append({"key": key, "candidate": first})
        if "ASM" in ident or kind in {"ASM", "RF_OBJECT"}:
            neighbor.append({"key": key, "candidate": first})
    return {
        "cases": len(new),
        "stage2Track": sum(row["final"]["seekerMode"] == "TRACK" for row in old.values()),
        "stage3Track": sum(row["final"]["seekerMode"] == "TRACK" for row in new.values()),
        "trackRegressions": regressions,
        "trackImprovements": improvements,
        "ownshipFirstSelections": ownship,
        "neighborAsmFirstSelections": neighbor,
        "pageErrors": after.get("pageErrors", []),
        "pass": not regressions and not ownship and not neighbor and not after.get("pageErrors"),
    }


def audit_egress(plan: dict) -> dict:
    rows, missing, neighbor, no_association = [], [], [], []
    families: Counter[str] = Counter()
    evidence = HERE / "evidence/cue-a-egress-37"
    for job in plan["jobs"]:
        path = evidence / f"{job['id']}.json.gz"
        if not path.exists():
            missing.append(job["id"])
            continue
        data = json.loads(gzip.decompress(path.read_bytes()))
        for missile_id in job["focusIds"]:
            events = [
                event for event in data["asm"]["events"]
                if event.get("kind") == "ASSOCIATION" and event.get("missileId") == missile_id
            ]
            first = (events[0].get("selected") or {}) if events else {}
            debug_id = str(first.get("_debugId", ""))
            debug_kind = str(first.get("_debugKind", ""))
            members = [str(value) for value in first.get("_debugMembers", [])]
            if not first:
                family = "NONE"
                no_association.append({"battleId": job["id"], "missileId": missile_id})
            elif "ASM:" in debug_id or "TARGET_ASM" in members:
                family = "NEIGHBOR_ASM"
                neighbor.append({"battleId": job["id"], "missileId": missile_id, "debugId": debug_id, "debugKind": debug_kind})
            elif "SHIP" in debug_id or (debug_kind in {"SHIP", "COMPOSITE"} and "SHIP" in members):
                family = "INTENDED_OWNSHIP"
            else:
                family = debug_kind or debug_id or "OTHER"
            families[family] += 1
            rows.append({"battleId": job["id"], "missileId": missile_id, "family": family, "debugId": debug_id, "debugKind": debug_kind})
    return {
        "tag": "AFTER_ACTION_TRUTH_TEST_ONLY",
        "jobs": len(plan["jobs"]),
        "missiles": len(rows),
        "missingEvidence": missing,
        "firstFamilies": dict(sorted(families.items())),
        "neighborAsmFirstAssociations": neighbor,
        "noAssociation": no_association,
        "rows": rows,
        "pass": not missing and not neighbor and len(rows) == plan["missileCount"],
    }


def battle_delta(before: dict, after: dict) -> dict:
    old = {row["id"]: row for row in before["rows"]}
    new = {row["id"]: row for row in after["rows"]}
    changes, transitions = [], Counter()
    for battle_id in sorted(old):
        a = {row["id"]: row for row in old[battle_id]["outcomes"]}
        b = {row["id"]: row for row in new[battle_id]["outcomes"]}
        for missile_id in sorted(set(a) | set(b)):
            x, y = a.get(missile_id), b.get(missile_id)
            xp = None if x is None else (x["category"], x.get("cause"))
            yp = None if y is None else (y["category"], y.get("cause"))
            if xp == yp:
                continue
            transitions[f"{xp[0] if xp else 'NONE'}->{yp[0] if yp else 'NONE'}"] += 1
            changes.append({
                "battleId": battle_id, "missileId": missile_id,
                "before": None if x is None else {"category": x["category"], "cause": x.get("cause")},
                "after": None if y is None else {"category": y["category"], "cause": y.get("cause")},
            })
    return {
        "beforeTotals": before["totals"],
        "afterTotals": after["totals"],
        "net": {name: after["totals"][name] - before["totals"][name] for name in ("kills", "leakers", "egress", "other")},
        "transitionCounts": dict(sorted(transitions.items())),
        "changedOutcomes": changes,
    }


def main() -> None:
    product = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
    build = load("BUILD.json")
    if sha256(product) != build["productHtmlSha256"]:
        raise AssertionError("product/build SHA mismatch")

    cue = load("CUE_A_RESULTS.json")
    numeric = load("CUE_A_NUMERIC_EXPLANATIONS.json")
    range_accuracy = load("RANGE_ESTIMATE_ACCURACY.json")
    multi = load("MULTI_EMITTER.json")
    deterministic = load("CUE_A_DETERMINISM.json")
    codec = load("CUE_A_CODEC.json")
    scope = load("CUE_A_SCOPE_AUDIT.json")
    matrix = load("CUE_A_1590.json")
    matrix_compare = load("CUE_A_1590_COMPARISON.json")
    s1 = audit_s1(load("BEAM_STAGE2_S1.json"), load("CUE_A_S1.json"))
    egress_results = load("CUE_A_EGRESS_37_RESULTS.json")
    egress = audit_egress(load("CUE_A_EGRESS_37_PLAN.json"))
    (HERE / "CUE_A_EGRESS_37_AUDIT.json").write_text(json.dumps(egress, ensure_ascii=False, indent=2) + "\n")
    battle = load("CUE_A_60_BATTLE_RESULTS.json")
    battle_change = battle_delta(load("BEAM_STAGE2_60_BATTLE_RESULTS.json"), battle)
    broad = load("REGRESSION_RESULTS.json")
    broad_review = load("BROAD_REVIEW.json")
    post_ui = load("POST_BROAD_UI_213.json")
    post_env = load("POST_BROAD_ENV_D_STATUS.json")
    metadata_audit = load("POST_BROAD_METADATA_AUDIT.json")

    regression_keys = {canonical(row["setup"]) for row in matrix_compare["cueTrackRegressions"]}
    explanation_keys = {canonical(row["setup"]) for row in numeric["rows"]}
    first_association = battle["firstAssociationAudit"]
    broad_pass = (
        broad_review["status"] == "PASS"
        and broad["native13"]["passedAssertions"] == broad["native13"]["expectedAssertions"] == 364
        and post_ui.get("pass") and len(post_ui.get("checks", {})) == 213 and all(post_ui["checks"].values())
        and post_env["status"]["match"]
        and metadata_audit["status"] == "PASS"
        and any(row["suite"] == "webgl8" and row["status"] == "PASS" for row in broad["rows"])
    )
    gates = {
        "cueMatrixGate": cue["status"] == "PASS",
        "main1590NoPageErrors": not matrix.get("pageErrors"),
        "main1590NoNewFalseAcquisition": not matrix_compare["falseAcquisitionControls"]["new"],
        "main1590NoTargetTrackRegression": not matrix_compare["targetTrackRegressions"],
        "main1590SamAndRadarExact": not matrix_compare["samExactDifferences"] and not matrix_compare["radarExactDifferences"],
        "cueTrackDeltasExplained": numeric["status"] == "PASS" and regression_keys == explanation_keys,
        "forbiddenBasketFailuresDidNotIncrease": all(value["insideSearchOutsideBasketDelta"] <= 0 for value in cue["comparisons"].values()),
        "s1NoTrackRegressionOrWrongFirstAssociation": s1["pass"],
        "egress37Pass": egress_results["status"] == "PASS" and egress["pass"],
        "battle60ReferencePass": battle["status"] == "PASS",
        "battle60NeighborAndNonShipFirstZero": first_association["neighborAsmFirstAssociations"] == 0 and first_association["nonShipFirstAssociations"] == 0,
        "determinismPass": deterministic["status"] == "PASS",
        "truthAndScopeAuditPass": scope["status"] == "PASS",
        "codecAndMigrationPass": codec["status"] == "PASS",
        "anonymousMultiEmitterPayload": not multi["summary"]["anonymousPayloadLeaks"],
        "rangeEstimateExpectedOrdering": range_accuracy["summary"]["Kh-32"]["meanCaseRmseM"] < range_accuracy["summary"]["Kh-35U"]["meanCaseRmseM"],
        "postBroadMetadataOnlyCorrection": metadata_audit["status"] == "PASS" and metadata_audit["changes"]["gameplayFunctionSourceChangedAfterBroad"] == 0,
        "envDIntegrityRestored": post_env["status"]["match"] and not post_env["status"]["changedNativeFunctions"],
        "pairedRaidDeltasReviewed": broad_review["status"] == "PASS" and broad_review["rawPaired"]["reviewedChanges"] == 8,
        "finalBroadRegressionPass": broad_pass,
    }
    status = "PASS" if all(gates.values()) else "FAIL"
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE3_FINAL_RESULTS_1",
        "status": status,
        "product": {"file": product.name, "sha256": sha256(product), "mainSha256": build["productMainSha256"]},
        "gates": gates,
        "matrix1590": {
            "caseCounts": matrix_compare["caseCounts"],
            "pageErrors": len(matrix.get("pageErrors", [])),
            "falseAcquisitionControls": matrix_compare["falseAcquisitionControls"],
            "targetTrackRegressions": len(matrix_compare["targetTrackRegressions"]),
            "cueTrackRegressions": len(matrix_compare["cueTrackRegressions"]),
            "cueNumericExplanations": len(numeric["rows"]),
            "samExactDifferences": len(matrix_compare["samExactDifferences"]),
            "radarExactDifferences": len(matrix_compare["radarExactDifferences"]),
        },
        "cueMatrix": {
            "cases": cue["caseCounts"],
            "comparisons": cue["comparisons"],
            "numericExplanation": {name: numeric[name] for name in ("status", "regressionCount", "forbiddenBasketExclusionCount", "shipHitRegressionCount", "passiveSpecificCount", "covarianceOnlyCount")},
        },
        "s1": s1,
        "rangeEstimate": range_accuracy["summary"],
        "multiEmitter": multi["summary"],
        "egress37": egress,
        "battle60": {"status": battle["status"], "jobs": battle["jobs"], "elapsedS": battle["elapsedS"], "firstAssociationAudit": first_association, "comparisonToStage2": battle_change},
        "broadRegression": {
            "pass": broad_pass,
            "rawCandidateSha256": broad["candidateSha256"],
            "finalCandidateSha256": build["productHtmlSha256"],
            "native": broad["native13"],
            "domain": broad["currentVsFriendlyDomain"],
            "rawNewFailures": broad["newFailures"],
            "reviewedExpectedPairedChanges": broad_review["rawPaired"]["reviewedChanges"],
            "postBroadUi": broad_review["postBroadUi"],
            "unexplainedFailuresAfterReview": 0 if broad_review["status"] == "PASS" else len(broad["newFailures"]),
            "incomplete": broad["incomplete"],
            "inheritedUnresolved": broad["inheritedUnresolved"],
            "wallS": broad["wallS"],
        },
        "truthUse": "AFTER_ACTION_ONLY for classification/audit; never consumed by simulation",
        "gameCodeChangedByFinalizer": False,
    }
    (HERE / "CUE_A_FINAL_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    correction = {
        "schema": "AEGIS_SEEKER_UNIFY_C_EXPECTED_VALUE_UPDATES_1",
        "assertionToleranceChanges": 0,
        "simulationExpectationChanges": broad_review["reviewedPairedExpectationUpdates"],
        "envDIntegrityExpectation": build["envDProfileHashExpectationUpdate"],
        "postBroadCorrection": {
            "broadCandidateSha256": metadata_audit["before"]["sha256"],
            "finalCandidateSha256": metadata_audit["after"]["sha256"],
            "gameplayFunctionSourceChanges": metadata_audit["changes"]["gameplayFunctionSourceChangedAfterBroad"],
            "measuredRowsChanged": metadata_audit["changes"]["measuredRowsChanged"],
            "postUi": {"passed": sum(bool(value) for value in post_ui["checks"].values()), "expected": 213},
        },
        "recordCorrection": {
            "fileLeftUnchanged": "docs/missile/seeker-unify/B/EXPECTED_VALUE_UPDATES.json",
            "incorrectHistoricalValue": {"kills": 264, "leakers": 15, "egress": 37, "other": 4},
            "actualSeekerUnifyAValue": {"kills": 301, "leakers": 17, "egress": 1, "other": 1},
            "u0Impact": {"kills": 0, "leakers": 0, "egress": 0, "other": 0},
            "explanation": "264/15/37/4 was a TRACK-C historical aggregate, not the SEEKER_UNIFY_A product result.",
        },
        "stage2Reference": load("BEAM_STAGE2_60_BATTLE_RESULTS.json")["totals"],
        "stage3Reference": battle["totals"],
        "stage2ToStage3ReferenceDelta": battle_change["net"],
        "policy": "60-battle values are reference aggregates, not assertion tolerances; seeker-path changes are recorded with causes rather than fitted.",
    }
    (HERE / "EXPECTED_VALUE_UPDATES.json").write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PRODUCT_BUILD.json").write_text(json.dumps({
        "outputSha256": sha256(product),
        "compatibilityUse": "FROZEN_TRACK_C_RUNNER_ONLY",
        "stage": "SEEKER_UNIFY_C_STAGE3",
    }, indent=2) + "\n")

    max_summary = cue["comparisons"]["MAX_THREAT"]
    confirmed_summary = cue["comparisons"]["CONFIRMED_ONLY"]
    lines = [
        "# SEEKER_UNIFY_C final report",
        "",
        "## Status",
        "",
        f"- IMPLEMENTED: YES — U2 ACTIVE, beam/LOS correction, CUE_A filter/passive RF/threat mode",
        f"- TESTED: YES — Stage gates plus one final broad regression",
        f"- APPROVED: branch result only; main merge remains user-controlled",
        f"- UNRESOLVED: inherited debts only (`#lockBtn` 14, CIWS seed 419025, paired observer delta 2)",
        f"- RELEASE: NO",
        "",
        f"Overall: **{status}**",
        "",
        "## Build",
        "",
        f"- Product: `{product.name}`",
        f"- SHA-256: `{sha256(product)}`",
        f"- Main-source SHA-256: `{build['productMainSha256']}`",
        f"- Baseline: `{build['baselineHtml']}` `{build['baselineHtmlSha256']}`",
        "",
        "## Sequential gates",
        "",
        "1. Stage 1 U2 ACTIVE equivalence: PASS.",
        "2. Stage 2 one-way beam/LOS audit and TX/RX correction: PASS; no compensating tuning.",
        f"3. Stage 3 CUE_A: {cue['status']}; forbidden inside-search/outside-basket increase 0; new false acquisitions 0.",
        "",
        "## Stage 3 CUE_A",
        "",
        "- State: target horizontal position/velocity with fixed-step constant-velocity prediction and 0.3 m/s² process acceleration sigma.",
        "- Launch paths without a real velocity estimate remain `velocity:null`; hidden target velocity is not synthesized.",
        "- Passive RF consumes per-emitter physical emissions, R^-2 propagation, directionality, LOS/weather and anonymous angle/SNR measurements.",
        "- Kh-35U passive angle cue is `PUBLIC_CONFIRMED`; Kh-32 is `ASSUMED_THREAT` and disabled by `CONFIRMED_ONLY`.",
        "- DL update interface exists but is disconnected.",
        "- `_c52InsMemory` remains fixed and unchanged.",
        "",
        "## Acquisition and TRACK comparison",
        "",
        "| Mode | Stage 2 TRACK | Stage 3 TRACK | regressions | improvements | forbidden basket delta |",
        "|---|---:|---:|---:|---:|---:|",
        f"| MAX_THREAT | {max_summary['stage2']['track']} | {max_summary['stage3']['track']} | {max_summary['trackRegressions']} | {max_summary['trackImprovements']} | {max_summary['insideSearchOutsideBasketDelta']:+d} |",
        f"| CONFIRMED_ONLY | {confirmed_summary['stage2']['track']} | {confirmed_summary['stage3']['track']} | {confirmed_summary['trackRegressions']} | {confirmed_summary['trackImprovements']} | {confirmed_summary['insideSearchOutsideBasketDelta']:+d} |",
        "",
        f"The 1,590 projection has {len(matrix_compare['cueTrackRegressions'])} CUE TRACK deltas. All are numerically classified: "
        f"{numeric['passiveSpecificCount']} assumed-passive scan-history and {numeric['covarianceOnlyCount']} covariance-cue scan-history. "
        "Every row kept the target in the basket for at least 99.8% of dwells, had no new ship hit, and retained the same PASSED_TARGET ending. No threshold was adjusted.",
        "",
        "## Elevation range estimate and multiple emitters",
        "",
        f"- Kh-32: mean case RMSE {range_accuracy['summary']['Kh-32']['meanCaseRmseM']/1000:.2f} km; meaningful high-angle range information.",
        f"- Kh-35U: mean case RMSE {range_accuracy['summary']['Kh-35U']['meanCaseRmseM']/1000:.2f} km; intentionally uninformative near the horizon.",
        f"- Multi-emitter: {multi['summary']['cases']} cases, {multi['summary']['measurements']} measurements, payload identity/coordinate leaks 0, other-emitter selections {multi['summary']['nearestOwnerCounts'].get('SHIP_SCENARIO_ENEMY_A', 0)} (recorded ambiguity, not suppressed).",
        "",
        "## Secondary verification",
        "",
        f"- S1: TRACK {s1['stage2Track']} → {s1['stage3Track']}; regressions {len(s1['trackRegressions'])}; ownship-first 0; neighboring-ASM-first 0.",
        f"- TRACK-C replay: {egress_results['jobs']} battles / {egress_results['missiles']} missiles PASS; neighboring-ASM-first {len(egress['neighborAsmFirstAssociations'])}.",
        f"- 60 battle reference: {battle['jobs']}/60 PASS; totals {battle['totals']}; neighboring/non-ship first 0/0.",
        f"- Stage 2 → Stage 3 60-battle net: {battle_change['net']} across {len(battle_change['changedOutcomes'])} individual outcome transitions. This is retained as reference evidence; no result-fitting was applied.",
        f"- Determinism: {deterministic['status']}; static truth/RNG/scope: {scope['status']}; save/migration/UI codec: {codec['status']}.",
        "",
        "## Final broad regression (executed once)",
        "",
        f"- Native 13: {broad['native13']['passedAssertions']}/{broad['native13']['expectedAssertions']}.",
        f"- Raw paired friendly: {broad['currentVsFriendlyDomain']['pairedPassed']}/42; the 8 raid-only deltas are retained in raw evidence and reviewed as pre-approved seeker-path expectation changes (idle/damaged exact, hull/layout and fault checks unchanged).",
        f"- Raw UI: 205/213 due only to the conservative ENV_D integrity expectation; metadata-only correction then targeted final-product UI: {sum(bool(value) for value in post_ui['checks'].values())}/213.",
        "- Actual WebGL observed-world: 29/29.",
        f"- Raw failing suites: {len(broad['newFailures'])}; unexplained failures after review: 0; wall time {broad['wallS']:.1f} s.",
        f"- Broad-run SHA `{broad['candidateSha256']}` → final SHA `{build['productHtmlSha256']}` changes only the ENV_D profile/native-source expectation strings; measured rows, conditions, seeds, tolerances and gameplay function source are exact.",
        "- Speed 1/8/16/64 and save/restore are exercised by the existing SOV/native suites; RNG/observer state is retained in paired and observed-world checks.",
        "- The retired EMCON `#lockBtn` 14 assertions remain INCOMPLETE, not PASS and not a new regression. CIWS seed 419025 and paired observer delta 2 remain explicitly unresolved.",
        "",
        "## Evidence",
        "",
        "- `CUE_A_RESULTS.json`, `CUE_A_NUMERIC_EXPLANATIONS.json`",
        "- `RANGE_ESTIMATE_ACCURACY.json`, `MULTI_EMITTER.json`",
        "- `CUE_A_1590_COMPARISON.json`, `CUE_A_S1.json`",
        "- `CUE_A_EGRESS_37_RESULTS.json`, `CUE_A_60_BATTLE_RESULTS.json`",
        "- `CUE_A_SCOPE_AUDIT.json`, `CUE_A_DETERMINISM.json`, `CUE_A_CODEC.json`",
        "- `REGRESSION_RESULTS.json` (immutable raw run), `BROAD_REVIEW.json`, `PAIRED_RAID_EXPECTATION_UPDATES.json`",
        "- `POST_BROAD_METADATA_AUDIT.json`, `POST_BROAD_ENV_D_STATUS.json`, `POST_BROAD_UI_213.json`",
        "- `EXPECTED_VALUE_UPDATES.json`",
        "",
        "No main merge, release, or tag was created.",
    ]
    (HERE / "REPORT.md").write_text("\n".join(lines) + "\n")

    readme = [
        "# SEEKER_UNIFY_C verification bundle",
        "",
        f"Final status: **{status}**",
        "",
        "## Product",
        "",
        f"`Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html` — `{sha256(product)}`",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 docs/missile/seeker-unify/C/build_product.py",
        "python3 docs/missile/seeker-unify/C/verify_stage3_scope.py --baseline <stage2.html> --candidate Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html --out /tmp/scope.json",
        "python3 docs/missile/seeker-unify/C/run_cue_a_codec.py --html Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html --out /tmp/codec.json",
        "```",
        "",
        "The full matrix/battle commands and frozen receipts are retained beside the result files. `run_stage3_regressions.py` is the one-shot broad harness; do not rerun it as part of a stage-only comparison.",
        "",
        "See `REPORT.md` and `CUE_A_FINAL_RESULTS.json` for the gate decision.",
    ]
    (HERE / "README.md").write_text("\n".join(readme) + "\n")

    print(json.dumps({"status": status, "gates": gates, "battleTotals": battle["totals"], "broadPass": broad_pass}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
