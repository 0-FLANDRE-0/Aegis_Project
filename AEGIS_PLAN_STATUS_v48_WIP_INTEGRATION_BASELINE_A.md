# AEGIS v48 WIP — INTEGRATION_BASELINE_A status

## Publication

- Branch: `integration-baseline-a`
- Base main: `d5f43c5a7d3550efb2f45d10aaf4195fb60955ae`
- Base merge: PR #78 SEEKER_CLOSE_A, Actions `42574022086` SUCCESS
- Pull request: #79, not merged
- Final candidate Actions: run `43011382037`, SUCCESS
- Release/tag: none

## Products

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Frozen baseline | `Aegis_SIM_v48_WIP_HP_A.html` | 22,200,135 | `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa` |
| Candidate | `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html` | 22,211,451 | `baf96f9a1350973d045c9ad4f9025a86c10eaeda3c1924ad52498c45b90d0b5b` |
| Candidate packed JS | `data-c55-index="13"` | 40,956,705 | `ceac2691e092e0db37e3d54a10debfbd67a06ee1798e2859f1450d437ce29097` |

## IMPLEMENTED

- Existing AUTO/H1/H2/H3/H4/Network G/CIWS ownership and call boundaries are documented and frozen.
- `AEGIS_DEFENSE_DECISION_INPUT_A1` is an owner-addressed, deep-frozen, observation-only snapshot.
- `AEGIS_DEFENSE_DECISION_COMMAND_A1` is a fail-closed advisory command with no safety or execution authority.
- `LEGACY_H1` reproduces the existing H1 order, priority and salvo result. After zero SHADOW mismatches, only the narrow WIP118 ordering/salvo/recommendation consumption path is ACTIVE.
- A reusable read-only `window.__DEFENSE_DECISION_A1__` diagnostic surface is present.

## TESTED

- Baseline/candidate browser-oracle digest: exact `c57bfc4f…c9615bf`.
- Contract repeat digest: exact `fa669dbe…fe61f0`.
- SHADOW: active DDG/CG 18 comparisons, foreign-friendly DDG/CG 4 comparisons, mismatch 0.
- Forbidden truth fields 0; provider RNG mismatch 0; save mutation 0; browser/page errors 0.
- Protected functions: 24/25 exact; only `wip118BuildEngagementControl` changed for the intended adapter. Six new port functions are separately hashed.
- Frozen-candidate broad evidence: effective 782/782 PASS. Expectations changed 0; tolerances changed 0.

The broad runner was started once. Its raw receipt is retained: 59 assertions ran and passed; 19 suites stopped before browser launch with zero assertions because two files were absent from the sparse checkout. Those two files were restored and only the zero-execution suites received their first actual run on the same candidate SHA, passing 723/723. The broad suite was not restarted and already-run suites were not repeated.

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

