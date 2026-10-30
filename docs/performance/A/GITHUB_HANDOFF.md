# PERF_A 원본 및 검증 인계

사용자가 승인한 직접 원본 업로드·확인 범위로 `performance-a`에 HTML/status/SHA/README/지침/support/evidence/manual workflow를 반영한다. main과 H4A branch/선행 PR은 병합하지 않는다. PR 생성은 별도 사용자 승인 없이는 실행하지 않는다.

현재 환경에서 원본 직접 검사:

```sh
npm ci --prefix docs/performance/A --ignore-scripts --no-audit --no-fund
python docs/performance/A/verify_static.py archive/v48/WIP_MULTI_SHIP_H4A/Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html Aegis_SIM_v48_WIP_PERF_A.html artifacts/PERF_A/static
AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium python docs/performance/A/run_all.py Aegis_SIM_v48_WIP_PERF_A.html artifacts/PERF_A --baseline archive/v48/WIP_MULTI_SHIP_H4A/Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html
```

동시 검사 작업이 모두 끝난 뒤 성능 비교를 별도 직렬 실행:

```sh
AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium python docs/performance/A/benchmark.py archive/v48/WIP_MULTI_SHIP_H4A/Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html Aegis_SIM_v48_WIP_PERF_A.html artifacts/PERF_A/benchmark --repeats 2
```

검증은 위 파일의 원본 bytes를 사용한다. main override·호출 빈도 변경·대체 HTML을 사용하지 않는다. 구체적인 로컬 실행/브라우저/backend 조건은 최종 evidence에 기록한다. `.github/workflows/performance-a.yml`은 workflow_dispatch 전용이고 이번 작업에서 dispatch하지 않는다.

업로드 직전 main/H4A/new branch head를 읽고 새 사용자 commit이 있으면 보존한다. 정상 git push 뒤 `verify_remote.py`로 commit tree와 모든 변경 파일의 원격 raw/blob bytes·크기·SHA-256·Git blob을 다시 대조한다. H4A 네 원본과 stable v48 blob을 보존한다. readback 결과는 자기 자신을 해시하지 않도록 support checksum에서 제외하고 proof-only 후속 commit으로 추가한다. 그 후 최종 head를 다시 독립 대조한다.
