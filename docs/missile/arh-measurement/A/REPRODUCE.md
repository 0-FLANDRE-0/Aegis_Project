# 재현과 자료 구분

`kit/`는 첨부 원본이며 수정하지 않았다. 원래 README 명령은 `kit-replay/` 복사본에서 실행했다. `run_contract_checks.cjs`는 계약 위반을 찾으면 exit1이며, 정상적인 예상 결과다. 산술 검산은 exit0이다.

```sh
node docs/missile/arh-measurement/A/kit-replay/run_contract_checks.cjs
python docs/missile/arh-measurement/A/kit-replay/verify_saved_evidence.py
```

현재 설정 자료는 `active/`다. `capture_active.py`는 기존 저장소 지원 환경을 사용하고 pin된 실제 HTML을 읽는다. 원래 fixture의 SM-6 VLS 객체 생성 뒤 `maxTimeS=0`으로 적분을 건너뛰어 프로파일/함수만 캡처한다. 실제 비행 재실행과 혼동하지 않는다. 재실행할 때는 기존 증거를 별도 사본에 보존한다.

```sh
python docs/missile/arh-measurement/A/capture_active.py
node docs/missile/arh-measurement/A/run_active_contracts.cjs
python docs/missile/arh-measurement/A/verify_live_points.py
```

현재 설정 계약 검사도3개 위반을 검출해 exit1을 반환한다. 진단 환경 오류/예외와 구분해야 한다. 현재 프로파일을 수정하거나 기본값으로 치환하지 않는다. 출력의 `profileSha256`와 원래 HTML SHA를 먼저 확인한다.

실제 함수와 프로파일을 VM에 넣고 게임과 같은 수학 helper를 사용한다. 경계는 `getArhSeekerModel=RF_V2`, 캡처한 SM6_ARH_RF_V2_PROFILE, 탐지 draw0, 표준정규 잡음의 독립 결정적 스트림이다. 기본 sigma를 임의로 넣지 않는다. 실제 게임 RNG를 쓰지 않으며 합성점 관측이지 비행 모사기가 아니다.

`verify_live_points.py`는 실제 브라우저 함수로22개 점을 실행한다. 노이즈 draw만0으로 격리하고 finally에서 원래 함수를 복구한다. actual profile·global RNG·tick/life 불변을 검사한다. 독립 VM과 동일한 각도/거리/sigma/R을 비교한다.

브라우저 환경은 기존 Playwright/Chromium/CPU Canvas2D 지원을 재사용한다. Node24/Python3.12를 사용했다. 별도 새 추진/유도/시커 모델은 만들지 않았다.

`active-contracts-missing-TAU-invalid.log`는 초기 분리시험 환경의 누락된 수학 상수로 인한 무효 실행이다. 현재 `active-contracts.log`와 구분한다. 제품 결함 판정이나 재현 검사 통계에 합산하지 않는다.

원래240km 새 비행, 수정 A/B와 전체 회귀는 이번 범위가 아니다. 보고서 ZIP은 실행 HTML을 포함하지 않으므로 pin된 저장소 checkout의 기존 HTML·지원 코드가 필요하다.
