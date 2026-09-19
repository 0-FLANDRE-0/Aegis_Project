# AEGIS v48 WIP12E 인계서 — 구획 기반 폭압·폭풍·배출 종말효과

## 0. 이 문서의 용도

이 문서는 새 채팅에서 WIP12E를 바로 착수하기 위한 상세 인계서다. 새 작업자는 대화 기억이나 과거에 전달된 임시 HTML보다 GitHub `main`과 아래 기준 파일을 먼저 확인한다.

- 저장소: `0-FLANDRE-0/Aegis_Project`
- WIP12E 시작 기준: WIP12D가 병합된 `main`
- 기준 시뮬레이터: `Aegis_SIM_v48_WIP12D.html`
- 기준 HTML SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 기준 HTML 크기: `3,058,349 bytes`
- WIP12D 상태 문서: `AEGIS_PLAN_STATUS_v48_WIP12D.md`
- WIP12D 설계 문서: `docs/WIP12D_KH32_RESIDUAL_OVERPENETRATION.md`
- 공통 종말탄도 설계: `docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`
- 프로젝트 고정 규칙: `AEGIS_PROJECT_INSTRUCTIONS.md`

이 문서는 구현 완료 보고가 아니라 **WIP12E의 범위·권위·자료구조·검증 계약을 고정한 착수 문서**다. WIP12E 코드는 아직 없다.

## 1. 사용자 요구와 문제 정의

사용자가 직접 확인한 핵심 문제는 다음과 같다.

1. WIP12D의 폭발 형상은 기존 구형 표시보다 나아졌지만, 실제 결과는 여전히 `damage = 191` 같은 legacy scalar 예산을 head/peak/tail 위치에 재분배하는 수준이다.
2. 큰 탄두의 내부 폭발이 구획 벽, 갑판, 문, 파괴구, 외부 개구부와 상호작용하는 압력파처럼 느껴지지 않는다.
3. “폭발이 더 커 보이게” 단순히 반경이나 구를 키우는 것이 아니라, 폭압·반사압·충격량·폭풍·고온가스·배출 jet을 서로 구분한 현실적인 효과가 필요하다.
4. WIP12D에서 이미 구현한 관통 경로, 잔존체, 반대편 외판 구멍, 침수, 드문 취약장비 발화는 보존해야 한다.
5. 내부 시각화는 명시적으로 `내부 구조` 보기를 켰을 때만 자세히 표시하고, 기본 외부 화면을 복잡하게 만들거나 렉을 유발하면 안 된다.

따라서 WIP12E의 한 줄 정의는 다음과 같다.

> WIP12E는 WIP12D의 scalar blast 분배를 구획·portal·파괴구를 따라 전파되는 bounded pressure/impulse solver로 교체하고, 그 결과를 구조·장비·승조원·화재·시각화 consumer에 중복 없이 전달하는 단계다.

## 2. WIP12D에서 이미 끝난 것

WIP12E는 아래 기능을 다시 만들거나 되돌리면 안 된다.

### 2.1 종말탄도와 잔존체

- `TerminalProjectileSpec/State`, event-driven ordered traversal, 독립된 `traversalOutcome`/`projectileFailure` 축이 존재한다.
- `PERFORATED + SHATTERED`가 동시에 가능하다.
- Kh-32 정상 기폭은 최대 4개의 결정적 `MACRO_FRAGMENT`를 만든다.
- 큰 잔존체는 내부 경계·장비 volume·반대편 외판을 실제 재질 solver로 다시 해결한다.
- 외부로 나간 잔존체는 제한된 실제 형상 재질의를 통해 다른 선체/상부구조에 재진입할 수 있다.
- 모든 완전 관통 physical-hull crossing은 실제 구멍을 만들며, 젖은 구멍은 기존 침수 모델에 연결된다.
- 비폭발성 파편과 구조 충격 자체는 화재를 일으키지 않는다. 실제 취약 물질 volume 기계 충돌만 드문 결정적 발화를 허용한다.

### 2.2 표시와 성능

- 관통선, macro body, 출구, 재진입, 해수 진입과 blast envelope는 명시적 `내부 구조` 보기에서만 보인다.
- 피격 후 외부 파괴구를 통해 보이는 내부는 coarse `COMPARTMENT_INTERIOR_V8` 침수구획이다.
- `내부 구조`에서는 coarse layer를 숨기고 상세 138-space topology와 hazard를 표시한다.
- `피격 중심` 모드는 clipping plane과 object-AABB culling을 함께 사용한다.
- 검증 장면의 draw call은 전체 내부 `2,342`, 피격 중심 `298`이다.
- 물리 계산은 impact-time이며 render frame에서 geometry query를 하지 않는다.

