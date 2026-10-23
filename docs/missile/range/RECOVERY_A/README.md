# RANGE_RECOVERY_A 재현

기준은 RANGE_A `d42284ae4666914c604f77adbde25045a915e93f`이며 결과는 별도 `range-loft-recovery-a` 시험 브랜치에 둔다. 원본 분석은 [INPUT_ANALYSIS.md](INPUT_ANALYSIS.md)다. 정지 6조건에 접근300m/s/이탈150m/s를 추가했고, 장거리 이탈의 모두 실패를 확인한 뒤 같은 기종/고도의60km 이탈 확인6조건을 추가했다. 전체96조합 스윕은 실행하지 않는다.

실행 HTML은 리포트 ZIP과 별도로 받는다. 원시 JSON은 gzip으로 수록하며 요약 CSV/그래프는 바로 읽을 수 있다. 재현은 저장소 checkout에서 수행한다. 이전 ALL4_TERM/RANGE_A HTML은 각각 `archive/v48/WIP_ALL4_TERM/`, `archive/v48/WIP_RANGE_A/`에 있다. 결과에는 실제 시험한 HTML SHA를 기록한다.

```bash
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
python -m pip install playwright matplotlib
python -m playwright install chromium
export NODE_PATH="$PWD/docs/performance/F/node_modules"
export MPLCONFIGDIR=/tmp/aegis-recovery-mpl
mkdir -p /tmp/aegis-recovery
python docs/missile/range/RECOVERY_A/prepare.py
node docs/missile/range/RECOVERY_A/verify_static.cjs
node docs/missile/range/RECOVERY_A/run.cjs /tmp/aegis-recovery/run-1.json
node docs/missile/range/RECOVERY_A/run.cjs /tmp/aegis-recovery/run-2.json
node docs/missile/range/RECOVERY_A/run.cjs /tmp/aegis-recovery/control-1.json --controls
node docs/missile/range/RECOVERY_A/run.cjs /tmp/aegis-recovery/control-2.json --controls
python docs/missile/range/RECOVERY_A/verify_browser.py
python docs/missile/range/RECOVERY_A/verify_results.py
python docs/missile/range/RECOVERY_A/report.py
```

브라우저가 시스템 Chromium을 찾지 못하면 `AEGIS_CHROMIUM_EXECUTABLE`에 Playwright의 설치 경로를 지정한다. 기존 `docs/pip/B/browser_backend.py`의 headless Canvas2D 보정과 원래 출항·일시정지 경로를 쓴다. 센서/비행 코드를 다른 근사 모델로 대체하지 않는다.

`run.cjs`는 ENV_C의 네이티브 소스와 기존 private 경계/1/60초 적분을 그대로 사용한다. 각 사격의 RNG는1831565813으로 재설정된다. `reduce.cjs`는 결과만 읽으며 첫 shelf(10Hz 최초 유효 샘플), 첫 하강, 단계 전환, 마지막10초60Hz 로그를 추출한다. 시뮬레이션에 쓰지 않는다. 원시 결과에 실행 시각을 넣지 않고 wall time은 별도 영수증에 둔다.

브라우저 검증은 원래 게임 페이지에서 캡처한 프로파일/설정이 offline 입력과 같은지 먼저 검사한다. 같은 네이티브 함수를 독립 scope에서 실행한 결과와 실제 월드의 미사일 배열에 넣어 실행한 결과를 비교한다. 이상 지속 관측과 고정 발사 경계는 버리는 시험 페이지에만 연결한다. 이 검증은 자연 레이더/기동 AI 종합 인증이 아니다.

검증 무결성 PASS와 복구 후보의 성공 판정은 분리한다. 잔여 기존 성공→실패가 있으면 `baselineSuccessesFullyPreserved=false`로 기록한다. fullLoft 복원 외 추가 수치를 변경하지 않으며, 계산표가 여전히 유효한 것처럼 해시를 덮어쓰지 않는다.

기록 환경: Node24 / Python3.12 / Chromium151, CPU quota4core. 기존 headless2D backend를 썼다. 전체420+UI88 회귀, 전체96최대거리 재측정, 자연센서 종합 시험은 재실행하지 않았다. 게임과 동일한 가상 모델의 SIM_TUNED 시험이며 실물 성능 자료/비교는 사용하지 않는다.
