# SEEKER_CLOSE_A Commit B — current-product bounded diagnostic

Status: **PASS / NO PRODUCT CONTRACT DEFECT REPRODUCED**
Authority product: `Aegis_SIM_v48_WIP_HP_A.html`, 22,200,135 bytes, SHA-256
`9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`.

The formal product was not modified.  The diagnostic HTML is a test-only
derivative; all protected seeker, guidance, decoy, damage, HP, and save
function bodies have the exact HP_A hashes recorded in
`DIAGNOSTIC_BUILD.json`.

## Fixture and limits

The exact historical TRACK-C fixture was not retained in executable form.
The replacement is a fixed terminal Kh-35U fixture at 18 km, 300 m/s and
15 m altitude.  There is no seed search.  DDG uses 11 cases and CG uses six,
below the 30-case branch cap.  Normal cases have a 100 s observation window;
the same-seed miss pair uses 180 s so that the already-passed missile can
reach the fixed 30 km / 10 s outward-egress endpoint.

The 64-transition audit cap is diagnostic-only.  It is not passed into the
game and does not change a seeker threshold.  The Kh-35U terminal cases
reached at most 19 transitions.  A separate fixed Kh-32 60 km boundary probe
reached 61 transitions and is reported below rather than hidden.

## Terminal results

| Ship | Condition | Seed | Category | Native cause | End s | Closest m | Transitions | Chaff / Nulka |
|---|---|---:|---|---|---:|---:|---:|---|
| DDG-119 | no defense | 6209793 | TARGET_HIT | NORMAL_HIT | 60.55 | 58.09 | 2 | not deployed / not deployed |
| DDG-119 | hard kill only | 6209794 | DEFENSE_INTERCEPT | INTERCEPT_KILL (5in MFF) | 43.22 | 5,192.60 | 2 | not deployed / not deployed |
| DDG-119 | chaff only | 6209795 | TARGET_HIT | NORMAL_HIT | 61.20 | 41.36 | 7 | selected, target recovered / not deployed |
| DDG-119 | Nulka only | 6209796 | TARGET_HIT | NORMAL_HIT | 60.50 | 76.14 | 2 | not deployed / selected, target recovered |
| DDG-119 | chaff + Nulka | 6209797 | TARGET_HIT | NORMAL_HIT | 60.65 | 44.90 | 6 | selected, target recovered / selected, target recovered |
| DDG-119 | EMCON + ECM | 6209798 | TARGET_HIT | NORMAL_HIT | 60.55 | 56.94 | 2 | not deployed / not deployed |
| DDG-119 | clock 1x | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | 2 | not deployed / not deployed |
| DDG-119 | clock 8x | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | 2 | not deployed / not deployed |
| DDG-119 | clock 16x | 6209799 | TARGET_HIT | NORMAL_HIT | 60.57 | 58.42 | 2 | not deployed / not deployed |
| DDG-119 | deterministic A | 6209800 | KINEMATIC_MISS | — | 162.43 | 128.87 | 19 | selected, target recovered / selected, target recovered |
| DDG-119 | deterministic B | 6209800 | KINEMATIC_MISS | — | 162.43 | 128.87 | 19 | selected, target recovered / selected, target recovered |
| CG-52 | no defense | 6210049 | TARGET_HIT | NORMAL_HIT | 60.68 | 20.69 | 2 | not deployed / not deployed |
| CG-52 | hard kill only | 6210050 | TARGET_HIT | NORMAL_HIT | 60.62 | 41.40 | 2 | not deployed / not deployed |
| CG-52 | chaff only | 6210051 | TARGET_HIT | NORMAL_HIT | 60.50 | 74.99 | 2 | selected, target recovered / not deployed |
| CG-52 | Nulka only | 6210052 | TARGET_HIT | NORMAL_HIT | 60.50 | 78.06 | 2 | not deployed / selected, target recovered |
| CG-52 | chaff + Nulka | 6210053 | TARGET_HIT | NORMAL_HIT | 60.52 | 73.38 | 2 | selected, target recovered / selected, target recovered |
| CG-52 | EMCON + ECM | 6210054 | TARGET_HIT | NORMAL_HIT | 60.48 | 79.10 | 2 | not deployed / not deployed |

