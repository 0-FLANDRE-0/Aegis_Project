#!/usr/bin/env python3
"""Prove that the post-broad CUE_A-1 correction is metadata-only."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

from build_product import (
    ENV_D_PROFILE_AFTER,
    ENV_D_PROFILE_BEFORE,
    ENV_D_SPAWN_AFTER,
    ENV_D_SPAWN_BEFORE,
)


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
    normalized = after.replace(ENV_D_PROFILE_AFTER, ENV_D_PROFILE_BEFORE).replace(
        ENV_D_SPAWN_AFTER, ENV_D_SPAWN_BEFORE
    )
    before_table, after_table = table(before), table(after)
    normalized_table = json.loads(json.dumps(after_table))
    normalized_table["profileHash"] = before_table["profileHash"]
    normalized_table["nativeSourceHashes"]["spawnEnemyMissile"] = before_table["nativeSourceHashes"]["spawnEnemyMissile"]
    checks = {
        "normalizedMainExact": normalized == before,
        "profileHashChangedExactlyOnce": before.count(ENV_D_PROFILE_BEFORE) == 1 and after.count(ENV_D_PROFILE_AFTER) == 1,
        "spawnExpectationChangedExactlyTwice": before.count(ENV_D_SPAWN_BEFORE) == 2 and after.count(ENV_D_SPAWN_AFTER) == 2,
        "measuredRowsExact": before_table["rows"] == after_table["rows"],
        "conditionsExact": before_table["conditions"] == after_table["conditions"],
        "seedsExact": before_table["seeds"] == after_table["seeds"],
        "normalizedTableExact": normalized_table == before_table,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_POST_BROAD_METADATA_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "before": {"file": args.before.name, "sha256": sha(args.before)},
        "after": {"file": args.after.name, "sha256": sha(args.after)},
        "checks": checks,
        "changes": {
            "profileHash": {"before": ENV_D_PROFILE_BEFORE, "after": ENV_D_PROFILE_AFTER},
            "nativeSourceHashes.spawnEnemyMissile": {"before": ENV_D_SPAWN_BEFORE, "after": ENV_D_SPAWN_AFTER},
            "measuredRowsChanged": 0,
            "conditionsChanged": 0,
            "seedsChanged": 0,
            "tolerancesChanged": 0,
            "gameplayFunctionSourceChangedAfterBroad": 0,
        },
        "reason": "Stage 2 observed emitter metadata advances the conservative ENV_D fingerprint without changing its ideal-target measurements.",
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
