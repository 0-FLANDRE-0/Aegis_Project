# PERF_E 재현과 업로드

```sh
npm ci --prefix docs/performance/E --ignore-scripts --no-audit --no-fund
pip install -r docs/bunkerhill/K/requirements.txt
python -m playwright install --with-deps chromium
python docs/performance/E/build.py archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html candidate.html
python docs/performance/E/verify_static.py archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html Aegis_SIM_v48_WIP_PERF_E.html artifacts/static
python docs/performance/E/run_all.py Aegis_SIM_v48_WIP_PERF_E.html artifacts --baseline archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html --workers 2 --exclude camera
python docs/performance/E/run_suite.py camera Aegis_SIM_v48_WIP_PERF_E.html artifacts/camera
python docs/performance/E/benchmark_cumulative.py archive/v48/WIP_MULTI_SHIP_H4A/Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html Aegis_SIM_v48_WIP_PERF_E.html cumulative
python docs/performance/E/benchmark_damage.py archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html Aegis_SIM_v48_WIP_PERF_E.html native-latency
python docs/performance/E/benchmark_render.py archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html Aegis_SIM_v48_WIP_PERF_E.html native-render
sha256sum -c SHA256SUMS_v48_WIP_PERF_E.txt
sha256sum -c docs/performance/E/REPOSITORY_SUPPORT.sha256
```

Set AEGIS_CHROMIUM_EXECUTABLE to the installed Chromium path. Run camera alone after the other regression jobs. Run all three timing commands serially after every static/runtime/browser job ends; do not run other tests/profile work during performance capture. The manual-only workflow is prepared and not dispatched. Local final-original reports are the verification gate. Shape fixtures and a controlled light WebGL scene verify exact geometry/GPU bytes; they are separate from native RAF timing.

Normal push to performance-e is authorized. Preserve user commits and use expected-head checks; never force-push or merge main/prior branches. After normal push, verify_remote.py independently reads branch/tree and every changed path's raw/blob bytes, size, SHA256 and Git blob, removed previous roots and preserved stable/archive blobs. A proof-only commit may follow; read its full final head again outside the repo to avoid recursive evidence. No PR creation or Actions dispatch is included.
