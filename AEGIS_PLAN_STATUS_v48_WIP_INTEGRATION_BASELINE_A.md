# AEGIS v48 WIP — INTEGRATION_BASELINE_A status

## Publication

- Branch: `integration-baseline-a`
- Base main: `d5f43c5a7d3550efb2f45d10aaf4195fb60955ae`
- Base merge: PR #78 SEEKER_CLOSE_A, Actions `42574022086` SUCCESS
- Pull request: #79, not merged
- Final candidate Actions: pending final corrected HEAD
- Release/tag: none

## Products

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Frozen baseline | `Aegis_SIM_v48_WIP_HP_A.html` | 22,200,135 | `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa` |
| Candidate | `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html` | 22,212,299 | `655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0` |
| Candidate packed JS | `data-c55-index="13"` | 40,958,311 | `c95b6022dd28ff87f95cb2a02af6f082ee25653bcd372137cf6d722cc0e8764d` |

## IMPLEMENTED

- Existing AUTO/H1/H2/H3/H4/Network G/CIWS ownership and call boundaries are documented and frozen.
- `AEGIS_DEFENSE_DECISION_INPUT_A1` is an owner-addressed, deep-frozen, observation-only snapshot.
- `AEGIS_DEFENSE_DECISION_COMMAND_A1` is a fail-closed advisory command with no safety or execution authority.
- `LEGACY_H1` reproduces the existing H1 order, priority and salvo result. After zero SHADOW mismatches, only the narrow WIP118 ordering/salvo/recommendation consumption path is ACTIVE.
- A reusable read-only `window.__DEFENSE_DECISION_A1__` diagnostic surface is present.

## TESTED

- Baseline/candidate browser-oracle digest: exact `c57bfc4f…c9615bf`.
- Contract repeat digest: exact `b3c3e8d3…550234`.
- Crew contract: 25/25, repeat digest exact `649d34b0…fc4c7`.
- SHADOW: active DDG/CG 18 comparisons, foreign-friendly DDG/CG 4 comparisons, mismatch 0.
- Forbidden truth fields 0; provider RNG mismatch 0; save mutation 0; browser/page errors 0.
- Protected functions: 30/31 exact; only `wip118BuildEngagementControl` changed for the intended adapter. Eleven boundary functions are separately hashed.
- Final-correction broad attempt 1 stopped at the first suite with 0 assertions because `WIP_HELI_CG_A` was absent; the failure evidence is retained.
- The authorized attempt 2 passed preflight 12/12 and broad coverage 785/785. Expectations changed 0; tolerances changed 0; game constants changed 0.

The pre-correction 782/782 evidence remains historical. For the corrected candidate, attempt 1 and its stop receipt remain immutable. The user explicitly authorized one corrected rerun only after sparse-checkout and indirect-input preflight were complete; attempt 2 was run once and passed 785/785.

## APPROVED

- Structural transition only: current decisions and downstream outcomes remain exact.
- Existing A3, Network G, FCS/SPG, reserve, re-engagement, damage/EMCON and formal release checks remain authoritative.
- H1 radar/EW, H2, H3, H4 and immediate local CIWS remain outside the provider.
- No new save field, OODA timing/slot model, modernization coefficient, weapon/sensor tuning or new tactical policy was introduced.

## UNRESOLVED

- `CIWS_SEED_419025_FAIL`
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
- WIP12D CIWS 42/47 fixed-step scale debt
- Legacy Chromium memory/crash and checkout-timeout debt
- Kh-32 60 km population study
- `CONFIRMED_ONLY` performance remains unverified
- SOV active sensors/Moskit, communications EMCON, active FIRE_CONTROL emitter registry, enemy-aircraft rebuild, physical hull break and external-save cross-field policy
- Inherited core self-test diagnostics: `SARH WIP61 confidence continuity missing`; `SARH confidence still double-penalizes raw SNR`

## RELEASE

- `RELEASE: NO`
- PR #79 is the review boundary. Do not merge, release or tag without the user's decision.
- After merge, proceed directly to `DEFENSE_OODA_A`; do not create an intermediate cleanup stage.

