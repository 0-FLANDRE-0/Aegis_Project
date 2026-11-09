#!/usr/bin/env python3
"""Freeze the HP_A seeker/decoy baseline for SEEKER_CLOSE_A.

This is a read-only source audit.  It does not build or mutate a game product.
The historical TRACK-B/TRACK-C numbers are retained only as provenance; they
are deliberately not used as a current-product acceptance threshold.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HP_A_BYTES = 22_200_135
HP_A_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"
BASE_MAIN = "78b01165bad64e9c6dc384ff070a70f868da5113"
HP_A_PR_HEAD = "a3e45f7cfb5cecc1f7180e24ee3fbf35197458f5"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def unpack_main(raw: bytes) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match.group(1))).decode("utf-8")


def brace_end(source: str, brace: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = line_comment = block_comment = False
    index = brace
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char in "\r\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise AssertionError("unterminated function")


def function_spans(source: str, name: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    pattern = re.compile(rf"^[ \t]*function\s+{re.escape(name)}\s*\(", re.MULTILINE)
    for match in pattern.finditer(source):
        paren = source.find("(", match.start(), match.end())
        depth = 0
        quote: str | None = None
        escaped = False
        close = -1
        for index in range(paren, len(source)):
            char = source[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                continue
            if char in "'\"`":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    close = index
                    break
        brace = source.find("{", close + 1)
        if brace < 0:
            raise AssertionError(f"function brace missing: {name}")
        spans.append((match.start(), brace_end(source, brace)))
    return spans


FUNCTIONS = {
    "common_association_state": [
        "seekerU4SelectIndexC", "seekerU4StateSnapshotC",
        "seekerU4RecordTransitionC", "seekerU4RunPolicyC",
    ],
    "asm_sensor_and_guidance": [
        "createAsmSeekerState", "asmSeekerWorldRfReturnsWip13A",
        "asmSeekerVisibleRfReturns", "asmSeekerCompositeReturns",
        "asmSeekerEchoMeasurement", "asmSeekerAssociationGates",
        "asmSeekerAssociateMeasurements", "asmSeekerMeasurement",
        "updateAsmSeeker", "asmPassedTarget3D", "updateEnemyMissileBaseC52",
    ],
    "harpoon": [
        "harpoonMemoryA", "harpoonPredictionA", "harpoonRfObservationsA",
        "harpoonSeekerA", "harpoonFinishA", "harpoonImpactA",
    ],
    "soft_kill_and_decoys": [
        "nulkaFire15B", "nulkaFlight15B", "nulkaRfReturns15B",
        "deployOwnChaffForThreat", "getOwnChaffRadarReturns",
        "updateSoftKillThreatManager", "softKillDoctrineAuditSnapshot",
    ],
}


TERMINAL_CATEGORIES = [
    "DEFENSE_INTERCEPT", "CIWS_KILL", "DECOY_SEDUCTION", "TARGET_HIT",
    "KINEMATIC_MISS", "SEA_IMPACT", "GUIDANCE_CONTROL_LOSS",
    "SEEKER_NO_VALID_MEASUREMENT", "SEEKER_ASSOCIATION_DROP",
    "SEEKER_GATE_REJECT", "SEEKER_SEARCH_ACQUIRE_LOOP",
    "SEEKER_COAST_TIMEOUT", "TARGET_REMOVED_OR_INVALID", "UNCLASSIFIED",
]
DECOY_STAGES = [
    "NOT_DEPLOYED", "DEPLOYED_OUTSIDE_WINDOW", "DEPLOYED_NOT_OBSERVABLE",
    "OBSERVABLE_GATE_REJECTED", "CANDIDATE_NOT_SELECTED",
    "SELECTED_THEN_RECOVERED_TARGET", "SEDUCED",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("--json", type=Path, default=HERE / "BASELINE_AUDIT.json")
    parser.add_argument("--markdown", type=Path, default=HERE / "BASELINE_AUDIT.md")
    args = parser.parse_args()

    raw = args.product.read_bytes()
    if len(raw) != HP_A_BYTES or sha256(raw) != HP_A_SHA256:
        raise AssertionError("pinned HP_A product mismatch")
    source = unpack_main(raw)
    rows: list[dict] = []
    missing: list[str] = []
    for group, names in FUNCTIONS.items():
        for name in names:
            spans = function_spans(source, name)
            if not spans:
                missing.append(name)
                continue
            for occurrence, (start, end) in enumerate(spans, 1):
                body = source[start:end].encode()
                rows.append({
                    "group": group,
                    "name": name,
                    "occurrence": occurrence,
                    "line": source.count("\n", 0, start) + 1,
                    "bytes": len(body),
                    "sha256": sha256(body),
                })
    checks = {
        "productBytesExact": len(raw) == HP_A_BYTES,
        "productShaExact": sha256(raw) == HP_A_SHA256,
        "requiredFunctionsPresent": not missing,
        "u4CommonModeActive": "const SEEKER_U4_COMMON_MODE_C='ACTIVE';" in source,
        "u4AnonymousContractPresent": "anonymousDecisionSource" in source,
        "u4CommonRngFreeContractPresent": "rngConsumedByCommonLayer:false" in source,
        "nulkaPhysicalReturnPathPresent": "_debugKind:'NULKA'" in source,
        "chaffPhysicalReturnPathPresent": "kind:'CHAFF'" in source,
        "decoySelectionDiagnosticFieldsPresent": all(token in source for token in (
            "lastDeceptionReturnCount", "lastAssocDebugKind", "lastCandidateCount",
            "lastValidatedCandidateCount", "lastRejectReasonWip13C8",
        )),
        "hpAOutcomeContractPresent": "AEGIS_SHIP_OUTCOME_A_1" in source,
    }
    historical = {
        "role": "HISTORICAL_REFERENCE_ONLY_NOT_CURRENT_ACCEPTANCE_TARGET",
        "population": "TRACK-B R4 and TRACK-C paired battle set; 320 initial ASM per product",
        "R4": {"seekerLoss": 36, "decoyLure": 0, "other": 3},
        "TRACK_C": {"seekerLoss": 34, "decoyLure": 0, "other": 3},
        "trackCReportZipSha256": "b2d1a4ee5a733c4f16836182a5f71776ab73f95e0b3d957a59e8056e9645e8b0",
        "trackCReportMdSha256": "6cc540ac21adbde23bed241e9fc3d63fc6337e4c463445a5c962db5491a34a3a",
        "trackCLineageResultsSha256": "f7e290a483d10df3f70231770d2ed0104923e609cf521ce28bd8f40904e435d8",
        "trackBR4ReportMdSha256": "66fafe7dbf1187f147adcd7daf8c179bcd2852f4eef0e98df336f7bc496a5d98",
    }
    contract = {
        "schema": "AEGIS_SEEKER_CLOSE_A_CLASSIFICATION_CONTRACT_1",
        "afterActionOnly": True,
        "truthMayBeUsedOnlyAfterTerminal": True,
        "tacticalConsumerReads": 0,
        "terminalCategories": TERMINAL_CATEGORIES,
        "decoyStages": DECOY_STAGES,
        "requiredPerShotFields": [
            "weapon", "profile", "seed", "launchTimeS", "terminalTimeS",
            "terminalCategory", "firstValidObservationS", "lastValidObservationS",
            "stateTransitions", "gateRejectReasons", "validCandidateCounts",
            "selectedCandidateKinds", "guidanceAvailable", "decoyStage",
            "hardKillIntervention", "ciwsIntervention", "softKillIntervention",
            "closestApproachM", "seaImpact", "targetHit", "combatRngStart", "combatRngEnd",
        ],
        "noForcedInference": "Unresolved evidence remains UNCLASSIFIED.",
    }
    payload = {
        "schema": "AEGIS_SEEKER_CLOSE_A_BASELINE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baseMain": BASE_MAIN,
        "precondition": {
            "hpAPullRequest": 77,
            "hpAHead": HP_A_PR_HEAD,
            "mergeCommit": BASE_MAIN,
            "mergeMethod": "MERGE_COMMIT",
            "actionsRun": 42545220615,
        },
        "product": args.product.name,
        "productBytes": len(raw),
        "productSha256": sha256(raw),
        "packedMainBytes": len(source.encode()),
        "packedMainSha256": sha256(source.encode()),
        "checks": checks,
        "missingFunctions": missing,
        "functionHashes": rows,
        "historicalReference": historical,
        "classificationContract": contract,
        "productMutationCount": 0,
        "broadRegressionRun": False,
        "release": False,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(strict(payload))
    table = "\n".join(
        f"| {row['group']} | `{row['name']}` | {row['occurrence']} | {row['line']} | `{row['sha256']}` |"
        for row in rows
    )
    markdown = f"""# SEEKER_CLOSE_A Commit A — baseline audit

