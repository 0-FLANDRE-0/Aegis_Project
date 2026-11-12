#!/usr/bin/env python3
"""Compare exact protected functions and required defense boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from baseline_audit import (
    NEW_BOUNDARY_DEFINITION_COUNTS,
    NEW_BOUNDARY_FUNCTIONS,
    PROTECTED_FUNCTIONS,
)


HP_SAVE_BOUNDARIES = [
    "shipOutcomeFromInputsA", "shipOutcomeA", "shipOutcomeWriteDisplayA",
    "shipOutcomeRestoreCompatibilityA", "exportOperationalState",
    "importOperationalState",
]
INTENTIONAL_CHANGED = ["wip118BuildEngagementControl"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    candidate = json.loads(args.candidate.read_text())
    before, after = baseline["functions"], candidate["functions"]
    before_definitions, after_definitions = baseline["definitionHashes"], candidate["definitionHashes"]
    exact = [name for name in PROTECTED_FUNCTIONS if before_definitions.get(name) == after_definitions.get(name)]
    changed = [name for name in PROTECTED_FUNCTIONS if before_definitions.get(name) != after_definitions.get(name)]
    candidate_contract = candidate.get("contract", {})
    definition_counts = candidate_contract.get("definitionCounts", {})
    checks = {
        "protectedBaselineCount31": len(PROTECTED_FUNCTIONS) == 31 and all(name in before for name in PROTECTED_FUNCTIONS),
        "protectedCandidateCount31": len(PROTECTED_FUNCTIONS) == 31 and all(name in after for name in PROTECTED_FUNCTIONS),
        "protectedExact30": len(exact) == 30,
        "onlyApprovedAdapterChanged": changed == INTENTIONAL_CHANGED,
        "hpSaveBoundariesExact6": all(before.get(name) == after.get(name) for name in HP_SAVE_BOUNDARIES),
        "newBoundaryCount11": len(NEW_BOUNDARY_FUNCTIONS) == 11,
        "newBoundaryRequired": candidate_contract.get("newBoundaryRequired") is True,
        "newBoundaryDefinitionCountsExact": all(definition_counts.get(name) == NEW_BOUNDARY_DEFINITION_COUNTS[name] for name in NEW_BOUNDARY_FUNCTIONS),
        "ownerLocalLexicalCopiesExact": all(len({row["sha256"] for row in after_definitions.get(name, [])}) == 1 for name, count in NEW_BOUNDARY_DEFINITION_COUNTS.items() if count == 2),
        "newBoundaryHashed": all(name in after for name in NEW_BOUNDARY_FUNCTIONS),
        "baselineHasNoNewBoundary": all(name not in before for name in NEW_BOUNDARY_FUNCTIONS),
    }
    failed = [name for name, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_INTEGRATION_BASELINE_FUNCTION_HASH_GATE_A_2",
        "checks": checks,
        "protectedCount": len(PROTECTED_FUNCTIONS),
        "protectedExact": exact,
        "intentionalChanged": changed,
        "hpSaveBoundaries": HP_SAVE_BOUNDARIES,
        "newBoundaryFunctions": NEW_BOUNDARY_FUNCTIONS,
        "failed": failed,
        "status": "PASS" if not failed else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": payload["status"], "protected": len(PROTECTED_FUNCTIONS), "exact": len(exact), "changed": changed, "new": len(NEW_BOUNDARY_FUNCTIONS)}))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
