# AEGIS_PLAN_STATUS v48 WIP SEEKER_UNIFY_U3

## 상태

- IMPLEMENTED: A–D ACTIVE
- TESTED: 단계별 게이트 + 최종 MAX_THREAT 광역 회귀 1회
- APPROVED: 사용자 확정 계약과 각 단계 게이트
- UNRESOLVED: paired raw 4건, 상속 부채, CONFIRMED_ONLY 성능, 후속 EMITTER_A
- RELEASE: 아님. PR #72 OPEN이며 병합·release·tag는 사용자 결정 전 금지

## 기준과 결과물

- 기준 main: `be19f46794705a18bfd69feba99d7a4b00dd4a0c`
- 기준 HTML: `Aegis_SIM_v48_WIP_CUE_A_1.html`
- 기준 SHA-256: `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`
- 결과 HTML: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html`
- 크기: 22,143,087 bytes
- SHA-256: `3eecf254b9a586398fb2236068cca722912730d8dc492275f06157407ed6e2ea`
- packed main SHA-256: `e050149c3cfbf1113033df7955c3c2d6a88788879556fb1f333595ff594b4639`

## 완료 범위

1. 하푼 RF 관측을 U2 공통 프로필 계약에 연결하고 기존 출력·RNG를 보존했다.
2. 일반 추적의 고정 4 km 상한을 제거하고 발사 시점 트랙 메모리와 공분산을 CUE_A 예측에 전달했다.
3. 경로점 모드는 4 km `ROUTE_PLAN_PRIOR`로 유지하며 실제 관측으로 위장하지 않는다.
4. ASM HOJ를 공통 포트 뒤로 옮기고 하푼 terminal HOJ를 미사일별 상태로 추가했다.
5. 하푼 HOJ는 `ASSUMED_THREAT`; MAX_THREAT ON, CONFIRMED_ONLY OFF다.
6. Mahalanobis gate 통과 후 수동 RF 후보를 `d² + ln(det(S))`로 선택한다.
7. truth ID/숨은 위치, 신규 보상 상수, 저장 스키마 변경은 없다.

## 검증

- A: power 55,441 + cell 3,615 비교, mismatch 0; 대표 18장면 exact.
- B: 유효/노화/누락/물리상한/route prior 계약 PASS; 자연 6장면 결정적.
- C: ASM 90 SHADOW state/RNG mismatch 0; MAX/CONFIRMED 기능 장면 PASS.
- D: 20장면 SHADOW exact, ACTIVE 반복 exact, truth/RNG 선택기 사용 0.
- 최종 광역 1회: native 364/364, UI 213/213, WebGL 29/29 PASS.
- paired raw 38/42: 두 함종 raid의 combat RNG/observer exact-state 4건.
  C 시점 42/42, D SHADOW exact, D ACTIVE 순위 변경으로 원인 분리했다.
  물리·손상·VLS·최종 결과는 동일하며 기대값/허용오차 변경은 0이다.
- `#lockBtn` 14는 상속 INCOMPLETE로 유지했고 PASS로 계산하지 않았다.

## 다음

- 우선순위는 기존 로드맵의 `EMITTER_A`다.
- `EMCON_B`, 적 항공기 재제작, Kh-32 60 km 조사, TRACK-D/OODA는 U3에 포함하지 않았다.
- PR #72 병합은 사용자가 결정한다.