### 2.3 현재 Kh-32 기준값

seed `481232`, 100 km Kh-32 기준:

| 항목 | WIP12D 값 |
|---|---:|
| 명중 시각 | `92.78333333333333 s` |
| 보고 충돌 속도 | `991 m/s` |
| legacy 충돌 에너지 | `2,849.804054661079 MJ` |
| legacy 관통 점수 | `4.318827711120478` |
| 첫 접촉 | `전방연돌` |
| 물리 경로 길이 | `22.52876902577326 m` |
| legacy blast damage budget | `191` |
| legacy damaged parts | `17` |
| WIP12D blast source | `3`, power 합 `1.0` |
| 폭발 직전 복원 속도 | `900.1216723041238 m/s` |
| macro body | `4` |
| macro 초기 운동에너지 | `96.54254026518716 MJ` |
| 내부 정지 / 외판 이탈 | `2 / 2` |
| residual 외피 구멍 | `2` |
| residual 기계 피해 보충 | `9.343133985302943 units` |
| 해수면 / 수중 진입 | `1 / 1` |

이 값 중 관통, 기폭 위치, 잔존체, 구멍, RNG는 WIP12E에서도 회귀 기준이다. `191`과 부품별 피해 행은 새 폭압 solver의 **비교·보정 기준**이지, 권위 전환 뒤 무조건 exact로 보존할 값이 아니다.

## 3. 현재 blast 구현의 정확한 한계

현재 코드는 이미 weapon-agnostic 이름을 쓰지만 실제 물리는 다음과 같다.

- `ASM_BLAST_MODEL`은 TNT 질량의 세제곱근 반경과 tuned damage power/cap을 계산한다.
- `asmBlastOverpressureFactor()`는 물리 단위의 압력파가 아니라 선형 감쇠 normalized proxy다.
- `buildWip101ChainBlastSources()`는 하나의 유한 탄두 budget을 기폭점에서 정지점까지 head/peak/tail source로 나눈다.
- `computeWip101BlastDamageFromSources()`는 box 중심 거리와 취약도에 따라 scalar damage를 만들고, 다시 legacy single-burst 총량으로 정규화한다.
- 승조원 내부 전파는 WIP07의 portal 그래프를 사용하지만, pressure/fragment attenuation을 게임용 계수로 전달하는 별도 consumer다.
- 구조, 장비, 승조원, 시각화가 같은 “구획별 peak pressure/impulse trace”를 공유하지 않는다.
- 문/격벽 파괴로 새로운 통로가 열리고 그 통로를 통해 후속 압력이 배출되는 연쇄는 없다.
- 현재 물방울형 envelope는 같은 source를 읽는 보존적 표시이지만, 압력파의 시간 전개나 반사/배출을 의미하지 않는다.

즉, WIP12D에서 “폭발이 작다/단순하다”고 느껴지는 이유는 VFX 크기보다 **공간 전파 상태와 시간·구조 반응 계약이 없기 때문**이다.

## 4. WIP12E 절대 원칙

### 4.1 하나의 폭발 사건, 하나의 피해 권위

- 같은 `impactEventId`에 legacy scalar blast와 신규 compartment blast를 둘 다 적용하지 않는다.
- 개발 중에는 신규 solver를 `SHADOW_DIAGNOSTIC`으로 실행할 수 있지만 이때 피해 state를 바꾸면 안 된다.
- 권위 전환은 명시적 mode로 한다.

권장 mode:

```text
LEGACY_SCALAR_BLAST_COMPAT
COMPARTMENT_BLAST_SHADOW
COMPARTMENT_BLAST_AUTHORITY
```

- `COMPARTMENT_BLAST_SHADOW`: trace와 비교표만 생성, damage consumer 호출 금지.
- `COMPARTMENT_BLAST_AUTHORITY`: legacy blast channel 적용을 끄고 신규 packet만 한 번 적용.
- 관통·파편·잔존체·breach 경로는 blast 권위 전환과 별개로 기존 결과를 유지.

### 4.2 구획은 압력을 전달하지만 빈 공간은 관통 저항이 아님

WIP12A의 `EMPTY` 원칙과 충돌하지 않게 한다.

- projectile traversal의 빈 구획: 관통 저항 0.
- detonation 뒤 gas/pressure solver의 구획: 압력 상태를 가질 수 있음.
- 승조원 점유는 projectile 저항도 아니고 압력 차폐재도 아님.

### 4.3 폭압과 파편을 섞지 않음

