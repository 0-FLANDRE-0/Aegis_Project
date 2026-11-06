# Aegis_Project 시커 작업 인계서 (2026-11-04)

이 문서는 새 채팅에서 바로 이어가기 위한 인계서다. 대화 기억보다 이 문서와 레포 실제 내용을 우선한다. 레포 내용과 이 문서가 다르면 **레포가 맞다**. 다른 점은 사용자에게 알린다.

---

## 1. 프로젝트와 작업 방식

- **레포**: GitHub `0-FLANDRE-0/Aegis_Project` (공개). 단일 HTML 함정 방공·교전 시뮬레이터 `Aegis_SIM_v48_WIP_*.html`
  - 게임 소스는 HTML 안의 `data-c55-index="13"` gzip+base64 블록에 들어 있다. 압축 해제하면 약 40 MB JS다.
  - 디코드:
    ```python
    re.search(rb'data-c55-index="13">([^<]+)', raw)
    gzip.decompress(base64.b64decode(m[1]))
    ```
- **역할 분담**
  - 사용자: 방향 결정, 지시서 검토·전달, 플레이 검수, **PR 병합은 직접 함**
  - 리뷰 AI(이 채팅의 Claude): 레포 검토, 결과 해석, 지시서 작성
  - 작업 AI(Codex/GPT): 구현·시험·PR 생성
- **사용자 성향** (지시서·답변에 반영)
  - 코드는 직접 안 읽음. 결과와 방향 위주로 설명할 것
  - 현실 고증 우선, 결과에 맞춘 계수 튜닝 싫어함
  - 설계는 먼저 대화로 정하고, **지시서는 요청받았을 때만** 작성
  - 반말·친구 말투 선호
- **고정 작업 규칙**: 레포 `AEGIS_PROJECT_INSTRUCTIONS.md`
  - Truth 경계: 센서 출력 이후 실제 id·좌표 사용 금지
  - 고정 dt, 격리 RNG, 3D는 표시 전용

## 2. 지시서 관례 (이전 지시서에서 확립)

이전 지시서 원본(사용자 보관): `ASM_SEEKER_A`, `ASM_SEEKER_B`, `SEEKER_UNIFY_A`, `SEEKER_UNIFY_B`(U0~U2), `SEEKER_UNIFY_C`

- **구성**: §0 현재 상태 → §1 기준과 산출물 → 진단 → 수정 원칙 → 검증 → 병합 권한 → 금지 사항
- **기준**: 시작 시 HEAD·HTML SHA를 대조하고 기록
- **커밋 작성자**: `110261808+0-FLANDRE-0@users.noreply.github.com`
- **산출물 위치**: `docs/missile/<작업>/<단계>/`. 보고서 머리말은 `IMPLEMENTED / TESTED / APPROVED / UNRESOLVED / RELEASE`
- **시간 상한**: 단계별로 명시. 넘으면 커밋하고 보고한 뒤 멈춤
- **SIM_TUNED 상수**: 지시서에 적은 것만 만들고, 시험 **전에** 고정 커밋. 결과 보고 재조정 금지
- **보상 튜닝 금지**: 물리 수정으로 성능이 떨어져도 다른 계수로 메우지 않음
- **출처 태그**
  - 수치: `PUBLIC_VALUE / PUBLIC_FORMULA / SIM_TUNED`
  - 기능(SEEKER_UNIFY_C부터): `PUBLIC_CONFIRMED / ASSUMED_THREAT / NOT_EQUIPPED`
- **기대값**: 변경 경로로 설명되는 변화는 사전 승인 갱신(전후 값·원인 기록, 허용 오차 변경 0). 설명 안 되면 멈춤
- **병합**: 최근 지시서는 **PR 생성까지만**, 병합은 사용자. release·tag·main 직접 커밋 금지
- **시험 비용 관리** (사용자가 시험이 너무 오래 걸린다고 두 번 지적함)
  - 광역 회귀(native13, UI, WebGL, 헬기·하푼 재현, ISAR, EMCON, 소브레멘니, 배속, 저장/복원, RNG·ENV)는 **지시서당 1회, 마지막에만**
  - 단계 중간에는 "변경 함수 외 함수 해시 동일 + 그 단계 시험"만
  - 동등성 시험은 **분기 커버리지 대표 케이스(경로당 최대 30) + 함수 해시**로. seed 200개 반복은 하지 않음. 한 페이지에서 배치 실행
  - SEEKER_UNIFY_C에는 아직 "경로당 200 케이스"가 남아 있음. 다음 지시서부터 적용할 것
