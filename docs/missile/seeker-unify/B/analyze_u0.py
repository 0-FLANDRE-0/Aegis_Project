#!/usr/bin/env python3
"""Reduce U0 cue matrices into the directive gate and review tables."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def key(row: dict) -> tuple:
    q = row["setup"]
    return (q["label"], q["rangeKm"], q["speedKt"], q["turnDeg"], q["seed"], q["emcon"])


def stats(values: list[float]) -> dict | None:
    values = sorted(v for v in values if v is not None and math.isfinite(v))
    if not values:
        return None
    return {"min": values[0], "median": values[len(values) // 2], "max": values[-1], "count": len(values)}


baseline = load("U0_CUE_BASELINE.json")
shadow = load("U0_CUE_SHADOW.json")
if (HERE / "U0_CUE_SHADOW_CAP.json").exists():
    shadow = load("U0_CUE_SHADOW_CAP.json")
active = load("U0_CUE_ACTIVE_CAP.json") if (HERE / "U0_CUE_ACTIVE_CAP.json").exists() else load("U0_CUE_ACTIVE.json")
b = {key(row): row for row in baseline["rows"]}
s = {key(row): row for row in shadow["rows"]}
a = {key(row): row for row in active["rows"]}
assert b.keys() == s.keys() == a.keys()

shadow_diffs = []
regressions = []
justified_regressions = []
improvements = []
failure_categories: dict[str, list[dict]] = defaultdict(list)
for k in sorted(b):
    rb, rs, ra = b[k]["result"], s[k]["result"], a[k]["result"]
    comparable = ("everAcquire", "everTrack", "firstAcquireS", "firstTrackS", "finalMode", "closestM", "endedBy", "alive", "flightTimeS", "shipHit", "rejectReason")
    diff = {field: [rb.get(field), rs.get(field)] for field in comparable if rb.get(field) != rs.get(field)}
    if diff:
        shadow_diffs.append({"key": k, "differences": diff})
    if not ra["everTrack"]:
        audit = ra.get("failureAudit") or {"category": "OTHER", "reason": "MISSING_FAILURE_AUDIT"}
        failure_categories[audit["category"]].append({"key": k, "reason": audit.get("reason"), "audit": audit})
    if rb["everTrack"] and not ra["everTrack"]:
        row = {"key": k, "baseline": rb, "active": ra, "failureAudit": ra.get("failureAudit")}
        if (ra.get("failureAudit") or {}).get("category") == "OUTSIDE_SEARCH_SECTOR":
            justified_regressions.append(row)
        else:
            regressions.append(row)
    if not rb["everTrack"] and ra["everTrack"]:
        improvements.append({"key": k, "baseline": rb, "active": ra})

summary: dict[str, dict] = {}
for label in ("Kh-35U", "Kh-32"):
    for emcon in (False, True):
        for distance in (60, 100, 130):
            for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90)):
                kk = (label, distance, speed, turn, emcon)
                rows_b = [r for r in baseline["rows"] if (r["setup"]["label"], r["setup"]["rangeKm"], r["setup"]["speedKt"], r["setup"]["turnDeg"], r["setup"]["emcon"]) == kk]
                rows_a = [r for r in active["rows"] if (r["setup"]["label"], r["setup"]["rangeKm"], r["setup"]["speedKt"], r["setup"]["turnDeg"], r["setup"]["emcon"]) == kk]
                summary["|".join(map(str, kk))] = {"baselineTrack": sum(r["result"]["everTrack"] for r in rows_b), "activeTrack": sum(r["result"]["everTrack"] for r in rows_a), "shots": len(rows_a)}

baskets = []
attempts = updates = converged_rows = 0
for row in active["rows"]:
    r = row["result"]
    snap = r.get("firstTrackBasket") or r.get("firstAcquireBasket")
    if snap and snap.get("basket"):
        q = snap["basket"]
        baskets.append({"rangeLowM": q["rangeLowM"], "rangeHighM": q["rangeHighM"], "azHalfDeg": q["azHalfDeg"], "searchSectorAzDeg": q.get("searchSectorAzDeg"), "rangeAgeS": q["rangeAgeS"], "bearingAgeS": q["bearingAgeS"]})
    p = (r.get("finalCue") or {}).get("passive")
    if p:
        attempts += p["attempts"]
        updates += p["updates"]
        converged_rows += int(bool(p.get("lastConverged")))

cap_violations = [q for q in baskets if q.get("searchSectorAzDeg") is None or q["azHalfDeg"] > q["searchSectorAzDeg"] + 1e-12]
result = {
    "schema": "AEGIS_SEEKER_UNIFY_B_U0_ANALYSIS_1",
    "status": "PASS" if not shadow_diffs and not regressions and not cap_violations and not baseline["pageErrors"] and not shadow["pageErrors"] and not active["pageErrors"] else "FAIL",
    "rows": len(a),
    "shadowOutcomeDifferences": shadow_diffs,
    "activeTrackRegressions": regressions,
    "activeTrackRegressionsJustifiedOutsideSearchSector": justified_regressions,
    "activeTrackImprovements": improvements,
    "activeFailureCategories": {name: {"count": len(rows), "rows": rows} for name, rows in sorted(failure_categories.items())},
    "azimuthCapViolations": cap_violations,
    "summary": summary,
    "basketAtFirstTrackOrAcquire": {field: stats([q[field] for q in baskets]) for field in ("rangeLowM", "rangeHighM", "azHalfDeg", "rangeAgeS", "bearingAgeS")},
    "passiveBearingClock": {"attempts": attempts, "updates": updates, "updateRate": updates / attempts if attempts else None, "rowsEndingConverged": converged_rows},
    "pageErrors": {"baseline": baseline["pageErrors"], "shadow": shadow["pageErrors"], "active": active["pageErrors"]},
}
(HERE / "U0_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

def table_rows(label: str, emcon: bool) -> str:
    lines = ["| Range | Motion | Baseline TRACK | U0 TRACK |", "|---:|---|---:|---:|"]
    for distance in (100, 130):
        for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90)):
            q = summary["|".join(map(str, (label, distance, speed, turn, emcon)))]
            motion = f"{speed} kn straight" if not turn else f"{speed} kn + {turn} deg"
            lines.append(f"| {distance} km | {motion} | {q['baselineTrack']}/{q['shots']} | {q['activeTrack']}/{q['shots']} |")
    return "\n".join(lines)

md = f"""# U0 results

