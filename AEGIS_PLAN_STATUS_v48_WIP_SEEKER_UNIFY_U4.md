# AEGIS_PLAN_STATUS v48 WIP SEEKER_UNIFY_U4

## 상태

- IMPLEMENTED: 커밋 A(SARH 쌍정), B(RAM 수동 RF/IR), C(공통 연관·상태기계) ACTIVE
- TESTED: A/B/C 제한 게이트, 동결 후보 MAX_THREAT 광역 회귀 정확히 1회, byte-exact 재생성·packed main 문법
- APPROVED: 단계별 SHADOW 동등성과 RAM 신호 소유권의 좁은 결함 수정
- UNRESOLVED: `CONFIRMED_ONLY` 성능, SOV 센서·무장, 통신 EMCON, Kh-32 별도 조사와 상속 회귀 부채
- RELEASE: 아님. PR #76 제출 후보이며 병합·release·tag는 사용자 결정 전 금지

## 기준과 결과물

- 기준 main: `f17d3777a625699ab26f6a40de80a383f675ae85` (PR #75 ESM_A merge commit)
- 기준 HTML: `Aegis_SIM_v48_WIP_ESM_A.html`
- 기준 SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- 결과 HTML: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`
- 크기: 22,195,923 bytes
- SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- packed main SHA-256: `e06c2e6133b66fe8be2f6c1305b39473a7776176680390a45673e7487e9a462e`

## 완료 범위

1. SARH는 능동 단안 모델로 가장하지 않고 `SARH_BISTATIC_4D` 어댑터로 연결했다. SPG 조사, 송·수신 빔, 두 LOS, 두 경로와 weapon-local RNG의 기존 소유권을 유지한다.
2. RAM의 RF/IR을 각각 `PASSIVE_RF_2D` / `PASSIVE_IR_2D` 익명 측정으로 연결했다. player와 owner/NPC 복사본은 같은 계약을 쓰되 물리 후보 생성과 RNG는 기존 소유자에 남는다.
3. 물리 방사 세기가 수신 RAM의 추적 품질에 역의존하던 결함을 제거했다. 기존 명목값·감도·gate·Pd·RNG는 튜닝하지 않았다.
4. ASM·Harpoon·SARH·ARH·RAM의 연관 선택과 상태 사건을 공통 엔진으로 옮겼다. HOJ, route/INS, SARH↔ARH arbiter, RAM MEM/RF/IR authority와 유도 법칙은 무장 훅으로 보존했다.
5. 공통 계층에는 entity/profile/faction/hostile/truth 위치가 없고 RNG를 소비하거나 저장 스키마를 추가하지 않는다.
6. 기존 로드맵 U5와 U6은 별도 브랜치 없이 U4 커밋 B/C로 흡수했다.

## 검증

- A: bistatic power 20,088회, cell 411,299회 mismatch 0; 실제 SM-2 SARH 비행과 두 LOS/beam fail-closed PASS.
- B: SHADOW exact; RF/IR authority·dropout·복수 RAM 격리 PASS. 허용된 ownership 수정 외 보호 함수 해시 동일.
- C: SHADOW association 5,002회, state 1,648회 mismatch 0; ACTIVE 전술 결과·반복 결정성 exact.
- 최종 1회: static 13/13, native 364/364, ESM_A paired 42/42, 후보 결정성 42/42, 현재 EMCON 14/14, UI 213/213, 실제 WebGL 29/29 PASS.
- U4 장면 raw 15/19의 네 assertion은 제품 실패가 아니라 하네스 판정 결함이었다. 원시 FAIL을 보존한 채 기록된 terminal physics/RNG와 제품 바이트만 오프라인 재검토해 effective 19/19로 분류했다. 광역 회귀는 재실행하지 않았고 제품 코드·기대값·허용오차 변경은 0이다.

## 다음

- Actions의 U4 제한 candidate gate를 통과시킨 뒤 PR #76을 제출한다.
- PR은 사용자가 병합한다. 이 단계에서 release/tag는 만들지 않는다.
- `CONFIRMED_ONLY`는 기능 비활성 제한 장면만 확인했으며 성능은 `UNVERIFIED`다.
