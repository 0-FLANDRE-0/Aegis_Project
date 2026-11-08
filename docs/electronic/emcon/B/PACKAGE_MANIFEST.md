# EMCON_B package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMCON_B.html` | 22,162,415 | `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee` | Corrected executable product |
| `Aegis_SIM_v48_WIP_EMCON_B_HTML.zip` | 16,476,586 | `127d380d1affecf061601d678a5af2d512d08b2af299dae268535155a875b9de` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMCON_B_REPORT.zip` | 21,538,899 | `81dd7332df29329eedd8c36c7e4d9661fe08e521519a938004d309df9a800f3b` | Reports, both correction gates, inherited raw evidence, screenshots, diffs and reproduction tools; no executable HTML |

Both ZIP archives pass `unzip -t`. The executable ZIP contains exactly one HTML and its
extracted SHA equals the product SHA. The report ZIP contains zero HTML files.

The report archive intentionally preserves the pre-correction raw broad-run failures and the
separate evidence-based classification; it does not rewrite incomplete inherited runner/harness
rows as PASS or attribute that run to the correction SHA. The immutable package hashes are
generated before remote publication. The final commit-pinned full-byte readback and candidate
Actions receipt are recorded in PR #74 after the final push; `REMOTE_PUBLICATION.json` points to
that authority without causing a self-triggering receipt commit.

Candidate authority is `AEGIS_CURRENT_PRODUCT.json`. Both correction-specific static and Chromium
gates, D/E gates, release smoke, baseline exact comparison, and lock 14/14 pass locally; the
remote run URL and conclusion are recorded in PR #74 without a self-triggering documentation
commit.

PR metadata: corrections 2–3 update the existing PR #74. It remains unmerged; release/tag are absent.
