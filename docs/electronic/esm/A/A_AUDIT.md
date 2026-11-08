# ESM_A Commit A — baseline and ownership audit

## Confirmed merged baseline

- `main`: `babb4d7f6d42cc8d774feadce17d8108b3a24040`
- PR #74: merged into that commit
- product: `Aegis_SIM_v48_WIP_EMCON_B.html`
- bytes: `22,162,415`
- SHA-256: `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`
- packed main SHA-256: `2cc2dc1a130f54d7970df9f4be8c8ae4d565d9b65af001ef718cf1fd90fa4d64`

## Existing ownership

| Concern | Current owner | Commit-A finding |
|---|---|---|
| Physical RF scene | `electronicPhysicalEmittersF()` | truth remains internal to physical/sensor synthesis |
| Passive receive synthesis | `electronicReceiverPlotsF()` | uses truth internally; outputs anonymous bearing DTO only |
| Contact association | `electronicAcceptPlotsF()` | `ShipRuntime.ew.executionF.contacts`; bearing-only, no point state |
| Contact lifetime | `stepElectronicReceiversF()` | inherited 0.2 s revisit, 12 s hold, 96-contact cap |
| Tactical presentation | `drawRadar()`, `mapEsmReadA()` | current bearing ray incorrectly reuses current ownship origin |
| Friendly network | `prepareNetworkG()`, `networkFixedStepG()` | shares SELF/TRACK only; no raw ESM path |
| Save | operational ship/fleet EW settings | raw ESM history/estimate is not yet persisted |
| Reset/destroy | `resetElectronicFleetF()`, `retireElectronicF()`, network equivalents | contacts/queues have explicit owners but no ESM_A state yet |
| Missile passive RF | `asmPassiveRfMeasurementB2()` | seeker-specific gate; not copied into ship ESM |
| SOV | `sovNoEquipmentA`, inactive Band Stand/MR-184 metadata | remains inactive and outside ESM_A adapters |

## Commit-A gate

`baseline_audit.py` verifies the merged product, deterministic exact rebuild, packed-main hash, existing anonymous measurement whitelist and frozen function hashes. Existing correction-3 EMCON binding static/runtime gates remain PASS with page and console errors zero. No product byte or game behavior changes are made in Commit A; MAX_THREAT broad regression is not run here.
