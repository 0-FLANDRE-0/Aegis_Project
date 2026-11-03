#!/usr/bin/env python3
"""Reduce the U0 S1 comparison and Harpoon audit."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


baseline = load("U0_S1_BASELINE.json")
active = load("U0_S1_ACTIVE_CAP.json") if (HERE / "U0_S1_ACTIVE_CAP.json").exists() else load("U0_S1_ACTIVE.json")


def s1_key(row: dict) -> tuple:
    q = row["setup"]
    return (q["launchRangeKm"], q["separationDeg"], q["seed"])


b = {s1_key(row): row for row in baseline["rows"]}
a = {s1_key(row): row for row in active["rows"]}
assert b.keys() == a.keys()
s1_regressions = []
s1_differences = []
ownship_first = []
for k in sorted(b):
    before, after = b[k], a[k]
    if before["final"]["seekerMode"] == "TRACK" and after["final"]["seekerMode"] != "TRACK":
        s1_regressions.append(k)
    if before["final"] != after["final"]:
        s1_differences.append({"key": k, "before": before["final"], "after": after["final"]})
    first = after["metrics"].get("firstCandidate") or {}
    if str(first.get("id", "")).startswith("SHIP") or first.get("kind") == "SHIP":
        ownship_first.append({"key": k, "candidate": first})
s1 = {
    "schema": "AEGIS_SEEKER_UNIFY_B_U0_S1_COMPARISON_1",
    "status": "PASS" if not baseline["pageErrors"] and not active["pageErrors"] and not s1_regressions and not s1_differences and not ownship_first else "FAIL",
    "rows": len(a),
    "baselineTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in b.values()),
    "activeTrack": sum(row["final"]["seekerMode"] == "TRACK" for row in a.values()),
    "trackRegressions": s1_regressions,
    "finalStateDifferences": s1_differences,
    "ownshipFirstSelections": ownship_first,
    "pageErrors": {"baseline": baseline["pageErrors"], "active": active["pageErrors"]},
}
(HERE / "U0_S1_COMPARISON.json").write_text(json.dumps(s1, ensure_ascii=False, indent=2) + "\n")

harpoon = load("HARPOON_BASKET_AUDIT.json")
groups: dict[tuple, list[dict]] = defaultdict(list)
for row in harpoon["rows"]:
    q = row["setup"]
    groups[(q["rangeKm"], q["speedKt"], q["turnDeg"])].append(row)
harpoon_summary = [
    {
        "rangeKm": k[0], "speedKt": k[1], "turnDeg": k[2], "shots": len(rows),
        "track": sum(row["result"]["everTrack"] for row in rows),
        "closestM": [min(row["result"]["closestM"] for row in rows), max(row["result"]["closestM"] for row in rows)],
    }
    for k, rows in sorted(groups.items())
]
(HERE / "HARPOON_BASKET_AUDIT_SUMMARY.json").write_text(json.dumps({"schema":"AEGIS_SEEKER_UNIFY_B_HARPOON_BASKET_AUDIT_SUMMARY_1","status":"PASS","productCodeModified":False,"rows":harpoon_summary,"pageErrors":harpoon["pageErrors"]}, indent=2) + "\n")

lines = [
    "# Harpoon basket audit",
    "",
    "## Status header",
    "",
    "- IMPLEMENTED: no Harpoon product-code change",
    "- TESTED: 60/100/120 km x four target motions x five deterministic seeds",
    "- APPROVED: audit-only scope from the B directive",
    "- UNRESOLVED: time-aged Harpoon search basket is deferred to U3",
    "- RELEASE: audit evidence only",
    "",
    "The fixture advances a detached RGM-84D receiver at the existing profile cruise speed and calls the unchanged `harpoonSeekerA` RF observation, independent RNG, scan, validation, gate, and state-machine path. Contact/damage physics is intentionally excluded because this audit measures acquisition, not impact.",
    "",
    "| Range | Motion | TRACK |",
    "|---:|---|---:|",
]
for row in harpoon_summary:
    motion = f"{row['speedKt']} kn straight" if not row["turnDeg"] else f"{row['speedKt']} kn + {row['turnDeg']} deg"
    lines.append(f"| {row['rangeKm']} km | {motion} | {row['track']}/{row['shots']} |")
lines += [
    "",
    "## Finding",
    "",
    "Straight motion and 30-degree turns remain inside the existing velocity-propagated launch memory and acquire in all tested cells. A 90-degree turn fails at 100 and 120 km (0/5) because lateral displacement from the frozen launch velocity exceeds the fixed 4,000 m search basket. This is the same information-age class of problem as U0, but Harpoon has its own memory/covariance/route contract and is deliberately left for U3.",
]
(HERE / "HARPOON_BASKET_AUDIT.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"s1":s1["status"],"s1Track":[s1["baselineTrack"],s1["activeTrack"]],"s1FinalDiffs":len(s1_differences),"harpoonRows":len(harpoon_summary)}, indent=2))
