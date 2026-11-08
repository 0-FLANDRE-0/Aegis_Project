# AEGIS v48 WIP EMCON_B status

- Base: merged EMITTER_A `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941`
- Baseline product: `Aegis_SIM_v48_WIP_EMITTER_A.html`
- Baseline SHA-256: `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- Branch: `emcon-b`
- Product target: `Aegis_SIM_v48_WIP_EMCON_B.html`
- Candidate: 22,159,899 bytes / SHA-256 `e08cc2aede89e6452786efbf97fbd8ef49480ab33f8f8da178cbee0bff87377f`
- State: Commits A–E plus PR #74 correction 2 IMPLEMENTED + TESTED; explicit V2 global hard-off, exact equipment consumers, common UI, lifecycle migration, lock 14/14 and local correction gates pass; the one broad run remains pre-correction evidence only; remote Actions/PR publication is recorded outside this status; RELEASE=false

## Commit A

- Corrected the archived PR #73 state from OPEN to user-merged.
- Classified existing master owners, compatibility readers, physical/sensor/weapon gates,
  UI routing, and diagnostics.
- Frozen 20 baseline function hashes, the exact 40,783,829-byte packed main script
  hash, and representative merged EMITTER_A evidence.
- Product HTML behavior change: none.

## Commit B

- Added per-owner detail policy without duplicating the existing radar master. Correction 2
  advances the persisted contract to `AEGIS_SHIP_EMCON_B_2` with explicit
  `allRadiationSilent` authority and minimal radar-master restore metadata.
- Strictly rejects unknown profile/category/equipment/enum and inactive FORCE requests.
- Pure query applies registration, operational, master, network, override and category priority.
- Actual resolver stays authoritative; SHADOW observes its single output without a second resolver call.
- Static protected-hash gate and actual Chromium DDG/CG/mixed/same-class/offline/SOV/ECM matrix PASS.
- Default policy is exact with EMITTER_A, query RNG consumption 0, page/console errors 0.

## Commit C

- Activated policy consumption in physical emitters and the own/NPC SPY, surface-search,
  and navigation-radar measurement paths.
- Category silence produces zero new measurements and zero blocked-sensor RNG consumption;
  existing lifecycle age/coast paths remain intact.
- ECM silence preserves requests but produces allocator resource 0, physical jammer 0,
  receiver coupling 0, and HOJ evidence 0; re-radiation resumes normally.
- DDG/CG default physical matrices remain exact with EMITTER_A; mixed and same-class owner
  scenes pass; page and console errors are 0.
- Evidence: `docs/electronic/emcon/B/C_REPORT.md`, `C_STATIC.json`, and `C_GATE.json`.

## Commit D

- Extended the existing MAP EMCON chip/menu with registry-generated category and equipment
  controls; no DDG/CG equipment IDs are hard-coded in UI code.
- Verified override priority, damage/offline precedence, selected-owner routing, mixed/same-class
  isolation, and render-time zero mutation.
- `FIRE_CONTROL` is honestly shown as a contract-only row with no registered equipment.
- The corrected single top `전파방사통제` control reads only authoritative global state.
  It overrides every radar/ECM `FORCE_RADIATE` decision while preserving ECM requests.
- Selecting SPY/SPQ/NAV/ECM during global silence atomically clears global/master silence,
  normalizes all categories/overrides, and enables only the selected equipment/category.
- 1400×900, 832×384, and 390×844 layouts remain inside the viewport with 36 px new controls.
- Evidence: `docs/electronic/emcon/B/D_REPORT.md`, `D_STATIC.json`, `D_GATE.json`, and screenshots.

## Commit E

- Added authoritative per-owner V2 global/detail export, V1 migration, strict preflight,
  exact round-trip restore, reset defaults, and destroy cleanup.
- Preserved group EMCON as a transient overlay and verified SILENT/ACTIVE/PLAYER_SEARCH/
  ALLY_SEARCH/INDIVIDUAL behavior for DDG→CG and CG→DDG.
- Operator detail changes under a group overlay are recorded as
  `MANUAL_DETAIL_UNDER_GROUP_OVERLAY`; the group overlay retains higher priority.
- Tactical AI does not write detail policy and communications remain outside radar EMCON.
- Actual Chromium gate after correction 2: 17/17 checks PASS, page errors 0, console errors 0.
- Evidence: `docs/electronic/emcon/B/E_REPORT.md`, `E_STATIC.json`, and `E_GATE.json`.

## Final verification

- Retired `#lockBtn` debt: actual Chromium 14/14 PASS at 390/1100 px. MAP_E's intentionally
  detached visible node required a test-only adapter; the native product listener was retained.
- The MAX_THREAT broad regression ran exactly once on the **pre-correction** product SHA
  `3343f5bb…c33` (2,224.21 s). It was not rerun on the corrected product. Helicopter 85/85,
  ISAR class 8/8, ISAR clock 12/12, SOV native 30/30, casualty 13/13, visual 10/10,
  paired 42/42, and real WebGL 29/29 pass.
- Raw broad evidence also preserves incomplete inherited runner/harness rows. Chromium crashed
  before assertions in six large existing diagnostic paths; SOV deployment 13/15 and the
  UI213 832.CG.PIP fixture differences reproduce on the unchanged EMITTER_A baseline. They are
  not relabeled PASS. See `FINAL_REGRESSION_CLASSIFICATION.json`.
- Corrected-candidate limited closure: manifest/bytes/SHA and exact rebuild PASS; correction
  static 15/15, global hard-silent/breakout 10/10, D UI 13/13, E lifecycle 17/17,
  uninstrumented release smoke 7/7, baseline Chromium 6/6, and lock 14/14 PASS;
  page/console errors 0.
- Expected values and tolerances changed: 0. `CONFIRMED_ONLY` performance remains UNVERIFIED.

## Publication boundary

- Final report: `docs/electronic/emcon/B/FINAL_REPORT.md`.
- The correction candidate is approved only by the limited closure matrix and the single
  manifest-selected candidate Actions run. Prior broad evidence is not attributed to its SHA.
- `FIRE_CONTROL` remains contract/UI-only because no active SPG-62 registry item exists.
- Communication EMCON is not implemented; Hawklink/Link behavior remains separate.
- PR #74 is the intended review vehicle. The user retains merge authority; main, release and tag
  remain unchanged until that decision.

No main mutation, merge, release, or tag is authorized by this status.
