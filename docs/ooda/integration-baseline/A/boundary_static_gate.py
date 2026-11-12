#!/usr/bin/env python3
"""Static call-direction and authority audit for the corrected defense port."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from baseline_audit import (
    NEW_BOUNDARY_FUNCTIONS,
    definition_positions,
    function_source,
    packed_main,
)


RNG_CALL = re.compile(r"\b(?:simRandom|randn|Math\.random)\s*\(")
EXECUTION_CALL = re.compile(
    r"\b(?:consumeVlsCell|vlsReleaseStandardB1|vlsReleaseEssmB1|"
    r"stepOwnerPhalanxD|applyPhalanxProjectileHit|wip119FireOne|"
    r"launchHarpoon|fireMainGun)\s*\("
)
SAVE_CALL = re.compile(r"\b(?:exportOperationalState|importOperationalState)\s*\(")
TRUTH_TOKEN = re.compile(
    r"\b(?:truthObject|truthRef|truthId|actualEnemy|actualTarget|"
    r"hostileTruth|faction)\b",
    re.IGNORECASE,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = packed_main(args.product.read_bytes()).decode("utf-8")
    positions = definition_positions(source, NEW_BOUNDARY_FUNCTIONS)
    bodies = {
        name: [function_source(source, name, start) for start in starts]
        for name, starts in positions.items()
    }
    tactical = [function_source(source, "wip118BuildEngagementControl", start) for start in definition_positions(source, ["wip118BuildEngagementControl"])["wip118BuildEngagementControl"]]
    salvo_wrappers = [function_source(source, "wip118SalvoPolicy", start) for start in definition_positions(source, ["wip118SalvoPolicy"])["wip118SalvoPolicy"]]
    decision_sources = "\n".join(body for rows in bodies.values() for body in rows)
    truth_sources = "\n".join(
        body for name, rows in bodies.items()
        if name != "defenseDecisionForbiddenPathA1" for body in rows
    )
    crew_sources = "\n".join(bodies["defenseDecisionCrewInputA1"])
    checks = {
        "inputCallsCrewSummaryPerOwner": all(body.count("defenseDecisionCrewInputA1(r)") == 1 for body in bodies["defenseDecisionInputSnapshotA1"]),
        "inputCallsTrackProjectionPerOwner": all(body.count("defenseDecisionTrackInputA1(") == 1 for body in bodies["defenseDecisionInputSnapshotA1"]),
        "legacyBeginCallsInputAndProvider": all("defenseDecisionInputSnapshotA1()" in body and "defenseDecisionLegacyCommandA1(input,rows)" in body for body in bodies["defenseDecisionLegacyBeginA1"]),
        "wip118CallsBeginAndFinishPerOwner": all(body.count("defenseDecisionLegacyBeginA1(") == 1 and body.count("defenseDecisionLegacyFinishA1(") == 1 for body in tactical),
        "legacySalvoAdvisoryOnly": all("defenseDecisionLegacySalvoA1" in body and "wip118SalvoPolicyNativeH1" in body for body in salvo_wrappers),
        "forbiddenAuditConnected": source.count("defenseDecisionForbiddenPathA1(input)") >= 3,
        "freezeAuditConnected": source.count("defenseDecisionFrozenA1(") >= 3,
        "crewProjectionLimited": not re.search(r"\b(?:groups|roster|locations|spaceId|casualtyLog|damageEvents)\b", crew_sources),
        "truthAccessZero": not TRUTH_TOKEN.search(truth_sources),
        "rngCallsZero": not RNG_CALL.search(decision_sources),
        "directExecutionCallsZero": not EXECUTION_CALL.search(decision_sources),
        "saveCallsZero": not SAVE_CALL.search(decision_sources),
    }
    failed = [name for name, value in checks.items() if not value]
    payload = {
        "schema": "AEGIS_INTEGRATION_BASELINE_BOUNDARY_STATIC_A_2",
        "product": args.product.name,
        "checks": checks,
        "definitionCounts": {name: len(rows) for name, rows in bodies.items()},
        "findings": {
            "truthAccess": [], "rngCalls": [], "directExecutionCalls": [],
            "saveCalls": [], "excessCrewFields": [],
        },
        "status": "PASS" if not failed else "FAIL",
        "failed": failed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "failed": failed}))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