다음 채널은 계속 독립이다.

- incident overpressure
- reflected pressure
- positive-phase pressure impulse
- dynamic/blast-wind impulse
- hot-gas/thermal exposure
- warhead fragments
- plate plug/rear spall
- macro residual-body direct impact
- breach/opening
- structural shock

아라미드와 얇은 판재가 각각 어느 채널에 영향을 주는지 기존 계약을 유지한다. 폭압 감소를 이유로 직접 관통이나 macro fragment 에너지를 다시 깎지 않는다.

### 4.4 full CFD를 만들지 않음

브라우저에서 매 tick 유체격자를 푸는 구조는 범위 밖이다.

- impact 순간에만 계산한다.
- 상세 구획과 portal을 노드/edge로 바꾼 bounded event solver를 사용한다.
- 각 구획은 소수의 lumped pressure state만 가진다.
- 시각화는 이미 계산된 trace를 재생할 뿐 물리를 다시 풀지 않는다.
- cap에 걸리면 조용히 누락하지 말고 trace에 `TRUNCATED_BY_BUDGET`을 남긴다.

### 4.5 공개되지 않은 제원을 사실처럼 만들지 않음

- 정확한 Kh-32 탄두 구조, 폭약 조성, 파쇄 분포, DDG-119 내부 치수는 공개 확정값으로 주장하지 않는다.
- 현재 Kh-32 탄두 `750 kg = explosive 500 kg + case 250 kg`, TNT factor `1.0`은 프로젝트의 `SIM_TUNED / PUBLIC_IDENTITY_UNCERTAIN` 입력이다.
- 모든 미확인 계수에는 provenance를 붙인다.
- 검증되지 않은 “현실 공식” 하나로 숫자를 멋있게 보이게 하는 구현은 금지한다.

## 5. 권장 데이터 계약

이름은 구현 중 조정할 수 있지만 역할과 분리는 유지한다.

### 5.1 `BlastChargeSpec`

고정 탄두 사양:

```js
{
  id,
  explosiveMassKg,
  tntEquivalentFactor,
  casingMassKg,
  detonationClass,
  energyModel,
  provenance,
  confidence
}
```

`massKg` 전체를 폭약량으로 사용하지 않는다. WIP12A의 전체 질량/관통체 질량 분리와 같은 이유다.

### 5.2 `CompartmentBlastEvent`

한 번의 기폭 입력:

```js
{
  schema: 'AEGIS_COMPARTMENT_BLAST_EVENT_V48_WIP12E',
  impactEventId,
  sourceProjectileId,
  targetEntityId,
  coordinateSpace: 'SHIP_LOCAL_METRES',
  detonationPoint,
  detonationTimeS,
  projectileDirection,
  projectileSpeedMps,
  charge,
  seedMode: 'EVENT_ID_HASH_NO_COMBAT_RNG',
  authorityMode
}
```

### 5.3 `BlastCell`

상세 WIP06 topology space를 blast 계산용으로 변환한 불변 geometry adapter:

```js
{
  id,
  bounds,
  volumeM3,
  centroid,
  surfaces,
  portalIds,
  occupancyVolumeId,
  equipmentVolumeIds,
  exteriorExposure
}
```

기존 138-space topology를 복제하지 말고 adapter/cache로 소비한다. coarse flood cell은 침수 consumer용이며 blast propagation의 주 geometry로 사용하지 않는다.

### 5.4 `BlastPortal`

압력이 이동할 수 있는 연결:

```js
{
  id,
  aCellId,
  bCellId,              // exterior면 null 또는 EXTERIOR
  kind,
  centre,
  areaM2,
  normal,
  openFraction01,
  failureThreshold,
  leakageModel,
  sourceOpeningId,
  provenance
}
```

portal 후보:

- 정상 개방 문/통로/계단/해치
- 닫힌 수밀문/방화문과 그 누설
- 관통으로 이미 생긴 entry/exit hole
- WIP12D residual body가 만든 `additionalShellOpening`
- blast가 새로 파괴한 격벽/문/외판 breach
- 외부로 향하는 vent

### 5.5 `BlastCellState`

구획별 가변 결과:

```js
{
  cellId,
  arrivalTimeS,
  peakIncidentKPa,
  peakReflectedKPa,
  positivePhaseDurationMs,
  pressureImpulseKPaMs,
  dynamicImpulsePaS,
  hotGasExposure,
  ventedEnergyJ,
  absorbedEnergyJ,
  remainingGasEnergyJ,
  revision
}
```

`peakPressure` 하나로 승조원·장비·구조 피해를 모두 결정하지 않는다. peak와 impulse가 서로 다른 failure mode를 만들 수 있어야 한다.

