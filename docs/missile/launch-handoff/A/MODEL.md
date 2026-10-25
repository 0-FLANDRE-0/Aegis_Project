# LAUNCH_HANDOFF_A 인계 계약

이 문서는 게임용 `SIM_TUNED` 제어 계약이다. 실제 장비의 성능 보증이 아니다. 생산 변경은 `updateMissileBodyB3`의 준비 판정과 순수 함수 `samLaunchHandoffGateA`뿐이다. 임계값은 비행 성공률에 맞춰 반복 조정하지 않았다.

## 입력과 좌표

기존 `samNavB1OwnState`의 온보드 항법 속도(m/s), 수신 관측으로 계산한 `cor.desiredPitch`/`cor.bearing`(rad), 기존 기체 자세, MSL 고도(m), `_samVlsControlConfig`를 사용한다. 새 함수에서 표적 truth, 실제 표적 id, 적 배열을 읽지 않는다. 예정 경로 단위벡터는 `(cos γ cos ψ, cos γ sin ψ, sin γ)`다.

## 공중 Standard의 AND 조건

| 조건 | 판정 / 근거 |
|---|---|
| 유한 입력 | 항법 속도, 고도, 자세, 경로각, 기존 설정이 유한해야 함 |
| 함체 이격 | 기존 `exitAltM` 이상. 기존 VLS 수직 이탈/회전 시작/해면 안전 로직도 보존 |
| 기체 자세 | 경로 대비 heading/pitch 오차가 기존 `headingTol`/`pitchTol` 이내 |
| 3D 속도 정렬 | 속도·예정 경로의 내적 각도 ≤ 기존 `pitchTol` |
| 받음각 보호 | 기체 축·항법 속도의 각도 ≤ 기존 동역학 `aoaMaxDyn`; 아직 유효 샘플이 없으면 기존 두 정렬 허용각의 작은 값 |
| 전진 속도 | `v·u ≥ cfg.minForwardMps` 및 양수. 기존 수평 속도 하한을 예정 3D 경로 방향 성분으로 해석 |
| 하류 좌표계 | 수평 속도 ≥1m/s. 기존 `applyAccelCommandToAutopilotV1`의 `vH<1` null 반환 경계와 동일; 물리 가용 G나 발사 속력의 새 튜닝이 아님 |
| 안정화 시간 | 기존 `pitMinS` 이상 |

기존 40° 안팎의 절대 수평 경로각 제한을 정상 고각 공중 사격에 적용하지 않는다. `deadlineExceeded`는 여전히 경고이며 해제 조건이 아니다. 저속/후진/미정렬/이격 부족은 deadline 이후에도 차단한다. 정확히 수직이고 수평 좌표기저가 정의되지 않는 상태를 정상 인계로 위장하지 않는다.

프로파일별 기존 허용각·속력·이격/시간 값은 변경하지 않았다. `cfg`가 비행 상태에 따라 변하는 기존 동작도 그대로다. 별도 타깃 거리/고도 특례, 명중 여부 분기, 강제 시간 초과 해제, 새 RNG는 없다.

## 상태와 제어권

`updateMissileBodyB3`가 준비 여부를 소비한다. 기존 성공 분기에서 `pitchoverPhase=false`, `pitchoverDone=true`, 완료 시각과 corridor 종료를 기록한다. 이어지는 기존 함수 본문이 launch authority/overlap/blend를 정리하고 선택된 유도 커널로 같은 틱에 전달한다. 구동기 필터·기체 각속도·속도 벡터를 재설정하지 않아 물리적 순간 회전/가속을 만들지 않는다. 별도 블렌드 이득이나 시간 상수를 추가하지 않았다.

계측의 `beforeGate → preDynamics → postDynamics`는 서로 다른 지점이다. 전환 틱의 전/후 차이는 정상이다. 인계 후 같은 틱의 `launchAuthority=false`, `overlap=false`, blend0과 Kappa/terminal 명령 소비를 확인했다. 초기 VLS 내부처럼 동역학 호출이 없는 샘플의 owner는 `IN_CELL/NOT_EVALUATED`로 해석해야 한다. 일부 raw의 `GUIDANCE_OR_FALLBACK`는 실제 제어기 활성 판정이 아니다.

## 별도 계약 보존

- 범위: guidanceCore v1의 SM2MR/SM2ER/SM6 공중 사격만.
- ESSM과 대수상은 기존 gate, `surfaceLaunchVectorAlignedWip13C6`, 기존 보호를 유지한다.
- `_samVlsControlConfig`, `_samLeadPointForLaunch`, `_samSetLaunchCorridorCommand`, 가속도 bridge, 6DOF, D/Z/T, PN/APN/Kappa/로프트/추진·항력·질량/G/시커/신관·파편/Pk/배터리의 기존 선언은 byte 동일하다.
- `_launchHandoffA`는 미사일에 붙은 detached 진단 값이며 스케줄러·표적선택·발사 권한·난수·저장 스키마를 변경하지 않는다.

## 설계 이력과 한계

비행 전 계약은 `design-before-candidate-flights.json`에 보존했다. 내부 revision1은 마지막 하류 수평 기저 조건이 빠져 있었다. 소비자 소스의 기존 null 경계를 확인해 revision2에 추가했고 최종 HTML로 검증을 다시 수행했다. 성공률에 맞춘 문턱 조정이 아니다. revision1 evidence는 최종 제품 검수에 합산하지 않았다.

안전한 인계가 명중을 보장하지 않는다. 100m/20km SM-6 신규 비명중, 기존 240km SM-6 2발 손실과 원래 회귀 6개 실패 때문에 전면 승격은 보류한다. 10m/20km의 일부 사례는 실제 자세/속도 미정렬로 인계하지 않는다. 이 경우도 시간으로 강제 해제하지 않았다.