## Status header

- IMPLEMENTED: TargetCue accessor, independent cue clocks, SHADOW/ACTIVE hard basket
- TESTED: {len(a)}-case cue matrix for each of baseline, SHADOW, and ACTIVE
- APPROVED: constants frozen by commit `3bdcde42ce8deac0d6962e6b50ddedcfde7991b8`
- UNRESOLVED: pre-launch track age remains unavailable
- RELEASE: no release; PR only

Overall: **{result['status']}**

- SHADOW outcome differences: {len(shadow_diffs)}
- baseline TRACK to U0 unexplained/defect failure: {len(regressions)}
- baseline TRACK to justified outside-search-sector failure: {len(justified_regressions)}
- baseline failure to U0 TRACK: {len(improvements)}
- azimuth basket cap violations: {len(cap_violations)}
- passive clock update/attempt: {updates}/{attempts} ({(100*updates/attempts if attempts else 0):.2f}%)

## ACTIVE failure classification (after-action truth only)

```json
{json.dumps({name: len(rows) for name, rows in sorted(failure_categories.items())}, indent=2)}
```

## Kh-35U, EMCON OFF

{table_rows('Kh-35U', False)}

## Kh-35U, EMCON ON

{table_rows('Kh-35U', True)}

## Basket at first TRACK (or first ACQUIRE if TRACK was absent)

```json
{json.dumps(result['basketAtFirstTrackOrAcquire'], indent=2)}
```
"""
(HERE / "U0_RESULTS.md").write_text(md)
print(json.dumps({"status": result["status"], "shadowDiffs": len(shadow_diffs), "regressions": len(regressions), "justifiedRegressions": len(justified_regressions), "improvements": len(improvements), "failureCategories": {name: len(rows) for name, rows in sorted(failure_categories.items())}, "azimuthCapViolations": len(cap_violations), "passiveUpdateRate": result["passiveBearingClock"]["updateRate"]}, indent=2))
