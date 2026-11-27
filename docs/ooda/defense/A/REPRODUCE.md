# DEFENSE_OODA_A reproduction guide

Run commands from the repository root. The broad MAX_THREAT regression has
already consumed its one authorized execution and must not be repeated.

## Exact product rebuild

```bash
python3 docs/ooda/defense/A/defense_ooda_patch.py \
  Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  /tmp/Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  --stage D --js-output /tmp/defense-ooda-a.js
cmp Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  /tmp/Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html
node --check /tmp/defense-ooda-a.js
```

Expected result: 22,226,343 bytes and SHA-256
`1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d`.

## Function and boundary audit

```bash
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_HP_A.html /tmp/hp-hashes.json
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html /tmp/integration-hashes.json \
  --require-new
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html /tmp/defense-hashes.json \
  --require-new
python3 docs/ooda/defense/A/d_hash_gate.py \
  /tmp/hp-hashes.json /tmp/integration-hashes.json /tmp/defense-hashes.json \
  /tmp/defense-hash-gate.json
python3 docs/ooda/integration-baseline/A/boundary_static_gate.py \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html /tmp/defense-boundary-gate.json
```

## Limited browser gates

Start a repository-root HTTP server and run the committed oracles. These are
limited contract gates, not the broad regression.

```bash
python3 -m http.server 8123 --bind 127.0.0.1

node docs/ooda/defense/A/contract_oracle.cjs \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  /tmp/defense-contract.json ACTIVE
node docs/ooda/defense/A/engine_oracle.cjs \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  /tmp/defense-engine.json ACTIVE
node docs/ooda/defense/A/active_oracle.cjs \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  /tmp/defense-active.json
```

For SHADOW, deterministically build stage C and run `shadow_oracle.cjs` against
that file. The final product remains stage D/ACTIVE.

## Broad evidence

`FINAL_REGRESSION.json` is authoritative. It combines the original completed
checkpoints and the no-rerun resume receipt. The raw paired failure and the
§9-4 classification are deliberately separate. Do not rerun
`run_final_regression.py` or `run_final_regression_resume.py` for publication.

## Packages

```bash
python3 docs/ooda/defense/A/package_artifacts.py
python3 docs/ooda/defense/A/package_contract_gate.py \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A_HTML.zip \
  Aegis_SIM_v48_WIP_DEFENSE_OODA_A_REPORT.zip \
  docs/ooda/defense/A/PACKAGE_MANIFEST.md \
  docs/ooda/defense/A/PACKAGE_CONTRACT_GATE.json
unzip -t Aegis_SIM_v48_WIP_DEFENSE_OODA_A_HTML.zip
unzip -t Aegis_SIM_v48_WIP_DEFENSE_OODA_A_REPORT.zip
```

The executable archive contains exactly one HTML. The report archive contains
no HTML and includes reports, tests, logs, screenshots, and reproduction tools.

