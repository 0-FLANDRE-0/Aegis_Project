# HP_A Commit B — common outcome contract

Status: `IMPLEMENTED / TESTED` (bounded gate only; final broad regression is reserved for Commit C)

## Product checkpoint

- Base: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- Base SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- Phase-B product bytes: `22,199,339`
- Phase-B product SHA-256: `5a337cf54c1f7a6423a5270a1eb4f37c08d70263fc68e6426b8e5b7beeefafa1`
- Packed-main SHA-256: `90b39db3b90edee3d2fca40873995932381aa7a82875705ee591c264b5dc26b3`

`build_product.py --phase B` stops after the common one-way outcome projection is
ACTIVE. Save migration, legacy-authority consumer removal and presentation closure
are deliberately deferred to phase C.

## Contract

`shipOutcomeA(runtime)` now derives, without writing back to physical models:

- physical survival from the existing `createShipSurvivalV1` snapshot;
- mission state from existing equipment-offline and crew-combat-unavailable gates;
- damage severity from the exact `computeShipStatus().overall` compatibility alias;
- display HP as zero only for irreversible/lost physical state, otherwise `1..100`.

The player global `shipHP` and NPC `runtime.health.shipHP` are written only by the
same projection path after impacts and fixed damage/flood ticks. Protected damage,
flood, longitudinal-strength and survival functions are byte-identical to U4.

## Bounded gate

Evidence: `evidence/commit-b/core-gate.json`

- Result: `PASS` (11/11 checks, page/console errors 0)
- DDG and CG reversible severity 100: display HP 1, irreversible false
- Fixed Kh-35 scene: flight/discrete state/RNG preserved; reversible display HP positive
- SOV controlled casualty: recoverable CRITICAL remains positive, irreversible and
  LOST transitions produce zero, irreversible-loss and sunk events exactly once
- Duplicate fixed ticks: no duplicate loss callbacks
- 1x/8x/16x: physical state, outcome, crew and RNG exact

JavaScript engine processes showed last-bit variance in continuous floating values
while all discrete state and RNG stayed exact. The raw comparison is preserved:

- numeric comparison tolerance: `1e-12` (diagnostic-only; no game threshold)
- damage severity maximum delta: `1.4210854715202004e-14`
- flood/survival maximum delta: `3.0531133177191805e-16`
- flight, crew and RNG delta: zero

No gameplay coefficient, damage weight, RNG stream, or acceptance threshold was
changed to obtain this result.
