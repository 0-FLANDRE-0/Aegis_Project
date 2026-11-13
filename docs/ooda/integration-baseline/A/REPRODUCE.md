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

## Corrected-candidate final regression

Attempt 1 is preserved under `evidence/final-correction/final-regression/`. It stopped at the first suite with zero assertions because the WIP_HELI_CG_A fixture was absent. Do not delete, rewrite or count that receipt as a pass.

Before the user-authorized attempt 2, sparse checkout included this exact tracked fixture:

```text
/archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html
```

The attempt-2 runner performs a mandatory preflight over the pinned product, baseline, fixture, 32 explicit inputs, all 21 suite input maps and every tracked `docs/`/`tests/` indirect fixture. Its dry-run must execute zero broad suites. The authorized run was:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -u docs/ooda/integration-baseline/A/run_final_regression.py
```

`FINAL_CORRECTION_REGRESSION_ATTEMPT_2.json` and `evidence/final-correction/final-regression-attempt-2/` preserve the only authorized second run. It passed 785/785. Do not rerun it; the final evidence count is attempt 1 stop plus one attempt-2 execution.

## Current-candidate Actions gate

The dedicated stage rebuilds the candidate from HP_A, compares exact bytes, audits function hashes, then runs the candidate and command oracles against their pinned deterministic digests. It does not repeat the broad regression.

## Packages

```bash
python3 docs/ooda/integration-baseline/A/package_artifacts.py
python3 docs/ooda/integration-baseline/A/package_contract_gate.py
unzip -t Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_HTML.zip
unzip -t Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_REPORT.zip
```

The HTML archive must contain exactly one `.html`. The report archive must contain none.
