# 사용자 결정 기록

추가만 한다. 뒤집을 때는 새 줄로 적는다.

## SEEKER_UNIFY_A~B (날짜 미기록)

- 함정 RCS: Skolnik 1974 경험식 `52·√f_MHz·D_kt^1.5`. DDG 스텔스 저감 −15 dB(SIM_TUNED)
- U0 cue 바구니: 경과 시간 × 최대 속력(18 m/s)으로 확장, 중심은 이동하지 않음
- 시커 통합은 SHADOW → 비트 동등성 → ACTIVE 순서로 간다

## SEEKER_UNIFY_C (2026-11-03 전후)

- U2 차이 4건: 공통층이 양쪽 방식을 다 담고 프로필이 고른다. 기존 동작은 비트 단위로 보존한다
- 대함 시커 빔·LOS 물리 보정 진행. 정의가 불명이면 왕복(TX_RX_SEPARATE)으로 전환한다
- CUE_A 진행: cue 필터, 수동 RF 방위·고각, 고각 거리 추정, 공분산 바구니, DL 자리
- 기능 출처 태그 도입: Kh-35U 수동 RF `PUBLIC_CONFIRMED`, Kh-32 수동 RF `ASSUMED_THREAT`
- 위협 가정 스위치 기본값 `MAX_THREAT`

## 2026-11-05 (CUE_A-1)

- 모든 행렬·전투·회귀는 MAX_THREAT로만 시험한다. CONFIRMED_ONLY는 정적 검사 + 장면 1~2개, 성능은 UNVERIFIED
- 대역 모델 감도 기준: 기존 SPY 150/250 km 역산값을 유지한다(새 기준점 없음). CONFIRMED_ONLY도 같은 감도에 X대역 한정
- cue 기동 모델: Singer, τ=60 s, 6개 상태(위치·속도·가속도). 정확 이산화
- 속도 미상 시 축별 σ=vmax/2, 속도 공분산 상한 vmax/2
- 바구니: `max(하한, min(3σ, vmax×t + 3σ_INS))`. 하한이 우선한다
- 중기 수동 RF는 함정 레이더 family만 받는다(SPY·SPQ-9B·항해 레이더). 재머는 함정·눌카 모두 HOJ에서만 처리한다
- 회전 레이더 θ3는 기존 코드 값(BridgeMaster 2°, SPQ-9B 0.6°)을 쓴다
- 대함 시커 거리 하한 0.5 km 원복(SAM은 0.20 km 유지)
- 동등성 시험은 분기 커버리지 대표 케이스(경로당 최대 30) + 함수 해시. seed 200개 반복은 금지

## 2026-11-06

- PR #69, #70 병합
- 적 항공기는 나중에 삭제하고 다시 만든다. 그래서 발사 cue 오차 작업은 지금 하지 않는다
- 다음 작업은 U3 하푼. 수동 RF 우도 선택을 U3에 포함한다
- 하푼 cue 계산을 공통 CUE_A 필터로 바꾼다
- 레포 안에 작업 아카이브(`docs/archive/`)를 운영한다

## 2026-11-06 (SEEKER_UNIFY_U3 실행 확정)

- 일반 하푼 추적은 고정 4 km 상한을 제거하고 발사 트랙의 위치·속도·공분산·관측 시각을 CUE_A에 입력한다. 새 대체 거리 상수는 만들지 않는다.
- 경로점 모드는 기존 4 km 탐색 반경을 `ROUTE_PLAN_PRIOR`로 유지하고 실제 센서 관측으로 위장하지 않는다.
- 수동 RF 후보는 기존 Mahalanobis gate 통과 뒤 `d² + ln(det(S))` 최솟값을 사용한다. 동점은 관측 가능한 값으로 결정하며 emitter/platform/truth ID·위치는 쓰지 않는다.
- 하푼 HOJ는 공개 확인 전 `ASSUMED_THREAT`; MAX_THREAT ON, CONFIRMED_ONLY OFF다. 하푼 중기 수동 RF는 추가하지 않는다.
- A–D는 단계마다 push/readback하며 마지막에 광역 회귀를 한 번만 실행한다. PR까지만 진행하고 병합은 사용자가 결정한다.
- 최종 paired exact-state 4건은 원본 expectation을 바꾸지 않는다. C 42/42와 D SHADOW exact로 D ACTIVE 순위 변경에 귀속하고 raw FAIL 증거를 보존한다.

## 2026-11-06 (SEEKER_UNIFY_U3 PR #72 보정)

- 일반 추적 covariance search basket에서 pre-U3의 250 m 하한을 복구한다. 제거 대상은 4 km 상한뿐이며 새 튜닝 상수를 만들지 않는다.
- 실제 일반 추적 발사에서 동적 basket의 cueHandoff·시커·보호 판정 전달을 증명하고, 경로점 `ROUTE_PLAN_PRIOR` 시험과 분리한다.
- stale 관측은 실제 센서 dropout으로 만들고 상위 발사 게이트의 거부를 증명한다.
- Playwright 1.55를 실행하는 Actions job만 `ubuntu-24.04`로 고정하며 단순 재실행으로 처리하지 않는다.
- 보정 제한 시험 뒤 보정본 광역 회귀는 한 번만 실행한다. PR #72는 병합하지 않는다.

## 2026-11-07 (EMITTER_A)

- PR #72 병합본을 기준으로 EMITTER_A를 별도 `emitter-a` 브랜치에서 진행한다.
- DDG/CG의 기존 물리 방출 출력·순서·RNG·전력 호환 단위를 유지하며 ShipProfile 불변 장비 등록 → SHADOW exact → ACTIVE 순서로 전환한다.
- 장비 범주와 관측 `emitterClass`를 분리한다. 최소 범주는 AIR_SEARCH, SURFACE_SEARCH, NAV, FIRE_CONTROL, ECM이다.
- mutable 방사 상태는 기존 ShipRuntime observer/EW 소유자를 유지하고 이중 상태나 저장 스키마를 추가하지 않는다.
- SOV는 기존 SOV_A 메타데이터만 비활성 등록한다. 공개 근거 없는 RF 값을 만들거나 방출·탐지·EW·공격 기능을 활성화하지 않는다.
- 마지막 MAX_THREAT 광역 회귀는 한 번만 실행한다. CONFIRMED_ONLY는 기능 비활성/제한 장면만 확인하고 성능은 UNVERIFIED로 남긴다.
- 최종 산출물은 HTML ZIP과 보고서 ZIP을 분리하고 원격 전체 bytes/SHA readback 후 PR까지만 생성한다. 병합·release·tag는 사용자가 결정한다.
