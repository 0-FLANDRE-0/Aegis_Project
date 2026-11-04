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

sys.path[:0] = [
    "/dev/shm/seeker-unify-track-c/docs/missile/fuze-zem/A",
    "/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
    "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
    "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
    "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K",
]


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
B_RUNNER = ROOT / "docs/missile/seeker-unify/B/run_60_battles.py"
PRODUCT = Path(os.environ.get("SEEKER_C_BATTLE_PRODUCT", ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"))
TMP = Path(os.environ.get("SEEKER_C_BATTLE_TMP", "/dev/shm/seeker-unify-c-stage2-battle-root"))
BUILD_RECEIPT = Path(os.environ.get("SEEKER_C_BATTLE_BUILD", HERE / "BUILD.json"))
OUTPUT_DIR = Path(os.environ.get("SEEKER_C_BATTLE_OUTPUT_DIR", HERE / "evidence/beam-stage2-60-battles"))
RESULT_PATH = Path(os.environ.get("SEEKER_C_BATTLE_RESULT", HERE / "BEAM_STAGE2_60_BATTLE_RESULTS.json"))
COMPAT_RESULT_PATH = Path(os.environ.get("SEEKER_C_BATTLE_COMPAT_RESULT", HERE / "U0_60_BATTLE_RESULTS.json"))
COMPAT_RECEIPT_PATH = Path(os.environ.get("SEEKER_C_BATTLE_COMPAT_RECEIPT", HERE / "PRODUCT_BUILD.json"))


def load_runner():
    spec = importlib.util.spec_from_file_location("seeker_unify_c_stage2_battles", B_RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.SHARDS = max(1, int(os.environ.get("SEEKER_C_BATTLE_SHARDS", str(module.SHARDS))))
    compat_here = COMPAT_RESULT_PATH.parent
    compat_here.mkdir(parents=True, exist_ok=True)
    module.HERE = compat_here
    module.ROOT = ROOT
    module.TMP = TMP
    module.PRODUCT = PRODUCT
    TMP.mkdir(parents=True, exist_ok=True)
    alias = TMP / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
    if alias.is_symlink() or alias.exists():
        alias.unlink()
    alias.symlink_to(PRODUCT)
    module.runner.ROOT = TMP
    module.runner.HERE = compat_here
    module.runner.ORIG = Path("/dev/shm/seeker-unify-track-c")
    module.runner.OUT = OUTPUT_DIR
    module.runner.OUT.mkdir(parents=True, exist_ok=True)
    build = json.loads(BUILD_RECEIPT.read_text())
    (compat_here / "BUILD.json").write_text(json.dumps(build, indent=2) + "\n")
    COMPAT_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPAT_RECEIPT_PATH.write_text(json.dumps({
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
    source = COMPAT_RESULT_PATH
    result = json.loads(source.read_text())
    result.update({
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_60_BATTLE_REFERENCE_1",
        "stage": "SEEKER_UNIFY_C_STAGE2",
    })
    output = RESULT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    source.unlink()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
