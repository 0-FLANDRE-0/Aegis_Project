#!/usr/bin/env python3
"""Run the one CUE_A-1 60-battle reference with the frozen TRACK-C runner."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "docs/missile/seeker-unify/C/run_stage2_60_battles.py"
RESULT = HERE / "CUE_A_1_60_BATTLE_RESULTS.json"
PRIOR = ROOT / "docs/missile/seeker-unify/C/CUE_A_60_BATTLE_RESULTS.json"
TEMP_HARNESS = Path("/dev/shm/cue-a1-60-harness")


def prepare_harness() -> Path:
    """Recreate only the two frozen source files lost with the old worktree."""
    b_dir = TEMP_HARNESS / "docs/missile/seeker-unify/B"
    a_dir = TEMP_HARNESS / "docs/missile/asm-seeker/A"
    b_dir.mkdir(parents=True, exist_ok=True)
    a_dir.mkdir(parents=True, exist_ok=True)
    files = {
        ROOT / "docs/missile/seeker-unify/B/run_60_battles.py": b_dir / "run_60_battles.py",
        ROOT / "docs/missile/seeker-unify/B/BUILD.json": b_dir / "BUILD.json",
        Path("/workspace/aegis-asm-seeker-a/docs/missile/asm-seeker/A/run_s3_battles.py"):
            a_dir / "run_s3_battles.py",
    }
    for source, target in files.items():
        assert source.exists(), source
        if not target.exists() or target.read_bytes() != source.read_bytes():
            shutil.copy2(source, target)
    return b_dir / "run_60_battles.py"


def prior_rows() -> dict[str, dict]:
    data = json.loads(PRIOR.read_text())
    return {str(row["id"]): row for row in data["rows"]}


def main() -> int:
    os.environ.update({
        "SEEKER_C_BATTLE_PRODUCT": str(ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"),
        "SEEKER_C_BATTLE_TMP": "/dev/shm/cue-a1-final-battle-root",
        "SEEKER_C_BATTLE_BUILD": str(HERE / "BUILD.json"),
        "SEEKER_C_BATTLE_OUTPUT_DIR": "/dev/shm/cue-a1-final-60-battles",
        "SEEKER_C_BATTLE_RESULT": str(RESULT),
        "SEEKER_C_BATTLE_COMPAT_RESULT": "/dev/shm/cue-a1-final-compat/U0_60_BATTLE_RESULTS.json",
        "SEEKER_C_BATTLE_COMPAT_RECEIPT": "/dev/shm/cue-a1-final-compat/PRODUCT_BUILD.json",
        "SEEKER_C_BATTLE_SHARDS": os.environ.get("SEEKER_C_BATTLE_SHARDS", "4"),
    })
    spec = importlib.util.spec_from_file_location("cue_a_1_final_60_battles", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.B_RUNNER = prepare_harness()
    # Make child commands re-enter this adapter, so every worker receives the
    # same reconstructed frozen harness instead of the vanished old worktree.
    module.__file__ = str(Path(__file__).resolve())
    original_load = module.load_runner

    def load_runner():
        loaded = original_load()
        # The old TRACK-C statistics checkout was ephemeral.  The immediately
        # preceding C-final 60-battle result is the requested comparison and
        # supplies the same compact baseline keys without touching simulation.
        loaded.runner.baseline_rows = prior_rows
        return loaded

    module.load_runner = load_runner
    code = module.main()
    if code == 0:
        data = json.loads(RESULT.read_text())
        data.update({
            "schema": "AEGIS_CUE_A_1_60_BATTLE_REFERENCE_1",
            "stage": "CUE_A_1_FINAL",
            "comparisonBaseline": "SEEKER_UNIFY_C_FINAL",
            "comparisonBaselineSha256": "efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7",
            "runnerPolicy": "FROZEN_TRACK_C_AFTER_ACTION_REFERENCE; MAX_THREAT; four parallel shards",
        })
        RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
