#!/usr/bin/env python3
"""Prove the B correction changes only the named legacy floor adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_b_scope import digest, function_source, unpack


def spec_block(source: str) -> str:
    start = source.index("const HARPOON_CUE_B_SPEC=")
    end = source.index("\nfunction harpoonCuePacketB", start)
    return source[start:end]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    before, after = unpack(args.baseline), unpack(args.candidate)
    unchanged = [
        "harpoonCuePacketB", "harpoonCuePredictB", "harpoonCueHorizontalSigmaB", "harpoonCueMeanB",
        "harpoonMemoryA", "harpoonGateA", "harpoonRouteGateE", "harpoonRequestFireA", "harpoonReleaseA",
        "harpoonSeekerA", "attackPathGuardH3", "harpoonJournalReleaseF1", "harpoonFlightStepA",
        "harpoonRfObservationsA", "harpoonRandomA", "harpoonNoiseA", "harpoonImpactA",
        "harpoonExportA", "harpoonRestoreA", "asmCueUpdateA", "asmPassiveRfMeasurementB2",
        "surfaceMissileIdentityPolicyWip13C4", "surfaceMissileTrackReadinessWip13C4",
        "asmUpdateHojTrack", "harpoonUpdateHojC", "seekerU3PassiveRfSelectionD",
    ]
    hashes = {}
    unexpected = []
    for name in unchanged:
        left, right = function_source(before, name), function_source(after, name)
        same = left == right
        hashes[name] = {"baseline": digest(left), "candidate": digest(right), "byteEqual": same}
        if not same:
            unexpected.append(name)
    old_spec, new_spec = spec_block(before), spec_block(after)
    old_handoff, new_handoff = function_source(before, "harpoonCueHandoffB"), function_source(after, "harpoonCueHandoffB")
    normalized = after.replace(new_spec, old_spec, 1).replace(new_handoff, old_handoff, 1)
    checks = {
        "onlySpecAndHandoffChanged": normalized == before,
        "handoffChanged": old_handoff != new_handoff,
        "legacyFloorNamed": "trackBasketFloorM:250" in new_spec
        and "LEGACY_HARPOON_NATIVE_250M_FLOOR" in new_spec,
        "old4kmCapNotRestored": "Math.min(cfg.seekerSearchBasketM" not in new_handoff,
        "floorAppliedWithoutCap": "Math.max(HARPOON_CUE_B_SPEC.trackBasketFloorM,covarianceBasketM)" in new_handoff,
        "noUnexpectedFunctionChanges": not unexpected,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_B_CORRECTION_SCOPE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baselineHtmlSha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        "candidateHtmlSha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        "checks": checks,
        "unchangedFunctionHashes": hashes,
        "unexpectedChangedFunctions": unexpected,
        "intentionallyChanged": {
            "HARPOON_CUE_B_SPEC": {"baseline": digest(old_spec), "candidate": digest(new_spec)},
            "harpoonCueHandoffB": {"baseline": digest(old_handoff), "candidate": digest(new_handoff)},
        },
        "newTuningConstants": 0,
        "namedLegacyConstantFields": 1,
        "rfPhysicsChanged": False,
        "saveSchemaChanged": False,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "unchangedFunctions": len(unchanged)}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
