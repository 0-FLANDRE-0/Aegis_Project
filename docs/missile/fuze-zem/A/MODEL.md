# SAM_SIGNAL_A 설계와 경계

이 값들은 실물 신관 제원이 아닌 게임용 **SIM_TUNED 정규화 수신기 모델**이다. 기존 코드에는 표적 RCS를 약하게 Pd에 반영하는 식과 미사일별 고정 난수는 있었으나, 수신 전력·잡음 전력·수신기 대역폭의 절대 단위 모델은 없었다. 따라서 실제 장비 수치를 주장하지 않는다. `deterministic-design-before-flights.json`에 수치와 소스 해시를 먼저 고정했고, D의 사격 결과를 본 뒤 성공률에 맞춰 계수를 변경하지 않았다.

## 입력과 계산

기존 신관 무장 조건, 4종별 탐지 반경 R, 기존 TDD의 기체축 기준 polar 중심/반각을 그대로 사용한다. rel은 **미사일−표적**, SI m이며 기존 빔 함수가 부호를 뒤집어 표적 방향을 구한다. RCS는 기존 `getASMRcs` / `targetRcsM2`의 관측 방위·고각 의존값이다. 표적 위치와 형상은 이 물리 신관/충돌 경계에서만 사용하며 관측 기반 종료기로 넘기지 않는다.

```
vr = dot(rel, relativeVelocity) / |rel|
coherence = 1 / sqrt(1 + (|vr| × coherentLookS / rangeCellM)²)
SNR = referenceSnrAtGate × (RCS / 기존 rcsRefM2) × (R / r)⁴
      × coherence / (1 + clutterToNoise)
```

범위 밖/기존 TDD 빔 밖에서는 유효 신호가 0이다. RCS는 선형, 거리 감쇠는 단상 레이더 방정식의 4제곱 구조다. 짧은 coherent look 중 거리셀 이동은 신호 결맞음을 낮춘다. 절대 RF 출력 대신 기존 기종별 반경·기준 RCS에 정규화했다. **basePd/minPd/maxPd나 기존 draw는 이 식에 사용하지 않는다.**

C/N은 기존 저고도·해상상태 게이트와 그레이징 기하를 사용한 별도의 SIM_TUNED 배경잡음 비다. 저고도/거친 해면/수평 시선에서 증가한다. 기존의 확률적 해면 클러터 오탐·조기 기폭과 다른 항목이며, 그 난수 경로를 대체하지 않는다. 굴절·다중경로·도플러 필터·실제 수신기 대역폭은 모델링하지 않는다.

## 지속시간·누적

유효 SNR≥1인 동안 `E += min(32, max(SNR−1,0)) × dt`를 누적한다. **E≥0.004 excess-SNR·s와 연속 유효 신호≥1ms를 모두 만족**해야 acquisition이 성립한다. 앞 조건은 약한 신호의 노출 시간을 요구하고, 뒤 조건은 강한 단발 샘플만으로 탐지되는 것을 막는 0.5ms look 2개 조건이다. 과도한 순간 SNR은 적분률을 제한한다. 수치는 물리적 구조를 가진 게임 설계 가정이며, 실제 장비 감도나 명중률로 보정한 값이 아니다.

- 유효 신호 없음/빔 이탈: E를 시정수 8ms로 지수 감쇠, 연속 유효 시간은 즉시 0.
- 마지막 유효 신호 이후 50ms: 남은 E도 0.
- 무장 전: acquisition 불가. 신호 없음과 같은 감쇠.
- 탐지 성립 뒤: 기존 CPA 경로가 사용할 획득 증거를 유지한다. 이는 강제 기폭이 아니다.
- 대상별 WeakMap 채널의 처리 시각으로 겹친 구간의 이중 누적을 막는다. 작전 저장 스키마는 변경하지 않는다.

