# EMCON_B package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMCON_B.html` | 22,157,395 | `3343f5bbe7d6adac0694656ebafef538c3b7407d7ce642225fff94207c142c33` | Executable product |
| `Aegis_SIM_v48_WIP_EMCON_B_HTML.zip` | 16,472,667 | `a06d863ea6e9bfde9d243a0dc7c20cff71eccc9d121248f828824211ddb5e53f` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMCON_B_REPORT.zip` | 21,265,466 | `8927ac751d108adf45289a770d62ab670d0a2bb296ba9a912d394bbd50feb90d` | Reports, raw evidence, screenshots, diffs and reproduction tools; no executable HTML |

Both ZIP archives pass `unzip -t`. The executable ZIP contains exactly one HTML and its
extracted SHA equals the product SHA. The report ZIP contains zero HTML files.

The report archive intentionally preserves the raw broad-run failures and the separate
evidence-based classification; it does not rewrite incomplete inherited runner/harness rows as
PASS. The immutable package hashes are generated before remote publication. Commit-pinned
readback is recorded separately in `REMOTE_PUBLICATION.json`.

Candidate authority is `AEGIS_CURRENT_PRODUCT.json`. The local workflow-equivalent static and
Chromium gates pass; the remote run URL and conclusion are recorded in PR #74 without a
self-triggering documentation commit.

PR metadata: PR #74 is the intended new review PR. It remains unmerged; release/tag are absent.
