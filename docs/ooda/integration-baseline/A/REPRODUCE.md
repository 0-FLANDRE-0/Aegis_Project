# Reproduce

All commands run from the repository root.

```bash
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_HP_A.html \
  docs/ooda/integration-baseline/A/FUNCTION_HASHES.json
```

The extractor reads only `data-c55-index="13"`, decodes base64, then gunzips it. Function source is located with a lexical brace scanner. Hashes are SHA-256 of exact UTF-8 function source bytes; `normalization` is `NONE_EXACT_SOURCE_BYTES`.

Browser/Playwright versions and all later gate commands are recorded in `FINAL_REPORT.md`; unexecuted tests are never marked PASS.
