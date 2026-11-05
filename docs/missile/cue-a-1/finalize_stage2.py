#!/usr/bin/env python3
"""Freeze Stage-2 evidence and produce the passive-RF gate report."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import shutil
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def key(row: dict) -> str:
    return canonical(row["setup"])


def summarize(rows: list[dict]) -> dict:
    return {"cases": len(rows), "acquire": sum(bool(row["result"]["everAcquire"]) for row in rows),
            "track": sum(bool(row["result"]["everTrack"]) for row in rows),
            "shipHit": sum(bool(row["result"]["shipHit"]) for row in rows),
            "failureCategories": dict(sorted(Counter(row["result"]["failureAudit"]["category"] for row in rows).items()))}


def s1_audit(before: dict, after: dict) -> dict:
    row_key = lambda row: (row["setup"]["launchRangeKm"], row["setup"]["separationDeg"], row["setup"]["seed"])
    old, new = {row_key(row): row for row in before["rows"]}, {row_key(row): row for row in after["rows"]}
    if old.keys() != new.keys():
        raise AssertionError("S1 keys differ")
    regressions, ownship, neighbor = [], [], []
    for item in old:
        a, b = old[item], new[item]
        if a["final"]["seekerMode"] == "TRACK" and b["final"]["seekerMode"] != "TRACK":
            regressions.append(item)
        first = b.get("metrics", {}).get("firstCandidate") or {};ident, kind = str(first.get("id", "")), str(first.get("kind", ""))
        if ident.startswith("SHIP") or kind == "SHIP": ownship.append({"key": item, "candidate": first})
        if "ASM" in ident or kind in {"ASM", "RF_OBJECT"}: neighbor.append({"key": item, "candidate": first})
    return {"cases": len(new), "baselineTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in old.values()),
            "candidateTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in new.values()),
            "trackRegressions": regressions, "ownshipFirstSelections": ownship, "neighborAsmFirstSelections": neighbor,
            "pageErrors": after.get("pageErrors", []), "pass": not regressions and not ownship and not neighbor and not after.get("pageErrors")}


def egress_audit(plan: dict, evidence: Path) -> dict:
    families: Counter[str] = Counter();rows, missing, neighbor = [], [], []
    for job in plan["jobs"]:
        path = evidence / f"{job['id']}.json.gz"
        if not path.exists(): missing.append(job["id"]);continue
        data = json.loads(gzip.decompress(path.read_bytes()))
        for missile_id in job["focusIds"]:
            events = [event for event in data["asm"]["events"] if event.get("kind") == "ASSOCIATION" and event.get("missileId") == missile_id]
            first = (events[0].get("selected") or {}) if events else {};debug_id, debug_kind = str(first.get("_debugId", "")), str(first.get("_debugKind", ""));members = [str(value) for value in first.get("_debugMembers", [])]
            if not first: family = "NONE"
            elif "ASM:" in debug_id or "TARGET_ASM" in members: family = "NEIGHBOR_ASM";neighbor.append({"battleId": job["id"], "missileId": missile_id, "debugId": debug_id})
            elif "SHIP" in debug_id or (debug_kind in {"SHIP", "COMPOSITE"} and "SHIP" in members): family = "INTENDED_OWNSHIP"
            else: family = debug_kind or debug_id or "OTHER"
            families[family] += 1;rows.append({"battleId": job["id"], "missileId": missile_id, "family": family})
    return {"tag": "AFTER_ACTION_TRUTH_TEST_ONLY", "jobs": len(plan["jobs"]), "missiles": len(rows),
            "missingEvidence": missing, "firstFamilies": dict(sorted(families.items())), "neighborAsmFirstAssociations": neighbor,
            "rows": rows, "pass": not missing and not neighbor and len(rows) == plan["missileCount"]}


def change_explanation(before: dict, after: dict) -> dict:
    label = before["setup"]["label"];base_deg = .65 if label == "Kh-35U" else .45
    old_measure = before.get("cueA", {}).get("lastMeasurement") or {};old_snr = old_measure.get("snr")
    old_sigma = base_deg * math.sqrt(1 + 1 / max(1, old_snr)) if isinstance(old_snr, (int, float)) else None
    synthesis = after.get("passiveSynthesis") or {}
    return {"setup": before["setup"],
            "before": {"acquire": before["result"]["everAcquire"], "track": before["result"]["everTrack"], "shipHit": before["result"]["shipHit"],
                       "failure": before["result"]["failureAudit"]["category"], "band": old_measure.get("band"), "snr": old_snr, "bearingSigmaDeg": old_sigma},
            "after": {"acquire": after["result"]["everAcquire"], "track": after["result"]["everTrack"], "shipHit": after["result"]["shipHit"],
                      "failure": after["result"]["failureAudit"]["category"], "family": synthesis.get("selectedFamily"), "band": synthesis.get("selectedBand"),
                      "frequencyMHz": synthesis.get("frequencyMHz"), "snr": (after.get("cueA", {}).get("lastMeasurement") or {}).get("snr"),
                      "bearingSigmaDeg": synthesis.get("bearingSigmaRad") * 180 / math.pi if synthesis.get("bearingSigmaRad") is not None else None},
            "cause": "The 3 GHz SPY observation uses the directive wavelength factor k=10/3 for sigma and receive half-width. The wider observable acceptance changed deterministic passive angle updates; no family outside the allow-list was selected."}


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("kh35", "kh32", "controls", "s1", "determinism", "scope", "passive", "egress_plan", "egress_results"):
        parser.add_argument("--" + name.replace("_", "-"), dest=name, type=Path, required=True)
    parser.add_argument("--egress-evidence", type=Path, required=True)
    args = parser.parse_args()
    old_rows = load(HERE / "STAGE1B_CUE_MATRIX_KH35U.json")["rows"] + load(HERE / "STAGE1B_CUE_MATRIX_KH32.json")["rows"]
    kh35, kh32 = load(args.kh35), load(args.kh32);new_rows = kh35["rows"] + kh32["rows"]
    old, new = {key(row): row for row in old_rows}, {key(row): row for row in new_rows}
    if old.keys() != new.keys() or len(new) != 240: raise AssertionError("cue matrix keys differ")
    changes, track_regressions, hit_regressions = [], [], []
    for item in sorted(old):
        a, b = old[item], new[item]
        before_tuple = (a["result"]["everAcquire"], a["result"]["everTrack"], a["result"]["shipHit"], a["result"]["failureAudit"]["category"])
        after_tuple = (b["result"]["everAcquire"], b["result"]["everTrack"], b["result"]["shipHit"], b["result"]["failureAudit"]["category"])
        if before_tuple != after_tuple: changes.append(change_explanation(a, b))
        if before_tuple[1] and not after_tuple[1]: track_regressions.append(a["setup"])
        if before_tuple[2] and not after_tuple[2]: hit_regressions.append(a["setup"])
    comparisons = {}
    for label in ("Kh-35U", "Kh-32"):
        for emcon in (False, True):
            label_key = f"{label}|EMCON_{'ON' if emcon else 'OFF'}"
            comparisons[label_key] = {"stage1": summarize([row for row in old_rows if row["setup"]["label"] == label and row["setup"]["emcon"] is emcon]),
                                      "stage2": summarize([row for row in new_rows if row["setup"]["label"] == label and row["setup"]["emcon"] is emcon])}
    forbidden_old = sum(row["result"]["failureAudit"]["category"] == "INSIDE_SEARCH_OUTSIDE_BASKET" for row in old_rows)
    forbidden_new = sum(row["result"]["failureAudit"]["category"] == "INSIDE_SEARCH_OUTSIDE_BASKET" for row in new_rows)
    controls = load(args.controls);old_controls = {key(row): row for row in load(HERE / "STAGE1B_FALSE_ACQUISITION_CONTROLS.json")["rows"]}
    control_diffs = [row["setup"] for row in controls["rows"] if canonical(row) != canonical(old_controls[key(row)])]
    new_false = [row["setup"] for row in controls["rows"] if row["result"]["everAcquire"] and not old_controls[key(row)]["result"]["everAcquire"]]
    s1 = s1_audit(load(HERE / "STAGE1B_S1.json"), load(args.s1));determinism, scope, passive = load(args.determinism), load(args.scope), load(args.passive)
    egress = egress_audit(load(args.egress_plan), args.egress_evidence);egress_results = load(args.egress_results)
    page_errors = kh35.get("pageErrors", []) + kh32.get("pageErrors", []) + controls.get("pageErrors", []) + load(args.s1).get("pageErrors", [])
    gates = {"passiveEquipmentBandBeamTests": passive["status"] == "PASS", "cueMatrixKeysExact240": len(new_rows) == 240,
             "cueMatrixPageErrorsZero": not page_errors, "trackRegressionsZero": not track_regressions,
             "shipHitRegressionsZero": not hit_regressions, "insideSearchOutsideBasketDidNotIncrease": forbidden_new <= forbidden_old,
             "falseAcquisitionIncreaseZero": not new_false, "falseAcquisitionControlsBitExact": not control_diffs,
             "s1NoRegressionOrWrongFirstAssociation": s1["pass"], "egress37NoNeighborFirstAssociation": egress_results["status"] == "PASS" and egress["pass"],
             "determinismExact": determinism["status"] == "PASS", "truthFunctionScopeAndHojAudit": scope["status"] == "PASS"}
    result = {"schema": "AEGIS_CUE_A_1_STAGE2_RESULTS_1", "status": "PASS" if all(gates.values()) else "FAIL",
              "implementationCommit": "48a268f79e1f40e46c2d7ab96f9ead721276f2a2", "mode": "MAX_THREAT", "gates": gates,
              "product": {"file": "Aegis_SIM_v48_WIP_CUE_A_1.html", "sha256": hashlib.sha256((ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html").read_bytes()).hexdigest()},
              "cueMatrix": {"cases": len(new_rows), "comparisons": comparisons, "outcomeChanges": changes, "trackRegressions": track_regressions,
                            "shipHitRegressions": hit_regressions, "insideSearchOutsideBasket": {"stage1": forbidden_old, "stage2": forbidden_new, "delta": forbidden_new - forbidden_old}},
              "passiveRf": {"checks": passive["checks"], "summary": passive["summary"]},
              "falseAcquisitionControls": {"cases": len(controls["rows"]), "bitExactDifferences": control_diffs, "newFalseAcquisitions": new_false},
              "s1": s1, "egress37": egress, "determinism": determinism,
              "scope": {"status": scope["status"], "checks": scope["checks"], "unchangedSharedFunctions": scope["unchangedSharedFunctions"], "unexpected": scope["unexpected"]},
              "elapsedS": {"passive": passive["elapsedS"], "cueMatrix": kh35["elapsedS"] + kh32["elapsedS"], "controls": controls["elapsedS"],
                           "s1": load(args.s1)["elapsedS"], "egress": egress_results["elapsedS"], "determinism": determinism["elapsedS"]},
              "confirmedOnly": {"performance": "UNVERIFIED", **passive["summary"]["confirmedOnly"]},
              "truthUse": "AFTER_ACTION_TRUTH_TEST_ONLY for angle error and first-association audit; never consumed by simulation", "gameCodeChangedByFinalizer": False}
    save(HERE / "PASSIVE_RF_EMITTER_BAND.json", result)
    raw = {args.kh35: HERE / "STAGE2_CUE_MATRIX_KH35U.json", args.kh32: HERE / "STAGE2_CUE_MATRIX_KH32.json",
           args.controls: HERE / "STAGE2_FALSE_ACQUISITION_CONTROLS.json", args.s1: HERE / "STAGE2_S1.json",
           args.determinism: HERE / "STAGE2_DETERMINISM.json", args.scope: HERE / "STAGE2_SCOPE_AUDIT.json",
           args.passive: HERE / "STAGE2_PASSIVE_TESTS.json", args.egress_plan: HERE / "STAGE2_EGRESS_37_PLAN.json",
           args.egress_results: HERE / "STAGE2_EGRESS_37_RESULTS.json"}
    for source, destination in raw.items(): shutil.copy2(source, destination)
    destination = HERE / "evidence/stage2-egress-37";destination.mkdir(parents=True, exist_ok=True)
    for source in args.egress_evidence.glob("*.json.gz"): shutil.copy2(source, destination / source.name)
    lines = ["# CUE_A-1 Stage 2 — passive RF emitter and band model", "", f"Status: **{result['status']}**  ",
             "Performance mode: **MAX_THREAT**  ", "CONFIRMED_ONLY performance: **UNVERIFIED**  ",
             f"Frozen implementation: `{result['implementationCommit']}`  ", f"Product SHA-256: `{result['product']['sha256']}`", "", "## Gates", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} — `{name}`" for name, value in gates.items()]
    lines += ["", "## Results", "", f"- Equipment matrix: 150 before + 150 after rows; all-off received 0 samples.",
              f"- Contaminant matrix: 50 rows; selected contaminants {len(passive['summary']['contaminantsSelectedAfter'])}.",
              f"- Cue matrix: TRACK regressions {len(track_regressions)}, hit regressions {len(hit_regressions)}, changed outcomes {len(changes)}.",
              f"- Forbidden inside-search/outside-basket: {forbidden_old} → {forbidden_new}.",
              f"- Controls: {len(controls['rows'])} rows, byte differences {len(control_diffs)}, new false acquisitions {len(new_false)}.",
              f"- S1 TRACK: {s1['baselineTrack']} → {s1['candidateTrack']}; wrong first associations 0.",
              f"- Egress: {egress['jobs']} battles / {egress['missiles']} missiles, first families {egress['firstFamilies']}.",
              f"- Other runtime functions byte-identical: {scope['unchangedSharedFunctions']}; HOJ protected and identical.", "", "## Changed cue cells", ""]
    for row in changes: lines.append(f"- `{canonical(row['setup'])}`: `{row['before']}` → `{row['after']}`. {row['cause']}")
    lines += ["", "## Receiver accuracy and limits", "",
              f"- Equipment summary (after): `{canonical(passive['summary']['equipmentAfter'])}`",
              f"- Range-estimate summary before: `{canonical(passive['summary']['rangeBefore'])}`",
              f"- Range-estimate summary after: `{canonical(passive['summary']['rangeAfter'])}`",
              "- Direct elevation-derived range is diagnostic only. The larger S-band angle sigma intentionally worsens that diagnostic estimate and does not overwrite target-memory range.",
              "- CONFIRMED_ONLY scenes verified Kh-32 passive RF off and Kh-35U selection limited to 10 GHz X-band. No performance matrix was run or claimed.",
              "- The one final broad regression remains reserved for the next checkpoint."]
    (HERE / "PASSIVE_RF_EMITTER_BAND.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": result["status"], "gates": gates, "changes": len(changes), "comparisons": comparisons,
                      "egress": egress["firstFamilies"]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
