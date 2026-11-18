# DEFENSE_OODA_A state and save contract

Runtime and save schema: `AEGIS_DEFENSE_OODA_STATE_A1`, revision 1.

Each `ShipRuntime` owns its own OODA state. There is no global state and no
fallback from an explicitly requested foreign owner to `ACTIVE_SHIP_RUNTIME`.

Stored runtime rows contain only:

- owner-local `trackId`, stable queue sequence and assigned slot;
- `OBSERVE / ORIENT / DECIDE / READY` phase;
- start step, remaining fixed steps, ready step and last-seen step;
- last accepted input step/revision and bounded diagnostic counters;
- minimum last-command metadata (step, revision, reason, digest).

Raw input DTOs, copied track histories, truth IDs/positions, renderer objects,
functions/closures and RNG state are forbidden. Command creation always re-reads
the current immutable input DTO and drops rows whose owner-local track no longer
exists.

## Import rules

Import validates schema/revision, owner/profile, exact keys, integer/range
bounds, duplicate track/sequence/slot values and the profile queue limit before
authoritative mutation. Invalid input is zero-mutation. Old saves without the
field start from a clean owner-local state and record a migration disposition.

Remaining service steps, not elapsed wall time, are saved. On restore, ready
steps are reconstructed from the current fixed step. Therefore save/load cannot
skip OBSERVE/ORIENT/DECIDE work and the same subsequent fixed-step inputs yield
the same ready step and command digest.

## Capacity and service

Capacity, clamps and rounding are frozen in `PROFILE_LEDGER.md`. The OODA engine
runs only at the existing `updateWip118EngagementControl` 5 Hz fixed-step
boundary. UI/render time is never a timing input.
