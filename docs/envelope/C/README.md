# ENV_C 재현

RANGE_A의 가상 게임 엔진만 측정한다. 실제 장비 성능 자료나 비교값은 사용하지 않는다.

1. `stage0/`의 native-engine/private/inputs는 ENV_B와 byte-identical이다. 진단 상한만500km로 늘리고 SM-2ER/SM-6, 정지, 고도1/10/20km의6조합을 두 번 실행한다. 사거리 숫자를 바꾸기 전 완료·검증한 결과다.
2. `docs/missile/range/A/build.py`는 검증된 stage0 영수증을 요구한다. 최신 ALL4_TERM SHA를 검사한 뒤8개 설계 사거리 숫자만 바꾼다. MR/ESSM, 추진/항력/시커/신관/배터리/종료기/유도 함수는 보존한다.
3. 현재 HTML의 native 함수 closure를 `extract.cjs`로 복사하고, `generate.py`로 진단 전용 독립 capsule을 만든다. 실제 게임에서 `__ENV_C__.capture()`한 detached 입력을 사용한다.
4. `node docs/envelope/C/run.cjs OUT.json --stage1`: 정렬 후 같은6조합. `--stage1`을 빼면4종×6고도×4운동=96조합과120궤적이다. 각각 독립적으로 두 번 실행한다.
5. 최초 coarse bracket→1km 이분 탐색 뒤 더 먼 모든 정수 km를 역순 검사한다. 비연속 명중 구간을 누락하지 않는다. 표 안쪽 모든 사거리에 명중한다는 보장은 아니다.
6. `node docs/envelope/C/investigate.cjs OUT.json [--baseline]`: 저고도 이탈3건+횡단18건. 네이티브 함수에 쓰지 않고 기존 필드만 읽어60Hz 로그를 수집한다. 기본 ENV 궤적 샘플은10Hz다.

`interceptPointKm`는 각 최대 최초거리 성공 사격의 실제 근접신관/파괴 시점 미사일 수평 위치와 발사점 사이 거리다. 성공이 아니면 null이며 종료 위치는 별도 `terminationPointKm`다. 표적 최초 거리와 같은 값으로 가정하지 않는다. 보고한 두 표는 같은 성공 사격을 서로 다른 거리 정의로 표현한다.

프로파일 수치와 모든 방정식은 현재 게임의 SIM_TUNED 설정이다. `GAME_ENGINE_COMPUTED` provenance와 프로파일/함수/진단 경계 해시를 표에 기록한다. 결과표는 지도·교전 권한·AI에 입력하지 않는다. 진단은 명시적인 API 호출 또는 오프라인 실행에서만 작동한다. 원본 ENV_A/B는 변경하지 않는다.

## 실행 명령

기록 환경은 Node24.19/Python3.12/Chromium151, Linux x86_64다. 저장소 루트에서 실행한다. 런타임 간 작은 부동소수 차이를 두 독립 실행의 bit 동일성과 혼동하지 않는다.

```bash
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
python -m pip install -r docs/helicopter/F/requirements.txt matplotlib
python -m playwright install chromium
export NODE_PATH="$PWD/docs/performance/F/node_modules"
```

관리 환경 밖에서 시스템 chromium이 없으면 `AEGIS_CHROMIUM_EXECUTABLE`에 Playwright가 설치한 chromium 실행 경로를 지정한다. 브라우저 스크립트는 별도 물리 근사 모델로 교체하지 않는다.

```bash
node docs/envelope/C/stage0/run.cjs /tmp/range-stage0-1.json
node docs/envelope/C/stage0/run.cjs /tmp/range-stage0-2.json
python docs/envelope/C/verify_stage.py /tmp/range-stage0-1.json /tmp/range-stage0-2.json docs/envelope/C/stage0
python docs/missile/range/A/build.py
node docs/envelope/C/extract.cjs /tmp/range-a/live.js
python docs/envelope/C/generate.py
python docs/missile/range/A/build.py
python docs/envelope/C/capture.py Aegis_SIM_v48_WIP_RANGE_A.html
node docs/envelope/C/run.cjs /tmp/range-stage1-1.json --stage1
node docs/envelope/C/run.cjs /tmp/range-stage1-2.json --stage1
python docs/envelope/C/verify_stage.py /tmp/range-stage1-1.json /tmp/range-stage1-2.json docs/envelope/C/stage1
node docs/envelope/C/run.cjs /tmp/range-env-c-1.json
node docs/envelope/C/run.cjs /tmp/range-env-c-2.json
python docs/missile/range/A/postprocess.py /tmp/range-env-c-1.json /tmp/range-env-c-2.json
```

`postprocess.py`는 R2 결과 대조를 통과한 뒤에만 표·그래프 생성, 최종 표 내장, 네이티브 코드/후보→최종 차이 검사, 실제 게임/사본 궤적, 브라우저 경계, 상태 해시·보고서 갱신을 순서대로 실행한다. Git 업로드는 하지 않는다. 원래 브라우저·도메인 검수 영수증은 실제 검사한 후보 SHA를 유지하고, 최종 변경이 표 데이터뿐임을 별도 확인한다.

저고도 조사와 설계 거리 자체 사격은 다음 명령으로 재현한다. 이 명령은 게임 물리 코드를 수정하지 않는다.

```bash
node docs/envelope/C/investigate.cjs /tmp/range-low-baseline.json --baseline
node docs/envelope/C/investigate.cjs /tmp/range-low-aligned.json
python docs/envelope/C/report_low.py /tmp/range-low-baseline.json /tmp/range-low-aligned.json docs/envelope/C/results
node docs/envelope/C/measure_goals.cjs /tmp/range-goal-shots.json
```
