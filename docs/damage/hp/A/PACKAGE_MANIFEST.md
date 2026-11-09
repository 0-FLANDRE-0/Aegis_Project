# HP_A package manifest

## Product authority

- Product: `Aegis_SIM_v48_WIP_HP_A.html`
- Bytes: `22,200,135`
- SHA-256: `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- Baseline: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- Baseline SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- Build: `phase=C`
- Packed-main bytes: `40,927,903`
- Packed-main SHA-256: `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`

## Packages

### Executable package

`Aegis_SIM_v48_WIP_HP_A_HTML.zip` contains exactly one file:

- `Aegis_SIM_v48_WIP_HP_A.html`

### Report package

`Aegis_SIM_v48_WIP_HP_A_REPORT.zip` contains no HTML. It contains:

- the Commit A/B/C reports, audit tables, raw evidence and gate receipts;
- the frozen-candidate broad-regression raw record and reconciliation;
- the reproducible product builder, bounded gates and analysis scripts;
- the root plan/status/handoff and archive decision/status/roadmap/backlog;
- `AEGIS_CURRENT_PRODUCT.json`, the candidate workflow and its validator.

Python bytecode caches, `node_modules`, unrelated worktree files and every
HTML file are excluded. `PACKAGE_CHECKSUMS_v48_WIP_HP_A.txt` is generated only
after both immutable ZIP files, so it is intentionally detached rather than
embedded in either archive.

## Validation boundary

- The MAX_THREAT broad regression was invoked exactly once on the frozen
  product SHA above; packaging and candidate Actions do not repeat it.
- Six raw paired `samePhysicalState` failures and the skipped U4 scene harness
  are preserved. Their classified analysis and isolated scene recovery do not
  modify expectations, tolerances, product code or the broad-run record.
- Candidate Actions performs an exact phase-C rebuild, fail-closed HP authority
  audit and the bounded 19-check browser contract gate only.
- `release=false`; merge, release and tag remain user decisions.

## Evidence map

- Commit A: `COMMIT_A_BASELINE.md`, `evidence/commit-a/`
- Commit B: `COMMIT_B_OUTCOME.md`, `evidence/commit-b/`
- Commit C: `COMMIT_C_CLOSURE.md`, `evidence/commit-c/`
- Broad raw: `FINAL_REGRESSION.json`, `evidence/final-regression/`
- Reconciliation: `FINAL_REGRESSION_RECONCILIATION.json`
- Final narrative: `FINAL_REPORT.md`, `AEGIS_PLAN_STATUS_v48_WIP_HP_A.md`
