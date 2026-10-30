# PERF_B 재현과 업로드

baseline은 archive의 exact PERF_A다. Python3.12/Playwright1.62.0과 Chromium, Node24/acorn8.19.0/eslint-scope9.1.2를 사용했다.

```bash
npm ci --prefix docs/performance/B --ignore-scripts --no-audit --no-fund
pip install -r docs/bunkerhill/K/requirements.txt
export AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium
export PYTHONDONTWRITEBYTECODE=1
python docs/performance/B/build.py archive/v48/WIP_PERF_A/Aegis_SIM_v48_WIP_PERF_A.html /tmp/perf-b.html
python docs/performance/B/verify_static.py archive/v48/WIP_PERF_A/Aegis_SIM_v48_WIP_PERF_A.html Aegis_SIM_v48_WIP_PERF_B.html /tmp/perf-b-tests/static
python docs/performance/B/run_all.py Aegis_SIM_v48_WIP_PERF_B.html /tmp/perf-b-tests --baseline archive/v48/WIP_PERF_A/Aegis_SIM_v48_WIP_PERF_A.html
python docs/performance/B/benchmark.py archive/v48/WIP_PERF_A/Aegis_SIM_v48_WIP_PERF_A.html Aegis_SIM_v48_WIP_PERF_B.html /tmp/perf-b-benchmark
sha256sum -c SHA256SUMS_v48_WIP_PERF_B.txt
sha256sum -c docs/performance/B/REPOSITORY_SUPPORT.sha256
```

benchmark는 다른 검사와 동시에 실행하지 않는다. profiler samples는 별도 작업이다. `.github/workflows/performance-b.yml`은 manual only이며 dispatch하지 않았다. 로컬 원본 검사에 Actions 결과를 합산하지 않는다.

`performance-b`를 새 branch로 push한 뒤 `verify_remote.py COMMIT OUTPUT`으로 remote head/tree와 변경한 모든 full raw bytes·SHA-256·Git blob, 이전4개 archive 및 stablev48을 독립 확인한다. contents raw transport 실패 시 GitHub git/blob API의 base64를 독립 읽는다. 증거 자체를 support 체크섬에서 제외하며 `evidence/remote-publication.json`은 code/support commit을 pin한다. proof-only commit 뒤 final-head readback도 별도 scratch에 수행한다. main/이전 PR 병합과 새 PR 생성은 실행하지 않는다.
