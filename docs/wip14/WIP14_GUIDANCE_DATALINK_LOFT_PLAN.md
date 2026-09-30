# AEGIS v48 WIP14 — Missile Navigation, VLS Release, Weapon Link, and Loft Plan

작성일: 2026-09-30 (KST)  
계획 기준: GitHub `WIP14` branch + 사용자 제공 `Aegis_SIM_v48_WIP14B1.html`  
B1 HTML SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`

## 1. 단계 재편 결론

WIP14의 다음 단계는 아래와 같이 고정한다.

| 단계 | 범위 | 상태 |
| --- | --- | --- |
| B1 | SM-2MR / SM-2ER / SM-6 / ESSM onboard own-navigation 및 DL truth boundary | 로컬 후보 완료 |
| **B2** | **ASM/RAM own-navigation truth boundary 완성 + 공통 VLS launch interval/scheduler** | 다음 구현 |
| **B3** | **범용 weapon-link transport + 범용 return-link capability + bounded assistance** | B2 완료 후 |
| **B4** | **SM-2MR / SM-2ER / SM-6 / ESSM별 stateful loft profile** | 번호 유지, B3 완료 후 |

기존 B2 weapon-link 단계는 **B3으로 한 칸 이동**한다. 기존 B4 번호와 목적은 변경하지 않는다.

작업 순서는 반드시 `B2 → B3 → B4`로 유지한다.  
B2에서 모든 유도탄의 own-state truth boundary와 VLS 실제 발사 시간축을 먼저 고정해야 B3 packet transport가 잘못된 physical own-state를 네트워크로 포장하지 않고, B4 장거리 궤적 변화도 발사 스케줄/DL 변화와 분리해서 검증할 수 있다.

## 2. B1 기준선

B1에서 다음 네 계통은 error-bearing onboard navigation state를 사용한다.

- SM-2MR — `SM2MR_INS_B1`
- SM-2ER — `SM2ER_INS_B1`
- SM-6 — `SM6_GPS_INU_B1`
- ESSM Block 2 — `ESSM_INS_B1`

B1의 주요 계약은 유지한다.

- 물리 `x/y/z/vx/vy/vz`는 dynamics, RF/IR measurement synthesis, collision/fuze/damage, diagnostic comparison에만 사용한다.
- guidance/PIP/PN/APN/ZEM/Kappa/autopilot/planner는 error-bearing onboard state를 사용한다.
- seeker의 물리 relative measurement를 absolute state로 만들 때 onboard own-state frame에 re-anchor한다.
- DL hard-cut 뒤 launcher live track/truth를 다시 읽어 갱신하지 않는다.

2026-09-30 추가 감사에서 다음 gap이 확인됐다.

- Kh-35U / Kh-32: guidance와 seeker observer가 raw physical `em.x/y/z/vx/vy/vz`를 직접 소비
- RAM Block 1A: B1 own-nav profile 미적용, vector PN과 sea-clearance가 raw own velocity/altitude를 직접 소비
- C52 INBOUND INS ASM fixture는 target memory를 고정할 뿐 missile own-navigation을 모델링하지 않음
- ASM passive RF correction에는 truth-derived bearing/range dependency가 별도로 남아 있음

상세 감사: `docs/wip14/B1/AEGIS_WIP14B1_OWN_NAV_COVERAGE_AUDIT.md`

---

# 3. B2 — Generic Missile Own-Navigation & VLS Release Scheduler

예정 결과 파일: `Aegis_SIM_v48_WIP14B2.html`

B2는 두 기능을 함께 닫는다.

1. **Kh-35U / Kh-32 / RAM의 exact-own-state leakage 제거**
2. **모든 실제 VLS 발사 경로에 0.6~1.0 s급 고정-step 발사 간격 적용**

B2는 weapon-link packet transport를 구현하지 않는다. 그것은 B3 범위다.

## 3.1 B2a — Generic Missile Navigation Authority

현재 SAM 전용 `samNavB1OwnState()` 개념을 범용 missile own-navigation layer로 승격한다.

권장 구조:

```text
physical missile state
        ↓
