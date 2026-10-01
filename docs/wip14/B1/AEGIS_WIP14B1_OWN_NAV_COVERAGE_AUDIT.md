# AEGIS v48 WIP14B1 — All-Missile Own-Navigation Coverage Audit

작성일: 2026-09-30 (KST)

## 기준

- 감사 대상: 사용자 제공 `Aegis_SIM_v48_WIP14B1.html`
- HTML SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`
- embedded C55 game-main source SHA-256: `dcec641772f3e9e3324ad1e43403fd1c70b661b692ff2c3edd85dceeee1b03d9`
- 목적: 현재 운용되는 미사일이 guidance/seeker 계산에서 실제 physical own position/velocity를 직접 알고 있는지 확인

## 결론

B1 own-navigation boundary는 현재 **SM-2MR, SM-2ER, SM-6, ESSM Block 2의 v1 SAM guidance path**에만 적용되어 있다.

Kh-35U와 Kh-32는 별도의 error-bearing own-navigation state가 없고, guidance/seeker 계산이 physical `em.x/y/z/vx/vy/vz`를 직접 소비한다. 따라서 대함미사일에는 exact-own-state leakage가 남아 있다.

RAM Block 1A도 B1 SAM nav profile 대상이 아니며, angular seeker 자체는 측정 기반이지만 PN flight-path projection과 sea-clearance guidance가 physical own velocity/altitude를 직접 소비한다. ASM보다 범위는 좁지만 공통 own-nav boundary 관점에서는 미완료다.

## 현재 PASS 범위 — SM-2MR / SM-2ER / SM-6 / ESSM

B1의 `SAM_NAV_B1_PROFILES`는 다음 profile을 가진다.

- `SM2MR_INS_B1`
- `SM2ER_INS_B1`
- `SM6_GPS_INU_B1`
- `ESSM_INS_B1`

`samNavB1OwnState()`가 error-bearing onboard position/velocity를 제공하고, PN/APN/ZEM/Kappa/PIP/autopilot 등 주요 v1 guidance consumer가 이를 사용한다. SARH/ARH 상대측정도 physical measurement synthesis 뒤 onboard nav frame으로 re-anchor된다.

physical truth는 dynamics, RF measurement synthesis, collision/fuze, diagnostic comparison에 남는 것이 정상이다.

## FAIL — Kh-35U / Kh-32

두 ASM은 같은 common ASM guidance/seeker core를 사용하며 다음 exact-own-state 경로가 확인됐다.

### 1. Seeker observer state

`asmSeekerObserverState(em)`가 직접 다음을 반환한다.

- `worldToMeters(em.x)`
- `worldToMeters(em.y)`
- `em.z`
- `em.vx / em.vy / em.vz`

이 값은 seeker EKF init/prediction/Jacobian과 horizontal PN relative velocity 계산에 사용된다. 따라서 RF 측정 자체에 오차가 있어도 observer own-nav error는 없다.

### 2. Guidance range / bearing

다음 함수가 physical own coordinate를 target estimate 또는 INS target memory와 직접 비교한다.

- `asmGuidanceRangeKm()`
- `asmGuidanceHorizontalRangeKm()`
- `asmSeekerHorizontalGuidanceAngle()`
- `asmSeekerCueAngles()`
- `asmSeekerHorizontalPnRate()`
- `asmPassedTarget3D()`

즉 target estimate가 불완전해도 missile own position/velocity는 exact다.

### 3. Main ASM guidance loop

`updateEnemyMissileBaseC52()`에서도 다음 값이 physical own state로 직접 계산된다.

- ship/INS target까지 거리
- ship/INS target 방위
- seeker aim까지 heading
- climb/level/dive/terminal 전이용 range
- vertical guidance의 현재 altitude
- passed-target/CPA 판단

따라서 Kh-35U와 Kh-32 모두 현재 구조에서는 error-bearing own INS/GPS solution을 갖지 않는다.

### 4. C52 "INBOUND INS ASM" fixture의 의미

`wip13cSpawnInboundInsAsm()`와 `_c52InsMemory`는 **발사 시점의 표적 좌표를 기억하고 실시간 자함 위치 갱신을 막는 fixture**다.

이는 target-memory truth feed를 막는 장치이지 missile own-navigation model이 아니다. fixture에서도 missile 자신의 위치/속도는 common ASM guidance가 physical state에서 직접 읽는다.

## 별도 발견 — ASM passive ESM target-truth dependency

own-state 문제와 별개로, Kh-32/Kh-35U passive RF bearing correction은 현재:

- physical ownship coordinate에서 `trueAng`를 생성
- physical missile↔ship `dKm`로 correction availability/gain을 결정

하는 경로가 있다.

주석상 bearing-only correction이지만 현재 구현은 sensor measurement adapter가 아닌 direct truth-derived bearing/range gate에 가깝다. 이후 ASM navigation/truth audit에서 별도 폐쇄가 필요하다.

## PARTIAL FAIL — RAM Block 1A

RAM은 B1 `SAM_NAV_B1_PROFILES`에 포함되지 않는다.

`updateRamMeasurementSeeker()`에서:

- physical `rm.vx/vy/vz`로 missile flight-path vector를 만들고 vector PN acceleration을 투영
- physical `rm.z`와 `rm.vz`로 projected altitude와 sea-clearance guard를 계산

한다.

RF/IR physical echo synthesis에서 truth own position을 사용하는 것은 허용 가능하지만, guidance consumer에 전달되는 own kinematics에는 별도의 error-bearing onboard state가 없다. 따라서 공통 missile own-nav boundary를 만들 때 RAM도 포함해 재검토해야 한다.

## 권장 후속 계약

B2 weapon-link를 확장하기 전에 또는 같은 branch의 선행 fix로 다음 공통 계약을 두는 것이 안전하다.

1. SAM 전용 `samNavB1OwnState()` 개념을 모든 유도탄이 사용할 수 있는 generic missile own-navigation adapter로 일반화한다.
2. missile profile이 INS/GPS/기타 aid 활성 여부, initial error, bias/noise, update cadence를 선언한다.
3. guidance geometry는 raw `x/y/z/vx/vy/vz`를 직접 읽지 않고 generic onboard own-state만 소비한다.
4. physical truth 사용은 dynamics, measurement synthesis, collision/fuze, diagnostic comparison으로 제한한다.
5. ASM의 `insTgtX/Y` target memory와 missile own-navigation state를 명확히 분리한다.
6. seeker relative measurements는 B1 SAM과 동일한 원칙으로 onboard own frame에 re-anchor한다.
7. RAM도 동일한 common adapter를 소비하되 필요한 profile 세부값은 별도 검증 후 정한다.
8. ASM passive ESM correction의 truth-derived bearing/range gate는 measurement-level sensor adapter로 교체하거나 명시적으로 진단 전용으로 제한한다.

## 판정

- SM-2MR: own-state boundary 확인
- SM-2ER: own-state boundary 확인
- SM-6: own-state boundary 확인
- ESSM Block 2: own-state boundary 확인
- Kh-35U: **exact-own-state leakage 존재**
- Kh-32: **exact-own-state leakage 존재**
- RAM Block 1A: **own-nav abstraction 미적용 / exact own kinematics guidance 사용**

B1의 기존 PASS는 위 SAM/ESSM 범위에서는 유지할 수 있지만, "모든 미사일 own-navigation boundary 완료"로 해석하면 안 된다.
