#!/usr/bin/env python3
"""Run SEEKER_CLOSE_A's bounded current-product diagnostic matrix.

The HTML passed here is a diagnostic-only derivative whose protected game
function bodies are byte-identical to HP_A.  The matrix is fixed in this file;
there is no seed search and each behavioral branch stays below 30 cases.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


SHIPS = ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")
# Diagnostic-only runaway guard.  This is not a seeker/gameplay threshold and
# is never passed into the product.  It only makes an unbounded state loop a
# visible failed result instead of silently truncating the evidence.
TRANSITION_AUDIT_CAP = 64


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


DDG_CASES = [
    {"condition": "NO_DEFENSE", "seed": 0x5EC101},
    {"condition": "HARD_KILL_ONLY", "seed": 0x5EC102, "hardKill": True},
    {"condition": "CHAFF_ONLY", "seed": 0x5EC103, "chaff": True},
    {"condition": "NULKA_ONLY", "seed": 0x5EC104, "nulka": True},
    {"condition": "CHAFF_NULKA", "seed": 0x5EC105, "chaff": True, "nulka": True},
    {"condition": "RADAR_MASTER_SILENT_ECM_ON", "seed": 0x5EC106, "ecm": True, "legacyRadarMaster": True},
    {"condition": "CLOCK_1X", "seed": 0x5EC107, "timeScale": 1},
    {"condition": "CLOCK_8X", "seed": 0x5EC107, "timeScale": 8},
    {"condition": "CLOCK_16X", "seed": 0x5EC107, "timeScale": 16},
    {"condition": "DETERMINISM_A", "seed": 0x5EC108, "chaff": True, "nulka": True, "maxTimeS": 180},
    {"condition": "DETERMINISM_B", "seed": 0x5EC108, "chaff": True, "nulka": True, "maxTimeS": 180},
    {"condition": "ALL_RADIATION_SILENT", "seed": 0x5EC109, "ecm": True, "allRadiationSilent": True},
]

CG_CASES = [
    {"condition": "NO_DEFENSE", "seed": 0x5EC201},
    {"condition": "HARD_KILL_ONLY", "seed": 0x5EC202, "hardKill": True},
    {"condition": "CHAFF_ONLY", "seed": 0x5EC203, "chaff": True},
    {"condition": "NULKA_ONLY", "seed": 0x5EC204, "nulka": True},
    {"condition": "CHAFF_NULKA", "seed": 0x5EC205, "chaff": True, "nulka": True},
    {"condition": "RADAR_MASTER_SILENT_ECM_ON", "seed": 0x5EC206, "ecm": True, "legacyRadarMaster": True},
    {"condition": "ALL_RADIATION_SILENT", "seed": 0x5EC207, "ecm": True, "allRadiationSilent": True},
]


def normalized_shot(row: dict, *, clock: bool = False, deterministic: bool = False) -> dict:
    ignore = {"condition", "frames", "timeScale"} if clock else {"condition"}
    result = {key: value for key, value in row.items() if key not in ignore}
    if deterministic:
        result.pop("condition", None)
    return result


def semantic_result(value: dict) -> dict:
    """Drop only wall-clock fields; all simulated state remains exact."""
    result = copy.deepcopy(value)
    result.get("runtime", {}).pop("elapsedS", None)
    return result


def decoy_evidence_consistent(shot: dict) -> bool:
    for kind in ("CHAFF", "NULKA"):
        evidence = shot["decoyEvidence"][kind]
        if evidence["stage"] != shot["decoyStages"][kind]:
            return False
        if evidence["stage"] == "SELECTED_THEN_RECOVERED_TARGET":
            if not evidence["selected"] or not evidence["recoveredShipAfterLastSelection"]:
                return False
            if evidence["firstShipAfterLastSelectionStep"] <= evidence["lastSelectedStep"]:
                return False
            recovered = evidence["associationEvidence"]["firstShipAfterLastSelection"]
            if not recovered or not any("SHIP" in item for item in recovered["selectedKinds"]):
                return False
        if evidence["stage"] == "SELECTED_TARGET_HIT_RECOVERY_UNPROVEN":
            if not evidence["terminalTargetHit"] or evidence["recoveredShipAfterLastSelection"]:
                return False
        if evidence["stage"] == "SEDUCED":
            association = evidence["associationEvidence"]
            if not association["selectionMaintainedAsDecoyOnly"] or not evidence["causalEvidence"]:
                return False
            last = association["lastValidSelection"]
            if not last or any("SHIP" in item for item in last["selectedKinds"]):
                return False
    return True


def defense_evidence_consistent(shot: dict) -> bool:
    evidence = shot["defenseEvidence"]
    hard, ciws = evidence["hardKill"], evidence["ciws"]
    if hard["enabled"] != shot["hardKill"] or ciws["enabled"] != shot["hardKill"]:
        return False
    for row in (hard, ciws):
        if row["engaged"] is True and row["shotsOrEvents"] <= 0:
            return False
        if row["kill"] and (row["engaged"] is not True or row["hit"] is not True):
            return False
        if row["engaged"] is None and not row["unverifiedReason"]:
            return False
    if shot["terminalCategory"] == "DEFENSE_INTERCEPT" and not hard["kill"]:
        return False
    if shot["terminalCategory"] == "CIWS_KILL" and not ciws["kill"]:
        return False
    soft = evidence["softKill"]
    return (
        soft["chaff"]["requested"] == shot["chaff"]
        and soft["nulka"]["requested"] == shot["nulka"]
        and soft["ecm"]["requested"] == shot["ecm"]
    )


def run_ship(pw, product: Path, ship: str, cases: list[dict]) -> dict:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, product.read_bytes(), ship=ship, seed=0x5EC10A, errors=errors)
    page.set_default_timeout(180_000)
    contract = page.evaluate("()=>window.__SEEKER_CLOSE_A_DIAG__.contractAudit()")
    core = page.evaluate("()=>Array.from(window.__CORE_SELFTEST_FAILURES__||[])")
    shots = []
    for case in cases:
        options = {"rangeKm": 18, "speedMps": 300, "maxTimeS": 100, "altM": 15, **case}
        shots.append(page.evaluate("options=>window.__SEEKER_CLOSE_A_DIAG__.runCase(options)", options))
    # Kh-32 runs first: the bounded Harpoon physical fixture intentionally
    # creates a surface target and is not an authority for fixture cleanup.
    # Reversing this order would let that diagnostic target contaminate the
    # Kh-32 association result.
    kh32 = page.evaluate(
        "seed=>window.__NAVAL_SIM_DIAG__.runWip108AsmAcquireCase({label:'Kh-32',speedKt:0,seed,headingDeg:90,rangeKm:60,maxTimeS:220,emconActive:true})",
        0x5EC320 if ship.startswith("DDG") else 0x5EC321,
    )
    harpoon = page.evaluate(
        "seed=>window.__SEEKER_CLOSE_A_DIAG__.runHarpoonSupport(seed)",
        0x5EC300 if ship.startswith("DDG") else 0x5EC301,
    )
    common = page.evaluate("()=>({snapshot:__SEEKER_U4_C__.snapshot(),contract:__SEEKER_U4_C__.contractAudit()})")
    browser.close()
    return {"ship": ship, "contract": contract, "coreFailures": core, "shots": shots, "harpoon": harpoon, "kh32": kh32, "common": common, "errors": errors}


def write_csv(path: Path, shots: list[dict]) -> None:
    columns = [
        "ship", "condition", "weapon", "profile", "seed", "launchTimeS", "terminalTimeS",
        "terminalCategory", "nativeCause", "terminalQualified", "firstValidObservationS",
        "lastValidObservationS", "searchAcquireReturns", "guidanceAvailable", "decoyStages", "decoyEvidence",
        "defenseEvidence", "hardKillIntervention", "ciwsIntervention", "softKillIntervention", "emconMode", "emconEvidence", "closestApproachM",
        "seaImpact", "targetHit", "combatRngStart", "combatRngEnd", "ticks", "timeScale",
    ]
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for shot in shots:
            row = {key: shot.get(key) for key in columns}
            for key in ("decoyStages", "decoyEvidence", "defenseEvidence", "emconEvidence"):
                row[key] = json.dumps(row[key], sort_keys=True, separators=(",", ":"))
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("diagnostic", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path, default=HERE / "DIAGNOSTIC_BUILD.json")
    parser.add_argument("--compare-results", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(args.receipt.read_text())
    body = args.diagnostic.read_bytes()
    if len(body) != receipt["outputBytes"] or sha256(body) != receipt["outputSha256"]:
        raise AssertionError("diagnostic build mismatch")
    if len(DDG_CASES) > 30 or len(CG_CASES) > 30:
        raise AssertionError("per-branch case cap exceeded")
    os.environ.setdefault("TMPDIR", "/dev/shm")
    with sync_playwright() as pw:
        results = [run_ship(pw, args.diagnostic, SHIPS[0], DDG_CASES), run_ship(pw, args.diagnostic, SHIPS[1], CG_CASES)]
    shots = [shot for result in results for shot in result["shots"]]
    kh32_rows = [result["kh32"] for result in results]
    transition_counts = [len(shot["stateTransitions"]) for shot in shots] + [len(row["transitions"]) for row in kh32_rows]
    acquire_search_returns = [shot["searchAcquireReturns"] for shot in shots] + [
        sum(1 for event in row["transitions"] if event.get("from") == "ACQUIRE" and event.get("to") == "SEARCH")
        for row in kh32_rows
    ]
    by_condition = {(shot["ship"], shot["condition"]): shot for shot in shots}
    clock = [by_condition[(SHIPS[0], f"CLOCK_{scale}X")] for scale in (1, 8, 16)]
    deterministic = [by_condition[(SHIPS[0], name)] for name in ("DETERMINISM_A", "DETERMINISM_B")]
    required_deployments = [
        shot for shot in shots
        if shot["chaff"] or shot["nulka"]
    ]
    global_silence = [shot for shot in shots if shot["condition"] == "ALL_RADIATION_SILENT"]
    radar_master_silent = [shot for shot in shots if shot["condition"] == "RADAR_MASTER_SILENT_ECM_ON"]
    global_zero = lambda shot: (
        shot["emconEvidence"]["mode"] == "ALL_RADIATION_SILENT"
        and shot["emconEvidence"]["allRadiationSilent"]
        and shot["emconEvidence"]["effective"]["allocatorResourceMax"] == 0
        and shot["emconEvidence"]["effective"]["radarEmitterCountMax"] == 0
        and shot["emconEvidence"]["effective"]["ecmEmitterCountMax"] == 0
        and shot["emconEvidence"]["effective"]["jammerCouplingRawWMax"] == 0
        and shot["emconEvidence"]["effective"]["hojDirectJOverNMax"] == 0
        and not shot["emconEvidence"]["effective"]["jammerSampleSeen"]
        and not shot["emconEvidence"]["effective"]["hojActiveSeen"]
        and not any(row["emissionActive"] for row in shot["emconEvidence"]["equipment"])
    )
    checks = {
        "pageAndConsoleErrorsZero": all(not result["errors"] for result in results),
        "coreSelfTestsZero": all(not result["coreFailures"] for result in results),
        "diagnosticContractPass": all(result["contract"]["pass"] for result in results),
        "commonAnonymousContractPass": all(result["common"]["contract"]["pass"] for result in results),
        "commonLayerNoRngSaveMutation": all(
            not result["common"]["snapshot"]["rngConsumedByCommonLayer"]
            and not result["common"]["snapshot"]["saveSchemaChanged"]
            for result in results
        ),
        "allShotsFaultFree": all(not shot["diagnosticFaults"] for shot in shots),
        "correctedMatrixHasNineteenShots": len(shots) == 19,
        "allShotsTerminalOrQualifiedEgress": all(shot["terminalQualified"] for shot in shots),
        "stateTransitionAuditCapRespected": all(count <= TRANSITION_AUDIT_CAP for count in transition_counts),
        "allRequestedChaffDeployed": all(
            not shot["chaff"] or shot["decoyDeployments"]["CHAFF"]["ok"] for shot in required_deployments
        ),
        "allRequestedNulkaDeployed": all(
            not shot["nulka"] or shot["decoyDeployments"]["NULKA"]["ok"] for shot in required_deployments
        ),
        "oneEightSixteenPhysicalExact": normalized_shot(clock[0], clock=True) == normalized_shot(clock[1], clock=True) == normalized_shot(clock[2], clock=True),
        "sameSeedRepeatExact": normalized_shot(deterministic[0], deterministic=True) == normalized_shot(deterministic[1], deterministic=True),
        "decoyEvidenceInternallyConsistent": all(decoy_evidence_consistent(shot) for shot in shots),
        "recoveryRequiresLaterShipAssociation": all(
            evidence["stage"] != "SELECTED_THEN_RECOVERED_TARGET"
            or evidence["firstShipAfterLastSelectionStep"] > evidence["lastSelectedStep"]
            for shot in shots for evidence in shot["decoyEvidence"].values()
        ),
        "targetHitNeverSubstitutesForRecovery": all(
            not (evidence["terminalTargetHit"] and not evidence["recoveredShipAfterLastSelection"] and evidence["stage"] == "SELECTED_THEN_RECOVERED_TARGET")
            for shot in shots for evidence in shot["decoyEvidence"].values()
        ),
        "defenseEvidenceInternallyConsistent": all(defense_evidence_consistent(shot) for shot in shots),
        "trueGlobalSilenceCasesPresent": len(global_silence) == 2 and {shot["ship"] for shot in global_silence} == set(SHIPS),
        "trueGlobalSilenceAuthorityCommandsSucceeded": all(
            shot["emconEvidence"]["authorityPath"].startswith("ownEcmCommandE/UI_AUTHORITY")
            and all(action["result"].get("ok") for action in shot["emconEvidence"]["actions"])
            for shot in global_silence
        ),
        "trueGlobalSilencePreservesRequestButZerosOutput": all(shot["emconEvidence"]["ecmRequestPreserved"] and global_zero(shot) for shot in global_silence),
        "legacyRadarMasterScenesPresentAndDistinct": len(radar_master_silent) == 2 and all(
            shot["emconEvidence"]["mode"] == "RADAR_MASTER_SILENT_ECM_ON"
            and shot["emconEvidence"]["legacyRadarMaster"]
            and not shot["emconEvidence"]["allRadiationSilent"]
            and shot["emconEvidence"]["ecmRequestPreserved"]
            for shot in radar_master_silent
        ),
        "harpoonSupportPass": all(
            result["harpoon"]["core"]["pass"] and result["harpoon"]["seeker"]["pass"] and result["harpoon"]["selection"]["pass"]
            for result in results
        ),
        "kh32BoundaryProbeCompleted": all(
            not result["kh32"].get("error")
            and result["kh32"]["durationS"] > 0
            and isinstance(result["kh32"].get("transitions"), list)
            for result in results
        ),
        "kh32FixtureIsolation": all(
            result["kh32"].get("arhValidation", {}).get("lastAssociationKindDiagnostic") != "SURFACE_TARGET"
            for result in results
        ),
        "truthFeedbackZero": all(not result["contract"]["classifierTruthFeedback"] for result in results),
        "caseCapsRespected": len(DDG_CASES) <= 30 and len(CG_CASES) <= 30,
    }
    counts = Counter(shot["terminalCategory"] for shot in shots)
    decoy_counts = {
        kind: dict(Counter(shot["decoyStages"][kind] for shot in shots))
        for kind in ("CHAFF", "NULKA")
    }
    payload = {
        "schema": "AEGIS_SEEKER_CLOSE_A_LIMITED_DIAGNOSTIC_2",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "authorityProduct": "Aegis_SIM_v48_WIP_HP_A.html",
        "authorityProductSha256": receipt["authorityProductSha256"],
        "diagnosticBuild": args.diagnostic.name,
        "diagnosticBuildSha256": receipt["outputSha256"],
        "fixedMatrix": {"DDG": DDG_CASES, "CG": CG_CASES, "seedSearch": False, "perBranchCap": 30},
        "checks": checks,
        "terminalCounts": dict(counts),
        "stateTransitionAudit": {
            "diagnosticOnlyCap": TRANSITION_AUDIT_CAP,
            "terminalShotMaxObserved": max(len(shot["stateTransitions"]) for shot in shots),
            "kh32BoundaryMaxObserved": max(len(row["transitions"]) for row in kh32_rows),
            "maxObserved": max(transition_counts),
            "maxAcquireToSearchReturnsObserved": max(acquire_search_returns),
        },
        "unclassifiedCount": counts.get("UNCLASSIFIED", 0),
        "decoyStageCounts": decoy_counts,
        "decoyEvidenceSummary": {
            "provenRecoveries": sum(evidence["stage"] == "SELECTED_THEN_RECOVERED_TARGET" for shot in shots for evidence in shot["decoyEvidence"].values()),
            "firstShipRecoveryEvents": sum(evidence["recoveredShipAfterSelection"] for shot in shots for evidence in shot["decoyEvidence"].values()),
            "provenSeduction": sum(evidence["stage"] == "SEDUCED" for shot in shots for evidence in shot["decoyEvidence"].values()),
            "unresolvedSelectedOutcomes": sum(evidence["stage"] in {"SELECTED_OUTCOME_UNRESOLVED", "SELECTED_TARGET_HIT_RECOVERY_UNPROVEN"} for shot in shots for evidence in shot["decoyEvidence"].values()),
        },
        "shots": shots,
        "supportingPaths": [{"ship": result["ship"], "harpoon": result["harpoon"], "kh32": result["kh32"]} for result in results],
        "kh32BoundaryProbePolicy": "TWO_FIXED_SEEDS_SUPPORTING_ONLY_NOT_A_RATE_OR_PASS_TARGET",
        "runtime": {"ships": results, "elapsedS": time.perf_counter() - started},
        "broadRegressionRun": False,
        "productCodeChanged": False,
        "release": False,
    }
    (args.output / "RESULTS.json").write_text(strict(payload))
    write_csv(args.output / "SHOTS.csv", shots)
    summary = {
        "schema": "AEGIS_SEEKER_CLOSE_A_LIMITED_SUMMARY_2",
        "status": payload["status"],
        "checks": checks,
        "terminalCounts": payload["terminalCounts"],
        "stateTransitionAudit": payload["stateTransitionAudit"],
        "unclassifiedCount": payload["unclassifiedCount"],
        "decoyStageCounts": decoy_counts,
        "decoyEvidenceSummary": payload["decoyEvidenceSummary"],
        "shotCount": len(shots),
        "elapsedS": payload["runtime"]["elapsedS"],
        "diagnosticOnly": True,
        "formalProductUnchanged": True,
    }
    (args.output / "SUMMARY.json").write_text(strict(summary))
    if args.compare_results:
        expected = json.loads(args.compare_results.read_text())
        if semantic_result(payload) != semantic_result(expected):
            actual_hash = sha256(strict(semantic_result(payload)).encode())
            expected_hash = sha256(strict(semantic_result(expected)).encode())
            raise AssertionError(f"committed evidence semantic mismatch: actual={actual_hash} expected={expected_hash}")
    print(strict(summary))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
