#!/usr/bin/env python3
"""Numerically explain every Stage-2 TRACK regression without changing state.

The probe wraps the real game measurement function in the browser.  It records
only pre-existing RF geometry for the ownship return and then delegates to the
original function.  Stage-1 and Stage-2 theoretical clean S/N are computed from
the exact formulas so the added monostatic factor (one-way beam gain * one-way
LOS quality) is explicit for every failed cell.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = [
    "/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
    "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
    "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
    "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K",
]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


EXPRESSION = r"""jobs=>jobs.map(job=>{
  const attempts=[];
  const original=asmSeekerEchoMeasurement;
  asmSeekerEchoMeasurement=function(em,s,p,src){
    const ship=src?._debugKind==='SHIP'||src?._debugMembers?.includes('SHIP');
    if(!ship)return original.apply(this,arguments);
    const g=src._g??asmSeekerReturnGeometry(em,src),rKm=g.rangeM/1000;
    const az01=clamp(src._offAz/Math.max(src._halfAz,1e-6),0,1),el01=clamp(src._offEl/Math.max(src._halfEl,1e-6),0,1);
    const offGain=Math.max(.08,Math.cos(az01*Math.PI/2)**2*Math.cos(el01*Math.PI/2)**2),los=Math.max(0,src._losQ??1);
    const lowAlt=clamp(((src.z??0)+8)/45,0,1),clutter=src._debugKind==='SEA_CLUTTER'?1:lerp(.88,1,lowAlt);
    const weather=maritimeRfWeatherPathFactorWip13A3('IJ',2*rKm),base=(src.rcs/p.refRcsM2)*Math.pow(p.snrRefKm/Math.max(.5,rKm),4)*clutter*weather;
    const stage1=base*offGain*los,stage2=stage1*offGain*los;
    const out=original.apply(this,arguments);
    attempts.push({timeS:Number(em.life)||0,mode:s.mode,rangeKm:rKm,azNorm:az01,elNorm:el01,offGain,los,addedFactor:offGain*los,stage1CleanSnr:stage1,stage2CleanSnr:stage2,detected:!!out});
    return out;
  };
  let result;
  try{result=job.kind==='range'?__SEEKER_UNIFY_A_DIAG__.runRangeCase(job.setup):__SEEKER_UNIFY_A_DIAG__.runCueCase(job.setup);}
  finally{asmSeekerEchoMeasurement=original;}
  const quant=(values,q)=>{if(!values.length)return null;const a=values.slice().sort((x,y)=>x-y);return a[Math.min(a.length-1,Math.floor((a.length-1)*q))];};
  const summarize=rows=>({attempts:rows.length,detections:rows.filter(q=>q.detected).length,
    rangeKm:{min:quant(rows.map(q=>q.rangeKm),0),median:quant(rows.map(q=>q.rangeKm),.5),max:quant(rows.map(q=>q.rangeKm),1)},
    beamNorm:{azP50:quant(rows.map(q=>q.azNorm),.5),azP90:quant(rows.map(q=>q.azNorm),.9),elP50:quant(rows.map(q=>q.elNorm),.5),elP90:quant(rows.map(q=>q.elNorm),.9)},
    offGain:{min:quant(rows.map(q=>q.offGain),0),median:quant(rows.map(q=>q.offGain),.5),max:quant(rows.map(q=>q.offGain),1)},
    los:{min:quant(rows.map(q=>q.los),0),median:quant(rows.map(q=>q.los),.5),max:quant(rows.map(q=>q.los),1)},
    addedFactor:{min:quant(rows.map(q=>q.addedFactor),0),median:quant(rows.map(q=>q.addedFactor),.5),p90:quant(rows.map(q=>q.addedFactor),.9),max:quant(rows.map(q=>q.addedFactor),1)},
    cleanSnr:{stage1Median:quant(rows.map(q=>q.stage1CleanSnr),.5),stage2Median:quant(rows.map(q=>q.stage2CleanSnr),.5),stage1P90:quant(rows.map(q=>q.stage1CleanSnr),.9),stage2P90:quant(rows.map(q=>q.stage2CleanSnr),.9)}});
  const byMode={};for(const mode of [...new Set(attempts.map(q=>q.mode))])byMode[mode]=summarize(attempts.filter(q=>q.mode===mode));
  return {kind:job.kind,setup:job.setup,result,summary:summarize(attempts),byMode,firstTen:attempts.slice(0,10)};
})"""


def jobs(comparison: dict) -> list[dict]:
    rows = []
    for row in comparison["targetTrackRegressions"]:
        rows.append({"kind": "range", "setup": row["setup"]})
    for row in comparison["cueTrackRegressions"]:
        rows.append({"kind": "cue", "setup": row["setup"]})
    return rows


def run(browser, html: Path, work: list[dict], errors: list[str]) -> list[dict]:
    body = html.read_bytes()
    rows: list[dict] = []
    # Cue cases are long; bounded pages prevent accumulated game registries.
    for offset in range(0, len(work), 6):
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        rows.extend(page.evaluate("jobs=>__SEEKER_UNIFY_C_BEAM_EXPLAIN__.run(jobs)", work[offset:offset + 6]))
        page.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1", type=Path, required=True)
    parser.add_argument("--stage2", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    comparison = json.loads(args.comparison.read_text())
    work = jobs(comparison)
    errors: list[str] = []
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        stage1 = run(browser, args.stage1, work, errors)
        stage2 = run(browser, args.stage2, work, errors)
        browser.close()
    output = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_NUMERIC_EXPLANATION_1",
        "method": "read-only wrapper around actual asmSeekerEchoMeasurement; AFTER_ACTION_DIAGNOSTIC_ONLY",
        "stage1": {"input": str(args.stage1), "sha256": hashlib.sha256(args.stage1.read_bytes()).hexdigest(), "rows": stage1},
        "stage2": {"input": str(args.stage2), "sha256": hashlib.sha256(args.stage2.read_bytes()).hexdigest(), "rows": stage2},
        "formula": "stage2CleanSnr = stage1CleanSnr * oneWayBeamGain * oneWayLosQ",
        "cases": len(work),
        "pageErrors": errors,
        "elapsedS": time.monotonic() - started,
        "truthUse": "physical echo synthesis observed only by test wrapper; no tactical feedback",
    }
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": len(work), "stage1": len(stage1), "stage2": len(stage2), "pageErrors": len(errors), "elapsedS": output["elapsedS"]}))
    raise SystemExit(0 if len(stage1) == len(stage2) == len(work) and not errors else 1)


if __name__ == "__main__":
    main()
