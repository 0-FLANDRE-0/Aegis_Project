# SEEKER_UNIFY_C 지시서: U2 ACTIVE 마무리 → 대함 시커 빔·LOS 물리 보정 → CUE_A(cue 갱신 경로 통합)

## 0. 현재 상태 (이 문서가 최신 기준)

- SEEKER_UNIFY_B(PR #68) 결과: **U0 ACTIVE + U1 ACTIVE + U2 SHADOW**. U2는 `IMPLEMENTATION_DIVERGENCE` 3건 + `FP_ORDER` 1건으로 지시대로 멈췄다.
  - 제품 `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html`, SHA-256 `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d`
- 사용자 결정(이 문서로 확정):
  - U2 차이 4건은 **공통층이 양쪽 방식을 모두 담고, 무장 프로필이 고르는 방식**으로 정리한다. 기존 동작은 비트 단위로 유지한다.
  - 대함 시커(WIP22)의 빔·LOS 계산은 이번 지시서에서 **물리 보정까지 진행**한다. 단, U2 ACTIVE와 별도 단계로 한다.
  - 그다음 **CUE_A**(발사 cue 확장, cue 필터, 수동 RF 방위·고각, 수동 거리 추정, 공분산 바구니, 기능 출처 태그, 위협 가정 스위치, DL 자리)를 진행한다.
- 이 문서의 세 단계는 **반드시 순서대로** 한다. 각 단계는 직전 단계 산출물과 비교한다. 빔 보정과 CUE_A가 둘 다 Kh-35U 획득을 바꾸므로, 효과가 섞이지 않게 하려는 것이다.

## 1. 기준과 산출물

- **기준**: PR #68이 main에 병합됐으면 그 main HEAD, 아니면 `seeker-unify-b` `2879f2a6`. 시작 시 HEAD·HTML SHA를 대조하고 실제 값을 기록한다.
- **작업 브랜치**: `seeker-unify-c`
- **커밋 작성자**: `110261808+0-FLANDRE-0@users.noreply.github.com`
- **산출 HTML**: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`
- **문서 위치**: `docs/missile/seeker-unify/C/`
- 보고서 맨 위에 `IMPLEMENTED / TESTED / APPROVED / UNRESOLVED / RELEASE`를 표시한다.
- `AEGIS_PROJECT_INSTRUCTIONS.md`의 Truth 경계, 고정 dt, 격리 RNG 규칙을 그대로 적용한다.
- **실행 시간 상한**: 단계 1 **2시간**, 단계 2 **3시간**, 단계 3 **6시간**. 넘으면 그 시점 상태를 커밋하고 보고한 뒤 멈춘다.

## 2. 공통 규칙

1. **새 SIM_TUNED 상수는 이 문서에 적힌 것만** 만든다. 값은 해당 단계 시험 실행 **전에** 고정해서 커밋하고, 결과를 보고 다시 고르지 않는다.
2. **보상 튜닝 금지.** 빔 보정이나 CUE_A로 획득 거리가 줄어도, 그걸 메우려고 빔폭·감도·기준 RCS·문턱·탐색 구역·gate를 바꾸지 않는다.
3. **Truth 비누수.** cue, cue 필터, 수동 RF 측정, 바구니, 연관, EKF, 유도에 실제 entity id, profile id, 실제 좌표, 실제 속도를 넣지 않는다. 방사원 기하는 측정 합성 내부에서만 쓰고, 측정 payload에는 넣지 않는다. 사후 truth는 진단에서만 쓴다.
4. **RNG.** 무장별 기존 독립 RNG의 seed와 advance 순서를 유지한다. 새 측정이 난수를 쓰면 해당 무장의 격리 스트림에서 고정 순서로 쓰고, 그 사실을 기록한다.
5. **시험 범위.** 단계 중간에는 변경 함수 외 함수 해시 동일 확인 + 그 단계 시험만 한다. 광역 회귀는 지시서 전체에서 **1회**, 마지막 단계가 끝난 뒤(또는 멈춘 시점)에만 한다.
6. **기대값.** 해당 단계 변경 경로로 설명되는 기대값 변화는 사용자 사전 승인으로 갱신한다(전후 값·원인 기록, 허용 오차 변경 0). 설명되지 않는 변화는 멈추고 보고한다.
7. **멈춤 규칙.** 게이트 실패, 시간 상한 초과, 이 문서가 정하지 않은 판단 분기를 만나면 멈추고 보고한다.
8. **병합.** PR 생성까지만 한다. main 병합, release, tag는 하지 않는다. 병합은 사용자가 한다.

## 3. 단계 1 — U2 ACTIVE 마무리 (동작 변경 없음)

### 3.1 공통 계약을 상위집합으로 확장

| 항목 | 공통층이 담는 것 | 프로필 옵션 | ASM(WIP22) | SAM ARH |
|---|---|---|---|---|
| 빔·LOS | `txGain`, `rxGain`, `losTxQ`, `losRxQ`를 따로 받음 | `beamConvention` | `COMBINED_SINGLE`: 기존 결합 이득 1회 + LOS 1회 | `TX_RX_SEPARATE` |
| 셀 크기 | 구성원 목록 + 전력 가중 RMS + 구성원 최대값을 모두 출력 | `extentPolicy` | `POWER_WEIGHTED_RMS` | `MAX_MEMBER` |
| 각도 묶음 | 축별 판정과 구면 판정을 모두 지원 | `angularPolicy` | `AXIS_SEPARATE_COMPOSITE` | `SPHERICAL_MEMBER_PRESERVING` |

- 위 옵션값은 **하드웨어 주장이 아니라 기존 동작 보존용**이다. 프로필에 `provenance:'LEGACY_EQUIVALENCE'`로 표시한다.
- ASM `beamConvention`은 단계 2에서 다시 판정한다고 주석과 보고서에 명시한다.

### 3.2 FP_ORDER

SAM 단안 전력 계산은 공통층의 곱셈 순서를 기존 `_arhNormalizedMonostaticPower`와 똑같이 맞춰서 비트 동일로 만든다. 허용 오차로 넘기지 않는다.

### 3.3 전환

- SHADOW에서 위 계약으로 비트 동일이 나오면, 공통 `synthesizeEchoes` / `resolveCells`가 실제 결과를 내게 바꾼다.
- 기존 함수는 공통층에 위임하는 얇은 래퍼로 남긴다.
- **U2 SHADOW 감싸기 코드와 감사 배열은 제거한다.** 지금은 실제 게임에서도 시커 계산을 한 번 더 하고 있어서 런타임 부담이 있다.

### 3.4 시험과 게이트

- SEEKER_UNIFY_B의 U2 대표 장면 78개 + U1 동등성 6경로 × 200 케이스
- 게이트: 기존 대비 **비트 동일**, 페이지 오류 0, 결정성 동일, 변경 함수 외 함수 해시 동일
- 하나라도 다르면 멈춘다.

## 4. 단계 2 — 대함 시커 빔·LOS 물리 보정

### 4.1 배경

단안 능동 레이더는 같은 안테나로 쏘고 받는다. 그래서 빔 패턴 손실은 송신·수신에 각각 한 번씩, 가림·전파 경로 손실도 왕복 두 번 들어가는 것이 물리적이다. SAM ARH는 이렇게 계산한다. WIP22 ASM은 결합 이득 `max(.08, cos²·cos²)`와 LOS를 한 번만 곱한다. 이 때문에 빔 가장자리와 부엽 감도가 실제보다 좋게 나올 가능성이 있다. 부엽 바닥도 ASM은 0.08, SAM은 0.012/0.006이다.

### 4.2 먼저 감사 (코드 변경 없음)

`BEAM_DEFINITION_AUDIT.md`에 아래를 기록한다.

1. Kh-35U·Kh-32 프로필의 `searchBeamHalf*`, `trackBeamHalf*`가 단방향 기준인지 왕복 기준인지. 근거는 코드 주석, 이전 WIP 문서, 커밋 기록 순서로 찾는다.
2. 현재 패턴 함수에서 반폭 값이 실제로 뜻하는 것. 예: `cos²(off/half·π/2)`는 `off=half`에서 0이 되므로, 반폭은 −3 dB 폭이 아니라 영점 폭으로 쓰이고 있다. −3 dB 지점이 어디인지 계산해서 적는다.
3. ASM의 `losQ`, 해면·기상 계수가 단방향 값인지 왕복 값인지. 같은 함수를 SAM이 어떻게 쓰는지와 대조한다.
4. 부엽 바닥 0.08의 출처
5. 공개 자료: ARGS-35/Gran-K, Kh-32 시커의 빔폭·부엽 공개 수치. 없으면 없다고 적는다.

### 4.3 판정 규칙 (감사 전에 고정)

- **반폭·LOS가 단방향 값이거나 정의가 불명확하면** → 단방향 값으로 정의하고 `beamConvention:'TX_RX_SEPARATE'`로 바꾼다. 송신·수신에 같은 단방향 패턴을 각각 곱하고, LOS·전파 손실도 SAM과 같은 정의로 왕복 적용한다. 정의를 정한 사실은 `SIM_TUNED`로 표시한다.
- **문서로 왕복 기준임이 확인되면** → 바꾸지 않는다. 근거를 기록하고 단계 2를 "변경 없음"으로 끝낸다.
- 부엽 바닥은 단방향 값으로 해석해 송신·수신에 각각 적용한다. **0.08이라는 값 자체는 바꾸지 않는다.** 값 변경이 필요해 보이면 제안만 한다.
- HOJ와 수동 RF는 **수신 전용**이라 단방향이 맞다. 손대지 않는다.
- 반폭, 기준 거리 `snrRefKm`, 기준 RCS, 문턱, 탐색 구역은 바꾸지 않는다.

### 4.4 시험 (단계 1 산출물과 같은 seed로 비교)

1. SEEKER_UNIFY_A 1,590 조건 주 행렬
2. U0 cue 행렬: Kh-35U·Kh-32 × 60/100/130 km × (15 kn 직진, 30 kn 직진, 30 kn+30°, 30 kn+90°) × 5 seed × EMCON OFF/ON
3. 오획득 대조군: CHAFF / NO_TARGET / SEA_CLUTTER 전체
4. TRACK-C 이탈 37발 재현, ASM_SEEKER_A S1 행렬
5. 거리별 첫 ACQUIRE·첫 TRACK 거리 분포 (대형 함정, 15/200 m)
6. 참고: 60 전투

### 4.5 게이트

- 오획득 증가 0
- 이웃 ASM·자함 최초 연관 0
- 결정성 동일
- 획득 거리 감소와 TRACK 실패 증가는 **허용**한다. 대신 실패한 셀마다 원인을 빔 가장자리·부엽 SNR 변화 수치로 설명해야 한다. 설명되지 않는 실패가 하나라도 있으면 멈춘다.
- 보고에 단계 1 대비 Kh-35U·Kh-32 획득 거리 변화 표를 넣는다.

## 5. 단계 3 — CUE_A: cue 갱신 경로 통합

### 5.1 발사 cue 출처 전수 감사 (코드 변경 없음)

`LAUNCH_CUE_SOURCES.md`에 모든 대함미사일 발사 경로를 정리한다. SEEKER_UNIFY_B의 `INS_CUE_WRITERS.md`를 출발점으로 쓴다.

- 대상: 항공기 발사(`spawnEnemyMissile(fromTarget)`), 소브레멘니 NPC 발사, 기타 함정·시나리오 발사, 시험 fixture
- 경로마다 기록: 발사 측이 실제로 갖고 있는 표적 정보(위치·속도·시각·오차)와 그 정보의 출처(자체 트랙, ESM, 외부 정보, 또는 truth + 난수)
- 발사 측에 트랙 속도 추정이 **없으면** 이번에 만들지 않는다. 그 경로는 `velocity:null`로 둔다. truth + 난수 경로는 `UNRESOLVED`로 기록만 한다.

### 5.2 cue 필터

U0의 거리/방위 시계 구조를 작은 칼만 필터로 대체한다.

- **상태**: 표적 수평 위치·속도 `(x, y, vx, vy)`. 고도는 기존 조준 고도를 고정으로 쓴다.
- **초기화**: 발사 cue의 위치·속도·공분산. 속도가 null이면 속도 0, 속도 분산 `vmax²`로 시작한다. 이렇게 하면 U0의 "최대 속력 × 경과 시간" 성장이 특수한 경우로 자연스럽게 포함된다. 공분산이 없으면 기존 발사 INS 오차를 1σ로 쓴다.
- **시작 시각**: 발사 측 정보에 시각이 있으면 그 시각, 없으면 발사 시각
- **예측**: 등속 + 기동 가속 잡음. 속력 크기는 `vmax`로 제한한다.
- **갱신**: 수동 RF 방위·고각(5.3), DL(5.6, 자리만)
- **기존 경로 처리**: `asmApplyPassiveBearingB2`의 gain 회전과 `asmTargetMemoryDriftB2`는 필터로 대체한다. 기억 드리프트는 필터 예측 잡음이 맡는다. `_c52InsMemory` 고정 기억 경로는 기존 동작을 유지한다.
- 유도가 따라가는 INS 조준점(`em.insTgtX/Y`)은 필터 예측 위치로 갱신한다. 그래서 DR 중심 이동이 유도에도 반영된다.

### 5.3 수동 RF 측정 재작성

- **방사원**: 자함 하드코딩(`aircraft.x()`)과 전역 `emconActive`를 쓰지 않는다. 기존 `electronicPhysicalEmittersF()`가 내는 함별·장비별 방사원을 쓴다. 각 방사원의 EMCON, 장비 꺼짐·손상, 대역, 출력을 그대로 따른다.
- **수신 세기**: 단방향 R⁻² × 방사원 출력 × 방사원 안테나 방향성(`beamAz`가 있으면 그 방향 기준, 없으면 평균값) × 미사일 수동 수신 패턴 × LOS. 수신기 감도 문턱 이하는 측정 없음.
- **측정값**: 방위 + 고각 + SNR. 오차 σ는 기존 `bearingErrorRad`를 기준으로 SNR이 낮을수록 커지게 한다. 고각은 저고각에서 해면 다중경로 때문에 σ를 더 키운다. RAM RF 모델의 수평선 항과 같은 형태를 쓴다.
- **방사원 선택**: cue 필터의 예측 방위·고각 주변 Mahalanobis 게이트 안에서 고른다. 여러 개면 게이트 거리가 가장 작은 것을 고른다. 다른 함 방사원에 끌려가는 경우는 실제 약점이므로 막지 않는다. 대신 진단에 기록한다.
- 측정 payload에는 방사원 id나 함 id를 넣지 않는다. 대역·방사원 종류(`emitterClass`)는 수신기가 실제로 알 수 있는 정보라 허용한다.

### 5.4 수동 거리 추정 (고각 기반)

- 고각 측정을 cue 필터에 **직접** 넣는다. 측정 모델은 "필터 예측 위치에 가정 방사원 높이를 둘 때 미사일에서 보이는 고각"이고, 지구 곡률과 표준 굴절(4/3 지구 반경)을 포함한다. 그러면 고도가 높은 Kh-32는 거리 정보를 자연스럽게 크게 받고, 저고도 Kh-35U는 거의 못 받는다.
- 미사일 자기 고도는 미사일 자체 항법 상태값을 쓴다. 자기 상태라 truth 누수가 아니다.
- 진단용으로 고각에서 직접 푼 거리 추정값과 그 σ도 기록한다. 이 값을 cue에 덮어쓰지 않는다.
- 기존 주석 "MUST NOT infer true range"는 **truth 거리 누수 금지**라는 뜻이다. 측정에서 추정한 거리는 허용된다. 주석을 이 뜻으로 고쳐 쓴다.

### 5.5 공분산 기반 바구니

- 필터 예측 위치와 공분산을 미사일 기준 거리·방위로 투영한다. 바구니는 `basketSigma`배 폭으로 잡는다.
- 하한은 U0 값을 그대로 유지한다: 거리 반폭 `max(1200 m, 0.12R)` 이상, 거리 창 아래 끝 `max(1500 m, 0.5R)` 이상, 방위 반폭 5° 이상
- 상한: 방위는 `searchSectorAzDeg`, 고각 4°는 변경 없음
- EKF가 생긴 뒤의 연관 게이트는 건드리지 않는다.

### 5.6 DL 자리

`cueUpdate({source:'DL', positionM, velocityMps?, covariance, timeS})` 인터페이스만 만들고 연결하지 않는다. 호출하면 필터의 위치(+속도) 측정 갱신으로 들어가는 구조여야 한다.

### 5.7 기능 출처 태그와 위협 가정 스위치

- **기능 출처 태그**(새로 추가, 수치 출처 태그 `PUBLIC_VALUE/PUBLIC_FORMULA/SIM_TUNED`와 별개):
  - `PUBLIC_CONFIRMED`: 공개 자료로 탑재 확인
  - `ASSUMED_THREAT`: 확인되지 않았지만 최대 위협 평가를 위해 탑재를 가정함
  - `NOT_EQUIPPED`
- 이번에 붙일 대상:
  - Kh-35U 수동 RF 방위·고각 → `PUBLIC_CONFIRMED`. 근거로 공개 제원의 active/passive radar 표기를 쓰고, `RCS_SOURCES.md`와 같은 형식으로 `PASSIVE_RF_SOURCES.md`에 출처를 적는다. 세부 수치는 SIM_TUNED다.
  - Kh-32 수동 RF 방위·고각 → 공개 근거를 찾아보고, 없으면 `ASSUMED_THREAT`
- **위협 가정 스위치** `THREAT_ASSUMPTION_MODE`: `MAX_THREAT`(기본) / `CONFIRMED_ONLY`
  - `CONFIRMED_ONLY`이면 `ASSUMED_THREAT` 기능이 꺼진다.
  - 디버그 패널과 보고서에 현재 모드와 켜진 가정 기능 목록을 표시한다.
  - 저장 스키마에 필드가 필요하면 추가하고, 기존 저장은 `MAX_THREAT`로 읽는다.

### 5.8 새 SIM_TUNED 상수 (시험 전 고정)

| 상수 | 값 | 근거 |
|---|---|---|
| `cueManeuverAccelSigmaMps2` | 0.3 | 30 kn 수상함이 반경 수백 m로 선회할 때 횡가속 규모(v²/r ≈ 0.45 m/s²) 아래쪽 |
| `basketSigma` | 3.0 | 표준 3σ 게이트 |
| `assumedEmitterHeightM` | 25 | 수상 전투함 주 레이더 장착 높이 규모. σ 8 m로 함께 둔다 |
| `passiveRxSensitivity` 등 수신기 문턱 | 기존 `rangeKm`(Kh-35U 150, Kh-32 250)에서 자함 SPY 기준으로 역산한 값 하나 | 기존 탐지 거리 규모를 보존하기 위함. 역산식을 보고서에 적는다 |
| `vmax` | 18 m/s | U0 값 그대로 |

### 5.9 시험 (단계 2 산출물과 같은 seed로 비교)

1. U0 cue 행렬 × EMCON OFF/ON × `MAX_THREAT`/`CONFIRMED_ONLY`
2. 발사 cue 속도 있음/없음 비교(속도를 줄 수 있는 경로에서). 직진 표적에서 바구니 폭이 줄어드는지 본다.
3. **다중 방사원**: 표적함 + 다른 함 1척이 cue 방위 근처에 있는 배치. 방사원 선택 결과와 오획득을 기록한다.
4. **거리 추정 정확도**: Kh-32(고고도)·Kh-35U(저고도) 비행 중 고각 기반 거리 추정 오차를 사후 truth와 비교한다(진단 전용). Kh-32는 오차가 의미 있게 줄고 Kh-35U는 거의 정보가 없어야 정상이다.
5. 1,590 주 행렬, 오획득 대조군, TRACK-C 이탈 37발 재현, S1 행렬
6. 참고: 60 전투

### 5.10 게이트

- 오획득 증가 0, 이웃 ASM·자함 최초 연관 0, truth 누수 정적 검사 0, 결정성 동일
- TRACK 실패는 B의 세 분류(탐색 구역 밖 / 탐색 구역 안 + 바구니 밖 / 그 외)로 센다. "탐색 구역 안 + 바구니 밖"이 단계 2 대비 늘면 멈춘다.
- 다중 방사원 오유인은 실패로 보지 않고 기록만 한다.

## 6. 마지막 광역 회귀 (1회)

native13, paired friendly, UI, 실제 WebGL observed-world, 헬기·하푼 자연 재현, ISAR, EMCON, 소브레멘니, 배속 1/8/16/64, 저장/복원, RNG·ENV. 기존 부채(`#lockBtn` 14건, `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`)는 따로 기록하고 면제하지 않는다.

## 7. 기록 정정

SEEKER_UNIFY_B `EXPECTED_VALUE_UPDATES.json`은 60 전투의 before를 `SEEKER_UNIFY_A.html` 264/15/37/4로 적었다. 하지만 264/15/37/4는 TRACK-C 역사 수치이고, SEEKER_UNIFY_A 제품은 이미 301/17/1/1이었다. 즉 U0의 60 전투 영향은 0이다. C 문서에 정정 기록을 남긴다. B 파일은 수정하지 않고, C에서 정정 사실만 적는다.

## 8. 산출물

`docs/missile/seeker-unify/C/`:

- `PLAN.md`: 기준 SHA, 단계별 고정 상수와 커밋 해시
- 단계 1: `U2_ACTIVE_EQUIVALENCE.md/.json`
- 단계 2: `BEAM_DEFINITION_AUDIT.md`, `BEAM_FIX_RESULTS.md/.json`
- 단계 3: `LAUNCH_CUE_SOURCES.md`, `PASSIVE_RF_SOURCES.md`, `CUE_A_RESULTS.md/.json`, `RANGE_ESTIMATE_ACCURACY.md/.json`, `MULTI_EMITTER.md/.json`
- `REGRESSION_RESULTS.json`, `EXPECTED_VALUE_UPDATES.json`, `REPORT.md`, `changes.diff`, 빌드·실행 스크립트, 체크섬, README 최신 시험 후보 항목

## 9. 보고 시 꼭 포함할 것

1. 단계별 게이트 결과와 멈춘 지점
2. 빔 정의 감사 결론(단방향/왕복/불명)과 단계 2 적용 여부
3. 단계 1 → 2 → 3 획득 거리·TRACK 변화 표 (Kh-35U·Kh-32, EMCON OFF/ON)
4. `MAX_THREAT` vs `CONFIRMED_ONLY` 차이
5. 고각 기반 거리 추정 오차 (Kh-32 vs Kh-35U)
6. 다중 방사원 오유인 사례
7. 60 전투 참고 집계 (단계별)

## 10. 계속 금지

release·tag 생성, main 직접 커밋, 하푼 시커 수정(U3), TRACK-D·OODA·HP 지표·방어 무장 수정
