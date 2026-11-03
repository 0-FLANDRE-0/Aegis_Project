# 시커 공통 물리층 감사

IMPLEMENTED: **아니오 — 설계 감사만 수행**

TESTED: **소스 호출 경계와 현재 프로필 단위 대조**

APPROVED: **아니오 — 후속 구현은 별도 승인 대상**

UNRESOLVED: **SARH의 송·수신 이중 LOS, RAM 수동 RF/IR 합성, 하푼 전용 표적성 판정의 공통 계약화**

RELEASE: **아니오**

## 현재 경로

| 단계 | WIP22 Kh-32/Kh-35U | Harpoon | SAM v1 SARH | SAM v1 ARH (ESSM B2/SM-6 IA) | RAM Blk 1A | 분류 |
|---|---|---|---|---|---|---|
| 반사체 | `physicalRfReflectorRegistryWip13A3` | 같은 레지스트리 | `_sarhTruthReflectorPool` | `_sarhTruthReflectorPool` + 해면 셀 | RF는 방사체 열거, IR은 열원 함수 | RAM RF/IR은 `HARDWARE_DIFFERENCE`, 나머지는 공통화 후보 |
| 신호 | `snrRefKm/refRcsM2`, 단안 R^-4 | 전용 `seekerReference*`, 단안 R^-4 | SPG-62→표적→미사일 쌍정 경로 | `_arhNormalizedMonostaticPower`, R^-4 | RF 수동 수신 R^-2, IR R^-2 | 전파 경로 차이는 `HARDWARE_DIFFERENCE`; 정규화 API 분리는 `IMPLEMENTATION_DIVERGENCE` |
| 빔·가림·클러터 | 3D gimbal, 검색/추적 빔, LOS, 해면·지형·기상, ECM/HOJ | 3D gimbal, LOS, 해면·기상; 전용 필터 | 송신 SPG 빔 + 수신 빔 + 양 경로 LOS | 검색/추적 빔, LOS, 해면/지형 배경, PD/MTI | RF/IR 각 보어사이트·gimbal | 하드웨어 계수는 유지, 공통 geometry/LOS 계약은 통합 |
| 분해능·합성 | `asmSeekerCompositeReturns` | 합성 없음; 상위 96 관측 | `_sarhClusterEchoes` | `_arhClusterEchoes` | 각도 후보의 전력 합성 | 알고리즘 분기는 `IMPLEMENTATION_DIVERGENCE`; 센서별 분해능은 `HARDWARE_DIFFERENCE` |
| 측정 잡음 | range/az/el/doppler, glint/ECM 포함 | range/bearing/elevation/radial 전용 | bistatic range/az/el/path-rate | 4Q monopulse range/az/el/two-way path-rate | RF/IR 각도·품질 | 관측 차원 차이는 `HARDWARE_DIFFERENCE`; 공분산 출력 계약은 통합 |
| 표적 검증 | `arhRfTargetEvidenceWip13B12` | vertical extent, Doppler spread, memory radial gate | 조사·기하·SNR, SARH consistency | 공용 evidence + PD/MTI + temporal/ECCM | emitter/IR signal + authority hysteresis | 검증 플러그인으로 분리 |
| 연관·cue | range/angle/doppler/NIS + INS cue | 기억 바구니 + 위치/방사속도 gate | cue track + local EKF/NIS | cue/memory + local EKF/NIS + protected track | angular memory track | 공통 association 인터페이스, 무장별 gate profile |
| 상태기계 | OFF/SEARCH/ACQUIRE/TRACK/COAST/REACQUIRE | OFF/SEARCH/ACQUIRE/TRACK/COAST | OFF/SEARCH/ACQUIRE/TRACK/COAST/REACQUIRE | OFF/SEARCH/ACQUIRE/TRACK/COAST/REACQUIRE/LOST | MEM/RF/IR authority | 공통 상태 전이기 + RAM authority 훅 |
| 유도 입력 | RF EKF 또는 HOJ, 아니면 INS | confirmed local file, 아니면 INS memory | SARH EKF | ARH EKF, SARH/DL arbiter | RF/IR angular track 또는 memory | `HARDWARE_DIFFERENCE`; 공통 출력은 estimate/covariance/validity |
| 기만·ECM | noise/deception/HOJ | chaff/sea는 물리 관측, 별도 HOJ 없음 | illumination/EW | chaff/sea, ECCM, cross-mode | RF emitter + IR takeover | 무장별 훅 유지 |

## 확인된 구현 분기

1. WIP22와 SAM ARH는 같은 RF 레지스트리와 `arhRfTargetEvidenceWip13B12`를 쓰지만, 신호 정규화·분해능 합성·측정 객체 형식이 다르다.
2. Harpoon은 같은 반사체를 읽지만 `harpoonRfObservationsA` 안에서 신호·잡음·후보 gate를 다시 구현한다. 공용 composite와 공용 표적성 판정은 사용하지 않는다.
3. SARH는 쌍정 경로와 SPG-62 조사 의존이 본질적인 하드웨어 차이다. 단안 ARH로 합치면 안 된다.
4. RAM RF는 수동 방사체 유도이고 IR은 열원 유도다. RF/IR 후보 생성은 공용 능동 레이더 물리로 합치지 않고, 결과 측정 계약만 맞춰야 한다.
5. 각 구현은 자체 RNG와 상태를 갖는다. 통합 시 전역 RNG로 바꾸면 결정성과 기존 통계가 깨진다.

## 정보 비누수

- 물리 프런트엔드는 `_truthObject`와 `_physicsKind`를 에코 합성까지만 사용한다.
- 연관·EKF·유도에는 측정값, 공분산, 익명 echo key만 전달한다.
- `_debugSourceId/_debugSourceKind`는 진단 산출물에서만 허용한다.
- 통합 API는 실제 entity id, profile id, truth 좌표를 출력하지 않는다.
