#!/usr/bin/env python3
"""Replay the frozen TRACK-C 37 egress missiles against Stage 2."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = HERE / "evidence/beam-stage2-egress-37"
EVIDENCE.mkdir(parents=True, exist_ok=True)
ORIG = Path("/dev/shm/seeker-unify-track-c")
sys.path[:0] = [
    "/dev/shm/seeker-unify-track-c/docs/missile/fuze-zem/A",
    "/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
    "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
    "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
    "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K",
    "/dev/shm/aegis-ciws-dmg-a/docs/missile/fuze-zem/A",
]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from browser_tools import instrument
from playwright.sync_api import sync_playwright


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(result)
    return result


def sha(value) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else Path(value).read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def jobs() -> list[dict]:
    lineage = json.loads((ROOT / "docs/contact/track/C/LINEAGE_RESULTS.json").read_text())
    source = json.loads((ROOT / "docs/contact/track/B_statistics_r4/JOBS.json").read_text())
    cases = {(row["scenario"], row["seed"]): row["case"] for row in source if row["product"] == "R4"}
    output = []
    for row in lineage["rows"]:
        if row["product"] != "C" or not row["egress"]:
            continue
        scenario, seed, _ = row["id"].split("-")
        focus = [item["id"] for item in row["egress"]]
        case = {**cases[(scenario, int(seed))], "checkpointSeconds": [], "asmSeekerFocusIds": focus, "lineageOn": True}
        output.append({"id": row["id"], "scenario": scenario, "seed": int(seed), "focusIds": focus, "prior": row["egress"], "case": case})
    return output


def helper() -> str:
    source = (ORIG / "docs/contact/track/C/test_support/battle.js").read_text()
    needle = "  window.__TRACK_C_AA_INTERNAL__?.begin({record:c.lineageOn!==false});"
    assert source.count(needle) == 1
    source = source.replace(needle, "  window.__ASM_SEEKER_A_DIAG__.beginBattle(c.asmSeekerFocusIds??[]);\n" + needle, 1)
    needle = "  const trackCLineage=window.__TRACK_C_AA_INTERNAL__?.finish()??null;"
    assert source.count(needle) == 1
    source = source.replace(needle, needle + "\n  const asmSeekerADiagnostic=window.__ASM_SEEKER_A_DIAG__.finishBattle();", 1)
    needle = "  return {trackCLineage,schema:"
    assert source.count(needle) == 1
    source = source.replace(needle, "  return {trackCLineage,asmSeekerADiagnostic,schema:", 1)
    return (ORIG / "docs/contact/track/C/after_action.js").read_text() + "\n" + source


EXPRESSION = """c=>{const r=__TRACK_STABLE_BATTLE__.run(c),focus=new Set(c.asmSeekerFocusIds);return {schema:'AEGIS_SEEKER_UNIFY_C_STAGE2_EGRESS_REPLAY_1',case:r.case,status:r.status,end:r.end,qualification:r.qualification,targets:r.targets.filter(q=>focus.has(q.id)),events:r.events.filter(q=>(q.kind==='AFTER_ACTION_ASM_STATE'&&focus.has(q.target?.id))||q.kind==='NATIVE_PHALANX_HIT'||q.kind==='NATIVE_INTERCEPT_RESULT'||q.kind==='NATIVE_SHIP_HIT_RECORD'),asm:r.asmSeekerADiagnostic,lineage:r.trackCLineage?{seeker:r.trackCLineage.seeker.filter(q=>focus.has(q.id)),faults:r.trackCLineage.faults,dropped:r.trackCLineage.dropped}:null,final:{globalRng:r.final.globalRng,core:r.final.core,runtimeFault:r.final.runtimeFault,presentationFault:r.final.presentationFault},faults:r.faults};}"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostic", type=Path, default=Path("/dev/shm/seeker_c_stage2_asm_diag.html"))
    parser.add_argument("--build-receipt", type=Path, default=HERE / "BEAM_STAGE2_ASM_DIAGNOSTIC_BUILD.json")
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--plan", type=Path, default=HERE / "BEAM_STAGE2_EGRESS_37_PLAN.json")
    parser.add_argument("--progress", type=Path, default=HERE / "BEAM_STAGE2_EGRESS_37_PROGRESS.json")
    parser.add_argument("--out", type=Path, default=HERE / "BEAM_STAGE2_EGRESS_37_RESULTS.json")
    args = parser.parse_args()
    diagnostic = args.diagnostic
    build = json.loads(args.build_receipt.read_text())
    assert sha(diagnostic) == build["outputSha256"]
    inst = module("seeker_unify_c_stage2_track_instrument", ORIG / "docs/contact/track/C/instrument.py")
    probed, probe = inst.physical_probe(diagnostic.read_bytes())
    support = helper()
    body = instrument(probed, support)
    plan_jobs = jobs()
    plan = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE2_EGRESS_REPLAY_PLAN_1",
        "inputHtml": diagnostic.name,
        "inputSha256": sha(diagnostic),
        "instrumentedSha256": sha(body),
        "physicalProbe": probe,
        "helperSha256": sha(support.encode()),
        "jobs": plan_jobs,
        "jobCount": len(plan_jobs),
        "missileCount": sum(len(row["focusIds"]) for row in plan_jobs),
        "productCodeChanged": False,
        "truthUse": "AFTER_ACTION_ONLY",
    }
    save(args.plan, plan)
    args.evidence.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.monotonic()
    with sync_playwright() as pw:
        for job in plan_jobs:
            path = args.evidence / (job["id"] + ".json.gz")
            if path.exists():
                data = json.loads(gzip.decompress(path.read_bytes()))
                rows.append({"id": job["id"], "status": "CACHED", "sha256": sha(path), "targets": data["targets"], "end": data["end"]})
                continue
            errors: list[str] = []
            at = time.monotonic()
            browser = launch(pw)
            try:
                page = load(browser, body, ship=job["case"]["ship"], errors=errors)
                page.set_default_timeout(900000)
                data = page.evaluate(EXPRESSION, job["case"])
                assert not errors and not data["faults"] and not data["asm"]["faults"] and not data["lineage"]["faults"], (errors, data["faults"], data["asm"]["faults"], data["lineage"]["faults"])
                assert data["final"]["core"] == [] and data["final"]["runtimeFault"] is None
                blob = gzip.compress(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode(), 9, mtime=0)
                path.write_bytes(blob)
                row = {"id": job["id"], "status": "VALID", "sha256": hashlib.sha256(blob).hexdigest(), "wallS": time.monotonic() - at, "targets": data["targets"], "end": data["end"]}
            except Exception as exc:
                row = {"id": job["id"], "status": "INCOMPLETE", "wallS": time.monotonic() - at, "error": str(exc), "traceback": traceback.format_exc()}
            finally:
                browser.close()
            rows.append(row)
            save(args.progress, {"completed": len(rows), "planned": len(plan_jobs), "elapsedS": time.monotonic() - started, "rows": rows})
            print(json.dumps({name: row.get(name) for name in ("id", "status", "wallS", "error")}), flush=True)
            if row["status"] != "VALID":
                break
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE2_EGRESS_REPLAY_RESULTS_1",
        "status": "PASS" if len(rows) == len(plan_jobs) and all(row["status"] in {"VALID", "CACHED"} for row in rows) else "INCOMPLETE",
        "inputSha256": sha(diagnostic), "instrumentedSha256": sha(body),
        "jobs": len(plan_jobs), "missiles": sum(len(row["focusIds"]) for row in plan_jobs),
        "elapsedS": time.monotonic() - started, "rows": rows,
    }
    save(args.out, result)
    print(json.dumps({"status": result["status"], "jobs": result["jobs"], "missiles": result["missiles"], "elapsedS": result["elapsedS"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
