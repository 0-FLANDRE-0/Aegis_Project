#!/usr/bin/env python3
"""Build CUE_A-1's reviewed handoff documents from frozen test artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"
FINAL_SHA = "0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a"
BROAD_SHA = "83e3d76a50b6db4616cd7b5dcb013361617477dd90dfa4ea6352248ada84932c"
BASE_SHA = "efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7"


def load(name: str):
    return json.loads((HERE / name).read_text())


def dump(name: str, value) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(PRODUCT) == FINAL_SHA

# Preserve the immutable output of the one permitted broad run before making a
# reviewed result that classifies pre-approved deltas and the post-run metadata
# repair. Re-running this script never overwrites that raw record.
raw_path = HERE / "REGRESSION_RESULTS_RAW.json"
current_regression = load("REGRESSION_RESULTS.json")
if current_regression.get("schema") == "AEGIS_TRACK_A_EXISTING_REGRESSIONS_1":
    dump("REGRESSION_RESULTS_RAW.json", current_regression)
raw = json.loads(raw_path.read_text())
ui = load("POST_BROAD_UI_213.json")
metadata = load("POST_BROAD_METADATA_AUDIT.json")
env_d = load("POST_BROAD_ENV_D_STATUS.json")
battles = load("CUE_A_1_60_BATTLE_RESULTS.json")

paired_updates = [
    {
        "ship": "DDG_119_LATE_FLIGHT_IIA",
        "check": "samePhysicalState",
        "before": "dcf249991e954c5a64a909b1b813bf2516f92e79bef1fb33c301e11ee52ffb47",
        "after": "a55790447710bd70f65fd25471e9f80cbfb90210b01cd8a391a04af94d8b918a",
    },
    {
        "ship": "DDG_119_LATE_FLIGHT_IIA",
        "check": "sameCombatRng",
        "before": 619673995,
        "after": 4148992623,
    },
    {
        "ship": "DDG_119_LATE_FLIGHT_IIA",
        "check": "raidInventoryDeltaBounded",
        "before": 90,
        "after": 89,
    },
    {
        "ship": "DDG_119_LATE_FLIGHT_IIA",
        "check": "sameExistingObserverState",
        "before": "43d054f9a47edaef6e570333df1f0b12e121583b978eaa1107b3e81f1ff4b390",
        "after": "3ed420184aeb832cf1af7f55189c2db1d833c9ab871c5f4f883731ef1136e5c8",
    },
    {
        "ship": "CG_52_LATE_TICONDEROGA",
        "check": "samePhysicalState",
        "before": "6c6cc8e13c8be917aaa653b5c4238eea5888a31d0e79792875b9ee525c3dee58",
        "after": "03ee05c568cbd2593516be8e7d6acf4ede3a5d0892c76f799eb8399ddb73e0d2",
    },
    {
        "ship": "CG_52_LATE_TICONDEROGA",
        "check": "sameCombatRng",
        "before": 1655152390,
        "after": 709110536,
    },
    {
        "ship": "CG_52_LATE_TICONDEROGA",
        "check": "raidInventoryDeltaBounded",
        "before": 114,
        "after": 115,
    },
    {
        "ship": "CG_52_LATE_TICONDEROGA",
        "check": "sameExistingObserverState",
        "before": "cba2be8e815e13371e05296d0b9b84405f2c53ddebd934a6f155270791034861",
        "after": "6fa7f65b5fba099aee506957645910b0a5b07e84b188db81c932bdfba4f316ad",
    },
]
for row in paired_updates:
    row.update(
        {
            "approval": "PREAPPROVED_CHANGED_PATH",
            "cause": "CUE_A-1 cue prediction/passive-RF path; historical C Stage-2/Stage-3 contribution separately attributed in PAIRED_STAGE_ATTRIBUTION.json",
            "safetyOutcome": {
                "shipHpBeforeAfter": [100, 100],
                "sameHullDamageAndFixedLayout": True,
                "sameExistingOffboardPorts": True,
                "bothFaultFree": True,
            },
        }
    )

expected = {
    "schema": "AEGIS_CUE_A_1_EXPECTED_VALUE_UPDATES_1",
    "status": "APPROVED_BY_DIRECTIVE_CHANGED_PATH",
    "assertionLogicChanges": 0,
    "toleranceChanges": 0,
    "stateValueEncoding": "SHA-256 of compact, key-sorted JSON after the paired harness physical() normalizer; scalar RNG and VLS values are recorded directly",
    "pairedRaid": paired_updates,
    "envDMetadata": metadata["changes"] | {
        "approval": "PREAPPROVED_CHANGED_PATH",
        "cause": metadata["reason"],
    },
    "sixtyBattleReference": {
        "gate": False,
        "candidateSha256BeforeMetadataOnlyCorrection": BROAD_SHA,
        "finalGameplaySourceEquivalent": metadata["checks"]["normalizedMainExact"],
        "before": battles["baselineTotals"],
        "after": battles["totals"],
        "firstAssociation": battles["firstAssociationAudit"],
        "note": "Reference aggregate only; no assertion or tolerance was derived from it.",
    },
}
dump("EXPECTED_VALUE_UPDATES.json", expected)

native_rows = [r for r in raw["rows"] if r["suite"] not in ("emcon-ui", "paired-friendly", "ui213", "webgl8")]
review = {
    "schema": "AEGIS_CUE_A_1_BROAD_REVIEW_1",
    "status": "PASS_WITH_INHERITED_DEBT",
    "broadRun": {
        "executions": 1,
        "candidateSha256": BROAD_SHA,
        "wallS": raw["wallS"],
        "native13": raw["native13"],
        "nativeRowsAllPass": all(r["status"] == "PASS" for r in native_rows),
        "webgl": {"passed": 29, "expected": 29},
        "pairedRaw": {"passed": 34, "expected": 42, "classifiedExpectedDifferences": 8},
        "uiRaw": {"passed": 205, "expected": 213, "metadataOnlyDifferences": 8},
    },
    "postBroadCorrection": {
        "kind": "ENV_D_INTEGRITY_METADATA_ONLY",
        "candidateSha256": FINAL_SHA,
        "gameplayFunctionSourceChanged": metadata["changes"]["gameplayFunctionSourceChangedAfterBroad"],
        "measuredRowsChanged": metadata["changes"]["measuredRowsChanged"],
        "conditionsChanged": metadata["changes"]["conditionsChanged"],
        "seedsChanged": metadata["changes"]["seedsChanged"],
        "tolerancesChanged": metadata["changes"]["tolerancesChanged"],
        "envDStatusPass": env_d["pass"],
        "targetedUi": {
            "passed": ui["passedAssertions"],
            "expected": ui["expectedAssertions"],
            "errors": ui["errors"],
        },
    },
    "newUnexplainedFailures": [],
    "inheritedUnresolved": [
        "LEGACY_EMCON_UI_14_INCOMPLETE",
        "CIWS_SEED_419025_FAIL",
        "CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2",
    ],
    "releaseApproved": False,
    "releaseReason": "Directive permits PR only; no merge, release, or tag.",
}
dump("BROAD_REVIEW.json", review)

reviewed = {
    "schema": "AEGIS_CUE_A_1_REGRESSION_REVIEWED_1",
    "status": review["status"],
    "product": {"file": PRODUCT.name, "sha256": FINAL_SHA},
    "broadRaw": {
        "file": "REGRESSION_RESULTS_RAW.json",
        "candidateSha256": BROAD_SHA,
        "wallS": raw["wallS"],
        "native13": raw["native13"],
        "webgl": {"passed": 29, "expected": 29},
        "paired": {"passed": 34, "expected": 42, "expectedDifferences": 8},
        "ui": {"passed": 205, "expected": 213, "metadataOnlyDifferences": 8},
    },
    "postBroadMetadataCorrection": {
        "audit": "POST_BROAD_METADATA_AUDIT.json",
        "envD": "POST_BROAD_ENV_D_STATUS.json",
        "targetedUi": "POST_BROAD_UI_213.json",
        "uiPassed": 213,
        "uiExpected": 213,
        "gameplayFunctionChanges": 0,
    },
    "expectedValueUpdates": "EXPECTED_VALUE_UPDATES.json",
    "sixtyBattleReference": {
        "status": battles["status"],
        "jobs": battles["jobs"],
        "totals": battles["totals"],
        "baselineTotals": battles["baselineTotals"],
        "firstAssociation": battles["firstAssociationAudit"],
        "gate": False,
    },
    "newUnexplainedFailures": [],
    "inheritedUnresolved": review["inheritedUnresolved"],
    "releaseApproved": False,
}
dump("REGRESSION_RESULTS.json", reviewed)

build = load("BUILD_FINAL.json")
dump(
    "BUILD.json",
    {
        "schema": "AEGIS_CUE_A_1_BUILD_FINAL_1",
        "product": PRODUCT.name,
        "productHtmlSha256": FINAL_SHA,
        "productBytes": PRODUCT.stat().st_size,
        "baselineCommit": "4faeb4e079b7baddcb1e1b8c1b892af804565938",
        "baselineProductSha256": BASE_SHA,
        "stage1bImplementationCommit": "46889420995ddb545e64f02d700eb2bbdd3ba9f4",
        "stage2ImplementationCommit": "48a268f79e1f40e46c2d7ab96f9ead721276f2a2",
        "stage2EvidenceCommit": "6e816d35c241a9b58a1ede7554cceb49a4752a4f",
        "broadCandidateSha256": BROAD_SHA,
        "postBroadChange": build["envDMetadataExpectationUpdate"],
        "reproducibleBuild": "PASS_BYTE_EXACT",
    },
)

singer = load("CUE_FILTER_SINGER.json")["singer"]
velocity_rows = []
for row in singer["velocityTable"]:
    s, sig, basket = row["setup"], row["sigma"], row["basket"]
    velocity_rows.append(
        f"| {s['label']} | {'known' if s['known'] else 'null'} | {s['seconds']} | "
        f"{sig['positionM']:.2f} | {sig['velocityMps']:.2f} | {basket['capM']:.0f} | "
        f"{basket['rangeHalfM']:.2f} | {basket['rangeHalfLimiter']} / {basket['azHalfLimiter']} |"
    )

report = f"""# CUE_A-1 final report

