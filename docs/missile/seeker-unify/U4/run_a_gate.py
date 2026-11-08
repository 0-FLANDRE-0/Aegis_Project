#!/usr/bin/env python3
"""Commit A limited SARH SHADOW -> ACTIVE gate (no broad regression)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


SYNTHETIC = r"""()=>{
 const api=window.__SEEKER_U4_A__,powerRows=[
  [1,20,8,.9,.8,.95,.94,.85],[2.5,.25,.25,1,1,1,1,1],[.1,100,30,.02,.4,.2,.7,.5],
  [10,60,40,0,1,1,1,1],[10,60,40,1,0,1,1,1],[10,60,40,1,1,0,1,1],[10,60,40,1,1,1,0,1]
 ].map(args=>{const legacy=api.legacyBistaticPower(...args),common=api.bistaticPower(...args),routed=api.routedBistaticPower(...args);return {args,legacy,common,routed,equal:Object.is(legacy,common)&&Object.is(legacy,routed)};}),
 echo={rangeM:8000,txRangeM:20000,rxRangeM:8000,azRad:.2,elRad:-.01,dopplerPathRateMps:-320,receivedPowerNorm:.4,snr:12,rcsM2:1.2,txLosQ:.9,rxLosQ:.8,txBeamGain:.7,mountGain:.9,rxBeamGain:.6,rangeExtentM:10,crossExtentM:3,verticalExtentM:2,dopplerSpreadMps:4,_debugSourceId:'MUST_NOT_ESCAPE',_debugSourceKind:'AIRCRAFT'},
 dto=api.adaptEcho(echo,0),blocked=['txLosQ','rxLosQ','txBeamGain','rxBeamGain'].map(key=>{const q={...echo,[key]:0};return {key,valid:api.adaptEcho(q,0).valid};}),
 meas=api.adaptMeasurement({rangeM:8000,azRad:.2,elRad:-.01,dopplerPathRateMps:-320,rangeSigmaM:20,azSigmaDeg:.2,elSigmaDeg:.25,dopplerSigmaMps:4,snr:8,pd:.8}),
 nearA={...echo},nearB={...echo,rangeM:echo.rangeM+10,azRad:echo.azRad+Math.PI/180*.01,dopplerPathRateMps:echo.dopplerPathRateMps+1},
 farB={...echo,rangeM:echo.rangeM+1000000},unresolved={near:api.unresolved(nearA,nearB),far:api.unresolved(nearA,farB)},
 snap=api.snapshot(),keys=JSON.stringify(dto),checks={powerBitEqual:powerRows.every(q=>q.equal),validBistaticEcho:dto.valid&&dto.pathRangeM===28000&&dto.txLeg.rangeM===20000&&dto.rxLeg.rangeM===8000,
 noTruthOrDebug:/MUST_NOT_ESCAPE|debugSource|sourceId|entityId|targetId|profileId|faction|truthPosition/.test(keys)===false,
 twoLosAndBeamFailClosed:blocked.every(q=>q.valid===false),measurement4D:meas.dimension==='SARH_BISTATIC_4D'&&meas.values.length===4&&meas.covariance.length===16,
 cellPolicy:unresolved.near===true&&unresolved.far===false,rngFree:snap.rngConsumedByCommonLayer===false,truthFree:snap.truthOutput===false};
 return {mode:api.mode,profile:api.profile,powerRows,dto,blocked,meas,unresolved,snapshot:snap,checks,pass:Object.values(checks).every(Boolean)};
}"""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_product(pw, path: Path, with_adapter: bool, repeat_live: bool = False) -> dict:
    body = path.read_bytes(); errors: list[str] = []; browser = launch(pw)
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", seed=0xA40001, errors=errors)
    core = page.evaluate("()=>Array.from(window.__CORE_SELFTEST_FAILURES__??[])")
    fixture = page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip13c5SurfaceSarhFixture({rangeKm:8})")
    live = page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip13c5SurfaceSarhLiveFlightFixture({seed:1350501,rangeKm:8,maxTimeS:125})")
    synthetic = page.evaluate(SYNTHETIC) if with_adapter else None
    static = page.evaluate("()=>__SEEKER_U4_A__.sourceContract()") if with_adapter else None
    page.close(); browser.close()
    # The live fixture restores the tactical world but intentionally leaves some
    # diagnostic allocator state advanced.  Determinism therefore means two
    # identical fresh-page runs, not two sequential calls in one page.
    repeat = None
    if repeat_live:
        repeat_errors: list[str] = []
        repeat_browser = launch(pw)
        repeat_page = load(repeat_browser, body, ship="DDG_119_LATE_FLIGHT_IIA", seed=0xA40001, errors=repeat_errors)
        repeat = repeat_page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip13c5SurfaceSarhLiveFlightFixture({seed:1350501,rangeKm:8,maxTimeS:125})")
        repeat_page.close(); repeat_browser.close(); errors.extend(repeat_errors)
    return {"path": path.name, "sha256": sha(path), "fixture": fixture, "live": live, "repeat": repeat,
            "deterministic": (live == repeat) if repeat_live else None, "core": core, "synthetic": synthetic, "static": static, "errors": errors}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--shadow", type=Path, required=True)
    ap.add_argument("--active", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_product(pw, args.baseline, False)
        shadow = run_product(pw, args.shadow, True)
        active = run_product(pw, args.active, True, repeat_live=True)
    fixture_contract = (
        "liveManualRelease", "automaticSurfaceDenied", "spgReservationCommitted",
        "commonReflectorRegistry", "seaClutterSharesEchoChain",
        "surfaceReturnSharesEchoChain", "localSarhTrack",
        "measurementOnlyGuidance",
    )
    checks = {
        # This fixture also carries surface-contact/damage checks that are not
        # expected to pass in its short RF-only setup.  Commit A gates the SARH
        # observation contract explicitly and separately from those fields.
        "baselineFixtureContract": all(baseline["fixture"].get("checks", {}).get(k) is True for k in fixture_contract),
        "shadowFixtureEqual": shadow["fixture"] == baseline["fixture"],
        "activeFixtureEqual": active["fixture"] == baseline["fixture"],
        "baselineLivePass": baseline["live"].get("pass") is True,
        "shadowLiveEqual": shadow["live"] == baseline["live"],
        "activeLiveEqual": active["live"] == baseline["live"],
        "activeRepeatedInputDeterministic": active["deterministic"] is True,
        "shadowContract": bool(shadow["synthetic"] and shadow["synthetic"].get("pass") and shadow["synthetic"].get("mode") == "SHADOW"),
        "activeContract": bool(active["synthetic"] and active["synthetic"].get("pass") and active["synthetic"].get("mode") == "ACTIVE"),
        "activeTacticalRoute": active["synthetic"]["snapshot"].get("tacticalOutputUsed") is True,
        "powerAndCellBitEqual": active["synthetic"]["snapshot"].get("powerMismatches") == 0 and active["synthetic"]["snapshot"].get("unresolvedMismatches") == 0,
        "illuminationGeometryStatic": all(active["static"].values()),
        "coreSelfTests": all(q["core"] == [] for q in (baseline, shadow, active)),
        "pageErrorsZero": not any(q["errors"] for q in (baseline, shadow, active)),
    }
    result = {"schema":"AEGIS_SEEKER_UNIFY_U4_A_GATE_1","status":"PASS" if all(checks.values()) else "FAIL",
      "elapsedS":time.monotonic()-started,"broadRegressionRun":False,"representativeBranchesPerMode":11,"checks":checks,
      "baseline":baseline,"shadow":shadow,"active":active,"release":False}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"elapsedS":result["elapsedS"],"checks":checks,
      "fixture":active["fixture"].get("rf"),"live":{k:active["live"].get(k) for k in ("pass","deathReason","maxSarhEchoes","maxSarhMeasurements","sawSarhAuthority")},"audit":active["synthetic"]["snapshot"]},ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
