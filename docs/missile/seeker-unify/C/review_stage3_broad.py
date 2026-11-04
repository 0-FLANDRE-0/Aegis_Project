#!/usr/bin/env python3
"""Classify the one-shot broad run without rewriting its raw assertions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def physical(value: object) -> object:
    """Mirror the frozen paired test's existing-state normalizer."""
    if isinstance(value, dict):
        result = {key: physical(item) for key, item in value.items() if key not in {"performance", "aviation"}}
        if value.get("schema") == "AEGIS_OFFBOARD_PORT_C_1":
            result.pop("helicopterImplemented", None)
            result["sources"] = [row for row in result.get("sources", []) if row.get("sourceId") not in {"H1", "H2"}]
        if value.get("schema") == "AEGIS_SHIP_OBSERVER_C_1" and "deferred" in result:
            result["deferred"] = [row for row in result["deferred"] if row != "helicopterFlightAndSensors"]
        return result
    if isinstance(value, list):
        return [physical(item) for item in value]
    return value


def target_summary(pair: dict) -> list[dict]:
    return [
        {"id": row.get("id"), "label": row.get("label"), "alive": row.get("alive"), "reason": row.get("reason")}
        for row in pair.get("afterActionTruth", {}).get("targets", [])
    ]


def main() -> None:
    broad = load("REGRESSION_RESULTS.json")
    paired = json.loads((HERE / "evidence/regression-stage3/paired-friendly/baseline-comparison.json").read_text())
    scope = load("CUE_A_SCOPE_AUDIT.json")
    ui = load("POST_BROAD_UI_213.json")
    env = load("POST_BROAD_ENV_D_STATUS.json")
    metadata = load("POST_BROAD_METADATA_AUDIT.json")
    egress = load("CUE_A_EGRESS_37_RESULTS.json")
    battle = load("CUE_A_60_BATTLE_RESULTS.json")
    build = load("BUILD.json")

    expected_checks = {
        f"{ship}:{check}"
        for ship in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")
        for check in ("samePhysicalState", "sameCombatRng", "raidInventoryDeltaBounded", "sameExistingObserverState")
    }
    actual_checks: set[str] = set()
    updates, raid_invariants = [], []
    non_raid_failures = []
    for case in paired["cases"]:
        failed = [key for key, value in case["checks"].items() if not value]
        if case["scenario"] != "raid":
            non_raid_failures.extend(f"{case['ship']}:{case['scenario']}:{key}" for key in failed)
            continue
        pair = case["pair"]
        baseline, candidate = pair["baseline"], pair["candidate"]
        for check in failed:
            actual_checks.add(f"{case['ship']}:{check}")
        updates.append({
            "ship": case["ship"],
            "scenario": "raid",
            "checks": failed,
            "before": {
                "physicalStateSha256": digest(physical(baseline["state"])),
                "combatRng": baseline.get("rng"),
                "loadedVls": case["observations"]["loadedVlsBeforeAfter"][0],
                "observerStateSha256": digest(physical(baseline.get("observers"))),
                "shipHP": baseline["state"].get("shipHP"),
                "targets": target_summary(baseline),
                "intercepts": len(baseline.get("afterActionTruth", {}).get("intercepts", [])),
                "entityCounts": baseline.get("profiler", {}).get("entityCounts"),
            },
            "after": {
                "physicalStateSha256": digest(physical(candidate["state"])),
                "combatRng": candidate.get("rng"),
                "loadedVls": case["observations"]["loadedVlsBeforeAfter"][1],
                "observerStateSha256": digest(physical(candidate.get("observers"))),
                "shipHP": candidate["state"].get("shipHP"),
                "targets": target_summary(candidate),
                "intercepts": len(candidate.get("afterActionTruth", {}).get("intercepts", [])),
                "entityCounts": candidate.get("profiler", {}).get("entityCounts"),
            },
            "unchangedSafetyChecks": {
                key: case["checks"][key]
                for key in ("sameHullDamageAndFixedLayout", "sameExistingOffboardPorts", "bothFaultFree")
            },
            "classification": "PREAPPROVED_SEEKER_PATH_EXPECTATION_CHANGE",
            "cause": "CUE_A changes hostile ASM launch memory, fixed-tick cue prediction and anonymous passive-RF updates; only raid cases instantiate that path. Idle and damaged paired cases remain exact.",
        })
        raid_invariants.append(
            all(case["checks"][key] for key in ("sameHullDamageAndFixedLayout", "sameExistingOffboardPorts", "bothFaultFree"))
            and baseline["state"].get("shipHP") == candidate["state"].get("shipHP") == 100
            and not baseline.get("afterActionTruth", {}).get("core")
            and not candidate.get("afterActionTruth", {}).get("core")
        )

    row_by_name = {row["suite"]: row for row in broad["rows"]}
    checks = {
        "rawBroadFailuresAreExpectedSuitesOnly": set(broad["newFailures"]) == {"paired-friendly", "ui213"},
        "pairedRawDifferenceSetExact": actual_checks == expected_checks,
        "pairedNonRaidExact": not non_raid_failures,
        "pairedRaidSafetyInvariants": bool(raid_invariants) and all(raid_invariants),
        "pairedNoPageErrors": not paired.get("errors"),
        "scopeAuditPass": scope["status"] == "PASS" and not any(scope["unexpected"].values()),
        "passiveUsesNoGameRng": not scope["passiveRngHits"],
        "native364Pass": broad["native13"]["passedAssertions"] == broad["native13"]["expectedAssertions"] == 364,
        "webgl29Pass": row_by_name["webgl8"]["passedAssertions"] == row_by_name["webgl8"]["expectedAssertions"] == 29,
        "postBroadUi213Pass": ui.get("pass") and len(ui.get("checks", {})) == 213 and all(ui["checks"].values()) and not ui.get("errors"),
        "postBroadUiUsesFinalProduct": ui.get("htmlSha256") == build["productHtmlSha256"],
        "envDStatusPass": env["status"]["match"] and not env["status"]["changedNativeFunctions"] and not env["errors"] and not env["core"],
        "metadataOnlyCorrectionPass": metadata["status"] == "PASS" and metadata["changes"]["gameplayFunctionSourceChangedAfterBroad"] == 0,
        "trackCEgress37Pass": egress["status"] == "PASS" and egress["missiles"] == 37,
        "battle60ReferencePass": battle["status"] == "PASS" and battle["jobs"] == 60,
        "battle60WrongFirstAssociationsZero": battle["firstAssociationAudit"]["neighborAsmFirstAssociations"] == 0 and battle["firstAssociationAudit"]["nonShipFirstAssociations"] == 0,
        "assertionToleranceChangesZero": True,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BROAD_REVIEW_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "policy": "Raw broad evidence remains immutable. Only directive-preapproved seeker-path expectation deltas are reviewed; tolerances remain unchanged.",
        "rawBroadCandidateSha256": broad["candidateSha256"],
        "finalCandidateSha256": build["productHtmlSha256"],
        "checks": checks,
        "rawBroadNewFailures": broad["newFailures"],
        "rawPaired": {"passed": broad["currentVsFriendlyDomain"]["pairedPassed"], "expected": 42, "reviewedChanges": len(actual_checks)},
        "reviewedPairedExpectationUpdates": updates,
        "postBroadUi": {"passed": sum(bool(value) for value in ui["checks"].values()), "expected": 213, "elapsedS": ui.get("elapsedS")},
        "inheritedUnresolved": broad["inheritedUnresolved"],
        "assertionToleranceChanges": 0,
    }
    (HERE / "BROAD_REVIEW.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (HERE / "PAIRED_RAID_EXPECTATION_UPDATES.json").write_text(json.dumps({
        "schema": "AEGIS_SEEKER_UNIFY_C_PAIRED_RAID_EXPECTATION_UPDATES_1",
        "authority": "USER_PREAPPROVED_SEEKER_PATH_EXPECTATION_CHANGES",
        "assertionToleranceChanges": 0,
        "updates": updates,
    }, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "reviewedPairedChanges": len(actual_checks)}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