### 5.6 `BlastSurfaceLoad`

격벽·갑판·문·외판의 국부 하중:

```js
{
  surfaceId,
  cellId,
  localPoint,
  normal,
  incidentKPa,
  reflectedKPa,
  impulseKPaMs,
  dynamicImpulsePaS,
  loadedAreaM2,
  failureMode,
  residualStrength01,
  breachAreaM2
}
```

WIP12E에서는 persistent damage-patch ledger를 활성화하지 않는다. 다만 WIP12A patch diagnostic과 연결 가능한 surface/local 좌표를 남긴다.

### 5.7 `BlastTrace`와 `BlastDamagePacket`

```js
{
  impactEventId,
  authorityMode,
  sourceCellId,
  cellStates,
  portalEvents,
  surfaceLoads,
  ventJets,
  energyLedger,
  terminationReason,
  clippedByBudget,
  deterministicHash
}
```

피해 packet은 최소 다음 consumer payload를 분리한다.

- `structureLoads`
- `equipmentLoads`
- `crewPressureExposure`
- `thermalHotGas`
- `newBreaches`
- `ventJets`
- `secondaryIgnitionCandidates`

모든 packet은 `impactEventId`를 공유하고 consumer가 중복 적용을 거부해야 한다.

## 6. 권장 solver 흐름

### 6.1 전처리

1. 기폭점을 상세 138-space topology cell 또는 exterior에 locate한다.
2. 현재 portal state, 기존 entry/exit hole, WIP12D residual hole을 읽는다.
3. topology revision과 opening revision을 키로 blast graph/cache를 얻는다.
4. 탄두 사양에서 TNT-equivalent와 초기 가스/압력 budget을 만든다.
5. 관통 trace와 projectile velocity는 초기 방향성 보정에만 쓰고 에너지를 중복 생성하지 않는다.

### 6.2 earliest-event propagation

우선순위 queue의 한 항목은 `arrivalTimeS + stableTieKey`로 정렬한다. 각 cell에서 다음 사건을 경쟁시킨다.

- pressure front가 surface에 도달
- front가 열린 portal에 도달
- 닫힌 문/격벽이 failure threshold에 도달
- 새 breach가 열림
- gas가 exterior opening으로 vent
- local positive phase 종료

동일 시간 tie는 고정 순서로 처리한다.

1. 현재 surface load 확정
2. failure 여부 확정
3. breach/portal topology revision 생성
4. 그 위치에서 후속 전파/vent 생성

부동소수점 비교만으로 순서가 흔들리지 않도록 quantized event time 또는 명시적 epsilon과 stable ID 정렬을 사용한다.

### 6.3 압력과 반사

최소 구현에서도 다음을 분리한다.

- source cell의 free-field/near-field incident peak
- surface orientation에 따른 reflected peak
- positive-phase duration과 pressure impulse
- opening ratio와 cell volume에 따른 quasi-static gas pressure
- portal/door/partition transmission과 누설
- exterior venting에 따른 source-cell pressure 감소
- 다음 cell로 전달되는 transmitted impulse

정확한 blast-structure 상호작용을 주장하기 전에는 `SIM_TUNED` fixture로 제한한다. 그래도 단위는 kPa, kPa·ms, Pa·s, joule처럼 명시하고 dimensionless damage unit으로 조기에 뭉개지 않는다.

### 6.4 동적 breach와 재전파

닫힌 문이나 얇은 격벽이 파괴되면:

1. `BlastSurfaceLoad.failureMode`를 남긴다.
2. 양의 면적을 가진 새 `BlastPortal`을 만든다.
3. 같은 사건의 아직 남은 pressure/gas budget만 그 portal로 보낸다.
4. 이미 적용된 초기 front를 새 폭발처럼 다시 생성하지 않는다.
5. 외판 breach면 기존 침수/파괴구 consumer에 한 번 전달한다.

가능한 failure mode 예:

- `ELASTIC_NO_FAILURE`
- `DOOR_BLOWN_OPEN`
- `PANEL_YIELD`
- `PANEL_RUPTURE`
- `JOINT_FAILURE`
- `EXTERIOR_BREACH`

갑판/격벽 전체를 즉시 삭제하지 않는다. 국부 breach 면적과 잔존 구조강도를 기록한다.

### 6.5 exterior vent jet

실제 외부 개구부가 있으면:

