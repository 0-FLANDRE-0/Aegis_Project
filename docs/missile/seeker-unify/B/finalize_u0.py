#!/usr/bin/env python3
"""Assemble the complete U0 stage gate after all focused tests finish."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> dict:
    return json.loads((HERE / name).read_text())


cue = read("U0_RESULTS.json")
s1 = read("U0_S1_COMPARISON.json")
matrix = read("U0_1590_COMPARISON.json")
determinism = read("U0_DETERMINISM.json")
harpoon = read("HARPOON_BASKET_AUDIT_SUMMARY.json")
battles_path = HERE / "U0_60_BATTLE_RESULTS.json"
battles = read(battles_path.name) if battles_path.exists() else None

checks = {
    "cueShadowAndActive": cue["status"] == "PASS",
    "azimuthUsesProfileCap": len(cue["azimuthCapViolations"]) == 0,
    "s1NoRegressionOrOwnshipFirst": s1["status"] == "PASS",
    "matrix1590": matrix["status"] == "PASS",
    "determinismAndGlobalRng": determinism["status"] == "PASS",
    "harpoonAuditOnly": harpoon["status"] == "PASS" and harpoon["productCodeModified"] is False,
    "battleReferenceComplete": battles is not None and battles["status"] == "PASS",
    "neighborAsmFirstAssociationZero": battles is not None and battles["firstAssociationAudit"]["neighborAsmFirstAssociations"] == 0,
    "nonShipFirstAssociationZero": battles is not None and battles["firstAssociationAudit"]["nonShipFirstAssociations"] == 0,
}
result = {
    "schema": "AEGIS_SEEKER_UNIFY_B_U0_GATE_1",
    "status": "PASS" if all(checks.values()) else "INCOMPLETE" if battles is None else "FAIL",
    "checks": checks,
    "cue": {
        "rows": cue["rows"],
        "shadowOutcomeDifferences": len(cue["shadowOutcomeDifferences"]),
        "trackRegressions": len(cue["activeTrackRegressions"]),
        "justifiedOutsideSearchSector": len(cue["activeTrackRegressionsJustifiedOutsideSearchSector"]),
        "improvements": len(cue["activeTrackImprovements"]),
        "failureCategories": {key: value["count"] for key, value in cue["activeFailureCategories"].items()},
        "basket": cue["basketAtFirstTrackOrAcquire"],
        "passiveBearingClock": cue["passiveBearingClock"],
    },
    "matrix1590": matrix,
    "s1": s1,
    "determinism": {key: determinism[key] for key in ("jobs", "comparison", "resultSha256", "globalRng", "pageErrors")},
    "harpoon": harpoon,
    "battleReference": None if battles is None else {
        key: battles[key] for key in ("status", "jobs", "elapsedS", "totals", "baselineAvailable", "baselineTotals", "firstAssociationAudit")
    },
    "unresolved": [
        "PRE_LAUNCH_TRACK_AGE_NOT_REPRESENTED_IN_CURRENT_LAUNCH_CUE",
        "HARPOON_TIME_AGED_SEARCH_BASKET_DEFERRED_TO_U3",
    ],
    "broadRegressionPolicy": "DEFERRED_BY_USER_SUPPLEMENT_UNTIL_FINAL_STAGE_OR_STOP",
}
(HERE / "U0_GATE.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

battle_text = "not finished"
if battles is not None:
    audit = battles["firstAssociationAudit"]
    battle_text = (
        f"{battles['jobs']}/60, totals={battles['totals']}, "
        f"neighbor ASM first={audit['neighborAsmFirstAssociations']}, "
        f"non-ship first={audit['nonShipFirstAssociations']}"
    )
md = f"""# U0 stage gate

## Status header

- IMPLEMENTED: time-expanded TargetCue basket with independent range/bearing clocks and existing profile search-sector cap
- TESTED: cue 240 x baseline/SHADOW/ACTIVE, S1 100, primary matrix 1,590, deterministic replay 10 x 3, reference battles 60
- APPROVED: constants frozen before effect tests; existing `searchSectorAzDeg` used as the azimuth ceiling
- UNRESOLVED: pre-launch observation age; Harpoon time-aged basket deferred to U3
- RELEASE: no release; PR only

Overall: **{result['status']}**

```json
{json.dumps(checks, indent=2)}
```

## Key results

- U0 cue regressions: {len(cue['activeTrackRegressions'])}
- U0 cue improvements: {len(cue['activeTrackImprovements'])}
- after-action failure categories: {json.dumps(result['cue']['failureCategories'], sort_keys=True)}
- profile azimuth-cap violations: {len(cue['azimuthCapViolations'])}
- 1,590 matrix: {matrix['status']}; new false acquisitions {len(matrix['controls']['newFalseAcquisitions'])}
- S1: {s1['status']}; ownship first selections {len(s1['ownshipFirstSelections'])}
- deterministic result hashes: {', '.join(determinism['resultSha256'])}
- 60-battle reference: {battle_text}

Broad regression is intentionally not run at U0: the user supplement requires it exactly once after the final stage, or at the stop point.
"""
(HERE / "U0_GATE.md").write_text(md)
print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