measurement / dynamics boundary
        ↓
generic onboard navigation adapter
        ↓
weapon-specific nav profile
        ↓
guidance / seeker re-anchor / autopilot
```

공통 profile은 최소 다음 항목을 선언할 수 있어야 한다.

- navigation mode: INS / GPS-aided INS / 기타 aid
- initial position error
- initial velocity error
- deterministic bias / noise
- drift / uncertainty growth
- update cadence
- aid enable/disable
- aid error/correction strength
- vertical channel 특성
- diagnostic truth comparison 허용 여부

현재 네 SAM/ESSM profile의 B1 동작은 compatibility adapter로 **의도적 변화 없이 보존**한다.

금지 규칙:

- guidance geometry가 raw physical `x/y/z/vx/vy/vz`를 직접 읽지 않는다.
- return-link용 onboard state에 physical state를 그대로 포장하지 않는다.
- profile 이름이나 missile type을 이유로 truth boundary를 우회하지 않는다.

허용 규칙:

- 운동 적분
- RF/IR/ESM 물리 신호 합성
- 충돌/신관/피해
- diagnostic truth-vs-estimate 비교

## 3.2 B2b — Kh-35U / Kh-32 ASM Migration

Kh-35U와 Kh-32에 별도 error-bearing ASM own-navigation profile을 추가한다.

초기 profile 수치는 공개 근거가 없는 부분은 `SIM_TUNED`로 명시하고, 두 무장을 한 profile로 강제하지 않는다.

다음 consumer를 onboard own-state로 교체한다.

- `asmSeekerObserverState()`
- seeker EKF observer position/velocity
- `asmGuidanceRangeKm()`
- `asmGuidanceHorizontalRangeKm()`
- `asmSeekerHorizontalGuidanceAngle()`
- `asmSeekerCueAngles()`
- `asmSeekerHorizontalPnRate()`
- `asmPassedTarget3D()`
- `updateEnemyMissileBaseC52()`의 range/bearing/phase/vertical-guidance 판단
- 기타 ASM guidance에서 raw `em.x/y/z/vx/vy/vz`를 읽는 경로

### Target INS와 Own INS 분리

현재 `insTgtX/Y`와 `_c52InsMemory`는 **표적 기억 좌표**다.

B2에서는 반드시:

```text
target memory / seeker target estimate
≠
missile own navigation state
```

로 분리한다.

C52 fixture의 “발사 시점 자함 위치 기억 / 실시간 갱신 없음” 계약은 그대로 유지하되, 그 좌표까지 비행하는 missile own-state에는 실제 오차와 drift가 존재해야 한다.

### ASM passive RF / ESM truth boundary

own-state 수정과 함께 passive RF correction도 measurement boundary로 옮긴다.

- physical geometry는 RF/ESM measurement synthesis 내부에서만 사용 가능
- guidance에는 noisy bearing/confidence/availability 등 관측 결과만 전달
- exact physical ship bearing을 직접 guidance correction으로 전달 금지
- exact physical missile↔ship range를 hidden correction authority로 사용 금지
- 필요한 detection/SNR gate는 measurement adapter 내부 결과로 표현

이 수정은 seeker 성능을 임의로 약화시키는 것이 아니라 **정보 출처를 현실적인 센서 경계로 옮기는 작업**이다.

## 3.3 B2c — RAM Own-Navigation Migration

RAM Block 1A도 같은 generic own-nav adapter를 사용한다.

최소 수정 대상:

- vector PN projection의 own flight-path vector
- own velocity estimate
- vertical speed estimate
- sea-clearance / projected-altitude 계산
- seeker measurement를 absolute/local guidance frame으로 변환할 때 필요한 own-state

RF/IR echo 합성에서 physical geometry를 사용하는 것은 허용하되, 최종 guidance는 error-bearing own-state와 seeker measurement를 소비한다.

RAM은 ASM과 같은 장거리 INS target-memory 구조를 강제로 사용하지 않는다. 같은 adapter를 쓰되 필요한 state/channel만 profile로 활성화한다.

## 3.4 B2d — Common VLS Release Scheduler

현재 B1에는 실제 VLS 발사 간격의 단일 권위가 없다.

감사 기준:

- AUTO `WIP119_AUTONOMY_POLICY.salvoSpacingS`는 현재 `0.35 s`
- MANUAL / SEMIAUTO / 3D FIRE는 각각 실제 spawn 경로를 즉시 호출할 수 있음
- WIP156의 약 0.2 s급 “ignition → cell exit” 물리는 존재하지만 **연속 발사 간격과는 별도 현상**

B2에서는 실제 VLS ignition/release 앞에 공통 scheduler를 둔다.

권장 계약:

```text
operator / SEMIAUTO / AUTO / 3D
        ↓
