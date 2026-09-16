# AEGIS v48 WIP09 — DDG-119 ship profile foundation

## Scope

- Baseline: `Aegis_SIM_v48_WIP08.html`
- Establish one immutable, data-driven ship profile for the current DDG-119 late Flight IIA simulation.
- Preserve WIP08 deterministic behavior while routing geometry, navigation, mass, hydrostatics, internal topology, crew, sensors, weapons, damage control and 3D bindings through the profile.
- Keep all mutable navigation, damage, flooding, ammunition and crew state outside the immutable profile.
- Define protection/material extension slots only. Armor thickness, material performance and penetration changes remain deferred to WIP10.

## Active profile

- Profile ID: `DDG_119_LATE_FLIGHT_IIA`
- Schema: `AEGIS_SHIP_PROFILE_V48_WIP09`
- Basis: USS Delbert D. Black (DDG-119), late Flight IIA working configuration
- Runtime owner: `ACTIVE_SHIP_RUNTIME_V48_WIP09`
- Registry: `SHIP_PROFILE_REGISTRY_V48_WIP09`
- Expected migration behavior: `NO_GAMEPLAY_CHANGE`
- WIP08 parity baseline SHA-256: `fe537db57d08f7c87120ed80a6118acd7c83389e75169e3fde9d404834f67eb8`

## Implemented

- Added recursively frozen profile data for:
  - identity, coordinate convention and principal dimensions
  - hull stations, superstructure bounds and authoritative equipment hardpoints
  - navigation defaults, hydrostatics and aggregate/fixed/tank mass inputs
  - SPY-1D(V), SPQ-9B, SPG-62 and BridgeMaster E sensor definitions
  - forward/aft VLS and CIWS definitions
  - interior topology, crew establishment and damage-control configuration
  - flood, wave and survivability configuration
  - renderer bindings and presentation-only authority limits
  - future protection/material schema slots with `physicsCoupled=false`
- Added a separately allocated mutable runtime for navigation and subsystem instances.
- Added builder registries for sensor, VLS, close-in weapon, hitbox, interior, crew, mass, dynamics, wave, flood, damage-control and renderer consumers.
- Rewired current DDG-119 consumers to resolve their configuration from the active profile while retaining the established WIP08 numerical baselines.
- Added the read-only profile summary to `get3DRenderState()` and bound the rendered ship root to the same profile ID.
- Kept 3D strictly presentation-only; the renderer cannot write back to navigation, sensor, damage or weapon physics.
- Added diagnostics:
  - `shipProfileV48Wip09()`
  - `shipProfileAuditV48Wip09()`
  - `shipRuntimeBindingsV48Wip09()`
  - `window.__AEGIS_ACTIVE_SHIP_PROFILE__` as a frozen read-only reference
- Added the core self-test marker `SHIP-PROFILE-V48-WIP09`.

## Explicitly unchanged

- No armor or material thickness was assigned.
- No penetration, blast, fragmentation, flooding, stability, maneuvering, sensor, weapon or crew gameplay values were intentionally changed.
- No new target ship or second selectable profile was added.
- BridgeMaster E remains one functional radar at the WIP08 shared upper-starboard hardpoint.
- No release or tag is created for this WIP.

## Acceptance corrections

- The first browser run exposed that the profile audit was eagerly constructing lazy mass, dynamics, wave, interior and crew runtime objects during startup.
  - Reworked the audit to inspect authored constants, registries and already-existing bindings only.
  - Added an exact before/after runtime-binding assertion proving that repeated audit calls create no subsystem and mutate no runtime state.
  - Restored the original mass-ledger initial-equilibrium behavior and eliminated the resulting shared self-test RNG shift.
- A later stability regression exposed that the dynamics builder ID had been reused as the WIP04 diagnostic schema.
  - Added separate `hydrostatics.schema` and `hydrostatics.modelId` profile fields.
  - Restored `AEGIS_INTACT_STABILITY_V48_WIP04` without changing any stability or maneuvering value.
  - Added a static contract that locks both identities independently.

## Verification contract