Totals: `TARGET_HIT 14`, `DEFENSE_INTERCEPT 1`, `KINEMATIC_MISS 2`,
`UNCLASSIFIED 0`.  These 17 fixed cases are a cause audit, not a hit-rate or
decoy-rate estimate, and are not compared numerically with the historical
320-shot population.

## Seeker-loss and SEARCH/ACQUIRE finding

- The terminal Kh-35U set had zero direct `ACQUIRE -> SEARCH` returns.
- The repeated-seed miss did not lose a permanently valid candidate.  It
  entered TRACK, used COAST/REACQUIRE when returns disappeared, recovered the
  ship several times, passed at 128.87 m, and eventually left the 30 km
  battlespace endpoint.  Both repetitions are bit-exact.
- The observed gate reasons (`DISTRIBUTED_BACKGROUND_EVIDENCE`,
  `ASSOCIATION_GATE`, `BELOW_DETECTION`, and `NO_VISIBLE_RF_RETURN`) coincide
  with periods where the physical return/candidate history changed.  No
  common/weapon state overwrite, per-tick memory reset, duplicated covariance
  penalty, or valid-candidate permanent exclusion was reproduced.
- Therefore the two misses are classified as kinematic misses after genuine
  sensor reacquisition, not as a common-state contract defect.

## Chaff and Nulka finding

All six chaff-requested cases and all six Nulka-requested cases launched the
real game decoy.  Both return types appeared in the real RF-return producer,
passed candidate construction, and were selected.  Every selected decoy was
then followed by a valid ship selection; the final stage is
`SELECTED_THEN_RECOVERED_TARGET` for all 12 requested decoy paths.

Thus the observed seduction count of zero is not caused by no deployment,
no visibility, DTO loss, or permanent gate exclusion.  In this fixed scene
the seeker recovered the stronger/consistent ship contact.  No signal, RCS,
Pd, FOV, gate, memory, or decoy-strength tuning is justified.

## Supporting paths

- Harpoon physical acquisition reached `OFF -> ACQUIRE -> TRACK` on DDG and
  CG; the inherited core, seeker and tube-selection audits all passed.
- Two fixed Kh-32 60 km probes were run before the Harpoon fixture so a
  diagnostic surface target cannot contaminate association.  Both associated
  only `SHIP` returns and reached TRACK.  DDG seed 6210336 hit at 203.15 s
  after 29 `ACQUIRE -> SEARCH` returns; CG seed 6210337 ended `NORMAL_MISS`
  at 75.00 s after a shorter COAST/REACQUIRE path.  This two-seed boundary
  probe is supporting evidence, not a replacement for the historical 0/20
  survey.  The DDG path eventually tracked and hit, so its repeated attempts
  are retained as a separate Kh-32 observation rather than used to tune the
  common state machine.

## Gates

- page/console errors: 0
- core self-test failures: 0
- same-seed repeat: exact
- 1x / 8x / 16x physical result: exact
- common-layer truth fields: 0; common-layer RNG consumption: 0
- common save-schema mutation: 0
- diagnostic tactical-consumer reads/feedback: 0
- protected product function hashes: exact
- HP_A current-product contract gate: PASS, 19/19 checks, 137.06 s
  (DDG/CG save round-trip, mission/survival/display split, invalid-save
  zero-mutation, SOV flooding/loss callbacks, and 1x/8x/16x)

Evidence: `evidence/limited/RESULTS.json`, `SHOTS.csv`, `SUMMARY.json`, and
`evidence/hp-contract/contract-gate.json`.

## Commit C decision

**No Commit C product fix is created.**  No present-product ownership, unit,
or state-transition defect was reproduced.  The only corrections made during
Commit B were to the after-action diagnostic itself: allow the fixed miss to
reach an egress endpoint, read the existing retirement cause when classifying
a defense kill, and isolate the Kh-32 fixture from the Harpoon test target.
None of these values enters seeker, guidance, ROE, damage, or weapon code.
