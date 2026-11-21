#!/usr/bin/env python3
"""One-shot MAX_THREAT broad regression for DEFENSE_OODA_A."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE_RUNNER = ROOT / "docs/ooda/integration-baseline/A/run_final_regression.py"
spec = importlib.util.spec_from_file_location("integration_final_runner", BASE_RUNNER)
base = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

PRODUCT = ROOT / "Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html"
BASELINE = ROOT / "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html"
PRODUCT_BYTES = 22_226_343
PRODUCT_SHA256 = "1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d"
BASELINE_BYTES = 22_212_299
BASELINE_SHA256 = "655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0"
HELI_CG_A = ROOT / "archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html"
HELI_CG_A_BYTES = 16_078_336
HELI_CG_A_SHA256 = "c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3"
OUT = HERE / "evidence/final-regression"
SUMMARY = HERE / "FINAL_REGRESSION.json"
NATIVE = base.NATIVE
SUITES = [*NATIVE, "paired-integration", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "u4-seeker-scenes", "hp-contract", "seeker-close"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def environment() -> dict[str, str]:
    return {
        **os.environ, "TMPDIR": "/dev/shm", "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": os.environ.get("NODE_PATH", str(ROOT / "node_modules")),
        "B2_PHASE1_REGRESSION": "1", "B2_MODE": "ON", "B2_HTML": str(PRODUCT),
        "B2_OUT": str(OUT), "PYTHONPATH": str(ROOT / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0", "THREAT_ASSUMPTION_MODE": "MAX_THREAT",
    }


def command(name: str) -> list[str]:
    if name in NATIVE:
        return [sys.executable, "-u", str(ROOT / "docs/pip/B/run_domain.py"), str(PRODUCT), str(OUT / name), "--only", name]
    if name == "paired-integration":
        return [sys.executable, "-u", str(ROOT / "docs/helicopter/F/verify_regression.py"), str(BASELINE), str(PRODUCT), str(OUT / name), "--baseline-only", "--exclude-defense-ooda-a"]
    if name == "paired-determinism":
        return [sys.executable, "-u", str(ROOT / "docs/helicopter/F/verify_regression.py"), str(PRODUCT), str(PRODUCT), str(OUT / name), "--baseline-only"]
    if name == "current-emcon-ui":
        return [sys.executable, "-u", str(ROOT / "docs/map/E/verify_emcon_ui.py"), str(PRODUCT), str(OUT / name)]
    if name == "ui213":
        return [sys.executable, "-u", str(ROOT / "docs/contact/friendly/A/cpu2d_ui.py")]
    if name == "webgl8":
        return [sys.executable, "-u", str(ROOT / "docs/envelope/D/run_observed_webgl.py"), str(PRODUCT), str(OUT / name)]
    if name == "u4-seeker-scenes":
        return [sys.executable, "-u", str(ROOT / "docs/ooda/integration-baseline/A/run_u4_scenes_candidate.py"), str(PRODUCT), str(OUT / name / "scenes.json")]
    if name == "hp-contract":
        return [sys.executable, "-u", str(ROOT / "docs/damage/hp/A/run_contract_gate.py"), str(PRODUCT), str(OUT / name / "contract-gate.json")]
    if name == "seeker-close":
        return [sys.executable, "-u", str(ROOT / "docs/ooda/integration-baseline/A/run_seeker_close_candidate.py"), str(PRODUCT), str(OUT / name)]
    raise ValueError(name)


def result_location(name: str) -> tuple[Path, int]:
    if name in NATIVE:
        return OUT / name / NATIVE[name][0], NATIVE[name][1]
    if name in {"paired-integration", "paired-determinism"}:
        return OUT / name / "baseline-comparison.json", 42
    if name == "current-emcon-ui":
        return OUT / name / "ui.json", 14
    if name == "ui213":
        return OUT / "map/E/evidence/d-ui/ui.json", 213
    if name == "webgl8":
        return OUT / name / "observed-world.json", 29
    if name == "u4-seeker-scenes":
        return OUT / name / "scenes.json", 19
    if name == "hp-contract":
        return OUT / name / "contract-gate.json", 19
    if name == "seeker-close":
        return OUT / name / "SUMMARY.json", 26
    raise ValueError(name)


# Reuse the audited execution/extraction implementation with this frozen input.
base.PRODUCT, base.BASELINE, base.OUT, base.SUMMARY = PRODUCT, BASELINE, OUT, SUMMARY
base.PRODUCT_BYTES, base.PRODUCT_SHA256 = PRODUCT_BYTES, PRODUCT_SHA256
base.BASELINE_BYTES, base.BASELINE_SHA256 = BASELINE_BYTES, BASELINE_SHA256
base.HELI_CG_A, base.command, base.result_location, base.environment = HELI_CG_A, command, result_location, environment


def static_integrity() -> dict:
    load=lambda name:json.loads((HERE/name).read_text())
    active=load("D_ACTIVE_GATE.json"); contract=load("D_CONTRACT_GATE.json"); engine=load("D_ENGINE_GATE.json")
    hashes=load("D_FUNCTION_HASH_GATE.json"); boundary=load("D_BOUNDARY_STATIC_GATE.json"); shadow=load("C_SHADOW_GATE_ATTEMPT_7.json")
    final_samples=[scene["result"]["samples"][-1] for scene in active["scenes"]]
    checks={
        "productBytesPinned":PRODUCT.stat().st_size==PRODUCT_BYTES,
        "productShaPinned":sha256(PRODUCT.read_bytes())==PRODUCT_SHA256,
        "activeGatePass":active.get("pass") is True,
        "activeGateProductPinned":active.get("product",{}).get("sha256")==PRODUCT_SHA256,
        "contractGatePass":contract.get("pass") is True,
        "contractGateProductPinned":contract.get("product",{}).get("sha256")==PRODUCT_SHA256,
        "engineGatePass":engine.get("pass") is True,
        "engineGateProductPinned":engine.get("product",{}).get("sha256")==PRODUCT_SHA256,
        "functionHashGatePass":hashes.get("status")=="PASS",
        "protectedExact30":hashes.get("checks",{}).get("integrationProtectedExact30") is True,
        "onlySaveExportProtectedChange":hashes.get("protected",{}).get("integrationToDChanged")==["exportOperationalState"],
        "boundaryStaticPass":boundary.get("status")=="PASS" and all(boundary.get("checks",{}).values()),
        "shadowGatePass":shadow.get("pass") is True,
        "activeProviderExact":all(scene["result"]["provider"]["provider"]=="DEFENSE_OODA_A" and scene["result"]["provider"]["mode"]=="ACTIVE" for scene in active["scenes"]),
        "fallbackZero":all(sample[side]["diagnostics"]["fallback"]==0 for sample in final_samples for side in ("ownOoda","allyOoda")),
        "rejectedZero":all(sample[side]["diagnostics"]["rejected"]==0 for sample in final_samples for side in ("ownOoda","allyOoda")),
        "truthRngValidationZero":all(sample[side][key]==0 for sample in final_samples for side in ("ownDiagnostics","allyDiagnostics") for key in ("validationFailures","rngMismatchCount","truthAuditFailures")),
        "readOnlyUi":all(scene["result"]["ui"]["readOnly"] for scene in active["scenes"]),
        "manualHoldNoLaunch":all(scene["result"]["manualHold"]["manualMissileDelta"]==0 and scene["result"]["manualHold"]["foreignFireDelta"]==0 for scene in active["scenes"]),
        "activeRepeatExact":active.get("checks",{}).get("repeatExact") is True,
    }
    failed=[key for key,value in checks.items() if not value]
    payload={"schema":"AEGIS_DEFENSE_OODA_A_FINAL_STATIC_1","checks":checks,"errors":[],"failed":failed}
    path=OUT/"static-integrity.json";path.write_text(strict(payload))
    return {"suite":"static-integrity","status":"PASS" if not failed else "FAIL","exitCode":0 if not failed else 1,"wallS":0,"expectedAssertions":len(checks),"executedAssertions":len(checks),"passedAssertions":sum(checks.values()),"failedAssertions":failed,"errors":[],"resultPath":str(path.relative_to(OUT))}


def source_provenance() -> None:
    files=[ROOT/p for p in [
        "docs/pip/B/run_domain.py","docs/map/E/verify_emcon_ui.py","docs/contact/friendly/A/cpu2d_ui.py",
        "docs/envelope/D/run_observed_webgl.py","docs/helicopter/F/verify_regression.py","docs/damage/hp/A/run_contract_gate.py",
        "docs/ooda/integration-baseline/A/run_u4_scenes_candidate.py","docs/ooda/integration-baseline/A/run_seeker_close_candidate.py",
        "docs/ooda/integration-baseline/A/build_seeker_close_diagnostic.py","docs/ooda/defense/A/defense_ooda_patch.py",
        "docs/ooda/defense/A/defense_ooda_runtime.js","docs/ooda/defense/A/defense_ooda_ui.js","docs/ooda/defense/A/active_oracle.cjs",
    ]]
    payload={"schema":"AEGIS_DEFENSE_OODA_A_FINAL_SOURCE_PROVENANCE_1","candidateSha256":PRODUCT_SHA256,"candidateBytes":PRODUCT_BYTES,"baselineSha256":BASELINE_SHA256,"threatMode":"MAX_THREAT","runCount":1,"expectedValuesUpdated":False,"tolerancesChanged":False,"gameConstantsChanged":False,"files":[{"path":str(p.relative_to(ROOT)),"sha256":sha256(p.read_bytes())} for p in files]}
    (OUT/"source-provenance.json").write_text(strict(payload))


def write_summary(rows: list[dict], started: float, complete: bool) -> dict:
    failures=[row["suite"] for row in rows if row["status"]!="PASS"]
    native=[row for row in rows if row["suite"] in NATIVE]
    result={
        "schema":"AEGIS_DEFENSE_OODA_A_FINAL_REGRESSION_1","complete":complete,
        "candidate":PRODUCT.name,"candidateSha256":PRODUCT_SHA256,"candidateBytes":PRODUCT_BYTES,
        "baseline":BASELINE.name,"baselineSha256":BASELINE_SHA256,"threatAssumptionMode":"MAX_THREAT",
        "broadRun":{"runCount":1,"oneShot":True,"candidateFrozen":True},
        "expectedValuesUpdated":False,"tolerancesChanged":False,"gameConstantsChanged":False,"rows":rows,
        "native13":{"suiteCount":len(native),"expectedSuiteCount":13,"expectedAssertions":364,"executedAssertions":sum(r["executedAssertions"] for r in native),"passedAssertions":sum(r["passedAssertions"] for r in native)},
        "coverage":{"defenseOoda":"static-integrity + D ACTIVE/contract/engine gates","pairedDdgCg":["paired-integration","paired-determinism"],"hpOutcomeSave":"hp-contract","seekerCloseNineteenShots":"seeker-close","representativeRealFlights":["u4-seeker-scenes","harpoon-f1"],"emconAndEsm":["current-emcon-ui","seeker-close"],"browserUi":"ui213","actualWebgl":"webgl8"},
        "pairedNormalization":{"excludedField":"defenseOodaA","scope":"new owner-local decision phase only","separateContractEvidence":"D_CONTRACT_GATE.json"},
        "confirmedOnly":{"staticAndLimitedFeatureOffEvidence":"INHERITED_PASS","performance":"UNVERIFIED"},
        "inheritedDebt":["CIWS_SEED_419025_FAIL","CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2","WIP12D_CIWS_FIXED_STEP_SCALE_DEBT","CHROMIUM_MEMORY_CRASH_AND_CHECKOUT_TIMEOUT_DEBT","KH32_60KM_POPULATION_NOT_RUN","CONFIRMED_ONLY_PERFORMANCE_UNVERIFIED","LEGACY_SARH_SELFTEST_DIAGNOSTIC_DEBT"],
        "effectiveFailures":failures,"wallS":time.perf_counter()-started,"release":False,
    }
    SUMMARY.write_text(strict(result));return result


def tracked_paths(prefix: str) -> list[Path]:
    output=subprocess.check_output(["git","ls-tree","-r","-z","--name-only","HEAD","--",prefix],cwd=ROOT)
    return [ROOT/value.decode() for value in output.split(b"\0") if value]


def preflight() -> dict:
    native_sources=[ROOT/path for path in [
        "docs/helicopter/J/verify_native.py","docs/helicopter/G/verify_native.py","docs/helicopter/L/verify_native.py",
        "docs/helicopter/L/verify_classes.py","docs/helicopter/L/verify_clock.py","docs/helicopter/L/verify_ui.py",
        "docs/helicopter/K/verify_native.py","docs/helicopter/H/verify_native.py","docs/helicopter/H/verify_ui_clock.py",
        "docs/sovremenny/A/verify_native.py","docs/sovremenny/A/verify_casualty.py","docs/sovremenny/A/verify_deployment.py","docs/sovremenny/A/verify_visual.py",
    ]]
    required=[PRODUCT,BASELINE,HELI_CG_A,ROOT/"docs/multiship/G/browser_g.py",ROOT/"docs/missile/fuze-zem/A/browser_tools.py",ROOT/"docs/pip/B/run_domain.py",ROOT/"docs/pip/B/browser_backend.py",ROOT/"docs/map/A/verify_regressions.py",ROOT/"docs/viewport/A/verify_regressions.py",ROOT/"docs/helicopter/H/browser.py",ROOT/"docs/map/E/verify_emcon_ui.py",ROOT/"docs/contact/friendly/A/cpu2d_ui.py",ROOT/"docs/envelope/D/run_observed_webgl.py",ROOT/"docs/helicopter/F/verify_regression.py",ROOT/"docs/damage/hp/A/run_contract_gate.py",ROOT/"docs/ooda/integration-baseline/A/run_u4_scenes_candidate.py",ROOT/"docs/ooda/integration-baseline/A/run_seeker_close_candidate.py",ROOT/"docs/ooda/integration-baseline/A/build_seeker_close_diagnostic.py",HERE/"defense_ooda_patch.py",HERE/"defense_ooda_runtime.js",HERE/"defense_ooda_ui.js",HERE/"active_oracle.cjs",HERE/"D_ACTIVE_GATE.json",HERE/"D_CONTRACT_GATE.json",HERE/"D_ENGINE_GATE.json",HERE/"D_FUNCTION_HASH_GATE.json",HERE/"D_BOUNDARY_STATIC_GATE.json",*native_sources]
    tracked_docs=tracked_paths("docs")
    tracked_tests=tracked_paths("tests")
    missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    missing_tracked=[str(p.relative_to(ROOT)) for p in [*tracked_docs,*tracked_tests] if not p.exists()]
    sparse=subprocess.check_output(["git","sparse-checkout","list"],cwd=ROOT,text=True).splitlines()
    suite_inputs={}
    for name in SUITES:
        script=next(Path(v) for v in command(name)[1:] if str(v).endswith(".py"));inputs=[PRODUCT,script]
        if name in NATIVE:inputs.extend([ROOT/"docs/pip/B/browser_backend.py",ROOT/"docs/map/A/verify_regressions.py",ROOT/"docs/viewport/A/verify_regressions.py",native_sources[list(NATIVE).index(name)]])
        if name=="helicopter-flight":inputs.append(HELI_CG_A)
        if name=="paired-integration":inputs.append(BASELINE)
        suite_inputs[name]=sorted({str(p.relative_to(ROOT)) for p in inputs})
    with tempfile.TemporaryDirectory(prefix="defense-ooda-preflight-") as td:
        rebuilt=Path(td)/"rebuilt.html";js=Path(td)/"rebuilt.js"
        build=subprocess.run([sys.executable,str(HERE/"defense_ooda_patch.py"),str(BASELINE),str(rebuilt),"--stage","D","--js-output",str(js)],cwd=ROOT,capture_output=True,text=True)
        syntax=subprocess.run(["node","--check",str(js)],cwd=ROOT,capture_output=True,text=True) if js.exists() else None
        rebuild_exact=build.returncode==0 and rebuilt.read_bytes()==PRODUCT.read_bytes();syntax_ok=syntax is not None and syntax.returncode==0
    d_evidence=[json.loads((HERE/name).read_text()) for name in ["D_ACTIVE_GATE.json","D_CONTRACT_GATE.json","D_ENGINE_GATE.json"]]
    checks={
        "branchExact":subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()=="defense-ooda-a",
        "productBytesPinned":PRODUCT.is_file() and PRODUCT.stat().st_size==PRODUCT_BYTES,
        "productShaPinned":PRODUCT.is_file() and sha256(PRODUCT.read_bytes())==PRODUCT_SHA256,
        "baselineBytesPinned":BASELINE.is_file() and BASELINE.stat().st_size==BASELINE_BYTES,
        "baselineShaPinned":BASELINE.is_file() and sha256(BASELINE.read_bytes())==BASELINE_SHA256,
        "heliCgFixturePinned":HELI_CG_A.is_file() and HELI_CG_A.stat().st_size==HELI_CG_A_BYTES and sha256(HELI_CG_A.read_bytes())==HELI_CG_A_SHA256,
        "allExplicitInputsPresent":not missing,
        "allTrackedDocsMaterialized":not [p for p in missing_tracked if p.startswith("docs/")],
        "allTrackedTestsMaterialized":not [p for p in missing_tracked if p.startswith("tests/")],
        "heliCgFixtureInSparseCheckout":"/archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html" in sparse,
        "suiteCountExact":len(suite_inputs)==21,
        "expectedAssertionCountsExact":sum(result_location(name)[1] for name in SUITES)==768,
        "builderRebuildBytesExact":rebuild_exact,
        "packedJavascriptSyntax":syntax_ok,
        "dEvidencePinned":all(q.get("pass") is True and q.get("product",{}).get("sha256")==PRODUCT_SHA256 for q in d_evidence),
        "chromiumPresent":Path("/usr/bin/chromium").is_file(),
        "playwrightPresent":subprocess.run(["node","-e","require('playwright')"],cwd=ROOT,env=environment(),capture_output=True).returncode==0,
        "outputUnused":not OUT.exists() or not any(OUT.iterdir()),
    }
    payload={"schema":"AEGIS_DEFENSE_OODA_A_FINAL_PREFLIGHT_1","checks":checks,"candidate":{"path":str(PRODUCT.relative_to(ROOT)),"bytes":PRODUCT_BYTES,"sha256":PRODUCT_SHA256},"baseline":{"path":str(BASELINE.relative_to(ROOT)),"bytes":BASELINE_BYTES,"sha256":BASELINE_SHA256},"indirectFixture":{"path":str(HELI_CG_A.relative_to(ROOT)),"bytes":HELI_CG_A_BYTES,"sha256":HELI_CG_A_SHA256},"sparseCheckoutPatterns":sparse,"trackedMaterialization":{"docsCount":len(tracked_docs),"testsCount":len(tracked_tests),"missing":missing_tracked},"suiteInputs":suite_inputs,"missingExplicitInputs":missing,"expectedValuesUpdated":False,"tolerancesChanged":False,"gameConstantsChanged":False}
    failed=[name for name,value in checks.items() if not value]
    if failed:raise AssertionError(f"DEFENSE_OODA_A preflight failed: {failed}; missing={missing}; tracked={missing_tracked[:20]}")
    return payload


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--dry-run",action="store_true");args=parser.parse_args();preflight_result=preflight()
    if args.dry_run:
        print(strict({"product":str(PRODUCT),"productBytes":PRODUCT_BYTES,"productSha256":PRODUCT_SHA256,"output":str(OUT),"oneShot":True,"preflight":preflight_result,"jobs":{name:command(name) for name in SUITES},"broadRunCountOnDryRun":0}));return
    OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir()),"final broad regression is one-shot; output directory must be empty"
    (OUT/"preflight-inputs.json").write_text(strict(preflight_result));started=time.perf_counter();rows=[static_integrity()];source_provenance();write_summary(rows,started,False)
    for name in SUITES:
        row=base.execute(name);rows.append(row);write_summary(rows,started,False)
        if row["executedAssertions"]==0:raise SystemExit(f"zero-assertion suite: {name}")
        if row["status"]!="PASS":raise SystemExit(f"broad regression stopped on failure: {name}")
    result=write_summary(rows,started,True);raise SystemExit(1 if result["effectiveFailures"] else 0)


if __name__=="__main__":
    main()
