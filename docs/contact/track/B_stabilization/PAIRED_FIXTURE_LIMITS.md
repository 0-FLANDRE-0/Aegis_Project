# Original paired raid: intent, native progression, and evidentiary limits

Status: **read-only source/evidence review; original paired four failures remain unapproved**.
No browser or simulation was executed for the original static review below. A subsequently and separately authorized A/DDG pilot is recorded in `ORIGINAL_RAID_PILOT_RESULTS.md`; it changes the earlier unknown A/DDG progression facts, not the original paired approval status. No product/fixture/coefficient/expectation/tolerance was changed.

The old 32 s fixture is a deterministic state-regression workload, not an end-of-battle assertion. Its 120 s extension genuinely ran the native fixed ticks, but neither the initial eight Kh-32 nor the later background threats reached an archived terminal outcome. A new completed Kh-35U battle provides additional native-path evidence; it does **not** prove the original paired four state differences harmless or authorize their expected values.

## 1. Reproducible input provenance

Historical inputs were read from git objects, not assumed from possibly stale working files. Review revision: `5718f2d25f2e069f9ebd7948360fcf468bcdbb0b` on `track-b-stabilization-a`.

Command form: `git show 5718f2d25f2e069f9ebd7948360fcf468bcdbb0b:<path>`.

| Input | SHA-256 |
|---|---|
| `docs/multiship/H4/regression_baseline.py`, complete original file | `9c1c7239f31e9a0a15f3d752ab9a2925729758fd0f23fb879d5b7ec6e90479e0` |
| Its single AST string constant beginning `scenario=>`, unmodified | `1049cc9b70cd6e0718f33966a352cf3edfbf687fa5f64de38d2bba66c4ab2019` |
| Paired effective expression, adding only the existing observer/offboard readout | `3b54ea341abd67143df73dbc91aff1cd154d9f16a4958a6a9e5630b778b32d04` |
| Extended expression, changing only `raid:1920` to `raid:7200` | `89dbec8df636dbf8b6f2fe111413d4766c7a37358239f92c05e61c79f4487e1c` |

`B/paired_cause.py:25–32` extracts that original AST string and adds the two readouts. `B/paired_cause_120.py:15–16` changes only the tick horizon. These latter hashes match the archived `B/evidence/paired-cause-120/PLAN.json`. The source file's introductory contract explicitly says **diagnostic seeded measurements**, physical state/combat RNG comparison, and exclusion of EW/network/tactical/maneuver metadata and profiler. There is no threat-resolution stop condition in the original expression.

Native source references below use the decompressed TRACK-A main source `/dev/shm/track-b-baseline-source.js`, SHA-256 `8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e`. This equals the baseline source hash in all archived 120 s instrumentation receipts. Baseline and old B retain the same native fixed-tick body hash `a4360bd84ee5401aedfca45439dd0ff78a266101948433a006906b5eb72ad5b1` and installed pipeline wrapper hash `c4f08708d5810c3838be61e8c354e5709178929007056069674a4624b8ffc1b1`.

## 2. What the original expression actually sets up

The H4 expression (`regression_baseline.py:24–37`) enables terrain diagnostic bypass, calls `wip119DiagSpawnRealAsms({count:8,label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]})`, sets overall AUTO, and runs `runFramesToTicks(60,8,1920)`. It samples exported ship state/dynamics/RNG afterward. It does not reset through `_wip75ResetCase`, disable background patrols, require natural track initiation, wait for an impact, or ask whether every initial missile has ended.