**IMPLEMENTED:** YES — range-floor restoration, exact-discrete Singer cue filter, bounded cue uncertainty, ship-radar-family passive RF and frequency/rotating-beam handling.<br>
**TESTED:** YES — all Stage 0/1/2 gates, one final broad run, post-broad metadata audit/UI confirmation, and one 60-battle reference run.<br>
**APPROVED:** PR CANDIDATE — directive-preapproved changed-path expectations are recorded with tolerance changes 0.<br>
**UNRESOLVED:** inherited `#lockBtn` 14, `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`; CONFIRMED_ONLY performance remains UNVERIFIED.<br>
**RELEASE:** NO — PR only; main merge, release and tag were not performed.

## 1. Product

- Baseline: `seeker-unify-c@4faeb4e079b7baddcb1e1b8c1b892af804565938`, SHA `{BASE_SHA}`.
- Candidate: `{PRODUCT.name}`, SHA `{FINAL_SHA}`, {PRODUCT.stat().st_size:,} bytes.
- Performance mode: MAX_THREAT. CONFIRMED_ONLY received static/scene checks only.

## 2. Sequential gates

| Stage | Result | Evidence |
|---|---|---|
| 0 — paired attribution | PASS | All 8 C-era differences attributed; no code/expectation/tolerance change. |
| 1a — ASM range floor | PASS | SAM 24/24 exact; ASM exact at/above 0.5 km; differences confined below 0.5 km. |
| 1b — Singer filter | PASS (12/12 gates) | TRACK/hit regressions 0/0, controls 180 exact, S1 50/50, egress 37/37 intended ship. |
| 2 — passive RF | PASS (12/12 gates) | contaminants 0/50, controls 180 exact, S1 50/50, egress 37/37 intended ship. |
| Final broad | PASS WITH INHERITED DEBT | Native13 364/364, real WebGL 29/29; expected paired 8 classified. |
| Post-broad metadata check | PASS | ENV_D match, changed gameplay functions 0, targeted UI 213/213. |

