# SEEKER_UNIFY_C recovery checkpoint

Saved after the managed executor lost the linked-worktree Git metadata that had
been stored under `/dev/shm`. The product and evidence files remained intact in
`/workspace`; the original local commit objects did not. This recovery commit
preserves the surviving content without claiming completion of Stage 2 or CUE_A.

## Product

- File: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`
- SHA-256: `dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec`
- Implemented content: U2 ACTIVE equivalence work and the audited ASM two-way
  beam/LOS convention.
- CUE_A product implementation has not started.

## Completed evidence

- U2 ACTIVE: 1,200 exact-equivalence cases and 78 representative cases.
- Stage-2 primary matrix: 1,590 cases, zero page errors.
- Stage-2 S1 matrix: 100 cases, zero page errors.
- Stage-2 determinism run: saved and parseable.
- Numeric explanation runner: 22 cases completed. The Kh-32 cue rows contain
  valid beam/LOS measurements. Six stationary-DDG range rows were not captured
  by the first diagnostic selector; the selector source is repaired but those
  six rows must be rerun before the Stage-2 gate can close.

## Resume points

- Full cue matrix: 100 / 240 rows saved in
  `BEAM_STAGE2_CUE_MATRIX.progress.json`.
- Sixty-battle validation: seven valid rows saved in shard 0. Shard 1 contains
  one renderer-crash record and must be rerun; it is not a product result.
- Thirty-seven egress cases: the interrupted renderer run must be rerun.
- RCS direct audit and the final Stage-2 report remain pending.
- Broad regression has not been run, as required by the directive (run once
  only after the final stage or at a gated stop).

## Recovery rules

- Resume browser work with one Chromium worker at a time.
- Do not start CUE_A implementation until the Stage-2 gate is closed.
- Do not treat renderer-crash rows as product failures.
- Do not merge this branch into `main`; the user performs the merge after PR
  review.
