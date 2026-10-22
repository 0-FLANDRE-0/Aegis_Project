# ALL4_TERM 누적 이식과 검증 재현

기준은 최신 `pip-b-env-a@294bbb066df41489e77f5f16d0ad6a84eec32f91`의 PIP_B다. 구형 UI_A1 예제에 적용한 결과를 가져오지 않는다. PIP_B 원본 SHA-256은 `ad6ed26d8011fd1bcab80c66eac06a63c748e52b471eb622ef38a2ad26498a55`다. 기존 UI/PiP, 헬기, ISAR, 하푼과 ENV_A 자료를 보존한다.

## 소스 이식

`kit/`은 사용자가 제공한 7개 파일 그대로다. 첨부 독립 테스트 JSON의 PASS는 제공자의 기록이다. 이 작업의 실제 검증 결과와 합산하지 않는다. 구식 truth 의존 PostMiss 실험본은 포함하지 않는다.

현재 HTML에는 ENV_A 네이티브 함수 사본이 문자열로 내장되어 있다. 첨부 CLI는 문자열 속 B4 정의까지 세어 3개로 인식하여 fail-closed 중단한다. `build.py`는 진단 문자열을 떼어 놓고 두 실제 경로(자함과 NPC owner context)에 같은 codemod를 적용한다. 이전 B4 적용 여부를 검사하는 원래 idempotence 경로를 유지한다. 새 ENV_B 사본은 실제 수정된 현재 네이티브 코드에서 다시 추출한다.

```bash
python docs/missile/termination/A/build.py
NODE_PATH=docs/performance/F/node_modules node docs/envelope/B/extract.cjs /tmp/aegis-term/final-live.js
python docs/envelope/B/generate.py
python docs/missile/termination/A/build.py
NODE_PATH=docs/performance/F/node_modules node docs/missile/termination/A/verify_static.cjs Aegis_SIM_v48_WIP_ALL4_TERM.html /tmp/static.json
```

Node 24 / Python 3.12 / `acorn`, `eslint-scope`, Playwright Chromium을 사용했다. 의존 패키지는 기존 `docs/performance/F/package-lock.json`으로 설치한다. 브라우저 실행에는 환경이 허용하는 로컬 소켓 접근이 필요하다. `docs/pip/B/browser_backend.py`의 기존 검증 전용 Canvas2D CPU 설정을 사용하며 실제 WebGL을 대체하지 않는다.

## 첨부 종료기에서 보완한 두 가지

1. **대체 유도 지원:** ARH만 차단하고 SARH를 유지한 18조건 중 기존에 명중하던 16조건이 첨부 원안의 12초 미획득 종료로 끊겼다. 새 어댑터는 ARH 대신 신선한 SARH RF EKF를 사용할 수 있으며, 이미 수신해 유효하다고 판정된 DL 유도 상태의 `isValid/source`만 확인해 종료를 보류한다. DL 좌표를 읽지 않는다. 지원이 사라지면 무지원 미획득 12초 / 교차 후 무지원 공백 2.5초를 검사한다. SARH에 ARH 미획득 규칙을 복사하지 않는다.
2. **교차 시계 상한:** 원안의 `min(65, range/closing)`을 종료기에서만 `range/closing`으로 바꿨다. 관측 거리 35km, 접근률 200m/s는 175초이며 65초로 잘라서는 안 된다. Kappa 유도용 90초 상한과 계산은 변경하지 않는다.

이 두 보완은 `support-guard.cjs`에 분리했다. B4 helper의 코드와 수치, MR/ESSM의 상한 변경, ER/SM-6의 기존 프로파일 한계는 첨부 ALL4와 같다. SM-6 전원 수명은 게임 조정값 480초다. MR 380 / ER 430 / ESSM 185초는 유지한다. `window.AEGIS_GAME_TERMINATION_ENABLED=false`는 새 종말 종료만 끄며 배터리 종료는 끄지 않는다.

## 실제 게임 회귀와 시험의 경계

`verify_live.py`는 전체 완성 HTML을 Chromium에서 부팅·출항하고, 폐기할 테스트 페이지에 `live-fixture.js`만 삽입한다. 실제 네이티브 발사·INS·할당기·SPG 서보·RF 프런트엔드·시커 EKF·B4·Kappa·힘 적분·신관을 실행한다. 선형 운동과 함 레이더 트랙은 명시한 시험 조건으로 공급한다. 전체 전술 AI를 동시에 돌린 플레이 승률 시험은 아니다.

에코 차단은 프런트엔드의 측정 패킷만 비우며 시커 추적 상태를 직접 주입하지 않는다. 표적 소실은 시험 엔티티 제거다. 그 사실을 종료기로 전달하지 않는다. 배터리 검사는 실제 발사·비행 뒤 시험 시계만 경계 부근으로 옮겨 네이티브 업데이트를 진행한다. 480초 전체를 자연 비행했다는 검증으로 표현하지 않는다.

```bash
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ALL4_TERM.html /tmp/normals.json --cases docs/missile/termination/A/cases/normal.json --batch 10
python docs/envelope/B/verify_browser.py Aegis_SIM_v48_WIP_ALL4_TERM.html /tmp/env-browser
node docs/envelope/B/run.cjs /tmp/env-b-results.json
```

사거리 진단은 [ENV_B](../../../envelope/B/README.md)를 따른다. ENV_A의 구버전 표와 원시 결과는 `docs/envelope/A/` 그대로 보존한다. 지도/발사 관문에는 이 표를 연결하지 않는다.

## 알려진 사격 결과 변화

SM-6 / 초기 거리 100km / 고도 5km / 접근 250m/s / seed 12002는 PIP_B에서 명중하고 Dynamic B4 적용 뒤 종료기 OFF에서도 비명중 후 SEA_IMPACT가 된다. 재현 원시 궤적을 증거에 포함한다. 신규 종료기의 조기 종료로 분류하지 않으며, 요청한 ALL4 수치를 바꾸어 숨기지 않는다. 따라서 모든 기존 교전 결과가 동일하다는 주장이나 무제한 안정판 선언을 하지 않는다.

전체 월드 자연 관측 검사는 `verify_observed_world.py`로 재현한다. 보고서의 8발 비교는 실제 레이더가 만든 트랙을 커서 지정→LOCK→정식 VLS로 발사하고 전체 fixed tick 및 실제 WebGL을 사용한다.
