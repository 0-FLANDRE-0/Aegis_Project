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

## Artifact draft

- File: `Aegis_SIM_v48_WIP09.html`
- Size: `2,626,858 bytes`
- SHA-256: `0fe806267435d2562408e638246a353b93ddf9c7e6295914f12cf83ec684b54f`
- Git blob: pending remote upload

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

Pending the WIP09 branch run. This section will be replaced with the tested commit, run, job result, browser audit, parity evidence and artifact digests before merge.

## Planned repository tree operation

- Add root `Aegis_SIM_v48_WIP09.html` and `AEGIS_PLAN_STATUS_v48_WIP09.md`.
- Preserve the exact WIP08 HTML/status under `archive/v48/WIP08/` using their existing Git blobs.
- Remove root WIP08 HTML/status after archiving.
- Update workflow, package manifest and tests to target WIP09.
- Remove all temporary source-export/patch workflows before acceptance.
- No release or tag at WIP stage.
