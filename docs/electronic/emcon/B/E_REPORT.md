# EMCON_B Commit E report

Status: **IMPLEMENTED + TESTED**. Release and merge remain false.

## Implemented contract

- `AEGIS_SHIP_EMCON_B_1` is exported for the active ship and every physical fleet ship.
- Legacy snapshots migrate to profile-derived `RADIATE` / `INHERIT` defaults while retaining
  the existing master `emcon` boolean.
- Unknown category, equipment, enum, registry, or profile data is rejected during clone-first
  preflight. Rejected imports make zero authoritative mutation.
- Network group modes remain transient overlays. They never rewrite category policy or equipment
  override state. `ACTIVE` may clear the master radar-silence overlay, but damage and
  `FORCE_SILENT` still win. `INDIVIDUAL` and lease expiry restore each ship's prior master state.
- An operator detail command under a group overlay is retained as an individual manual detail
  policy and recorded as `MANUAL_DETAIL_UNDER_GROUP_OVERLAY`; it does not bypass a group-silent
  overlay.
- Tactical AI still controls only the pre-existing master policy and does not create or replace
  detail policy.
- Reset creates profile defaults. Destroy clears the all-radiation memory and detail root before
  retiring the runtime, leaving no owner-addressed reference.
- Communications remain a separate network policy and were not gated by radar EMCON.

## Deterministic evidence

`E_STATIC.json` passes protected-scope, schema, migration ordering, strict preflight, unchanged
network functions, unchanged tactical implementation, communications separation, and the absence
of diagnostic code from the product.

`E_GATE.json` ran in actual Chromium for DDG→CG and CG→DDG ownership combinations. All 16 checks
pass:

- group SILENT overlay and manual-detail audit;
- exact INDIVIDUAL restoration;
- ACTIVE lease with `FORCE_SILENT` precedence;
- `PLAYER_SEARCH` and `ALLY_SEARCH` split modes;
- expired follower lease restoration;
- communications and connected-peer state preserved;
- tactical evaluation does not mutate detail policy;
- exact save round-trip;
- invalid import rejection and zero mutation;
- legacy migration defaults;
- reset defaults and destroy cleanup;
- enemy and inactive SOV operator-command rejection;
- console errors 0 and page errors 0.

The diagnostic wrapper is test-only and inverse-removable byte-for-byte. The release product has
no `__EMCON_B_E_DIAG__` symbol.

## Scope limit

`FIRE_CONTROL` remains a schema/UI category with no active registered equipment. No SPG-62 RF
model or new emitter was added. Network leases themselves remain transient and are intentionally
not serialized; their underlying individual master/detail settings and the group-mode setting are
serialized, after which a live link may issue a fresh lease.

## Next gate

Run the retired `#lockBtn` 14-case browser debt against the current UI contract, then the single
final MAX_THREAT broad regression. No expectation or tolerance was changed in Commit E.
