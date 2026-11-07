# EMITTER_A package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMITTER_A.html` | 22,146,163 | `04bfb9c991929bed5800e7899f2ffb79087bfd20b79300c9bb01628b7edc98c6` | Executable product |
| `Aegis_SIM_v48_WIP_EMITTER_A_HTML.zip` | 16,465,554 | `31ccaf3470462fc275a8ae7be63f55c8eaa9402f3a3e85d6ec3b771c02c8ac91` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMITTER_A_REPORT.zip` | 37,212,629 | `8e0e427e3aad9c3ca1ccdb01adce9a3dd8e1122f3c7179a519af86c33827774a` | Reports, raw/normalized evidence, screenshots, diffs and reproduction tools; no executable product HTML |

Both ZIP archives passed `unzip -t`. The WebGL harness's two permissive raw
files containing JavaScript `-Infinity` sentinels are preserved verbatim as
`.raw.txt`; strict-JSON report copies use `null` with a normalization receipt.

PR metadata: [PR #73](https://github.com/0-FLANDRE-0/Aegis_Project/pull/73),
OPEN and unmerged. Remote readback is recorded separately after publication so
that these immutable archive hashes do not recursively change.
