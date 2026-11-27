#!/usr/bin/env python3
"""DEFENSE_OODA_A D-stage exact function/boundary hash gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sys import path as sys_path

HERE = Path(__file__).resolve().parent
BASELINE_TOOLS = HERE.parents[1] / "integration-baseline" / "A"
sys_path.insert(0, str(BASELINE_TOOLS))
from baseline_audit import (  # noqa: E402
    NEW_BOUNDARY_DEFINITION_COUNTS,
    NEW_BOUNDARY_FUNCTIONS,
    PROTECTED_FUNCTIONS,
)


HP_APPROVED_CHANGES = {"wip118BuildEngagementControl", "exportOperationalState"}
INTEGRATION_PROTECTED_CHANGES = {"exportOperationalState"}
INTEGRATION_BOUNDARY_CHANGES = {
    "defenseDecisionLegacyCommandA1",
    "defenseDecisionLegacyBeginA1",
    "defenseDecisionLegacySalvoA1",
    "defenseDecisionRecommendationOrderA1",
    "defenseDecisionLegacyFinishA1",
    "defenseDecisionValidateCommandA1",
}


def changed(before: dict, after: dict, names: list[str]) -> set[str]:
    return {name for name in names if before.get(name) != after.get(name)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("hp", type=Path)
    parser.add_argument("integration", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    hp = json.loads(args.hp.read_text())
    integration = json.loads(args.integration.read_text())
    candidate = json.loads(args.candidate.read_text())
    hpd, based, cand = hp["definitionHashes"], integration["definitionHashes"], candidate["definitionHashes"]
    hp_changed = changed(hpd, cand, PROTECTED_FUNCTIONS)
    protected_changed = changed(based, cand, PROTECTED_FUNCTIONS)
    boundary_changed = changed(based, cand, NEW_BOUNDARY_FUNCTIONS)
    counts = candidate["contract"]["definitionCounts"]
    checks = {
        "protectedCount31": len(PROTECTED_FUNCTIONS) == 31,
        "hpApprovedChangesOnly": hp_changed == HP_APPROVED_CHANGES,
        "integrationProtectedExact30": len(PROTECTED_FUNCTIONS) - len(protected_changed) == 30,
        "integrationProtectedChangesOnlySaveExport": protected_changed == INTEGRATION_PROTECTED_CHANGES,
        "activeBoundaryChangesExact": boundary_changed == INTEGRATION_BOUNDARY_CHANGES,
        "boundaryDefinitionCountsExact": all(counts.get(name) == NEW_BOUNDARY_DEFINITION_COUNTS[name] for name in NEW_BOUNDARY_FUNCTIONS),
        "ownerLocalCopiesExact": all(len({row["sha256"] for row in cand.get(name, [])}) == 1 for name, n in NEW_BOUNDARY_DEFINITION_COUNTS.items() if n == 2),
    }
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_D_FUNCTION_HASH_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "protected": {
            "count": len(PROTECTED_FUNCTIONS),
            "hpToDChanged": sorted(hp_changed),
            "integrationToDChanged": sorted(protected_changed),
            "integrationToDExact": sorted(set(PROTECTED_FUNCTIONS) - protected_changed),
        },
        "boundaries": {
            "count": len(NEW_BOUNDARY_FUNCTIONS),
            "integrationToDChanged": sorted(boundary_changed),
            "integrationToDExact": sorted(set(NEW_BOUNDARY_FUNCTIONS) - boundary_changed),
            "definitionCounts": {name: counts.get(name) for name in NEW_BOUNDARY_FUNCTIONS},
        },
        "intentionalChangeReasons": {
            "wip118BuildEngagementControl": "INTEGRATION_BASELINE_A immutable provider port; unchanged from the integration baseline",
            "exportOperationalState": "optional owner-local defenseOodaA save field for active and foreign ships",
            "activeBoundarySet": "four frozen H1 upper judgment consumers plus provider validation; downstream execution remains exact",
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": payload["status"], "checks": checks, "protectedChanged": sorted(protected_changed), "boundaryChanged": sorted(boundary_changed)}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
