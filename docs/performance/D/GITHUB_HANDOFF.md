# PERF_D 재현과 업로드

```sh
npm ci --prefix docs/performance/D --ignore-scripts --no-audit --no-fund
pip install -r docs/bunkerhill/K/requirements.txt
python -m playwright install --with-deps chromium
python docs/performance/D/build.py archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html candidate.html
python docs/performance/D/verify_static.py archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html Aegis_SIM_v48_WIP_PERF_D.html artifacts/static
python docs/performance/D/run_all.py Aegis_SIM_v48_WIP_PERF_D.html artifacts --baseline archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html --workers 2 --exclude camera
python docs/performance/D/run_suite.py camera Aegis_SIM_v48_WIP_PERF_D.html artifacts/camera
python docs/performance/D/benchmark.py archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html Aegis_SIM_v48_WIP_PERF_D.html benchmark
python docs/performance/D/benchmark_damage.py archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html Aegis_SIM_v48_WIP_PERF_D.html native-latency
sha256sum -c SHA256SUMS_v48_WIP_PERF_D.txt
sha256sum -c docs/performance/D/REPOSITORY_SUPPORT.sha256
```

Set AEGIS_CHROMIUM_EXECUTABLE to the installed Chromium path. Run camera alone after other regression jobs, and both performance commands serially after all tests. The manual-only workflow is prepared but was not dispatched. Local final original reports are the verification gate.

Normal push to performance-d is authorized; never force-push or merge main/prior branches. After push, `verify_remote.py COMMIT output.json` independently checks branch/tree, all changed paths' raw/blob bytes, size, SHA256 and Git blob, removed old roots, and preserved archive/stable blobs. A proof-only commit may follow; final head gets another full independent readback outside the repo to avoid recursive proofs. Full original HTML upload was persistently authorized by the user. No PR creation is included.
