# Reproduce

All commands run from the repository root.

```bash
python3 docs/ooda/integration-baseline/A/baseline_audit.py \
  Aegis_SIM_v48_WIP_HP_A.html \
  docs/ooda/integration-baseline/A/FUNCTION_HASHES.json
```

The extractor reads only `data-c55-index="13"`, decodes base64, then gunzips it. Function source is located with a lexical brace scanner. Hashes are SHA-256 of exact UTF-8 function source bytes; `normalization` is `NONE_EXACT_SOURCE_BYTES`.

Serve the repository root and capture the deterministic browser oracle twice:

```bash
python3 -m http.server 8123
node docs/ooda/integration-baseline/A/baseline_oracle.cjs \
  Aegis_SIM_v48_WIP_HP_A.html \
  http://127.0.0.1:8123/Aegis_SIM_v48_WIP_HP_A.html \
  /tmp/BASELINE_ORACLE.json
```

Both runs must report the same `deterministicDigest`. The committed HP_A baseline is
`f4ff4317c17a5c43a33138bc5346d2a4d78a40673cbb80fc2941a0693136d682`.

Browser/Playwright versions and all later gate commands are recorded in `FINAL_REPORT.md`; unexecuted tests are never marked PASS.
