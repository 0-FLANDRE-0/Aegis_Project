# AEGIS v48 WIP11C — ASM wreckage and water-surface effects

## Scope

- Baseline: `archive/v48/WIP11B/Aegis_SIM_v48_WIP11B.html`
- Keep an intercepted ASM's physical remains after the live threat is retired.
- Couple wreck breakup and presentation to the existing ASM component, structural and warhead state.
- Advance wreck motion under fixed-step drag and gravity until ship, terrain, water or bounded retirement.
- Add water-entry and near-surface explosion event/presentation layers.
- Make burning wreck fire/black smoke easier to read and keep interceptor trails longer but spatially sparser under a bounded, age-thinned render budget.
- Keep ASM smoke at high altitude only, without changing ASM flight or guidance authority.
- Keep a bounded BDA coast after an intercept, immediately suspend AUTO fire, release fire-control support on direct breakup, and retire the original missile's ghost-MEM presentation after confirmation.
- Carry the combat-system track assigned to SM-2/ESSM, RAM and Phalanx through terminal damage and breakup so anonymous SPY tracks receive the same BDA retirement as truth-bound diagnostics.
- Correlate tightly matching pre-effect sibling/coast files to the same terminal-effect BDA without reading truth, while allowing any coherent post-effect measurement to reopen the contact.
- When a preceding fuze-only event is promoted to physical breakup, rebase its effect epoch, terminal report and return-resolution state to the real breakup tick so the last same-tick SPY plot cannot masquerade as a post-kill return.
- Transfer every weapon, CIWS, SPG-62 and selected-lock owner when a replacement alias appears on the original track's first LOST assessment frame.
- Retire a steeply descending, no-return ASM coast as an observed sea impact without reading enemy truth, while protecting the active-ship envelope and reopening on any coherent return.
- Preserve the commanded SM-2/ESSM launch azimuth while the physical Mk41 in-cell position and velocity remain constrained to the ship deck-normal axis.
- Preserve all WIP11B operational-import safety and WIP11 combat/physics/rendering contracts.

WIP11C does not implement terminal-ballistics generalization, a persistent ocean debris ledger, underwater blast damage, gun firing, exterior ballistics or FCS.

## Threat and wreckage authority

`AEGIS_ASM_WRECKAGE_V48_WIP11C` separates combat authority from physical remains:

- a kill immediately retires the live ASM and its truth association;
- any coasting sensor track can no longer resolve the retired truth object;
- the new wreck pieces live only in `ENGAGEMENT_RUNTIME.world.entities.asmWreckage`;
- wreckage cannot be tracked, assessed as a hostile missile, engaged or fed back into intercept probability;
- wreckage and water events are combat transients and remain excluded from the operational snapshot.

All SAM/RAM kill, accumulated intercept structural failure, Phalanx kill/failure, ASM warhead airburst and delayed structural-failure paths queue the same retirement contract.

## Kill assessment and AUTO cease fire

WIP11C adds `KILL_ASSESSMENT` to the observed-track operational contract without turning world truth into a radar decision input:

