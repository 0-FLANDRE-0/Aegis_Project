# ESM_A package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_ESM_A.html` | 22,182,527 | `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7` | Corrected executable product |
| `Aegis_SIM_v48_WIP_ESM_A_HTML.zip` | 16,495,658 | `c06274e363a078436e45f1e468da92a2409d9d3320dc61346d89e904ee641ce1` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_ESM_A_REPORT.zip` | 76,355,647 | `7a22519a4e3d44cd4338d45d635df58b2a324ada4a952351b15b10a8f5695d22` | Reports, source modules, diffs, limited gates, corrected broad evidence, UI screenshots, and reproduction tools; zero HTML files |

Both ZIP archives pass `unzip -t`. The executable ZIP contains exactly one
entry and one HTML; its extracted HTML SHA equals the product SHA. The report
ZIP contains 397 entries and zero HTML files. Package manifest and root
checksum files are kept outside the report archive to avoid a self-referential
archive hash.

Candidate authority is `AEGIS_CURRENT_PRODUCT.json`, stage `ESM_A`. Remote
commit-pinned byte/SHA readback and the final Actions receipt are recorded in
the PR after publication without rebuilding these immutable packages.

Release is `false`. Merge, release, and tag remain the user decision.
