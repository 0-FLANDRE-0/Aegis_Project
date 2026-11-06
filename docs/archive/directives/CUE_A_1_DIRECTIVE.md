# CUE_A-1 지시서: cue 필터 잡음 모델 정비 → 중기 수동 RF 방사원·대역 정비

## 0. 현재 상태 (이 문서가 최신 기준)

- SEEKER_UNIFY_C(PR #69): U2 ACTIVE, 대함 시커 빔·LOS 왕복 보정, CUE_A. 게이트는 모두 통과했다.
  - 브랜치 HEAD `4faeb4e0`, 제품 `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html` SHA-256 `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`
  - 단계 2 제품(빔 보정까지만): 커밋 `cd0d6868`의 같은 파일, SHA-256 `dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec`
- 리뷰에서 확인된 문제:
  1. **cue 필터 기동 잡음이 틱 크기에 묶여 있다.** 이산 백색가속 Q를 매 틱(`SIM_FIXED_DT`=1/60 s) 더해서 위치 분산이 대략 `σ²·dt·T³/3`이다. 180 s 뒤 약 54 m다. `CUE_A_RESULTS.md`의 속도 표(4.9 km)는 180 s를 한 번에 예측한 값이라 실제 게임 동작이 아니다. 원인은 C 지시서가 잡음 모델 형태를 정하지 않은 것이다.
  2. **속도 미상 cue의 바구니가 물리적 최대의 약 3배다.** 속도 1σ=vmax로 두고 3σ 바구니를 잡아서 반폭이 3·vmax·t가 된다. 이것도 C 지시서 설계 탓이다.
  3. **vmax 제한이 속도 추정값만 자르고 속도 공분산은 자르지 않는다.**
  4. **수동 RF 후보에 모든 방사원이 들어간다.** 미사일 시커(아군 ESSM/SM-6 ARH 포함), 항공기 레이더, 함정 재머, 눌카까지 다 들어가고 게이트 거리로만 고른다. 함정 재머와 눌카는 둘 다 `JAMMER`/`RF INTERFERENCE`라서 구분하려면 truth가 필요하다.
  5. **수동 RF에 대역 개념이 없다.** 회전 레이더 송신 패턴은 35° 가우시안이고 0.2 s 순간 샘플링이라 주빔·부엽 구분이 의미가 없다.
  6. **C 단계 2에서 대함 시커 거리 하한이 바뀌었는데 보고가 없다.** `max(.5,R)`가 `max(.20,R)`로 바뀌었다. SAM 식을 그대로 가져와서 생긴 일이다.
  7. **paired DDG_119·CG_52 raid 기대값 변경 원인이 CUE_A로만 적혀 있다.** 광역 회귀가 B → C 최종 1회 비교라 단계 2(빔) 영향이 분리되지 않았다.
- 사용자 결정(이 문서로 확정):
  - 위협 가정 기본값 `MAX_THREAT`. **모든 행렬·전투·회귀는 MAX_THREAT로만 시험한다.** `CONFIRMED_ONLY`는 정적 검사 + 장면 1~2개만 하고 성능 수치는 `UNVERIFIED`로 표시한다.
  - 기동 잡음은 Singer 모델, τ=60 s. 속도 미상 시 축별 σ=vmax/2. 바구니 상한 `vmax×t + 3σ_INS`. 속도 불확실성에도 상한을 둔다.
  - 중기 수동 RF는 **함정 레이더 family만** 받는다. 재머(함정·눌카)는 HOJ 채널에서만 처리한다.
  - 대역 감도 기준은 기존 SPY 150/250 km 역산값을 그대로 쓴다. 새 기준점은 만들지 않는다.
  - 0.2 km 하한은 대함 시커만 0.5 km로 원복한다.
  - Kh-32 60 km 명중 0 조사는 이번 범위가 아니다.

## 1. 기준과 산출물

- **기준**: PR #69가 main에 병합됐으면 그 main HEAD, 아니면 `seeker-unify-c` `4faeb4e0`. 시작 시 HEAD·HTML SHA를 대조하고 실제 값을 기록한다.
- **작업 브랜치**: `cue-a-1`
- **커밋 작성자**: `110261808+0-FLANDRE-0@users.noreply.github.com`
- **산출 HTML**: `Aegis_SIM_v48_WIP_CUE_A_1.html`
- **문서 위치**: `docs/missile/cue-a-1/`
- 보고서 맨 위에 `IMPLEMENTED / TESTED / APPROVED / UNRESOLVED / RELEASE`를 표시한다.
- `AEGIS_PROJECT_INSTRUCTIONS.md`의 Truth 경계, 고정 dt, 격리 RNG 규칙을 그대로 적용한다.
- **시간 상한**: 단계 0 **1시간**, 단계 1 **3시간**, 단계 2 **4시간**, 마지막 회귀 **1시간**. 넘으면 그 시점 상태를 커밋·push하고 보고한 뒤 멈춘다.
- **push 의무**: 단계가 끝날 때마다 원격에 push한다. 리뷰 AI는 로컬 커밋을 볼 수 없다. C에서 로컬 커밋을 잃은 적이 있다.

## 2. 공통 규칙

1. **새 SIM_TUNED 상수는 §6 표에 적힌 것만** 만든다. 해당 단계 시험 실행 **전에** 고정 커밋한다. 결과를 보고 다시 고르지 않는다.
2. **보상 튜닝 금지.** 획득·TRACK이 줄어도 빔폭·감도·RCS·문턱·탐색 구역·게이트·바구니 하한을 바꾸지 않는다. 대신 실패한 셀마다 원인을 수치로 설명한다.
3. **Truth 비누수.** cue 필터, 바구니, 연관, EKF, 유도, 수동 RF **선택 로직**은 관측 가능한 값만 읽는다: `emitterClass`, `family`, 대역, 수신 세기·SNR, 각도. `owner`, `ship`, `entityId`, 방사원 좌표는 측정 합성 내부에서만 쓴다. 정적 검사로 확인한다.
4. **RNG.** 무장별 기존 격리 해시 스트림(`_samB1HashSigned`)과 salt를 유지한다. 새 salt가 필요하면 값과 사용 순서를 기록한다.
5. **시험 비용**
   - 위협 가정: MAX_THREAT만 쓴다(§0).
   - 단계 중간: 변경 함수 외 함수 해시 동일 + 그 단계 시험만 한다.
   - 광역 회귀: **지시서 전체에서 1회, 맨 마지막에만** 한다.
   - 동등성 시험: **분기 커버리지 대표 케이스(경로당 최대 30) + 함수 해시**. seed 200개 반복은 금지한다. 한 페이지에서 배치 실행하고 케이스마다 페이지를 다시 띄우지 않는다.
   - 60 전투: 참고용이고 게이트가 아니다. 마지막에 1회만 돌린다.
6. **기대값.** 변경 경로로 설명되는 변화는 사전 승인 갱신이다. 전후 값, 원인, **어느 단계 탓인지**를 기록하고 허용 오차 변경은 0이다. 설명되지 않으면 멈춘다.
7. **멈춤 규칙.** 게이트 실패, 시간 상한 초과, 이 문서가 정하지 않은 판단 분기를 만나면 멈추고 보고한다. 우회하지 않는다.
8. **병합.** PR 생성까지만 한다. main 병합·release·tag·main 직접 커밋은 하지 않는다.
9. 단계 1과 단계 2는 둘 다 Kh-35U 획득을 바꾼다. **단계·커밋을 분리하고, 각 단계는 직전 단계 산출물과 같은 seed로 비교한다.**

## 3. 단계 0 — paired 기대값 원인 분리 (코드 변경 없음)

- 같은 paired 시험 하네스로 `DDG_119_LATE_FLIGHT_IIA raid`, `CG_52_LATE_TICONDEROGA raid` 두 시나리오를 돌린다. 대상 제품은 세 개다.
  - B 제품 `b8551e5a…`
  - C 단계 2 제품 `dca6d886…`
  - C 최종 제품 `efba68ca…`
- C의 `PAIRED_RAID_EXPECTATION_UPDATES.json`에 있는 8개 변경 항목 각각이 B→단계 2와 단계 2→최종 중 어디서 바뀌었는지 기록한다.
- 산출물: `PAIRED_STAGE_ATTRIBUTION.md/.json`
- C 파일은 수정하지 않는다. 정정 사실만 이 문서에 적는다.
- 어느 쪽 변경 경로로도 설명되지 않는 항목이 있으면 멈춘다.

## 4. 단계 1 — cue 필터 정비 + 거리 하한 원복

### 4.1 대함 시커 거리 하한 원복 (커밋 1a)

- `seekerSynthesizeMonostaticPowerU2`의 `TX_RX_SEPARATE` 분기에서 거리 하한을 프로필 옵션 `rangeFloorKm`으로 뺀다.
  - `ASM_WIP22`: 0.5
  - `SAM_ARH`: 0.20
  - 두 값 모두 `provenance:'LEGACY_EQUIVALENCE'`
- 시험(대표 케이스, 경로당 최대 30):
  - SAM 경로는 C 최종과 비트 동일
  - ASM 경로는 R ≥ 0.5 km에서 비트 동일, 차이는 R < 0.5 km에서만
- 게이트: 위 조건 + 변경 함수 외 함수 해시 동일

### 4.2 Singer 기동 모델 (커밋 1b)

**상태**: 축별 `[위치, 속도, 가속도]`, 수평 x·y 두 축. 상태 벡터는 `(px, py, vx, vy, ax, ay)`. 고도는 기존 조준 고도를 고정으로 쓴다.

**연속시간 모델**(축별):

```text
ṗ = v,  v̇ = a,  ȧ = −a/τ + w(t)
w: 백색잡음, 스펙트럼 밀도 q = 2σa²/τ   (정상상태 가속도 표준편차 = σa)
σa = cueManeuverAccelSigmaMps2 = 0.3,  τ = cueManeuverTauS = 60
```

**이산화**: 예측 간격 Δt마다 **정확 이산화**를 쓴다. 테일러 근사와 "틱마다 고정 Q 더하기"는 금지한다.

```text
A = [[0,1,0],[0,0,1],[0,0,−1/τ]],  G = [0,0,1]ᵀ
F = exp(AΔt)
Q = ∫₀^Δt exp(As)·G·q·Gᵀ·exp(As)ᵀ ds
```

- Singer(1970) 닫힌 식이나 Van Loan 방법 중 하나로 계산한다. 쓴 방법을 보고서에 적는다.
- 고정 dt라 F·Q는 미리 계산해 둬도 된다.

**초기화**
- 위치: 발사 cue 위치, 분산은 발사 INS 오차 σ_INS²(기존 값)
- 속도: 발사 측 속도가 있으면 그 값·공분산. `null`이면 **속도 0, 축별 σ = vmax/2 = 9 m/s**
- 가속도: 0, 축별 분산 σa²

**상한 (예측과 갱신 뒤마다 적용)**
- 속도 추정값: 크기 > vmax면 vmax로 축소한다(기존과 같음).
- 속도 공분산: 축마다 `P[v,v] > (vmax/2)²`이면 `k = (vmax/2)/√P[v,v]`로 그 속도 행과 열을 곱해서 줄인다. 대각 성분은 k²배가 된다. 이렇게 하면 양의 준정부호가 유지된다.

**바구니**(`asmCueBasketU0`)
- R = cue까지 거리, Rh = 수평 거리
- σ_range, σ_cross = 위치 공분산을 거리·횡방향으로 투영한 값

```text
capM       = vmax × (now − capRefTimeS) + 3 × capRefSigmaM
rangeHalf  = max(1200, 0.12·R, min(3·σ_range, capM))
rangeLow   = max(R − rangeHalf, 1500, 0.5·R)
rangeHigh  = R + rangeHalf
azHalf     = min(searchSectorAz, max(5°, min(atan2(3·σ_cross, Rh), atan2(capM, Rh))))
elHalf     = 4°   (변경 없음)
```

- `capRefTimeS`·`capRefSigmaM`은 마지막 **절대 위치 정보**의 시각과 위치 σ다. 처음에는 발사 시각과 σ_INS다.
  - DL 위치 갱신 때만 바꾼다.
  - 수동 RF 각도 갱신으로는 바꾸지 않는다. 각도는 절대 위치를 주지 않기 때문이다.
- 우선순위: **하한이 상한보다 우선한다.** 발사 직후 capM이 작아도 1200 m / 0.12R / 5° 아래로 내려가지 않는다.
- `basketSigma`=3, 하한, `searchSectorAz` 상한은 기존 값 그대로다.

**기존 경로**
- `_c52InsMemory`는 그대로 둔다.
- DL `cueUpdate` 인터페이스는 유지하되 연결하지 않는다. 상태가 6차원이 돼도 측정 H는 위치·속도 성분만 본다.

### 4.3 단계 1 시험 (MAX_THREAT)

1. **dt 독립성**(진단 함수, 상한을 끈 순수 예측):
   - σ_p0=300 m, σ_v0=0, σ_a0=0.3, 180 s
     - 한 번 예측: 위치 σ 3529.28 m (리뷰 AI 계산값)
     - 1/60 s × 10800회 예측: 같은 값
     - 상대 오차 1e-6 이내
   - σ_v0=9 m/s도 같은 조건으로: 3883.33 m
   - 두 값 모두 재현해야 한다.
2. **속도 표 재작성**: Kh-35U·Kh-32 × 60/120/180 s × 속도 null/known. **반드시 틱 단위로 돌린다.** 위치 σ, 속도 σ, capM, 실제 바구니 반폭을 적고, 하한·3σ·상한 중 어느 것이 바구니를 정했는지 표시한다.
3. **U0 cue 행렬**: Kh-35U·Kh-32 × 60/100/130 km × (15 kn 직진, 30 kn 직진, 30 kn+30°, 30 kn+90°) × 5 seed × EMCON OFF/ON. 240케이스. C 최종과 같은 seed로 비교한다. TRACK, 명중, B의 실패 세 분류를 기록한다.
4. **오획득 대조군**: CHAFF / NO_TARGET / SEA_CLUTTER (1,590 행렬 중 ASM 대조군 행만)
5. **TRACK-C 이탈 37발 재현**, **ASM_SEEKER_A S1 행렬**

### 4.4 단계 1 게이트

- dt 독립성 통과
- 오획득 증가 0, 이웃 ASM·자함 최초 연관 0, truth 누수 정적 검사 0, 결정성 동일
- "탐색 구역 안 + 바구니 밖" 실패가 C 최종 대비 늘면 멈춘다.
  - 예외: 사후 truth로 봤을 때 **발사 INS 오차가 3σ_INS를 넘은** 경우는 기록만 한다. 상한 식이 3σ_INS를 쓰기 때문이다.
- 획득 변화가 생긴 셀마다 원인을 바구니 반폭 전후 수치로 설명한다.

## 5. 단계 2 — 중기 수동 RF 정비

### 5.1 방사원 선택 (truth 안전)

- 후보는 **family 허용 목록**으로만 거른다. 이름은 `ASM_MIDCOURSE_PASSIVE_FAMILIES`이고, 분류 규칙이라 수치 상수가 아니다.
  - `SHIP SEARCH RADAR`(SPY), `SURFACE SEARCH RADAR`(SPQ-9B), `NAVIGATION RADAR`(BridgeMaster)
- 제외 대상: `ACTIVE_SEEKER` 전부(적·아군 미사일 시커), `AIR SEARCH RADAR`(항공기), `JAMMER` 전부(함정 재머·눌카)
- 재머는 기존 HOJ 경로(`electronicHojF`, `asmUpdateHojTrack`)에서만 처리한다. 그 경로는 **수정하지 않는다.**
- 선택 로직은 §2-3의 관측 가능한 값만 읽는다. 게이트 거리가 가장 작은 후보를 고른다(기존과 같음).

### 5.2 대역 게이트

- **방사원 주파수**: 프로필에 `frequencyMHz`가 있으면 그 값을 쓴다(예: BridgeMaster 3050 MHz). 없으면 대역 태그 중심값을 쓴다: `S` → 3.0 GHz, `IJ` → 10.0 GHz.
- **수신기 수신 범위**(무장 수동 RF 프로필에 추가):
  - MAX_THREAT: 2~18 GHz. 기능 태그 `ASSUMED_THREAT`
  - CONFIRMED_ONLY: 8~12 GHz(능동 시커와 같은 X대역). 기능 태그 `SIM_TUNED`
  - 범위 밖 주파수는 수신하지 않는다.
- Kh-32 수동 RF는 기존대로 `ASSUMED_THREAT`이다. CONFIRMED_ONLY에서는 전체가 꺼진다.
- **감도는 기존 역산값을 그대로 쓴다.** Kh-35U `7.07355302630646e-11 W`, Kh-32 `2.5464790894703257e-11 W`. 두 모드 공통이다.
- 수신 전력식은 고정 유효 개구면(0.008 m²)이라 대역 때문에 바뀌지 않는다. 그대로 둔다.

### 5.3 파장 비례 정확도·수신 빔폭

- 기준 주파수는 `f_ref = 10 GHz`다. 기존 `bearingErrorRad`와 시커 탐색 빔 반폭을 이 X대역 값으로 본다.
- `k = f_ref / f_emitter` (파장비)
  - 방위 σ = `bearingErrorRad × k × √(1 + 1/max(1,SNR))`
  - 고각 σ = 방위 σ × 기존 다중경로 항 `(1 + 0.75·exp(−|el|/2°))`
  - 수동 수신 패턴 반폭 = 시커 탐색 빔 반폭 × k. 패턴 형태 `cos²`와 부엽 바닥 0.08은 그대로다.
- 예: SPY 3.0 GHz → k = 3.33.

### 5.4 회전 레이더 주빔 훑음 판정

- 대상: `beamAz`가 있는 방사원(SPQ-9B, BridgeMaster). SPQ-9B는 기존 `double`(양면)을 유지한다.
- 송신 패턴: −3 dB 전폭 θ3 가우시안 `g = max(floor, exp(−4·ln2·(off/θ3)²))`
  - θ3: **기존 코드 값을 쓴다.** BridgeMaster `horizontalBeamwidthDeg: 2`, SPQ-9B는 기존 관측 모델이 쓰는 0.6°.
  - θ3 출처를 확인해 태그를 붙인다. 공개 자료가 있으면 `PUBLIC_VALUE`, 없으면 기존 값 `SIM_TUNED`(새 값 아님).
  - floor: 기존 0.015 유지
- 판정: 샘플 간격(직전 샘플 시각부터 현재까지, 0.2 s) 동안 회전자가 미사일 방향을 ±θ3/2 안으로 **훑고 지나갔으면** 주빔 수신으로 보고 g=1을 쓴다. 아니면 그 구간 최대 부엽 이득을 쓴다.
  - 회전 각속도는 기존 회전자 상태(rpm 30)를 **합성 내부에서만** 읽는다.
- SPY는 기존대로 `beamAz:null`(평균값)이다.

### 5.5 단계 2 시험 (MAX_THREAT, 단계 1 산출물과 같은 seed)

1. **장비별 수신 시험**: 자함 DDG를 대상으로 Kh-35U·Kh-32 × 60/100/130 km × 5 seed에서 아래 다섯 조건을 비교한다.
   - (a) 전부 ON
   - (b) SPY만 OFF
   - (c) SPQ-9B만 OFF
   - (d) NAV만 OFF
   - (e) 전부 OFF(EMCON)
   - 장비별 EMCON은 아직 없으므로 기존 장비 활성 플래그(`o.enabled`)로 끈다.
   - 기록: 수신 여부, 선택된 family, 방위·고각 오차(사후 truth), 수신 간격
2. **혼입 시험**: cue 방위 근처에 아군 ESSM/SM-6 ARH(능동 시커 켜짐), 항공기 레이더, 활성 눌카, 함정 재머를 각각 배치한다. **선택 횟수 0**이어야 한다. 눌카·재머의 HOJ 동작은 C 최종과 같아야 한다.
3. U0 cue 행렬 240, C의 다중 방사원 케이스(MAX_THREAT만), 고각 거리 추정 정확도(Kh-32·Kh-35U 각 15케이스)
4. 오획득 대조군, TRACK-C 37발, S1
5. **CONFIRMED_ONLY**:
   - 정적 검사: Kh-32 수동 RF 꺼짐, Kh-35U는 X대역만 수신해서 SPY·NAV 불수신
   - 장면 1~2개
   - 성능 수치는 `UNVERIFIED`

### 5.6 단계 2 게이트

- 오획득 증가 0, 이웃 ASM·자함 최초 연관 0, 결정성 동일
- 혼입 시험 선택 0. 선택 로직의 truth 필드 참조 0(정적 검사)
- "탐색 구역 안 + 바구니 밖" 실패가 단계 1 대비 늘면 멈춘다.
- 획득·TRACK이 바뀐 셀마다 원인을 수신 family·SNR·σ 전후 수치로 설명한다.

## 6. 새 상수 (시험 전 고정)

| 상수 | 값 | 출처 태그 | 근거 |
|---|---|---|---|
| `cueManeuverTauS` | 60 s | SIM_TUNED | 수상함 기동이 지속되는 시간 규모. 정상 가속 σa=0.3(기존)과 함께 Singer 모델 구성 |
| 속도 미상 초기 σ / 속도 공분산 상한 | 축별 vmax/2 = 9 m/s | SIM_TUNED | 반경 vmax 원 안에 고르게 분포할 때의 축별 표준편차 |
| 바구니 상한 | `vmax×Δt + 3σ_ref` | PUBLIC_FORMULA | 물리적 최대 이동거리 + 초기 위치 오차 3σ |
| MAX_THREAT 수동 수신 범위 | 2~18 GHz | 기능 ASSUMED_THREAT | 광대역 ESM 수신기 일반 범위 |
| CONFIRMED_ONLY 수동 수신 범위 | 8~12 GHz | SIM_TUNED | 능동 시커와 같은 X대역 |
| 대역 태그 중심 주파수 | S 3.0 GHz, IJ 10.0 GHz | SIM_TUNED(대역 정의 안의 선택) | IEEE 대역 정의의 중심. 장비 주파수가 있으면 그 값 우선 |
| 정확도 기준 주파수 | 10 GHz | SIM_TUNED | 기존 `bearingErrorRad`와 빔 반폭을 X대역 값으로 해석 |

이 표에 없는 새 수치는 만들지 않는다. 기존 θ3·부엽·rpm은 새 상수가 아니다. 출처 태그만 확인한다.

## 7. 마지막 광역 회귀 (1회)

- 대상: native13, paired friendly, UI, 실제 WebGL observed-world, 헬기·하푼 자연 재현, ISAR, EMCON, 소브레멘니, 배속 1/8/16/64, 저장/복원, RNG·ENV. 모두 MAX_THREAT로 돌린다.
- 기존 부채는 따로 기록하고 면제하지 않는다: `#lockBtn` 14건, `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
- 참고: 60 전투(C 최종 대비)
- 기대값 변경은 단계 1/단계 2 중 어느 쪽 탓인지 적는다. 갈리지 않으면 해당 시나리오만 단계 1 산출물로 한 번 더 돌린다.
- 회귀 뒤 제품을 바꿨으면 바뀐 부분과 재시험 범위를 적는다.

## 8. 산출물

`docs/missile/cue-a-1/`:

- `PLAN.md`: 기준 SHA, 단계별 고정 상수·커밋 해시
- 단계 0: `PAIRED_STAGE_ATTRIBUTION.md/.json`
- 단계 1: `CUE_FILTER_SINGER.md/.json`(dt 독립성, 속도 표, cue 행렬, 대조군)
- 단계 2: `PASSIVE_RF_EMITTER_BAND.md/.json`(장비별 수신, 혼입, 대역·σ, 회전 레이더), `PASSIVE_RF_SOURCES.md` 갱신(θ3 출처)
- `REGRESSION_RESULTS.json`, `EXPECTED_VALUE_UPDATES.json`, `REPORT.md`, `changes.diff`, 빌드·실행 스크립트, 체크섬, README 최신 시험 후보 항목

## 9. 보고 시 꼭 포함할 것

1. 단계별 게이트 결과와 멈춘 지점
2. paired 8건의 단계별 원인
3. dt 독립성 결과와 틱 단위 속도 표. 바구니를 정한 항(하한/3σ/상한) 분포
4. 단계 C 최종 → 1 → 2의 Kh-35U·Kh-32 TRACK·명중 표 (EMCON OFF/ON)
5. 장비별 수신 결과: 어떤 조건에서 어떤 family로 수신했는지, 방위 오차, 회전 레이더 수신 간격
6. 혼입 시험 결과
7. CONFIRMED_ONLY 정적 검사 결과 (성능 UNVERIFIED)
8. 60 전투 참고 집계

## 10. 금지

- release·tag 생성, main 직접 커밋
- 하푼 시커 수정(U3)
- HOJ 경로 수정
- `electronicPhysicalEmittersF` 하드코딩 범용화(EMITTER_A). 이번에는 읽기만 하고, 필요한 관측 필드 추가만 허용한다.
- 장비별 EMCON UI(EMCON_B)
- Kh-32 60 km 조사
- TRACK-D·OODA·HP 지표·방어 무장 수정
- 이번에 고정한 상수와 기존 SIM_TUNED 값의 재조정
