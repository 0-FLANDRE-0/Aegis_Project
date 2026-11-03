#!/usr/bin/env python3
"""Compare the U0 product's 1,590 diagnostic rows to SEEKER_UNIFY_A."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "A" / "PRODUCT_DIAGNOSTICS.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def map_rows(rows: list[dict]) -> dict[str, dict]:
    return {json.dumps(row["setup"], sort_keys=True, separators=(",", ":")): row for row in rows}


baseline = load(BASE)
active = load(HERE / "U0_1590_ACTIVE.json")
sections = ("rangeCases", "samArhCases", "cueCases", "radarCases")
paired = {}
for section in sections:
    b = map_rows(baseline[section])
    a = map_rows(active[section])
    assert b.keys() == a.keys(), section
    paired[section] = [(b[k], a[k]) for k in sorted(b)]

controls = [(b, a) for b, a in paired["rangeCases"] if b["setup"]["control"] != "TARGET"]
control_false_before = sum(bool(row[0]["result"]["everTrack"]) for row in controls)
control_false_after = sum(bool(row[1]["result"]["everTrack"]) for row in controls)
control_new_false = [a["setup"] for b, a in controls if not b["result"]["everTrack"] and a["result"]["everTrack"]]
target_track_regressions = [a["setup"] for b, a in paired["rangeCases"] if b["setup"]["control"] == "TARGET" and b["result"]["everTrack"] and not a["result"]["everTrack"]]
cue_track_regressions = [a["setup"] for b, a in paired["cueCases"] if b["result"]["everTrack"] and not a["result"]["everTrack"]]

def exact_differences(section: str, ignored: set[str] | None = None) -> list[dict]:
    ignored = ignored or set()
    rows = []
    for before, after in paired[section]:
        fields = sorted((before.keys() | after.keys()) - {"setup"} - ignored)
        diff = {field: [before.get(field), after.get(field)] for field in fields if before.get(field) != after.get(field)}
        if diff:
            rows.append({"setup": after["setup"], "differences": diff})
    return rows

sam_diffs = exact_differences("samArhCases")
radar_diffs = exact_differences("radarCases")
result = {
    "schema": "AEGIS_SEEKER_UNIFY_B_U0_1590_COMPARISON_1",
    "status": "PASS" if not active["pageErrors"] and not control_new_false and not target_track_regressions and not cue_track_regressions and not sam_diffs and not radar_diffs else "FAIL",
    "counts": {section: len(active[section]) for section in sections},
    "pageErrors": active["pageErrors"],
    "controls": {"rows": len(controls), "baselineTrack": control_false_before, "activeTrack": control_false_after, "newFalseAcquisitions": control_new_false},
    "targetTrackRegressions": target_track_regressions,
    "cueTrackRegressions": cue_track_regressions,
    "samExactDifferences": sam_diffs,
    "radarExactDifferences": radar_diffs,
}
(HERE / "U0_1590_COMPARISON.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status":result["status"],"counts":result["counts"],"controls":result["controls"],"targetTrackRegressions":len(target_track_regressions),"cueTrackRegressions":len(cue_track_regressions),"samDiffs":len(sam_diffs),"radarDiffs":len(radar_diffs)}, indent=2))
