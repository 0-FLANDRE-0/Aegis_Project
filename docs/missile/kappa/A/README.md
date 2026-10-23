# KAPPA_PIP_LOS_A 재현

기준 `range-loft-recovery-a` / `5af4726113994b4e38bbfe5da8283424f04856fe`, 별도 시험 브랜치 `kappa-pip-los-a`. [원본 지시서](kit/AEGIS_KAPPA_PIP_LOS_Codex_Instructions.md), [게임 변경 diff](game-change.diff), [실제 관측 로그 추가 diff](diagnostic-telemetry.diff)를 확인한다.

정해진14조건만 CURRENT/PATCHED로 각각2회 실행한다. 실제 월드/진단 동등성도 같은14조건만 사용한다. 새 사거리 탐색, 비기본 정책, 다른 계수 최적화는 하지 않는다. 실패는 그대로 기록하고 조건을 제외하거나 추진/제어/해면 보호를 자동 조정하지 않는다.

```bash
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
python -m pip install playwright matplotlib
python -m playwright install chromium
export NODE_PATH="$PWD/docs/performance/F/node_modules"
export MPLCONFIGDIR=/tmp/aegis-kappa-mpl
mkdir -p /tmp/aegis-kappa
python docs/missile/kappa/A/bootstrap.py
node docs/missile/kappa/A/verify_static.cjs
node docs/missile/kappa/A/run.cjs /tmp/aegis-kappa/run-1.json
node docs/missile/kappa/A/run.cjs /tmp/aegis-kappa/run-2.json
python docs/missile/kappa/A/verify_browser.py
python docs/missile/kappa/A/verify_results.py
python docs/missile/kappa/A/report.py
```

시스템 Chromium이 없으면 `AEGIS_CHROMIUM_EXECUTABLE`에 Playwright가 설치한 실행 경로를 지정한다. 원래 headless Canvas2D 보정과 원래 출항·일시정지 경로를 사용한다. 브라우저 native 비교는 이상 지속 정보/발사 경계만 버리는 페이지에 연결한다. 자연 센서·기동 AI 종합시험으로 부르지 않는다.

기록 환경은 Node24.19.0/Python3.12.14/Chromium151.0.7922.173, CPU quota4core다. RNG1831565813, dt1/60초이며 wall time은 별도 영수증에 둔다. 두 반복의 원시 JSON이 같은지 검사한다. gzip 포장 시각과 Node/Chromium의 부동소수 차이를 원시 반복 결정성과 혼동하지 않는다.

`bootstrap.py`는 원본 압축 실행 코드를 읽고 제공 patch 도구로 정확히2블록을 바꾼다. 그 소스에서 `diagnostic/extract.cjs`가 함수 closure를 새로 복사한다. 기존 복사본에 단1회 patch한 결과와도 일치해야 한다. 재생성한 native 함수 해시·진단 source·gzip 인덱스 integrity를 내장한다. 중복 patch는 거부된다.

`diagnostic/private.js`의 추가 필드는 read-only 로그다. 실제 물리·신관·유도 함수는 새로 추출한 원문 그대로다. `kappaFresh`로 현재 틱에서 새로 계산된 벡터와 남아 있는 debug 값을 구분한다. 모든60Hz 로그는 원시 JSON/명령 CSV에 있고10Hz 궤적은 실제 월드/사본 비교에 사용한다.

`window.__ENV_KAPPA_A__.status()`는 nativeCapsuleSynchronized=true, envelopeMeasured=false와 과거 자료 목록을 반환한다. 기존 `__ENV_C__`는 이 새 캡슐의 호환 별칭이다. 새 사거리표는 rows0/profileHashnull이며 ‘재계산 필요’다. 기존 ENV_C 및 RECOVERY_A 결과를 새 유도 측정값으로 옮기지 않는다. 96조합 전체 실행 API는 자동 호출하지 않는다.

재현은 저장소 checkout에서 한다. 이전 HTML은 `archive/v48/WIP_RANGE_RECOVERY_A/`에 보존한다. 실행 HTML은 리포트 ZIP과 별도이며, 리포트의 원시 JSON/CSV는 `.gz`로 유지한다. summary CSV와 PNG/SVG는 바로 읽을 수 있다. 전체420+UI88/자연센서 종합/96조합 사거리 검사는 이번에 재실행하지 않았다.