| Native path | Actual behavior, not inferred from the scenario name |
|---|---|
| `wip119DiagSpawnRealAsms`, source L55138 | Creates eight real ASM objects, marks test fixtures, calls `_wip75SyncTrack` once for each. Bearings cycle, so two missiles share each of four launch bearings. |
| `_wip107SpawnRealAsm`, L54175–54180 | Kh-32 starts at **16 km horizontal range, 10,000 m altitude, inbound carrier velocity 250 m/s**. This is the full native launch, not a 16 km terminal dive injection or fixed-speed inbound threat. |
| `_wip75SyncTrack`, L53641–53650 | Creates/refreshes a TEST canonical track using fixture truth: confirmed, high hits/quality, ASM classification. This is initial diagnostic setup, so the original raid cannot establish a zero-track natural-acquisition contract. The expression does not repeat this call every tick. |
| `spawnEnemyMissile`, L31360–31435 | Native INS aim is the carrier's last-known ownship position plus its existing 0.15–0.6 km error. Kh-32 cruise target is **22–28 km**, phase starts `SEPARATE`, with 2.0–3.5 s separation; initial velocity is the carrier's. `cruiseSpeedMps:1200` and `terminalSpeedMps:1420` are fields, not a forced kinematic teleport to those speeds. |
| `updateAsmFlightPhysics`, L30445–30556 | Existing BODY-6DOF-LITE thrust, mass burn, drag, body/velocity lag and control limits integrate the physical velocity/position. No constant-speed fixture override was found on this live path. |
| Patrol/default AI, L30184–30286 and L55152–55337 | Patrol spawning remains eligible in SANDBOX when aircraft spawning is enabled. Existing aircraft can independently detect, launch sequential native ASM, and egress. The original expression does not suppress this path. |

The test loader (`docs/bunkerhill/K/browser_i.py:load`) pauses RAF advancement after departure. That does **not** explain a zero-tick raid: native `runFramesToTicks`/`advanceFrameNoRender` (L55019–55032) explicitly accumulate the supplied scale and call the complete `simulateFixedTick`. The fixed-tick body updates each live enemy missile at L55449–55451. All four archived 120 s runs report exactly **7,200 steps / 900 synthetic frames**, and their 32 s checkpoints match the preceding short runs in all **24/24** recorded checks. There is no source evidence here of an intentional `_testFixture` flight freeze.

### Repeated carrier geometry and legacy truth-seeded canonical files

This was also checked against the actual current B input `/dev/shm/track-b-stable-base.js`, SHA-256 `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`. Its `_wip107SpawnRealAsm` is at L54481–54486 and diagnostic arrow at L55444. The helper body is byte-identical to TRACK-A's L54175–54180 (body SHA `e6191e9da87ae48f2f958e21223c10ade1260402cd68859c4ade4c5e8aa22a81`); the trimmed complete diagnostic-arrow line likewise matches TRACK-A L55138 (line SHA `1cf0c333cf45e3b6d7251b7516528bf97a4eeba58f10e5df4627c161f3fa1ae8`). These source checks do not rely on the helper's name or its documentation.

For the original call, `ranges=[16]`, `bearings=[-60,-20,20,60]`, `count=8`. Both arrays are indexed modulo their lengths. Spawn indices 0/4, 1/5, 2/6 and 3/7 therefore repeat **the same carrier input geometry**: range, bearing, 10,000 m launch height, carrier heading/velocity and synthetic carrier ID `97032`. After every native spawn the diagnostic arrow calls `_wip75SyncTrack(em)`, then obtains its diagnostic canonical ID. Thus it deliberately starts two independently numbered, truth-seeded canonical files for each repeated launch geometry, rather than demonstrating that an anonymous RF processor had independently resolved those two missiles.

Distinguish that static carrier-input fact from the physical and observed outputs. `spawnEnemyMissile` uses the existing random INS aim error, cruise altitude and separation duration, and missile navigation has independent estimation error. Shared input geometry does **not** prove identical subsequent physical trajectories, identical noisy measurements, or unresolvable range/Doppler/elevation throughout the raid. Actual initial physical poses/IDs and later separation must be read from the new pilot's AFTER_ACTION records; the original 32/120 recorder did not preserve those trajectories.

This inherited setup creates a plausible legitimate ambiguity: two near-coincident anonymous returns/canonical predictions can both pass the same native gates, without a physical measured feature that establishes which numbered file should receive which plot. A complete valid near-tie need not be an unnecessary HOLD; forcing an ID-based choice simply to restore an old exact-state result would be unjustified. The documented early native B HOLD components (DDG tick194, CG tick197; `B/evidence/paired-cause-120/CRITICAL_NATIVE_EDGES.json` and paired causal report) must still be judged from their actual precomputed observed candidates/NIS/covariance, not from diagnostic truth IDs or a blanket “these were duplicates” inference. Those archived HOLD-edge windows cover the early ambiguity, not a full 120 s HOLD-duration census.

