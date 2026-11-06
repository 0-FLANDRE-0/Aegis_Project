#!/usr/bin/env python3
"""Exercise CUE_A threat-mode UI/save migration on the uninstrumented product."""
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


EXPRESSION = r"""()=>{
  const d=__NAVAL_SIM_DIAG__,api=__ASM_CUE_A__,checks={};
  checks.defaultIsMaxThreat=api.mode()==='MAX_THREAT';
  checks.uiMounted=!!document.getElementById('cueAThreatModesC')&&document.querySelectorAll('#cueAThreatModesC button').length===2;
  api.setMode('CONFIRMED_ONLY');
  const confirmed=d.exportOperationalStateV48Wip11A();
  checks.confirmedExported=confirmed.threatAssumptionMode==='CONFIRMED_ONLY';
  checks.confirmedValid=d.validateOperationalStateV48Wip11B(confirmed).ok;
  api.setMode('MAX_THREAT');d.importOperationalStateV48Wip11A(confirmed);
  checks.confirmedRestored=api.mode()==='CONFIRMED_ONLY';
  const legacy=structuredClone(confirmed);delete legacy.threatAssumptionMode;
  api.setMode('CONFIRMED_ONLY');
  const migrated=d.importOperationalStateV48Wip11A(legacy),after=d.exportOperationalStateV48Wip11A();
  checks.legacyDefaultsMax=!!migrated.validation.ok&&api.mode()==='MAX_THREAT'&&after.threatAssumptionMode==='MAX_THREAT';
  const bad=structuredClone(after);bad.threatAssumptionMode='INVALID';
  const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
  let threw=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){threw=true;}
  checks.invalidRejectedAtomically=threw&&!d.validateOperationalStateV48Wip11B(bad).ok&&before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
  checks.assumptionSwitch=api.enabledAssumptions().length===1;
  api.setMode('CONFIRMED_ONLY');checks.confirmedDisablesAssumed=api.enabledAssumptions().length===0;
  return {checks,mode:api.mode(),confirmedValidation:d.validateOperationalStateV48Wip11B(confirmed),migrated,core:__CORE_SELFTEST_FAILURES__};
}"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = args.html.read_bytes()
    errors: list[str] = []
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        result = page.evaluate(EXPRESSION)
        page.close()
        browser.close()
    checks = result["checks"]
    output = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_A_CODEC_1",
        "status": "PASS" if all(checks.values()) and not errors and not result["core"] else "FAIL",
        "inputSha256": hashlib.sha256(raw).hexdigest(),
        "checks": checks,
        "pageErrors": errors,
        "result": result,
        "elapsedS": time.monotonic() - started,
    }
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": output["status"], "checks": checks, "pageErrors": errors, "elapsedS": output["elapsedS"]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if output["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
