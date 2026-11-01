# TRACK-A 개발·검증 경위

아래 기록은 실패를 제거하거나 기대값을 갱신하는 승인 기록이 아니다. 최종 PASS에는 최종 RC2 SHA의 실제 실행 자료만 사용한다. 데이터와 기대값은 그대로 보존한다.

## 기준 고정과 최초 실행

시작 시 원격 `friendly-contact-a`가 지시서의 `4ba64ba0cace9124497a710d00df1b174984ffdc`와 같음을 확인하고 별도 `track-a-contract-trace`를 만들었다. 기준 HTML의 SHA는 `cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda`다. main·cg-turret-a·friendly-contact-a를 재기반/직접 수정·병합하지 않는다.

`baseline_runner.py`는 기존 friendly 스크립트를 runpy로 그대로 실행하고 evidence 출력만 TRACK-A 전용 디렉터리로 옮겼다. fixture·기존 단언·계수는 바꾸지 않았다. fresh D130의 전체 상태/RNG 서명30/30이 아카이브와 같았고 세 재현도 물리·트랙·RNG가 같았다. 최초 CIWS419025 실패, observer2 KNOWN_DELTA, 구형 EMCON UI14 INCOMPLETE를 baseline으로 고정했다. 실행 exit0은 기존 전투 손실 승인이나 모든 표적 요격 성공을 의미하지 않는다.

## 사건별 RNG 계측

과거419025 증거에는 사건별 global RNG·source key 기록이 부족했다. 별도의 test-only pass-through hook으로 native hit/측정 함수 결과를 그대로 반환하고, 기존 cdEmit dedupe가 끝난 뒤 사후 RNG를 붙였다. `seekerFailed` 확인을 위해 갱신 함수를 재호출하지 않고 이미 있는 behavior flag만 읽었다. CG 원본과 friendly 모두 추가 계측의 전체 상태/RNG 서명이 해당 ordinary run과 같았다.

34.55s 명중은 global RNG2회 소비, seeker57.8<100, 구조23.159<30, hard-failure flag없음으로 기록됐다. 이전과 다른 종료 틱의 최종 RNG만 비교해 인과를 단정하거나, 작은 사전 roundoff를 숨기고 모든 geometry가 동일하다고 선언하지 않았다. 추가 사격·명중·RNG/관측 분기를 기록했지만 결과를 맞추는 RNG·Pd/Pk·발사 간격 수정은 하지 않았다.

## RC1: 동작 보존 결과와 설명 오류를 구분

Audit 커밋은 `7e7ba089a689a0c876e5c99881d4631127a2a491`, RC1 구현은 `34c29992b2160428bf823136a6b765a546a1e34e`다. RC1 HTML SHA는 `2fbe5392ac5f69fb2c2b4a42efd76eb7a3fc1ec0b4d8253748c1fb0be4caded5`였다. 기존 native13의364와 friendly 대비 paired42가 통과했지만 후속 검토에서 합성 NETWORK_RECONCILE estimate의 현재 epoch를 실제 측정·수신 시각처럼 설명하는 metadata 오류를 발견했다.

**native 결과 동등성은 관측 계약 설명의 정확성까지 보장하지 않는다.** RC1 결과가 이미406개 통과했어도 최종 승인하지 않았다. 기존 worker는 결과를 보존하며 끝내고 UI/WebGL tail로 확대하지 않았다. 관련 controller pause/handoff/rc1-hold 기록은 `evidence/regression/RC1/`에 있다. 후보 runtime·성능·sampling 자료도 `evidence/rc1-candidate/`로 분리해 historical/not-final로 표시했다.

## RC2: metadata 보정 후 전부 새 SHA로 검수

`bae3cb3da79ba8de74220c9b53e99d7b884becea`에서 reconcile CANDIDATE/ASSIGNMENT의 `measuredAtS:null`, `receivedAtS:null`, `reported.stateAtS:now`를 명시했다. native selector/CI·EKF·분류·발사·피해 코드는 조정하지 않았다. 최종 HTML SHA는 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`, 내장 모듈 SHA는 `b5fc75792e4bc7f05b7dc8f7e67f0195af3240b2f4a9aeb04b0b8bf85daf1810`다.

Node unit에는 합성 epoch와 미상인 측정·수신 시각 구별 단언을 추가해52개가 됐다. direct native ingress47에서는 실제 reconcile candidate/assignment trace를 확인했다. unit52와 ingress47은 자연 RF/교전이나 기존420의 대체물이 아니다. 최종 RC2의 D130·자연 재현·trace ON/OFF·IFF·idle120·배속·owner독립성·성능·native13·paired·UI213·실제 WebGL8/29를 다시 실행한다. RC1의 완료 수를 RC2에 복사해 PASS로 계산하지 않는다. 최종 완료 여부는 root `VALIDATION.json` 및 해당 SHA raw자료를 따른다.

## 환경 문제·과거 UI debt

앞선 friendly 작업에서 보존된 Target crashed/OOM 및 누락된 sparse historical HTML 실패는 archived 환경 문제다. 현재 단계의 fresh 실행과 분리한다. 기존 retired-node/CPU Canvas2D·실제 WebGL 테스트 어댑터는 그대로 재사용한다. 원래 단언이나 허용 오차를 바꿔 구형 DOM을 통과시키지 않는다.

원래 EMCON UI14는 현 UI에 없는 `#lockBtn` bounding box를 요구한다. RC1의 제한된 원본 시도는 보존했고 이를 RC2의 합격으로 계산하지 않는다. `INCOMPLETE`로 명시하며 native EMCON 검수와 별도로 둔다. 새 자율제어·기능 OFF·동의 완화로 가짜 PASS를 만들지 않는다.

## 비용 측정과 보고 안전장치

호스트 스케줄링·동시 브라우저로 느린 baseline/outlier가 생길 수 있으므로 원시 반복 값을 삭제하지 않는다. 두 반복의 순서를 바꾸고 각 fresh page에서 warmup 뒤 같은 native tick 수를 측정한다. live heap 전후 차이를 총 할당량으로 부르지 않으며 HeapProfiler sampling도 통계 추정으로 표시한다. 중첩 association kernel의 inclusive 시간·함수 호출 수는 고유 후보 수처럼 합산하지 않는다.

`report.py`는 오직 REPORT.md만 생성한다. root의 authoritative finalEvidenceComplete/trackAStatus, 최종 SHA runtime·회귀·unit·scope·ingress·성능이 모두 확인되기 전에는 INCOMPLETE를 유지한다. VALIDATION·시험 결과·원본 기대값·제품은 수정하지 않는다. `--require-complete`는 미완료 시 exit2다. TRACK-B/C/D 구현·PR·병합·release/tag는 이번 단계에 포함하지 않는다.
