# SEEKER_UNIFY_U4 package manifest

## Product authority

- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- Bytes: `22,195,923`
- SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- Baseline: `Aegis_SIM_v48_WIP_ESM_A.html`
- Baseline SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- Build: `through=C`, `mode=ACTIVE`
- Packed-main SHA-256: `e06c2e6133b66fe8be2f6c1305b39473a7776176680390a45673e7487e9a462e`

## Packages

### Executable package

`Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4_HTML.zip` contains exactly one file:

- `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`

### Report package

`Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4_REPORT.zip` contains:

- U4 baseline audit, A/B/C reports and gate receipts;
- frozen-build and final broad-regression raw/review records;
- the complete `docs/missile/seeker-unify/U4/evidence/` tree;
- reproducible build and limited-gate source modules/scripts;
- root status/handoff and archive decision/status/roadmap/backlog documents;
- `AEGIS_CURRENT_PRODUCT.json`, candidate workflow and core checksum list.

The report package contains zero `.html` files. Python bytecode caches and
`node_modules` are excluded. Package ZIP byte counts and SHA-256 values are
detached in `PACKAGE_CHECKSUMS_v48_WIP_SEEKER_UNIFY_U4.txt`, which is generated
after both immutable ZIP files and therefore is intentionally not embedded in
either package.

## Validation boundary

- The MAX_THREAT broad regression was executed exactly once on the product
  SHA above and is not run by packaging or candidate Actions.
- `FINAL_REGRESSION.json` preserves the four raw scene assertion failures.
  `FINAL_REGRESSION_REVIEW.json` classifies them from retained evidence without
  changing product code, expected values or tolerances and without a rerun.
- The candidate workflow performs exact rebuild, manifest/static/packed-main
  checks and the limited C SHADOW/ACTIVE Chromium gate only.
- `release=false`; merge, release and tag remain user decisions.
