# SEEKER_UNIFY_B 작업 지시서 — U0(cue 바구니 시간 확장) + U1~U2(시커 공통층 1차)

## 0. 기준

- 레포: `0-FLANDRE-0/Aegis_Project`
- 기준 커밋: `main` `ba9bc11` (PR #67 `seeker-unify-a` 병합본)
- 기준 HTML: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html`
  - 22,118,891 bytes / SHA-256 `53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8`
  - 게임 소스는 `data-c55-index="13"` gzip+base64 블록. 빌드는 SEEKER_UNIFY_A의 `build_product.py` 방식(앵커 1회 일치 치환)을 따른다.
- 작업 브랜치: `seeker-unify-b` (새로 만든다)
- 산출 HTML: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html`
- 문서 위치: `docs/missile/seeker-unify/B/`
- 설계 근거: `docs/missile/seeker-unify/A/UNIFY_DESIGN.md`, `UNIFY_AUDIT.md`, `PROFILE_MIGRATION_TABLE.json`
- `AEGIS_PROJECT_INSTRUCTIONS.md`의 Truth 경계, 고정 dt, 격리 RNG 규칙을 그대로 적용한다.

## 1. 공통 규칙 (모든 단계)

1. **계수 변경 금지.** RF/Pd, 잡음, RCS, 빔, 탐색 구역, gimbal, 유도, 추진, 신관, 피해 계수는 손대지 않는다. 이번 지시서에서 새로 만드는 SIM_TUNED 상수는 U0의 3개뿐이며, 시험 실행 **전에** 값을 고정하고 커밋한다. 결과를 보고 되돌려 맞추지 않는다.
2. **허용 오차 확대와 기대값 자동 변경 금지.** 동등성 시험이 깨지면 원인을 기록하고 멈춘다.
3. **Truth 비누수.** cue, 바구니, 연관, EKF, 유도에는 실제 entity id, profile id, 실제 좌표, 실제 속도를 넣지 않는다. `_debug*` 필드는 진단 산출물에서만 쓴다.
4. **RNG.** 무장별 기존 독립 RNG의 seed와 advance 순서를 유지한다. 전역 RNG로 바꾸지 않는다. U0은 난수를 새로 소비하지 않는다.
5. **단계 순서.** 각 단계는 SHADOW → 동등성 확인 → ACTIVE 순서로 진행한다. 앞 단계 게이트를 통과하지 못하면 다음 단계로 넘어가지 않는다.
6. **멈춤 규칙.** 게이트 실패, 시간 상한 초과, 판단이 필요한 분기를 만나면 그 자리에서 멈추고 보고한다. 다른 방법으로 우회하지 않는다.
7. **병합.** PR 생성까지만 한다. `main` 병합, release, tag는 하지 않는다. 병합은 사용자가 직접 한다.
8. **보고 머리말.** 모든 보고서는 `IMPLEMENTED / TESTED / APPROVED / UNRESOLVED / RELEASE` 머리말을 쓴다.

## 2. U0 — cue 바구니 시간 확장 (DL 대비 구조)

### 2.1 문제

`asmSeekerAssociateMeasurements`의 EKF 없음 분기(ASM_SEEKER_A에서 hard basket으로 바뀐 부분)는 바구니 폭이 고정이다.

- 거리: `max(1200 m, cueRange × 0.12)`
- 방위: 5°
- 고각: 4°

SEEKER_UNIFY_A의 `runCueCase` 진단 결과:

| 조건 | Kh-35U TRACK | Kh-32 TRACK |
|---|---|---|
| 60 km 전 조건 | 20/20 | 20/20 |
| 100 km, 30 kn 직진 | 1/5 | 5/5 |
| 100 km, 30 kn + 30° 변침 | 2/5 | 5/5 |
| 130 km, 30 kn 직진 | 0/5 | 5/5 |
| 130 km, 30 kn + 30° 변침 | 0/5 | 5/5 |
| 90° 변침 전부 | 5/5 | 5/5 |

원인 판단:

- 진단 시나리오에서 함 초기 침로는 미사일 진행 방향과 같다. "직진"은 시선 방향으로 그대로 도망가는 경우다.
- 아음속 Kh-35U가 비행하는 동안 표적이 움직인 거리가 거리 바구니 폭(수 km)을 넘는다.
- 방위는 `asmApplyPassiveBearingB2`(SIM_TUNED 수동 RF 방위 보정)가 INS 조준점을 돌려주기 때문에 90° 변침에서도 맞는다. 거리는 설계상 수동 보정이 고치지 않는다.
- 따라서 **EMCON ON이면 방위 보정이 끊겨 90° 변침도 실패할 것으로 예상**한다. U0 시험에서 확인한다.

### 2.2 수정 원칙

실제 대함미사일처럼, 목표 지정 이후 경과 시간 × 표적이 낼 수 있는 최대 속력만큼 탐색 창을 넓힌다. **바구니 중심은 이번에 옮기지 않는다.** 표적 속도로 중심을 예측하는 기능은 별도 작업으로 뺀다.

### 2.3 TargetCue 구조 (DL 대비)

`em.insTgtX/Y`를 바구니가 직접 읽지 않게 하고, cue 접근 함수 하나를 거친다.

```text
TargetCue {
  positionM      // 현재 INS 조준점 (기존 em.insTgtX/Y를 그대로 읽음)
  velocityMps    // 지금은 항상 null. 중심 예측·DL용 자리
  rangeRefTimeS  // 거리 정보가 마지막으로 갱신된 시각 (em.life 기준)
  bearingRefTimeS// 방위 정보가 마지막으로 갱신된 시각
  source         // LAUNCH | PASSIVE_BEARING | SEEKER_MEMORY | DL(예약)
}
```

- 처음 만들 때 `rangeRefTimeS = bearingRefTimeS = 발사 시각`으로 둔다.
- **거리 시계와 방위 시계는 따로 간다.** 갱신 종류마다 줄어드는 차원이 다르기 때문이다.
  - 수동 RF 방위 보정: **방위 시계만** 갱신한다. 거리 시계는 절대 리셋하지 않는다. 보정은 gain 방식이라 한 번에 수렴하지 않으므로, 측정 방위와 cue 방위 차이가 `3 × bearingErrorRad` 이내로 수렴했을 때만 방위 시계를 갱신한다.
  - 시커 트랙 기억(트랙을 잃고 기억 위치로 돌아가는 경로가 있다면): 그 트랙의 마지막 유효 측정 시각으로 두 시계를 갱신한다.
  - DL 위치 갱신: 이번에는 구현하지 않는다. 들어오면 두 시계를 모두 갱신하는 자리로 `source:'DL'`만 예약한다.
  - `asmTargetMemoryDriftB2`의 기억 드리프트: 시계를 건드리지 않는다.
  - `_c52InsMemory` 고정 기억 경로: 기존 동작을 유지하고, 시계는 발사 시각 그대로 둔다.
- **발사 측 표적 데이터 시각**: 현재 `lastKnownShipX/Y`에는 타임스탬프가 없다. 이번에는 발사 시각을 쓰고 `UNRESOLVED`에 "발사 전 트랙 나이 미반영"으로 기록한다. 발사 측에 시각 필드를 새로 만들지 않는다.

### 2.4 바구니 계산

새 SIM_TUNED 상수 3개(`ASM_CUE_BASKET_U0` 프로필, 시험 전 고정):

| 상수 | 값 | 근거 |
|---|---|---|
| `assumedMaxTargetSpeedMps` | 18.0 (약 35 kn) | 수상 전투함 최대 속력의 공개 범위 상단. 실제 표적 속도를 읽지 않는다 |
| `minAcqRangeFloorM` | 1500 | 같은 salvo 이웃 ASM(수백 m)을 계속 배제하기 위한 절대 하한 |
| `minAcqRangeFrac` | 0.5 | 거리 창 아래 끝이 cueRange의 절반 밑으로 내려가지 않게 하는 상대 하한 |

계산(`R = cueRange`):

```text
Ur = assumedMaxTargetSpeedMps × (now − rangeRefTimeS)
Ub = assumedMaxTargetSpeedMps × (now − bearingRefTimeS)
rangeHalf  = max(1200, 0.12·R, Ur)            // 기존 값보다 작아지지 않음
rangeLow   = max(R − rangeHalf, minAcqRangeFloorM, minAcqRangeFrac·R)
rangeHigh  = R + rangeHalf
azHalf     = max(5°, atan(Ub / max(R,1)))
elHalf     = 4°                                // 변경 없음
```

- 바구니 판정은 `rangeLow ≤ m.rangeM ≤ rangeHigh`, `azErr ≤ azHalf`, `elErr ≤ elHalf`로 한다.
- 점수식의 정규화 척도(`cueRangeScaleM` 등)는 **기존 값 그대로** 둔다. 바구니 판정만 바꾼다. 점수식까지 바꾸면 효과가 섞인다.
- EKF가 생긴 뒤의 연관 게이트(`asmSeekerAssociationGates`)는 건드리지 않는다.
- 진단용으로 `s.lastCueBasketU0 = {rangeLowM, rangeHighM, azHalfDeg, rangeAgeS, bearingAgeS, source}`를 기록한다. 이 값을 유도·판단에 쓰지 않는다.

### 2.5 insTgtX/Y 작성자 전수 목록

수정 전에 `em.insTgtX/Y`에 쓰는 모든 위치를 찾아 아래 분류 표를 `INS_CUE_WRITERS.md`로 남긴다. 분류는 `LAUNCH / PASSIVE_BEARING / SEEKER_MEMORY / DRIFT / FIXED_MEMORY / TEST_FIXTURE / 기타`다. `기타`가 나오면 멈추고 보고한다. 이 표가 나중에 DL을 붙일 때 기준이 된다.

### 2.6 하푼 감사 (수정 금지)

하푼은 `seekerSearchBasketM: 4000` 고정 기억 바구니를 쓴다. 아음속 장거리라 같은 문제가 있을 가능성이 높다. U0과 같은 `runCueCase` 방식으로 하푼 60/100/120 km × (15 kn 직진, 30 kn 직진, 30 kn+30°, 30 kn+90°) × 5 seed를 측정만 하고, 결과와 원인 판단을 `HARPOON_BASKET_AUDIT.md`로 남긴다. **하푼 코드는 수정하지 않는다.** 하푼 수정은 U3에서 결정한다.

### 2.7 U0 시험

모든 시험은 기준판과 U0판을 같은 seed, 같은 브라우저 엔진으로 실행한다.

1. **cue 행렬:** Kh-35U·Kh-32 × 60/100/130 km × (15 kn 직진, 30 kn 직진, 30 kn+30°, 30 kn+90°) × 5 seed(729300~729304) × **EMCON OFF/ON**
2. **오획득 대조군:** SEEKER_UNIFY_A의 CHAFF / NO_TARGET / SEA_CLUTTER 행렬 전체
3. **이웃 ASM 재발 방지:** ASM_SEEKER_A의 TRACK-C 이탈 37발 재현. 첫 accepted association이 목표 함정이 아닌 RF 물체인 경우가 0이어야 한다
4. **ASM_SEEKER_A S1 행렬:** Kh-35U 20/45 km × 분리각 0/5/10/20/40° × 10 seed. 자함 최초 선택 0, 기존 TRACK 결과 유지
5. **SEEKER_UNIFY_A 1,590 조건 주 행렬**
6. **광역 회귀:** native13, UI, observed WebGL, paired DDG/CG (SEEKER_UNIFY_A와 같은 구성)
7. **결정성:** 같은 seed 2회 bit-equal, 전역 RNG SHA 동일
8. **참고(게이트 아님):** 60 전투. 기준판 대비 격추·유출·이탈 집계만 보고한다

### 2.8 U0 게이트

- 오획득 증가 0
- 이웃 ASM 최초 연관 0
- 기준판에서 TRACK이던 셀이 U0에서 실패한 경우 0 (셀 하나라도 나오면 멈춤)
- 광역 회귀 신규 실패 0
- Kh-35U 100/130 km 직진·30° 변침 셀 개선 여부는 **보고만** 한다. 개선이 부족해도 상수를 다시 고르지 않는다
- EMCON ON 90° 변침 결과도 보고만 한다

## 3. U1 — DTO·단위·RNG 어댑터 (계산은 기존 함수에 위임)

### 3.1 범위

`UNIFY_DESIGN.md`의 공통 경계를 **자료 형식만** 먼저 만든다. 계산은 전부 기존 함수가 그대로 한다.

- `EchoSample`, `ResolvedCell`, `Measurement`(값+공분산), `TargetCue`(U0 구조를 공식 DTO로 승격), `SeekerEstimate {valid, mode, position?, velocity?, bearing?, covariance, ageS, quality}`
- 관측 차원 enum: `ACTIVE_MONOSTATIC_4D`, `SARH_BISTATIC_4D`, `PASSIVE_RF_2D`, `PASSIVE_IR_2D`
- 단위는 `PROFILE_MIGRATION_TABLE.json`의 `commonUnits`(m, rad, m/s, m², SI 제곱 공분산)를 따른다
- 프로필 이전은 같은 표의 `mappings`대로 **읽기 전용 view**를 만든다. 원본 프로필 객체는 바꾸지 않는다
- RNG 어댑터: 각 무장의 기존 RNG 핸들을 감싸기만 하고, seed와 advance 순서를 그대로 넘긴다

### 3.2 대상 무장

Kh-32, Kh-35U, RGM-84D Harpoon, SM-2/ESSM Block 1 SARH, ESSM Block 2 / SM-6 Block IA ARH, RAM Block 1A

- SARH 쌍정 경로와 RAM 수동 RF/IR은 `HARDWARE_DIFFERENCE`다. DTO는 맞추되 계산을 단안 ARH로 합치지 않는다
- 하푼의 Pd(`1-exp(-snr/7)`)는 어댑터로 감싸기만 하고 바꾸지 않는다

### 3.3 U1 시험과 게이트

- 무장별 고정 반사체 장면 200 측정에서 raw echo → composite → measurement → EKF event가 기존 경로와 **bit-equal**
- 정보 비누수 정적 검사: DTO 출력에 entity id, profile id, truth 좌표가 없음
- 광역 회귀 신규 실패 0, 결정성 bit-equal
- bit-equal이면 ACTIVE로 전환한다. 하나라도 다르면 멈춘다

## 4. U2 — WIP22 ASM + SAM ARH 에코·셀 공통화

### 4.1 범위

능동 단안 경로 두 개만 공통 `synthesizeEchoes` / `resolveCells`로 묶는다.

- 대상: WIP22 Kh-32/Kh-35U(`asmSeekerVisibleRfReturns`, `asmSeekerCompositeReturns`, `asmSeekerEchoMeasurement`)와 ESSM B2 / SM-6 ARH(`_arhNormalizedMonostaticPower`, `_arhClusterEchoes`, `buildEssmArhEchoPool` 계열)
- 신호 정규화: 두 경로 모두 R⁻⁴ 단안이다. 공통 함수는 프로필의 `sensitivity`(referenceRange/referenceRcs/referenceSnr)로 같은 값을 내야 한다
- 분해능·합성: 전력 가중 centroid/extent를 한 번만 적용하는 `resolveCells(profile)`로 묶는다. 무장별 unresolved range/angle/Doppler는 프로필 값을 그대로 쓴다
- 제외: 하푼(U3), SARH(U4), RAM(U5), 상태기계·연관(U6). U0 바구니도 그대로 둔다

### 4.2 진행

1. **SHADOW:** 기존 경로가 계속 실제 결과를 내고, 공통 경로는 옆에서 같은 입력으로 계산만 한다. 틱마다 SNR, 측정값, 공분산, 셀 구성원을 비교해 기록한다
2. **차이 분류:** 차이가 나면 아래 셋 중 하나로 분류한다
   - `FP_ORDER`: 부동소수 연산 순서 차이. 연산 순서를 기존과 맞춰서 없앤다
   - `IMPLEMENTATION_DIVERGENCE`: 두 경로의 알고리즘이 실제로 다름. **어느 쪽으로 맞출지 작업자가 정하지 않는다.** 차이 내용, 영향 받는 조건, 각 안의 물리적 근거를 정리해 보고하고 멈춘다
   - `HARDWARE_DIFFERENCE`: 센서 하드웨어 차이. 프로필 값으로 분리한다
3. **동등성:** 차이가 0이 된 구성요소만 ACTIVE로 전환한다. 일부만 같으면 그 부분만 전환하고 나머지는 SHADOW로 남긴다

### 4.3 U2 시험과 게이트

- SEEKER_UNIFY_A의 ESSM B2 / SM-6 air·surface × AIRCRAFT/ASM/SEA_CLUTTER/CHAFF × 10~50 km 행렬
- U0 cue 행렬 전체(EMCON OFF/ON 포함)
- 오획득 대조군, 이웃 ASM 재현, 1,590 주 행렬, 광역 회귀, 결정성
- 게이트: ACTIVE로 바꾼 구성요소의 결과가 기준(U1 산출본)과 bit-equal. 신규 실패 0. 오획득 증가 0

## 5. 시간 상한

| 단계 | 상한 |
|---|---|
| U0 (2.6 하푼 감사 포함) | 4시간 |
| U1 | 4시간 |
| U2 | 6시간 |

상한을 넘기면 그 시점 상태를 커밋하고 보고한다.

## 6. 산출물

`docs/missile/seeker-unify/B/`에:

- `PLAN.md`: 기준 SHA, 시험 전에 고정한 U0 상수 3개와 커밋 해시
- `INS_CUE_WRITERS.md`, `HARPOON_BASKET_AUDIT.md`
- `U0_RESULTS.md`(+json): cue 행렬 기준/U0 비교, EMCON OFF/ON, 대조군, 이웃 ASM, S1
- `U1_EQUIVALENCE.md`(+json)
- `U2_SHADOW_DIFF.md`(+json): 차이 분류 표, ACTIVE 전환한 구성요소 목록
- `REPORT.md`: 단계별 상태, 게이트 결과, UNRESOLVED 목록
- `changes.diff`, 빌드·실행 스크립트, 체크섬
- README 최신 시험 후보 항목 추가

## 7. 보고 시 꼭 포함할 것

1. U0 전후 Kh-35U 100/130 km 표 (EMCON OFF/ON 따로)
2. U0에서 바구니가 실제로 얼마나 커졌는지: 시커 획득 시점의 `rangeLow/High`, `azHalf` 분포
3. 수동 방위 보정의 방위 시계 갱신 횟수와 수렴 판정 통과율
4. 하푼 감사 결과와 원인 판단
5. U2에서 `IMPLEMENTATION_DIVERGENCE`로 분류된 항목 전부 (사용자 판단 대기)
6. 60 전투 참고 집계
