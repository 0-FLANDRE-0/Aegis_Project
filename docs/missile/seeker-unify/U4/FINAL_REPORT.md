# SEEKER_UNIFY_U4 final report

## Status ledger

| State | Result |
|---|---|
| IMPLEMENTED | A — explicit bistatic SARH adapter; B — passive RAM RF/IR adapters and narrow emitter-signal ownership fix; C — common anonymous association and state-event engine, all ACTIVE. |
| TESTED | A/B/C deterministic limited gates and exactly one frozen-candidate MAX_THREAT broad regression; byte-exact rebuild and packed-main syntax gate. |
| APPROVED | Structure-only SHADOW equivalence and the directive-authorized RAM ownership correction. Expected values and tolerances were not changed. |
| UNRESOLVED | `CONFIRMED_ONLY` performance, inherited project debts, SOV sensor/weapon integration, communication EMCON and the separate Kh-32 investigation. |
| RELEASE | NO. The U4 PR is the user merge boundary; no merge, release or tag was created. |

## Product

- Baseline main: `f17d3777a625699ab26f6a40de80a383f675ae85`
- Baseline: `Aegis_SIM_v48_WIP_ESM_A.html`, 22,182,527 bytes, SHA-256 `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`, 22,195,923 bytes
- Product SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- Packed-main SHA-256: `e06c2e6133b66fe8be2f6c1305b39473a7776176680390a45673e7487e9a462e`

## Sequential implementation

### A — SARH bistatic adapter

SARH remains an explicitly bistatic observation. The physical front end owns
the SPG-62 opportunity and allocation, transmitter and receiver kinematics,
both beams, both LOS legs, bistatic range/path-rate, clutter/RCS/power and the
weapon-local RNG. Only anonymous SI-unit echoes, cells, measurements and 4x4
covariance cross the common boundary. The downstream tactical carrier remains
the legacy value, preserving UI, guidance and source-arbiter contracts.

The limited gate compared 20,088 bistatic-power values and 411,299 cell
decisions with zero mismatches. Independent TX LOS, RX LOS, TX beam and RX
beam removal failed closed. The live SM-2 surface-SARH flight retained local
measurement guidance and physical contact. Protected allocation, body flight,
source arbitration, RCS and beam-gain hashes remained unchanged.

### B — RAM passive RF/IR adapters

RAM RF and IR are distinct `PASSIVE_RF_2D` and `PASSIVE_IR_2D` observations,
not synthetic active-radar echoes. Both player and owner/NPC declarations use
the same anonymous angle/covariance/quality boundary while preserving their
hardware-context candidate synthesis and owner-local RNG. IDs, faction and
truth references are not copied.

The baseline physical emitter strength incorrectly read the receiving/local
missile seeker's track quality. ACTIVE removes that reverse ownership while
retaining the existing nominal expression `0.65 + 0.55 * 0.75 = 1.0625`.
Emission enablement, propagation, sensitivity, Pd, gates, timing and RNG were
not tuned. RF-first, IR-only, RF→IR takeover, RF/IR dropout, MEM return and
two-missile isolation passed. The RF direct-flight geometry changed only along
the authorized ownership path; the result remained finite with no sea impact.

### C — common association and state engine

ASM, Harpoon, SARH, ARH and RAM route anonymous numeric scores and local-track
events through the common engine. Their front ends still own prediction,
covariance, NIS/absolute gates and measurement generation. HOJ, Harpoon
route/INS, SARH↔ARH arbitration, RAM MEM/RF/IR authority, guidance and release
authority remain weapon hooks. There is no cross-weapon mutable tactical
singleton, common RNG call or new save field.

C SHADOW performed 5,002 association and 1,648 state comparisons with zero
mismatches. Commit-B baseline, C SHADOW, C ACTIVE and a fresh-page ACTIVE
repeat produced exact tactical results for representative ASM, Harpoon, SM-2,
ESSM Block 2 and RAM paths. Lifecycle events covered measurement acquisition,
hit accumulation, coast, reacquire, signal/illumination loss, timeout/lost/off
and destroy/retire.

