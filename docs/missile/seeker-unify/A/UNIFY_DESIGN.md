# 시커 공통 물리층 설계안

IMPLEMENTED: **아니오**

TESTED: **계약·이전표 정적 대조만 완료**

APPROVED: **아니오**

UNRESOLVED: **공통 composite의 SARH 쌍정 확장과 RAM 수동 센서 어댑터**

RELEASE: **아니오**

## 목표 경계

```text
physical scene
  -> synthesizeEchoes(receiver, propagationModel, waveformProfile)
  -> resolveCells(echoes, resolutionProfile)
  -> makeMeasurements(cells, observableModel, rngState)
  -> validateMeasurements(measurements, validationHooks)
  -> associateLocalTrack(measurements, cue, gateProfile)
  -> seekerStateMachine(localTrackEvent, transitionProfile)
  -> SeekerEstimate {valid, mode, position?, velocity?, bearing?, covariance, ageS, quality}
  -> weapon-specific guidance arbiter
```

## 공통 API

### `synthesizeEchoes(request)`

- 입력: receiver position/velocity, band, beam/gimbal, min/max range, monostatic/bistatic/passive propagation tag, waveform profile, independent RNG handle.
- 출력: 익명 `EchoSample[]` (`range/pathRange`, angle, path-rate, received power/SNR, apparent extents, clutter class observable).
- 금지 출력: entity id, profile id, truth reference.
- SARH는 `tx`와 `rx`를 모두 받고 두 LOS·두 beam·쌍정 RCS를 계산한다. RAM RF/IR은 별도 passive adapters가 같은 출력형식으로 변환한다.

### `resolveCells(echoes, profile)`

- range/angle/Doppler 분해능과 전력 가중 centroid/extent를 한 번만 적용한다.
- 현재 WIP22, SAM SARH, SAM ARH의 unresolved 기준을 프로필로 이전한다.
- Harpoon은 `NONE`에서 시작해 공용 cell 합성을 SHADOW로 먼저 비교한다.

### `makeMeasurements(cells, model, rng)`

- 관측 차원 enum: `ACTIVE_MONOSTATIC_4D`, `SARH_BISTATIC_4D`, `PASSIVE_RF_2D`, `PASSIVE_IR_2D`.
- 출력은 값과 정확히 같은 공분산을 함께 가진다.
- 각 무장의 기존 독립 RNG seed/advance 순서를 유지하는 adapter를 둔다.

### `validateMeasurements` / `associateLocalTrack`

- 표적 검증은 공통 feature 객체를 받고 플러그인 목록을 적용한다.
- gate floor는 프로필 값이며 NIS와 절대 range/angle/Doppler gate를 함께 보존한다.
- cue는 측정공간 prediction/covariance만 받는다. truth id 비교는 금지한다.

## 무장별 훅

- Kh-32: rosette/spiral search, planned dive, HOJ takeover.
- Kh-35U: 3-bar raster, sea-skimming terminal profile, HOJ.
- Harpoon: 경유점 완료/기억 바구니 활성화, INS-only preterminal, DL 없음.
- SM-2/ESSM B1: SPG-62 조사 기회와 SARH bistatic receiver.
- SM-6/ESSM B2: SARH→ARH source arbiter, active 4Q monopulse, cross-mode consistency.
- RAM: passive RF first, IR promotion/dropout hysteresis, bearing-only guidance.

## 표적 검증 후속안

Part 1에서 RCS 보정 후에도 장거리 수상 반사가 해면 셀과 합성되어 기존 폭 기반 점수 아래에 남는 경우에만 다음을 순서대로 SHADOW 측정한다.

1. 동일 range-angle-Doppler cell 주변 대비 국소 signal-to-clutter ratio.
2. dwell 사이 centroid/power 지속성.
3. waveform range/Doppler morphology.

어느 항목도 현재 `.55` 통과율에 맞춰 계수를 고르지 않는다. 해면·채프·무표적 오획득이 하나라도 늘면 ACTIVE 승격하지 않는다.

## 구현 단계

| 단계 | 변경 | 같은 입력 동등성 시험 | 예상 |
|---|---|---|---:|
| U1 | DTO·단위·RNG adapter, 계산은 기존 함수 위임 | 무장별 200 고정 측정 bit-equal | 1일 |
| U2 | WIP22 + SAM ARH echo/cell 공통화 SHADOW | SNR/측정/공분산, 대조군 | 1–2일 |
| U3 | Harpoon adapter | 기존 `harpoonSeekerCoreAuditC`, 장거리 route | 1일 |
| U4 | SARH bistatic adapter | SPG 조명/차단/재획득 | 1–2일 |
| U5 | RAM passive adapters | RF-first/IR-takeover, emitter/flare | 1일 |
| U6 | 상태기계·association 공통화 | 같은 seed 쌍 전투 + 전체 회귀 | 2일 |

각 단계는 SHADOW→동등성→ACTIVE 순서다. 허용 오차를 넓히거나 기대값을 자동 변경하지 않는다.