- 내부 gas energy와 압력을 감소시킨다.
- opening normal 방향의 `ventJet`을 만든다.
- 외부 VFX에는 짧은 고온가스/연기/먼지/잔해 jet을 표시할 수 있다.
- exterior jet은 별도 표적과 재충돌하는 무기가 아니다.
- 인접 외부 구조에 meaningful load를 줄지 여부는 bounded surface-load consumer로만 결정한다.

## 7. 소비자별 피해 규칙

### 7.1 구조

- 구조는 peak reflected pressure, impulse, loaded area, 지지 조건을 소비한다.
- 기존 `getShipLongitudinalStrengthV48Wip03().impact()`의 한 점 impulse는 compatibility consumer로 남길 수 있지만, 신규 surface load를 scalar 폭약량으로 다시 환산해 중복 적용하지 않는다.
- 새 외피 breach는 침수 opening으로 연결한다.
- WIP12E 중 persistent patch ledger는 여전히 비활성이다.

### 7.2 장비

- 장비 volume은 해당 cell의 압력/impulse와 국부 line-of-sight/shielding을 소비한다.
- 민감 전자장비, 배관, 발전기, VLS는 서로 다른 threshold profile을 갖는다.
- 장비 HP 감소와 기능상실은 기존 consumer를 통해 적용하되 source channel을 기록한다.

### 7.3 승조원

- `CREW_EXPOSURE`는 여전히 projectile 저항이 아니다.
- 승조원은 위치 cell의 incident/reflected pressure, impulse, blast-wind, 파편/스폴을 각각 받는다.
- pressure casualty와 fragment casualty를 하나의 확률로 합치지 않는다.
- door/partition 뒤 차폐와 portal transmission을 실제 `BlastTrace`에서 읽는다.

### 7.4 화재와 열

- 폭압만으로 일반 구획에 자동 화재를 만들지 않는다.
- 명시적 hot-gas/thermal exposure, 연료·윤활유·전기·탄약 volume의 손상, 이미 존재하는 ignition source만 발화 후보가 된다.
- WIP12C의 희박하고 결정적인 취약 volume 발화 cap을 기본 상한으로 보존한다.
- inert fragment, plate plug, structural impulse는 단독 ignition source가 아니다.
- VLS/탄약의 cook-off는 WIP12E에서 기존 incident consumer까지만 연결하고, 새로운 복잡한 탄약 연쇄모델은 별도 승인 없이는 만들지 않는다.

### 7.5 침수

- 신규 exterior breach만 기존 flood opening으로 전달한다.
- 내부 문/격벽 breach는 곧바로 해수 유입구가 아니다.
- 수선 아래 외피 파괴구는 위치·면적·법선을 보존한다.
- 같은 `impactEventId + surfaceId + breach serial`의 중복 opening을 거부한다.

## 8. 시각화 계약

### 8.1 기본 외부 보기

기본 외부 화면에는 내부 pressure volume을 표시하지 않는다. 허용되는 것은 다음뿐이다.

- 실제 파괴구
- exterior vent jet
- 외부로 나온 먼지·연기·불꽃·잔해
- 매우 짧고 절제된 외부 shock cue

### 8.2 `내부 구조` 보기

명시적 내부 모드에서만 다음을 표시한다.

- 시간에 따라 cell/portal을 이동하는 pressure front
- peak/impulse heat map
- 반사압이 큰 surface highlight
- 문/격벽 파괴와 새 breach
- exterior로 빠지는 vent jet
- 기존 관통선, macro fragment, 출구, 해수 진입

구획이 겹쳐 보이는 문제를 줄이기 위해 기본은 `피격 중심`을 유지한다. `전체 내부`는 사용자가 명시적으로 선택할 때만 138-space 전체를 보여준다.

### 8.3 VFX와 권위 분리

- renderer는 `BlastTrace`의 immutable presentation snapshot만 읽는다.
- renderer가 압력, 피해, breach, 발화, 난수를 계산하지 않는다.
- 시각적 크기를 키우기 위해 물리 반경이나 피해를 바꾸지 않는다.
- pressure front는 개별 구 수십 개보다 instanced/batched cell shell 또는 portal ribbon을 우선한다.
- draw call과 transient mesh 수를 diagnostic에 남긴다.

## 9. 성능 계약

초기 구현은 아래 형태의 하드 cap을 가져야 한다. 정확한 수치는 첫 benchmark 뒤 조정할 수 있지만 cap 자체를 없애면 안 된다.

| 항목 | 권장 초기 상한 |
|---|---:|
| 방문 blast cell | `96` |
| portal propagation event | `384` |
| surface load record | `512` |
| dynamic breach | `64` |
| cell pressure integration slice | `32` |
| exterior vent jet | `32` |
| presentation keyframe | `256` |

