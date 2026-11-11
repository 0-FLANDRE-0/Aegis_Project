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

FUNCTIONS = [
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
]

OPTIONAL_FUNCTIONS = [
    "defenseDecisionInputSnapshotA1", "defenseDecisionLegacyCommandA1",
    "defenseDecisionLegacyBeginA1", "defenseDecisionLegacySalvoA1",
    "defenseDecisionRecommendationOrderA1", "defenseDecisionValidateCommandA1",
]


def packed_main(raw: bytes) -> bytes:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise ValueError("packed main index 13 not found")
    return gzip.decompress(base64.b64decode(match.group(1)))


def function_source(source: str, name: str) -> str:
    match = re.search(r"(?:async\s+)?function\s+" + re.escape(name) + r"\s*\(", source)
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


def audit(product: Path, stage: str) -> dict:
    raw = product.read_bytes()
    main = packed_main(raw)
    source = main.decode("utf-8")
    hashes = {}
    names = list(FUNCTIONS)
    names.extend(name for name in OPTIONAL_FUNCTIONS if re.search(
        r"(?:async\s+)?function\s+" + re.escape(name) + r"\s*\(", source
    ))
    for name in names:
        body = function_source(source, name).encode("utf-8")
        hashes[name] = {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
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
        "functions": hashes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--stage", default="INTEGRATION_BASELINE_A_COMMIT_A")
    args = parser.parse_args()
    result = audit(args.product, args.stage)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"product": result["product"], "packedMain": result["packedMain"], "functions": len(result["functions"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