No gate was bypassed. No result-dependent tuning was made.

## 3. Paired eight-item cause record

Stage 0 shows physical/VLS differences first occur in C Stage 2→final, while combat RNG/observer differences have both B→C Stage 2 and C Stage 2→final contributions. The final candidate's exact before/after values and safety invariants are in `EXPECTED_VALUE_UPDATES.json`; all eight are changed-path preapprovals. Both ships remain HP 100, fixed hull/damage layout and ports match, and both sides are fault-free. Assertion logic and tolerances changed by 0.

## 4. Singer dt result and fixed-tick table

- Method: Van Loan block exponential with Higham Padé13.
- 180 s, initial velocity sigma 0: one-step `3529.2813585273 m`, 1/60 s ticks `3529.2813585259 m`, relative error `{singer['relativeErrors']['velocitySigma0']:.3e}`.
- 180 s, initial velocity sigma 9 m/s: one-step `3883.3267835257 m`, 1/60 s ticks `3883.3267835243 m`, relative error `{singer['relativeErrors']['velocitySigma9']:.3e}`.

| Weapon | Velocity input | t (s) | position sigma (m) | velocity sigma (m/s) | cap (m) | range half (m) | limiter |
|---|---|---:|---:|---:|---:|---:|---|
{chr(10).join(velocity_rows)}

