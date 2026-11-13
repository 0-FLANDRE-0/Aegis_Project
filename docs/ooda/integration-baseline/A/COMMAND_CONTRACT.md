# AEGIS_DEFENSE_DECISION_COMMAND_A1

The command is a deep-frozen advisory from provider `LEGACY_H1`. It cannot reserve or fire a weapon. Existing WIP118/119, A3, Network G, FCS, reserve, damage, EMCON and release gates remain authoritative after the advisory is consumed.

## Exact fields

| Field | Contract |
|---|---|
| `schema` | `AEGIS_DEFENSE_DECISION_COMMAND_A1` |
| `provider` | `LEGACY_H1` |
| `ownerEntityId` | exactly matches the input/runtime owner |
| `inputStep`, `inputRevision` | exactly match current fixed step and input revision |
| `trackOrder[]` | unique owner-local IDs present in the input |
| `priorities[]` | unique `{trackId, score}` rows; finite score only |
| `salvoOverrides[]` | unique `{trackId, weapon, desiredSalvo, reason}`; known local ID, allowed weapon, integer 0-4 |
| `advisoryHold`, `deferUntilStep` | advisory-only hold/defer; no direct state transition or release |
| `reason` | non-empty bounded diagnostic reason |

No additional fields are accepted. The command itself and all descendants must be frozen.

## Fail-closed validation

Validation rejects schema/field mismatch, owner mismatch, stale step or revision, unknown or duplicate local IDs, non-finite scores, duplicate or out-of-range salvo rows, mutable objects and forbidden authority/truth fields. A rejected command is not consumed; the existing native path remains the safe fallback.

## Authority explicitly excluded

The port cannot:

- call VLS, RAM, Phalanx, gun, Harpoon or any release function;
- change A3 identity/threat/engagement authority;
- create SPG reservations or Network G leases;
- bypass reserve, re-engagement brake, EMCON, damage or FCS gates;
- command H2 navigation, H3 surface attack or H4 team behavior;
- suppress or initiate immediate local CIWS defense.

## LEGACY_H1 transition

The adapter computes the existing direct H1 order/salvo/recommendation result and the provider result from the same owner-local inputs. It records an exact JSON comparison before the provider result is consumed. SHADOW produced zero mismatches, then the narrow ordering/salvo consumer moved to ACTIVE; all downstream safety and execution code stayed in place.

## Evidence

`CONTRACT_ORACLE.json` exercises a valid command plus owner, step, revision, track-order, duplicate, extra-authority, mutability and cross-owner rejection cases. `BASELINE_ORACLE.json` and `CANDIDATE_ORACLE.json` have the same deterministic game-state digest.