- every interceptor terminal report can publish a `FUZE_DETONATION` event;
- physical ASM breakup publishes the stronger `DIRECT_BREAKUP` event in the same fixed tick, using friendly-weapon engagement provenance rather than requiring a truth-to-track reverse lookup;
- SM-2/ESSM carries `assignedTargetId`, RAM carries `targetId`, and each Phalanx projectile retains the mount's track ID from its firing instant; surviving damage stores that provenance for later warhead airburst or delayed structural failure;
- each `DIRECT_BREAKUP` terminal-effect report carries the effect step plus SI position and velocity; a sibling/coast observed track is correlated to the same BDA only when it existed before the effect, has no later measurement, remains missile-like and passes tight bounded position/velocity gates;
- correlated sibling files do not become permanently dead: an accepted coherent measurement later than the effect immediately clears that BDA evidence and reopens observed `THREAT` or `HARMLESS` assessment;
- truth-bound diagnostic fixtures retain a compatibility lookup, but live anonymous SPY files do not depend on `truthRef` or the truth object ID;
- the later 5 Hz cleanup/telemetry echo is merged with the same terminal event and cannot downgrade a `DIRECT_BREAKUP` assessment back to the longer fuze-only confirmation window;
- if an earlier `FUZE_DETONATION` record is promoted to `DIRECT_BREAKUP`, the merged record takes the real breakup step/time, terminal position/velocity and direct-confirmation window and clears any stale return-resolution marker; a measurement must be strictly later than that rebased effect tick to reopen the contact;
- either report immediately changes the coasting track to `KILL_ASSESSMENT / WITHHELD`, so VLS AUTO, CIWS, soft-kill allocation and SEMIAUTO designation stop treating it as a live threat;
- `DIRECT_BREAKUP` immediately removes target-level SPG-62 live ownership and reservations, clears SARH illumination and DL support from surviving interceptors, and suppresses new SPY missile-support/handoff tasks for that target;
- direct breakup requires `0.35 s` with no coherent return before `DESTROYED`; fuze telemetry alone requires `1.5 s`;
- during that short assessment window the PPI uses an amber `BDA` cross rather than a red live-ASM symbol; after confirmation it uses a grey `KILL` cross for `1.25 s`, then hides the original missile's ghost MEM track;
- the internal track record can remain available to anonymous search-plot association even after presentation suppression, but it has no display or fire-control quality and cannot hold an illuminator;
- an accepted measurement with a step later than the effect report resolves the BDA event and restores the normal observed `THREAT` or `HARMLESS` assessment;
- when a replacement alias appears on the exact 5 Hz frame that the original file first becomes LOST, the post-loss alias pass transfers SM-2/ESSM assignment, RAM target, Phalanx engagement ID, CIWS mount tracking/cue, SPG-62 live/reservation ownership and the selected lock to the replacement ID;
- `wip121RecordFriendlyInterceptEvent()`, `wip121TerminalEffectCorrelationCandidates()`, `wip121CorrelateTerminalEffectTracks()`, `wip121KillPlausibility()`, `wip121TargetSupportBlocked()`, `wip121BdaTrackPresentation()`, `wip121ReleaseTargetFireControlSupport()` and `wip118UpdateKillAssessment()` do not read `truthEnded`, `enemyMissiles` or `truthObjectForTrackV27()`.

The deterministic browser fixtures verified `THREAT → KILL_ASSESSMENT → DESTROYED → hidden ghost MEM → THREAT`, released a primed SPG-62 reservation and all DL/SARH mirrors on direct breakup, withheld engagement authority during BDA, and launched zero additional AUTO rounds after the breakup report. A duplicate-file regression creates a second pre-effect `MEM-?` coast for the same kinematics, confirms both files receive the breakup BDA and disappear, then proves a coherent post-effect return reopens the sibling rather than being permanently suppressed. A first-LOST-frame regression also confirms full weapon and SPG ownership moves to the replacement alias. The actual anonymous-SPY regression uses full ESSM flight rather than a truth-bound BDA fixture: seed `991212` produced `PROX_DETONATION_KILL`, immediate `DIRECT_BREAKUP / KILL_ASSESSMENT`, no SPG reservation or illumination, and zero displayed ASM tracks after the kill-mark hold. A second real-flight regression uses an anonymous Kh-32 track at seed `112000`, places a preceding fuze echo five ticks before ESSM `4` achieves the physical `PROX_DETONATION_KILL`, and verifies that promotion rebases the event from step `840` to the real breakup at step `845`. The SPY plot also stamped at `845` is therefore not treated as a later coherent return: AUTO fires no additional round, SPG/DL/SARH support remains released, the original ASM presentation retires, and the independently simulated wreckage continues.

## Kh-32 observed sea-impact coast and Mk41 launch azimuth

`WIP11C_OBSERVED_SEA_IMPACT_TRACK_POLICY` closes the remaining case where no friendly terminal-effect report exists and an anonymous high-speed ASM disappears at the sea while its EKF file continues across the PPI as `MEM-?`:

- the decision path consumes only the track EKF, sensor-return state and own-ship geometry; it does not read `enemyMissiles`, `truthEnded`, `_deathReason` or a truth alive/dead flag;
- the file must be missile-like, descending at least `45 m/s`, within `0.35 s` of its estimated sea crossing, without a coherent plot for at least `0.25 s`, and remain eligible for `0.30 s`;
- confirmation additionally requires estimated altitude at or below `8 m` and the predicted sea-crossing point outside the physical ship envelope plus a `25 m` margin, preventing premature retirement of a track still diving into the ship;
- confirmation latches `OBSERVED_SEA_IMPACT / HARMLESS`, hides the ASM presentation, suppresses AUTO re-engagement and releases SPG-62/reservation/missile support;
- a later associated radar plot clears the inference and restores the ordinary observed-track path;
- direct-breakup or fuze BDA remains stronger evidence and retains `BDA/KILL` presentation priority if both records coexist.

