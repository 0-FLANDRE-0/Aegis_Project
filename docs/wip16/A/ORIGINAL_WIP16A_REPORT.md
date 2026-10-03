# AEGIS v48 WIP16A — Phalanx Fire-Control Stabilization Report

작성: 2026-10-03 (KST)

## 1. 기준 / 목적

- 안정 기준: `Aegis_SIM_v48.html` (로컬 byte-identical WIP15C 기준)
- 기준 SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- 결과: `Aegis_SIM_v48_WIP16A.html`
- 결과 크기: `7,354,882 bytes`
- 결과 SHA-256: `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`
- decoded main SHA-256: `8e5fb5f435c6f164879d4246feb5f548ceabef087701ac760c0132cb1dac0669`
- 목표 안정 버전: **v48.1**

사용자 관찰은 "Phalanx CIWS가 너무 많은 탄을 쏘면서 실제 명중탄은 지나치게 적다"는 것이었다. 이번 단계는 탄종 분산이나 센서 성능을 임의 상향하기보다, **사격을 허가하는 fire-control gate와 실제 피격 형상**을 우선 감사·수정한다.

## 2. 감사에서 확인한 핵심 원인

### 2.1 고정 각도 fire gate가 20 mm 근접방어에는 너무 느슨함

기존 Phalanx는 TRACK→ENGAGE와 실제 발사에서 수 도 단위의 residual turret error를 허용할 수 있었다. 반면 현재 Mk 244 모델은 `3.0 mil / 80% diameter` 고정 분산을 가진다. 수 km 거리에서 수 도 단위 gate는 탄착군 중심을 표적에서 수십~수백 m 벗어나게 허용할 수 있으므로, "추적 품질은 높은데 계속 쏘면서 안 맞는" 구간을 만든다.

### 2.2 projectile collision이 몸통 capsule 위주

기존 physical hit는 Kh-35U/Kh-32 몸통 capsule과의 swept intersection을 권위로 사용했다. 그러나 WIP112에는 이미 exposed `fins` 계통의 실제 system box가 있고 WIP113은 그 손상을 control authority 저하로 소비한다. 따라서 단순 hitbox 확대 대신 **기존 exposed-fin geometry를 실제 20 mm projectile surface로 연결**할 수 있었다.

### 2.3 WIP104 spotting은 존재하지만 이번에 숫자를 버프하지 않음

closed-loop projectile spotting은 기존에도 존재한다. 이번 수정에서는 `minSamples`, noise, correction gain, max correction 등 WIP104 상수를 바꾸지 않았다. 사격 시작점 자체가 더 정렬된 조건으로 바뀌면서 기존 spotting이 그대로 후속 보정을 수행하도록 유지했다.

## 3. WIP16A 변경

### 3.1 거리 기반 burst-centre gate

새 `WIP16_PHALANX_FIRE_CONTROL_MODEL`은 현재 사거리와 고정 Mk244 분산으로 80% group radius를 계산한다. 발사 허용은:

- turret angular residual을 현재 거리의 **metres of centre error**로 변환
- Mk244 group radius에 비례한 허용 centre-error window
- ballistic solution의 `predictedMissM` 별도 제한
- ENGAGE 상태에는 작은 hysteresis

를 함께 만족해야 한다.

따라서 단순히 `3° / 4°` 아래라는 이유만으로 탄을 뿌리지 않는다.

### 3.2 Mk244 분산은 그대로

`dispersion80DiameterMil = 3.0`을 **변경하지 않았다.** 이번 결과는 탄 자체를 더 정확하게 만든 결과가 아니다.

### 3.3 실제 control-surface hit

`ciwsBulletSweptHit()`는 먼저 기존 body capsule을 검사한다. body miss인 경우에만 기존 WIP112 `fins` system box를 missile-local frame에서 swept test한다.

