#!/usr/bin/env python3
"""Extract packed main and freeze exact function-source hashes."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

PROTECTED_FUNCTIONS = [
    "updateTrackOperationalStateA3", "trackEngagementGateA3",
    "wip118BuildEngagementControl", "wip118SalvoPolicyNativeH1",
    "wip119EvaluateRow", "wip119FireOne", "networkBidG",
    "networkCoordinateG", "networkVlsGateG", "defenseGateE",
    "defenseCloseInE", "defenseLocalMeasurementH4A",
    "defenseLocalReleaseH4A", "consumeVlsCell", "vlsReleaseStandardB1",
    "vlsReleaseEssmB1", "stepOwnerPhalanxD", "applyPhalanxProjectileHit",
    "maneuverEvaluateH2", "attackEvaluateH3", "teamFixedStepH4",
    "tacticalEvaluateH1", "tacticalOrderH1",
    "tacticalRecommendationOrderH1", "tacticalSalvoH1",
    "shipOutcomeFromInputsA", "shipOutcomeA", "shipOutcomeWriteDisplayA",
    "shipOutcomeRestoreCompatibilityA", "exportOperationalState",
    "importOperationalState",
]

NEW_BOUNDARY_FUNCTIONS = [
    "defenseDecisionCrewInputA1", "defenseDecisionTrackInputA1",
    "defenseDecisionInputSnapshotA1", "defenseDecisionLegacyCommandA1",
    "defenseDecisionLegacyBeginA1", "defenseDecisionLegacySalvoA1",
    "defenseDecisionRecommendationOrderA1", "defenseDecisionLegacyFinishA1",
    "defenseDecisionValidateCommandA1", "defenseDecisionForbiddenPathA1",
    "defenseDecisionFrozenA1",
]

# The adapter is intentionally installed once in each of the two existing
# owner-local lexical roots (player and foreign ship). Global validation helpers
# remain single definitions. These are not duplicate symbols in one scope.
NEW_BOUNDARY_DEFINITION_COUNTS = {
    "defenseDecisionCrewInputA1": 2,
    "defenseDecisionTrackInputA1": 2,
    "defenseDecisionInputSnapshotA1": 2,
    "defenseDecisionLegacyCommandA1": 2,
    "defenseDecisionLegacyBeginA1": 2,
    "defenseDecisionLegacySalvoA1": 2,
    "defenseDecisionRecommendationOrderA1": 2,
    "defenseDecisionLegacyFinishA1": 2,
    "defenseDecisionValidateCommandA1": 1,
    "defenseDecisionForbiddenPathA1": 1,
    "defenseDecisionFrozenA1": 1,
}


def packed_main(raw: bytes) -> bytes:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise ValueError("packed main index 13 not found")
    return gzip.decompress(base64.b64decode(match.group(1)))


def function_source(source: str, name: str, start: int = 0) -> str:
    pattern = re.compile(r"(?:async\s+)?function\s+" + re.escape(name) + r"\s*\(")
    match = pattern.search(source, start)
    if not match:
        raise ValueError(f"function not found: {name}")
    # The first brace after the function name is not necessarily the function
    # body: this codebase frequently uses object defaults such as `opts={}`.
    # Walk the complete parameter list before locating the body.  Strings and
    # comments are ignored so parentheses inside them do not change nesting.
    param_open = match.end() - 1
    paren_depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = param_open
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if ch in "\r\n":
                line_comment = False
        elif block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 1
        elif quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
        elif ch == "/" and nxt == "/":
            line_comment = True
            i += 1
        elif ch == "/" and nxt == "*":
            block_comment = True
            i += 1
        elif ch in "'\"`":
            quote = ch
        elif ch == "(":
            paren_depth += 1
        elif ch == ")":
            paren_depth -= 1
            if paren_depth == 0:
                break
        i += 1
    if paren_depth != 0:
        raise ValueError(f"unterminated parameter list: {name}")
    brace = source.find("{", i + 1)
    if brace < 0:
        raise ValueError(f"function body not found: {name}")
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if ch in "\r\n":
                line_comment = False
        elif block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 1
        elif quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
        elif ch == "/" and nxt == "/":
            line_comment = True
            i += 1
        elif ch == "/" and nxt == "*":
            block_comment = True
            i += 1
        elif ch in "'\"`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[match.start() : i + 1]
        i += 1
    raise ValueError(f"unterminated function: {name}")


def definition_positions(source: str, names: list[str]) -> dict[str, list[int]]:
    wanted = set(names)
    result = {name: [] for name in names}
    pattern = re.compile(r"(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
    for match in pattern.finditer(source):
        name = match.group(1)
        if name in wanted:
            result[name].append(match.start())
    return result


def audit(product: Path, stage: str, require_new: bool = False) -> dict:
    raw = product.read_bytes()
    main = packed_main(raw)
    source = main.decode("utf-8")
    hashes = {}
    positions = definition_positions(source, [*PROTECTED_FUNCTIONS, *NEW_BOUNDARY_FUNCTIONS])
    counts = {name: len(rows) for name, rows in positions.items()}
    invalid_protected = {name: counts[name] for name in PROTECTED_FUNCTIONS if counts[name] < 1}
    if invalid_protected:
        raise ValueError(f"protected function definition count: {invalid_protected}")
    invalid_new = {name: counts[name] for name in NEW_BOUNDARY_FUNCTIONS if counts[name] != NEW_BOUNDARY_DEFINITION_COUNTS[name]}
    if require_new and invalid_new:
        raise ValueError(f"required boundary function definition count: {invalid_new}")
    unexpected_new = {name: counts[name] for name in NEW_BOUNDARY_FUNCTIONS if not require_new and counts[name] not in (0, NEW_BOUNDARY_DEFINITION_COUNTS[name])}
    if unexpected_new:
        raise ValueError(f"unexpected boundary function definition count: {unexpected_new}")
    names = [*PROTECTED_FUNCTIONS, *(name for name in NEW_BOUNDARY_FUNCTIONS if counts[name] == 1)]
    names.extend(name for name in NEW_BOUNDARY_FUNCTIONS if counts[name] > 1)
    for name in names:
        body = function_source(source, name, positions[name][0]).encode("utf-8")
        hashes[name] = {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
    definition_hashes = {}
    for name, rows in positions.items():
        definition_hashes[name] = []
        for start in rows:
            body = function_source(source, name, start).encode("utf-8")
            definition_hashes[name].append({"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)})
    return {
        "schema": "AEGIS_INTEGRATION_BASELINE_FUNCTION_HASHES_A_1",
        "stage": stage,
        "mainHead": "d5f43c5a7d3550efb2f45d10aaf4195fb60955ae",
        "product": {
            "path": product.name,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "packedMain": {"index": 13, "bytes": len(main), "sha256": hashlib.sha256(main).hexdigest()},
        "extraction": "regex data-c55-index=13 -> base64 decode -> gzip decompress",
        "normalization": "NONE_EXACT_SOURCE_BYTES",
        "contract": {
            "protectedFunctions": PROTECTED_FUNCTIONS,
            "newBoundaryFunctions": NEW_BOUNDARY_FUNCTIONS,
            "newBoundaryExpectedDefinitionCounts": NEW_BOUNDARY_DEFINITION_COUNTS,
            "newBoundaryRequired": require_new,
            "definitionCounts": counts,
            "policy": "PROTECTED_EXACT_BASELINE_CANDIDATE; NEW_BOUNDARY_OPTIONAL_ONLY_FOR_PRE_PORT_BASELINE_AND_REQUIRED_FOR_ACTIVE_CANDIDATE",
        },
        "functions": hashes,
        "definitionHashes": definition_hashes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--stage", default="INTEGRATION_BASELINE_A_COMMIT_A")
    parser.add_argument("--require-new", action="store_true")
    args = parser.parse_args()
    result = audit(args.product, args.stage, args.require_new)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"product": result["product"], "packedMain": result["packedMain"], "functions": len(result["functions"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