VLS release request
        ↓
common fixed-step scheduler
        ↓
release gates 재검사
        ↓
cell 선택/소모
        ↓
spawn + ignition
```

### 발사 간격

초기 기본값:

```text
ship-wide minimum VLS release separation = 0.8 s  (SIM_TUNED)
```

프로필/설정에서 **0.6~1.0 s 범위로 조정 가능**하게 한다.

- 랜덤 wall-clock delay를 사용하지 않는다.
- 첫 구현에서 매 발 0.6~1.0 s를 난수로 흔들지 않는다.
- `simStepCounter × SIM_FIXED_DT` 또는 동등한 fixed-step simulation time이 권위다.
- 1× / 8× / 16×에서 같은 release step을 가져야 한다.
- 64×는 결과 동일성과 scheduler 부하를 별도 확인한다.

### 모든 실제 발사 경로 통합

다음 경로가 동일 scheduler를 우회하지 못하게 한다.

- 2D MANUAL FIRE
- 3D FIRE
- SEMIAUTO release
- AUTO salvo
- SM-2MR
- SM-2ER
- SM-6
- ESSM

테스트/fixture가 low-level spawn을 직접 호출해야 한다면 명시적 diagnostic/test bypass만 허용하고 실제 플레이 경로에는 사용하지 않는다.

### 요청과 실제 발사를 분리

발사 요청 시점에는 VLS cell을 소모하지 않는다.

실제 release 시점에 다시 검사한다.

- track 존재/quality
- identity / engagement authority
- EMCON policy
- VLS power/damage/availability
- ready cell
- reserve policy
- SPG-62 reservation/illumination requirement
- 해당 무장 profile의 기타 gate

검사 통과 직전에 cell을 선택·소모하고 spawn한다.

따라서 cooldown 중 거부되거나 권한이 사라진 요청은 탄약을 먹지 않는다.

### MANUAL / SEMIAUTO / AUTO 정책

- MANUAL / 3D: cooldown 중 추가 입력은 `VLS_CYCLE`로 거부하고 남은 시간을 표시한다. 버튼 spam으로 무한 queue를 만들지 않는다.
- SEMIAUTO: operator 승인 1회당 1발 release request. cooldown이면 발사 보류 상태를 명확히 표시한다.
- AUTO: 기존 pending salvo를 유지할 수 있으나 실제 release는 common scheduler가 허용하는 시점에만 발생한다.
- 기존 `WIP119_AUTONOMY_POLICY.salvoSpacingS=.35`는 더 이상 physical launch timing authority가 아니다. AUTO의 논리적 salvo 요청 주기와 실제 VLS release 주기를 분리하거나 common scheduler 값에서 파생한다.

### 기존 cell-exit 물리 보존

WIP156의 in-cell ignition/travel과 cell-exit 판정은 그대로 유지한다.

즉:

```text
발사 A ignition
  ↓ 약 0.2 s
