#!/usr/bin/env python3
"""Run the bounded pre-change HP reproduction on the unmodified U4 product."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html"
PRODUCT_SHA256 = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"
PRODUCT_BYTES = 22_195_923

KH35_SCENE = r"""()=>{
 const d=__NAVAL_SIM_DIAG__;
 const read=()=>{const s=d.snapshot(),st=d.wip101ShipStatus(),f=d.damageFloodSnapshotV1(),c=d.v48Wip07CrewState(),p=d.shipDynamics().pose;return {
   shipHP:s.shipHP,hitCount:s.shipHitCount,damageSeverityPct:st.overall,
   flood:{waterM3:f.summary.waterM3,floodingPct:f.summary.floodingPct,openings:f.summary.openings},
   crew:{mode:c.mode,combatUnavailable:c.combatUnavailable,equipmentOffline:c.equipmentOffline,dead:c.dead},
   survival:{state:p.state,equipmentOffline:p.equipmentOffline,lost:p.lost,irreversible:p.irreversible,waterM3:p.waterM3,heelRad:p.heelRad,trimRad:p.trimRad}
 };};
 d._resetShipTest();const before=read();
 const q=d.runWip108AsmAcquireCase({label:'Kh-35U',speedKt:15,seed:729300,headingDeg:90,rangeKm:60,maxTimeS:220,emconActive:false});
 const impact=read();d.ciwsB1Closure.advance({timeScale:1,simSeconds:2,fps:60});const after=read();
 return {input:{label:'Kh-35U',speedKt:15,seed:729300,headingDeg:90,rangeKm:60,maxTimeS:220,emconActive:false},
   flight:{durationS:q.durationS,shipHit:q.shipHit,deathReason:q.deathReason,everAcquire:q.everAcquire,everTrack:q.everTrack},
   before,impact,after,rngState:d.snapshot().simRngState,core:Array.from(window.__CORE_SELFTEST_FAILURES__??[])};
}"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archived_controls() -> dict[str, object]:
    base = ROOT / "docs/missile/seeker-unify/U4/evidence/final-regression/sov-casualty"
    save = json.loads((base / "flood-save.json").read_text())
    casualty = json.loads((base / "casualty.json").read_text())
    false_zero = save["before"]
    irreversible = [
        row for row in casualty["rows"]
        if isinstance(row, dict) and isinstance(row.get("survival"), dict)
        and (row["survival"].get("irreversible") or row["survival"].get("lost"))
    ]
    return {
        "sourceProductSha256": casualty["htmlSha256"],
        "falseZeroControl": {
            "fixture": "SOV controlled HARPOON contacts before watertight-isolation loss",
            "claimScope": "contract reproduction only; not the requested one-shot Kh-35 scene",
            "shipHP": false_zero["ship"]["shipHP"],
            "survival": false_zero["survival"],
            "floodSummary": false_zero["ship"]["damage"]["flooding"]["summary"],
            "crewMode": false_zero["ship"]["crew"]["mode"],
        },
        "irreversibleLossControl": {
            "first": {
                "survival": irreversible[0]["survival"],
                "flood": irreversible[0]["flood"],
            },
            "last": {
                "survival": irreversible[-1]["survival"],
                "flood": irreversible[-1]["flood"],
            },
            "transitionCount": len(irreversible),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/damage/hp/A/evidence/commit-a/baseline-repro.json")
    args = parser.parse_args()
    raw = PRODUCT.read_bytes()
    assert len(raw) == PRODUCT_BYTES
    assert sha(raw) == PRODUCT_SHA256
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", seed=729300, errors=errors)
        kh35 = page.evaluate(KH35_SCENE)
        page.close()
        browser.close()
    payload = {
        "schema": "AEGIS_HP_A_BASELINE_REPRO_1",
        "status": "REPRODUCED_CONTRACT_BUT_KH35_FALSE_ZERO_NOT_REPRODUCED",
        "product": PRODUCT.name,
        "productBytes": len(raw),
        "productSha256": sha(raw),
        "kh35FixedScene": kh35,
        "kh35FalseZeroReproduced": bool(kh35["after"]["shipHP"] == 0 and not kh35["after"]["survival"]["irreversible"]),
        "reproductionPolicy": "No arbitrary seed search. Fixed scene came from archived CUE_A evidence.",
        "archivedDeterministicControls": archived_controls(),
        "pageErrors": errors,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "kh35ShipHit": kh35["flight"]["shipHit"], "kh35Hp": kh35["after"]["shipHP"], "errors": errors}))


if __name__ == "__main__":
    main()
