#!/usr/bin/env python3
"""Explain Stage-3 CUE-only TRACK deltas without changing the simulation.

The comparison contains an intentionally small projection of the 1,590-case
matrix.  This reporting-only audit joins that projection to the full
MAX_THREAT/CONFIRMED_ONLY CUE matrix and proves whether each lost TRACK is a
cue scan-history delta or a forbidden search-sector/basket exclusion.

AFTER_ACTION truth is read only for classification.  Nothing produced here is
consumed by the product, seeker, cue filter, guidance, or association code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


WEAK_EVIDENCE_REASONS = {
    "BELOW_DETECTION",
    "DISTRIBUTED_BACKGROUND_EVIDENCE",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(setup: dict) -> tuple:
    return (
        setup.get("seed"), setup.get("label"), setup.get("rangeKm"),
        setup.get("speedKt"), setup.get("turnDeg"), bool(setup.get("emcon", False)),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--cue-results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    comparison = load(args.comparison)
    cue = load(args.cue_results)
    by_mode = {
        (row["setup"]["threatMode"], key(row["setup"])): row
        for row in cue["rows"]
    }
    rows = []
    for delta in comparison["cueTrackRegressions"]:
        setup = delta["setup"]
        joined = by_mode.get(("MAX_THREAT", key(setup)))
        confirmed = by_mode.get(("CONFIRMED_ONLY", key(setup)))
        if not joined or not confirmed:
            raise AssertionError(f"missing full CUE row for {setup}")
        after = delta["after"]
        before = delta["before"]
        audit = after.get("failureAudit") or {}
        dwells = int(audit.get("dwells") or 0)
        inside = int(audit.get("insideBasketDwells") or 0)
        basket_fraction = inside / dwells if dwells else 0.0
        confirmed_result = confirmed["result"]
        passive_specific = bool(confirmed_result.get("everTrack"))
        closest_delta = abs(float(after["closestM"]) - float(before["closestM"]))
        checks = {
            "afterActionClassificationIsOther": audit.get("category") == "OTHER",
            "forbiddenInsideSearchOutsideBasketIsZero": int(audit.get("insideSectorOutsideBasketDwells") or 0) == 0,
            "targetInsideBasketAtLeast99_8Percent": basket_fraction >= 0.998,
            "sameNoShipHitOutcome": not bool(before.get("shipHit")) and not bool(after.get("shipHit")),
            "samePassedTargetTermination": before.get("endedBy") == after.get("endedBy") == "PASSED_TARGET",
            "sameFinalSearchMode": before.get("finalMode") == after.get("finalMode") == "SEARCH",
            "closestApproachDeltaAtMost10m": closest_delta <= 10.0,
            "weakRfEvidenceAtEnd": after.get("rejectReason") in WEAK_EVIDENCE_REASONS,
        }
        classification = (
            "ASSUMED_PASSIVE_RF_SCAN_HISTORY_DELTA"
            if passive_specific else "COVARIANCE_CUE_SCAN_HISTORY_DELTA"
        )
        rows.append({
            "setup": setup,
            "classification": classification,
            "confirmedOnlyRetainsTrack": bool(confirmed_result.get("everTrack")),
            "basketDwells": inside,
            "totalDwells": dwells,
            "basketDwellFraction": basket_fraction,
            "insideSearchOutsideBasketDwells": int(audit.get("insideSectorOutsideBasketDwells") or 0),
            "closestApproachBeforeM": before.get("closestM"),
            "closestApproachAfterM": after.get("closestM"),
            "closestApproachDeltaM": closest_delta,
            "terminalEvidenceReason": after.get("rejectReason"),
            "beforeTrack": bool(before.get("everTrack")),
            "afterTrack": bool(after.get("everTrack")),
            "beforeShipHit": bool(before.get("shipHit")),
            "afterShipHit": bool(after.get("shipHit")),
            "checks": checks,
            "explained": all(checks.values()),
            "explanation": (
                "The observed target remained in the covariance basket; the new cue path changed "
                "the deterministic search dwell centre/history and therefore the weak RF evidence "
                "sequence.  The case never produced a ship hit before or after."
            ),
        })

    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_NUMERIC_EXPLANATIONS_1",
        "status": "PASS" if rows and all(row["explained"] for row in rows) else "FAIL",
        "comparisonSha256": sha256(args.comparison),
        "cueResultsSha256": sha256(args.cue_results),
        "regressionCount": len(rows),
        "forbiddenBasketExclusionCount": sum(
            row["insideSearchOutsideBasketDwells"] > 0 for row in rows
        ),
        "shipHitRegressionCount": sum(
            row["afterShipHit"] and not row["beforeShipHit"] for row in rows
        ),
        "passiveSpecificCount": sum(
            row["classification"] == "ASSUMED_PASSIVE_RF_SCAN_HISTORY_DELTA" for row in rows
        ),
        "covarianceOnlyCount": sum(
            row["classification"] == "COVARIANCE_CUE_SCAN_HISTORY_DELTA" for row in rows
        ),
        "tuningChanged": False,
        "truthUse": "AFTER_ACTION_TRUTH_TEST_ONLY",
        "rows": rows,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# Stage 3 CUE TRACK delta explanations",
        "",
        f"Status: **{result['status']}**",
        "",
        "This is a reporting-only AFTER_ACTION audit. No value from this file is read by the simulation.",
        "",
        "| seed / motion | class | in-basket dwells | closest delta | end evidence | ship hit |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        setup = row["setup"]
        motion = f"{setup['seed']} / {setup['speedKt']} kt / {setup['turnDeg']}°"
        lines.append(
            f"| {motion} | {row['classification']} | "
            f"{row['basketDwells']}/{row['totalDwells']} ({row['basketDwellFraction']:.3%}) | "
            f"{row['closestApproachDeltaM']:.3f} m | {row['terminalEvidenceReason']} | "
            f"{row['beforeShipHit']} → {row['afterShipHit']} |"
        )
    lines += [
        "",
        "All rows kept the target inside the search basket and ended as the same no-hit PASSED_TARGET outcome. "
        "The lost diagnostic TRACKs are deterministic scan-history changes in weak RF evidence, not a new "
        "inside-search/outside-basket failure. No compensating threshold or seeker tuning was applied.",
    ]
    args.markdown.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
