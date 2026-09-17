# AEGIS v48 WIP11 — material and protection integration

## Scope

- Baseline: `archive/v48/WIP10/Aegis_SIM_v48_WIP10.html`
- Ground the six life-raft canisters beside the aft VLS on explicit cradles.
- Define one shared material/thickness ledger for shell plating, decks, bulkheads, doors, structural members and local vital-space protection.
- Derive both structural mass and penetration resistance from that ledger.
- Replace the legacy fixed surface/submerged shell constants in the live missile penetration path.
- Apply aramid only to fragment and rear-spall transmission, never as large-body penetration armor.
- Preserve WIP10 geometry, calibrated displacement/GM, combat behavior and all unrelated subsystem contracts.

This WIP does not add gun ammunition, shell fuzes or naval-gun ballistics. Those remain WIP12 and later work.

## Authority and limits

- Profile: `DDG_119_LATE_FLIGHT_IIA`, revision `V48_WIP11`
- Schema: `AEGIS_SHIP_PROFILE_V48_WIP11`, schema version `3`
- Protection contract: `AEGIS_MATERIAL_PROTECTION_V48_WIP11`
- Coordinate frame: ship-local metres; `+X` bow, `+Y` starboard, `+Z` up
- Material properties are public-property references used as simulation material IDs.
- Every plate thickness and structure factor is `SIM_TUNED_NOT_DDG119_SHIPYARD_DRAWING`; no unreleased DDG-119 scantling is claimed.
- The resistance model is a first-order simulation work model, not a naval classification or weapons-effect certification calculation.

Public references:

- DLA ASSIST, legacy MIL-S-24645 HSLA steel record: <https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=17677>
- ABS rules and guides for naval ships: <https://ww2.eagle.org/en/Products-and-Services/global-government/rules-and-guides-for-naval-ships.html>
- US Navy DDG-51 fact file: <https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2169871/destroyers-ddg-51/>
- HII Arleigh Burke Flight III overview: <https://hii.com/capabilities/arleigh-burke-flight-iii/>

## Aft life-raft correction

The old canisters were free-standing cylinders with no authored support relationship. WIP11 moves them into one profile-owned installation:

| Property | WIP11 value |
|---|---:|
| Canisters | `6` (`3` port, `3` starboard) |
| Longitudinal positions | `-30.4`, `-32.0`, `-33.6 m` |
| Transverse positions | `±7.25 m` |
| Canister radius / length | `0.38 / 1.25 m` |
| Support deck | `z = 10.55 m` |
| Cradle height | `0.10 m` |
| Canister centre | `z = 11.03 m` |
| Cradle top / canister bottom | both `z = 10.65 m` |

All six named canisters, cradles and chocks are under `AFT_LIFERAFT_INSTALLATION`. The WebGL audit resolves every part and measures the support gap as floating-point zero (`-1.776e-15 m`).

## Material library

| Material ID | Density | Yield basis | Simulation role |
|---|---:|---:|---|
| `HSLA_80` | `7,850 kg/m³` | `552 MPa` | shell, strength deck, primary structure and vital-space steel |
| `DH36` | `7,850 kg/m³` | `355 MPa` | weather deck, superstructure and hangar shell |
| `AH36` | `7,850 kg/m³` | `355 MPa` | internal decks, structural/watertight bulkheads and doors |
| `GRADE_A_STEEL` | `7,850 kg/m³` | `235 MPa` | light partitions and equipment casings |
| `ARAMID_SPLINTER` | `1,440 kg/m³` | separate attenuation model | fragments and rear spall only |

The direct normal resistance for a structural layer is derived as:

`R_MJ = projectileArea_m2 × thickness_m × yieldStrength_MPa × structureFactor`

The existing incidence/obliquity treatment remains downstream of this calculation. Open doors have zero direct resistance. Damaged/opening behavior continues to use the existing damage and portal state contracts.

## Representative WIP11 boundaries

The table uses the contract reference projectile diameter of `0.42 m`.

| Boundary | Material and thickness | Direct resistance | Areal mass |
|---|---|---:|---:|
| Keel / centre girder | HSLA-80 `16 mm` | `1.3827 MJ` | `125.60 kg/m²` |
| Bottom / bilge shell | HSLA-80 `14 mm` | `1.1028 MJ` | `109.90 kg/m²` |
| Waterline shell | HSLA-80 `14 mm` | `1.0707 MJ` | `109.90 kg/m²` |
| Upper side shell | HSLA-80 `12 mm` | `0.9177 MJ` | `94.20 kg/m²` |
| Strength/main deck | HSLA-80 `12 mm` | `1.0003 MJ` | `94.20 kg/m²` |
| Flight deck | DH36 `10 mm` | `0.4918 MJ` | `78.50 kg/m²` |
| General watertight bulkhead | AH36 `9 mm` | `0.4781 MJ` | `70.65 kg/m²` |
| Machinery watertight bulkhead | AH36 `10 mm` | `0.5509 MJ` | `78.50 kg/m²` |
| CIC local protection | HSLA-80 `10 mm` + aramid `12 mm` | `0.8259 MJ` steel only | `95.78 kg/m²` |
| Magazine/VLS local protection | HSLA-80 `12 mm` + aramid `15 mm` | `1.0462 MJ` steel only | `115.80 kg/m²` |
| Steering/cable local protection | AH36 `8 mm` + aramid `8 mm` | `0.4171 MJ` steel only | `74.32 kg/m²` |