The reported Kh-32/AUTO case was reproduced with seed `932008`, bearing `-45°`, range `90 km`, altitude `24,000 m` and speed `1,200 m/s`. AUTO launched an SM-2, but the interceptor missed by about `2.82 km` and retired `LOW_SPEED`; no friendly kill event was invented. The physical Kh-32 left the world at loop tick `4169`, and the no-return coast was hidden at tick `4185` (`16` ticks later) with estimated sea-impact evidence and a `442.29 m` predicted ship clearance. Final displayed ASM count was zero, assessment was `HARMLESS`, and no SPG reservation or illumination remained.

The separate SM-2 reversal came from treating the tiny horizontal projection of a nearly vertical, roll/pitch-tilted Mk41 deck normal as a valid azimuth. `launchAzimuthRad` now retains the target-bearing command while the in-cell position and velocity still follow the physical deck normal. Four deterministic bearings (`-135°`, `-45°`, `+45°`, `+135°`) held exactly zero in-cell command error; after two seconds the largest body-to-desired-bearing error was `0.0983°`.

## Existing ASM damage coupling

Wreck creation is deliberately deferred until the WIP112 component-damage observers have completed. The final source state drives:

| Existing ASM state | WIP11C result |
|---|---|
| fuel damage | burning wreck and smoke eligibility |
| guidance, fin and engine damage | reduced integrity and breakup severity |
| accumulated structural damage | structural-breakup mode |
| detonated warhead | explosive-breakup mode and reduced coherent mass |
| projected impact mass | source mass divided among physical pieces |

Every piece retains its source ASM identity, damage snapshot, warhead state, inherited velocity, coherent mass proxy, size, integrity and deterministic seed.

## Fixed-step wreck physics

Each physical piece advances in the existing `60 Hz` simulation tick with:

- inherited three-axis velocity;
- altitude-dependent air density, reference area and drag coefficient;
- gravity;
- yaw, pitch and roll tumble rates;
- swept ship collision, terrain elevation collision and interpolated sea-surface crossing;
- bounded maximum lifetime and battlespace-distance retirement.

Random breakup geometry uses an independent deterministic xorshift stream derived from simulation seed, source ASM, kill step and cause. It never consumes the combat RNG stream.

## Residual ship impact

A wreck piece that sweeps through the active ship is passed into the existing WIP11B DUD-compatible impact pipeline with its current mass, speed, dimensions and integrity. The path can therefore create:

- direct equipment and hitbox damage;
- material-aware residual penetration;
- entry/exit openings and flooding;
- VLS cell damage;
- rigid-body impulse;
- a `SHIP_WRECK_IMPACT` presentation event.

This path is explicitly kinetic-only. It sets explosive, TNT-equivalent and casing mass to zero. Generalized residual-warhead fuze behavior belongs to WIP12A.

## Water-surface events and presentation

`AEGIS_WATER_SURFACE_EVENT_V48_WIP11C` records two bounded event types:

- `WATER_ENTRY`: a wreck crosses the interpolated sea plane;
- `WATER_SURFACE_BLAST`: an interceptor or ASM airburst is low enough to couple to the surface under a yield-scaled height gate.

High airbursts do not create an immediate surface event. A coupled event carries source identity, velocity, entry angle, surface energy, explosive mass, coupling and deterministic seed.

The 3D presentation consumes these events to create a directionally biased water column/fan, expanding surface rings and a longer-lived foam patch. These are read-only render effects; WIP11C does not turn the event into underwater pressure damage.

## Physical 3D wreckage

- Main body and broken sections are persistent meshes while the authoritative pieces remain alive.
- Mesh orientation follows authoritative heading, pitch and roll.
- Integrity and breakup mode darken and deform the body; a torn face exposes the broken end.
- Fuel-damaged pieces carry a layered orange/yellow flame, denser dark smoke and short-lived incandescent flame puffs.
- The former one-shot fake breakup is suppressed whenever physical wreckage exists, avoiding duplicate debris.
- Meshes and their materials are disposed immediately when the authoritative piece retires.