추가 규칙:

- topology와 portal geometry는 revision cache를 사용한다.
- pressure solver는 impact 순간 한 번 실행한다.
- fire/flood/DC의 기존 저주기 tick은 결과만 소비한다.
- render frame geometry query와 재전파는 `0`이어야 한다.
- hard cap에 걸린 사건은 diagnostics에 count와 discarded energy estimate를 남긴다.
- 64× 과부하에서도 backlog를 만들지 않고 impact-time budget 초과를 계측한다.

## 10. 결정성과 에너지 bookkeeping

### 10.1 RNG

- pressure propagation은 원칙적으로 난수가 필요 없다.
- 취약장비 발화나 파편 샘플이 필요하면 `impactEventId` hash만 사용한다.
- 전투 RNG 상태는 전후 exact 동일해야 한다.

### 10.2 에너지 ledger

최소 ledger:

```js
{
  chemicalInputJ,
  initialBlastEnergyJ,
  pressureWorkJ,
  structuralAbsorptionJ,
  ventedEnergyJ,
  thermalRetainedJ,
  unresolvedResidualJ,
  truncationDiscardJ,
  closureErrorJ
}
```

필수 invariant:

```text
모든 output/absorbed/remaining/truncated energy 합
<= modeled input energy + tolerance
```

WIP12D macro fragment chemical coupling `2.4%`를 신규 blast energy와 이중 계산하지 않는다. 그 값은 이미 잔존체 초기 운동에너지 ledger에 배정된 몫이다.

### 10.3 순서 결정성

- priority queue tie는 `time → event type priority → cell ID → portal/surface ID` 순으로 정렬한다.
- object insertion order나 브라우저별 Map 순서에 결과를 의존하지 않는다.
- 결과 snapshot은 stable sort 뒤 hash한다.
- 같은 seed, 1×/8×/16×에서 authoritative 결과가 exact 일치해야 한다.

## 11. 필수 진단 fixture

실제 특정 탄약의 공개 정확도를 주장하지 않도록 diagnostic ID를 사용한다.

### 11.1 단위 fixture

1. `TEST_BLAST_OPEN_AIR`
   - exterior burst, 구조물 없음.
   - 압력/충격량 거리 감쇠와 energy closure 확인.

2. `TEST_BLAST_SEALED_CELL`
   - 닫힌 단일 구획.
   - reflected peak와 quasi-static tail 존재 확인.

3. `TEST_BLAST_OPEN_PORTAL`
   - 같은 두 구획, 열린 문.
   - source cell pressure 감소와 downstream 전달 확인.

4. `TEST_BLAST_CLOSED_DOOR`
   - 닫힌 문이 버티는 case와 파괴되는 경계 case.
   - 파괴 뒤 남은 positive phase만 전달되는지 확인.

5. `TEST_BLAST_BREACH_VENT`
   - 외피 구멍이 없는 case와 있는 case 비교.
   - 개구부가 source cell quasi-static pressure를 낮추고 exterior vent jet을 만드는지 확인.

6. `TEST_BLAST_MULTI_CELL`
   - 세 개 이상 구획과 두 경로.
   - shortest distance가 아니라 portal geometry/time 순서로 전파되는지 확인.

7. `TEST_BLAST_DUD`
   - cell state, damage packet, fire, vent jet 모두 0.

8. `TEST_BLAST_IDEMPOTENCE`
   - 동일 `impactEventId` 두 번 적용 시 두 번째 zero-mutation.

### 11.2 live integration fixture

WIP12D의 seed `481232`, 100 km Kh-32를 그대로 사용한다.

보존해야 할 것:

- hit time과 impact speed
- 첫 접촉 `전방연돌`
- penetration score와 physical path
- 기폭 위치와 fuze outcome
- macro body 4개와 mass/energy ledger
- 내부 정지 2, 외판 이탈 2
- residual opening 2
- 해수면/수중 진입 1/1
- DUD body/exit/blast 0
- combat RNG exact

의도적으로 바뀔 수 있는 것:

- 총 scalar damage `191`
- damaged parts `17`
- 부품별 피해 순위와 수치
- crew casualty와 장비 failure 분포
- 구조 breach 수와 면적
- blast VFX 반경과 지속시간

변경값은 “더 커 보이게” 임의 조절하지 말고 pressure/impulse trace의 결과로 설명해야 한다.

## 12. 회귀와 완료 조건

### 12.1 정적 계약