A cell exit

발사 A ignition
  ↓ 약 0.8 s (공통 VLS release separation)
발사 B ignition
```

두 시간축을 하나로 합치지 않는다.

## 3.5 B2에서 변경하지 않는 것

- SM-2MR/ER/SM-6/ESSM의 기존 공력·추진·질량·6DOF 계수
- B4 loft profile/tuning
- B3 packet delay/loss/sequence/return-link
- VLS loadout 수량
- SPG-62 물리 servo/geometry
- 기존 terminal-event / damage authority
- AIM-174B 운용 등록

## 3.6 B2 필수 검증

### Own-navigation

1. SM-2MR/ER/SM-6/ESSM B1 regression이 허용 오차 안에 유지된다.
2. Kh-35U와 Kh-32 onboard position/velocity는 physical truth와 의도적인 non-zero 오차를 가진다.
3. 같은 seed/fixed-step에서 ASM nav error history가 결정적으로 반복된다.
4. ASM guidance/seeker consumer가 raw physical own state를 직접 읽는 경로가 제거되거나 measurement/dynamics 허용 경계로 제한된다.
5. C52 target-memory fixture에서 launcher/target truth를 움직여도 기억 좌표는 갱신되지 않는다.
6. 같은 fixture에서 missile own-nav error는 별도로 존재한다.
7. ASM passive RF correction은 exact truth bearing/range를 guidance authority로 전달하지 않는다.
8. RAM PN/sea-clearance consumer가 generic onboard own-state를 사용한다.
9. physical truth 사용은 measurement synthesis / dynamics / collision / fuze / damage / diagnostics에만 남는다.

### VLS scheduler

10. 실제 플레이 경로의 연속 ignition/release 간격이 profile 설정값보다 짧지 않다.
11. 기본 profile은 약 `0.8 s`, 허용 설정 범위는 `0.6~1.0 s`다.
12. 2D MANUAL, 3D FIRE, SEMIAUTO, AUTO가 모두 같은 scheduler를 사용한다.
13. AUTO 기존 `0.35 s` salvo timing이 실제 missile spawn을 0.35 s 간격으로 발생시키지 않는다.
14. cooldown 중 거부된 MANUAL/3D 요청은 missile과 VLS inventory를 변경하지 않는다.
15. 실제 release 직전에 FCQ/identity/EMCON/VLS damage/cell/SPG gate를 다시 검사한다.
16. 실패한 재검사는 cell을 소모하지 않는다.
17. 1×/8×/16×에서 동일 seed의 release step/history가 같다.
18. 기존 WIP156 in-cell/cell-exit fixture는 회귀 PASS한다.

### 공통

19. core self-test failure 0.
20. A14 engagement/UI regression PASS.
21. A13 frozen physical contract PASS.
22. combat RNG stream은 nav/scheduler diagnostics 때문에 변하지 않는다.
23. browser/3D smoke 가능 환경에서는 2D/3D FIRE cooldown 표시와 실제 spawn timing을 확인한다.

## 3.7 B2 종료 조건

아래를 모두 만족할 때만 B2 CLOSED로 본다.

- ASM exact-own-state leakage 제거
- RAM guidance own-state abstraction 완료
- ASM passive RF truth boundary 정리
- 공통 missile nav adapter 활성
- VLS common release scheduler 활성
- 0.8 s 기본 inter-launch timing 및 0.6~1.0 s profile 조정 가능
- 모든 실제 VLS release path가 scheduler를 우회하지 않음
- B1/A13/A14 회귀 통과

---

# 4. B3 — Generic Weapon-Link Transport & Return-Link Capability

예정 결과 파일: `Aegis_SIM_v48_WIP14B3.html`

B3는 기존 계획의 B2를 번호만 한 칸 이동한 단계다.

양방향 기능은 **SM-6 전용으로 구현하지 않는다.**

공통 weapon-link가 uplink와 return-link를 모두 지원하고, 각 미사일 profile이 세부 스펙을 선언한다.

## 4.1 B3a — Common Packet Transport + Uplink

각 적용 미사일은 공통 weapon-link record를 가진다.

- 익명 target track ID / link/channel ID
- launch-time support plan
- 불변 support deadline
- uplink/downlink tx/rx sequence
- next transmit time
- pending delivery queue
- delay / jitter / loss / out-of-order
- last RX time / link health
- packet age / target covariance / uncertainty growth
- transport 전용 deterministic RNG stream

미사일별 link profile은 최소 다음을 설정할 수 있어야 한다.

- `uplinkEnabled`
- `returnLinkEnabled`
- transmit cadence
- payload class/capability
- delay/jitter/loss/out-of-order
- max age / TTL
- uncertainty growth
- assistance enable
- assistance limits

core transport에 `missileType === 'SM6'` 식의 양방향 전용 분기를 두지 않는다.

launcher→missile payload는 track layer 정보만 포함한다.

- target position/velocity estimate
- covariance
- sample/tx time
- sequence
- bounded PIP/TGO advisory
- support deadline
- link health

target object reference, actual target position, actual alive state, future truth trajectory는 금지한다.

## 4.2 B3b — Generic Return-Link Capability

return-link도 공통 transport의 선택 capability다.

현재 WIP14의 첫 활성 profile은 SM-6이지만 다른 미사일도 profile 변경만으로 동일 transport를 사용할 수 있어야 한다.

SM-6 첫 payload:

- onboard estimated nav position/velocity
- onboard nav uncertainty
- guidance phase
- seeker handoff/terminal acknowledgement
- nav aid/link health
- sequence/sample/tx time

B2에서 완성한 generic onboard navigation state만 payload source로 허용한다.

physical `x/y/z/vx/vy/vz`를 직접 return packet에 넣지 않는다.

## 4.3 B3c — Profile-Bounded Launcher Assistance

return-link가 활성화되어도 assistance가 자동으로 허용되는 것은 아니다.

profile이 별도로 허용하는 경우에만:

- PIP / expected TGO correction
- pursuit/loft scale bounded correction
- corridor altitude advisory
- terminal handoff advisory

를 제공한다.

confidence, packet age, target covariance, missile nav covariance로 감쇠하며 profile별 hard limit을 가진다.

return-link는 launch-time support deadline을 갱신하거나 연장할 수 없다.

deadline/link-cut 이후 pending packet은 폐기하고 missile local IOG/seeker가 권위를 가진다.

## 4.4 현재 link profile 방향

| 무장 | Own navigation | Uplink | Return link | terminal authority |
| --- | --- | --- | --- | --- |
| SM-2MR | B2 generic adapter / INS | one-way target-state | 현재 비활성, 공통 capability 사용 가능 | SPG-62/SARH |
| SM-2ER | B2 generic adapter / INS | one-way target-state | 현재 비활성, 공통 capability 사용 가능 | SPG-62/SARH |
| SM-6 | B2 generic adapter / GPS/INU | target-state + bounded advisory | **현재 활성 profile** | onboard ARH/seeker |
| ESSM Block 2 | B2 generic adapter / INS | one-way target-state | 현재 비활성, 공통 capability 사용 가능 | onboard ARH/seeker |
| RAM | B2 generic adapter | profile 미정/현재 필요 없음 | capability 사용 가능하되 현재 미활성 | onboard RF/IR |
| Kh-35U / Kh-32 | B2 generic adapter | 현재 hostile standalone ASM 경로 | capability 자체는 generic, 현재 미활성 | onboard seeker |
| AIM-174B | 참고용 | 참고 구조만 | 참고용 | 함정 VLS 등록 금지 |

## 4.5 B3 필수 검증

1. zero-delay/zero-loss에서 B2 유도 결과가 허용 오차 안에 유지된다.
2. 고정 delay/loss/out-of-order 패턴이 같은 seed에서 결정적으로 반복된다.
3. 1×/8×/16× packet history와 비행 milestone이 같다.
4. stale/out-of-order packet이 권위 상태를 되돌리지 않는다.
5. packet age/covariance가 규칙대로 증가한다.
6. hard-cut/support deadline 뒤 global track/truth 갱신 0회.
7. 현재 profile 기준 SM-2MR/ER/ESSM return packet 0회, SM-6만 활성.
8. synthetic profile에서 다른 missile의 `returnLinkEnabled`를 켜면 core 수정 없이 동일 queue/scheduler/envelope를 사용한다.
9. return nav position/velocity가 B2 onboard solution과 같고 physical truth와 의도적 오차를 가진다.
10. return 수신 전후 support deadline 불변.
11. assistance age-out / confidence fade / hard limit 준수.
12. terminal seeker authority를 launcher assistance가 덮지 않는다.

---

# 5. B4 — Per-Missile Stateful Loft

예정 결과 파일: `Aegis_SIM_v48_WIP14B4.html`

B4 번호와 목적은 기존 계획에서 변경하지 않는다.

공통 상태기계:

```text
CLIMB
  ↓
