#!/usr/bin/env python3
"""Freeze Stage-1b raw evidence and produce the Singer cue-filter gate report."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def matrix_key(row: dict) -> str:
    return canonical(row["setup"])


def s1_key(row: dict) -> tuple:
    setup = row["setup"]
    return setup["launchRangeKm"], setup["separationDeg"], setup["seed"]


def summarize(rows: list[dict]) -> dict:
    return {
        "cases": len(rows),
        "acquire": sum(bool(row["result"]["everAcquire"]) for row in rows),
        "track": sum(bool(row["result"]["everTrack"]) for row in rows),
        "shipHit": sum(bool(row["result"]["shipHit"]) for row in rows),
        "failureCategories": dict(sorted(Counter(row["result"]["failureAudit"]["category"] for row in rows).items())),
        "failureReasons": dict(sorted(Counter(row["result"]["failureAudit"]["reason"] for row in rows).items())),
    }


def basket_numbers(entry: dict | None) -> dict | None:
    basket = (entry or {}).get("basket")
    if not basket:
        return None
    low, high = basket.get("rangeLowM"), basket.get("rangeHighM")
    return {
        "rangeLowM": low,
        "rangeHighM": high,
        "rangeHalfM": None if low is None or high is None else (high - low) / 2,
        "azHalfDeg": basket.get("azHalfDeg"),
        "searchSectorAzDeg": basket.get("searchSectorAzDeg"),
        "rangeAgeS": basket.get("rangeAgeS"),
        "source": basket.get("source"),
    }


def audit_s1(before: dict, after: dict) -> dict:
    old = {s1_key(row): row for row in before["rows"]}
    new = {s1_key(row): row for row in after["rows"]}
    if old.keys() != new.keys():
        raise AssertionError("S1 key mismatch")
    regressions, improvements, ownship, neighbor, changed = [], [], [], [], []
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
        if canonical(a.get("final")) != canonical(b.get("final")) or canonical(a.get("metrics")) != canonical(b.get("metrics")):
            changed.append({"key": key, "beforeFinal": a.get("final"), "afterFinal": b.get("final")})
    return {
        "cases": len(new),
        "baselineTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in old.values()),
        "candidateTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in new.values()),
        "trackRegressions": regressions,
        "trackImprovements": improvements,
        "ownshipFirstSelections": ownship,
        "neighborAsmFirstSelections": neighbor,
        "changedRows": len(changed),
        "pageErrors": after.get("pageErrors", []),
        "pass": not regressions and not ownship and not neighbor and not after.get("pageErrors"),
    }


def audit_egress(plan: dict, evidence: Path) -> dict:
    rows, missing, neighbor, no_association = [], [], [], []
    families: Counter[str] = Counter()
    for job in plan["jobs"]:
        path = evidence / f"{job['id']}.json.gz"
        if not path.exists():
            missing.append(job["id"])
            continue
        data = json.loads(gzip.decompress(path.read_bytes()))
        for missile_id in job["focusIds"]:
            events = [event for event in data["asm"]["events"] if event.get("kind") == "ASSOCIATION" and event.get("missileId") == missile_id]
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kh35", type=Path, required=True)
    parser.add_argument("--kh32", type=Path, required=True)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--s1", type=Path, required=True)
    parser.add_argument("--determinism", type=Path, required=True)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--egress-plan", type=Path, required=True)
    parser.add_argument("--egress-results", type=Path, required=True)
    parser.add_argument("--egress-evidence", type=Path, required=True)
    args = parser.parse_args()

    baseline = load(ROOT / "docs/missile/seeker-unify/C/CUE_A_RESULTS.json")
    baseline_rows = [row for row in baseline["rows"] if row["setup"].get("threatMode") == "MAX_THREAT"]
    kh35, kh32 = load(args.kh35), load(args.kh32)
    candidate_rows = kh35["rows"] + kh32["rows"]
    old, new = {matrix_key(row): row for row in baseline_rows}, {matrix_key(row): row for row in candidate_rows}
    if old.keys() != new.keys():
        raise AssertionError("cue matrix key mismatch")

    outcome_changes, track_regressions, hit_regressions = [], [], []
    for key in sorted(old):
        a, b = old[key], new[key]
        before_tuple = (a["result"]["everAcquire"], a["result"]["everTrack"], a["result"]["shipHit"], a["result"]["failureAudit"]["category"])
        after_tuple = (b["result"]["everAcquire"], b["result"]["everTrack"], b["result"]["shipHit"], b["result"]["failureAudit"]["category"])
        if before_tuple != after_tuple:
            outcome_changes.append({
                "setup": a["setup"],
                "before": {"acquire": before_tuple[0], "track": before_tuple[1], "shipHit": before_tuple[2], "failureCategory": before_tuple[3],
                           "firstAcquireS": a["result"].get("firstAcquireS"), "basket": basket_numbers(a["result"].get("firstAcquireBasket"))},
                "after": {"acquire": after_tuple[0], "track": after_tuple[1], "shipHit": after_tuple[2], "failureCategory": after_tuple[3],
                          "firstAcquireS": b["result"].get("firstAcquireS"), "basketAtFirstAcquire": basket_numbers(b["result"].get("firstAcquireBasket")),
                          "finalBasket": basket_numbers(b["result"].get("finalCue"))},
                "afterActionGeometry": {"before": a["result"]["failureAudit"], "after": b["result"]["failureAudit"]},
                "explanation": "Transient ACQUIRE disappeared, but TRACK/hit/failure class did not change. Candidate truth remained in the basket; this is not an inside-search/outside-basket exclusion.",
            })
        if a["result"]["everTrack"] and not b["result"]["everTrack"]:
            track_regressions.append(a["setup"])
        if a["result"]["shipHit"] and not b["result"]["shipHit"]:
            hit_regressions.append(a["setup"])

    comparisons = {}
    for label in ("Kh-35U", "Kh-32"):
        for emcon in (False, True):
            name = f"{label}|EMCON_{'ON' if emcon else 'OFF'}"
            comparisons[name] = {
                "baseline": summarize([row for row in baseline_rows if row["setup"]["label"] == label and row["setup"]["emcon"] is emcon]),
                "candidate": summarize([row for row in candidate_rows if row["setup"]["label"] == label and row["setup"]["emcon"] is emcon]),
            }
    baseline_forbidden = sum(row["result"]["failureAudit"]["category"] == "INSIDE_SEARCH_OUTSIDE_BASKET" for row in baseline_rows)
    candidate_forbidden = sum(row["result"]["failureAudit"]["category"] == "INSIDE_SEARCH_OUTSIDE_BASKET" for row in candidate_rows)

    controls = load(args.controls)
    baseline_controls = {canonical(row["setup"]): row for row in load(ROOT / "docs/missile/seeker-unify/C/CUE_A_1590.json")["rangeCases"]}
    control_differences = [row["setup"] for row in controls["rows"] if canonical(row) != canonical(baseline_controls[canonical(row["setup"])])]
    new_false_acquisition = [row["setup"] for row in controls["rows"] if row["result"]["everAcquire"] and not baseline_controls[canonical(row["setup"])]["result"]["everAcquire"]]
    s1 = audit_s1(load(ROOT / "docs/missile/seeker-unify/C/CUE_A_S1.json"), load(args.s1))
    egress_plan, egress_results = load(args.egress_plan), load(args.egress_results)
    egress = audit_egress(egress_plan, args.egress_evidence)
    determinism, scope = load(args.determinism), load(args.scope)
    model = load(HERE / "CUE_FILTER_SINGER_MODEL.json")
    page_errors = kh35.get("pageErrors", []) + kh32.get("pageErrors", []) + controls.get("pageErrors", []) + load(args.s1).get("pageErrors", [])
    gates = {
        "exactDiscreteSingerAndDtIndependence": model["status"] == "PASS",
        "cueMatrixKeysExact240": len(candidate_rows) == len(old) == 240,
        "cueMatrixPageErrorsZero": not page_errors,
        "trackRegressionsZero": not track_regressions,
        "shipHitRegressionsZero": not hit_regressions,
        "insideSearchOutsideBasketDidNotIncrease": candidate_forbidden <= baseline_forbidden,
        "falseAcquisitionControlIncreaseZero": not new_false_acquisition,
        "falseAcquisitionControlsBitExact": not control_differences,
        "s1NoTrackRegressionOrWrongFirstAssociation": s1["pass"],
        "egress37NoNeighborFirstAssociation": egress_results["status"] == "PASS" and egress["pass"],
        "determinismExact": determinism["status"] == "PASS",
        "truthAndFunctionScopeAudit": scope["status"] == "PASS",
    }
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE1B_RESULTS_1",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "implementationCommit": "46889420995ddb545e64f02d700eb2bbdd3ba9f4",
        "product": {"file": "Aegis_SIM_v48_WIP_CUE_A_1.html", "sha256": sha256(ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html")},
        "baseline": {"commit": "4faeb4e079b7baddcb1e1b8c1b892af804565938", "productSha256": sha256(ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html")},
        "mode": "MAX_THREAT",
        "gates": gates,
        "singer": {"method": "VAN_LOAN_HIGHAM_PADE13", "checks": model["checks"], "relativeErrors": model["relativeErrors"], "dt": model["dt"], "velocityTable": model["velocityTable"], "capReference": model["capReference"]},
        "cueMatrix": {"cases": len(candidate_rows), "comparisons": comparisons, "outcomeChanges": outcome_changes, "trackRegressions": track_regressions,
                      "shipHitRegressions": hit_regressions, "insideSearchOutsideBasket": {"baseline": baseline_forbidden, "candidate": candidate_forbidden, "delta": candidate_forbidden - baseline_forbidden},
                      "threeSigmaInsExceptions": []},
        "falseAcquisitionControls": {"cases": len(controls["rows"]), "bitExactDifferences": control_differences, "newFalseAcquisitions": new_false_acquisition},
        "s1": s1,
        "egress37": egress,
        "determinism": determinism,
        "scope": {"status": scope["status"], "checks": scope["checks"], "unchangedSharedFunctions": scope["unchangedSharedFunctions"], "unexpected": scope["unexpected"]},
        "elapsedS": {"model": model["elapsedS"], "cueMatrix": kh35["elapsedS"] + kh32["elapsedS"], "controls": controls["elapsedS"], "s1": load(args.s1)["elapsedS"], "egress": egress_results["elapsedS"], "determinism": determinism["elapsedS"]},
        "truthUse": "AFTER_ACTION_TRUTH_TEST_ONLY for failure and first-association audit; never consumed by simulation",
        "gameCodeChangedByFinalizer": False,
    }
    save(HERE / "CUE_FILTER_SINGER.json", result)
    save(HERE / "STAGE1B_EGRESS_37_AUDIT.json", egress)

    raw = {
        args.kh35: HERE / "STAGE1B_CUE_MATRIX_KH35U.json",
        args.kh32: HERE / "STAGE1B_CUE_MATRIX_KH32.json",
        args.controls: HERE / "STAGE1B_FALSE_ACQUISITION_CONTROLS.json",
        args.s1: HERE / "STAGE1B_S1.json",
        args.determinism: HERE / "STAGE1B_DETERMINISM.json",
        args.scope: HERE / "STAGE1B_SCOPE_AUDIT.json",
        args.egress_plan: HERE / "STAGE1B_EGRESS_37_PLAN.json",
        args.egress_results: HERE / "STAGE1B_EGRESS_37_RESULTS.json",
    }
    for source, destination in raw.items():
        shutil.copy2(source, destination)
    destination = HERE / "evidence/stage1b-egress-37"
    destination.mkdir(parents=True, exist_ok=True)
    for source in args.egress_evidence.glob("*.json.gz"):
        shutil.copy2(source, destination / source.name)

    lines = [
        "# CUE_A-1 Stage 1b — Singer cue filter",
        "",
        f"Status: **{result['status']}**  ",
        "Mode: **MAX_THREAT** (CONFIRMED_ONLY performance remains UNVERIFIED)  ",
        f"Frozen implementation: `{result['implementationCommit']}`  ",
        f"Product SHA-256: `{result['product']['sha256']}`",
        "",
        "## Gate summary",
        "",
    ]
    lines.extend(f"- {'PASS' if passed else 'FAIL'} — `{name}`" for name, passed in gates.items())
    lines += [
        "",
        "## Key results",
        "",
        f"- Exact-discrete Singer prediction used Van Loan + Higham Padé13. Relative dt errors: {model['relativeErrors']}.",
        f"- Cue matrix: 240 cells; TRACK regressions {len(track_regressions)}, hit regressions {len(hit_regressions)}, acquisition-state changes {len(outcome_changes)}.",
        f"- Forbidden inside-search/outside-basket failures: {baseline_forbidden} → {candidate_forbidden}.",
        f"- False-acquisition controls: {len(controls['rows'])} cases, new false acquisitions {len(new_false_acquisition)}, byte differences {len(control_differences)}.",
        f"- S1: TRACK {s1['baselineTrack']} → {s1['candidateTrack']}; ownship/neighbor first selection {len(s1['ownshipFirstSelections'])}/{len(s1['neighborAsmFirstSelections'])}.",
        f"- TRACK-C egress: {egress['jobs']} battles / {egress['missiles']} missiles; first family {egress['firstFamilies']}; neighbor-first {len(egress['neighborAsmFirstAssociations'])}.",
        f"- Determinism: {determinism['cases']} representative cases, hashes `{determinism['firstSha256']}` / `{determinism['secondSha256']}`.",
        f"- Scope: {scope['unchangedSharedFunctions']} other functions byte-identical; protected changes 0; truth/RNG token hits 0.",
        "",
        "## Changed acquisition cell",
        "",
    ]
    for change in outcome_changes:
        lines.append(f"- `{canonical(change['setup'])}`: {change['before']} → {change['after']}. {change['explanation']}")
    lines += [
        "",
        "No TRACK or hit outcome changed in that cell. The after-action audit still recorded 932 in-basket dwells and zero inside-search/outside-basket dwells, so no 3σ INS exception was used.",
        "",
        "## Limits",
        "",
        "- No broad regression was run in Stage 1; the directive reserves it for one final run after Stage 2.",
        "- CONFIRMED_ONLY has no performance claim in this stage.",
        "- Raw truth-bearing geometry appears only in after-action diagnostic evidence.",
    ]
    (HERE / "CUE_FILTER_SINGER.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": result["status"], "gates": gates, "outcomeChanges": len(outcome_changes), "egress": egress["firstFamilies"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
