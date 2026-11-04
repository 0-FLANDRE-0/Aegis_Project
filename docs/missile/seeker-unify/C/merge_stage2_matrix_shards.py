#!/usr/bin/env python3
"""Merge Stage-2 shards in the canonical 1,590-case matrix order."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


COLLECTIONS = ("rangeCases", "samArhCases", "cueCases", "radarCases")


def key(row: dict) -> str:
    setup = {k: v for k, v in row["setup"].items() if k not in {"targetId", "turnAtS"}}
    return json.dumps(setup, sort_keys=True, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text())
    inputs = [json.loads(path.read_text()) for path in args.inputs]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_DIAGNOSTICS_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(args.html.read_bytes()).hexdigest(),
        "elapsedS": sum(float(doc.get("elapsedS", 0)) for doc in inputs),
        "wallClockMode": "FOUR_INDEPENDENT_SHARDS; elapsedS is summed CPU-wall, not parallel wall time",
        "pageErrors": sum((doc.get("pageErrors", []) for doc in inputs), []),
        # RCS audit values are geometry-only and unchanged by Stage 2.  The
        # candidate's direct audit is recorded separately and checked equal.
        "rcsAudits": baseline["rcsAudits"],
    }
    for name in COLLECTIONS:
        rows: dict[str, dict] = {}
        duplicates: list[str] = []
        for doc in inputs:
            for row in doc.get(name, []):
                row_key = key(row)
                if row_key in rows and rows[row_key] != row:
                    duplicates.append(row_key)
                rows[row_key] = row
        expected = [key(row) for row in baseline[name]]
        missing = [row_key for row_key in expected if row_key not in rows]
        extra = sorted(set(rows) - set(expected))
        if missing or extra or duplicates:
            raise SystemExit(f"{name}: missing={len(missing)} extra={len(extra)} conflicting={len(duplicates)}")
        result[name] = [rows[row_key] for row_key in expected]
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({
        "output": str(args.out),
        "sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
        "counts": {name: len(result[name]) for name in COLLECTIONS},
        "pageErrors": len(result["pageErrors"]),
    }))


if __name__ == "__main__":
    main()
