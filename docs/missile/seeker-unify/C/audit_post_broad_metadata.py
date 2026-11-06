#!/usr/bin/env python3
"""Prove that the post-broad ENV_D repair changes expectation metadata only."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


OLD_PROFILE = "fa87852960ef276597cd43653d3d112da07cd844448d5ee6ad703c4791043121"
NEW_PROFILE = "06b12b074b8a7461e121a00c109b41fa085510de0ab25654b78f2dd2b9f591e8"
OLD_SPAWN = "464f1388a3e2b53ca6de34b2d7915434d4b11e0cf9619ea61f0ef8eddc29021f"
NEW_SPAWN = "cc18263e2b72d6a8ac7b5c49b492e65891a03012b56b41de170f1c37498327ec"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(path: Path) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', path.read_bytes())
    if not match:
        raise AssertionError(f"packed main source missing: {path}")
    return gzip.decompress(base64.b64decode(match[1])).decode()


def table(source: str) -> dict:
    marker = "const ENVELOPE_TABLE_D="
    start = source.index(marker) + len(marker)
    end = source.index(";\n", start)
    return json.loads(source[start:end])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    before, after = unpack(args.before), unpack(args.after)
    normalized = after.replace(NEW_PROFILE, OLD_PROFILE).replace(NEW_SPAWN, OLD_SPAWN)
    before_table, after_table = table(before), table(after)
    normalized_table = json.loads(json.dumps(after_table))
    normalized_table["profileHash"] = before_table["profileHash"]
    normalized_table["nativeSourceHashes"]["spawnEnemyMissile"] = before_table["nativeSourceHashes"]["spawnEnemyMissile"]
    checks = {
        "normalizedMainExact": normalized == before,
        "profileHashChangedExactlyOnce": before.count(OLD_PROFILE) == 1 and after.count(NEW_PROFILE) == 1,
        "spawnExpectationChangedExactlyTwice": before.count(OLD_SPAWN) == 2 and after.count(NEW_SPAWN) == 2,
        "measuredRowsExact": before_table["rows"] == after_table["rows"],
        "conditionsExact": before_table["conditions"] == after_table["conditions"],
        "seedsExact": before_table["seeds"] == after_table["seeds"],
        "normalizedTableExact": normalized_table == before_table,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_POST_BROAD_METADATA_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "before": {"file": args.before.name, "sha256": sha(args.before)},
        "after": {"file": args.after.name, "sha256": sha(args.after)},
        "checks": checks,
        "changes": {
            "profileHash": {"before": OLD_PROFILE, "after": NEW_PROFILE},
            "nativeSourceHashes.spawnEnemyMissile": {"before": OLD_SPAWN, "after": NEW_SPAWN},
            "measuredRowsChanged": 0,
            "conditionsChanged": 0,
            "tolerancesChanged": 0,
            "gameplayFunctionSourceChangedAfterBroad": 0,
        },
        "reason": "CUE_A launch-memory metadata changes the conservative ENV_D integrity input without changing its straight-target measurements.",
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
