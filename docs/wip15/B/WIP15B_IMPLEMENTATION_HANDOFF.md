# WIP15B — Nulka / Reserve Ammunition / Empty-Bank Reload

Updated: 2026-10-02

**FEATURE IMPLEMENTED / SCOPED VALIDATION PASSED / LOCAL CANDIDATE.** This is not an all-scenarios effectiveness claim or an all-core-tests-green declaration.

## Artifact and baseline

- Output: `Aegis_SIM_v48_WIP15B.html`
- Size: 7,351,441 bytes
- SHA-256: `0264bb06397b60559daf74f964ab51be4cee95f45fe92dcfb1eb25b773461236`
- Baseline: user-visible local `Aegis_SIM_v48_WIP15A.html`
- Baseline SHA-256: `462318f7dc4860b526d96a09c9ed069731e242375b9aecedc455a938d7a208f7`
- The original 15A HTML was not changed.
- Large HTML and the support ZIP are conversation deliverables, not uploaded by this commit. As checked during this work, the root WIP15A HTML is not present on branch WIP15. Do not describe a local candidate as a verified remote runtime.

## User-approved inventory/reload contract

| System | Banks | Loaded | Reserve | Total | Empty-bank service |
| --- | --- | ---: | ---: | ---: | --- |
| SRBOC | 6 × 6 tubes | 36 | 72 | 108 | 6 rounds, 60 simulation seconds |
| Nulka | 4 × 2 canisters | 8 | 16 | 24 | 2 rounds, 90 simulation seconds |

Reserve quantities and the completely-empty-bank trigger are the user's request. Reload durations are adjustable `SIM_TUNED` game settings, not real handling or hardware specifications.

A partially used bank is not topped up. When a serviceable bank becomes completely empty, a whole set moves from reserve to in-service inventory. Only the completion tick loads the tubes. Each bank progresses independently; disabled/damaged/offline service pauses and resumes its remaining ticks. Insufficient reserve cannot create a partial or free refill. Conservation is `loaded + reserve + inService + spent = initial total`.

## Geometry and implementation

The existing C5 model was audited: four twin-canister stations, two per side. Each has 512 existing source triangles; 2,048 triangles total are registered under canonical hardpoints. Eight bore mouths and axes were derived from the existing upper/lower 12-vertex rings. These are game-model coordinates, not DDG-119 blueprint measurements.

The fixed ship model retains 224,404 triangles and identical triangle positions at source 0.1mm precision. Vertex storage changes from 536,404 to 532,816 through unused-vertex compaction, not surface removal. Existing SRBOC 852 source faces and 36 mouths remain registered. No duplicate launcher overlay is added.

- Ship-owned Nulka banks and supply: `ACTIVE_SHIP_RUNTIME.weapons.nulka`.
- Deployed entities: `ENGAGEMENT_RUNTIME.world.entities.activeDecoys`.
- Launch from the selected canonical mouth with ship translation and local-point rotational velocity.
- DLP consumes the observed soft-kill cue and ship/launcher state. Track-backed requests recheck current observed identity, age and existence at release. It does not inspect hostile truth or actual enemy seeker attachment.
- Autonomous bounded game flight: LAUNCH_CLEAR → TRANSLATE → HOVER_SEDUCE → WALK_OFF → FALL → EXPIRED. The controller receives imperfect own-state observations. There is no teleport-to-hover or live-ship following after release.
- Unitless active RF received level enters the existing physical visibility, measurement, association and HOJ adapters. A Nulka identity does not force a target switch. All-passive paths retain their original function bodies.
- Manual Nulka button requires a valid observed cue. SK AUTO uses the common threat manager, with separate supply and response history. Duplicate-response coverage uses our own launch plan rather than enemy seeker truth.
- 2D own-deployment markers, bank stock/reload readouts, and 3D airborne body plus restrained continuous plume.

## Mass, lifecycle and snapshot

