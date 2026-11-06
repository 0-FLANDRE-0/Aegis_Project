#!/usr/bin/env python3
"""Compare Stage-2 full cue and TRACK-C S1 matrices with Stage 1."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def cue_key(row: dict) -> tuple:
    q = row["setup"]
    return (q["label"], q["rangeKm"], q["speedKt"], q["turnDeg"], q["seed"], q["emcon"])


def s1_key(row: dict) -> tuple:
    q = row["setup"]
    return (q["launchRangeKm"], q["separationDeg"], q["seed"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cue-before", type=Path, required=True)
    parser.add_argument("--cue-after", type=Path, required=True)
    parser.add_argument("--s1-before", type=Path, required=True)
    parser.add_argument("--s1-after", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cb = json.loads(args.cue_before.read_text())
    ca = json.loads(args.cue_after.read_text())
    sb = json.loads(args.s1_before.read_text())
    sa = json.loads(args.s1_after.read_text())
    cue_before = {cue_key(row): row for row in cb["rows"]}
    cue_after = {cue_key(row): row for row in ca["rows"]}
    s1_before = {s1_key(row): row for row in sb["rows"]}
    s1_after = {s1_key(row): row for row in sa["rows"]}
    if cue_before.keys() != cue_after.keys() or s1_before.keys() != s1_after.keys():
        raise SystemExit("matrix key mismatch")

    cue_regressions = []
    cue_improvements = []
    summary = {}
    for key in sorted(cue_before):
        before, after = cue_before[key], cue_after[key]
        if before["result"]["everTrack"] and not after["result"]["everTrack"]:
            cue_regressions.append({"key": key, "before": before["result"], "after": after["result"]})
        if not before["result"]["everTrack"] and after["result"]["everTrack"]:
            cue_improvements.append({"key": key, "before": before["result"], "after": after["result"]})
    for label in ("Kh-35U", "Kh-32"):
        for emcon in (False, True):
            for distance in (60, 100, 130):
                for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90)):
                    keys = [key for key in cue_before if key[:4] == (label, distance, speed, turn) and key[5] == emcon]
                    summary["|".join(map(str, (label, distance, speed, turn, emcon)))] = {
                        "shots": len(keys),
                        "stage1Track": sum(cue_before[key]["result"]["everTrack"] for key in keys),
                        "stage2Track": sum(cue_after[key]["result"]["everTrack"] for key in keys),
                    }

    s1_regressions = []
    s1_improvements = []
    s1_final_differences = []
    ownship_first = []
    neighbor_first = []
    for key in sorted(s1_before):
        before, after = s1_before[key], s1_after[key]
        before_track = before["final"]["seekerMode"] == "TRACK"
        after_track = after["final"]["seekerMode"] == "TRACK"
        if before_track and not after_track:
            s1_regressions.append({"key": key, "before": before["final"], "after": after["final"]})
        if not before_track and after_track:
            s1_improvements.append({"key": key, "before": before["final"], "after": after["final"]})
        if before["final"] != after["final"]:
            s1_final_differences.append({"key": key, "before": before["final"], "after": after["final"]})
        first = after.get("metrics", {}).get("firstCandidate") or {}
        ident = str(first.get("id", ""))
        kind = str(first.get("kind", ""))
        if ident.startswith("SHIP") or kind == "SHIP":
            ownship_first.append({"key": key, "candidate": first})
        if "ASM" in ident or kind in {"ASM", "RF_OBJECT"}:
            neighbor_first.append({"key": key, "candidate": first})

    hard_gate = not cb.get("pageErrors") and not ca.get("pageErrors") and not sb.get("pageErrors") and not sa.get("pageErrors") and not ownship_first and not neighbor_first
    explanation_needed = bool(cue_regressions or s1_regressions)
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_SECONDARY_COMPARISON_1",
        "status": "NEEDS_NUMERIC_EXPLANATION" if hard_gate and explanation_needed else "PASS" if hard_gate else "FAIL",
        "cue": {
            "rows": len(cue_after), "summary": summary,
            "trackRegressions": cue_regressions, "trackImprovements": cue_improvements,
            "pageErrors": {"stage1": cb.get("pageErrors", []), "stage2": ca.get("pageErrors", [])},
        },
        "s1": {
            "rows": len(s1_after),
            "stage1Track": sum(row["final"]["seekerMode"] == "TRACK" for row in s1_before.values()),
            "stage2Track": sum(row["final"]["seekerMode"] == "TRACK" for row in s1_after.values()),
            "trackRegressions": s1_regressions, "trackImprovements": s1_improvements,
            "finalStateDifferences": s1_final_differences,
            "ownshipFirstSelections": ownship_first, "neighborAsmFirstSelections": neighbor_first,
            "pageErrors": {"stage1": sb.get("pageErrors", []), "stage2": sa.get("pageErrors", [])},
        },
        "hardGatePass": hard_gate,
        "numericExplanationComplete": not explanation_needed,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "status": result["status"],
        "cueRegressions": len(cue_regressions),
        "cueImprovements": len(cue_improvements),
        "s1Track": [result["s1"]["stage1Track"], result["s1"]["stage2Track"]],
        "s1Regressions": len(s1_regressions),
        "s1Improvements": len(s1_improvements),
        "ownshipFirst": len(ownship_first),
        "neighborFirst": len(neighbor_first),
        "hardGatePass": hard_gate,
    }, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 2 if result["status"] == "NEEDS_NUMERIC_EXPLANATION" else 1)


if __name__ == "__main__":
    main()