- **단계 원칙**
  - 코드 이전(리팩터링)은 SHADOW → 비트 동등성 → ACTIVE
  - 동작을 일부러 바꾸는 단계는 동등성 대신 행동 시험
  - 둘은 같은 지시서 안에서도 **단계·커밋을 분리**

## 3. 지금까지의 흐름

| 작업 | 내용 | 상태 |
|---|---|---|
| TRACK-A/B/C | 트랙 신뢰성 | main 병합 |
| ASM_SEEKER_A (PR #65/66) | 이웃 ASM 오획득 원인 확정. 시커 최초 연관에서 발사 cue를 **hard basket**으로 변경. 거리 `max(1200 m, 0.12R)`, 방위 5°, 고각 4° | main 병합 |
| ASM_SEEKER_B | 원거리 획득 실패 진단. 원인은 함정 RCS 과소 | 진단만, 미병합 |
| SEEKER_UNIFY_A (PR #67) | 함정 RCS를 Skolnik 1974 경험식 `52·√f_MHz·D_kt^1.5`로 정비(DDG −15 dB SIM_TUNED). 시커 통합 감사·설계(`UNIFY_AUDIT.md`, `UNIFY_DESIGN.md`, `PROFILE_MIGRATION_TABLE.json`) | main 병합 `ba9bc11` |
| SEEKER_UNIFY_B (PR #68) | U0 cue 바구니 시간 확장, U1 공통 DTO ACTIVE, U2 SHADOW에서 IMPLEMENTATION_DIVERGENCE로 정지 | PR. 병합 여부는 사용자에게 확인 |
| **SEEKER_UNIFY_C** | 단계 1 U2 ACTIVE → 단계 2 빔·LOS 물리 보정 → 단계 3 CUE_A | **작업 완료 보고됨, 검토 대기** |

### SEEKER_UNIFY_B 핵심 결과

- **U0**
  - Kh-35U 100/130 km 전 조건 TRACK 5/5. 이전엔 30 kn 직진이 0~1/5였음
  - EMCON ON 130 km 90° 변침: 0/5 → 5/5. 수동 방위 보정이 끊기면 실패할 거라던 예측이 확인됨
  - 오획득 증가 0, 이웃 ASM 최초 연관 0/320
  - 고정 상수: `assumedMaxTargetSpeedMps=18`, `minAcqRangeFloorM=1500`, `minAcqRangeFrac=0.5`. 방위 상한은 `searchSectorAzDeg`
- **하푼 감사**
  - 100/120 km, 30 kn + 90° 변침에서만 0/5
  - 원인: 4 km 고정 바구니 + 수동 방위 보조 없음
- **기록 오류**
  - B의 `EXPECTED_VALUE_UPDATES.json`은 60 전투 변화(264 → 301)를 U0 탓으로 적음. 실제로 264/15/37/4는 TRACK-C 역사 수치이고, SEEKER_UNIFY_A 제품이 이미 301/17/1/1이었음
  - 즉 U0의 60 전투 영향은 0이다. C 지시서 §7에 정정을 지시함
- **U2 차이 4건과 결정**: 공통층이 양쪽 방식을 다 담고, 프로필이 고르는 방식으로 정리
  - 빔·LOS: ASM은 결합 이득 1회 + LOS 1회, SAM은 tx·rx 각각 + LOS 2회
  - 셀 크기: ASM은 RMS, SAM은 구성원 보존 + 최대값
  - 각도 묶음: ASM은 축별 판정, SAM은 구면 판정
  - 단안 전력 계산의 FP 순서 차이(1e-15): 연산 순서를 기존과 맞춤

## 4. SEEKER_UNIFY_C에서 확정한 설계 (지시서 원문은 사용자 보관)

- 브랜치 `seeker-unify-c`, 제품 `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`, 문서 `docs/missile/seeker-unify/C/`

**단계 1: U2 ACTIVE**
- 위 상위집합 계약으로 비트 동일 전환
- 프로필 옵션은 `provenance:'LEGACY_EQUIVALENCE'`로 표시
- 실제 게임에서도 돌던 U2 SHADOW 래퍼는 제거

**단계 2: 대함 시커 빔·LOS 보정**
- 먼저 `BEAM_DEFINITION_AUDIT.md`로 Kh-35U·Kh-32 빔 반폭이 단방향인지 왕복인지 감사
  - 현재 패턴 `max(.08, cos²·cos²)`는 반폭에서 0이 되므로 반폭이 사실상 영점 폭
- 판정 규칙(사전 고정)
  - 단방향이거나 정의가 불명확하면 → `TX_RX_SEPARATE`로 전환하고 LOS를 왕복 적용
  - 왕복 기준이 문서로 확인되면 → 변경 없음
- 부엽 바닥 0.08은 값 유지, 각 방향에 적용. HOJ·수동 RF는 수신 전용이라 제외
- 획득 거리 감소는 허용. 대신 실패한 셀마다 SNR 수치로 설명해야 하고, 설명 안 되는 실패가 있으면 멈춤

**단계 3: CUE_A (cue 갱신 경로 통합)**
- **발사 cue 출처 감사** `LAUNCH_CUE_SOURCES.md`
  - 현재 발사 측은 위치만 넘김. 항공기 경로는 `lastKnownShip`(truth + 난수)이고 시각이 없음
  - 속도 추정이 없는 경로는 `velocity:null`
- **cue 필터**: 상태 `(x, y, vx, vy)`, 등속 + 기동 가속 잡음, 속력 상한 vmax
  - 속도가 null이면 속도 분산 vmax²로 시작함. U0 성장 방식이 이 필터의 특수한 경우가 됨
  - 기존 `asmApplyPassiveBearingB2` gain 회전과 `asmTargetMemoryDriftB2`를 대체. `_c52InsMemory`는 유지
  - INS 조준점은 필터 예측 위치로 갱신되므로 DR 중심 이동이 유도에도 반영됨
- **수동 RF 재작성**
  - 자함 하드코딩(`aircraft.x()`)과 전역 `emconActive`를 버리고 `electronicPhysicalEmittersF()`를 씀. 함별·장비별 EMCON·손상·대역·출력 반영
  - 세기: 단방향 R⁻²
  - 측정: 방위 + 고각. σ는 SNR이 낮을수록, 그리고 저고각 다중경로에서 커짐
  - 방사원 선택: cue 예측 주변 Mahalanobis 게이트. 다른 함에 끌려가는 오유인은 허용하고 기록만 함
- **수동 거리 추정**
  - 고각을 필터에 직접 측정으로 넣음. 측정 모델에 가정 방사원 높이, 지구 곡률, 4/3 굴절 포함
  - 그래서 Kh-32(고고도)는 거리 정보를 받고 Kh-35U(저고도)는 거의 못 받아야 정상
  - 기존 주석 "MUST NOT infer true range"는 truth 누수 금지라는 뜻으로 재작성
- **바구니**: 필터 공분산을 3σ로 투영
  - 하한은 U0 값 유지: `max(1200, 0.12R)`, `max(1500, 0.5R)`, 방위 5°
  - 상한: 방위 `searchSectorAzDeg`, 고각 4° 유지
- **기능 출처 태그**
  - Kh-35U 수동 RF → `PUBLIC_CONFIRMED`. 근거: 공개 제원 "Inertial, satellite navigation, active/passive radar", GlobalSecurity의 수동 모드 서술, 2024년 Gran-K 실전 보도(35 km에서 방사 방위 추적 후 능동 종말). 세부 수치는 SIM_TUNED
  - Kh-32 → 근거 없으면 `ASSUMED_THREAT`
- **위협 가정 스위치** `THREAT_ASSUMPTION_MODE`: `MAX_THREAT`(기본, 사용자 결정) / `CONFIRMED_ONLY`
- **DL 자리**: `cueUpdate({source:'DL', ...})` 인터페이스만 만듦
- **새 SIM_TUNED**
  - `cueManeuverAccelSigmaMps2=0.3`
  - `basketSigma=3.0`
  - `assumedEmitterHeightM=25 ± 8`
  - 수동 수신 문턱은 기존 `rangeKm`(Kh-35U 150, Kh-32 250)에서 자함 SPY 기준으로 역산
  - `vmax=18`

### 진행 중 보고된 것 (2026-11-03 중단 시점, GPT 요약)

- 단계 1·2 제품 변경 커밋 완료
- 1,590 행렬, "수치 설명 22조건"(빔 보정으로 바뀐 셀 설명으로 추정), S1 100조건, 결정성 완료
- cue 행렬 100/240에서 중단 → 2026-11-04 재개 후 사용자가 **완료됐다고 알림**. 결과는 아직 검토 안 함

## 5. 새 채팅에서 할 일

1. 레포를 받아 `seeker-unify-c` 브랜치(또는 PR)를 확인한다. PR #68 병합 여부도 확인한다.
2. `docs/missile/seeker-unify/C/`의 `REPORT.md`부터 읽는다. 중점 확인 항목:
   - **빔 감사 결론**(단방향/왕복/불명)과 단계 2 적용 여부, Kh-35U·Kh-32 획득 거리 변화
   - CUE_A가 단계 2 대비 "탐색 구역 안 + 바구니 밖" 실패를 늘리지 않았는지
   - 고각 거리 추정 오차가 Kh-32에선 작고 Kh-35U에선 정보가 거의 없는지
   - `MAX_THREAT` vs `CONFIRMED_ONLY` 차이, 다중 방사원 오유인 사례
   - 오획득 증가 0, 이웃 ASM 최초 연관 0, truth 누수 0, 결정성
   - B 기록 오류 정정이 들어갔는지
   - 지시서에 없는 SIM_TUNED 상수가 생기지 않았는지, 보상 튜닝은 없었는지
3. 결과를 사용자에게 쉬운 말로 요약하고, 병합 권고 여부와 남은 결정 사항을 정리한다.

## 6. 이후 로드맵 (사용자 합의)

1. **U3 하푼**: 공통층 이전(분기 커버리지 동등성) → 별도 커밋으로 하푼 **HOJ 추가**(ECCM, 기존 ASM HOJ 훅 재사용 + 하푼 프로필, 행동 시험)
   - 하푼 시간 성장 바구니도 여기서 결정
   - 공개 자료상 하푼의 수동 RF는 **발사 함정 ESM 쪽**이고, 미사일 시커는 능동임. 미사일 쪽 수동 보조는 넣지 않는 방향
2. **U4** SARH 쌍정 어댑터 → **U5** RAM 수동 RF/IR 어댑터 → **U6** 상태기계·연관 공통화
   - RAM 메모: 자함용·타함용 복사본 두 개, 방사 세기가 상대 시커 추적 품질에 따라 바뀌는 이상점
3. **TRACK-D**(링크·소비자 통합) → **HP 지표** → **통합 기준선** → **교전·방어 OODA**

### 보류·참고 항목

- 발사 전 트랙 나이(발사 측 정보 시각) 미반영. 발사 측 트랙 속도 추정 배관은 별도 과제
- 미사일 패시브 RF 현황(C 이전)
  - (1) ASM 중기 방위 보정: 엉성함, C에서 재작성
  - (2) ASM 종말 HOJ: 함별 재머 물리 모델 기반, 양호
  - (3) RAM RF→IR
- 기존 회귀 부채: `#lockBtn` 14건 미실행, `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