Accordingly, original paired four failures can reveal a policy-induced state change without proving that the old file assignment was uniquely correct or that the new HOLD was harmful. The reverse inference is also invalid: repeated launch geometry does not by itself approve the four failures. Preserve their strict failure status and separately report measured native outcome/resource/trajectory evidence. This is **legacy diagnostic fixture setup debt**, not a statement that the new production association path reads truth.

The new natural Kh-35U battle path (`B_stabilization/battle.js:39–43`) calls native spawn without `_wip75SyncTrack`, checks zero initial tracks, and then requires actual native sensor updates/AUTO release. Its archived qualification confirms that check. It usefully covers a different boundary and must remain a separately labeled fixture.

## 3. Why the Kh-32 setup can remain unresolved

The flight-profile branch is concrete: in `updateEnemyMissileBaseC52` L31639–31713, Kh-32 `CRUISE` tests **`own.z < em.cruiseAltM * 0.9` first**. It commands `CLIMB` before testing horizontal range against `diveStartKm`. Thus even a launch only 16 km away does not immediately become a terminal dive: it first aims for roughly **19.8–25.2 km altitude**, starting at 10 km. Seeker ON/TRACK is explicitly independent of the flight-profile transition. The horizontal channel can turn or use observed PN while the vertical channel still climbs.

This branch plus existing body dynamics makes a late/overshooting approach plausible. For illustration only, a 20° commanded climb through the required 9.8–15.2 km altitude gain corresponds to approximately 26.9–41.8 km horizontal travel. This is **not** an integrated trajectory or a proven lower bound: actual flight-path lag/overshoot, thrust, seeker state and turns matter. It must not be presented as the measured reason that any particular original missile was still alive at 120 s.

Terminal retirement is not based on initial range divided by nominal speed. Native updates retain the missile until, for example, actual collision, sea/terrain impact, native interception/structural failure, >380 km battlespace exit, or `life > maxLife` (600 s). Target memory/navigation and RF seeker estimates feed guidance; this review found no test-only command to chase current target truth or force a later terminal result.

**Limit of the historical archive:** the archived 120 s recorder stores outcome/damage flags but not each hostile's physical position, velocity, altitude, `phase`, `flight.cruisePhase`, `flight.timeS`, or `life`. Therefore that archive alone cannot distinguish continued climb, turn/re-approach, lost seeker, flyout, or another unresolved flight state, nor explain the absence of every SAM intercept. The separate new A/DDG pilot now measures continued climb at 32 s, diver/terminal descent at 120 s, one ESSM kill and seven physical surface-target impacts at 135–157 s; see `ORIGINAL_RAID_PILOT_RESULTS.md`. The corresponding B/DDG and CG comparative outcomes remain unmeasured by that single pilot.

## 4. The 21 alive ASM are not 21 old threats

Archived `paired-cause-120/<version>-<ship>.json.gz`, `events[].kind == 'ASM_NATIVE_STATE'`, records first observation of the eight initial Kh-32 immediately after tick 1. It first records the other **13 Kh-35U only from tick 4,937 onward**. These are later native aircraft launches, not the eight-object original fixture turning into 21 initial threats.

| Run | Later Kh-35U count | First recorded birth | Last recorded birth | Age available by t=120 s |
|---|---:|---:|---:|---|
| TRACK-A DDG / old B ACTIVE DDG | 13 each | 82.2833 s | 119.8167 s | about 0.18–37.73 s |
| TRACK-A CG / old B ACTIVE CG | 13 each | 82.2833 s | 119.8333 s | about 0.17–37.73 s |

Birth is observed post-tick, with at most one fixed-step uncertainty. These times are read from native object appearance; no extra spawn or motion was run. Existing patrol aircraft start 150–280 km away (`spawnPatrol` L30190–30223), with varied altitude, and native ASM release occurs according to their detection/launch-range conditions. The archive does not preserve the later missiles' exact release position, so no per-missile arrival time is claimed. Being alive less than 38 s after such a launch is not evidence of a frozen missile or failed defense.

The archived overall facts remain:

