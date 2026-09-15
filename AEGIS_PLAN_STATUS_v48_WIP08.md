# AEGIS v48 WIP08 — BridgeMaster E navigation radar correction

## R2 corrective pass

- Replaced the unsupported lower-port-yardarm placement from the first WIP08 draft.
- Kept exactly one functional BridgeMaster E channel; no cosmetic duplicate radar was added for symmetry.
- Moved the shared physical/sensor/damage/beam hardpoint to the released-photo-derived upper-starboard main-mast yardarm position.
- Filled the otherwise sparse yardarms with presentation-only RF housings, a small port mushroom fitting, red/green navigation lights, whip aerials, stays and hanging cable runs.
- Batched all 20 thin whip/cable segments into one `LineSegments` drawable. The complete new decorative outfit is bounded to 14 drawables and has no simulation feedback.

## Scope

- Baseline: `Aegis_SIM_v48_WIP07.html`
- Replace the incorrect legacy surface/navigation-radar entry with BridgeMaster E for the DDG-119 late Flight IIA basis.
- Keep this WIP limited to radar identity, authoritative sensor state, physical mounting, damage coupling, diagnostics, UI and 3D presentation.
- Armor/material profiles, naval gunfire, surface-fire FCS and target ships remain subsequent work.

## Implemented

- Removed every SPS-73 name, source identifier, UI control and renderer field from the simulator.
- Added `BRIDGEMASTER_E_INSTALLATION` with schema `AEGIS_BRIDGEMASTER_E_INSTALLATION_V48_WIP08`.
- Rebased the working model on the public BridgeMaster E S-band equipment values:
  - `3050 MHz ±10 MHz`, `30 kW` peak power
  - `12 ft / 3.7 m` aperture, `2.0° × 30°` beam, `26 dB` gain, horizontal polarization
  - `30 RPM` nominal and `50 RPM` high-speed operation for the 60 Hz baseline
  - receiver noise figure `~5 dB`, dynamic range `~80 dB`, IF `60 MHz`
- Added the public pulse-mode table:
  - short: `0.05 μs / 1800 Hz`, IF bandwidth `~20 MHz`
  - medium: `0.25 μs / 1800 Hz`, IF bandwidth `~20 MHz`
  - long: `0.75 μs / 785 Hz`, IF bandwidth `~3 MHz`
- Preserved the published near-range claims as inequalities (`minimum range <35 m`, `range resolution <35 m`) and separated them from the simulation working values (`30 m`, `34 m`).
- Separated maintained-track limits from display scale: `0.25–40 nmi`, `150 kt` maximum relative speed and `60` radar tracks versus a selectable display scale of `96 nmi`.
- Added the combined capacity contract of `40 radar tracks + 40 AIS`.
- Marked the exact DDG-119 special naval variant antenna/RF configuration as `PUBLIC_UNKNOWN`; only the detection-probability tuning remains simulation-derived.
- Moved the authoritative sensor origin to the starboard end of the upper main-mast yardarm:
  - ship-local X: `15.75 m`
  - ship-local Y: `+5.15 m` (starboard)
  - ship-local Z: `31.78 m`
  - mount basis: `DDG119_PHOTO_DERIVED_UPPER_STARBOARD_YARDARM`
- Detection range/bearing, radar horizon, measurement synthesis, ARPA-relative plots, shoreline echoes, 3D beam and mesh now consume the same hardpoint.
- Added physical damage target `bridgemaster_e.01` / system `BRIDGEMASTER_E`; direct damage now reduces radar health independently of general mast damage.
- Added actual 3D pedestal, gearbox and `BRIDGEMASTER_E_12FT_OPEN_ARRAY` rotating mesh.
- Added `DDG119_PHOTO_DERIVED_MAST_OUTFIT`; its static auxiliary fittings are explicitly presentation-only and are not additional radar channels.
- The 3D radar volume renders the `40 nmi` maintained-track envelope. The `96 nmi` value remains display-scale metadata and is not presented as detection range.
- The 3D antenna mirrors the authoritative simulation rotor angle and never advances radar physics in the renderer.
- Added UI button `external3DBridgeMasterEBtn` and removed the old control.
- Added diagnostics:
  - `bridgeMasterEAudit()`
  - `bridgeMasterEInstallation()`
  - `stepSurfaceBridgeMasterOnly()`
  - `bridgeMasterEAuditV48Wip08()` on the 3D view

