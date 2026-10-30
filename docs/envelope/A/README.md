# ENV_A — 게임 엔진 비행 진단

실제 무기 자료를 입력하거나 비교하지 않는다. 결과는 이 빌드의 가상 게임 모델에서 계산한 `GAME_ENGINE_COMPUTED` 데이터다. 원본 프로파일의 기존 출처 주석은 보존했다.

## 실행 경계

`extract.cjs`가 PIP_A의 실제 자함 런타임에서 비행·유도·로프트·신관 함수 원문을 추출한다. `native-engine.js`는 자동 생성된 복사본이다. 별도 근사 비행 모델을 작성하지 않았다. 각 원문 SHA-256과 외부 의존성은 `dependencies.json`, 격리 경계와 그 이유는 `boundaries.json`에 기록한다.

`new Function`으로 만든 독립 어휘 공간은 자신의 미사일·표적 배열, 관측 파일, RNG, 틱을 갖는다. 게임 월드에 삽입하지 않는다. 실제 비행·로프트·유도·신관의 계산 본문은 수정하지 않고, 그 밖의 표시·장비 가용성·RF 측정 입력만 경계에서 대체한다. 원래 게임에서 사용하던 파괴 판정을 그대로 사용한다.

공통 입력은 다음과 같다.

- 발사 기준점 MSL 0m, 정지·무경사 플랫폼. 원래 수직 관내 발사·피치오버 함수를 사용한다.
- 오차 없는 DL/SARH/ARH 표적 상태를 지속 공급한다. 탐지·조사 자원·전송 장애·전자전은 계산하지 않는다.
- 기존 일반 항공기 점 표적의 직선 등속 운동과 기존 근접신관/항공기 파괴 거리 판정. 임의 요격 성공 거리 기준을 추가하지 않는다.
- 독립 RNG seed `1831565813`, 항법 seed `2047861954`, 신관 환경 계수 `1.0649859543133355`를 고정했다. 마지막 둘은 고정한 기준 fixture의 입력이며 실행 중 게임 날씨/시나리오를 읽지 않는다.
- 고정 적분 `1/60s`. 궤적 10Hz와 최종 종료 상태를 기록한다. 단계 시간 구간은 이 10Hz 관측의 분해능을 갖는다.

## 거리 탐색

1/5/15/30/60/100/150/200/250/300km에서 성공 구간을 찾고 정수 이분 탐색을 수행한다. 근거리 발사 사각과 비단조 성공 구간을 가정 없이 처리하기 위해 결과보다 먼 모든 정수 km도 검사한다. 가장 먼 성공과 바로 다음 실패를 보존한다. 300km 성공은 검사 상한에 도달한 것이며, 그 이상의 한계를 확정한 값이 아니다.

범위 내부에 실패 구간이 있을 수 있으므로 이 표는 모든 안쪽 거리를 명중권으로 표시하는 근거가 아니다. 이번에는 지도나 교전 판단에 연결하지 않았다.

## API

게임 시작 시 진단을 실행하지 않는다.

```js
await window.__ENV_A__.status();
window.__ENV_A__.table();
window.__ENV_A__.case({weapon:'SM2',rangeKm:30,altM:5000,targetSpeedMps:0});
await window.__ENV_A__.run({onProgress:console.log});
```

`run()`은 Worker 4개에서 계산하고 결과를 반환한다. `case()`는 명시 호출한 단일 격리 진단이며 동기 실행한다. 프로파일 해시가 바뀌면 `status()`가 재계산 필요를 표시한다. 실제 게임 함수가 복사 원문과 달라지면 전체 실행을 거부하고 캡슐 재생성을 요구한다.

## 재현

필요 항목: Node(acorn, eslint-scope), Python(Playwright, matplotlib), Chromium. 원본 PIP_A는 archive의 동일 바이트 파일이다.

```sh
NODE_PATH=<dependencies> node docs/envelope/A/extract.cjs archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html
python docs/envelope/A/generate.py
python docs/pip/B/build.py archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html Aegis_SIM_v48_WIP_PIP_B.html
node docs/envelope/A/run.cjs /tmp/env-a-results-1.json
node docs/envelope/A/run.cjs /tmp/env-a-results-2.json
python docs/envelope/A/report.py /tmp/env-a-results-1.json /tmp/env-a-report
```

오프라인 입력 `inputs.json`은 기준 브라우저에서 분리한 설정이다. 실행 시간은 별도 receipt에 기록하며, 결정적 결과 JSON에는 경과 시간을 넣지 않는다. CSV/그래프에서는 동일 시각의 최종 샘플 중복을 제거한다. 원시 진단 JSON의 종료 상태는 보존한다.

동일 경로 검증은 `verify_browser.py`가 수행한다. 별도의 폐기용 실제 게임 페이지에 원래 발사 함수로 미사일을 넣고, 동일한 이상 조건의 입력 포트를 적용해 원래 update 함수를 실행한다. 게임의 비행 함수 본문은 그대로이며, 이 검증을 사용자의 플레이 월드에서 실행하지 않는다.