- schema/version/coordinate/units 존재
- source·state·trace·packet 역할 분리
- authority mode 세 가지가 명시적
- legacy/new blast 동시 적용 금지
- crew occupancy가 resistance로 쓰이지 않음
- renderer가 damage/RNG 함수를 호출하지 않음
- 모든 cap과 termination reason 존재

### 12.2 물리/결정성 계약

- open portal이 닫힌 portal보다 더 많은 downstream impulse를 전달
- exterior opening이 커질수록 source cell의 retained quasi-static pressure가 증가하지 않음
- surface reflection이 incident pressure와 독립 기록
- door failure 전/후 propagation이 시간순
- energy ledger가 tolerance 안에서 닫힘
- 동일 event 적용 두 번째는 zero-mutation
- DUD는 blast state 0
- same-seed exact, combat RNG 불변

### 12.3 기존 기능 회귀

- WIP12A terminal ballistics 전부 통과
- WIP12B live ordnance/fuze 전부 통과
- WIP12C internal traversal/fire 정책 전부 통과
- WIP12D residual overpenetration/re-entry/flood 전부 통과
- 침수·구조·승조원·VLS·damage-control 회귀 통과
- snapshot import 실패 시 zero-mutation 유지
- 1×·8×·16× authoritative 결과 일치

### 12.4 브라우저/표시 계약

- 외부 보기에서 내부 pressure volume 숨김
- 내부 보기에서 trace/heat map/breach/vent 표시
- 피격 중심과 전체 내부 전환 정상
- hull/upper-structure envelope 밖으로 상세 구획이 돌출되지 않음
- draw-call과 transient mesh 상한 기록
- console/page error 0

### 12.5 완료 판정

WIP12E 완료는 다음을 모두 만족할 때만 선언한다.

- `BlastTrace`와 `BlastDamagePacket` 계약 존재
- bounded compartment/portal propagation 동작
- incident/reflected pressure, pressure impulse, blast wind가 분리됨
- door/bulkhead failure와 dynamic breach가 후속 전파에 반영됨
- 실제 exterior opening이 venting과 침수 양쪽에 한 번씩 올바르게 연결됨
- legacy scalar blast와 신규 blast 중복 적용 없음
- fire가 pressure/불활성 파편만으로 남발되지 않음
- WIP12D 관통·잔존체·구멍·RNG 회귀 유지
- 새로운 Kh-32 공간 피해 결과가 trace로 설명 가능
- 전체 정적·결정적·브라우저·성능 회귀 통과
- README, 프로젝트 지침, 상태 문서, 체크섬 동시 갱신

## 13. WIP12E에서 하지 않는 것

- full CFD 또는 셀 단위 Navier–Stokes
- 무제한 파편 개별 물체
- 수중 폭발/버블펄스/선체 whipping
- 함외 자유공간 폭발 전문 solver
- 실제 표면 표적 선택과 대함 발사/FCS
- 실제 함포 발사·포탑·탄창·외탄도
- production homogeneous/KC armor
- persistent damage patch ledger
- operational snapshot에 transient blast wave 저장
- 새 표적함과 복수 함선 프로파일
- VLS cook-off의 새로운 다단 탄약 연쇄모델

위 항목은 WIP12E가 끝난 뒤 별도 범위로 승인한다.

## 14. 권장 구현 순서

1. WIP12D `main` SHA와 HTML checksum 재검증
2. 새 branch `feat/v48-wip12e-compartment-blast`
3. WIP12E 계약/진단 함수부터 추가
4. 상세 topology → immutable blast cell/portal adapter
5. charge/event/state/trace/ledger schema
6. source-cell incident/reflected pressure와 impulse
7. 열린 portal transmission과 exterior venting
8. 닫힌 door/bulkhead load와 동적 breach
9. bounded priority-queue propagation과 cap diagnostics
10. shadow mode에서 legacy `191`과 비교
11. 구조·장비·승조원·열·breach packet consumer 연결
12. `COMPARTMENT_BLAST_AUTHORITY` 전환과 legacy blast 적용 차단
13. interior-only pressure/vent visualization
14. 단위 fixture 8종과 Kh-32 live integration
15. 1×/8×/16×, 64× 과부하, draw-call 측정
16. 전체 Playwright/Actions 통과
17. 새 HTML·상태문서·README·지침·체크섬 동시 갱신

## 15. 현재 코드에서 먼저 볼 위치

`Aegis_SIM_v48_WIP12D.html`의 함수/상수 이름으로 찾는다. 줄 번호는 다음 버전에서 변할 수 있으므로 이름이 권위다.

