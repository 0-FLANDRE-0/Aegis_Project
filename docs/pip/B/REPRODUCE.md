# 재현 순서

보고서ZIP에는 실행HTML을 넣지 않는다. `DELIVERY_MANIFEST.json`은 ZIP 수록 파일의 압축 해제 bytes와SHA-256이며 `.gz` 원시 데이터는 읽기 쉬운JSON/CSV로 풀어 넣었다. 저장소용 `REPOSITORY_SUPPORT.sha256`는 저장소 checkout에서 검사하는 별도 파일이다.

## 독립 미사일 진단만 다시 계산

Node24에서 외부 패키지 없이 가능하다. 원본 게임 함수를 이미 복사한 `native-engine.js`, 고정 입력 `inputs.json`이 포함되어 있다.

```sh
node docs/envelope/A/run.cjs /tmp/env-a-results-1.json
node docs/envelope/A/run.cjs /tmp/env-a-results-2.json
python docs/envelope/A/verify_results.py /tmp/env-a-results-1.json /tmp/env-a-results-2.json /tmp/env-a-verify
pip install matplotlib
MPLCONFIGDIR=/tmp/env-mpl python docs/envelope/A/report.py /tmp/env-a-results-1.json /tmp/env-a-report
```

전체 계산은12005사격이며 이 환경에서 수십 분~1시간 이상 걸렸다. 실행 시 게임 월드와 연결하지 않는다.

## HTML 재빌드와 UI/경로 검사

전체 저장소의 `pip-b-env-a` 또는 발행 영수증의 검증 commit을 checkout한다. 기준HTML은 `archive/v48/WIP_PIP_A/`의 같은 bytes 파일이다. Python3.12/Playwright/Chromium, Node24/acorn/eslint-scope가 필요하다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
export NODE_PATH="$PWD/docs/performance/F/node_modules"
pip install -r docs/helicopter/F/requirements.txt matplotlib
python -m playwright install chromium
node docs/envelope/A/extract.cjs archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html
python docs/envelope/A/generate.py
python docs/pip/B/build.py archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html /tmp/PIP_B.html
cmp /tmp/PIP_B.html Aegis_SIM_v48_WIP_PIP_B.html
python docs/pip/B/verify_static.py archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-static
python docs/pip/B/verify_ui.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-ui
python docs/pip/B/verify_pip.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-input
python docs/pip/B/verify_render.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-render
python docs/envelope/A/verify_browser.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-native
python docs/envelope/A/verify_status.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-profile
python docs/pip/B/run_domain.py Aegis_SIM_v48_WIP_PIP_B.html /tmp/check-domain --parallel 2
```

나머지 MAP_A/기존 UI 검사는 `run_map.py`, 실제WebGL 검사는 `verify_visual.py`에 있다. `.github/workflows/pip-b-env-a.yml`은 수동 재현 경로를 제공하지만 이번 발행에서 Actions를 실행하지 않았다. 실제 단말 성능 측정이 필요하면 대규모 ENV_A 계산과 분리해 실행해야 한다.
