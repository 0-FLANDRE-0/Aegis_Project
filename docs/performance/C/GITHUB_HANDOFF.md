# PERF_C 재현과 업로드

baseline은 archive의 exact PERF_B다. 최신 결과·SHA는 verification-summary 및 root 체크섬이 기준이다.

```bash
npm ci --prefix docs/performance/C --ignore-scripts --no-audit --no-fund
pip install -r docs/bunkerhill/K/requirements.txt
export AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium
export PYTHONDONTWRITEBYTECODE=1
python docs/performance/C/build.py archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html /tmp/perf-c.html
python docs/performance/C/verify_static.py archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html Aegis_SIM_v48_WIP_PERF_C.html /tmp/perf-c-tests/static
python docs/performance/C/run_all.py Aegis_SIM_v48_WIP_PERF_C.html /tmp/perf-c-tests --baseline archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html --workers 2 --exclude camera
python docs/performance/C/run_suite.py camera Aegis_SIM_v48_WIP_PERF_C.html /tmp/perf-c-tests/camera --baseline archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html
python docs/performance/C/benchmark.py archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html Aegis_SIM_v48_WIP_PERF_C.html /tmp/perf-c-benchmark
sha256sum -c SHA256SUMS_v48_WIP_PERF_C.txt
sha256sum -c docs/performance/C/REPOSITORY_SUPPORT.sha256
```

기존 camera pointer/touch suite는 다른 회귀가 끝난 후 단독 실행한다. benchmark는 회귀/profile 작업 없이 직렬로 실행하고 각 조건의 두 pass에서 AB/BA 순서를 반대로 한다. CDP sample은 timing과 별도 작업이다. Actions는 manual only이며 계정 제한으로 dispatch하지 않는다.

`performance-c` 새 branch에 normal push한 뒤 `verify_remote.py COMMIT OUTPUT`으로 head/tree·모든 변경 raw bytes/size/SHA-256/Git blob과 직전 네 원본/stable을 독립 읽는다. raw transport가 실제로 실패한 파일만 GitHub blob base64로 fallback한다. proof-only commit 뒤 final-head도 별도 scratch에 확인한다. `evidence/remote-publication.json`은 code commit을 pin하고 자기 체크섬에서는 제외한다. main/선행 PR 병합·새 PR 생성은 이번 단계에 포함하지 않는다.
