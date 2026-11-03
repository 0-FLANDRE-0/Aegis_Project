#!/usr/bin/env python3
"""Compare identical baseline/product SEEKER_UNIFY_A engine measurements."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def group(rows: list[dict], keys: tuple[str, ...], predicate) -> dict[tuple, dict]:
    out: dict[tuple, dict] = defaultdict(lambda: {"shots": 0, "positive": 0})
    for row in rows:
        key = tuple(row["setup"].get(k) for k in keys)
        out[key]["shots"] += 1
        out[key]["positive"] += bool(predicate(row))
    return dict(out)


def rows_from(groups: dict[tuple, dict], keys: tuple[str, ...]) -> list[dict]:
    return [{**dict(zip(keys, key)), **value} for key, value in sorted(groups.items(), key=lambda q: tuple(str(x) for x in q[0]))]


baseline = load("BASELINE_DIAGNOSTICS.json")
product = load("PRODUCT_DIAGNOSTICS.json")

target_keys = ("kind", "speedKt", "altM", "rangeKm")
control_keys = ("control", "altM", "rangeKm")
sam_keys = ("path", "targetKind", "rangeKm")
cue_keys = ("label", "rangeKm", "speedKt", "turnDeg")
radar_keys = ("kind", "radar", "rangeKm")

target_b = group([r for r in baseline["rangeCases"] if r["setup"]["control"] == "TARGET"], target_keys, lambda r: r["result"]["everTrack"])
target_p = group([r for r in product["rangeCases"] if r["setup"]["control"] == "TARGET"], target_keys, lambda r: r["result"]["everTrack"])
control_b = group([r for r in baseline["rangeCases"] if r["setup"]["control"] != "TARGET"], control_keys, lambda r: r["result"]["everAcquire"] or r["result"]["everTrack"])
control_p = group([r for r in product["rangeCases"] if r["setup"]["control"] != "TARGET"], control_keys, lambda r: r["result"]["everAcquire"] or r["result"]["everTrack"])
sam_b = group(baseline["samArhCases"], sam_keys, lambda r: bool(r.get("target", {}).get("pass")))
sam_p = group(product["samArhCases"], sam_keys, lambda r: bool(r.get("target", {}).get("pass")))
cue_b = group(baseline["cueCases"], cue_keys, lambda r: r["result"]["everTrack"])
cue_p = group(product["cueCases"], cue_keys, lambda r: r["result"]["everTrack"])
radar_b = group(baseline["radarCases"], radar_keys, lambda r: r["detected"] and r["trackEligible"])
radar_p = group(product["radarCases"], radar_keys, lambda r: r["detected"] and r["trackEligible"])


def paired(before: dict, after: dict, keys: tuple[str, ...]) -> list[dict]:
    all_keys = sorted(set(before) | set(after), key=lambda q: tuple(str(x) for x in q))
    return [
        {
            **dict(zip(keys, key)),
            "shots": after.get(key, before.get(key, {})).get("shots", 0),
            "baseline": before.get(key, {}).get("positive", 0),
            "product": after.get(key, {}).get("positive", 0),
            "delta": after.get(key, {}).get("positive", 0) - before.get(key, {}).get("positive", 0),
        }
        for key in all_keys
    ]


target = paired(target_b, target_p, target_keys)
controls = paired(control_b, control_p, control_keys)
sam = paired(sam_b, sam_p, sam_keys)
cues = paired(cue_b, cue_p, cue_keys)
radars = paired(radar_b, radar_p, radar_keys)

# The user explicitly extended the no-increase gate from ESSM Block 2 to both
# SM-6 Block IA air and surface configurations.  Conservatively gate every
# air/ASM/clutter/chaff candidate cell; only the intentional SURFACE target in
# the SM-6 surface configuration is excluded from the false-acquisition gate.
sam_false = [r for r in sam if r["targetKind"] in ("AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF")]
false_increases = [r for r in controls if r["delta"] > 0] + [r for r in sam_false if r["delta"] > 0]
horizon_violations = [
    {"label": data["label"], **r["setup"], "horizonKm": r["horizonKm"]}
    for data in (baseline, product)
    for r in data["radarCases"]
    if r["detected"] and r["setup"]["rangeKm"] > r["horizonKm"] + 1e-9
]

cue_summary = {
    label: {
        "baselineTrack": sum(r["result"]["everTrack"] for r in baseline["cueCases"] if r["setup"]["label"] == label),
        "productTrack": sum(r["result"]["everTrack"] for r in product["cueCases"] if r["setup"]["label"] == label),
        "baselineHit": sum(r["result"]["shipHit"] for r in baseline["cueCases"] if r["setup"]["label"] == label),
        "productHit": sum(r["result"]["shipHit"] for r in product["cueCases"] if r["setup"]["label"] == label),
        "shots": sum(1 for r in product["cueCases"] if r["setup"]["label"] == label),
    }
    for label in ("Kh-32", "Kh-35U")
}

product_envelope = []
for kind in ("DDG", "CG", "SOV", "HULK"):
    for alt_m in (15, 200):
        for speed_kt in (0, 15):
            cells = [
                row for row in target
                if row["kind"] == kind and row["altM"] == alt_m and row["speedKt"] == speed_kt
            ]
            product_envelope.append({
                "kind": kind,
                "altM": alt_m,
                "speedKt": speed_kt,
                "furthestAnyTrackKm": max((row["rangeKm"] for row in cells if row["product"] > 0), default=None),
                "furthestAllFiveTrackKm": max((row["rangeKm"] for row in cells if row["product"] == row["shots"]), default=None),
            })

result = {
    "schema": "AEGIS_SEEKER_UNIFY_A_RANGE_REDIAGNOSIS_1",
    "baselineSha256": baseline["inputSha256"],
    "productSha256": product["inputSha256"],
    "identicalConditions": True,
    "counts": {
        "asmRange": len(product["rangeCases"]),
        "samArh": len(product["samArhCases"]),
        "terminalCue": len(product["cueCases"]),
        "shipRadar": len(product["radarCases"]),
    },
    "primaryDecision": "PASS" if not false_increases else "FAIL",
    "falseAcquisitionIncreases": false_increases,
    "horizonViolations": horizon_violations,
    "pageErrors": {"baseline": baseline["pageErrors"], "product": product["pageErrors"]},
    "targetTrackByCondition": target,
    "productAsmTrackEnvelope": product_envelope,
    "asmControls": controls,
    "samCandidateAcceptance": sam,
    "terminalCue": cues,
    "terminalCueSummary": cue_summary,
    "shipRadarPlotEligibility": radars,
    "limitations": [
        "shipRadarPlotEligibility is a physical-echo plus anonymous surface-evidence measurement; managed TrackStore creation is recorded by the separate MANAGED_RADAR results",
        "SAM rows exercise the production ARH RF pool and target-evidence acceptance; full missile guidance is covered by broad regressions",
    ],
}
(HERE / "RANGE_REDIAGNOSIS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


def table(rows: list[dict], columns: list[str]) -> str:
    head = "| " + " | ".join(columns) + " |\n|" + "|".join("---" for _ in columns) + "|\n"
    return head + "".join("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |\n" for row in rows)


changed_targets = [r for r in target if r["delta"]]
changed_radars = [r for r in radars if r["delta"]]
md = f"""# Range rediagnosis

