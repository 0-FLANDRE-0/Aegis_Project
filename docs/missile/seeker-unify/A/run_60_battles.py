#!/usr/bin/env python3
"""Reuse the frozen TRACK-C 60-battle runner against SEEKER_UNIFY_A."""
from __future__ import annotations

import importlib.util
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "docs/missile/asm-seeker/A/run_s3_battles.py"
TMP = Path("/dev/shm/seeker-unify-battle-root")
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"

spec = importlib.util.spec_from_file_location("seeker_unify_frozen_s3", SOURCE)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)

TMP.mkdir(parents=True, exist_ok=True)
alias = TMP / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
if not alias.exists():
    alias.symlink_to(PRODUCT)
assert alias.resolve() == PRODUCT.resolve()

runner.ROOT = TMP
runner.HERE = HERE
runner.ORIG = Path("/dev/shm/seeker-unify-track-c")
runner.OUT = HERE / "evidence/s3-battles"
runner.OUT.mkdir(parents=True, exist_ok=True)

SHARDS = 2


def worker(shard: int) -> int:
    all_jobs = runner.jobs()
    runner.jobs = lambda: all_jobs[shard::SHARDS]
    return runner.worker(shard)


def finalize(started: float, commands: list[list[str]]) -> int:
    shards = [json.loads((runner.OUT / f"shard-{n}.json").read_text()) for n in range(SHARDS)]
    rows = sorted(
        [row for shard in shards for row in shard["rows"]],
        key=lambda row: (row["scenario"], row["seed"]),
    )
    baseline = runner.baseline_rows()
    comparisons = []
    for row in rows:
        prior = baseline.get(row["id"])
        comparisons.append({
            "id": row["id"],
            "baselineAvailable": prior is not None,
            "before": None if prior is None else {
                key: prior[key] for key in (
                    "kills", "leakers", "egress", "other", "damagingHitRounds", "floodM3", "hpReferenceOnly"
                )
            },
            "after": {
                key: row[key] for key in ("kills", "leakers", "egress", "other", "floodM3", "hpReferenceOnly")
            },
        })
    sum_keys = ("kills", "leakers", "egress", "other")
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_60_BATTLE_REFERENCE_1",
        "status": "PASS" if len(rows) == 60 and all(
            row["status"] == "QUALIFYING_COMPLETED_BATTLE" and all(row["post"].values()) for row in rows
        ) else "INCOMPLETE",
        "productSha256": json.loads((HERE / "PRODUCT_BUILD.json").read_text())["outputSha256"],
        "jobs": len(rows),
        "expectedJobs": 60,
        "elapsedS": sum(row["wallS"] for row in rows),
        "currentResumeWallS": time.monotonic() - started,
        "commands": commands,
        "totals": {key: sum(row[key] for row in rows) for key in sum_keys},
        "baselineAvailable": len(baseline),
        "baselineTotals": {key: sum(value[key] for value in baseline.values()) for key in sum_keys},
        "rows": rows,
        "comparisons": comparisons,
        "physicalProbe": [shard["probe"] for shard in shards],
        "decisionUse": "REFERENCE_ONLY_PER_DIRECTIVE",
    }
    (HERE / "S3_BATTLE_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "jobs", "elapsedS", "currentResumeWallS", "totals", "baselineAvailable", "baselineTotals"
    )}, indent=2))
    return 0 if result["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int)
    args = parser.parse_args()
    if args.worker is not None:
        return worker(args.worker)
    started = time.monotonic()
    commands = [
        [sys.executable, "-u", str(Path(__file__).resolve()), "--worker", str(shard)]
        for shard in range(SHARDS)
    ]
    processes = []
    for shard, command in enumerate(commands):
        log = (runner.OUT / f"shard-{shard}.log").open("w")
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env={**os.environ, "TMPDIR": "/dev/shm", "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        processes.append((process, log))
    codes = []
    for process, log in processes:
        codes.append(process.wait())
        log.close()
    if any(codes):
        return 1
    return finalize(started, commands)


if __name__ == "__main__":
    raise SystemExit(main())
