# PERF_F 재현

루트 HTML 전체 bytes를 사용한다. decoded main override를 사용하지 않는다. Python/Node/Chromium 의존성은 DEPENDENCIES.md와 package-lock.json을 따른다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
sha256sum -c SHA256SUMS_v48_WIP_PERF_F.txt
sha256sum -c docs/performance/F/REPOSITORY_SUPPORT.sha256
python docs/performance/F/verify_static.py archive/v48/WIP_PERF_E/Aegis_SIM_v48_WIP_PERF_E.html Aegis_SIM_v48_WIP_PERF_F.html artifacts/F/static
python docs/performance/F/run_all.py Aegis_SIM_v48_WIP_PERF_F.html artifacts/F --baseline archive/v48/WIP_PERF_E/Aegis_SIM_v48_WIP_PERF_E.html --workers 2 --exclude camera
python docs/performance/F/run_suite.py camera Aegis_SIM_v48_WIP_PERF_F.html artifacts/F/camera --baseline archive/v48/WIP_PERF_E/Aegis_SIM_v48_WIP_PERF_E.html
```

모든 위 작업 종료 후 성능 측정만 직렬로 실행한다.

```sh
python docs/performance/F/benchmark_queue.py archive/v48/WIP_PERF_E/Aegis_SIM_v48_WIP_PERF_E.html Aegis_SIM_v48_WIP_PERF_F.html artifacts/F-native-queue
```

manual workflow_dispatch만 보존한다. 현재 Actions 불가 상황에서는 로컬 최종 원본 증거가 gate이며 CI PASS로 표현하지 않는다. normal push 후 verify_remote.py로 branch head/tree/raw bytes/size/SHA/blob 및 E 네 파일·stable 보존을 독립 확인한다. 증거 commit 이후 최종 head를 다시 확인한다.
