#!/usr/bin/env python3
"""Run the frozen TRACK-C 60-battle matrix and audit first ASM associations.

Physical labels are read only from the frozen after-action observer.  They are
never exposed to, or consumed by, the product simulation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "docs/missile/asm-seeker/A/run_s3_battles.py"
TMP = Path("/dev/shm/seeker-unify-b-battle-root")
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html"

spec = importlib.util.spec_from_file_location("seeker_unify_b_frozen_s3", SOURCE)
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
runner.OUT = HERE / "evidence/u0-60-battles-cap-r2"
runner.OUT.mkdir(parents=True, exist_ok=True)
# The frozen runner expects its historical receipt filename.  Generate the
# compatibility receipt from this stage's authoritative BUILD.json.
build_receipt = json.loads((HERE / "BUILD.json").read_text())
(HERE / "PRODUCT_BUILD.json").write_text(json.dumps({
    "outputSha256": build_receipt["productHtmlSha256"],
    "compatibilityUse": "FROZEN_TRACK_C_RUNNER_ONLY",
}, indent=2) + "\n")

# Return only the first accepted association for each initial ASM, rather than
# serializing the full after-action trace.  This is an AFTER_ACTION_TRUTH-only
# assertion and cannot affect the game path.
runner.EXPR = """c=>{const r=__TRACK_STABLE_BATTLE__.run(c);return {
  status:r.status,end:r.end,qualification:r.qualification,counts:{launches:r.counts.launches,
  intercepts:r.counts.intercepts,phalanxHits:r.counts.phalanxHits,shipHitRecords:r.counts.shipHitRecords},
  targets:r.targets,ship:{hp:r.final.ship.shipHP,flooding:r.final.ship.damage.flooding},
  inventory:r.final.inventory,globalRng:r.final.globalRng,core:r.final.core,
  runtimeFault:r.final.runtimeFault,presentationFault:r.final.presentationFault,
  diagnostics:r.diagnostics,faults:r.faults,statisticalEndpoint:r.statisticalEndpoint,
  firstAssociations:(r.trackCLineage?.seeker??[]).map(q=>({id:q.id,first:q.accepted?.[0]??null}))};}"""

base_compact = runner.compact


def compact(job, value, wall):
    row = base_compact(job, value, wall)
    row["firstAssociations"] = value.get("firstAssociations", [])
    return row


runner.compact = compact
SHARDS = 2


def worker(shard: int) -> int:
    all_jobs = runner.jobs()
    runner.jobs = lambda: all_jobs[shard::SHARDS]
    return runner.worker(shard)


def first_family(entry: dict) -> str:
    first = entry.get("first") or {}
    members = first.get("members") or []
    filtered = sorted({str(v) for v in members if v is not None and v != "SEA_CLUTTER"})
    return "+".join(filtered) if filtered else "NONE"


def finalize(started: float, commands: list[list[str]]) -> int:
    shards = [json.loads((runner.OUT / f"shard-{n}.json").read_text()) for n in range(SHARDS)]
    rows = sorted(
        [row for shard in shards for row in shard["rows"]],
        key=lambda row: (row["scenario"], row["seed"]),
    )
    baseline = runner.baseline_rows()
    sum_keys = ("kills", "leakers", "egress", "other")
    associations = [
        {
            "battleId": row["id"],
            "scenario": row["scenario"],
            "seed": row["seed"],
            "missileId": entry["id"],
            "family": first_family(entry),
            "first": entry.get("first"),
        }
        for row in rows for entry in row.get("firstAssociations", [])
    ]
    non_ship = [row for row in associations if row["family"] != "NONE" and "SHIP" not in row["family"]]
    neighbor = [row for row in associations if "ASM" in row["family"]]
    status = "PASS" if (
        len(rows) == 60
        and all(row["status"] == "QUALIFYING_COMPLETED_BATTLE" and all(row["post"].values()) for row in rows)
        and not neighbor
        and not non_ship
    ) else "INCOMPLETE"
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U0_60_BATTLE_REFERENCE_1",
        "status": status,
        "productSha256": json.loads((HERE / "BUILD.json").read_text())["productHtmlSha256"],
        "jobs": len(rows),
        "expectedJobs": 60,
        "elapsedS": sum(row["wallS"] for row in rows),
        "currentResumeWallS": time.monotonic() - started,
        "commands": commands,
        "totals": {key: sum(row[key] for row in rows) for key in sum_keys},
        "baselineAvailable": len(baseline),
        "baselineTotals": {key: sum(value[key] for value in baseline.values()) for key in sum_keys},
        "firstAssociationAudit": {
            "tag": "AFTER_ACTION_TRUTH_TEST_ONLY",
            "observed": len(associations),
            "families": dict(Counter(row["family"] for row in associations)),
            "neighborAsmFirstAssociations": len(neighbor),
            "nonShipFirstAssociations": len(non_ship),
            "neighborRows": neighbor,
            "nonShipRows": non_ship,
        },
        "rows": rows,
        "physicalProbe": [shard["probe"] for shard in shards],
        "decisionUse": "REFERENCE_PLUS_U0_FIRST_ASSOCIATION_GATE",
    }
    (HERE / "U0_60_BATTLE_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "jobs", "elapsedS", "currentResumeWallS", "totals",
        "baselineAvailable", "baselineTotals", "firstAssociationAudit",
    )}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


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