CRUISE / ENERGY-SHELF
  ↓
DIVE / TERMINAL
```

DIVE 진입 뒤 CLIMB 재진입은 금지한다.

| 무장 | 별도 profile 방향 |
| --- | --- |
| SM-2MR | 중거리 완만한 climb/short shelf, SARH 지원과 terminal geometry 고려 |
| SM-2ER | booster energy를 이용한 장거리 climb/shelf, q/Mach/energy reserve 기반 전이 |
| SM-6 | 가장 긴 networked midcourse shelf, B3 assistance를 제한적으로 소비하되 onboard state가 권위 |
| ESSM Block 2 | direct/mild loft 중심, 불필요한 Standard 계열 고고도 climb 금지 |

각 profile 입력에는 최소 다음을 포함한다.

- launch range
- target altitude estimate
- remaining range / TGO
- Mach
- dynamic pressure
- energy height
- onboard nav uncertainty
- target track uncertainty
- seeker/support state

공통 고정 `tgo <= 30 s` clamp나 단일 pitch bias로 모든 미사일의 loft authority를 결정하지 않는다.

180 km / target altitude 2 km 회귀에서는 특정 apex 숫자를 하드코딩하지 않는다.

검증 항목:

- SM-2ER/SM-6의 기존 약 2.4 km 저고도 장거리 수평비행 패턴 탈출
- CLIMB/CRUISE/DIVE transition 기록
- finite apex/q/Mach/specific-energy/TGO
- DIVE 뒤 re-loft 0회
- 도달/실패 이유가 energy/support/seeker/nav state로 설명 가능
- truth coordinate injection으로 궤적을 보정하지 않음

권장 envelope:

```text
range: 40 / 80 / 120 / 180 km
target altitude: 0.05 / 2 / 10 km
time scale: 1× / 8× / 16×
```

---

# 6. 참고 공대공 HTML 사용 원칙

`references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`에서는 개념만 참고한다.

- physical state와 INS/GPS onboard state 분리
- common one-way/two-way packet transport
- launch-time support deadline 불변
- return-link as profile capability
- bounded assistance
- stateful `CLIMB → CRUISE → DIVE`
- DIVE 이후 re-loft 금지

공대공 좌표계, radar/FCS, AIM-174B 성능값과 상수를 그대로 이식하지 않는다.

AIM-174B는 함정 VLS inventory/교전 UI에 추가하지 않는다.

---

# 7. 현재 branch에서 아직 하지 않은 것

- B2 runtime 구현
- B3 packet transport 구현
- B4 loft 구현
- B1 HTML 대형 파일 원격 업로드
- main 수정
- PR/merge/release/tag 생성

다음 실제 코드 작업은 **B2 — Generic Missile Own-Navigation & VLS Release Scheduler**다.