## Evidence basis and limits

- Northrop Grumman's contract announcement identifies BridgeMaster E naval radars for DDG-51-class new construction beginning with USS Mason (DDG-87):
  <https://investor.northropgrumman.com/news-releases/news-release-details/northrop-grumman-supply-radars-new-us-navy-destroyers>
- The DDG-119 main-mast yardarm placement and auxiliary fittings are derived from multiple released photographs, not from a released installation drawing:
  <https://upload.wikimedia.org/wikipedia/commons/4/43/USS_Delbert_D._Black_%28DDG-119%29_is_undergoing_builder%27s_trials_in_the_Gulf_of_Mexico.jpg>
  <https://www.dvidshub.net/image/8209901/uss-delbert-d-black-operates-mediterranean-sea>
- The S-band values and waveform table are public BridgeMaster E product-family specifications. A direct public source establishing the exact 12 ft S-band special naval variant on DDG-119 has not been identified, so that installation choice remains an explicit working baseline rather than a claimed ship-specific fact.

## Local verification

- Inline JavaScript parse: `PASS` (`INLINE_JS_OK`)
- `tests/bridgemaster-e-contract.cjs`: `PASS`
  - identity
  - absence of legacy radar strings
  - shared physical hardpoint
  - damage target
  - 3D mesh declaration
  - authoritative rotor mirroring
  - upper-starboard mount coordinates and actual-mesh hardpoint coupling
  - single functional radar and bounded presentation-only mast outfit
  - UI and read-only renderer contract
- `tests/crew-wip07-contract.cjs`: `PASS`
- `tests/interior-wip06-contract.cjs`: `PASS`
  - 138 spaces
  - 160 portals
  - 70 equipment nodes
  - 0 superstructure-outside vertices
- Playwright browser execution: `ENVIRONMENT BLOCKED`
  - reason: local Playwright Chromium executable is absent
  - failure occurred before page launch; this is not a simulator assertion failure
- Actual WebGL mesh audit remains required in GitHub Actions Chromium.

## Artifact

- File: `Aegis_SIM_v48_WIP08.html`
- Size: `2,607,181 bytes`
- SHA-256: `a9bf0cbc40c003f51ce271bdd795ee4278cc1b00cbb27d2cc4bd8b063d2d8b2d`

## GitHub Actions acceptance

- Workflow `SIM_FILE` must be `Aegis_SIM_v48_WIP08.html`.
- Existing WIP01–WIP07 regressions must remain green.
- New `bridgemaster-e` job must pass both static and browser contracts.
- `aegis-3d-render` must record and pass:
  - `meshPresent=true`
  - `mountPresent=true`
  - `meshAtAuthoritativeHardpoint=true`
  - `upperStarboardYardarm=true`
  - `rotorMirrorsAuthoritative=true`
  - `physicalHitbox=true`
  - `sharedHardpoint=true`
  - `mastOutfitPresent=true`
  - `mastOutfitDrawables=14`
  - `mastOutfitBounded=true`
  - `duplicateFunctionalRadar=false`
  - `publicSbandBaseline=true`
  - `trackDisplayRangeSeparated=true`
  - `beamTrackRangeM=74,080` and `beamDisplayScaleMaxM=177,792`
  - `presentationOnly=true`
  - `physicsFeedback=false`
- After Actions, append run ID, passed job list, artifact IDs/digests and the captured BridgeMaster E 3D audit before merge.

## Planned repository tree operation

- Add root `Aegis_SIM_v48_WIP08.html` and `AEGIS_PLAN_STATUS_v48_WIP08.md`.
- Preserve the exact WIP07 HTML/status under `archive/v48/WIP07/` using their existing Git blobs.
- Remove root WIP07 HTML/status after archiving.
- Update workflow, package manifest and tests to target WIP08.
- No release or tag at WIP stage.
