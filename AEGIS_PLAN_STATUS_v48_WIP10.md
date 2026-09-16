# AEGIS v48 WIP10 — aft geometry and Mk 45 correction

## Scope

- Baseline: `archive/v48/WIP09/Aegis_SIM_v48_WIP09.html`
- Keep the helicopter flight deck as one flat landing plane.
- Lower the hangar doors, hangar shell, aft VLS roof and related aft structures to meet that plane.
- Replace the simplified forward gun with a Mk 45 Mod 4-inspired public-visual approximation.
- Synchronize the authored profile, physical hitboxes, mass locations, internal spaces, 3D mesh, damage openings and 2D hit indicator.
- Preserve combat, sensor, weapon inventory, crew and non-aft contracts except where the corrected physical geometry necessarily changes CG and stability.
- Keep protection/material physics deferred to WIP11.

## Geometry authority

- Profile: `DDG_119_LATE_FLIGHT_IIA`, revision `V48_WIP10`
- Schema: `AEGIS_SHIP_PROFILE_V48_WIP10`, schema version `2`
- Coordinate frame: ship-local metres; `+X` bow, `+Y` starboard, `+Z` up
- Basis: public imagery of DDG-119 and late Flight IIA ships, with unreleased dimensions explicitly marked `PUBLIC_PHOTO_DERIVED_SIM_TUNED`
- Public references:
  - US Navy DDG-51 fact file: <https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2169871/destroyers-ddg-51/>
  - DDG-119 DVIDS unit imagery: <https://www.dvidshub.net/unit/DDG-119>
  - DDG-119 flight-quarters imagery: <https://www.dvidshub.net/image/9485174/uss-delbert-d-black-ddg-119-conducts-flight-quarters>

## Authoritative WIP10 dimensions

| Surface or mount | WIP10 value | Contract |
|---|---:|---|
| Flight-deck plane | `z = 4.88 m` | All 8 authored stations and every rendered deck vertex share one height |
| Hangar-door sill | `z = 4.90 m` | Within `0.02 m` of the landing plane |
| Hangar-door top | `z = 10.18 m` | Lowered with the hangar shell |
| Hangar roof / aft VLS deck | `z = 10.55 m` | One coupled physical and rendered plane |
| Hangar interior | `4.96–10.16 m` | `5.20 m` clear height in both bays |
| Lower aft support roof | `z = 13.76 m` | Replaces the oversized box-like mass |
| Mk 45 base deck | `z = 8.05 m` | Profile-driven mount |
| Mk 45 exposed barrel | `7.05 m` | Public-visual Mod 4 approximation |

The flight deck is not a ramp. Height transition occurs at the forward step and in the lowered hangar/aft structures, never across the landing surface.

## Implemented

- Added the immutable `geometry.aft` contract and exposed `aftGeometryAuditV48Wip10()`.
- Rebuilt the flight-deck mesh as `WIP10_FLAT_FLIGHT_DECK` with `flat=true` metadata.
- Lowered and realigned:
  - both hangar doors and thresholds
  - both hangar bays and roof
  - aft Mk 41 deck and hitbox
  - SeaRAM support and aft SPG support stages
  - stairs, rails and adjacent aft details
- Replaced the aft support block with a lower tapered house plus separate high/low SPG pedestals.
- Rebuilt the forward gun as `MK45_MOD4_5IN_62`, including a fixed base, rotation ring, faceted housing, sleeve, barrel, muzzle collar and bore.
- Updated physical hull/deck/equipment hitboxes and mass-node positions from the same profile values.
- Updated WIP06 interior bounds while retaining 138 spaces, 160 portals and 70 equipment nodes.
- Regenerated the 2D top/side hit-indicator projection directly from the current Three.js ship root:
  - 1,016 source meshes
  - 1,014 top-view polygons
  - 1,015 side-view polygons
- Verified real entry and exit damage holes on opposite hull sides at the corrected aft geometry.
- Fixed the 3D damage-scar queue fallback so an empty pending queue cannot enqueue an undefined scar.

## Physical transition from WIP09

- Full-load mass: unchanged at `9,652,445.6336 kg`
- Lightship, variable load, category masses and 157 mass nodes: unchanged
- Full-load CG Z: `4.3882570000 → 4.3752754195 m` (`12.9816 mm` lower)
- WIP10 upright GM0: `1.4130272307 m`
- Missile energy/momentum, BridgeMaster E, forward VLS hardpoint, VLS inventory, crew and topology contracts: unchanged
- WIP10 aft VLS and mass positions intentionally follow the lowered geometry.

## Verification contract

- The authored flight-deck stations must all equal `4.88 m`.
- The rendered flight deck must have exactly one unique vertical coordinate.
- Door thresholds, hangar clearance, roof/VLS plane and all aft physical hitboxes must pass the profile audit.
- Interior rendering must represent and contain all 138 spaces, 160 portals and 70 equipment nodes.
- The 2D hit indicator must identify itself as `V48_WIP10_AFT_GEOMETRY` and render the regenerated projection.
- Actual 3D entry and exit holes must be mesh-matched and attached.
- WIP09-to-WIP10 comparison must preserve non-geometry contracts and prove the intended CG/aft deltas.
- Protection physics must remain disconnected and deferred to WIP11.

## Local verification

- Inline JavaScript parse: `PASS`
- `git diff --check`: `PASS`
- Workflow YAML parse: `PASS` (`16` jobs)
- Static profile, interior, crew and BridgeMaster E contracts: `PASS`
- Playwright suite: all `15` browser tests passed after WIP10 expectation updates
- Dedicated `aft-geometry-wip10` WebGL test: `PASS`
- Multi-view visual probe: `PASS`, with no page or console errors
- Actual WebGL checks:
  - authored flat deck: `true`
  - rendered flat deck: `true`
  - door/deck continuity: `true`
  - internal alignment: `true`
  - Mk 45 named parts and barrel length: `true`
  - synchronized 2D drawing: `true`
  - attached entry/exit holes: `true`