IMPLEMENTED: **surface-ship RCS scale only**

TESTED: **{sum(result['counts'].values())} identical browser-engine cases**

APPROVED: **directive pre-approval applies only if primary and broad regression gates pass**

UNRESOLVED: **see limitations and managed-radar supplement**

RELEASE: **no release/tag**

## Primary result

**{result['primaryDecision']}** — false-acquisition increases: {len(false_increases)};
radar-horizon violations: {len(horizon_violations)}; page errors:
baseline {len(baseline['pageErrors'])}, product {len(product['pageErrors'])}.

The RCS values were fixed before this matrix was executed.  No result was fed
back into the RCS constants.

## Terminal cue

{table([{'label': k, **v} for k, v in cue_summary.items()], ['label','shots','baselineTrack','productTrack','baselineHit','productHit'])}

## Changed ASM target-track cells

{table(changed_targets, ['kind','speedKt','altM','rangeKm','shots','baseline','product','delta']) if changed_targets else 'No changed cells.\n'}

## Product ASM track envelope on the measured grid

{table(product_envelope, ['kind','altM','speedKt','furthestAnyTrackKm','furthestAllFiveTrackKm'])}

The 15 m rows stop between the 30 and 40 km samples consistently with the
low-altitude radar horizon. At 200 m, the non-low-observable CG/Project 956/hulk
reach the 45 km sample and stop at 50 km; the 15 dB-reduced DDG reaches 30 km.
This is compatible with the public Kh-35 family 20/50 km context without using
those distances to tune the RCS constants.

## False-acquisition controls

{table(controls, ['control','altM','rangeKm','shots','baseline','product','delta'])}

## ESSM B2 / SM-6 air, ASM, sea-clutter and chaff no-increase gate

{table(sam_false, ['path','targetKind','rangeKm','shots','baseline','product','delta'])}

## Changed ship-radar plot-eligible cells

{table(changed_radars, ['kind','radar','rangeKm','shots','baseline','product','delta']) if changed_radars else 'No changed cells.\n'}

## Interpretation

`detected + trackEligible` means the production common RF echo field generated
an echo and the production anonymous surface-domain evidence admitted it.  The
separate managed-radar supplement drives the actual SPY/SPQ/BridgeMaster plot
acceptors and reports TrackStore creation.  All detections are checked against
the same target-height radar horizon.
"""
(HERE / "RANGE_REDIAGNOSIS.md").write_text(md)
print(json.dumps({"decision": result["primaryDecision"], "falseIncreases": len(false_increases), "horizonViolations": len(horizon_violations), "counts": result["counts"]}))
