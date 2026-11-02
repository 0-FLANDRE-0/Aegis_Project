"""Run the frozen 60-case TRACK-C battle matrix on ASM_SEEKER_A.

The runner records compact native outcomes. Physical IDs are confined to the
unchanged TRACK-C after-action observer and are not consumed by gameplay.
"""
from pathlib import Path
from collections import Counter
import argparse, concurrent.futures, hashlib, importlib.util, json, os, subprocess, sys, time, traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIG = Path("/dev/shm/aegis-ciws-dmg-a")
OUT = HERE / "evidence/s3-battles"
OUT.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(ORIG / "docs/pip/B"), str(ORIG / "docs/helicopter/H"),
                str(ORIG / "docs/multiship/G"), str(ORIG / "docs/bunkerhill/K"),
                str(ORIG / "docs/missile/fuze-zem/A")]
import browser_backend
browser_backend.install()
from browser_i import launch, load
from browser_tools import instrument
from playwright.sync_api import sync_playwright


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else Path(value).read_bytes()).hexdigest()


def jobs():
    values = json.loads((ORIG / "docs/contact/track/B_statistics_r4/JOBS.json").read_text())
    return [{"id": f"{row['scenario']}-{row['seed']}-ASM", "scenario": row["scenario"],
             "seed": row["seed"], "case": row["case"]}
            for row in values if row["product"] == "R4"]


def helper():
    return (ORIG / "docs/contact/track/C/after_action.js").read_text() + "\n" + \
           (ORIG / "docs/contact/track/C/test_support/battle.js").read_text()


EXPR = """c=>{const r=__TRACK_STABLE_BATTLE__.run(c);return {
  status:r.status,end:r.end,qualification:r.qualification,counts:{launches:r.counts.launches,
  intercepts:r.counts.intercepts,phalanxHits:r.counts.phalanxHits,shipHitRecords:r.counts.shipHitRecords},
  targets:r.targets,ship:{hp:r.final.ship.shipHP,flooding:r.final.ship.damage.flooding},
  inventory:r.final.inventory,globalRng:r.final.globalRng,core:r.final.core,
  runtimeFault:r.final.runtimeFault,presentationFault:r.final.presentationFault,
  diagnostics:r.diagnostics,faults:r.faults,statisticalEndpoint:r.statisticalEndpoint};}"""


def native_cause(target):
    return (target.get("retirement") or {}).get("cause") or target.get("_deathReason") or \
           target.get("_wip113Outcome") or target.get("retiredReason")


def category(target):
    cause = native_cause(target)
    kills = {"INTERCEPT_KILL", "INTERCEPT_STRUCTURAL_FAILURE", "PHALANX_KILL",
             "DELAYED_STRUCTURAL_FAILURE", "WARHEAD_AIRBURST"}
    hits = {"NORMAL_HIT", "DUD_PENETRATION", "DAMAGED_HIT", "DEGRADED_HIT", "WARHEAD_DUD_HIT"}
    if target.get("alive") and (target.get("statisticalEgress") or {}).get("qualified"):
        return "EGRESS"
    if cause in kills:
        return "KILL"
    if cause in hits:
        return "LEAKER"
    return "OTHER"


def compact(job, value, wall):
    outcomes = [{"id": row["id"], "category": category(row), "cause": native_cause(row),
                 "egress": row.get("statisticalEgress")} for row in value["targets"]]
    counts = Counter(row["category"] for row in outcomes)
    flood = sum(cell.get("waterM3", 0) for cell in value["ship"]["flooding"]["cells"])
    return {"id": job["id"], "scenario": job["scenario"], "seed": job["seed"],
            "status": value["status"], "end": value["end"], "outcomes": outcomes,
            "kills": counts["KILL"], "leakers": counts["LEAKER"], "egress": counts["EGRESS"],
            "other": counts["OTHER"], "hpReferenceOnly": value["ship"]["hp"], "floodM3": flood,
            "counts": value["counts"], "inventory": value["inventory"], "globalRng": value["globalRng"],
            "post": {"coreZero": value["core"] == [], "runtimeFaultNull": value["runtimeFault"] is None,
                     "presentationFaultNull": value["presentationFault"] is None,
                     "faultsZero": value["faults"] == [], "noGameObjectsRetiredByTest": value["statisticalEndpoint"]["gameObjectsRetiredByTest"] == 0},
            "wallS": wall}


