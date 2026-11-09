# HP_A Commit C — consumer, save, UI and report closure

Status: `IMPLEMENTED / TESTED`; release remains `NO`.

## Frozen candidate

- Product: `Aegis_SIM_v48_WIP_HP_A.html`
- Bytes: `22,200,135`
- SHA-256: `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- Packed main SHA-256: `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`

## Closure

- Player and NPC save restore recompute display outcome from physical authority;
  saved HP is mismatch-audited compatibility data only.
- Player save carries the existing survival snapshot and validates its schema;
  legacy saves migrate without inventing a survival state.
- HP-based bottom-bar survival and direct cookoff loss authority are removed.
- HUD/damage banner, AAR and diagnostics present mission/survival separately.
- mission-kill, irreversible-loss and sunk transitions are deduplicated.

## Limited evidence

- Candidate authority audit: 30 textual HP occurrences, invalid authority use 0
- Forbidden authority patterns: 0
- Required common contract paths: all present
- Protected physical function hashes: exact to U4
- C product-path contract gate: 19/19 PASS, page/console errors 0
- Actual SOV casualty/save suite: PASS; four contacts preserved and physical
  progression reaches LOST

The broad-run raw result and its non-mutating reconciliation are reported in
`FINAL_REPORT.md`, `FINAL_REGRESSION.json`, and
`FINAL_REGRESSION_RECONCILIATION.json`.
