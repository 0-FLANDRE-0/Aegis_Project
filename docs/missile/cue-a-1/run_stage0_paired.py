#!/usr/bin/env python3
"""Attribute frozen paired-raid deltas across B, C Stage 2, and C final."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKS = (
    "samePhysicalState",
    "sameCombatRng",
    "raidInventoryDeltaBounded",
    "sameExistingObserverState",
)
METRIC = {
    "samePhysicalState": "physicalStateSha256",
    "sameCombatRng": "combatRng",
    "raidInventoryDeltaBounded": "loadedVls",
    "sameExistingObserverState": "observerStateSha256",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def physical(value: object) -> object:
    """Mirror the frozen paired harness normalizer."""
    if isinstance(value, dict):
        result = {key: physical(item) for key, item in value.items() if key not in {"performance", "aviation"}}
        if value.get("schema") == "AEGIS_OFFBOARD_PORT_C_1":
            result.pop("helicopterImplemented", None)
            result["sources"] = [row for row in result.get("sources", []) if row.get("sourceId") not in {"H1", "H2"}]
        if value.get("schema") == "AEGIS_SHIP_OBSERVER_C_1" and "deferred" in result:
            result["deferred"] = [row for row in result["deferred"] if row != "helicopterFlightAndSensors"]
        return result
    if isinstance(value, list):
        return [physical(item) for item in value]
    return value


def target_summary(pair: dict) -> list[dict]:
    return [
        {key: row.get(key) for key in ("id", "label", "alive", "reason")}
        for row in pair.get("afterActionTruth", {}).get("targets", [])
    ]


def run_pair(label: str, baseline: Path, candidate: Path, harness_root: Path, raw_root: Path) -> dict:
    out = raw_root / label
    out.mkdir(parents=True, exist_ok=True)
    verifier = harness_root / "docs/helicopter/F/verify_regression.py"
    env = {
        **os.environ,
        "TMPDIR": "/dev/shm",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": "/workspace/aegis-performance-c/docs/performance/C/node_modules",
        "B2_PHASE1_REGRESSION": "1",
        "B2_MODE": "ON",
        "B2_HTML": str(candidate.resolve()),
        "B2_OUT": str(out.resolve()),
        "PYTHONPATH": str(harness_root / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0",
    }
    command = [sys.executable, "-u", str(verifier), str(baseline), str(candidate), str(out), "--baseline-only"]
    print(f"RUN {label}: {sha(baseline)[:12]} -> {sha(candidate)[:12]}", flush=True)
    completed = subprocess.run(command, env=env, text=True, capture_output=True)
    (out / "stdout.log").write_text(completed.stdout)
    (out / "stderr.log").write_text(completed.stderr)
    result_path = out / "baseline-comparison.json"
    if not result_path.exists():
        raise RuntimeError(f"{label}: paired harness produced no result (exit {completed.returncode})")
    result = json.loads(result_path.read_text())
    execution = {
        "label": label,
        "command": command,
        "exitCode": completed.returncode,
        "baseline": {"path": str(baseline), "sha256": sha(baseline)},
        "candidate": {"path": str(candidate), "sha256": sha(candidate)},
        "resultSha256": sha(result_path),
        "errors": result.get("errors", []),
        "assertions": sum(len(case.get("checks", {})) for case in result.get("cases", [])),
    }
    (out / "execution.json").write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n")
    print(f"DONE {label}: exit={completed.returncode}, errors={len(result.get('errors', []))}", flush=True)
    return {"result": result, "execution": execution}


def stage_snapshot(case: dict, side: str) -> dict:
    pair = case["pair"][side]
    index = 0 if side == "baseline" else 1
    return {
        "physicalStateSha256": digest(physical(pair["state"])),
        "combatRng": pair.get("rng"),
        "loadedVls": case["observations"]["loadedVlsBeforeAfter"][index],
        "observerStateSha256": digest(physical(pair.get("observers"))),
        "shipHP": pair["state"].get("shipHP"),
        "targets": target_summary(pair),
        "intercepts": len(pair.get("afterActionTruth", {}).get("intercepts", [])),
        "entityCounts": pair.get("profiler", {}).get("entityCounts"),
        "faults": pair.get("faults"),
    }


def raid_cases(result: dict) -> dict[str, dict]:
    return {case["ship"]: case for case in result["cases"] if case["scenario"] == "raid"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--b", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html")
    parser.add_argument("--stage2", type=Path, required=True)
    parser.add_argument("--final", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html")
    parser.add_argument("--harness-root", type=Path, default=Path("/workspace/aegis-ui-a"))
    parser.add_argument("--raw-root", type=Path, default=Path("/dev/shm/cue-a1-stage0"))
    args = parser.parse_args()

    first_run = run_pair("b-to-stage2", args.b, args.stage2, args.harness_root, args.raw_root)
    second_run = run_pair("stage2-to-final", args.stage2, args.final, args.harness_root, args.raw_root)
    first = raid_cases(first_run["result"])
    second = raid_cases(second_run["result"])
    expected = json.loads((ROOT / "docs/missile/seeker-unify/C/PAIRED_RAID_EXPECTATION_UPDATES.json").read_text())
    expected_by_ship = {row["ship"]: row for row in expected["updates"]}

    rows = []
    gates = {
        "productHashesMatchDirective": sha(args.b) == "b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d"
        and sha(args.stage2) == "dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec"
        and sha(args.final) == "efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7",
        "harnessErrorsZero": not first_run["result"].get("errors") and not second_run["result"].get("errors"),
        "shipsExact": set(first) == set(second) == set(expected_by_ship),
        "stage2ReplayExact": True,
        "allEightFinalChangesAttributed": True,
        "safetyChecksRemainTrue": True,
    }
    for ship in sorted(expected_by_ship):
        first_case, second_case = first[ship], second[ship]
        stages = {
            "B": stage_snapshot(first_case, "baseline"),
            "C_STAGE2": stage_snapshot(first_case, "candidate"),
            "C_STAGE2_REPLAY": stage_snapshot(second_case, "baseline"),
            "C_FINAL": stage_snapshot(second_case, "candidate"),
        }
        replay_exact = stages["C_STAGE2"] == stages["C_STAGE2_REPLAY"]
        gates["stage2ReplayExact"] &= replay_exact
        safety = {
            "bToStage2": {key: first_case["checks"][key] for key in ("sameHullDamageAndFixedLayout", "sameExistingOffboardPorts", "bothFaultFree")},
            "stage2ToFinal": {key: second_case["checks"][key] for key in ("sameHullDamageAndFixedLayout", "sameExistingOffboardPorts", "bothFaultFree")},
        }
        gates["safetyChecksRemainTrue"] &= all(safety[segment][key] for segment in safety for key in safety[segment])
        for check in CHECKS:
            key = METRIC[check]
            changed_stage2 = stages["B"][key] != stages["C_STAGE2"][key]
            changed_stage3 = stages["C_STAGE2"][key] != stages["C_FINAL"][key]
            final_changed = stages["B"][key] != stages["C_FINAL"][key]
            segments = [name for name, changed in (("B_TO_C_STAGE2", changed_stage2), ("C_STAGE2_TO_C_FINAL", changed_stage3)) if changed]
            expected_before = expected_by_ship[ship]["before"][key]
            expected_after = expected_by_ship[ship]["after"][key]
            matches_existing = stages["B"][key] == expected_before and stages["C_FINAL"][key] == expected_after
            attributed = final_changed and bool(segments) and matches_existing
            gates["allEightFinalChangesAttributed"] &= attributed
            cause = "ASM_BEAM_LOS_STAGE2" if segments == ["B_TO_C_STAGE2"] else "CUE_A_STAGE3" if segments == ["C_STAGE2_TO_C_FINAL"] else "BOTH_STAGE2_AND_STAGE3"
            rows.append({
                "ship": ship,
                "check": check,
                "metric": key,
                "B": stages["B"][key],
                "C_STAGE2": stages["C_STAGE2"][key],
                "C_FINAL": stages["C_FINAL"][key],
                "changedIn": segments,
                "cause": cause,
                "matchesExistingBToFinalRecord": matches_existing,
                "attributed": attributed,
                "stage2ReplayExact": replay_exact,
                "safetyChecks": safety,
            })

    report = {
        "schema": "AEGIS_CUE_A_1_PAIRED_STAGE_ATTRIBUTION_1",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "policy": "No product or expected value changed. Truth is used only after the run for diagnostic attribution.",
        "products": {
            "B": {"sha256": sha(args.b)},
            "C_STAGE2": {"sha256": sha(args.stage2)},
            "C_FINAL": {"sha256": sha(args.final)},
        },
        "gates": gates,
        "rawRuns": [first_run["execution"], second_run["execution"]],
        "rows": rows,
        "assertionToleranceChanges": 0,
    }
    (HERE / "PAIRED_STAGE_ATTRIBUTION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = [
        "# Paired raid Stage attribution",
        "",
        f"- Status: `{report['status']}`",
        "- Product code changes in Stage 0: `0`",
        "- Expected-value/tolerance changes: `0 / 0`",
        "- Truth use: post-run diagnostic attribution only",
        "",
        "| Ship | Check | B | C Stage 2 | C final | Attributed change |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        def short(value: object) -> str:
            return value[:12] + "…" if isinstance(value, str) and len(value) > 16 else str(value)
        lines.append(f"| {row['ship']} | {row['check']} | {short(row['B'])} | {short(row['C_STAGE2'])} | {short(row['C_FINAL'])} | {', '.join(row['changedIn'])} |")
    lines += ["", "## Gate results", ""] + [f"- {key}: `{value}`" for key, value in gates.items()]
    (HERE / "PAIRED_STAGE_ATTRIBUTION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": report["status"], "gates": gates, "rows": len(rows)}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
