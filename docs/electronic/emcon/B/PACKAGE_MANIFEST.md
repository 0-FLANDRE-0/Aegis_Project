# EMCON_B package manifest

| File | Bytes | SHA-256 | Contents |
|---|---:|---|---|
| `Aegis_SIM_v48_WIP_EMCON_B.html` | 22,159,899 | `e08cc2aede89e6452786efbf97fbd8ef49480ab33f8f8da178cbee0bff87377f` | Corrected executable product |
| `Aegis_SIM_v48_WIP_EMCON_B_HTML.zip` | 16,477,384 | `4e8d25d3527f3d3c979bb5b996901351eb45210ff294958e4799b4b8224e5202` | Exactly one executable HTML |
| `Aegis_SIM_v48_WIP_EMCON_B_REPORT.zip` | 21,517,282 | `98326d5668f9f2e2f3dfabc8049a950ac64c78aea7f185973e5b5ec4d05897f2` | Reports, correction gates, inherited raw evidence, screenshots, diffs and reproduction tools; no executable HTML |

Both ZIP archives pass `unzip -t`. The executable ZIP contains exactly one HTML and its
extracted SHA equals the product SHA. The report ZIP contains zero HTML files.

The report archive intentionally preserves the pre-correction raw broad-run failures and the
separate evidence-based classification; it does not rewrite incomplete inherited runner/harness
rows as PASS or attribute that run to the correction SHA. The immutable package hashes are
generated before remote publication. The final commit-pinned full-byte readback and candidate
Actions receipt are recorded in PR #74 after the final push; `REMOTE_PUBLICATION.json` points to
that authority without causing a self-triggering receipt commit.

Candidate authority is `AEGIS_CURRENT_PRODUCT.json`. The correction-specific static and Chromium
gates, D/E gates, release smoke, baseline exact comparison, and lock 14/14 pass locally; the
remote run URL and conclusion are recorded in PR #74 without a self-triggering documentation
commit.

PR metadata: correction 2 updates the existing PR #74. It remains unmerged; release/tag are absent.
