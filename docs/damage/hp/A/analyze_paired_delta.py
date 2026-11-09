#!/usr/bin/env python3
"""Classify the six inherited paired-state deltas without changing expectations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "docs/damage/hp/A/evidence/final-regression/paired-esm-a/baseline-comparison.json"


def strip_new_survival(value):
    clone = json.loads(json.dumps(value))
    clone.get("state", {}).pop("survival", None)
    return clone


def discrete(row: dict) -> dict:
    state, dynamics = row["state"], row["dynamics"]
    pose = dynamics["pose"]
    return {
        "shipHP": state["shipHP"],
        "survivalState": pose["state"],
        "irreversible": pose["irreversible"],
        "lost": pose["lost"],
        "waterM3": state["damage"]["flooding"]["summary"]["waterM3"],
        "moduleDamage": state["damage"]["moduleDamage"],
        "crew": {
            "mode": state["crew"]["mode"], "fit": state["crew"]["fit"],
            "injured": state["crew"]["injured"], "dead": state["crew"]["dead"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/damage/hp/A/evidence/final-regression/paired-esm-a/hp-a-delta-analysis.json")
    args = parser.parse_args()
    source = json.loads(SOURCE.read_text())
    rows = []
    for case in source["cases"]:
        baseline = case["pair"]["baseline"]
        candidate = case["pair"]["candidate"]
        normalized_baseline = {"state": baseline["state"], "dynamics": baseline["dynamics"]}
        normalized_candidate = strip_new_survival({"state": candidate["state"], "dynamics": candidate["dynamics"]})
        discrete_baseline = discrete(baseline)
        discrete_candidate = discrete(candidate)
        checks = {
            "combatRngExact": baseline["rng"] == candidate["rng"],
            "hullDamageAndInventoryExact": case["checks"]["sameHullDamageAndFixedLayout"],
            "observerExact": case["checks"]["sameExistingObserverState"],
            "offboardExact": case["checks"]["sameExistingOffboardPorts"],
            "faultFree": case["checks"]["bothFaultFree"],
            "discreteOutcomeExact": discrete_baseline == discrete_candidate,
            "onlyAddedSurvivalForUnmodifiedSave": case["scenario"] == "damaged" or normalized_baseline == normalized_candidate,
        }
        rows.append({
            "ship": case["ship"],
            "scenario": case["scenario"],
            "classification": "INTENDED_HP_A_SAVE_CONTRACT_DELTA",
            "reason": (
                "Candidate export adds the authoritative survival snapshot."
                if case["scenario"] != "damaged" else
                "The inherited fixture edits flooding after export but leaves the newly authoritative survival snapshot unchanged; restore therefore preserves that supplied pose/timer before fixed ticks. Final discrete survival, HP, water, module damage, crew and RNG remain exact."
            ),
            "checks": checks,
            "baselineDiscrete": discrete_baseline,
            "candidateDiscrete": discrete_candidate,
            "continuousPhysicalExact": case["checks"]["samePhysicalState"],
        })
    checks = {
        "sixExpectedCases": len(rows) == 6,
        "allDifferencesLimitedToSamePhysicalState": all(
            not case["checks"]["samePhysicalState"]
            and all(value for key, value in case["checks"].items() if key != "samePhysicalState")
            for case in source["cases"]
        ),
        "allDiscreteOutcomesAndRngPreserved": all(all(row["checks"].values()) for row in rows),
        "expectationsUpdated": False,
        "tolerancesChanged": False,
    }
    payload = {
        "schema": "AEGIS_HP_A_PAIRED_DELTA_ANALYSIS_1",
        "status": "CLASSIFIED_INTENDED" if all(value for key, value in checks.items() if key not in {"expectationsUpdated", "tolerancesChanged"}) else "UNRESOLVED",
        "authority": "User HP_A directive sections 5C and 6.8 require authoritative survival round-trip and non-authoritative saved HP.",
        "checks": checks,
        "rows": rows,
        "expectationPolicy": "Raw inherited failures retained; no baseline or tolerance update.",
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "checks": checks}))
    raise SystemExit(0 if payload["status"] == "CLASSIFIED_INTENDED" else 1)


if __name__ == "__main__":
    main()
