# SEEKER_UNIFY_U4 Commit A — SARH bistatic adapter

## State

- IMPLEMENTED: SARH bistatic echo/cell/measurement adapter and explicit `SARH_BISTATIC_4D` profile.
- TESTED: SHADOW and ACTIVE limited deterministic gate.
- APPROVED: structure-only migration under `LEGACY_EQUIVALENCE`.
- UNRESOLVED: none in Commit A scope.
- RELEASE: no; U4 is not releasable until Commit C and the one final broad regression pass.

## Contract and ownership

The physical SARH front end retains ownership of the illuminator opportunity, SPG-62 state,
transmit beam, receive beam/gimbal, both LOS legs, bistatic RCS/power, clutter and the existing
weapon-local RNG.  The common layer receives only anonymous SI-unit echo/cell/measurement data.
It does not receive an entity/profile/faction identifier or a truth reference, does not consume
RNG and does not own a mutable tactical singleton.

The ACTIVE route preserves the legacy arithmetic order for bistatic power and unresolved-cell
decisions.  Echo and measurement DTOs are materialized at the common boundary while the existing
tactical carrier remains the return value, preserving downstream state, UI and guidance contracts.

## Limited gate

Evidence: `A_GATE.json`, `BUILD_A_SHADOW.json`, `BUILD_A_ACTIVE.json`.

- Baseline, SHADOW and ACTIVE fixed-tick surface-SARH fixture outputs: exact match.
- Baseline, SHADOW and ACTIVE live SM-2 surface-SARH flight: exact match; physical contact and
  `SURFACE_TARGET_CONTACT` termination preserved.
- ACTIVE fresh-page repeat with the same seed: exact match.
- Bistatic power comparisons: 20,088; mismatches: 0.
- Cell-resolution comparisons: 411,299; mismatches: 0.
- Actual live packet: 46 echoes, 45 measurements, local `TRACK`, authority `SARH_RF_EKF`.
- Synthetic two-leg matrix: transmit LOS, receive LOS, transmit beam and receive beam each fail
  closed when independently removed; normal two-leg measurement is 4-D with a 4x4 covariance.
- Adjacent/far cell branches, sea-clutter/shared echo chain and single-target return: exercised.
- Initial core self-tests and page/console errors: 0.
- Source-arbiter static contract preserves SARH-only and `DUAL_MODE_ARH_SARH` priorities; its
  implementation hash is unchanged.

The short RF fixture also contains downstream surface-contact checks that are intentionally false
before its separate swept-contact sub-fixture.  Commit A gates only its eight SARH observation and
release-contract checks; the real live-flight fixture supplies the end-to-end contact result.

## Protected code

The build receipts prove unchanged hashes for release authority, missile body/flight physics,
SARH target-state consumption, source arbitration, bistatic RCS and both beam-gain functions,
RAM authority/guidance, Harpoon and ASM seeker paths.  No broad regression was run at this
intermediate commit.

## Harness corrections

Two harness-only assumptions were corrected before the passing run: the RF fixture's aggregate
`pass` includes damage checks outside this adapter gate, and deterministic repeat comparison must
use a fresh page because the diagnostic fixture deliberately advances allocator-only state.
Neither correction changes the product candidate.
