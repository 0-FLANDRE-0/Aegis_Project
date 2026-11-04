#!/usr/bin/env python3
"""Compare the Stage 2 ASM beam/path correction with the Stage 1 baseline."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def key(row: dict) -> str:
    return json.dumps(row["setup"], sort_keys=True, separators=(",", ":"))


def pairs(before: list[dict], after: list[dict]) -> list[tuple[dict, dict]]:
    left = {key(row): row for row in before}
    right = {key(row): row for row in after}
    if left.keys() != right.keys():
        raise AssertionError({"missingAfter": sorted(left.keys() - right.keys()), "missingBefore": sorted(right.keys() - left.keys())})
    return [(left[k], right[k]) for k in sorted(left)]


def acquire_range_m(row: dict, field: str) -> float | None:
    time_s = row.get("result", {}).get(field)
    if time_s is None:
        return None
    setup = row["setup"]
    closure = 280.0 - float(setup.get("speedKt", 0)) * 0.514444
    # The fixture moves both objects for one fixed tick before recording i=0.
    horizontal = max(0.0, float(setup["rangeKm"]) * 1000.0 - closure * (float(time_s) + 1 / 60))
    target_z = 11.5
    return math.hypot(horizontal, float(setup.get("altM", 0)) - target_z)


def exact_differences(rows: list[tuple[dict, dict]]) -> list[dict]:
    return [{"setup": after["setup"], "before": before, "after": after} for before, after in rows if before != after]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    candidate = json.loads(args.candidate.read_text())
    range_pairs = pairs(baseline["rangeCases"], candidate["rangeCases"])
    cue_pairs = pairs(baseline["cueCases"], candidate["cueCases"])
    sam_pairs = pairs(baseline["samArhCases"], candidate["samArhCases"])
    radar_pairs = pairs(baseline["radarCases"], candidate["radarCases"])
    controls = [(b, a) for b, a in range_pairs if b["setup"]["control"] != "TARGET"]
    target = [(b, a) for b, a in range_pairs if b["setup"]["control"] == "TARGET"]
    false_before = sum(bool(b["result"]["everAcquire"] or b["result"]["everTrack"]) for b, _ in controls)
    false_after = sum(bool(a["result"]["everAcquire"] or a["result"]["everTrack"]) for _, a in controls)
    new_false = [a["setup"] for b, a in controls if not (b["result"]["everAcquire"] or b["result"]["everTrack"]) and (a["result"]["everAcquire"] or a["result"]["everTrack"])]
    target_track_regressions = [{"setup": a["setup"], "before": b["result"], "after": a["result"]} for b, a in target if b["result"]["everTrack"] and not a["result"]["everTrack"]]
    cue_track_regressions = [{"setup": a["setup"], "before": b["result"], "after": a["result"]} for b, a in cue_pairs if b["result"]["everTrack"] and not a["result"]["everTrack"]]
    cue_track_improvements = [{"setup": a["setup"], "before": b["result"], "after": a["result"]} for b, a in cue_pairs if not b["result"]["everTrack"] and a["result"]["everTrack"]]
    snr_changes = []
    for before, after in target:
        bsnr = before.get("snapshot", {}).get("measurement", {}).get("snr")
        asnr = after.get("snapshot", {}).get("measurement", {}).get("snr")
        if isinstance(bsnr, (int, float)) and isinstance(asnr, (int, float)):
            snr_changes.append({"setup": after["setup"], "beforeSnr": bsnr, "afterSnr": asnr, "ratio": asnr / bsnr if bsnr else None})
    distributions: dict[str, dict] = {}
    for label, rows in (("before", [b for b, _ in target]), ("after", [a for _, a in target])):
        grouped: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            if row["setup"]["kind"] != "DDG":
                continue
            grouped[str(row["setup"]["altM"])].append(row)
        distributions[label] = {}
        for altitude, group in grouped.items():
            for event, time_field in (("acquire", "firstAcquireS"), ("track", "firstTrackS")):
                values = sorted(value for row in group if (value := acquire_range_m(row, time_field)) is not None)
                distributions[label][f"DDG_{altitude}m_{event}"] = {
                    "count": len(values),
                    "minM": min(values) if values else None,
                    "medianM": values[len(values) // 2] if values else None,
                    "maxM": max(values) if values else None,
                    "method": "fixture kinematics from recorded first-mode time; diagnostic-only",
                }
    exact_sam = exact_differences(sam_pairs)
    exact_radar = exact_differences(radar_pairs)
    unexplained = bool(target_track_regressions or cue_track_regressions)
    hard_gate_pass = not candidate.get("pageErrors") and not new_false and not exact_sam and not exact_radar
    status = "NEEDS_NUMERIC_EXPLANATION" if hard_gate_pass and unexplained else "PASS" if hard_gate_pass else "FAIL"
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_COMPARISON_1",
        "status": status,
        "caseCounts": {name: len(candidate[name]) for name in ("rangeCases", "samArhCases", "cueCases", "radarCases")},
        "pageErrors": candidate.get("pageErrors", []),
        "falseAcquisitionControls": {"rows": len(controls), "before": false_before, "after": false_after, "new": new_false},
        "targetTrackRegressions": target_track_regressions,
        "cueTrackRegressions": cue_track_regressions,
        "cueTrackImprovements": cue_track_improvements,
        "samExactDifferences": exact_sam,
        "radarExactDifferences": exact_radar,
        "targetSnapshotSnrChanges": snr_changes,
        "firstAcquireTrackRangeDistributions": distributions,
        "hardGatePass": hard_gate_pass,
        "numericExplanationComplete": not unexplained,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "caseCounts", "pageErrors", "falseAcquisitionControls", "targetTrackRegressions", "cueTrackRegressions", "cueTrackImprovements", "hardGatePass")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status == "PASS" else 2 if status == "NEEDS_NUMERIC_EXPLANATION" else 1)


if __name__ == "__main__":
    main()

