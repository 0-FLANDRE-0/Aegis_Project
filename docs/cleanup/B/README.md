# CLEAN_B

기준은 `clean-a@60a83ccfbde89ec26d927b2993f0a4a9585c98af`의 CLEAN_A HTML이다.
별도 `clean-b` 브랜치에서 작업하며 main/기준 브랜치 병합 및 release/tag를 만들지 않는다.

먼저 REPORT.md, ACCEPTANCE.json, STATUS.json을 읽는다. 게임 비행·센서·교전 코드는 그대로다.
내장 ENV_D 데이터/accessor 블록만 교체한다. 모든 성능 수치는 게임 SIM_TUNED 산출값이다.

CG 3건은 사용자가 승인한 결과 중심 기준으로 (a) 처리한다. 자원 소비 차이와 과거 판정은
그대로 기록하며, 승인한 exact 기대값과 게임 코어 해시를 함께 검사한다. DDG의 기존3건도 보존한다.
전체420건 재실행은 `run_domain.py`로 하며 B의 승인 manifest를 명시적으로 적용한다.

사격은 사전 PLAN.md/PLAN.json의 부족 격자와 선택 구간 최소거리 보강만 실행한다.
기존 D2 logical SHA-256, CLEAN_A의 Git blob, 결과5발 SHA-256/조건/시드가 같은 기록을 재사용한다.
새 격자는 1~30km의1km 간격, 이후35km부터5km 간격이며 바깥 최대거리에서 제한한다.
선택 구간은 가장 먼 끝값을 가진 연속 통과 구간이다. 시작이30km를 넘으면 앞 실패점과의
간격을1km로 전부 보강하고, 중간 실패를 반영해 구간을 다시 나눈다.
다른 성공 구간은 otherRuns, 사이 실패는 deadZones, 앞뒤 실패는 boundaryFailures에 기록한다.

재현(저장소 루트, 기존 acorn/Playwright/Chromium 의존성 필요):

```sh
python docs/cleanup/B/prepare_baselines.py
node docs/cleanup/B/plan.cjs
node docs/cleanup/B/measure.cjs
python docs/cleanup/B/build.py
node docs/cleanup/B/audit.cjs
python docs/cleanup/B/verify_intervals.py
node docs/cleanup/B/verify_native.cjs
python docs/cleanup/B/run_domain.py
python docs/cleanup/B/run_ui.py
python docs/cleanup/B/verify_delivery.py
python docs/cleanup/B/report.py
python docs/cleanup/B/package.py
```

사전 Git blob receipt는 evidence/base-cache-blobs.json이다. 신규 clone에서 receipt를 검증할 때는
기준 commit의 `docs/cleanup/A/results/interval-cells` Git tree와 비교한다. 실제 환경에서는
NODE_PATH에 기존 acorn 경로를, TMPDIR=/dev/shm, PYTHONDONTWRITEBYTECODE=1을 사용했다.

공식 실행시간/새 사격 수는 최초 실행 증거다. 기존 cache를 둔 재실행은 새 사격을 하지 않으므로
freshCalls=0일 수 있다. 이를 최초 실행의 시간·비용 증거에 덮어쓰지 않는다. 새 full 재현이 필요하면
공식 results/evidence를 보존하고 다른 작업 트리에서 수행한다.

보고 ZIP에는 새 게임 HTML을 넣지 않으며 HTML ZIP을 별도로 제공한다. 보고 ZIP은 B 폴더와
승인 기준을 읽는 회귀 도구를 저장소 상대경로로 담는다. 이전 D2/CLEAN_A 원시 자료는
명시한 기준 commit의 저장소 파일을 사용한다.
