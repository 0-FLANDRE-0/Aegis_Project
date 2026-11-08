# EMCON_B final report — PR #74 corrections 2–3

## 1. Status

| State | Result |
|---|---|
| `IMPLEMENTED` | Commits A–E plus corrections 2–3: explicit per-ship global radiation master, neutral consumer-to-equipment bindings, common category/equipment UI, V2 lifecycle |
| `TESTED` | Correction-specific static/Chromium gates, synthetic non-SPY profile, D/E gates, release smoke, baseline exact comparison, and legacy lock 14/14 |
| `APPROVED` | Local correction closure is PASS; remote candidate Actions is recorded in PR #74 after publication |
| `UNRESOLVED` | `CONFIRMED_ONLY` performance; physical SPG-62 registration; communication EMCON; inherited runner/harness debt |
| `INHERITED_DEBT` | CIWS seed 419025, CG paired observer delta 2, U3 raw paired delta 4, WIP12D speed determinism, Kh-32 60 km, and the pre-correction broad-run items below |
| `RELEASE` | `false`; no merge, tag, or release |

Base is merged EMITTER_A `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941` (PR #73). The baseline product SHA-256 is `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`.

The corrected candidate is `Aegis_SIM_v48_WIP_EMCON_B.html`, 22,162,415 bytes, SHA-256 `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`. Packed-main SHA-256 is `2cc2dc1a130f54d7970df9f4be8c8ae4d565d9b65af001ef718cf1fd90fa4d64`.

## 2. Corrected radiation contract

`AEGIS_SHIP_EMCON_B_2` adds authoritative `allRadiationSilent` and minimal radar-master restore metadata to each ShipRuntime. V1 state migrates explicitly with global silence OFF while preserving detail policy and the existing master boolean.

Effective emission priority is fixed as follows:

1. registry/install/physical-emission eligibility;
2. damage, power, enabled, and ship-offline gates;
3. `ALL_RADIATION_SILENT` hard-off;
4. existing radar master silence;
5. existing network group overlay for radar;
6. equipment override;
7. category policy;
8. ECM request and allocator.

Thus `FORCE_RADIATE` cannot bypass global silence, damage/offline, inactive registration, radar master, or network silence. Global silence preserves ECM noise/deception requests but immediately zeros allocator resource, physical output, receiver coupling, and HOJ evidence. Hawklink/Link communication remains separate and unchanged.

Actual own/NPC radar and IFF paths request only the neutral consumers `AIR_SEARCH_VOLUME`, `SURFACE_SEARCH_SCAN`, and `NAVIGATION_SCAN`. Immutable ShipProfile emitter-registry rows bind each consumer to one exact installed equipment ID. Missing, ambiguous, nonexistent, category-mismatched, or output-kind-mismatched bindings fail closed; category-wide `some()` is never a substitute. ECM physical and allocator paths continue to use the exact ECM equipment decision.

## 3. UI contract

- The existing chip only opens/closes the menu and does not change radiation state.
- The single large top control is `전파방사통제`; its color and `aria-pressed` read only the authoritative global state.
- Category and equipment controls are generated from the selected ShipProfile registry. The UI contains no DDG/CG equipment IDs.
- While global silence is ON, every operational child control displays OFF but remains selectable.
- Selecting an installed radar/ECM row atomically clears global and radar-master silence, resets every category to SILENT and every override to INHERIT, then enables only the selected category/equipment.
- ECM permission distinguishes `ARMED · 대기` from actual `TX`.
- `FIRE_CONTROL` is disabled as `등록 장비 없음`; SOV inactive entries cannot be enabled.
- New controls measure 36 px minimum and the menu remains within 1400×900, 832×384, and 390×844 viewports.

## 4. Correction-specific verification

| Gate | Result |
|---|---|
| Static correction audit | PASS, 15/15 |
| Neutral binding static audit | PASS, 17/17 |
| Neutral binding runtime audit | PASS, 16/16 |
| Global hard-silent + breakout | PASS, 10/10 |
| D UI/owner routing | PASS, 13/13 |
| E save/network/lifecycle | PASS, 17/17 |
| Uninstrumented release smoke | PASS, 7/7 |
| EMITTER_A default/master comparison | PASS, 6/6 |
| Legacy lock debt | PASS, 14/14 |
| Page errors / console errors | 0 / 0 |

The hard-silent gate covers DDG and CG as both active ship and NPC owner. It begins with every active radar/ECM override at `FORCE_RADIATE`, ECM requests present, and allocator resource above zero. After global silence: every decision is denied with `ALL_RADIATION_SILENT`, physical emitters and own/NPC measurements are zero, blocked sensor RNG is unchanged, ECM requests remain, allocator/coupling/HOJ are zero, and communication-link fingerprints are exact.

Separate fixtures verify SPY-only, SPQ-only, NAV-only, and ECM-only breakout. Each command completes without an intervening fixed tick and advances the detail revision once. Damage and ship-offline probes remain fail-closed. DDG→CG, CG→DDG, DDG→DDG, and CG→CG UI routing preserve owner isolation.

Correction 3 additionally traces all three neutral consumer IDs through DDG/CG player and NPC sensor/IFF calls. A synthetic profile whose registry and UI contain no SPY/SPQ name verifies profile-only UI generation, hard-off, exact physical output, and selective breakout. Its second AIR_SEARCH device remains allowed while the bound primary is forced silent; the air category is therefore allowed but `AIR_SEARCH_VOLUME` remains denied, proving that another same-category device cannot substitute. Missing, duplicate, and nonexistent binding fixtures all deny and reject restore with zero mutation.

Lifecycle evidence covers exact V2 round-trip, V1→V2 migration, missing-state defaults, invalid type/restore/category/equipment/profile zero-mutation rejection, reset, destroy, group overlays, and tactical-AI non-ownership.

## 5. Broad regression boundary

The MAX_THREAT broad runner was **not rerun** on correction SHA `50cbf50f…f96ee`, as required. Its one prior execution belongs to pre-correction SHA `3343f5bb…c33` and remains immutable evidence.

At that old SHA, completed PASS rows were helicopter 85/85, ISAR classes 8/8, ISAR clock 12/12, Sovremenny native 30/30, casualty 13/13, visual 10/10, paired 42/42, and real WebGL 29/29. Raw incomplete Chromium crashes and the inherited SOV/UI fixture differences remain preserved in `FINAL_REGRESSION.json` and `FINAL_REGRESSION_CLASSIFICATION.json`; none are relabeled PASS.

The corrected SHA is approved only by the limited closure matrix listed in section 4 and the manifest-based candidate Actions.

## 6. Build and scope integrity

- Exact rebuild: byte-for-byte PASS.
- Release product contains no correction, lifecycle, or lock diagnostic adapters.
- RF/Pd/noise/RCS/beam constants, EKF, IFF/ROE, weapons, guidance, fuze, damage/ship physics, communication links, SPG-62 registration, and SOV capability are unchanged.
- Expected values and tolerances changed: 0.
- Candidate manifest is `AEGIS_CURRENT_PRODUCT.json`; unknown stages remain fail-closed.
- Workflow runs on `ubuntu-24.04` and now executes both correction static/runtime gates, D/E gates, release smoke, baseline comparison, and lock gate.

## 7. Publication boundary

- Branch: `emcon-b`;
- PR: existing #74 only;
- `main`: unchanged;
- merge/release/tag: prohibited until user decision;
- executable HTML ZIP and report ZIP are separate;
- commit-pinned full-byte remote readback and final Actions run are recorded in PR #74 after the final push.

`CONFIRMED_ONLY` performance remains `UNVERIFIED`. Communication EMCON and physical SPG-62 registration remain separate follow-up work.
