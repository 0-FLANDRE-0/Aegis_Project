# SEEKER_CLOSE_A corrected bounded diagnostic

Status: **PASS / PRODUCT UNCHANGED**
Authority: `Aegis_SIM_v48_WIP_HP_A.html`, 22,200,135 bytes, SHA-256
`9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`.

The closure correction changes diagnostic evidence only. It does not repack
the authority product. The disposable diagnostic build is 22,215,311 bytes,
SHA-256 `eb1e1ab95740d1e2f1f12af5d7ff81b6ea224e8e3248ce5c7e1c82459c98a5e4`.
All protected seeker, guidance, decoy, damage, HP, and save function hashes
are byte-exact before and after instrumentation.

## Corrected matrix

The fixed matrix is now 19 shots: 12 DDG and seven CG cases. The two additions
are one true `ALL_RADIATION_SILENT` case per ship. No seed search was used.

| Ship | Condition | Seed | Category | Native cause | End s | Closest m | Chaff / Nulka final stage |
|---|---|---:|---|---|---:|---:|---|
| DDG-119 | NO_DEFENSE | 6209793 | TARGET_HIT | NORMAL_HIT | 60.55 | 58.09 | not deployed / not deployed |
| DDG-119 | HARD_KILL_ONLY | 6209794 | DEFENSE_INTERCEPT | INTERCEPT_KILL (5in MFF) | 43.22 | 5,192.60 | not deployed / not deployed |
| DDG-119 | CHAFF_ONLY | 6209795 | TARGET_HIT | NORMAL_HIT | 61.20 | 41.36 | recovered / not deployed |
| DDG-119 | NULKA_ONLY | 6209796 | TARGET_HIT | NORMAL_HIT | 60.50 | 76.14 | not deployed / recovered |
| DDG-119 | CHAFF_NULKA | 6209797 | TARGET_HIT | NORMAL_HIT | 60.65 | 44.90 | recovered / recovered |
| DDG-119 | RADAR_MASTER_SILENT_ECM_ON | 6209798 | TARGET_HIT | NORMAL_HIT | 60.55 | 56.94 | not deployed / not deployed |
| DDG-119 | CLOCK_1X | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | not deployed / not deployed |
| DDG-119 | CLOCK_8X | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | not deployed / not deployed |
| DDG-119 | CLOCK_16X | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | not deployed / not deployed |
| DDG-119 | DETERMINISM_A | 6209800 | DECOY_SEDUCTION | — | 162.43 | 128.87 | recovered / Nulka maintained |
| DDG-119 | DETERMINISM_B | 6209800 | DECOY_SEDUCTION | — | 162.43 | 128.87 | recovered / Nulka maintained |
| DDG-119 | ALL_RADIATION_SILENT | 6209801 | TARGET_HIT | NORMAL_HIT | 60.55 | 61.66 | not deployed / not deployed |
| CG-52 | NO_DEFENSE | 6210049 | TARGET_HIT | NORMAL_HIT | 60.68 | 20.69 | not deployed / not deployed |
| CG-52 | HARD_KILL_ONLY | 6210050 | TARGET_HIT | NORMAL_HIT | 60.62 | 41.40 | not deployed / not deployed |
| CG-52 | CHAFF_ONLY | 6210051 | TARGET_HIT | NORMAL_HIT | 60.50 | 74.99 | recovered / not deployed |
| CG-52 | NULKA_ONLY | 6210052 | TARGET_HIT | NORMAL_HIT | 60.50 | 78.06 | not deployed / recovered |
| CG-52 | CHAFF_NULKA | 6210053 | TARGET_HIT | NORMAL_HIT | 60.52 | 73.38 | recovered / recovered |
| CG-52 | RADAR_MASTER_SILENT_ECM_ON | 6210054 | TARGET_HIT | NORMAL_HIT | 60.48 | 79.10 | not deployed / not deployed |
| CG-52 | ALL_RADIATION_SILENT | 6210055 | TARGET_HIT | NORMAL_HIT | 60.65 | 34.38 | not deployed / not deployed |

