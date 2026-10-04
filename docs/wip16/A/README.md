# WIP16A reproducible support

The user-uploaded HTML is frozen: `Aegis_SIM_v48_WIP16A.html`, SHA-256 `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`.

- `build_wip16a.py` + `edits.json`: reconstruction from byte-identical stable v48; portable gzip header, UTF-8 byte output.
- `tests/package16a.py`: original 64 package acceptance checks.
- `tests/verify_package.py`: candidate/baseline hashes, all executable scripts and exact rebuild, in addition to the original checks.
- `tests/runtime16a.py`: original 13 runtime acceptance checks with fresh contexts for benchmark, spotting and legacy regressions. Uses the Playwright-installed Chromium unless `AEGIS_CHROMIUM_EXECUTABLE` is set.
- `ORIGINAL_WIP16A_REPORT.md` and `ORIGINAL_WIP16A_VALIDATION_SUMMARY.json`: unchanged historical support records, not new CI results.
- `evidence/original_support_manifest.json`: hashes/CRC provenance of the original ZIP and every included file.
- `evidence/closeout_package_local.json`: direct local package/rebuild verification.
- `evidence/closeout_chromium_summary.json`: directly inspected Chromium artifact summary, 13/13 PASS.
- `evidence/closeout_actions_summary.json`: all 4 candidate jobs and all 30 general-smoke jobs.
- `evidence/legacy_3d_failure_summary.json`: retained failed candidate 3D evidence.
- `evidence/renderer_preservation.json`: renderer-and-later source identical to stable v48; not a new baseline browser run.
- `CLOSEOUT.md`: exact tested heads, PR, Actions and the integration hold.

The original report's six-case aggregate came after diagnostic audits on one page. The original archive also contains a fresh-page aggregate with different counts. The current runtime harness selects fresh contexts as the canonical method; old numeric aggregates are historical evidence. It keeps the existing acceptance thresholds unchanged.

Run from the repository root:

```sh
python docs/wip16/A/tests/verify_package.py Aegis_SIM_v48_WIP16A.html Aegis_SIM_v48.html
python -m pip install playwright==1.55.0
python -m playwright install chromium
python docs/wip16/A/tests/runtime16a.py Aegis_SIM_v48_WIP16A.html
```

The support intentionally does not duplicate the large baseline or candidate HTML.
