# AEGIS v48 WIP13C6 — Surface Guidance Stabilization + ESSM ARH

- 기준 파일: `Aegis_SIM_v48_WIP13C5.html`
- 기준 SHA-256: `8d461aa383950729fd8a2f81963fd70e3f8bb323ed40d7ebea7a00a421bd96d7`
- 결과 파일: `Aegis_SIM_v48_WIP13C6.html`
- 결과 SHA-256: `50c41eff6e1e35b809786073353f880ac63673f05ce9c18012f03cccad78cede`
- 작성일: 2026-09-24
- 상태: C6 구현 및 결정적 VM 회귀 완료. 실제 브라우저 임의방위 실플레이 확인 후 WIP13C7/병합 진행

## 문제 재현 및 원인

사용자 실플레이에서 C5의 두 문제가 확인됐다.

1. SM-2는 seeker가 수상표적을 보고 있어도 pitch-over 이후 좌우 hunting을 하거나 해면으로 추락할 수 있었다.
2. ESSM은 수상표적 선택에도 기존 공중 SAM `trackIsFireControlQuality()` / A3 gate를 사용했고, live `SURFACE_ARH` runtime과 수상함 swept collision/WIP12F damage 경로가 연결되지 않았다.

C5 실비행 fixture도 실제 플레이 결함을 가릴 수 있었다. `runWip13c5SurfaceSarhLiveFlightFixture()`가 72개 절대방위에서 SPG-62 score가 가장 높은 단 하나의 방위를 골라 발사했기 때문에 임의 방위 launch/pitch-over 문제를 회귀로 잡지 못했다.

SM-2 launch controller에서는 BODY attitude 정렬을 검사했지만 실제 속도벡터 정렬은 ESSM에만 필수였다. 따라서 수상 SM-2는 BODY가 corridor를 향했더라도 flight-path vector가 아직 어긋난 상태에서 pitch-over 권한을 넘길 수 있었다. 또한 predictive sea-clearance rate guard는 ESSM에만 적용되어 수상 SM-2의 종말 하강 회복 여유가 부족했다.

## 구현

### 1. 수상 SM-2 launch hand-off 안정화

`surfaceLaunchVectorAlignedWip13C6()`를 추가했다.

- 수상 SM-2: 실제 속도벡터 heading 오차 ≤ 14°, pitch 오차 ≤ 12°일 때만 vector aligned
- 수상 ESSM: 기존 ESSM 수준인 heading ≤ 12°, pitch ≤ 9°
- 공중 SM-2: 기존 동작을 보존
- pitch-over deadline은 강제 권한 이양이 아니라 launch controller 유지 + 진단 경고로 남김

8개 절대방위 sweep에서 launch corridor bearing과 Mk41 in-cell launch azimuth가 요청 방위와 일치하는지 별도 검사한다.

### 2. 수상 SM-2 predictive sea-clearance

`_samSeaClearanceRateGuard()`의 적용 범위를 ESSM뿐 아니라 `_surfaceSarh` SM-2까지 확장했다.

- 현재 하강속도
- 이전 tick normal acceleration
- look-ahead 중력 낙하
- 해면 margin

을 사용해 미래 고도가 margin 아래로 내려갈 때 pitch-rate command floor를 만든다. 위치/속도 상태를 직접 수정하지 않는다.

### 3. 수상 estimator hunting 억제

`surfaceMissileFilterGuidanceStateWip13C6()`를 guidance source arbiter 뒤에 추가했다.

- SM-2: τ = 0.18 s
- ESSM: τ = 0.12 s
- source가 바뀌거나 추정 위치가 3.5 km 이상 jump하면 즉시 reset
- 입력은 선택된 `SARH_RF_EKF`, `ARH_RF_EKF`, `DL_TRACK` 등 estimator state뿐임
- truth object / reflector ID / entity ID는 사용하지 않음

진단 jitter 입력 `+100/-100 m` 반복에서 raw swing 200 m가 filtered swing 약 28.47 m로 감소했다.

### 4. ESSM 실제 `SURFACE_ARH` release

`spawnESSM()`이 수상트랙을 별도로 감지한다.

수상표적에서는 기존 공중용 `trackIsFireControlQuality()` / A3 gate 대신 `surfaceEssmLiveReleaseGateWip13C6()` → C4 `surfaceMissileReleaseAssessmentWip13C4()`를 사용한다.

필수 조건은 기존 C4 계약을 유지한다.

- `MANUAL`
- confirmed anonymous surface track
- `HOSTILE` 또는 `TRAINING_TARGET`
- surface missile FCQ 허용
- VLS/combat system 정상
- ARH acquisition basket 유효
- `AUTO` / `SEMIAUTO`, `UNKNOWN`, `FRIEND`, `NEUTRAL`은 차단

실제 `spawnESSM()` 회귀에서 ESSM 1발 소비와 `_surfaceArh` runtime 생성을 확인했다.

### 5. ESSM 수상 유도 corridor

C6의 `SURFACE_ARH` runtime은 다음 `SIM_TUNED_PUBLIC_UNKNOWN` 값을 사용한다.

