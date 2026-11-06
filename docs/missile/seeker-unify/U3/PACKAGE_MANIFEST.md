# SEEKER_UNIFY_U3 delivery manifest

## Executable package

`Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3_HTML.zip` contains exactly one file:

- `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html`

## Report package

`Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3_REPORT.zip` intentionally excludes the
executable HTML. It contains:

- `docs/missile/seeker-unify/U3/`: A–D gate reports and JSON, the B correction
  launch/stale/scope/Actions gates, both preserved pre-correction evidence and
  the single correction broad-regression evidence, Commit C/D paired
  attribution evidence, diffs and deterministic reproduction tools;
- root handoff files: `AEGIS_PLAN_STATUS_v48_WIP_SEEKER_UNIFY_U3.md`,
  `README.md`, and `AEGIS_PROJECT_INSTRUCTIONS.md`;
- current archive decisions/status/backlog/roadmap;
- `SHA256SUMS_v48_WIP_SEEKER_UNIFY_U3.txt`.

The detached `PACKAGE_CHECKSUMS_v48_WIP_SEEKER_UNIFY_U3.txt` is not embedded
in the report ZIP because it includes the completed report ZIP's own hash.

## Publication rule

All three downloadable artifacts are verified after push by full-byte remote
readback. The publication receipt records remote size and SHA-256. A pull
request may be created, but U3 does not merge, tag, or publish a release.