All 12 diagnostic cases were stepped at 1/60 s. Their range half-width was set by the existing 0.12R floor; azimuth by the existing 5° floor. The physical cap and 3-sigma values remain recorded in `CUE_FILTER_SINGER.json`.

## 5. C final → Stage 1 → Stage 2 outcomes

| Weapon / EMCON | C final TRACK/hit | Stage 1 TRACK/hit | Stage 2 TRACK/hit |
|---|---:|---:|---:|
| Kh-35U / OFF | 60 / 59 | 60 / 59 | 60 / 59 |
| Kh-35U / ON | 60 / 59 | 60 / 59 | 60 / 59 |
| Kh-32 / OFF | 40 / 40 | 40 / 40 | 45 / 40 |
| Kh-32 / ON | 44 / 40 | 44 / 40 | 44 / 40 |

Stage 1 removed one transient Kh-32 ACQUIRE without changing TRACK, hit, or failure class. Stage 2 changed ten Kh-32 EMCON-OFF cells through the mandated 3 GHz wavelength scaling; it improved TRACK by five while ship hits remained 40. Forbidden in-search/out-of-basket failures stayed 0.

## 6. Passive receiver/equipment result

- Equipment: 150 baseline + 150 candidate rows; ALL_OFF produced 0 samples.
- ALL_ON/NAV_OFF/SPQ_OFF are normally selected by `SHIP SEARCH RADAR`; SPY_OFF falls back to `SURFACE SEARCH RADAR` where observable.
- Mean receive interval: 0.2 s for SPY-dominated rows and 0.44 s for SPY_OFF rotating-radar rows.
- Kh-32 ALL_ON mean absolute error: bearing 0.763°, elevation 0.803°; SPY_OFF: 0.257° / 0.263°.
- Kh-35U ALL_ON mean absolute error: bearing 1.192°, elevation 1.628°; SPY_OFF: 0.392° / 0.538°.
- Direct elevation-derived range is diagnostic only and never overwrites target-memory range. Full per-condition family, SNR, errors, and intervals are in `STAGE2_PASSIVE_TESTS.json` and `PASSIVE_RF_EMITTER_BAND.json`.

## 7. Contaminants and CONFIRMED_ONLY

- Friendly ESSM/SM-6 active seekers, aircraft radar, active Nulka, and ship jammer: selected 0/50.
- HOJ functions remained byte-identical; no new false acquisition in 180 controls.
- CONFIRMED_ONLY: Kh-32 passive disabled; Kh-35U accepted X-band only. Performance is explicitly **UNVERIFIED**.

## 8. Final regression and post-run correction

The one broad run took {raw['wallS']:.3f} s. Native13 passed 364/364 and actual WebGL observed-world passed 29/29. Raw paired was 34/42 with exactly the eight preapproved state differences. Raw UI was 205/213: all eight failures were `tableMatch`, caused by ENV_D retaining the old `spawnEnemyMissile` integrity hash after Stage 2 added observed emitter metadata.