## Final broad regression — exactly one execution

The product was frozen before this run. Total wall time was 2,372.95 seconds.

| Suite | Result |
|---|---:|
| Static integrity | 13/13 PASS |
| Native 13 | 364/364 PASS |
| ESM_A → U4 paired DDG/CG idle/raid/damaged | 42/42 PASS |
| U4 two-run paired determinism | 42/42 PASS |
| Current EMCON UI | 14/14 PASS |
| Chromium UI | 213/213 PASS |
| Actual WebGL observed-world | 29/29 PASS |
| U4 representative scenes | raw 15/19; effective 19/19 after retained-evidence review |

Representative actual paths include ASM acquisition/TRACK, Harpoon native
contracts, SM-2 SARH proximity kill, ESSM SARH→ARH proximity kill, finite SM-6
dual-mode flight and RAM RF↔IR transitions. Page/console errors were zero.

### Retained raw harness assertion defects

`u4-seeker-scenes` retained four raw failures; they were not erased or rerun:

- `oneEightSixteenPhysicsExact` and `sixtyFourPhysicsExact` included diagnostic
  post-terminal display-batch step counts. Terminal position, velocity, mass,
  target state, lifetime and RNG are byte-exact at 1×/8×/16×/64×.
- `sixtyFourStepCapObserved` used the reversed frame-count inequality. Recorded
  frames are exactly `ceil(917 / scale)`; terminal-batch step overshoot is less
  than the selected scale.
- `esmRuntimeAndUiPresent` required body text on an unopened zero-contact view.
  Runtime schema is operational with truth/automatic authority false, and the
  packed candidate contains the ESM CIC/map render functions and `__ESM_A__`.

`FINAL_REGRESSION_REVIEW.json` performs an offline review of only those already
recorded values and frozen product bytes. It reports effective 19/19,
unexplained failures 0, product mutation after broad false, broad rerun false,
expectation changes 0 and tolerance changes 0. The corrected predicates are
kept for future runs, but the original evidence remains authoritative raw data.

## Information, RNG and lifecycle boundaries

- Truth objects are limited to physical echo/heat/emitter synthesis. Common
  DTO, association and state decisions contain no entity/profile/faction/
  hostile identifiers or truth position.
- The common engine consumes no RNG. Existing per-weapon streams and advance
  order remain with the weapon front ends.
- No operational save schema or field was added. Existing missile owners keep
  initialization, reset, import/export where supported, destroy and retire.
- Release authority, ROE, sensor performance, guidance laws, damage and ship
  physics were not redesigned or retuned.

## Evidence map

- Baseline: `U4_BASELINE_AUDIT.md/json`, `PLAN.md`
- A: `A_REPORT.md`, `A_GATE.json`, `BUILD_A_SHADOW.json`, `BUILD_A_ACTIVE.json`
- B: `B_REPORT.md`, `B_GATE.json`, `BUILD_B_SHADOW.json`, `BUILD_B_ACTIVE.json`
- C: `C_REPORT.md`, `C_GATE.json`, `BUILD_C_SHADOW.json`, `BUILD_C_ACTIVE.json`
- Final: `BUILD_FINAL.json`, `FINAL_REGRESSION.json`,
  `FINAL_REGRESSION_REVIEW.json`, `evidence/final-regression/`
- Reproduction: `build_product.py`, `run_a_gate.py`, `run_b_gate.py`,
  `run_c_gate.py`, `run_final_regression.py`, `run_u4_final_scenes.py`

## Delivery boundary

- Executable HTML ZIP contains only the product HTML.
- Report ZIP contains reports, raw evidence, reproduction tools, diffs,
  archive handoff documents and checksums, and contains no HTML.
- Candidate Actions rebuilds the product exactly, checks the packed script and
  runs the limited C gate. It does not repeat the broad regression.
- PR creation is allowed; merge, release and tag remain user decisions.
