# SEEKER_UNIFY_U3 plan

## Baseline

- Branch: \`seeker-unify-u3\`, forked from \`origin/main\` \`be19f46794705a18bfd69feba99d7a4b00dd4a0c\`
- Product: \`Aegis_SIM_v48_WIP_CUE_A_1.html\`
- Product SHA-256: \`0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a\`
- Main script SHA-256: recorded by \`BUILD_*.json\` at each checkpoint
- Archive decision audit: \`docs/archive/DECISIONS.md\` through 2026-11-06

No conflict was found between the current product/archive and the U3 directive. The
directive's section 11 choices are frozen before effect tests.

## Status vocabulary

- \`IMPLEMENTED\`: code exists in the checkpoint product.
- \`TESTED\`: the named test was actually executed and its evidence is present.
- \`APPROVED\`: a gate passed or a user decision explicitly permits the change.
- \`UNRESOLVED\`: implemented or observed work that does not satisfy a completion gate.
- \`RELEASE\`: publication state only; U3 may create a PR but may not merge, tag, or release.

## Commit sequence

1. **A — U2 common-layer connection**
   - Move Harpoon's existing monostatic power expression and pre-resolved-cell
     ordering/cap into profile-selected U2 adapters.
   - SHADOW first, then ACTIVE only after bit equality.
   - Preserve Harpoon RNG calls, Pd, noise, beam/gimbal, target evidence, and state machine.
2. **B — CUE_A data contract**
   - Convert frozen launch-track memory into the existing exact-discrete Singer
     covariance contract.
   - General track mode removes the fixed 4 km cap; existing seeker range,
     gimbal, activation range, and scan pattern remain the physical limits.
   - Route mode remains a 4 km \`ROUTE_PLAN_PRIOR\` and is never submitted as a
     measurement update.
3. **C — HOJ contract**
   - Harpoon HOJ is \`ASSUMED_THREAT\`: active in \`MAX_THREAT\`, inactive in
     \`CONFIRMED_ONLY\`.
   - State is missile-owned and never shared with an ASM instance.
   - No Harpoon midcourse passive-RF feature is added.
4. **D — passive RF candidate policy**
   - After the existing Mahalanobis gate, minimize \`d^2 + ln(det(S))\`.
   - Deterministic observable-only tie break; no source ID/platform/truth input.

## Validation policy

- Intermediate checkpoints: changed-function scope/hash audit, deterministic
  stage test, representative branch cases (at most 30 per branch), truth/RNG/
  lifetime audit. No broad suite.
- Final checkpoint: one \`MAX_THREAT\` broad regression. \`CONFIRMED_ONLY\` receives
  static checks and limited feature-off scenes and remains performance
  \`UNVERIFIED\`.
- No expected value or tolerance is changed merely to make a gate pass.
- Existing inherited debts remain visible and are not counted as U3 successes.

## Constant and provenance freeze

Commit A adds no gameplay constant. Its U2 Harpoon profile contains only existing
values/semantics and is tagged \`LEGACY_EQUIVALENCE\`.

Commit B creates no replacement range cap. It reuses the already approved
\`ASM_CUE_A_SPEC\` Singer process, 3-sigma basket convention, and maximum maritime
target speed, plus the existing Harpoon seeker range/gimbal/activation/scan
limits. The route prior retains the existing 4,000 m profile value.

Commit C will document its profile fields before its behavior test. Values reused
from the existing game HOJ abstraction remain \`SIM_TUNED\`; capability provenance
is independently \`ASSUMED_THREAT\`.