## Interceptor smoke persistence and bounded density

`AEGIS_INTERCEPTOR_SMOKE_VISUAL_V48_WIP11C` applies to SM-2, ESSM and RAM presentation only:

- every in-flight and launch-smoke particle receives `8×` its former nominal lifetime;
- new trail samples use `3.5×` the former base spacing;
- after `36%` of nominal life, two of every three in-flight trail particles remain, giving an effective aged spacing of `5.25×` base;
- aged smoke gains up to `1.8×` additional expansion; at `75%` life it still retains more than `40%` opacity, holds `42%` through the `86%` point, then fades to zero;
- the interceptor and global smoke budgets are `9,000` and `12,000` particles, leaving 3,000 slots for wreck and damage smoke;
- budget pressure thins aged interceptor smoke evenly before removing newer smoke, so a long tail does not disappear as one contiguous block;
- expansion-per-second is reduced to `0.15×`; together with the longer lifetime this yields about `1.2×` the former total expansion opportunity rather than eightfold over-expansion;
- every density, lifetime and overload choice is presentation-only and cannot feed back into physics, sensors or engagement probability.

For a 6 km rendered pass, the fresh-stage projections are 1,372 SM-2, 2,017 ESSM and 2,286 RAM particles; aged projections are 915, 1,345 and 1,524. The analytical lifetime/spacing/thinning population factor is `1.7981×` the original trail, slightly below the preceding `5× / 2.25× / 3-of-4` treatment while extending nominal persistence by another 60%.

The current synchronous WebGL worst-case benchmark deliberately kept every synthetic sprite visible. In the final local run, 0 / 9,000 / 12,000 sprites measured about `6.28 / 63.02 / 81.44 ms` per render and `1,264 / 10,264 / 13,264` draw calls. The last 3,000 sprites added about `18.42 ms` in this headless software-render run. Absolute timings vary heavily between runs and are not representative of a hardware browser; the exact draw-call deltas and hard ceilings are the useful results. Real trails normally receive frustum culling and aged thinning, so `12,000` remains a ceiling rather than a target population.

## ASM smoke altitude gate and intercept parity

`AEGIS_ASM_SMOKE_ALTITUDE_VISUAL_V48_WIP11C` is a presentation-only gate:

- Kh-32 creates no new smoke particles at or below `5,000 m`;
- visibility transitions smoothly from 0 to 1 between `5,000–8,000 m`;
- Kh-32 smoke is fully visible at and above `8,000 m`;
- Kh-35U retains its existing turbojet/no-smoke-cloud policy;
- an existing high-altitude trail can remain where it was emitted while the descending live missile stops creating new low-altitude smoke.

No guidance-law or kill-probability tuning was made. The WIP11C static contract compares 11 authority functions directly against WIP11B, including intercept kinematics, fragmentation Pk, SM-2/ESSM flight guidance, RAM guidance, `updateMissile`, CIWS intercept solution and hard-kill estimates. All are byte-identical. `applyInterceptResult()` keeps the same two `simRandom()` decisions and thresholds. The one deliberate pre-guidance change is the Mk41 launch-heading correction described above.

A same-seed SM-2 diagnostic at 100 km preserved every discrete WIP11B/WIP11C outcome and RNG state across 12 cases: 12 proximity events, 11 kills, one damaged target, zero misses, median CPA `13.0373417268 m` and median Pk `0.9995`. Continuous audit values are numerically equivalent under the explicit bound `|Δ| <= 1e-8 × max(1, |a|, |b|)`; the raw audit JSON differs only at floating-point noise scale, so its WIP11B/WIP11C digests are respectively `fd6f2a266f46387ddf87fddc48524c4c75adbcccaa15249f994d379a43b6e68b` and `abbac21264448394945adba28f55380cfe2963bce8e17fa7c2bddccc0c11a35b`. The independent ESSM/RAM Pk-curve digest remains byte-identical at `569761620bf3881aa53e4cd7896c64ef9e1e78f78a8c0162be724cfd8e3f61a4`.

## Lifecycle, moving world and import safety

