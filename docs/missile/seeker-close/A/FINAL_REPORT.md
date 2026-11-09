# SEEKER_CLOSE_A final report

## Outcome

SEEKER_CLOSE_A is complete as a **product-unchanged diagnostic closure**.
No current-product seeker ownership, unit, association, or state-transition
contract defect was reproduced, so Commit C was intentionally omitted.  The
authority product remains HP_A without repacking or byte changes.

## State ledger

| State | Result |
|---|---|
| IMPLEMENTED | Reusable AFTER_ACTION terminal classifier, physical-return observer, fixed DDG/CG fixture, decoy-stage trace, deterministic runner, HP/current-product gates |
| TESTED | 17 terminal Kh-35U cases; DDG/CG; no-defense, hard-kill, chaff, Nulka, combined decoy, EMCON/ECM; repeat determinism; 1x/8x/16x; Harpoon; two Kh-32 boundary probes; HP/save outcome gate |
| APPROVED | HP_A precondition merge only, as authorized by the directive; historical values remain reference-only; no expectation/tolerance update |
| UNRESOLVED | Historical Kh-32 60 km 0/20 population is not reproduced as a population; current two fixed seeds split hit/miss and do not replace it. `CONFIRMED_ONLY` performance remains unverified. Inherited regression debts remain open. |
| RELEASE | None. No release, tag, or SEEKER_CLOSE_A product was created. PR merge remains a user decision. |

## Precondition and frozen authority

- Repository: `0-FLANDRE-0/Aegis_Project`
- pre-merge main: `82617839e64ea6b70d33ca55b13b3114cca62f3e`
- verified HP_A PR #77 head: `a3e45f7cfb5cecc1f7180e24ee3fbf35197458f5`
- verified candidate Actions: run `42545220615`, SUCCESS
- unresolved review threads: 0; mergeable state: CLEAN
- verified HP_A product: 22,200,135 bytes,
  `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- verified packed main: 40,927,903 bytes,
  `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`
- merge method: merge commit; actual merge commit:
  `78b01165bad64e9c6dc384ff070a70f868da5113`
- post-merge bytes/SHA readback: exact

`Aegis_SIM_v48_WIP_HP_A.html` is still the formal authority.  The injected
`Aegis_SIM_v48_DIAGNOSTIC_SEEKER_CLOSE_A.html` was used only locally for
after-action instrumentation and is neither a product nor a release artifact.

## Historical evidence versus current measurement

Historical TRACK-B R4 and TRACK-C evidence is retained as an alarm only:

| Population | Initial ASMs | Seeker loss | Decoy lure | Other egress |
|---|---:|---:|---:|---:|
| TRACK-B R4 | 320 | 36 | 0 | 3 |
| TRACK-C | 320 | 34 | 0 | 3 |

The current bounded fixture is a different population and is not a rate
comparison or tuning target:

| Current HP_A fixed cases | Count |
|---|---:|
| TARGET_HIT | 14 |
| DEFENSE_INTERCEPT | 1 |
| KINEMATIC_MISS | 2 |
| all other categories | 0 |
| UNCLASSIFIED | 0 |

Detailed shot rows and all required fields are in
`evidence/limited/RESULTS.json` and `SHOTS.csv`.

## Seeker and decoy conclusions

The Kh-35U terminal set observed at most 19 state transitions and no direct
`ACQUIRE -> SEARCH` return.  The bit-exact repeated miss retained guidance,
coasted and reacquired real returns several times, passed the ship by
128.87 m, and reached the fixed outward-egress endpoint at 162.43 s.  It is a
kinematic miss after real sensor recovery, not a permanent valid-candidate
drop or state-owner overwrite.

Every requested chaff and Nulka was deployed by the real game path.  In all
six requested cases for each decoy type, the return was physically visible,
constructed as a candidate, selected, and then superseded by a recovered ship
contact.  The final stage is `SELECTED_THEN_RECOVERED_TARGET` 12/12 and
`SEDUCED` 0.  This result does not justify artificial decoy amplification or
seeker weakening.

The Kh-32 supporting probe is deliberately separate.  Both 60 km fixed seeds
used `SHIP` rather than the Harpoon diagnostic surface target and reached
TRACK.  DDG hit after 29 acquire retries; CG ended in a normal miss after a
shorter coast/reacquire history.  The diagnostic-only transition guard was 64
and the largest observed path was 61.  These two shots are not used as a
replacement for the historical 0/20 survey.

## Integrity and tests

### Diagnostic-only gate

- status: PASS; 17 terminal shots; elapsed 95.17 s
- page/console errors and core failures: 0
- same seed: exact
- 1x/8x/16x: exact physical result
- common anonymous contract: PASS
- common-layer RNG consumption: 0
- common save-schema mutation: 0
- classifier tactical-consumer reads / feedback: 0
- protected function bodies: exact HP_A hashes
- fixture contamination guard: PASS
- Harpoon core/seeker/selection: PASS on DDG and CG

### Current HP_A outcome/save gate

- status: PASS; 19/19 checks; elapsed 137.06 s
- DDG and CG survival-authority save round-trip: PASS
- stale stored HP ignored and audited: PASS
- mission kill separated from irreversible loss: PASS
- invalid save fail-closed with zero mutation: PASS
- SOV recoverable/irreversible flooding and exactly-once loss callbacks: PASS
- Kh-35 physics compatibility: PASS
- 1x/8x/16x outcome physics: exact

### Broad regression policy

No new broad regression was run.  The formal product is byte-identical HP_A,
whose frozen MAX_THREAT broad evidence already belongs to that exact SHA.
Running it again would violate the product-unchanged closure rule.  The
current work instead proves exact product SHA, diagnostic non-intrusion,
protected hashes, fixed-step determinism, save/HP preservation, and bounded
current-product behavior.

## Changed and preserved code

No product function was changed.  Repository changes are diagnostic scripts,
evidence, and documentation only.  `DIAGNOSTIC_BUILD.json` records exact
before/after hashes for the common selector/policy, ASM observation,
association, measurement, state update, enemy missile flight, Nulka, chaff,
Harpoon, ship outcome, flooding, and operational-save exporter.

The after-action classifier may inspect terminal truth only after the result.
It never writes selected lock, seeker target, INS target, ROE, guidance, or
weapon state.  The physical-return wrapper calls the original producer once,
does not call RNG, and stores diagnostic copies only.

## Inherited debt and exclusions

- `CIWS_SEED_419025_FAIL`, paired observer delta 2, and the fixed WIP12D
  CIWS time-scale debt remain inherited; none was reclassified here.
- `CONFIRMED_ONLY` performance remains UNVERIFIED.
- SOV Mineral/Band Stand/MR-184, Moskit cue, communications EMCON,
  FIRE_CONTROL registry, and enemy-aircraft rebuild were out of scope.
- A full Kh-32 population study remains separate unless it demonstrates the
  same current contract defect.

## Delivery

- branch: `seeker-close-a`
- pull request: recorded after remote creation in the PR receipt/body
- merge: not performed
- release/tag: not created
- executable: unchanged HP_A HTML ZIP
- report package: HTML-free SEEKER_CLOSE_A report ZIP
- next stage: `integrated baseline freeze -> engagement/defense OODA`