| Run | Live ASM at 120 s | Recorded SAM launches | Native intercept results | Ship hits / system hits | HP / flooding |
|---|---:|---:|---:|---:|---|
| TRACK-A DDG | 21 | 17 | 0 | 0 / 0 | 100 / 0 m³ |
| Old B ACTIVE DDG | 21 | 16 | 0 | 0 / 0 | 100 / 0 m³ |
| TRACK-A CG | 21 | 15 | 0 | 0 / 0 | 100 / 0 m³ |
| Old B ACTIVE CG | 21 | 19 | 0 | 0 / 0 | 100 / 0 m³ |

Read from `B/evidence/paired-cause-120/SUMMARY.json` and the four `*-SUMMARY.json` files. No sampler/runtime error was recorded. This establishes an unresolved checkpoint with different native resource use, **not** preserved ultimate combat outcome. In particular, all alive / HP 100 at that checkpoint is not an anti-ship kill, miss, or proof of unchanged future damage.

## 5. What the new natural Kh-35U battle adds—and cannot replace

`B_stabilization/battle.js:37–47` is an explicitly **new fixture**: fresh deterministic reset, patrol suppression, zero initial tracks, native Kh-35U spawn at low altitude near the ship, and complete native fixed ticks. It has a resolution stop condition plus five seconds of aftermath and retains after-action truth separately from observed track records. It does not seed canonical TEST tracks or repeatedly supply truth observations.

At review time the saved `evidence/battle-matrix/*-SUMMARY.json` for TRACK-A and old B SHADOW/ACTIVE report qualified completed battles for the DDG two-threat converging case, CG three-threat case, and DDG bearing-crossing case. The corresponding stored native results demonstrate actual AUTO release and terminal interceptions, with HP 100, rather than a timeout-only no-damage observation. The final stabilization candidate's result must still be read from its own pinned run; these earlier results are not a substitute for it.

Those battles can support the limited statement **“these measured low-altitude Kh-35U sensor→association→AUTO→weapon→terminal paths completed without the reported outcome regression.”** They cannot establish:

- equivalence of the initial TEST-track Kh-32 eight-threat geometry, high-altitude climb/diver/seeker path or its saturation/resource history;
- unchanged later damage in the original unsuppressed patrol scenario;
- that the old paired four exact-state differences are only harmless resource differences;
- that an ambiguity-policy change actually exercised/released the original paired ambiguity rather than avoiding it in another scenario;
- approval of strict expected values, seed 419025, or the separate seed 419012 cue difference.

Keep both sets: original strict failures and causal evidence, plus new native completed-battle coverage. Changing the fixture to make its threats arrive sooner, changing the original motion/AI, or replacing the failed baseline with the new scenario would defeat the historical comparison and was not done.

## 6. Longer-horizon decision and cost estimate only

A faithful longer original run would preserve the original commands, patrols and dynamics and change only the horizon, retaining references to the **initial eight** separately from later traffic. Whether 180/240/300 s is sufficient cannot be inferred from the archived flags. Before any such run, the proposal should explicitly retain passive hostile `life/position/velocity/flight-phase` and native terminal causes; without those it could consume more time and still leave the delay unexplained.

The code's 600 s lifetime provides only an eventual **administrative** retirement ceiling for the initial eight when complete native ticks continue, not a successful-defense horizon. With `life > maxLife`, allow a step beyond 600 s (floating-point boundary included). A MAX_LIFE disappearance must be reported as MAX_LIFE, never a defensive kill. Following all 21 objects first observed by t=120 would require up to approximately 720 s for that same ceiling; following every subsequently spawned object gives no fixed all-world-empty horizon while patrols remain enabled.

The measured historical four-page 120 s extension cost **275.490 s wall time**. A simple proportional extrapolation for the same four A/B × DDG/CG pages is:

| Proposed simulation horizon, not run here | Proportional four-page wall estimate |
|---|---:|
| 240 s | 551 s (9.2 min) |
| 300 s | 689 s (11.5 min) |
| >600 s | >1,377 s (>23.0 min) |
| approximately 720 s | 1,653 s (27.6 min) |

These are workload estimates, not promises: ongoing patrols, missile accumulation, later intercept/damage, tracing volume and machine contention may increase cost nonlinearly. A five-version matrix would cost more. **This document did not authorize a longer run.** Root later separately authorized one A/DDG pilot; its actual cost was 83.719 s wall because the cohort resolved and stopped at 162.133 s simulation, rather than requiring the 600 s cap. The remaining comparative original-cohort evidence is still needed to decide the original paired approval.
