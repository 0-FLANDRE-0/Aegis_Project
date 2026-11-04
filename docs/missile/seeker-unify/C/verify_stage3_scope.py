#!/usr/bin/env python3
"""Static CUE_A truth/RNG audit and Stage-2→3 function-scope comparison."""
from __future__ import annotations

import argparse
import base64
import functools
import gzip
import hashlib
import json
import re
from pathlib import Path


def unpack(path: Path) -> str:
    raw = path.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode()


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def function_source_at(source: str, match: re.Match[str]) -> str:
    body = re.search(r"\)\s*\{", source[match.end():])
    if not body:
        raise ValueError("function body not found")
    brace = match.end() + body.end() - 1
    depth = 0
    string = None
    escape = False
    template_expr = 0
    i = brace
    while i < len(source):
        char = source[i]
        if string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == string and (string != "`" or template_expr == 0):
                string = None
            elif string == "`" and char == "$" and i + 1 < len(source) and source[i + 1] == "{":
                template_expr += 1
                depth += 1
                i += 1
            elif string == "`" and char == "}" and template_expr:
                template_expr -= 1
                depth -= 1
        elif char in "'\"`":
            string = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():i + 1]
        i += 1
    raise ValueError("unterminated function body")


@functools.lru_cache(maxsize=None)
def function_source(source: str, name: str) -> str:
    source = source.split(' const source="function missileThrustN', 1)[0]
    match = re.search(rf"(?:async\s+)?function\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise KeyError(name)
    try:
        return function_source_at(source, match)
    except ValueError:
        # Equality-only fallback for legacy bodies containing regex literals the
        # lightweight brace scanner cannot classify. The next declaration is a
        # stable lexical boundary in both compared products.
        next_match = re.search(r"\n\s*(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(", source[match.end():])
        end = len(source) if not next_match else match.end() + next_match.start()
        return source[match.start():end]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    before, after = unpack(args.baseline), unpack(args.candidate)
    expected_changed = {
        "asmTargetCueStateU0", "asmTargetCueU0", "asmTargetCuePassiveBearingUpdateU0", "asmCueBasketU0",
        "asmPassiveRfMeasurementB2", "asmApplyPassiveBearingB2", "asmTargetMemoryDriftB2",
        "spawnEnemyMissile", "updateEnemyMissileBaseC52", "exportOperationalState",
        "validateOperationalEnvelopeV48Wip11B", "prepareOperationalStateV48Wip11B",
        "applyPreparedOperationalStateV48Wip11B", "wip14b2BoundaryFixture",
    }
    expected_removed: set[str] = set()
    expected_added = {
        "setThreatAssumptionModeC", "asmCueFeatureEnabledA", "asmCueEnabledAssumptionsA",
        "asmCueSymmetrizeA", "asmCueInitialPacketA", "asmTargetCueStateA", "asmCueLimitVelocityA",
        "asmCueSyncAimA", "asmTargetCuePredictA", "asmCueScalarUpdateA", "asmCueUpdateA",
        "asmCueAngularUpdateA", "asmTargetCueSnapshotA", "asmPassiveEmitterGainA",
        "asmPassiveReceiverGainA", "asmCuePredictedAnglesA", "asmPassiveDirectRangeEstimateA",
        "cueAUpdateUiC", "cueAMountUiC",
    }
    protected = {
        "asmSeekerEchoMeasurement", "asmSeekerCompositeReturns", "arhRfTargetEvidenceWip13B12",
        "arhRfCandidateAcceptedWip13B12", "updateAsmSeeker", "buildEssmArhEchoPool",
        "_v1UpdateArhMeasurementCore", "_v1UpdateSarhMeasurementCore", "harpoonSeekerA",
        "ramRfMeasurement", "ramUpdateSeekerAuthority", "shipboardRadarEchoFieldWip13B13",
        "shipboardRadarDomainEvidenceWip13B13", "electronicPhysicalEmittersF", "missileNavB2Update",
        "computeGuidanceAccelV1", "computeKappaMidcourseAccelV2", "computeZEMCorrectionV1",
        "missileThrustN", "updateMissileBodyB3", "computeInterceptPk",
        "wip113RefreshBehavior", "wip112ApplySystemDamage",
    }
    changed = sorted(name for name in expected_changed if function_source(before, name) != function_source(after, name))
    unchanged_expected = sorted(expected_changed - set(changed))
    protected_changes = sorted(name for name in protected if function_source(before, name) != function_source(after, name))
    before_live = before.split(' const source="function missileThrustN', 1)[0]
    after_live = after.split(' const source="function missileThrustN', 1)[0]
    removed = sorted(name for name in expected_removed if re.search(rf"function\s+{re.escape(name)}\s*\(", before_live) and not re.search(rf"function\s+{re.escape(name)}\s*\(", after_live))
    missing_removed = sorted(expected_removed - set(removed))
    added = sorted(name for name in expected_added if not re.search(rf"function\s+{re.escape(name)}\s*\(", before_live) and re.search(rf"function\s+{re.escape(name)}\s*\(", after_live))
    missing_added = sorted(expected_added - set(added))
    special_protected = {}
    for name in ("applyInterceptResult", "gameFlightTerminationEvaluateV48"):
        baseline_span = function_source(before, name)
        candidate_match = re.search(rf"function\s+{re.escape(name)}\s*\(", after_live)
        assert candidate_match
        candidate_span = after_live[candidate_match.start():candidate_match.start() + len(baseline_span)]
        special_protected[name] = {
            "beforeSha256": sha(baseline_span), "afterSha256": sha(candidate_span),
            "byteEqual": baseline_span == candidate_span,
            "boundary": "baseline declaration through next live function declaration",
        }
    unexpected = {
        "unchangedExpected": unchanged_expected,
        "protectedChanged": protected_changes,
        "missingRemoved": missing_removed,
        "missingAdded": missing_added,
        "specialProtectedChanged": sorted(name for name, row in special_protected.items() if not row["byteEqual"]),
    }

    here = Path(__file__).resolve().parent
    core = (here / "cue_a_core.js").read_text()
    passive = (here / "cue_a_passive.js").read_text()
    diagnostic = (here / "cue_a_diagnostic.js").read_text()
    forbidden_consumer_tokens = [
        "profileId", "entityId", "targetPool", "_samB1TruthOwnState", "physicalShipsB",
        "SIM_RNG_STATE", "simRandom", "Math.random", "rand(",
    ]
    consumer_hits = [token for token in forbidden_consumer_tokens if token in core]
    rng_hits = [token for token in ("SIM_RNG_STATE", "simRandom", "Math.random", "rand(") if token in passive]
    payload_match = re.search(r"s\.sample=\{source:'PASSIVE_RF_CUE_A'.*?\};", passive, re.S)
    assert payload_match
    payload_source = payload_match.group(0)
    payload_forbidden = [token for token in ("owner", "entity", "profile", "point", "coordinates", "source.id") if token in payload_source]
    checks = {
        "declaredFunctionsChangedAndProtectedFunctionsStable": not any(unexpected.values()),
        "consumerHasNoTruthIdentityOrGameRng": not consumer_hits,
        "passiveMeasurementUsesNoGameRng": not rng_hits,
        "anonymousPayloadHasNoEmitterIdentityOrCoordinates": not payload_forbidden,
        "diagnosticTruthIsExplicitlyTagged": "AFTER_ACTION_TRUTH_TEST_ONLY" in diagnostic,
        "productionApiDeclaresNoTruthOutput": "truthOutput:false" in passive,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE3_SCOPE_TRUTH_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baselineSha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        "candidateSha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        "checks": checks,
        "changed": [{"name": name, "beforeSha256": sha(function_source(before, name)), "afterSha256": sha(function_source(after, name))} for name in changed],
        "protected": [{"name": name, "sha256": sha(function_source(before, name)), "byteEqual": name not in protected_changes} for name in sorted(protected)],
        "specialProtected": special_protected,
        "removed": removed,
        "added": added,
        "unexpected": unexpected,
        "consumerForbiddenHits": consumer_hits,
        "passiveRngHits": rng_hits,
        "payloadForbiddenHits": payload_forbidden,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
