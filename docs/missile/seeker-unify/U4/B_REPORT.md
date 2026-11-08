# SEEKER_UNIFY_U4 Commit B — RAM passive RF/IR adapters

## State

- IMPLEMENTED: separate `PASSIVE_RF_2D` and `PASSIVE_IR_2D` anonymous measurement adapters,
  used by both player and ship-owned/NPC wrapper paths.
- IMPLEMENTED: narrow physical-emitter signal ownership correction.
- TESTED: SHADOW equivalence, ACTIVE deterministic direct flight and authority/dropout matrix.
- APPROVED: the signal-ownership correction is the sole allowed behavior change in Commit B.
- UNRESOLVED: full NPC combat exercise remains part of the one final broad regression; both
  closure-private owner declarations are nevertheless wrapped and the owner contract is directly
  exercised at the adapter boundary here.
- RELEASE: no.

## Measurement contract

The RF and IR physical front ends retain propagation/LOS, emitter or heat-source synthesis,
sea clutter, flare handling, dwell scheduling and the existing owner-local RNG.  Their outputs are
converted to anonymous azimuth/elevation measurements with 2x2 covariance and quality fields.
`_debugKind`, target/object IDs, faction and truth references are not copied.  The downstream RAM
carrier is preserved exactly, so this structural move does not change authority or guidance.

Two `ramRfMeasurement` and two `ramIrMeasurement` declarations were found: one pair in the
ship-owner context and one pair in the player context.  All four now route through the same common
adapter with explicit `OWNER`/`PLAYER` observation ownership.  Their physical candidate generation
remains hardware-context-specific.

## Confirmed ownership defect and narrow fix

The previous `ramEmitterStrength` read the emitting missile's `seeker.trackQuality` or
`_seekerQuality`.  That made a physical transmitter depend on a receiver/local tracker state and
could couple otherwise independent RAM/ASM state.  ACTIVE now preserves the existing default
signal expression `.65 + .55 * .75 = 1.0625` but removes those tracker reads.  Emission on/off,
propagation, sensitivity, Pd, gates, timing and RNG are unchanged.  SHADOW records but does not use
the corrected value.

## Limited gate

Evidence: `B_GATE.json`, `BUILD_B_SHADOW.json`, `BUILD_B_ACTIVE.json`.

- SHADOW vs Commit-A baseline: motion case, RF direct flight and IR-only direct flight all exact.
- ACTIVE same-seed fresh-page repeat: exact for all three cases.
- Existing 6 km full RAM motion case: same result and duration before/after.
- RF-emitter direct flight: expected source-switch timing changed; closest approach changed from
  2.388 m to 4.909 m, with no sea impact and the same eight authority switches.  No result tuning
  was performed.
- IR-only direct flight: exact (closest approach 1.437 m).
- Authority matrix: RF-only promotion, IR-only promotion, RF-first then IR takeover, IR dropout to
  RF, total dropout to MEM, and two-missile state isolation all pass.
- RF routes: 2,119; IR routes: 2,119 in the ACTIVE gate page.
- Truth-field violations: 0; common-layer RNG consumption: 0; page/core failures: 0.
- The intentional ownership difference was observed 299 times in actual/synthetic routed calls;
  maximum signal delta was 0.275.  No other protected function hash changed.

No broad regression was run at this intermediate commit.
