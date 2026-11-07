# EMITTER_A package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMITTER_A.html` | 22,146,163 | `04bfb9c991929bed5800e7899f2ffb79087bfd20b79300c9bb01628b7edc98c6` | Executable product |
| `Aegis_SIM_v48_WIP_EMITTER_A_HTML.zip` | 16,465,554 | `31ccaf3470462fc275a8ae7be63f55c8eaa9402f3a3e85d6ec3b771c02c8ac91` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMITTER_A_REPORT.zip` | 37,213,051 | `ebc776448121fcd050ba4eb044b1d9ccc02c6b05b253c2bf6b234065f51f2189` | Reports, raw/normalized evidence, screenshots, diffs and reproduction tools; no executable product HTML |

Both ZIP archives passed `unzip -t`. The WebGL harness's two permissive raw
files containing JavaScript `-Infinity` sentinels are preserved verbatim as
`.raw.txt`; strict-JSON report copies use `null` with a normalization receipt.

Remote readback and PR metadata are recorded separately after publication so
that these immutable archive hashes do not recursively change.
