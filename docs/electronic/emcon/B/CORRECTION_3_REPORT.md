# EMCON_B PR #74 correction 3 — ship-class-neutral sensor binding

## Outcome

| State | Result |
|---|---|
| `IMPLEMENTED` | Neutral `consumerId -> equipmentId` bindings are immutable ShipProfile emitter-registry data |
| `TESTED` | Static 17/17, binding/runtime 16/16, correction-2 10/10, D UI 13/13, E lifecycle 17/17, release 7/7, baseline 6/6, lock 14/14 |
| `APPROVED` | Local limited closure PASS; final remote Actions and readback are recorded in PR #74 after push |
| `UNRESOLVED` | Communication EMCON and active FIRE_CONTROL equipment remain out of scope |
| `RELEASE` | `false`; PR #74 remains unmerged |

The product remains `AEGIS_SHIP_EMCON_B_2`; no V3 save schema was added. RF/Pd/noise/RCS/beam, EKF, IFF/ROE, weapons, damage, communication links, and tactical AI were not retuned or rewritten.

## Contract

Sensor code requests only these ship-class-neutral capabilities:

- `AIR_SEARCH_VOLUME`
- `SURFACE_SEARCH_SCAN`
- `NAVIGATION_SCAN`

Each active ShipProfile emitter registry owns an immutable binding row with exactly two fields: `consumerId` and `equipmentId`. DDG-119 maps them to `AN_SPY_1DV`, `AN_SPQ_9B`, and `BRIDGEMASTER_E`; CG-52 maps them to `AN_SPY_1A_MODERNIZED`, `AN_SPQ_9`, and `AN_SPS_73`. The inactive Sovremenny registry owns an empty binding list.

`emconResolveConsumerBindingB` resolves exactly one row and exactly one registered physical equipment item. `emconConsumerDecisionB` then applies that equipment's installation, enabled state, damage, generator/ship-offline state, global hard-off, radar master, network overlay, equipment override, and category policy. A different allowed item in the same category cannot satisfy the consumer.

Missing bindings, duplicate bindings, nonexistent or duplicate equipment IDs, category mismatch, and output-kind mismatch all fail closed with explicit diagnostic reasons. Invalid profile bindings are also part of V2 state/preflight validation; restore is rejected before mutation. Explicit reuse of one equipment by multiple consumer rows is not rejected merely because the equipment ID repeats.

The old `emconReceiverDecisionB` / `emconReceiverAllowsB` API is removed. No common EMCON query call uses `SPY`, `SPQ`, or `NAV` as a consumer key. Existing implementation-internal scheduler, rotor, sensor-model, and equipment registration names remain where they describe the actual installed hardware.

## UI and lifecycle

The chip, single `전파방사통제` control, common category rows, and equipment override rows are unchanged. UI rows still come from the selected profile registry and never display `consumerId`. The synthetic non-vendor profile contains no SPY/SPQ names and renders only its registered generic equipment names.

Bindings are static profile data and are not serialized. V1→V2 migration, V2 exact round trip, invalid-import zero mutation, reset, destroy, and group overlay behavior remain unchanged.

## Verification

`CORRECTION_3_STATIC.json` proves the packed release has no legacy receiver API, forbidden consumer keys, vendor-specific UI IDs, or diagnostic payload. `CORRECTION_3_GATE.json` covers DDG and CG as both player and NPC, traces all three neutral consumer IDs through actual sensor and IFF calls, and repeats the synthetic profile fixture deterministically.

The synthetic profile registers two AIR_SEARCH devices. With the bound primary forced silent and the unbound peer still allowed, category-wide permission remains true while `AIR_SEARCH_VOLUME` remains denied; only the unbound peer can physically emit. This is the direct no-`some()`-bypass test.

Malformed synthetic bindings cover missing, ambiguous, and nonexistent equipment references. All three consumer decisions deny, and attempted V2 restore throws with byte-identical pre/post runtime state.

The prior broad MAX_THREAT run belongs only to pre-correction SHA `3343f5bb…c33`. It was not rerun or attributed to this correction. Expected values and tolerances changed: 0.