The old `0.65 MJ` submerged-shell constant is removed. Bottom/bilge shell resistance is now greater than upper-side resistance because it uses the same material model with `14 mm` rather than `12 mm` plating.

## Live coupling

- All `87` physical ship hitboxes carry a material profile, structural thickness, areal density and calculated reference resistance.
- The live residual-penetration solver recalculates boundary resistance from actual projectile area and records a `MATERIAL_THICKNESS` barrier trace.
- Local CIC, magazine/VLS and steering protection uses the same ledger as mass and penetration.
- Aramid contributes exactly `0 MJ` to direct penetration resistance.
- Closed protected-space boundaries apply the following fragment transmission factors:
  - CIC: `0.435275`
  - magazine/VLS: `0.353553`
  - steering/cable: `0.574349`
- Open boundaries and a detonation originating inside the protected room use transmission `1.0`; the liner does not incorrectly shield an open doorway or suppress its own room's internal explosion.
- Ordinary unlined spaces remain at transmission `1.0`.
- WIP10's deterministic Kh-32 transition probe retains the same `5,458.9136 MJ` raw kinetic energy and geometry while exit energy changes from `204.4837 MJ` to `197.0638 MJ` through the new material barriers.

## Mass closure

Legacy hard-coded shell/deck/superstructure thicknesses were removed from the lightship builder. WIP11 derives explicit structural and local-protection mass from the material ledger, then assigns only the remaining balance to residual outfit mass:

| Ledger item | Mass |
|---|---:|
| Material-derived structure and local protection | `1,465,027.2062 kg` |
| Residual outfit allowance | `5,620,218.4274 kg` |
| Lightship closure | `7,085,245.6336 kg` |

Full-load target, calibrated mass moments and the accepted WIP10 GM contract remain unchanged. This avoids double-counting while allowing later ship profiles to change structure by editing material/thickness data.

## Rendering and diagnostics

- The Three.js root and interior batches expose WIP11 material/protection metadata without feeding renderer state back into physics.
- The 2D top/side damage drawing was regenerated from the current live Three.js root:
  - schema `AEGIS_SHIP_DRAWINGS_V48_WIP11`
  - revision `V48_WIP11_MATERIAL_PROTECTION`
  - `1,046` source meshes
  - `1,044` top polygons
  - `1,045` side polygons
- Added diagnostics:
  - `materialProtectionAuditV48Wip11()`
  - `materialPlateProbeV48Wip11()`
  - `materialPenetrationProbeV48Wip11()`
  - `aramidFragmentProbeV48Wip11()`
  - `materialBoundaryMetricsV48Wip11()`
  - `aftLiferaft3DAuditV48Wip11()`
- WIP10 profile/aft diagnostic names remain read-only compatibility aliases for archived test harnesses.

## Local verification

- Inline JavaScript parse: `PASS`
- Material/protection static contract: `PASS`
- Ship-profile static contract: `PASS`
- Browser material audit and penetration probe: `PASS`
- Browser aramid fragment-transfer probe: `PASS`
- Browser aft geometry/life-raft WebGL audit: `PASS`
- Browser WIP10-to-WIP11 transition comparison: `PASS`
- Crew damage and medical-routing regression after aramid coupling: `PASS`
- Full Playwright suite: `16/16 PASS`
- Multi-view WebGL visual probe: `PASS`, with no page or console errors
- Workflow YAML parse: `PASS` (`17` jobs)

## Artifact

- File: `Aegis_SIM_v48_WIP11.html`
- Size: `2,696,275 bytes`
- SHA-256: `38acac296e67541a9fb6c9b6166f638aac407d73fb63221fe7064b8c9dadfb8a`
- Baseline WIP10 SHA-256: `2b33fe96d25ee65e4f195e5dd720f6a0d28a6d3ecdd85734976ea90456519cfa`

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP11.html`
- Transition baseline: `archive/v48/WIP10/Aegis_SIM_v48_WIP10.html`
- Expected jobs: `17`
- Added job: `material-protection-wip11`
- Renamed geometry job: `aft-geometry-wip11`
- Required final result: `17/17 jobs passed`
- Pull-request run: `#88` (`35205577555`) — `17/17 PASS`
- Pull request: `#22`, merged
- Main merge commit: `03c058821fdbe1f79520da7c11123b28eadddd63`

## Deferred work

- Strain-rate, fracture/plugging, projectile breakup, shaped-charge behavior, fuze logic and gun-shell terminal effects belong to WIP12.
- Aramid's equipment-fragment benefit is represented in the protection contract and space transfer model; a distinct equipment fragment damage channel will be added with WIP12's separated terminal-effect channels rather than reducing the current combined blast value.
- WIP13 adds naval-gun FCS. WIP14 adds simple target ships and multiple ship profiles.
- No release or tag is created for this WIP.

## Repository result

- Root contains the newest WIP11 simulator, status and checksum set.
- Exact WIP10 HTML, status and checksum files are preserved under `archive/v48/WIP10/`.
- Tests and workflow target WIP11; the transition test reads the archived WIP10 baseline.
