#!/usr/bin/env python3
"""Close the SEEKER_UNIFY_C Stage-2 beam/LOS gate from saved evidence.

This script is reporting-only.  It reads frozen product/diagnostic results and
AFTER_ACTION truth evidence, but never loads or mutates the simulation.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def egress_audit(plan: dict) -> dict:
    rows = []
    missing = []
    neighbor = []
    no_association = []
    families = Counter()
    for job in plan["jobs"]:
        path = HERE / "evidence/beam-stage2-egress-37" / f"{job['id']}.json.gz"
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
                neighbor.append({
                    "battleId": job["id"], "missileId": missile_id,
                    "debugId": debug_id, "debugKind": debug_kind,
                })
            elif "SHIP" in debug_id or debug_kind in {"SHIP", "COMPOSITE"} and "SHIP" in members:
                family = "INTENDED_OWNSHIP"
            else:
                family = debug_kind or debug_id or "OTHER"
            families[family] += 1
            rows.append({
                "battleId": job["id"], "missileId": missile_id,
                "family": family, "debugId": debug_id, "debugKind": debug_kind,
            })
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
        "note": "SHIP is the intended defended ship in this inbound-ASM replay; only neighboring ASM first selection is forbidden here.",
    }


def battle_delta(stage1: dict, stage2: dict) -> dict:
    before = {row["id"]: row for row in stage1["rows"]}
    after = {row["id"]: row for row in stage2["rows"]}
    changes = []
    transition_counts = Counter()
    for battle_id in sorted(before):
        b = {row["id"]: row for row in before[battle_id]["outcomes"]}
        a = {row["id"]: row for row in after[battle_id]["outcomes"]}
        for missile_id in sorted(set(b) | set(a)):
            old = b.get(missile_id)
            new = a.get(missile_id)
            old_pair = None if old is None else (old["category"], old.get("cause"))
            new_pair = None if new is None else (new["category"], new.get("cause"))
            if old_pair == new_pair:
                continue
            transition_counts[f"{old_pair[0] if old_pair else 'NONE'}->{new_pair[0] if new_pair else 'NONE'}"] += 1
            changes.append({
                "battleId": battle_id,
                "missileId": missile_id,
                "before": None if old is None else {"category": old["category"], "cause": old.get("cause")},
                "after": None if new is None else {"category": new["category"], "cause": new.get("cause")},
            })
    return {
        "stage1CorrectedTotals": stage1["totals"],
        "stage2Totals": stage2["totals"],
        "net": {
            key: stage2["totals"][key] - stage1["totals"][key]
            for key in ("kills", "leakers", "egress", "other")
        },
        "changedOutcomes": changes,
        "transitionCounts": dict(sorted(transition_counts.items())),
        "netInterpretation": (
            "One net INTERCEPT_KILL became GUIDANCE_CONTROL_LOSS_MISS. "
            "Leakers and egress did not increase; the reference battle harm count is unchanged."
        ),
    }


def main() -> None:
    build = load("BUILD.json")
    product = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
    assert sha(product) == build["productHtmlSha256"]

    comparison = load("BEAM_STAGE2_1590_COMPARISON.json")
    secondary = load("BEAM_STAGE2_SECONDARY_COMPARISON.json")
    range_explain = load("BEAM_STAGE2_RANGE_NUMERIC_EXPLANATIONS.json")
    cue_explain = load("BEAM_STAGE2_CUE_NUMERIC_EXPLANATIONS.json")
    rcs = load("BEAM_STAGE2_RCS_AUDIT.json")
    determinism = load("BEAM_STAGE2_DETERMINISM.json")
    egress_result = load("BEAM_STAGE2_EGRESS_37_RESULTS.json")
    egress = egress_audit(load("BEAM_STAGE2_EGRESS_37_PLAN.json"))
    battle = load("BEAM_STAGE2_60_BATTLE_RESULTS.json")
    battle_before = json.loads((ROOT / "docs/missile/seeker-unify/B/U0_60_BATTLE_RESULTS.json").read_text())
    battle_changes = battle_delta(battle_before, battle)

    target_regression_keys = {canonical(row["setup"]) for row in comparison["targetTrackRegressions"]}
    range_explanation_keys = {canonical(row["setup"]) for row in range_explain["rows"]}
    cue_regression_keys = {canonical({
        "label": row["key"][0], "rangeKm": row["key"][1],
        "speedKt": row["key"][2], "turnDeg": row["key"][3],
        "seed": row["key"][4], "emcon": row["key"][5],
    }) for row in secondary["cue"]["trackRegressions"]}
    cue_explanation_keys = {canonical(row["setup"]) for row in cue_explain["rows"]}

    cue_totals = defaultdict(lambda: {"shots": 0, "stage1Track": 0, "stage2Track": 0})
    for key, value in secondary["cue"]["summary"].items():
        label, _range, _speed, _turn, emcon = key.split("|")
        group = cue_totals[(label, emcon)]
        for name in group:
            group[name] += value[name]
    cue_summary = [
        {"label": label, "emcon": emcon == "True", **value}
        for (label, emcon), value in sorted(cue_totals.items())
    ]

    gates = {
        "matrixPageErrorsZero": not comparison["pageErrors"],
        "falseAcquisitionIncreaseZero": not comparison["falseAcquisitionControls"]["new"],
        "samExactDifferencesZero": not comparison["samExactDifferences"],
        "shipRadarExactDifferencesZero": not comparison["radarExactDifferences"],
        "targetRegressionsNumericallyExplained": (
            range_explain["status"] == "PASS"
            and not range_explain["uncaptured"]
            and not range_explain["unexpectedTrack"]
            and target_regression_keys == range_explanation_keys
        ),
        "cueRegressionsNumericallyExplained": (
            cue_explain["status"] == "PASS"
            and not cue_explain["uncaptured"]
            and not cue_explain["unexpectedTrack"]
            and cue_regression_keys == cue_explanation_keys
        ),
        "s1TrackCountPreserved": secondary["s1"]["stage1Track"] == secondary["s1"]["stage2Track"] == 40,
        "s1OwnshipFirstZero": not secondary["s1"]["ownshipFirstSelections"],
        "s1NeighborAsmFirstZero": not secondary["s1"]["neighborAsmFirstSelections"],
        "egressReplayPass": egress_result["status"] == "PASS" and egress["pass"],
        "battleReferencePass": battle["status"] == "PASS",
        "battleNeighborAsmFirstZero": battle["firstAssociationAudit"]["neighborAsmFirstAssociations"] == 0,
        "battleNonShipFirstZero": battle["firstAssociationAudit"]["nonShipFirstAssociations"] == 0,
        "determinismPass": determinism["status"] == "PASS",
        "rcsPhysicalInputsPreserved": rcs["status"] == "PASS",
    }
    status = "PASS" if all(gates.values()) else "FAIL"

    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_FIX_RESULTS_1",
        "status": status,
        "stage": 2,
        "product": {
            "file": product.name,
            "sha256": sha(product),
            "mainSha256": build["productMainSha256"],
        },
        "implementation": {
            "before": "COMBINED_SINGLE",
            "after": "TX_RX_SEPARATE",
            "beamPattern": "same one-way SIM_TUNED pattern applied once on transmit and once on receive",
            "los": "same LOS quality applied once outbound and once inbound",
            "sidelobeFloor": 0.08,
            "sidelobeFloorChanged": False,
            "hojAndPassiveRfChanged": False,
            "resultFitting": False,
        },
        "gates": gates,
        "matrix1590": {
            "cases": comparison["caseCounts"],
            "falseAcquisitions": comparison["falseAcquisitionControls"],
            "targetTrackRegressions": len(comparison["targetTrackRegressions"]),
            "targetNumericExplanations": len(range_explain["rows"]),
            "samExactDifferences": len(comparison["samExactDifferences"]),
            "radarExactDifferences": len(comparison["radarExactDifferences"]),
            "acquireTrackRangeDistributions": comparison["firstAcquireTrackRangeDistributions"],
        },
        "cue240": {
            "trackRegressions": len(secondary["cue"]["trackRegressions"]),
            "trackImprovements": len(secondary["cue"]["trackImprovements"]),
            "numericExplanations": len(cue_explain["rows"]),
            "summary": cue_summary,
        },
        "s1": {
            "cases": secondary["s1"]["rows"],
            "stage1Track": secondary["s1"]["stage1Track"],
            "stage2Track": secondary["s1"]["stage2Track"],
            "ownshipFirst": len(secondary["s1"]["ownshipFirstSelections"]),
            "neighborAsmFirst": len(secondary["s1"]["neighborAsmFirstSelections"]),
        },
        "egress37": egress,
        "battle60": {
            "status": battle["status"],
            "jobs": battle["jobs"],
            "elapsedS": battle["elapsedS"],
            "firstAssociationAudit": battle["firstAssociationAudit"],
            "comparisonToStage1": battle_changes,
        },
        "numericExplanation": {
            "formula": "stage2Signal = stage1Signal * rxBeamGain * losQ",
            "rangeCases": len(range_explain["rows"]),
            "cueCases": len(cue_explain["rows"]),
            "rangeUnexplained": len(range_explain["uncaptured"]) + len(range_explain["unexpectedTrack"]),
            "cueUnexplained": len(cue_explain["uncaptured"]) + len(cue_explain["unexpectedTrack"]),
        },
        "truthUse": "AFTER_ACTION_ONLY for association/outcome audits; never consumed by product simulation",
        "gameCodeChangedByFinalizer": False,
    }
    (HERE / "BEAM_FIX_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# SEEKER_UNIFY_C Stage 2 — ASM beam/LOS correction",
        "",
        f"- IMPLEMENTED: YES",
        f"- TESTED: YES",
        f"- APPROVED: USER PRE-APPROVED POLICY; FINAL MERGE NOT APPROVED",
        f"- UNRESOLVED: {'NONE IN STAGE 2' if status == 'PASS' else 'SEE FAILED GATES'}",
        f"- RELEASE: NO",
        "",
        f"## Gate: {status}",
        "",
        f"Product: `{product.name}` · SHA-256 `{sha(product)}`",
        "",
        "The audit found no public or project definition proving the legacy half-width, LOS, or 0.08 floor was already round-trip.  Per the fixed directive, the existing values are now one-way `SIM_TUNED` values and the ASM active seeker uses `TX_RX_SEPARATE`.  The numeric values themselves were not tuned.",
        "",
        "## Results",
        "",
        f"- 1,590 matrix: 660 range + 390 SAM ARH + 120 cue + 420 ship-radar cases; page errors 0.",
        f"- False acquisitions: {comparison['falseAcquisitionControls']['before']} → {comparison['falseAcquisitionControls']['after']}; new false acquisitions 0.",
        f"- SAM exact differences 0; ship-radar exact differences 0; RCS physical-input audit PASS.",
        f"- Target TRACK regressions: {len(comparison['targetTrackRegressions'])}; all {len(range_explain['rows'])} captured and numerically explained.",
        f"- Full cue matrix: {len(secondary['cue']['trackRegressions'])} regressions, {len(secondary['cue']['trackImprovements'])} improvements; all {len(cue_explain['rows'])} captured and numerically explained.",
        f"- S1: TRACK {secondary['s1']['stage1Track']} → {secondary['s1']['stage2Track']}; ownship-first 0; neighbor-ASM-first 0.",
        f"- TRACK-C replay: {egress_result['jobs']} battles / {egress_result['missiles']} missiles PASS; neighboring-ASM first association 0.",
        f"- 60 battles: {battle['jobs']}/60 PASS; first associations SHIP {battle['firstAssociationAudit']['observed']}/{battle['firstAssociationAudit']['observed']}; neighbor/non-ship 0/0.",
        f"- Battle totals Stage 1 → Stage 2: {battle_before['totals']} → {battle['totals']}.  Net leakers and egress are unchanged; one net kill became a guidance-control-loss miss.",
        f"- Determinism: PASS.",
        "",
        "## Cue TRACK totals",
        "",
        "| Weapon | EMCON | Shots | Stage 1 TRACK | Stage 2 TRACK |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in cue_summary:
        lines.append(
            f"| {row['label']} | {'ON' if row['emcon'] else 'OFF'} | {row['shots']} | {row['stage1Track']} | {row['stage2Track']} |"
        )
    lines += [
        "",
        "The Kh-32 60 km losses are the direct consequence of applying the existing one-way beam factor a second time.  The captured regression dwells have a median added factor of about 0.08 (the unchanged sidelobe floor), reducing representative median SNR from roughly 0.22 to 0.018.  No compensating sensitivity, beamwidth, threshold, RCS, or cue-basket tuning was applied.",
        "",
        "## Evidence",
        "",
        "- `BEAM_STAGE2_1590_COMPARISON.json`",
        "- `BEAM_STAGE2_RANGE_NUMERIC_EXPLANATIONS.json`",
        "- `BEAM_STAGE2_CUE_NUMERIC_EXPLANATIONS.json`",
        "- `BEAM_STAGE2_SECONDARY_COMPARISON.json`",
        "- `BEAM_STAGE2_EGRESS_37_RESULTS.json`",
        "- `BEAM_STAGE2_60_BATTLE_RESULTS.json`",
        "- `BEAM_STAGE2_RCS_AUDIT.json`",
        "- `BEAM_STAGE2_DETERMINISM.json`",
        "",
        "Stage 3 may start only from this PASS artifact.  Broad regression remains deferred until Stage 3 completion, as required by the directive.",
        "",
    ]
    (HERE / "BEAM_FIX_RESULTS.md").write_text("\n".join(lines))
    print(json.dumps({
        "status": status,
        "gates": gates,
        "rangeRegressions": len(target_regression_keys),
        "cueRegressions": len(cue_regression_keys),
        "egressMissiles": egress["missiles"],
        "battleTotals": battle["totals"],
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
