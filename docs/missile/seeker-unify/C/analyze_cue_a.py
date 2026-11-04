#!/usr/bin/env python3
"""Merge and compare the Stage-3 CUE_A matrix with the frozen Stage-2 gate.

This analysis never executes or mutates the simulation.  AFTER_ACTION_TRUTH is
used only to classify a failed diagnostic row, matching the U0/U2 audit
contract.  The active cue and seeker paths never consume this output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def canonical_setup(setup: dict) -> str:
    keep = {
        key: setup.get(key)
        for key in ("seed", "label", "rangeKm", "speedKt", "turnDeg", "emcon")
    }
    return json.dumps(keep, sort_keys=True, separators=(",", ":"))


def category(row: dict) -> str:
    return str(row.get("result", {}).get("failureAudit", {}).get("category") or "MISSING")


def basket_violations(row: dict) -> list[dict]:
    violations: list[dict] = []
    for name in ("firstAcquireBasket", "firstTrackBasket", "finalCue"):
        basket = (row.get("result", {}).get(name) or {}).get("basket")
        if not basket:
            continue
        az = basket.get("azHalfDeg")
        sector = basket.get("searchSectorAzDeg")
        if isinstance(az, (int, float)) and isinstance(sector, (int, float)) and az > sector + 1e-9:
            violations.append({"field": name, "azHalfDeg": az, "searchSectorAzDeg": sector})
    return violations


def summarize(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    raw: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        s = row["setup"]
        raw[(s["label"], bool(s["emcon"]))].append(row)
    for (label, emcon), items in sorted(raw.items()):
        counts = Counter(category(row) for row in items)
        by_range = {
            str(distance): {
                "cases": len(group),
                "acquire": sum(bool(row["result"].get("everAcquire")) for row in group),
                "track": sum(bool(row["result"].get("everTrack")) for row in group),
            }
            for distance in sorted({row["setup"]["rangeKm"] for row in items})
            if (group := [row for row in items if row["setup"]["rangeKm"] == distance])
        }
        tracked_ranges = [float(distance) for distance, value in by_range.items() if value["track"]]
        groups[f"{label}|EMCON_{'ON' if emcon else 'OFF'}"] = {
            "cases": len(items),
            "acquire": sum(bool(row["result"].get("everAcquire")) for row in items),
            "track": sum(bool(row["result"].get("everTrack")) for row in items),
            "shipHit": sum(bool(row["result"].get("shipHit")) for row in items),
            "failureCategories": dict(sorted(counts.items())),
            "insideSearchOutsideBasketFailures": counts.get("INSIDE_SEARCH_OUTSIDE_BASKET", 0),
            "trackByLaunchRangeKm": by_range,
            "maxLaunchRangeKmWithTrack": max(tracked_ranges) if tracked_ranges else None,
        }
    total = Counter(category(row) for row in rows)
    return {
        "cases": len(rows),
        "acquire": sum(bool(row["result"].get("everAcquire")) for row in rows),
        "track": sum(bool(row["result"].get("everTrack")) for row in rows),
        "shipHit": sum(bool(row["result"].get("shipHit")) for row in rows),
        "failureCategories": dict(sorted(total.items())),
        "insideSearchOutsideBasketFailures": total.get("INSIDE_SEARCH_OUTSIDE_BASKET", 0),
        "groups": groups,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage2", type=Path, default=HERE / "BEAM_STAGE2_CUE_MATRIX.json")
    parser.add_argument("--stage1", type=Path, default=ROOT / "docs/missile/seeker-unify/B/U0_CUE_ACTIVE_CAP.json")
    parser.add_argument("--kh35-max", type=Path, required=True)
    parser.add_argument("--kh35-confirmed", type=Path, required=True)
    parser.add_argument("--kh32-max", type=Path, required=True)
    parser.add_argument("--kh32-confirmed", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--range-json", type=Path)
    parser.add_argument("--range-markdown", type=Path)
    parser.add_argument("--multi-json", type=Path)
    parser.add_argument("--multi-markdown", type=Path)
    args = parser.parse_args()

    stage1_file = load(args.stage1)
    stage1_rows = stage1_file["rows"]
    stage2_file = load(args.stage2)
    stage2_rows = stage2_file["rows"]
    stage2_by_key = {canonical_setup(row["setup"]): row for row in stage2_rows}
    shards = [load(path) for path in (
        args.kh35_max, args.kh35_confirmed, args.kh32_max, args.kh32_confirmed
    )]
    rows = [row for shard in shards for row in shard["rows"]]
    modes = sorted({row["setup"]["threatMode"] for row in rows})
    by_mode = {mode: [row for row in rows if row["setup"]["threatMode"] == mode] for mode in modes}

    comparisons: dict[str, dict] = {}
    all_changes: list[dict] = []
    for mode, current in by_mode.items():
        changes: list[dict] = []
        missing: list[str] = []
        for row in current:
            key = canonical_setup(row["setup"])
            before = stage2_by_key.get(key)
            if not before:
                missing.append(key)
                continue
            bt = bool(before["result"].get("everTrack"))
            at = bool(row["result"].get("everTrack"))
            ba = bool(before["result"].get("everAcquire"))
            aa = bool(row["result"].get("everAcquire"))
            if (bt, ba, category(before)) != (at, aa, category(row)):
                changes.append({
                    "setup": row["setup"],
                    "stage2": {"acquire": ba, "track": bt, "category": category(before)},
                    "stage3": {"acquire": aa, "track": at, "category": category(row)},
                })
        all_changes.extend({"mode": mode, **item} for item in changes)
        before_summary = summarize(stage2_rows)
        after_summary = summarize(current)
        comparisons[mode] = {
            "stage2": before_summary,
            "stage3": after_summary,
            "trackRegressions": sum(x["stage2"]["track"] and not x["stage3"]["track"] for x in changes),
            "trackImprovements": sum(not x["stage2"]["track"] and x["stage3"]["track"] for x in changes),
            "changedRows": changes,
            "missingStage2Rows": missing,
            "insideSearchOutsideBasketDelta": (
                after_summary["insideSearchOutsideBasketFailures"]
                - before_summary["insideSearchOutsideBasketFailures"]
            ),
        }

    violations = [
        {"setup": row["setup"], "violations": found}
        for row in rows if (found := basket_violations(row))
    ]
    page_errors = [
        {"label": shard["label"], "mode": shard["mode"], "errors": shard.get("pageErrors", [])}
        for shard in shards if shard.get("pageErrors")
    ]
    duplicates = len(rows) - len({(canonical_setup(row["setup"]), row["setup"]["threatMode"]) for row in rows})
    expected_per_mode = len(stage2_rows)
    gates = {
        "allFourShardsPresent": len(shards) == 4,
        "caseCount": len(rows) == expected_per_mode * 2,
        "uniqueCases": duplicates == 0,
        "stage2Coverage": all(not item["missingStage2Rows"] for item in comparisons.values()),
        "noPageErrors": not page_errors,
        "azBasketNeverExceedsSearchSector": not violations,
        "insideSearchOutsideBasketDidNotIncrease": all(
            item["insideSearchOutsideBasketDelta"] <= 0 for item in comparisons.values()
        ),
    }
    diagnostics = load(args.diagnostics) if args.diagnostics else None
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_A_RESULTS_1",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "stage2Input": str(args.stage2),
        "stage1Input": str(args.stage1),
        "stage1InputSha256": hashlib.sha256(args.stage1.read_bytes()).hexdigest(),
        "stage2InputSha256": hashlib.sha256(args.stage2.read_bytes()).hexdigest(),
        "stage3InputSha256": sorted({shard["inputSha256"] for shard in shards}),
        "caseCounts": {"stage1": len(stage1_rows), "stage2": len(stage2_rows), "stage3": len(rows)},
        "stage1Summary": summarize(stage1_rows),
        "elapsedS": sum(float(shard.get("elapsedS", 0)) for shard in shards),
        "gates": gates,
        "pageErrors": page_errors,
        "basketViolations": violations,
        "comparisons": comparisons,
        "allChangedRows": all_changes,
        "diagnostics": ({
            "inputSha256": diagnostics["inputSha256"],
            "pageErrors": diagnostics["pageErrors"],
            "velocity": diagnostics["velocity"],
            "dlHook": diagnostics["dlHook"],
            "boundarySelfTest": diagnostics["boundarySelfTest"],
            "contract": diagnostics["contract"],
        } if diagnostics else None),
        "rows": rows,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# SEEKER_UNIFY_C Stage 3 — CUE_A results",
        "",
        f"Status: **{result['status']}**",
        "",
        f"- Stage 2 cases: {len(stage2_rows)}",
        f"- Stage 3 cases: {len(rows)} (MAX_THREAT + CONFIRMED_ONLY)",
        f"- Page errors: {sum(len(q['errors']) for q in page_errors)}",
        f"- Azimuth-basket/search-sector violations: {len(violations)}",
        "",
        "## Gates",
        "",
    ]
    lines += [f"- {'PASS' if value else 'FAIL'} — `{name}`" for name, value in gates.items()]
    lines += ["", "## Stage 1 → Stage 2 → Stage 3 by launch range", "", "Each range cell is TRACK/cases. This is launch-range outcome, not a truth-derived in-flight range.", "", "| missile / EMCON | Stage 1 | Stage 2 | Stage 3 MAX_THREAT | Stage 3 CONFIRMED_ONLY |", "|---|---|---|---|---|"]
    stage1_summary = summarize(stage1_rows)
    stage2_summary = summarize(stage2_rows)
    for group_name in sorted(stage2_summary["groups"]):
        def cells(summary):
            group = summary["groups"][group_name]
            return " · ".join(f"{distance}km {value['track']}/{value['cases']}" for distance, value in group["trackByLaunchRangeKm"].items())
        lines.append(f"| {group_name.replace('|', ' / ')} | {cells(stage1_summary)} | {cells(stage2_summary)} | {cells(comparisons['MAX_THREAT']['stage3'])} | {cells(comparisons['CONFIRMED_ONLY']['stage3'])} |")
    lines += ["", "## Stage 2 → Stage 3", "", "| Mode | TRACK | hit | inside-sector/outside-basket | delta | regressions | improvements |", "|---|---:|---:|---:|---:|---:|---:|"]
    for mode in modes:
        item = comparisons[mode]
        after = item["stage3"]
        lines.append(
            f"| {mode} | {item['stage2']['track']} → {after['track']} | "
            f"{item['stage2']['shipHit']} → {after['shipHit']} | "
            f"{item['stage2']['insideSearchOutsideBasketFailures']} → {after['insideSearchOutsideBasketFailures']} | "
            f"{item['insideSearchOutsideBasketDelta']:+d} | {item['trackRegressions']} | {item['trackImprovements']} |"
        )
    if diagnostics:
        lines += ["", "## Launch velocity and disconnected DL hook", "", "| label | time | launch velocity | position error | range sigma | az half |", "|---|---:|---|---:|---:|---:|"]
        for row in diagnostics["velocity"]:
            setup, basket, truth = row["setup"], row["basket"], row["afterActionTruth"]
            lines.append(f"| {setup['label']} | {setup['seconds']} s | {'known' if setup['known'] else 'null'} | {truth['errorM']:.1f} m | {basket['rangeSigmaM']:.1f} m | {basket['azHalfDeg']:.2f}° |")
        dl = diagnostics["dlHook"]
        lines += ["", f"Disconnected production DL: `{str(dl['connected']).lower()}`; diagnostic hook update: `{'PASS' if dl['result']['ok'] else 'FAIL'}`."]
    lines += [
        "",
        "`failureAudit` classification is AFTER_ACTION_TRUTH_TEST_ONLY and is never consumed by cue, seeker, association, or guidance code.",
    ]
    args.markdown.write_text("\n".join(lines) + "\n")

    if diagnostics and args.range_json and args.range_markdown:
        range_result = {
            "schema": "AEGIS_SEEKER_UNIFY_C_RANGE_ESTIMATE_ACCURACY_1",
            "inputSha256": diagnostics["inputSha256"],
            "truthUse": "AFTER_ACTION_TRUTH_TEST_ONLY",
            **diagnostics["rangeEstimate"],
        }
        args.range_json.write_text(json.dumps(range_result, ensure_ascii=False, indent=2) + "\n")
        range_lines = [
            "# CUE_A elevation range-estimate accuracy",
            "",
            "Direct range is diagnostic-only; it never overwrites the tactical cue. Error uses AFTER_ACTION_TRUTH_TEST_ONLY.",
            "",
            "| missile | cases | samples | mean case bias | median | mean case RMSE | interpretation |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
        for label, summary in diagnostics["rangeEstimate"]["summary"].items():
            def fmt(value):
                return "n/a" if value is None else f"{value / 1000:.2f} km"
            interpretation = "meaningful high-altitude range information" if label == "Kh-32" else "low-elevation geometry is effectively uninformative"
            range_lines.append(f"| {label} | {summary['cases']} | {summary['availableSamples']} | {fmt(summary['meanOfCaseMeanErrorM'])} | {fmt(summary['medianCaseAbsMeanErrorM'])} | {fmt(summary['meanCaseRmseM'])} | {interpretation} |")
        range_lines += ["", "Kh-35U cases use 10/20/30 km at 12 m; Kh-32 cases use 60/100/130 km at 10,000 m, five deterministic seeds per range and 20 samples per case."]
        args.range_markdown.write_text("\n".join(range_lines) + "\n")

    if diagnostics and args.multi_json and args.multi_markdown:
        multi_result = {
            "schema": "AEGIS_SEEKER_UNIFY_C_MULTI_EMITTER_1",
            "inputSha256": diagnostics["inputSha256"],
            "truthUse": "AFTER_ACTION_TRUTH_TEST_ONLY",
            **diagnostics["multiEmitter"],
        }
        args.multi_json.write_text(json.dumps(multi_result, ensure_ascii=False, indent=2) + "\n")
        lure_rows = [row for row in diagnostics["multiEmitter"]["rows"] if (row["afterActionTruth"].get("nearestToAnonymousBearing") or {}).get("owner") == row["afterActionTruth"].get("otherOwner")]
        summary = diagnostics["multiEmitter"]["summary"]
        multi_lines = [
            "# CUE_A multi-emitter diagnostic",
            "",
            f"- Cases: {summary['cases']}; anonymous measurements: {summary['measurements']}",
            f"- Forbidden identity/coordinate payload keys: {len(summary['anonymousPayloadLeaks'])}",
            f"- Other-emitter selections (AFTER_ACTION_TRUTH audit): {len(lure_rows)}",
            "",
            "A nearby emitter winning the Mahalanobis gate is recorded as a real passive-RF ambiguity, not hidden or forcibly reassigned.",
            "",
            "| missile | mode | seed | offset | selected owner | SNR |",
            "|---|---|---:|---:|---|---:|",
        ]
        for row in lure_rows:
            setup = row["setup"]
            nearest = row["afterActionTruth"]["nearestToAnonymousBearing"]
            multi_lines.append(f"| {setup['label']} | {setup['threatMode']} | {setup['seed']} | {setup['offsetDeg']}° | {nearest['owner']} | {row['measurement']['snr']:.2f} |")
        args.multi_markdown.write_text("\n".join(multi_lines) + "\n")
    print(json.dumps({"status": result["status"], "caseCounts": result["caseCounts"], "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