- Engagement reset and full-session reset clear wreckage, water events and their serials.
- Moving-world recentering shifts current and previous wreck coordinates together.
- Runtime ownership and entity-count diagnostics include the new world collections.
- WIP11B invalid-import mutation fingerprints include wreck IDs, water-event IDs and both serials.
- The operational-state codec is unchanged because both collections are intentionally transient.

## Diagnostics

Added diagnostic surfaces:

- `wip11cWreckageContract()`
- `wip11cWreckageSnapshot()`
- `wip11cCreateWreckageFixture()`
- `wip11cAdvanceWreckage()`
- `wip11cDiagnosticKillLiveAsm()`
- `wip11cWreckageDiagnostic()`
- `wip11cInterceptorSmokeAudit()`
- `wip11cAsmSmokeAltitudeAudit()`
- `sm2LaunchAudit()`
- `wip121RecordFriendlyInterceptEvent()`
- `wip121CloneCoastTrackForTest()`
- `wip121KillPlausibility()`
- `wip121TargetSupportSnapshot()` / `wip121PrimeDiagnosticTargetSupport()`
- `wip121BdaTrackPresentation()` and the existing WIP118/A3 control snapshots

The deterministic diagnostics verify damage coupling, inherited forward velocity, water entry, high-airburst rejection, low-airburst surface coupling, separation from hostile-threat collections, immediate BDA fire withholding, direct-breakup SPG/DL/SARH release, bounded kill-mark/ghost-MEM suppression, duplicate-file terminal-effect correlation, first-LOST-frame ownership transfer, no-return kill confirmation, coherent-return recovery, observed sea-impact retirement and physical Mk41 launch-azimuth preservation. The browser regressions also acquire unbound SPY files from normal anonymous plots, fly real ESSMs to terminal intercept, verify that the weapon-assigned track ID survives the target's physical retirement, and force the fuze-to-breakup promotion race that previously left a Kh-32 ghost track.

## Local verification

