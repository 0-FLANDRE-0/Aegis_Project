# EMITTER_A package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMITTER_A.html` | 22,146,163 | `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be` | Executable product |
| `Aegis_SIM_v48_WIP_EMITTER_A_HTML.zip` | 16,465,529 | `ba0e58b0aa48331c4a70c481406efd8933eea9c3e5f706e20dc90e39c17102e8` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMITTER_A_REPORT.zip` | 37,250,226 | `e89965405ad68da794e572182d425e9d5520d92ba668425304b6dc28f50153cc` | Reports, raw/normalized evidence, screenshots, diffs and reproduction tools; no executable product HTML |

Both ZIP archives passed `unzip -t`; the executable ZIP contains exactly one
HTML whose extracted SHA is the product SHA, while the report ZIP contains
zero HTML files. The WebGL harness's two permissive raw
files containing JavaScript `-Infinity` sentinels are preserved verbatim as
`.raw.txt`; strict-JSON report copies use `null` with a normalization receipt.

Candidate Actions authority: `AEGIS_CURRENT_PRODUCT.json`; dedicated workflow
run [42373876872](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/42373876872)
PASS. The 364/364 + 42/42 + 213/213 + 29/29 broad result belongs to the
pre-closure product and was not rerun for packaging.

PR metadata: [PR #73](https://github.com/0-FLANDRE-0/Aegis_Project/pull/73),
OPEN and unmerged. Remote readback is recorded separately after publication so
that these immutable archive hashes do not recursively change.