Additional variable ordnance mass versus 15A is `72*23 + (8+16)*67.5 = 3,276 kg`. Existing Mk214 mass is preserved; Nulka 67.5kg is explicitly a game mass assumption. No lightship offset or duplicate launcher hardware mass is added. Reserve, service and tube contents are counted once; reload transfers preserve total mass and launch removes one round.

Profile revision: `V48_WIP15B_ACTIVE_DECOY_RESERVES`. Supply schema: `SOFTKILL_RESERVES_15B_V1`. Stock, progress, serial, cooldown, tube and bank state are validated before restoration. Old 15A saves are deliberately rejected, not silently padded with ammunition. Deployed decoys and engagement responses are combat transients and are cleared by operational import/reset.

## Executed validation

- 15B runtime: 33/33.
- Geometry and bore registration: 8/8.
- Package/source preservation/syntax/reproducible build: 70/70.
- Desktop/mobile-size actual DOM controls: 2/2.
- Existing B3 runtime: 25/25.
- Existing B2 navigation: 38/38; VLS interval: 12/12; release policy: 22/22.
- Preserved transport module unit tests: 49/49; loft stage unit tests: 33/33.
- Unmodified production HTML: actual departure/SK AUTO/Kh35 debug-spawn buttons, 240 seconds through the production fixed-step clock, no injected source. Six Nulka launches; final Nulka loaded4/reserve12/inService2/spent6, total24. SRBOC loaded32/reserve72/spent4, total108. No page errors.
- Xvfb + headed Chromium + ANGLE/SwiftShader WebGL2: actual rendering of a 15-second hover fixture, one airborne Nulka. Screenshot is in the conversation/support evidence. This visual fixture used test-only closure access; the separate production smoke used unchanged HTML.

Counts overlap and must not be summed as unique tests. Full raw evidence, tests, geometry registration, builder and checksums are included in the conversation support ZIP.

## Combat observations and limitations

Fourteen recorded ASM conditions cover manual/AUTO, multiple ASMs, chaff/EA combinations, bearings and Kh32. They are finite diagnostic observations, not statistical Pk or actual-system performance validation.

- In the 20km Kh35 comparison, no decoy led to a hit; manual Nulka produced no ship hit within 100 seconds and about 125.8m sampled minimum ship-center separation. The missile was still flying afterward: this is observed passage/miss, not a kill.
- Near 8km side-entry and 20km AUTO cases still reacquired/hit the ship. The chaff/EA combinations did not guarantee survival in the tested seed.
- Kh32 RF/HOJ and AUTO integration was exercised, but its baseline without Nulka also missed. No-hit alone is not evidence of a causal Nulka save.
- Association counters count live fixed-step states, not independent detections. Sampled ship-center minima are not continuous hull CPA.

The inherited `V48 WIP13A surface target submergedBreachFloods` core failure remains. Actual mobile GPU/FPS and native file-URL navigation are unverified. There is no real waveform/ERP/propulsion/tactical optimizer, individual-decoy hard-kill damage solver or physical reload-crew route simulation. Flight, RF level, service duration, Nulka mass, magazine position and AUTO thresholds are `SIM_TUNED` game abstractions.

## Sources and next handoff

Primary public material supplies only the broad offboard active/hovering/ship-like-signal concept: U.S. Navy MK53 fact file, BAE Systems Nulka overview and L3Harris Nulka overview. The 4×2 layout is an audit of this project's model; reserves are user requirements; other coefficients are game assumptions.

Deliverables: `AEGIS_WIP15B_REPORT.md`, `AEGIS_PLAN_STATUS_v48_WIP15B.md`, `AEGIS_WIP15B_VALIDATION_SUMMARY.json`, `SHA256SUMS_v48_WIP15B.txt`, `AEGIS_v48_WIP15B_SUPPORT.zip`, and the standalone HTML in the conversation. After user upload of the HTML to WIP15, verify its hash before updating the remote runtime baseline or creating a PR. No main changes, PR, merge, release or tag were performed for this implementation.