Status: **{payload['status']}**. This audit is read-only; product/RNG/save mutation count is **0**.

## Frozen baseline

- main merge commit: `{BASE_MAIN}`
- HP_A PR #77 head: `{HP_A_PR_HEAD}`
- HP_A product: `{len(raw):,}` bytes, `{sha256(raw)}`
- packed main: `{len(source.encode()):,}` bytes, `{sha256(source.encode())}`

## Historical reference (not a current pass target)

TRACK-B R4: SEEKER_LOSS 36 / DECOY_LURE 0 / OTHER 3.  TRACK-C: 34 / 0 / 3.
Both populations contained 320 initial ASMs.  These values are retained only as an alarm and provenance record; no current-product threshold or tuning target is derived from them.

## Classification contract

Terminal categories: {', '.join(f'`{item}`' for item in TERMINAL_CATEGORIES)}.

Decoy stages: {', '.join(f'`{item}`' for item in DECOY_STAGES)}.

The classifier is AFTER_ACTION-only.  It may compare truth after terminal for diagnosis, but no physical ID or hidden coordinate enters the seeker, guidance, association, ROE, or weapon authority path.  Ambiguous evidence stays `UNCLASSIFIED`.

## Frozen function hashes

| Group | Function | Occurrence | Line | SHA-256 |
|---|---|---:|---:|---|
{table}
"""
    args.markdown.write_text(markdown)
    print(strict({"status": payload["status"], "checks": checks, "functions": len(rows)}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
