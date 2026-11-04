#!/usr/bin/env python3
"""Run the frozen TRACK-C 60-battle reference against Stage 2."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
B_RUNNER = ROOT / "docs/missile/seeker-unify/B/run_60_battles.py"
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
TMP = Path("/dev/shm/seeker-unify-c-stage2-battle-root")


def load_runner():
    spec = importlib.util.spec_from_file_location("seeker_unify_c_stage2_battles", B_RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.ROOT = ROOT
    module.TMP = TMP
    module.PRODUCT = PRODUCT
    TMP.mkdir(parents=True, exist_ok=True)
    alias = TMP / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
    if alias.is_symlink() or alias.exists():
        alias.unlink()
    alias.symlink_to(PRODUCT)
    module.runner.ROOT = TMP
    module.runner.HERE = HERE
    module.runner.ORIG = Path("/dev/shm/seeker-unify-track-c")
    module.runner.OUT = HERE / "evidence/beam-stage2-60-battles"
    module.runner.OUT.mkdir(parents=True, exist_ok=True)
    build = json.loads((HERE / "BUILD.json").read_text())
    (HERE / "PRODUCT_BUILD.json").write_text(json.dumps({
        "outputSha256": build["productHtmlSha256"],
        "compatibilityUse": "FROZEN_TRACK_C_RUNNER_ONLY",
        "stage": "SEEKER_UNIFY_C_STAGE2",
    }, indent=2) + "\n")
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int)
    args = parser.parse_args()
    module = load_runner()
    if args.worker is not None:
        return module.worker(args.worker)
    started = time.monotonic()
    commands = [
        [sys.executable, "-u", str(Path(__file__).resolve()), "--worker", str(shard)]
        for shard in range(module.SHARDS)
    ]
    processes = []
    for shard, command in enumerate(commands):
        log = (module.runner.OUT / f"shard-{shard}.log").open("w")
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
    code = module.finalize(started, commands)
    source = HERE / "U0_60_BATTLE_RESULTS.json"
    result = json.loads(source.read_text())
    result.update({
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_60_BATTLE_REFERENCE_1",
        "stage": "SEEKER_UNIFY_C_STAGE2",
    })
    output = HERE / "BEAM_STAGE2_60_BATTLE_RESULTS.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    source.unlink()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
