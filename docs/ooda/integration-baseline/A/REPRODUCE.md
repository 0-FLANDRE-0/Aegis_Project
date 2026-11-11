# Reproduce

All commands run from the repository root.

## Baseline hashes and browser oracle

```bash
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_HP_A.html \
  docs/ooda/integration-baseline/A/FUNCTION_HASHES.json

python3 -m http.server 8123
node docs/ooda/integration-baseline/A/baseline_oracle.cjs \
  Aegis_SIM_v48_WIP_HP_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_HP_A.html \
  docs/ooda/integration-baseline/A/BASELINE_ORACLE.json
```

The extractor reads only `data-c55-index="13"`, decodes base64, then gunzips it. It walks the complete parameter list before a lexical body-brace scan, so object defaults such as `opts={}` cannot truncate a function. Hashes are SHA-256 of exact UTF-8 source bytes; normalization is `NONE_EXACT_SOURCE_BYTES`.

Diagnostic wall-clock durations (`lastPlanMs`, `lastBuildMs`, `lastAssessmentMs`) are excluded from the oracle game-state digest. The committed normalized baseline digest is `c57bfc4ffa50adf3af6bb798dcb73d18758d32c5aec59d6469e1a80a6c9615bf`.

## Deterministic candidate build

```bash
python3 docs/ooda/integration-baseline/A/integration_baseline_patch.py \
  Aegis_SIM_v48_WIP_HP_A.html Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  --js-output /tmp/integration_baseline_candidate.js
node --check /tmp/integration_baseline_candidate.js
```

The builder count-checks every insertion/replacement and uses deterministic gzip (`mtime=0`).

## Candidate and contract oracles

```bash
node docs/ooda/integration-baseline/A/baseline_oracle.cjs \
  Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  docs/ooda/integration-baseline/A/CANDIDATE_ORACLE.json

node docs/ooda/integration-baseline/A/contract_oracle.cjs \
  Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  docs/ooda/integration-baseline/A/CONTRACT_ORACLE.json
```

Run the contract oracle a second time to prove the deterministic digest is bit-identical. These are stage tests, not the one-shot final broad regression.

## Candidate hashes

```bash
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html \
  docs/ooda/integration-baseline/A/FUNCTION_HASHES_CANDIDATE.json \
  --stage INTEGRATION_BASELINE_A_COMMIT_C
```

Browser/Playwright versions and final gates are recorded in `FINAL_REPORT.md`; unexecuted tests are never marked PASS.