## Artifact

- File: `Aegis_SIM_v48_WIP10.html`
- Size: `2,661,146 bytes`
- SHA-256: `2b33fe96d25ee65e4f195e5dd720f6a0d28a6d3ecdd85734976ea90456519cfa`
- Git blob: `13915a0e6d9a16cdfc680cffc5528bb86370aa69`
- WIP09 remains byte-for-byte preserved under `archive/v48/WIP09/`.

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP10.html`
- Transition baseline: `archive/v48/WIP09/Aegis_SIM_v48_WIP09.html`
- Expected jobs: `16`
- Added job: `aft-geometry-wip10`
- Required final result: `16/16 jobs passed`
- Final workflow run: [#85 / 35086383967](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/35086383967)
- Tested branch head: `9dcf95df299929b3b1f7e60739631dfe451091e3`
- Pull-request merge-test revision: `cb8ac338539121aea32d5a7c797fee18322e7d49`
- Result: `16/16 jobs passed`
- Passed jobs: `static-smoke`, `webgl-render-probe`, `aegis-3d-render`, `aft-geometry-wip10`, `ciws-b1-closure`, `ciws-b2-maneuver`, `ciws-b3-damage`, `ship-mass-ledger`, `ship-impact-penetration`, `ship-structural-fatigue`, `ship-stability-maneuver`, `ship-wave-flooding`, `ship-interior-topology`, `ship-crew-damage`, `bridgemaster-e`, `ship-profile`.

The first PR run reached `15/16`; `ciws-b3-damage` reported no failed checks but hit its 30-second startup readiness limit under runner saturation. Increasing only that readiness allowance to 60 seconds produced the clean final run. No simulator value or HTML changed.

### Captured WIP10 geometry evidence

- Authored flight deck: all 8 stations exactly `z=4.88 m`
- Rendered flight deck: one unique vertical coordinate
- Door sill / flight deck continuity: `true`
- Hangar clear height: `5.20 m`
- Interior representation and containment: 138 spaces, 160 portals, 70 equipment nodes, all `true`
- Aft mesh set: twin hangar, SeaRAM support, tapered support house, two SPG pedestals and Mk 45, all present
- 2D drawing: `AEGIS_SHIP_DRAWINGS_V48_WIP10`, 1,014 top and 1,015 side polygons
- Aft physical damage probe: starboard entry and port exit holes both mesh-matched and attached
- Protection physics: still disconnected and deferred to WIP11

### Workflow artifacts

| Artifact | ID | Digest |
|---|---:|---|
| aegis-3d-render | 10442311988 | `sha256:9cd8364334e151f4c3e0e9dee5d1ddbf30e2f361b67c1c2e6e24028de4e4c1d2` |
| aft-geometry-wip10 | 10442900403 | `sha256:6951458c25a0496232607dfdf29d49620f776c1955a406bc40c818d7841ffc3d` |
| bridgemaster-e | 10442586950 | `sha256:aa4434373f22f4a522dba7bea260af0494daea4b3372cfa5f21e5a6286283198` |
| ciws-b1-closure | 10442710864 | `sha256:e16a56916bcaf105b6b8b9e7f55a37f89bf1efd6d8e810e43b0caa37d30488c7` |
| ciws-b2-maneuver | 10441813170 | `sha256:e2172c43d1a6c28cfc719f707ff83fbd8bc31058fc00f83a61342843167747e3` |
| ciws-b3-damage | 10441999008 | `sha256:bd30d032004cc19c6ea13838f0873dfe5d9ff00ee9430ea0634d948783cd5e55` |
| ship-crew-damage | 10442288056 | `sha256:854c973cea0d3eaa64ea6ad44ed6671457d53423d3ef6a12d1be931a83eabbb1` |
| ship-impact-penetration | 10442337978 | `sha256:be6c187309afc65750ebe89c021cb7c0c7cd894d19b7c6d24ce4e673825ff876` |
| ship-interior-topology | 10441803368 | `sha256:73b3c2318a262aaf231d7ab99f3e8c058407d1843fabace990b5030bcdc4976e` |
| ship-mass-ledger | 10442278092 | `sha256:9c55a6213983049c266ea743b8f7f2b231a356fef51dbb33ec0a6abe9d33071f` |
| ship-profile | 10442377799 | `sha256:207d205c5a235adc6a615fe6adbc1e897f2b5b09600027871714e7c63ed0cadf` |
| ship-stability-maneuver | 10442371932 | `sha256:452ea94439493047eefba8f4ffd50aebfdf4009309cbfdbdb3bcce3464f5b19a` |
| ship-structural-fatigue | 10441824912 | `sha256:54d65b26acbefb5933d559a7af8ff8dcd877e5040a6a15da364248aa12439c85` |
| ship-wave-flooding | 10442721458 | `sha256:6e48c83a5761326a97650303ecbc11105990f6544e631457d27af9aff1d9cf1f` |
| webgl-probe | 10442327831 | `sha256:86b0060e4578d7c54d677e2ce8cfe3bda88fe1f63014ca9cf4e18cc9f144ba3c` |

## Repository result

- Root contains only the newest simulator and status document.
- Exact WIP09 HTML, status and checksum files are preserved under `archive/v48/WIP09/`.
- Tests and workflow target WIP10; the transition test reads the archived WIP09 baseline.
- Armor/material implementation is renumbered to WIP11.
- No release or tag is created for this WIP.
