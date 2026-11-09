# HP_A final report

## Status ledger

| State | Result |
|---|---|
| IMPLEMENTED | Common one-way ship outcome contract; player/NPC projection; save migration; authority-consumer and UI closure. |
| TESTED | Commit A audit/reproduction, B and C bounded product-path gates, actual SOV casualty/save path, one frozen-candidate MAX_THREAT broad run, and one skipped-scene harness recovery. |
| APPROVED | User-directed separation of physical survival, mission status and display HP; stored HP is compatibility-only. U4 PR #76 merge was separately pre-authorized. |
| UNRESOLVED | `CONFIRMED_ONLY` performance; inherited project debts; physical hull-break/longitudinal-collapse loss rule; external save-edit cross-field policy. |
| RELEASE | NO. HP_A is a PR-only handoff; no HP_A merge, release or tag. |

## Precondition and product

PR #76 was rechecked before HP work: base `main`, head
`88d5bd19a6f4279242a58d66a77aaf248c317c94`, Actions run `42518438311`
PASS, no unresolved review, and product bytes/SHA exact. It was merged using a
merge commit, producing HP_A base main
`82617839e64ea6b70d33ca55b13b3114cca62f3e`. No U4 release or tag was made.

- Base product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- Base: 22,195,923 bytes; SHA-256 `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- HP_A product: `Aegis_SIM_v48_WIP_HP_A.html`
- HP_A: 22,200,135 bytes; SHA-256 `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- Packed main: 40,927,903 bytes; SHA-256 `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`

## Sequential gates

### Commit A — audit and reproduction

The U4 product and relevant hashes were frozen without behavior changes. The
audit found 38 `shipHP` token occurrences and six invalid authority uses:
trusted stored player/NPC HP, a direct cookoff HP-zero assignment, and an HP-
based bottom-bar survival label. Every consumer is retained in the TSV.

The archived Kh-35 scene (seed 729300, 60 km, 15 kt) hit, but ended at display
cache HP 13.3712, `FLOODING`, reversible; the requested one-shot false-zero did
not reproduce and no seed search was used. The same exact U4 product's frozen
SOV casualty evidence did reproduce the general conflict: HP zero while
`FLOODING`, irreversible/lost false. Its later SINKING then LOST transition is
the independent physical-loss control.

### Commit B — common outcome ACTIVE

`shipOutcomeA(runtime)` derives `displayHp`, `damageSeverityPct`, physical
survival/afloat state and mission state without writing physical authority.
Player `shipHP` and NPC `runtime.health.shipHP` use the same projection after
impact and fixed damage/flood ticks. Built-in self-tests and transition-event
deduplication were added.

Phase-B product gate: 11/11 PASS, page/console errors 0. DDG/CG false-zero
guard, fixed Kh-35 physics, controlled SOV casualty, callback deduplication and
1x/8x/16x equality passed. Cross-process continuous JS values had only
last-bit variation (damage severity `1.42e-14`, flood/survival `3.05e-16`);
discrete state and RNG were exact. A diagnostic-only `1e-12` numeric comparison
was recorded; no game threshold or coefficient changed.

### Commit C — consumers, save and UI closure

- NPC/player restore no longer trusts serialized HP; it restores physical
  authority then recomputes the projection and records mismatch diagnostics.
- Player save carries the survival snapshot; old saves migrate by recomputing
  from existing damage/flood state. Invalid survival enums reject before mutation.
- Direct ammo-cookoff `shipHP=0`/false-loss text was removed; the existing
  event remains but only physical survival may declare loss.
- Bottom status, damage panel, survival banner, AAR and diagnostics expose
  mission/survival separately from display HP.
- Mission kill, irreversible loss and sunk transitions are distinct and
  deduplicated. Reset and runtime preparation establish fresh baselines.

Candidate audit: 30 HP occurrences, invalid authority uses 0, forbidden
patterns 0. Protected physics function hashes are exact. The C product-path
gate passed 19/19 with page/console errors 0. Actual SOV casualty verification
preserved four contacts and completed FLOODING → CRITICAL → SINKING → LOST.

## Frozen-candidate broad regression

The product was frozen at SHA `9121c448…d24836fa` before the one and only
MAX_THREAT broad invocation. Raw wall time was 2,383.73 seconds.

| Suite | Raw result |
|---|---:|
| HP_A static integrity | 11/11 PASS |
| Native 13 | 364/364 PASS |
| ESM_A → HP_A paired | 36/42; six `samePhysicalState` raw failures retained |
| HP_A two-run determinism | 42/42 PASS |
| Current EMCON UI | 14/14 PASS |
| Chromium UI | 213/213 PASS |
| Actual WebGL observed-world | 29/29 PASS |
| U4 representative scenes | raw 0/0; inherited U4 byte pin rejected before browser |

The paired six are authorized HP_A save-contract deltas, not hidden passes.
Idle/raid differ only by the new survival snapshot. The damaged fixture edits
flooding after export while leaving that newly authoritative snapshot stale;
the candidate therefore preserves the supplied pose/timer before fixed ticks.
In all six, final discrete HP/survival/water/module/crew state, combat RNG,
hull damage/inventory, observer/offboard state and fault-free status are exact.
Raw assertions remain failed and no expectation/tolerance was updated.

The final scene script asserted U4's fixed byte count before launching a
browser, so it exercised zero game code. A single isolated harness recovery
changed only the expected product byte count and SHA; the same scene body and
same HP_A product then passed 19/19, including two-run determinism, ASM,
Harpoon, SM-2, ESSM, SM-6, RAM, 1x/8x/16x/64x, ESM and lifecycle checks. The
broad suite was not rerun. Raw and reconciled evidence are both retained.

## Physical/RNG preservation

No warhead, penetration, fragment, blast, flooding, damage weight,
longitudinal strength, propulsion, seeker, fuze, guidance, weapon or combat RNG
coefficient changed. `createShipSurvivalV1`, `damageFloodImpactV1` and both
`getShipLongitudinalStrengthV48Wip03` bodies are byte-identical to U4. The
fixed Kh-35 scene preserved flight, crew, survival, flood, damage severity and
RNG within the documented existing numeric precision; discrete outputs and RNG
were exact.

## Evidence map

- Commit A: `COMMIT_A_BASELINE.md`, `evidence/commit-a/`
- Commit B: `COMMIT_B_OUTCOME.md`, `evidence/commit-b/`
- Commit C: `evidence/commit-c/`, `audit_candidate.py`, `run_contract_gate.py`
- Broad raw: `FINAL_REGRESSION.json`, `evidence/final-regression/`
- Reconciliation: `FINAL_REGRESSION_RECONCILIATION.json`,
  `analyze_paired_delta.py`, `run_scene_harness_recovery.py`
- Reproduction: `build_product.py`, `outcome_contract_a.js`, all gate scripts

## Delivery boundary

The executable ZIP contains only the HP_A HTML. The report ZIP contains no
HTML and carries reports, raw evidence, scripts, manifest and checksums. The
candidate workflow may rebuild and run bounded gates; it must not repeat the
one-shot broad regression. Merge, release and tag remain user decisions.

The current-product manifest is bound to branch `hp-a` and PR #77. Package
membership is recorded in `PACKAGE_MANIFEST.md`; ZIP identities are detached
in `PACKAGE_CHECKSUMS_v48_WIP_HP_A.txt` to avoid circular archives.