- Inline JavaScript parse: `PASS`
- Workflow YAML parse: `PASS`
- Workflow jobs declared: `20`
- Existing crew, interior, BridgeMaster E, ship-profile, material/protection and WIP11B import-safety static contracts: `6/6 PASS`
- WIP11C static contract: `32/32 checks PASS`
- WIP11C browser contract: `11/11 PASS`
- Full Playwright suite: `28/28 PASS` using the local Three.js dependency path
- WIP11C authoritative physics/water contract: `PASS`
- WIP11C actual WebGL wreck/water presentation contract: `PASS`
- BDA/AUTO contract: direct breakup released primed SPG/DL/SARH support, `KILL_ASSESSMENT / WITHHELD`, additional AUTO rounds `0`, no-return `DESTROYED`, `1.25 s` kill-mark then ghost-MEM hidden, coherent return `THREAT / AUTO_AUTHORIZED`
- Anonymous-track BDA contract: seed `991212`, unbound SPY track `300000001`, real ESSM `PROX_DETONATION_KILL`, immediate `DIRECT_BREAKUP`, SPG reservation/illumination and DL/SARH all cleared, one merged terminal event, final displayed ASM count `0`
- Kh-32 ESSM promotion-race contract: seed `112000`, unbound SPY track `300000001`, prior fuze echo step `840`, real ESSM `4` `PROX_DETONATION_KILL` and breakup step `845`, merged effect epoch rebased to `845`, same-tick last measurement not accepted as a post-kill return, additional AUTO rounds `0`, SPG/DL/SARH released, displayed ASM `0`, independent wreckage retained
- Duplicate-MEM BDA contract: a pre-effect sibling coast receives correlated `DIRECT_BREAKUP`, both presentations retire, and a later coherent measurement reopens the sibling as a live observed threat
- First-LOST alias contract: replacement ID receives live SAM/RAM/Phalanx/CIWS/SPG/selected-lock ownership in the same assessment frame and the prior ID retains none
- Kh-32 observed sea-impact contract: seed `932008`, anonymous SPY track, real AUTO SM-2 miss/`LOW_SPEED`, no invented friendly kill, physical removal-to-hidden coast `16` ticks, displayed ASM `0`, final `HARMLESS`, SPG/AUTO support released
- Mk41 launch-azimuth contract: four target bearings retained exact in-cell body/command alignment and no 180-degree deck-normal reversal; maximum two-second body/desired error `0.0983°`
- Interceptor smoke lifetime/density/age/budget audit: `PASS`
- Dynamic aged-smoke probe: `12` created, `8` retained, all aged, minimum opacity factor `0.7703`, minimum scale ratio `8.2380`
- ASM altitude-gate emission probe: `4 km = 0`, `9 km > 0`, audit transition `5 / 6.5 / 8 km = 0 / 0.5 / 1`
- WIP11B guidance/Pk compatibility: authority functions and Pk curves exact; same-seed 12-case discrete outcomes/RNG exact; continuous audit numerically equivalent under the declared `1e-8` relative bound
- WebGL visible-smoke stress benchmark: `0 / 9,000 / 12,000` sprites measured at `6.28 / 63.02 / 81.44 ms` synchronous render mean in the final headless run; exact `+9,000 / +3,000` draw-call deltas and hard caps preserved
- Existing CIWS, impact, mass, structure, stability, wave/flooding, interior, crew, profile, material and import-safety browser regressions: `PASS`
- Multi-view WebGL visual probe: `PASS`
- WebGL console/page errors: `0 / 0`
- Aft geometry, six liferaft contacts, Mk 45, material/protection and 2D drawing audits: `PASS`

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP11C.html`
- WIP10 transition baseline: `archive/v48/WIP10/Aegis_SIM_v48_WIP10.html`
- WIP11A safety/behavior baseline: `archive/v48/WIP11A/Aegis_SIM_v48_WIP11A.html`
- WIP11C wreckage baseline: `archive/v48/WIP11B/Aegis_SIM_v48_WIP11B.html`
- Expected jobs: `20`
- Added jobs: `asm-wreckage-wip11c-contract`, `asm-wreckage-wip11c`
- Required final result before merge: `20/20 jobs passed`
- Branch: `feat/v48-wip11c-asm-wreckage-water-effects`
- GitHub access check: authenticated as `0-FLANDRE-0` with `admin/maintain/push/pull/triage`; repository default branch is `main`
- Pre-merge `main` head: `4bbf024530a507d60abb84e1def3d5d9d0d37e5b`
- User-uploaded final HTML commit: `2a615e08d4a570dfb5cbdc0f3ff046bedafc5326`; remote Git blob `de3e0ea7a2216bd24f10e1a42962db23c9a90031` matched the local file byte-for-byte
- Accepted functional branch head: `7a9ac8a66eeddc6aea5989e78d318eab6b1dd231`
- Pull request: `#25` — `Complete v48 WIP11C ASM wreckage and ghost-track retirement`
- GitHub Actions run `#92` (`35370375704`): `20/20 jobs passed`
- Merge commit on `main`: `7db6a93431e26ebcfd53a0dec9e57dd7e212d6b5`

## Artifact

- File: `Aegis_SIM_v48_WIP11C.html`
- Size: `2,819,872 bytes`
- SHA-256: `464e1fc4a7e3ef9565bc32ce42e7e5a112041a977ee96fb7bdb5920f7410c01f`
- Exact WIP11B baseline SHA-256: `93084bb9b0d9a72f0544b244a5ced6f314fb37a224f18f5739163fd10ed3db62`

## Deferred work and next handoff

The next code WIP is WIP12A, the terminal-ballistics foundation. Its absolute design rules are:

1. share projectile state, traversal, trace and damage-result contracts rather than one universal penetration equation;
2. distinguish boundary surfaces, empty space and real material/damage volumes;
3. spend no penetration energy in empty space, while advancing flight and fuze time there;
4. select thin-plate, homogeneous-armor and later armor solvers by collision regime;
5. keep solver calculation separate from damage consumers;
6. preserve ASM behavior behind a compatibility adapter until deliberate migration;
7. define the damage-patch interface in WIP12A but defer persistent authoritative accumulation.

The authoritative WIP12A scope, contracts, fixtures and completion criteria are recorded in `docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`.

Actual gun launch, exterior ballistics, FCS, a production face-hardened-armor solver and live persistent patch state remain outside WIP12A.

## Repository result

- Root contains only the newest WIP11C simulator, status and checksum set.
- Exact WIP10, WIP11, WIP11A and WIP11B artifacts are preserved under `archive/v48/`.
- Tests target WIP11C; transition and behavior-parity tests read their archived baselines.
