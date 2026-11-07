# EMITTER_A Commit C — ACTIVE adapter report

## Status

- IMPLEMENTED: the common profile-declared ship emitter resolver is tactical authority for DDG-119 and CG-52; public definitions/runtime/audit API is available.
- TESTED: exact output/receiver/RNG equivalence, same/mixed profile NPC scenes, UI ownership, operational save/restore, U3 HOJ and passive-RF behavior.
- APPROVED: `C_GATE.json` and `SCOPE_C.json` both pass; ACTIVE promotion is accepted for this branch checkpoint.
- UNRESOLVED: SOV remains deferred to Commit D; inherited project debts are unchanged.
- RELEASE: no release/tag; branch checkpoint only.

## Ownership and API

The ACTIVE resolver reads immutable equipment declarations from each
`ShipProfile` and mutable values exclusively from existing observer, damage and
EW runtime owners. The public API is read-only: definitions, validation,
runtime snapshot, SHADOW/ACTIVE audit snapshot, and physical-output snapshot.
It creates no save field and changes no save schema.

The operational round trip deliberately changed EMCON and ECM requests after
export and verified the import restored the original common-runtime snapshot
exactly for both DDG and CG. Existing DOM controls were not recreated: their
ids remained unique, and clicking the existing EMCON/radar and ECM controls
changed the same existing owners observed by the new adapter.

See `C_GATE.json`, `SCOPE_C.json`, and `changes-C-active.diff`.