Totals: `TARGET_HIT 16`, `DEFENSE_INTERCEPT 1`,
`DECOY_SEDUCTION 2`, `UNCLASSIFIED 0`.

## Decoy evidence semantics

Each decoy now records request/deployment, physical observation, candidate
construction, selection, first and last selection, the first later anonymous
SHIP association, recovery after the last decoy selection, terminal hit, and
an explicit causal or unresolved reason.

- All six requested chaff paths and all six requested Nulka paths deployed,
  became physical returns, became candidates, and were selected.
- A later SHIP selection exists after the first decoy selection in all 12
  paths. This is the `firstShipRecoveryEvents: 12` fact.
- Ten paths have a SHIP association after the **last** decoy selection and
  end `SELECTED_THEN_RECOVERED_TARGET`.
- In the two bit-exact repeat shots, Nulka was selected again after an earlier
  ship recovery and remained the last valid, decoy-only association through
  qualified outward egress. Those two paths are `SEDUCED`, and the terminal
  after-action category is `DECOY_SEDUCTION`.
- There are no selected outcomes with insufficient evidence in this matrix.
- A terminal target hit is never used as substitute evidence for recovery.

The physical producer is still called exactly once and its return value is
unchanged. No diagnostic result is read by a tactical consumer.

## Defense evidence semantics

Configuration, engagement, hit, and kill are separate fields. Evidence comes
from actual auto-fire, close-in, gun-mount, physical-hit, or retirement events;
the terminal category is not used to invent an intervention.

- DDG hard-kill: enabled, engaged, hit, and kill are all true from the actual
  `INTERCEPT_KILL / 5in MFF / KILL` retirement event.
- CG hard-kill: enabled and engaged are true from three actual Mk45 MFF shots;
  kill is false and nonterminal hit is `null` because that event is not exposed.
- CIWS has no verified engagement in these two scenes. Where the complete
  close-in event snapshot is unavailable, `engaged` is `null`, not false.
- Chaff, Nulka, and ECM separately record requested, deployed/effective,
  observed, and selected states.

Legacy compatibility booleans now mean actual observed intervention only;
they no longer mean merely requested or enabled.

## EMCON evidence

The former `EMCON_ECM` case is correctly named
`RADAR_MASTER_SILENT_ECM_ON`. It uses the legacy radar master plus explicit
ECM technique requests: radar emission is zero, while allocator use, jammer
output, receiver coupling, and HOJ evidence are nonzero.

The two new `ALL_RADIATION_SILENT` cases use
`ownEcmCommandE('FULL')` followed by the same
`__EMCON_B_UI__.allRadiation()` ShipRuntime authority action as the current UI.
For DDG and CG alike, the technique request remains preserved while:

- allocator resource = 0
- active radar emitters = 0
- active ECM emitters = 0
- jammer receiver coupling = 0 W
- HOJ direct J/N = 0 and HOJ inactive
- every registered equipment decision reports `ALL_RADIATION_SILENT`

## Gates

- corrected fixed matrix: 19/19 terminal or qualified egress
- page/console errors and core failures: 0
- same-seed repeat: exact
- 1x / 8x / 16x physical result: exact
- decoy and defense structured-evidence consistency: PASS
- true global-silence request/output contract: PASS on DDG and CG
- common truth feedback, RNG consumption, save-schema mutation: 0
- protected product function hashes: exact
- Harpoon core/seeker/tube support: PASS on DDG and CG
- Kh-32: two fixed supporting boundary probes only, not a population result
- broad/MAX_THREAT regression: not rerun because product bytes are unchanged

The final workflow has a PR #78-specific job that independently rebuilds the
diagnostic, runs this 19-shot Chromium matrix, semantically compares all
simulated evidence while excluding only wall-clock elapsed time, reruns the
HP_A 19/19 outcome/save gate, rebuilds the report ZIP exactly, and uploads the
receipts. The exact final-head run is recorded in the PR receipt/comment.