- Inline JavaScript must parse without syntax errors.
- `shipProfileAuditV48Wip09()` must report:
  - deep recursive immutability
  - registry and active-profile resolution
  - separate mutable runtime ownership
  - profile-driven consumer bindings
  - deferred/non-coupled protection data
  - presentation-only/non-feedback renderer authority
  - expected geometry, VLS, mass, crew and topology counts
- The browser must prove that attempted profile mutation does not alter the profile and that mutable runtime navigation does not alter profile defaults.
- A fixed-seed WIP08/WIP09 parity fixture must compare impact, wave, interior, crew, mass, hardpoint, VLS, topology and BridgeMaster E outputs.
- All WIP01–WIP08 regression jobs must remain green.
- GitHub Actions must create exactly 15 jobs, including the new `ship-profile` static/browser job.

## Local verification

- Inline JavaScript parse: `PASS`
- `git diff --check`: `PASS`
- Workflow YAML parse: `PASS` (`15` jobs)
- `tests/ship-profile-contract.cjs`: `PASS`
- `tests/bridgemaster-e-contract.cjs`: `PASS`
- `tests/interior-wip06-contract.cjs`: `PASS`
  - 138 spaces, 160 portals, 70 equipment nodes
  - 0 superstructure-outside vertices
- `tests/crew-wip07-contract.cjs`: `PASS`
  - 310 spatial crew
- Local Playwright/WebGL execution: `ENVIRONMENT BLOCKED`
  - The local Playwright Chromium executable is absent.
  - Browser, fixed-seed parity and actual WebGL acceptance remain assigned to GitHub Actions.

## Artifact

- File: `Aegis_SIM_v48_WIP09.html`
- Size: `2,626,884 bytes`
- SHA-256: `9fd254af900baa76bfdbfff3c39d05b575d1d2f600d7a67d4787ae15c54025df`
- Git blob: `c660a99d42e57771f7e88909bc78c5b594e10737`
- The status-document SHA-256 is recorded with the HTML hash in `WIP09_SHA256SUMS.txt`.

## GitHub Actions acceptance

- Workflow `SIM_FILE`: `Aegis_SIM_v48_WIP09.html`
- Parity baseline: `archive/v48/WIP08/Aegis_SIM_v48_WIP08.html`
- Required result: `15/15 jobs passed`
- Required profile artifacts:
  - immutable/runtime-separation browser audit
  - fixed-seed WIP08/WIP09 parity result
- Required 3D result:
  - profile-bound rendered ship root
  - unchanged authoritative hardpoints and equipment meshes
  - `presentationOnly=true`
  - `physicsFeedback=false`

## Final GitHub Actions evidence