- midcourse sea-clearance: 80 m
- terminal floor: 2 m
- ARH handoff/pitbull: 13.5 km
- SPG-62: optional quality contributor, 발사 필수 토큰 아님

기존 공중 ESSM의 70 m legacy midcourse floor가 `_surfaceArh` 값을 다시 덮어쓰지 않도록 분리했다.

### 6. SM-2 / ESSM 공통 수상 terminal

C5의 SM-2 전용 terminal adapter를 `surfaceMissileSweptContactWip13C6()` / `resolveSurfaceMissileContactWip13C6()`로 일반화했다.

- 실제 missile segment와 실제 3D surface hull의 swept contact만 판정
- weapon key에 따라 `WIP12B_LIVE_ORDNANCE.SM2` 또는 `.ESSM` terminal spec 선택
- 표적 좌표계 상대속도로 WIP12F contact/direct-action trace 실행
- surface target runtime에 damage packet 1회 적용
- 수상 미사일은 공중/ASM용 truth proximity-kill shortcut을 사용하지 않음

ESSM synthetic physical contact 회귀는 760 m/s 접촉에서 `FUZE_AT_CONTACT`, perforation, impact/scar/breach/fire 각 1개와 `ESSM_SURFACE_ARH_LIVE` damage source를 확인했다.

## Truth boundary

C6 release/guidance state는 익명 track/measurement state만 소비한다.

결정 경로 정적 검사에서 다음 토큰의 신규 사용은 0건이다.

- `truthObjectForTrackV27(`
- `surfaceContacts`
- `SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A`
- `truthRef`
- `_truthObject`
- `_physicsKind`

truth/entity는 물리 swept collision과 damage application 경계에서만 사용한다.

## 결정적 검증

실행:

```text
AEGIS_REPORT_PATH=artifacts/wip13c6-surface-missile-guidance-regression.json node tests/surface-missile-wip13c6-guidance-regression.cjs Aegis_SIM_v48_WIP13C6.html
```

결과:

| 검증 | 결과 |
| --- | --- |
| C6 전용 guidance/live ESSM fixture | 15/15 통과 |
| C6 통합 regression wrapper | 20/20 통과 |
| core self-test | 실패 0 |
| C4 surface missile foundation | 11/11 통과 |
| C4 ordnance-neutral terminal adapter | 8/8 통과 |
| WIP13B12 ARH sea-clutter/discrete-target validation | 13/13 통과 |
| NAV/ARM/DEBUG tab invariance | 4/4 통과 |
| mobile ARM subtab invariance | 4/4 통과 |

C6 전용 핵심 check:

- ESSM manual surface release 허용
- AUTO surface release 차단
- 실제 `spawnESSM()` `_surfaceArh` 생성
- ESSM VLS 1발 소비
- ESSM runtime truth-clean
- 수상 SM-2 bad velocity vector hand-off 차단
- 공중 SM-2 legacy hand-off 보존
- 수상 SM-2 aligned vector hand-off 허용
- 8개 임의 절대방위 launch command 정렬
- ESSM 수상 midcourse floor 80 m 유지
- estimator jitter damping
- 수상 SM-2 predictive sea guard
- ESSM swept physical hull contact
- ESSM WIP12F damage
- release/guidance truth boundary

## 브라우저 검증 상태

현재 실행 환경의 시스템 Chromium은 존재하지만 로컬 `file://` 및 임시 로컬 HTTP 페이지 이동이 관리자 정책으로 차단되어 실제 WebGL 브라우저 회귀를 실행할 수 없었다.

따라서 아래는 아직 **미검증**으로 남긴다.

- 실제 UI에서 임의 방위 SM-2 발사 후 pitch-over/비행방위 육안 확인
- 실제 physical SARH RF chain 상태에서 좌우 hunting 감소 확인
- 실제 ESSM ARH RF acquisition/coast/reacquire 후 이동 표적함 명중/실패 궤적
- 2D/3D 화면에서 파괴구·화재·침수 시각 확인

결정적 VM 검증은 통과했지만 브라우저 실비행 결과를 통과했다고 주장하지 않는다. 병합 전 사용자 실플레이 확인을 권장한다.

## 다음 단계

`WIP13C7`:

- surface track 카드에 SM-2/ESSM FCQ, SPG assignment, ARH handoff 상태 표시
- contextual inhibit reason 정리
- 동일 표적 다중 발사 및 SPG 채널 경합
- 1×/8×/16× 결정성, 64× 성능 확인
- 2D/3D 전환 무영향
- 실제 브라우저에서 SM-2/ESSM 임의방위 발사·비행·충돌·피해 확인

## 산출물

- `Aegis_SIM_v48_WIP13C6.html`
- `WIP13C_SURFACE_MISSILE_ENGAGEMENT_PLAN.md`
- `AEGIS_PLAN_STATUS_v48_WIP13C5.md` (이전 단계 기록)
- `AEGIS_PLAN_STATUS_v48_WIP13C6.md`
- `tests/surface-missile-wip13c6-guidance-regression.cjs`
- `artifacts/wip13c6-surface-missile-guidance-regression.json`
- `SHA256SUMS_v48_WIP13C6.txt`
