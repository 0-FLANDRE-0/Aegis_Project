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

## Frozen-candidate final regression

The broad runner was invoked once:

```bash
python3 docs/ooda/integration-baseline/A/run_final_regression.py
```

`FINAL_REGRESSION_RAW.json` preserves that receipt. Nineteen suites had zero assertions because the sparse checkout did not contain `docs/multiship/G/browser_g.py` or `docs/missile/fuze-zem/A/browser_tools.py`. After restoring those tracked files, only those zero-execution suites received their first actual run:

```bash
python3 docs/ooda/integration-baseline/A/run_zero_execution_recovery.py

python3 docs/ooda/integration-baseline/A/reconcile_final_regression.py
```

Do not rerun the broad runner: the raw run count is one. The recovery command is only valid when every selected raw suite has `executedAssertions == 0` and the candidate SHA is exact.

## Current-candidate Actions gate

The dedicated stage rebuilds the candidate from HP_A, compares exact bytes, audits function hashes, then runs the candidate and command oracles against their pinned deterministic digests. It does not repeat the broad regression.

## Packages

```bash
python3 docs/ooda/integration-baseline/A/package_artifacts.py
unzip -t Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_HTML.zip
unzip -t Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_REPORT.zip
```

The HTML archive must contain exactly one `.html`. The report archive must contain none.