- `ASM_BLAST_MODEL`
- `computeAsmBlastEffects()`
- `asmBlastOverpressureFactor()`
- `buildWip101ChainBlastSources()`
- `computeWip101BlastDamageFromSources()`
- `wip12aDamagePacket()`
- `wip12aApplyDamagePacket()`
- `wip12bRecordLegacyAsmTerminalEffect()`
- `damageFloodImpactV48Wip12C()`
- `createShipInteriorTopologyV48Wip06()`
- WIP07 crew `blastGraphEvaluations`와 `damageImpact()` 경로
- `createShipDamageVisualStateV1()`
- `wip12dResidualOverpenetrationDiagnostics()`
- `wip12dResidualOverpenetration3DAudit()`

중요: 기존 WIP07 portal blast 전파를 그대로 “현실 폭압 solver”라고 이름만 바꾸면 안 된다. 그 코드는 승조원 피해용 게임 근사이며, WIP12E의 공통 `BlastTrace`를 소비하도록 단계적으로 바꾸는 대상이다.

## 16. 권장 새 diagnostic API

- `wip12eCompartmentBlastContract()`
- `wip12eCompartmentBlastDiagnostics()`
- `wip12eBlastFixtureDiagnostics()`
- `wip12eKh32BlastShadowComparison()`
- `wip12eBlastAuthorityProbe()`
- `wip12eBlastIdempotenceProbe()`
- `wip12eBlastPerformanceProbe()`
- `wip12eCompartmentBlast3DAudit()`

각 진단은 UI와 독립적으로 호출 가능해야 하며, 결과는 stable-sort된 JSON으로 저장할 수 있어야 한다.

## 17. 작업 중 특히 피해야 할 함정

1. **구 반경만 키우기**
   - 더 커 보일 뿐 반사·격벽·배출 문제가 해결되지 않는다.

2. **legacy 191 exact 강제**
   - 신규 pressure model이 다시 old scalar 정규화에 종속된다.

3. **legacy와 신규 피해 동시 적용**
   - Kh-32 피해가 두 번 들어간다.

4. **상세 topology와 coarse flood cell 혼용**
   - 표시와 피해 위치가 다시 어긋난다.

5. **문 파괴 뒤 폭발 새로 생성**
   - 에너지가 portal마다 복제된다.

6. **승조원 구역을 물질 저항으로 처리**
   - WIP12A의 EMPTY/CREW_EXPOSURE 계약을 깨뜨린다.

7. **renderer에서 전파 계산**
   - 내부 보기 on/off에 따라 authoritative 결과가 달라진다.

8. **모든 pressure damage를 화재로 연결**
   - 사용자가 명시적으로 금지한 비폭발성/충격 화재 남발이 재발한다.

9. **classified-like precision 주장**
   - 공개되지 않은 탄두/함체 값을 사실처럼 만드는 오류다.

10. **성능 cap 없이 BFS/재귀 확장**
    - 138-space 전체와 동적 breach가 결합하면 브라우저 hitch가 커진다.

## 18. 새 채팅에 그대로 붙일 착수 요청

아래 문장을 이 인계서와 함께 새 채팅에 전달하면 된다.

> `0-FLANDRE-0/Aegis_Project`의 WIP12D 병합 상태와 `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`를 먼저 확인해줘. `Aegis_SIM_v48_WIP12D.html` SHA-256이 `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`인지 검증한 다음, `feat/v48-wip12e-compartment-blast` 브랜치를 만들고 WIP12E를 진행하자. 먼저 현재 scalar blast/crew portal/damage consumer 경로를 코드에서 다시 추적하고, 인계서의 권위 전환·에너지 ledger·성능 cap을 반영한 상세 구현계획과 branch 생성까지만 해줘.

## 19. 최종 의사결정 요약

- WIP12D는 병합한다.
- 다음 구현 번호는 WIP13이 아니라 **WIP12E**다.
- WIP12E는 blast VFX 확대 작업이 아니라 compartment pressure/impulse 기반공사다.
- 신규 solver는 shadow → authority 두 단계로 전환한다.
- 권위 전환 뒤 legacy `191` exact parity는 요구하지 않는다.
- 관통·기폭 위치·잔존체·구멍·침수·전투 RNG 회귀는 유지한다.
- 폭압, 반사압, impulse, blast wind, hot gas, fragment, residual body를 별도 채널로 둔다.
- 실제 문·격벽·파괴구·외부 개구부가 전파와 venting을 바꾼다.
- full CFD 대신 bounded event-driven compartment/portal graph를 사용한다.
- 상세 pressure 표현은 `내부 구조` 보기에서만 보이고 renderer는 presentation-only다.
- 비폭발성 파편과 단순 충격은 계속 거의 화재를 만들지 않는다.