After the broad run, only ENV_D integrity metadata was advanced. Audit proved measured rows, conditions, seeds, normalized table, gameplay function source and tolerances changed by 0. `__ENV_D__.status()` then matched, and a bounded UI rerun passed 213/213. The raw broad file remains `REGRESSION_RESULTS_RAW.json`; reviewed disposition is `REGRESSION_RESULTS.json`.

The 60-battle reference (not a gate) completed 60/60: 301 kills, 19 leakers, 0 egress, 0 other versus C final 299/18/0/3. All 320 first associations were SHIP; neighbor/non-ship first associations were 0.

## 9. Remaining limits

- Legacy EMCON `#lockBtn` 14 assertions remain INCOMPLETE, not counted as PASS.
- `CIWS_SEED_419025_FAIL` and the two inherited CG observer differences remain open debts.
- Kh-32 60 km root-cause investigation, generic emitter work, HOJ changes, Harpoon U3, TRACK-D/OODA/HP/defensive-weapon work are out of scope.
- No main merge, release, or tag was made.
"""
(HERE / "REPORT.md").write_text(report)

readme = f"""# CUE_A-1

Current PR candidate: `{PRODUCT.name}`<br>
SHA-256: `{FINAL_SHA}`

This increment restores the ASM-only 0.5 km floor, replaces tick-coupled cue noise with an exact-discrete Singer model, bounds unknown-velocity uncertainty, and limits midcourse passive RF to observed ship-radar families with band and swept-beam handling.

- Start with `REPORT.md` for the reviewed outcome.
- Use `REGRESSION_RESULTS.json` for final disposition and `REGRESSION_RESULTS_RAW.json` for the immutable one-time broad output.
- Detailed Stage 1 and Stage 2 evidence is in `CUE_FILTER_SINGER.*` and `PASSIVE_RF_EMITTER_BAND.*`.
- `CONFIRMED_ONLY` performance is UNVERIFIED. Inherited debts are not waived.
- Delivery policy: PR only; no merge/release/tag.
"""
(HERE / "README.md").write_text(readme)

status = f"""# AEGIS PLAN STATUS — v48 WIP CUE_A_1

- Product: `{PRODUCT.name}`
- SHA-256: `{FINAL_SHA}`
- Baseline: `seeker-unify-c@4faeb4e079b7baddcb1e1b8c1b892af804565938`
- Branch: `cue-a-1`
- State: **PR candidate / PASS WITH INHERITED DEBT**

## Completed

- Stage 0 paired eight-item attribution.
- Stage 1a range-floor restoration and equivalence gate.
- Stage 1b exact-discrete Singer filtering and all 12 gates.
- Stage 2 passive RF family/band/swept-beam model and all 12 gates.
- One final broad run, post-broad ENV_D metadata-only integrity correction, UI 213/213 confirmation.
- One 60-battle reference run.

## Preserved

- Truth boundary, fixed-step ownership, isolated weapon RNG, HOJ, EKF/guidance/damage paths outside stated scope.
- ENV_D measured rows, test conditions, seeds and tolerances.

## Open

- CONFIRMED_ONLY performance UNVERIFIED.
- Legacy EMCON UI 14, CIWS seed 419025, inherited CG observer delta 2.
- No main merge, release, or tag.

See `docs/missile/cue-a-1/REPORT.md` and `REGRESSION_RESULTS.json` for evidence and exact disposition.
"""
(ROOT / "AEGIS_PLAN_STATUS_v48_WIP_CUE_A_1.md").write_text(status)

plan_path = HERE / "PLAN.md"
plan = plan_path.read_text()
plan = plan.replace(
    "- Final broad regression: not run.",
    f"- Final broad regression: `PASS WITH INHERITED DEBT`. One broad run on `{BROAD_SHA}` completed native13 364/364 and real WebGL 29/29. Exactly eight paired changed-path values were classified; the eight UI table failures were an ENV_D metadata fingerprint mismatch. A metadata-only correction (gameplay functions/rows/conditions/seeds/tolerances changed 0) produced final `{FINAL_SHA}` and targeted UI 213/213. The 60-battle reference completed 60/60 with 301 kills, 19 leakers, 0 egress, 0 other. No release/tag/merge.",
)
plan_path.write_text(plan)

print(json.dumps({"productSha256": FINAL_SHA, "rawBroadPreserved": True, "reviewedStatus": review["status"]}, indent=2))
