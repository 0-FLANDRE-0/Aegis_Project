#!/usr/bin/env python3
"""Run 200 fixed scenes per U1 weapon path and require exact delegation."""
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


def jobs() -> dict[str, list[dict]]:
    return {
        "KH35U": [
            dict(seed=810000+i, kind=("DDG", "CG", "SOV", "HULK")[i % 4],
                 rangeKm=(10, 20, 30, 40, 50)[i % 5], altM=(15, 200)[i % 2],
                 speedKt=(0, 15)[(i // 2) % 2], control="TARGET")
            for i in range(200)
        ],
        "KH32": [
            dict(seed=820000+i, label="Kh-32", rangeKm=(15, 20, 30, 40)[i % 4],
                 speedKt=(15, 30)[i % 2], turnDeg=(0, 30, 90)[i % 3], emcon=bool(i % 2))
            for i in range(200)
        ],
        "HARPOON": [
            dict(seed=830000+i, rangeKm=(5, 10, 20, 40)[i % 4],
                 speedKt=(0, 15, 30)[i % 3], turnDeg=(0, 30, 90)[i % 3])
            for i in range(200)
        ],
        "SARH_AND_ESSM_ARH": [
            dict(seed=840000+i, bearingDeg=(-25, 0, 25)[i % 3],
                 targetRangeKm=(8, 10, 14, 18)[i % 4], missileRangeKm=(2, 4, 6)[i % 3])
            for i in range(200)
        ],
        "SM6_ARH": [
            dict(seed=850000+i, path=("SM6_BLOCK_IA_AIR", "SM6_BLOCK_IA_SURFACE")[i % 2],
                 targetKind=(("AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF")[i % 4] if i % 2 == 0 else ("SURFACE", "SEA_CLUTTER", "CHAFF")[i % 3]),
                 rangeKm=(10, 20, 30, 40, 50)[i % 5])
            for i in range(200)
        ],
        "RAM": [
            dict(seed=860000+i, bearingDeg=(-20, 0, 20)[i % 3], rangeKm=(4, 6, 8)[i % 3],
                 altM=(10, 30)[i % 2], speedMps=(240, 280, 330)[i % 3])
            for i in range(200)
        ],
    }


EXPRESSIONS = {
    "KH35U": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))",
    "KH32": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))",
    "HARPOON": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))",
    "SARH_AND_ESSM_ARH": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runAllRfFixtureU1(o))",
    "SM6_ARH": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runSamArhCase(o))",
    "RAM": "a=>a.map(o=>__NAVAL_SIM_DIAG__.runWip106RamMeasurement({bearingsDeg:[o.bearingDeg],seeds:[o.seed],rangeKm:o.rangeKm,altM:o.altM,speedMps:o.speedMps,maxTimeS:20,physicsOnlyPk:true}))",
}


def run_one(pw, path: Path, label: str, matrix: dict[str, list[dict]], progress: Path) -> dict:
    body = path.read_bytes()
    output: dict[str, list] = {}
    errors: list[str] = []
    browser = launch(pw)
    for group, rows in matrix.items():
        values = []
        for offset in range(0, len(rows), 20):
            page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            values.extend(page.evaluate(EXPRESSIONS[group], rows[offset:offset+20]))
            page.close()
            progress.write_text(json.dumps({"label": label, "group": group, "completed": len(values), "total": len(rows), "pageErrors": errors}) + "\n")
        output[group] = values
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    contract = page.evaluate("""()=>{const api=window.__SEEKER_COMMON_U1__;if(!api)return null;
      const hostile={entityId:'FORBIDDEN',profileId:'FORBIDDEN',truthRef:{x:1},_debugSourceId:'FORBIDDEN',rangeM:1200,azRad:.2,elRad:.1,radialMps:-30,rcsM2:4,rangeSigmaM:8,azSigmaDeg:.1,elSigmaDeg:.2,radialVelSigmaMps:2};
      const samples={echo:api.echoSample(hostile),cell:api.resolvedCell(hostile),measurement:api.measurement(hostile),estimate:api.estimate({_kfX:new Float64Array([1,2,3,4,5,6]),_kfP:new Float64Array(36),trackValid:true,mode:'TRACK'})};
      const text=JSON.stringify(samples);return {schema:api.schema,mode:api.mode,units:api.units,dimensions:api.dimensions,delegates:api.delegates,truthUsed:api.truthUsed,samples,forbidden:/entityId|profileId|truthRef|_debugSourceId|FORBIDDEN/.test(text)};}""")
    page.close()
    browser.close()
    return {"label": label, "input": str(path), "inputSha256": hashlib.sha256(body).hexdigest(), "groups": output, "contract": contract, "pageErrors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    matrix = jobs()
    started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_one(pw, args.baseline, "U0_ACTIVE", matrix, args.out.with_suffix(".baseline.progress.json"))
        candidate = run_one(pw, args.candidate, "U1_SHADOW", matrix, args.out.with_suffix(".candidate.progress.json"))
    differences = {}
    for group in matrix:
        if baseline["groups"][group] != candidate["groups"][group]:
            differences[group] = [
                {"index": i, "baseline": before, "candidate": after}
                for i, (before, after) in enumerate(zip(baseline["groups"][group], candidate["groups"][group]))
                if before != after
            ]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U1_EQUIVALENCE_1",
        "status": "PASS" if not differences and not baseline["pageErrors"] and not candidate["pageErrors"] and candidate["contract"] and not candidate["contract"]["forbidden"] else "FAIL",
        "elapsedS": time.monotonic() - started,
        "counts": {group: len(rows) for group, rows in matrix.items()},
        "differences": differences,
        "staticDtoAudit": candidate["contract"],
        "pageErrors": {"baseline": baseline["pageErrors"], "candidate": candidate["pageErrors"]},
        "baseline": baseline,
        "candidate": candidate,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "elapsedS", "counts", "differences", "staticDtoAudit", "pageErrors")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