| 이름 | 값 | 단위·근거 |
|---|---:|---|
| referenceSnrAtGate / minSnr | 1 / 1 | 정규화 기준 / 유효 신호 경계 |
| integrationExcessSnrSeconds | .004 | excess-SNR·s, 시간 적분 요구 |
| coherentLookS / minValidS | .0005 / .001 | s, 2 look 연속 조건 |
| maxExcessSnr | 32 | 강신호 적분률 상한 |
| rangeCellM | 2 | m, range migration 정규화 |
| clutterNoiseRatio | 1 | C/N 정규화 |
| memoryDecayS / resetGapS | .008 / .050 | s, 유실 시 메모리 규칙 |
| quadratureStepS | .00025 | s, render/60Hz 추첨과 무관한 시간 적분 격자 |
| maxQuadratureSegments | 4096 | 비정상적으로 큰 입력 구간 계산량 방어 |

모두 `SIM_TUNED`. 기존 반경·빔·RCS 프로파일의 수치는 변경하지 않았다.

## swept / CPA / 처리 지연

원래 CPA와 같은 상대 선분 `rel(t)=rel_ref+v_rel×(t−reference)`를 사용해 반경 교차 구간을 해석적으로 자른다. 250µs 절대 시간 격자에서 기체 자세를 보간해 신호를 적분한다. 프레임 사이를 통과하는 고속 표적도 놓치지 않으며 **이미 지난 시간만 적분**한다. 기존 CPA가 보는 미래 `+dt`를 탐지 노출로 미리 적립하지 않는다.

공중 SAM은 원래 `dkm` 순간 거리 게이트를 swept `effDkm` 게이트로 바꾼 뒤 같은 과거 구간을 적분한다. 수상 proximity 경로도 같은 적분기를 사용하고 실제 획득 시각을 기존 처리 지연 관문에 넘긴다. 항법·시커·비행 및 기존 CPA 기폭 판단, 신관 처리 지연, 파편 도달시간, fragment geometry, Pk/구조 피해는 보존한다.

동일 연속 입력을 30/60/120Hz로 분할한 탐지 시점은 시험에서 약 15ns 범위였다. 이는 **신호 적분기**의 안정성이다. 전체 비행/기폭/피해 엔진의 타임스텝 불변성을 뜻하지 않는다. 실제 게임은 기존 60Hz를 유지한다.

## 난수 경계

- 현행 v1 SAM 4종의 공중·수상 acquisition은 `_wip99FuzeDetectionDraw`를 호출하지 않는다. 호출하면 throw하는 시험으로 확인했다.
- 함수 자체는 RAM/legacy 경로를 위해 남아 있으며, RAM을 이번 SAM 모델로 전환하지 않았다.
- `_wip99SeaClutterFalseTrigger → probabilityFromRatePerSec → _wip99FuzeClutterRandom`은 바이트 동일하다. 별도 저고도 오탐/조기 기폭이며 이번에 제거·완화하지 않았다.
- 게임 전체 RNG, 항법 오차, RF/EKF 잡음, 파편/피해/Pk 난수와 계산은 변경하지 않았다. 탐지 시점 변경으로 실제 교전 사건 순서가 바뀌면 이후 소비 순서와 결과가 달라질 수 있다. 이를 RNG 알고리즘 변경으로 혼동하지 않는다.

## ZEM·종료기는 별도 수정

ZEM 정의는 미래 **target−missile**. 미사일 가속의 결과는 `ZEM−0.5*a_m*tgo²`이므로 `+k*ZEM`이 오차를 줄인다. 기존 `−k*ZEM`은 반대였다. 좌표계와 autopilot의 속도 수직 투영/양의 yaw 소비까지 검사했다. 부호 외 이득·cap은 바꾸지 않았다.

새 종료기는 유효 TRACK의 무조건 return을 관측 기반 판정으로 대체한다. 관측 접근 이력, 관측 CPA 통과, 연속 opening≥2.5s, 거리 증가≥max(200m, 3σ), 신관 미작동을 모두 요구한다. RF 연속성/재획득, 실제 복귀 선회, 유효 대체 관측의 접근을 보호한다. 알려진 자체 제어명령이 남은 기존 배터리 시간 안에 closing 방향으로 회복할 수 있는지도 평가해 미세 APN 잡음을 복귀 기동으로 잘못 인정하지 않는다. 명령을 알 수 없으면 물리적 half-turn 여유를 주는 보수적 분기로 남긴다. 실제 표적 좌표·truth CPA·단순 발사 후 timeout은 사용하지 않는다. 기존 no-acquisition/lost-track/배터리 정책은 유지한다.
