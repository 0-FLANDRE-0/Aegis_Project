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

## 2026-11-07 (EMITTER_A PR #73 종료)

- ACTIVE에서는 legacy resolver를 호출하지 않고 declared resolver만 함정당 정확히 1회 호출한다. SHADOW는 legacy/declared를 각각 1회 호출하고 legacy를 전술 권위로 유지한다.
- 종료 뒤 광역 회귀는 반복하지 않는다. SHA `04bfb9c9…98c6`의 364/364·42/42·213/213·29/29는 pre-closure 광역 증거로 보존하고, SHA `3a5886b4…c2be`는 exact call/output/RNG·성능·한정 Chromium candidate 게이트로 마감한다.
- 현재 후보의 단일 권위는 `AEGIS_CURRENT_PRODUCT.json`이다. 전용 `AEGIS current candidate` workflow만 후보 승인을 담당하며, 고정 과거 제품을 검사한 legacy Actions는 후보 승인으로 해석하지 않는다.
- 서로 다른 Chromium 버전의 libm 최하위 비트는 반올림이나 허용오차로 숨기지 않는다. manifest에 고정된 U3 기준과 후보를 동일 Chromium에서 실행해 전체 JSON exact로 비교한다.
- PR #73은 사용자 결정 전 병합하지 않으며 main 직접 커밋·release·tag를 만들지 않는다.

## 2026-11-08 (EMCON_B 착수)

- 사용자가 PR #73을 merge commit `3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941`로 병합했다. EMITTER_A 제품 SHA는 `3a5886b4…c2be`로 유지되며 release/tag는 없다.
- 기존 `emconActive`/`observerC(r).emcon`은 전체 레이더 침묵 master 권위로 유지하고, EMCON_B는 함정별 범주 정책과 장비 override만 소유한다.
- 레이더 EMCON은 Hawklink/Link 통신 송신을 끄지 않는다. 통신 EMCON은 별도 후속 정책이다.
- FIRE_CONTROL은 registry 계약과 비활성 UI 경로만 다루며, 활성 SPG-62 방사원을 새로 등록하지 않는다.
- EMCON_B는 `emcon-b` 별도 브랜치와 새 PR로 진행한다. main 직접 변경·자동 병합·release/tag는 하지 않는다.

## 2026-11-08 (EMCON_B PR #74 2차 종료 보정)

- 상단 `전파방사통제`는 문자열 조합으로 추론하지 않고 ShipRuntime별 `AEGIS_SHIP_EMCON_B_2.allRadiationSilent`를 단일 권위로 쓴다.
- 유효 방사 우선순위는 registry/운용 가능→손상·전원·offline→global hard-off→radar master→network overlay→equipment override→category→ECM request/allocator다. `FORCE_RADIATE`는 global/master/network/손상 gate를 우회하지 못한다.
- Global ON 중 운용자가 SPY/SPQ/NAV/ECM 하나를 ON하면 global과 radar master를 해제하고, 모든 범주를 SILENT·override를 INHERIT로 정리한 뒤 선택한 장비만 원자적으로 방사한다.
- Global silence는 ECM technique request를 삭제하지 않고 allocator/output/coupling/HOJ evidence만 0으로 만든다. Hawklink/Link 통신은 레이더 EMCON과 분리한다.
- 수정 전 SHA `3343f5bb…c33`의 MAX_THREAT 광역 증거는 그 SHA에만 귀속한다. 보정 SHA에서는 광역을 재실행하지 않고 지시된 제한 closure와 candidate Actions 1회로 닫는다.
- 기존 `emcon-b`/PR #74만 갱신하고, 병합·main 직접 변경·release·tag는 사용자 결정 전까지 하지 않는다.

## 2026-11-08 (EMCON_B 완료 경계)

- 기존 radar master는 계속 권위 상태이며 EMCON_B는 함정별 category/equipment detail만 소유한다. 네트워크 group mode는 detail을 파괴하지 않는 transient overlay다.
- 실제 물리 방출과 own/NPC 센서 측정을 같은 정책으로 차단하고, ECM silence는 요청을 보존한 채 allocator/output/receiver coupling/HOJ를 0으로 만든다.
- `FIRE_CONTROL`은 활성 SPG-62 registry item이 없는 현재 상태를 정직하게 표시한다. 계약/비활성 UI 이상을 완료로 주장하지 않는다.
- 기존 `#lockBtn` 14건은 MAP_E의 visible-node 퇴역을 반영한 test-only adapter로 native listener를 실제 실행한다. 제품 우회나 기대값 완화로 처리하지 않는다.
- 최종 MAX_THREAT 광역은 동결 후보에서 정확히 1회만 실행한다. assertion 전 Chromium crash와 EMITTER_A에서도 같은 fixture 결과는 raw 실패를 보존한 채 `INCOMPLETE/INHERITED_DEBT`로 분리하고 PASS로 바꾸지 않는다.
- 현재 후보 Actions는 manifest stage whitelist로 EMITTER_A/EMCON_B를 dispatch한다. 실행 결과 문서만 변경해 재귀 실행하지 않으며 run 번호는 PR 본문에만 기록한다.

## 2026-11-08 (EMCON_B PR #74 3차 — 함종 독립 바인딩)

- 공통 EMCON 센서 소비자는 실제 장비명이나 기존 구현 키가 아니라 `AIR_SEARCH_VOLUME`, `SURFACE_SEARCH_SCAN`, `NAVIGATION_SCAN`을 사용한다.
- 정확한 `consumerId -> equipmentId` 관계는 불변 ShipProfile 방사 장비 등록부가 소유한다. 다른 함종은 프로필 바인딩만 추가하며 공통 조회 코드를 바꾸지 않는다.
- 바인딩 누락·중복·없는 장비·범주/출력 불일치는 fail-closed다. 같은 범주의 다른 허용 장비로 대체하는 우회 판정은 금지한다.
- 내부 consumer ID는 UI에 표시하지 않는다. 실제 장비명은 선택 함선에 설치된 등록 장비 행에서만 표시한다.
- 정적 바인딩은 저장 데이터에 복제하지 않으며 `AEGIS_SHIP_EMCON_B_2`를 유지한다. 광역 회귀는 반복하지 않고 바인딩 전용 결정적 검사와 기존 제한 폐쇄 게이트만 실행한다.
