# WIP16A closeout — 2026-10-03

## Verified payload

- base main: `d2b840bae95267ffc53bfda847442b2211c1ab03`
- user-upload WIP16 head: `3be1ba489a0f8b934b8d2000aec408b56ea863af`
- remote/local Git blob exact: `d0d8b3de795716cb21ba2f7ba9673b8024dc2ceb`
- candidate bytes: `7,354,882`
- candidate SHA-256: `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`
- stable v48 SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`

## Direct local verification

- supplied package checks: `64/64 PASS`
- additional integrity/all-script syntax/exact reconstruction checks: `21/21 PASS`
- executable scripts: `15` syntax PASS
- records 0–12 compressed bytes unchanged
- candidate HTML not rewritten; reconstruction exact after deterministic gzip-header fix
- Python `3.12.14`; local Chromium not installed, so no local browser pass claimed

## CI / PR — directly inspected

- PR: [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41), OPEN, not merged.
- tested WIP16 head: `4edae6dd627f57e9b67e7485ca386a70b67a368a`
- tested PR merge SHA: `b37f17a622cfa05fe9cd9024388e3765ce52bb9b`
- candidate Actions: [37090059200](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37090059200), **4/4 job PASS**.
- Python 3.11/3.12/3.13: uploaded SHA, original `64/64`, additional `21/21`, all executable scripts and byte-identical reconstruction PASS.
- uploaded candidate Chromium: **13/13 PASS**, core failures `[]`, page errors `[]`, `FRESH_BROWSER_CONTEXT_PER_PHASE`.
- runtime artifact `11261528254` was downloaded and CRC/JSON checked; ZIP SHA-256 `a24ec19d7641ad0a258c61c8fd2ab1bd399f4b1d38cc51442cecf38fe744fa7d`.
- general smoke: [37090059060](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37090059060), **29/30 job PASS**, `aegis-3d-render` FAIL.

All job outcomes are retained in `evidence/closeout_actions_summary.json`. The fresh runtime artifact summary is in `evidence/closeout_chromium_summary.json`; historical numeric aggregates are not mixed with it. No acceptance threshold was relaxed.

## 3D integration blocker

The general smoke workflow mainly runs historical payload checks but some jobs select a root HTML by filename. Artifact `11262312052` explicitly records `Aegis_SIM_v48_WIP16A.html` as the failed 3D job's source. It reached ready WebGL 2/SwiftShader; this is not a missing-WebGL failure.

The failed checks include entry/exit holes not attached/matched to the rendered hull and old BridgeMaster mesh/yardarm identifiers. Interior/crew presentation checks passed. The complete failed contract remains FAIL; it was not weakened or rerouted to an older simulator to turn it green.

`renderer_preservation.json` proves the candidate renderer-and-later source is byte-identical to stable v48. It is evidence that WIP16A did not edit this renderer code, **not** a fresh v48 WebGL baseline run. Existing imported C5 geometry/hole binding and legacy-model diagnostics need a separately scoped correction before full integration can be called complete. Exact failure summary: `evidence/legacy_3d_failure_summary.json`.

## Decision / remaining actions

**WIP16A scoped implementation/package/browser acceptance passed; full PR integration HOLD.** Main merge and v48.1 promotion have not been performed. Release/tag creation is outside this closeout request.

Final record-only changes do not alter HTML, executable support scripts or workflows. Preserve the exact tested code head above; do not claim a new simulator validation from a documentation-only commit.

Next entry point: reconcile C5 rendered-hull hole ownership and current model audit contracts, preserving the failed requirements. After integration, proceed with pre-departure ship selection/initialization, DDG-119 preservation, then Bunker Hill profile/model binding. Harpoon, Tomahawk and simultaneous friendly multi-ship simulation remain later scopes; numbers unassigned.