def worker(shard):
    product = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
    receipt = json.loads((HERE / "PRODUCT_BUILD.json").read_text())
    assert sha(product) == receipt["outputSha256"]
    inst = module(f"asm_s3_instrument_{shard}", ORIG / "docs/contact/track/C/instrument.py")
    probed, probe = inst.physical_probe(product.read_bytes())
    body = instrument(probed, helper())
    assigned = jobs()
    progress_path = OUT / f"shard-{shard}.json"
    if progress_path.exists():
        prior = json.loads(progress_path.read_text())
        rows = [row for row in prior.get("rows", []) if row.get("status") == "QUALIFYING_COMPLETED_BATTLE"]
    else:
        rows = []
    completed = {row["id"] for row in rows}
    errors = []
    started = time.monotonic()
    with sync_playwright() as pw:
        for index, job in enumerate(assigned, 1):
            if job["id"] in completed:
                continue
            at = time.monotonic(); page_errors = []; page = None
            browser = launch(pw)
            try:
                try:
                    page = load(browser, body, ship=job["case"]["ship"], errors=page_errors)
                    page.set_default_timeout(900000)
                    value = page.evaluate(EXPR, job["case"])
                    if page_errors or value["faults"]:
                        raise RuntimeError((page_errors, value["faults"]))
                    row = compact(job, value, time.monotonic() - at)
                except Exception as error:
                    row = {"id": job["id"], "status": "INCOMPLETE", "wallS": time.monotonic() - at,
                           "error": str(error), "traceback": traceback.format_exc()}
                    errors.append(row)
                finally:
                    if page is not None:
                        page.close()
                rows.append(row)
                progress_path.write_text(json.dumps({"probe": probe, "rows": rows, "errors": errors,
                                                      "elapsedS": time.monotonic() - started}, indent=2) + "\n")
                print(json.dumps({"shard": shard, "index": index, "planned": len(assigned),
                                  "id": row["id"], "status": row["status"], "wallS": row["wallS"]}), flush=True)
                if errors:
                    break
            finally:
                browser.close()
    return 0 if not errors else 1


def baseline_rows():
    statistics = json.loads((ORIG / "docs/contact/track/C/STATISTICS.json").read_text())
    return {
        f"{pair['scenario']}-{pair['seed']}-ASM": pair["C"]
        for pair in statistics["pairs"]
    }


def finalize(started, commands):
    shards = [json.loads((OUT / "shard-0.json").read_text())]
    rows = sorted([row for shard in shards for row in shard["rows"]], key=lambda row: (row["scenario"], row["seed"]))
    baseline = baseline_rows()
    comparisons = []
    for row in rows:
        prior = baseline.get(row["id"])
        comparisons.append({"id": row["id"], "baselineAvailable": prior is not None,
                            "before": None if prior is None else {key: prior[key] for key in ("kills", "leakers", "egress", "other", "damagingHitRounds", "floodM3", "hpReferenceOnly")},
                            "after": {key: row[key] for key in ("kills", "leakers", "egress", "other", "floodM3", "hpReferenceOnly")}})
    sum_keys = ("kills", "leakers", "egress", "other")
    result = {"schema": "AEGIS_ASM_SEEKER_A_S3_BATTLE_RESULTS_1",
              "status": "PASS" if len(rows) == 60 and all(row["status"] == "QUALIFYING_COMPLETED_BATTLE" and all(row["post"].values()) for row in rows) else "INCOMPLETE",
              "productSha256": json.loads((HERE / "PRODUCT_BUILD.json").read_text())["outputSha256"],
              "jobs": len(rows), "expectedJobs": 60,
              "elapsedS": sum(row["wallS"] for row in rows),
              "currentResumeWallS": time.monotonic() - started,
              "commands": commands,
              "totals": {key: sum(row[key] for row in rows) for key in sum_keys},
              "baselineAvailable": len(baseline),
              "baselineTotals": {key: sum(value[key] for value in baseline.values()) for key in sum_keys},
              "rows": rows, "comparisons": comparisons,
              "physicalProbe": [shard["probe"] for shard in shards]}
    (HERE / "S3_BATTLE_RESULTS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "jobs", "elapsedS", "totals", "baselineAvailable", "baselineTotals")}, indent=2))
    return 0 if result["status"] == "PASS" else 1


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--worker", type=int)
    args = parser.parse_args()
    if args.worker is not None:
        return worker(args.worker)
    started = time.monotonic(); commands = []
    processes = []
    for shard in range(1):
        log = OUT / f"shard-{shard}.log"
        command = [sys.executable, "-u", str(Path(__file__).resolve()), "--worker", str(shard)]
        handle = log.open("w")
        process = subprocess.Popen(command, cwd=ROOT, env={**os.environ, "TMPDIR": "/dev/shm", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=handle, stderr=subprocess.STDOUT)
        processes.append((process, handle)); commands.append(command)
    codes = []
    for process, handle in processes:
        codes.append(process.wait()); handle.close()
    if any(codes):
        raise SystemExit(codes)
    return finalize(started, commands)


if __name__ == "__main__":
    raise SystemExit(main())
