"""Run one frozen TRACK-C battle with and without ASM seeker diagnostics.

The two executions use fresh browser contexts and the same pinned product/helper.
This is evidence for observer neutrality; it is not a gameplay fixture.
"""
from pathlib import Path
import hashlib, importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIG = Path("/dev/shm/aegis-ciws-dmg-a")
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
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def frozen_case():
    plan = json.loads((HERE / "EGRESS_REPLAY_PLAN.json").read_text())
    return next(row["case"] for row in plan["jobs"] if row["id"] == "S6-419033-C")


def helper(diagnostic):
    source = (ORIG / "docs/contact/track/C/test_support/battle.js").read_text()
    if diagnostic:
        needle = "  window.__TRACK_C_AA_INTERNAL__?.begin({record:c.lineageOn!==false});"
        source = source.replace(
            needle,
            "  window.__ASM_SEEKER_A_DIAG__.beginBattle(c.asmSeekerFocusIds??[]);\n" + needle,
            1,
        )
        needle = "  const trackCLineage=window.__TRACK_C_AA_INTERNAL__?.finish()??null;"
        source = source.replace(
            needle,
            needle + "\n  const asmSeekerADiagnostic=window.__ASM_SEEKER_A_DIAG__.finishBattle();",
            1,
        )
        source = source.replace(
            "  return {trackCLineage,schema:",
            "  return {trackCLineage,asmSeekerADiagnostic,schema:",
            1,
        )
    return (ORIG / "docs/contact/track/C/after_action.js").read_text() + "\n" + source


EXPR = """c=>{const r=__TRACK_STABLE_BATTLE__.run(c);return {
  status:r.status,end:r.end,targets:r.targets,globalRng:r.final.globalRng,
  inventory:r.final.inventory,ship:r.final.ship,launches:r.counts.launches,
  intercepts:r.counts.intercepts,faults:r.faults,
  asm:r.asmSeekerADiagnostic??null};}"""


def run(page, case):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    value = page.evaluate(EXPR, case)
    if errors or value["faults"]:
        raise RuntimeError((errors, value["faults"]))
    return value


def main():
    case = frozen_case()
    base = (ROOT / "Aegis_SIM_v48_WIP_TRACK_C.html").read_bytes()
    diag = (ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A_DIAG.html").read_bytes()
    instrumenter = module("asm_seeker_det_track_c_instrument", ORIG / "docs/contact/track/C/instrument.py")
    base_probe, base_receipt = instrumenter.physical_probe(base)
    diag_probe, diag_receipt = instrumenter.physical_probe(diag)
    bodies = {
        "baseline": instrument(base_probe, helper(False)),
        "diagnostic": instrument(diag_probe, helper(True)),
    }
    result = {
        "schema": "AEGIS_ASM_SEEKER_A_REPLAY_DETERMINISM_1",
        "case": case,
        "inputs": {key: {"sha256": sha(body)} for key, body in bodies.items()},
        "physicalProbe": {"baseline": base_receipt, "diagnostic": diag_receipt},
        "runs": {},
    }
    started = time.monotonic()
    with sync_playwright() as pw:
        for key, body in bodies.items():
            at = time.monotonic()
            browser = launch(pw)
            try:
                page = load(browser, body, ship=case["ship"], errors=[])
                page.set_default_timeout(900000)
                value = run(page, case)
            finally:
                browser.close()
            value["wallS"] = time.monotonic() - at
            result["runs"][key] = value
            print(json.dumps({"run": key, "wallS": value["wallS"], "end": value["end"]}), flush=True)
    comparable = lambda value: {key: value[key] for key in (
        "status", "end", "targets", "globalRng", "inventory", "ship", "launches", "intercepts", "faults")}
    a, b = map(comparable, (result["runs"]["baseline"], result["runs"]["diagnostic"]))
    result["comparison"] = {
        "byteEqualComparableJson": json.dumps(a, sort_keys=True, separators=(",", ":")) ==
                                   json.dumps(b, sort_keys=True, separators=(",", ":")),
        "baselineSha256": sha(json.dumps(a, sort_keys=True, separators=(",", ":"))),
        "diagnosticSha256": sha(json.dumps(b, sort_keys=True, separators=(",", ":"))),
    }
    result["elapsedS"] = time.monotonic() - started
    (HERE / "REPLAY_DETERMINISM.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["comparison"], indent=2))


if __name__ == "__main__":
    main()