- BODY hit → 기존 Phalanx direct critical / structure 경로 보존
- CONTROL_SURFACE hit → 즉시 critical kill 확률 `0`; 직접 구조피해를 작게 적용
- WIP112 projectile observer가 실제 경로를 분류하고 fins system damage를 누적
- WIP113이 fins damage를 available-G/control authority로 소비

즉 단순히 "날개까지 몸통 hitbox로 취급"하지 않는다.

### 3.4 진단 fixture 격리 보강

감사 중 WIP103 CIWS 측정 fixture가 case reset에서 `trackingTrackId`, gun-local RNG state와 correlated aim-error state를 완전히 비우지 않는 것을 확인했다. 이것은 production gameplay 변경이 아니라 diagnostic isolation 문제다. WIP16A에서는 해당 상태를 case마다 명시적으로 지워 고정-seed 측정의 이전 case 의존성을 줄였다.

공정한 v48 비교에는 안정판에 **이 diagnostic reset만 적용한 임시 검사본**을 사용했다. 안정판 gameplay fire-control/ballistics/hit logic은 변경하지 않았다.

## 4. 4 km / 280 m/s 동일 조건 비교

조건: Kh-35U, 고도 12 m, 방위 -20/0/+20°, seed 23001/23002, SeaRAM/soft-kill 비활성.

| | v48 + 진단 reset만 | WIP16A acceptance |
|---|---:|---:|
| 발사탄 | 3,472 | 1,098 |
| physical hit | 10 | 15 |
| 탄당 physical hit rate | 0.288% | **1.366%** |
| fire-frame turret error 중앙값 | 0.0847° | **0.0338°** |
| 함정 피격 | 0/6 | 0/6 |

- physical hit rate: 약 **4.74×**
- 발사탄: 약 **68.4% 감소**
- 발사 중 turret residual 중앙값: 약 **60.1% 감소**
- WIP16A hit region: BODY 7, CONTROL_SURFACE 8

이 6조건에서 안정판도 전부 KILL/STRUCT_FAIL로 막았으므로 이 표를 "요격확률이 4.7배가 됐다"고 읽으면 안 된다. **탄약 효율과 실제 physical hit rate가 개선되었다는 회귀**다.

## 5. 늦은 대응은 여전히 실패 가능

1.5 km / 350 m/s, 정면, 4 seed의 짧은 경고 조건에서는:

- 발사탄 149
- physical hit 3
- 결과 {"PENETRATION_SUCCESS": 1, "KILL": 2, "INTERCEPT_FAIL_NO_HULL_HIT": 1}
- **함정 관통 1/4**

즉 WIP16A가 Phalanx를 보장요격 체계로 만들지는 않았다.

## 6. spotting / 기존 체계 보존

WIP104 spotting 상수는 변경하지 않았다. 최종 acceptance에서 최초 closed-loop correction은 발사 후 중앙값 약 **1.90 s**였다.

최종 runtime suite에서 다음을 다시 확인했다.

- core self-test failure 0
- Mk244 3.0 mil 고정값 보존
- CIWS B3 maneuver estimator 보존
- CIWS B3 damage ordering 보존
- WIP13A surface/flood diagnostics 및 time-scale regression 보존
- BODY와 CONTROL_SURFACE physical hit 모두 발생
- page error 0

## 7. 검증

- package / C55 manifest / source preservation / JS syntax: **64/64 PASS**
- runtime acceptance: **13/13 PASS**
- stable v48로부터 support builder exact rebuild: **PASS**

지원 묶음에는 edit script, exact builder, package/runtime test, raw evidence를 포함한다.

## 8. 판정 / 다음 단계

**WIP16A scoped validation passed / 사용자 gameplay 확인 대기.**

이 파일은 아직 정식 v48.1이 아니다. 실제 플레이에서 Phalanx 체감, 여러 방위/속도/기동 ASM, 탄약 소모를 확인한 뒤 사용자가 승인하면 v48.1 승격·릴리스를 진행한다.