- Workflow run: [#82 / 34969755361](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/34969755361)
- Tested branch head: `aa840664a62990035ad86a7ecd6702fc0a51b71d`
- Pull-request merge-test revision: `d1606415c0e9d71d9e86e5e70b521cbada52c9cd`
- Result: `15/15 jobs passed`
- Passed jobs: `static-smoke`, `webgl-render-probe`, `aegis-3d-render`, `ciws-b1-closure`, `ciws-b2-maneuver`, `ciws-b3-damage`, `ship-mass-ledger`, `ship-impact-penetration`, `ship-structural-fatigue`, `ship-stability-maneuver`, `ship-wave-flooding`, `ship-interior-topology`, `ship-crew-damage`, `bridgemaster-e`, `ship-profile`.

### Captured ship-profile audit

- Profile: `DDG_119_LATE_FLIGHT_IIA` / revision `V48_WIP09`
- Recursive immutability, registry identity, consumer parity, protection deferral, renderer authority and WIP08 baseline declaration: all `true`
- Registries resolved: sensor, VLS, close-in weapon, hitbox, interior, crew, mass, dynamics, wave, flood, damage control and renderer
- Runtime separation: `navigationIsMutable=true`, with authored profile still deeply frozen
- Audit side effects: runtime bindings before and after two audit calls were byte-for-byte equal
- Counts: 1 profile, 138 spaces, 160 portals, 70 equipment nodes, 310 crew, 32 forward VLS cells, 64 aft VLS cells
- Core self-test failures: `[]`

### Fixed-seed WIP08 parity

- Schema: `AEGIS_SHIP_PROFILE_PARITY_V48_WIP09`
- Baseline self-tests: `true`
- WIP09 self-tests: `true`
- Exact selected-state equality: `true`
- Compared surfaces: Kh-32/Kh-35U impact, wave flooding, interior topology, crew routes/casualties, mass ledger, 3D hardpoints/VLS/topology/crew and BridgeMaster E

### Captured 3D and stability evidence

- Chromium WebGL 2 / SwiftShader renderer ready: `true`
- Overall 3D audit: `pass=true`
- BridgeMaster E mesh, mount, upper-starboard hardpoint, rotor mirroring, physical hitbox and single functional radar: all `true`
- Interior: all 138 spaces, 160 portals and 70 equipment nodes represented; 9 batched drawables; 0 outside vertices
- Crew: all 310 personnel represented in one instance batch
- Hull entry/exit holes: opposite-side, mesh-matched, attached and read-only
- Renderer authority: `presentationOnly=true`, no physics feedback
- Stability diagnostic and state schema: `AEGIS_INTACT_STABILITY_V48_WIP04`
- Upright GM0: `1.5000000174 m`; all loading, finite-angle GZ, turn-envelope and constant-displacement checks passed

### Workflow artifacts

| Artifact | ID | Digest |
|---|---:|---|
| ciws-b3-damage | 10397340231 | `sha256:6a8099f7848aed795101f1eb606df2db58a7e0333114059a8eb66bf2915ea5ae` |
| ship-mass-ledger | 10397320281 | `sha256:9d74275ffc4190096ec0b109760b2506378a29a2b7a4d210dd1c4f824bce19a7` |
| ciws-b1-closure | 10397116101 | `sha256:479f278d3b548000652a5bd2abcdb5c29da9caf96d2fb57cd414e466cec026d3` |
| ship-profile | 10397061193 | `sha256:a88dc001ef448788cff1aeb7f9a41410a1476596849ac5b275b5ab763ad49279` |
| ship-structural-fatigue | 10397051299 | `sha256:7df97a48ec156353e4aaf45552e529065a51549b22c505e931239cde39d5a72b` |
| webgl-probe | 10396996338 | `sha256:a65de8daeec7ad63e849b3c1275d3a07aca142391b4e74838ef69236f741e41b` |
| aegis-3d-render | 10396847231 | `sha256:42e1583e8ac7a0aa92dacd8e904dcc05082c3a9757525a28bdaafaecf18571cf` |
| ship-interior-topology | 10396777769 | `sha256:27b4827decdb3358027a2ce034384b10f7189ec89b9e849a5847d9a68b694084` |
| ship-wave-flooding | 10396693126 | `sha256:003b02f90bdea492d4e0d7eaa8aae6c52ac9bf733471d59b679f8e55f28b00a3` |
| bridgemaster-e | 10396582525 | `sha256:1de3bf70358135388c4573144bf3d73bca0808c704ae34716ea69f27cc5f379a` |
| ship-impact-penetration | 10396427894 | `sha256:3d1567f552057abe8f491df765a6e8e4e1a4d3daa7f70f95f5aab844193ae6a7` |
| ciws-b2-maneuver | 10396264883 | `sha256:8e57f8e3013378f50357c3e6c771e7d42e6596c81daa8f641520e06a35ae7dc9` |
| ship-stability-maneuver | 10396103832 | `sha256:c120f57c26564b8cfb9f8a25ca14cb42d8a8a5f8b6bcc76bf73b78a13d35f256` |
| ship-crew-damage | 10396093663 | `sha256:208141338b809fe7f8e8240d912d33df619e3ff2da0e97f9c27ce45a512e2888` |

`static-smoke` produces no artifact by design.

## Repository tree result

- Root now contains `Aegis_SIM_v48_WIP09.html` and `AEGIS_PLAN_STATUS_v48_WIP09.md`.
- Exact WIP08 HTML/status blobs are preserved under `archive/v48/WIP08/`.
- Root WIP08 HTML/status were removed after archival.
- Workflow, package manifest and tests target WIP09; the parity job reads the archived WIP08 baseline.
- All temporary source-export/patch workflows and patch payloads were removed before acceptance.
- No release or tag at WIP stage.
