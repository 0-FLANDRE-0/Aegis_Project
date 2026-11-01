# NATURAL_SATURATION_13 — 9번째 ESSM 발사 지연 소비 경로 검토

읽기 전용 분석이다. 새 브라우저 실행, planner/RF/NIS/KF 추가 호출, 제품 수정, 기대값 변경은 하지 않았다. 결론은 **일부 소비 경로 확인, 최종 보류 사유 미확정**이다. 후보의 자연 포화전 결과 악화는 미승인 상태로 유지한다.

## 고정 입력과 분석 범위

- 기존 B ACTIVE HTML: `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`.
- 안정화 ACTIVE HTML: `87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18`.
- 안정화 packed script 13의 해제된 main SHA-256: `21f63de9c0ed32f3d247b9371e06b4e4eb0dd8a566a33c8bf4897533f466d35d`.
- 근거: [NATURAL13_CAUSE.json](evidence/battle-analysis/NATURAL13_CAUSE.json), [BATTLE_RESULTS.md](BATTLE_RESULTS.md), [기존 B 원시 실행](evidence/battle-final/old-active-NATURAL_SATURATION_13.json.gz), [후보 원시 실행](evidence/battle-final/candidate-active-NATURAL_SATURATION_13.json.gz), [원시 수집기](battle.js).
- 아래 코드 위치는 이 고정 main을 해제한 소스의 행 번호다. NPC의 `createWeaponContextD` 내부 복사본이나 `mapBNativePreview`의 발사 미리보기 복사본을 실제 자함 AUTO 경로로 취급하지 않았다.

## 로그에서 직접 확인되는 사실

| 항목 | 기존 B ACTIVE | 안정화 ACTIVE |
|---|---|---|
| 첫 8발 발사 시각 | 0.2 / 1.0 / 1.8 / 2.6 / 3.4 / 4.2 / 5.0 / 5.8 s | 동일 |
| 003 대상 첫 2발 | 3.4 / 4.2 s | 동일 |
| 9번째 전체 발사, 003 대상 3번째 발사 | 17.0 s, tick 1020 | 21.0 s, tick 1260 |
| 같은 재사격의 다음 발 | 17.8 s | 21.8 s |
| 9번째 발사 시 `engagement` / `round` | 2 / 3 | 2 / 3 |
| 90초 말 원시 ESSM / RAM 발사 수 | 20 / 3 | 19 / 3 |
| 90초 말 생존 초기 위협 수 | 1 | 3 |
| 종료 상태 | HORIZON_UNRESOLVED, HP 0 | HORIZON_UNRESOLVED, HP 0 |

9번째 발사는 새 표적의 첫 교전이 아니라 **같은 receiver-local 트랙 `300000003`에 대한 두 번째 salvo의 첫 발**이다. 두 발씩 발사되는 모양만으로 재사격 필요량, 대기 사유 또는 같은 물리 표적 여부까지 확정할 수는 없다.

최초 실제 연관 반환 차이는 2.6333333333초(tick 158)다. 그 앞 398개 실제 반환은 동일했다. 13×13·86 edge 성분에서 기존 B는 13개 모두 보류했고, 후보는 3쌍을 인증하여 갱신하고 10개를 보류했다. 이 사실은 연관 결과가 실제로 소비되었음을 증명하지만, **어떤 발사 관문이 4초를 기다리게 했는지까지 증명하지 않는다**.

### 003 트랙의 저장된 1초 표본

아래는 새 계산을 수행한 값이 아니라 수집된 실제 트랙 필드다. 전부 `confirmed=true`, `identity=ASSUMED_HOSTILE`, `classification=ASM`이다.

| 시각 s | 기존 B authority | 후보 authority | 기존 B sensorAge s | 후보 sensorAge s |
|---:|---|---|---:|---:|
| 15 | WITHHELD | AUTO_AUTHORIZED | 0.016667 | 0.050000 |
| 16 | AUTO_AUTHORIZED | AUTO_AUTHORIZED | 0 | 0.016667 |
| 17 | AUTO_AUTHORIZED | WITHHELD | 0.066667 | 0 |
| 18 | WITHHELD | WITHHELD | 0.216667 | 0 |
| 19 | WITHHELD | WITHHELD | 0 | 0 |
| 20 | AUTO_AUTHORIZED | WITHHELD | 0.016667 | 0 |
| 21 | AUTO_AUTHORIZED | AUTO_AUTHORIZED | 0 | 0.016667 |

따라서 후보의 17~20초 표본은 미확정 트랙도, 수 초간 관측이 끊긴 트랙도 아니다. 최신 관측이 있어도 기존 A3가 권한을 보류할 수 있다. 다만 이것은 fixed tick 종료 후 1초 간격 표본이다. 해당 AUTO 평가 순간의 반환과 동일하다고 가정하거나, 그 사이 계속 보류되었다고 주장하지 않는다.

첫 네 `applyInterceptResult` 기록(11.45 / 13.366667 / 14.1 / 14.616667초)은 두 실행에서 같은 시각·무기·결과·사후 대상 ID를 갖는다. 이는 전체 궤적, 내부 RNG 또는 그 시각의 planner 상태가 동일하다는 증거는 아니다. 현재 수집기는 SAM 소멸 시점과 실제 planner 거부 반환을 기록하지 않는다.

## 실제 자함 AUTO 소비 경로

1. `updateWip118EngagementControl` → `wip118BuildEngagementControl` (main L50136~50154).
   - 관측 기반 `wip118ControlState.assessments`에서 THREAT/LOST를 선택한다.
   - 후보 무장마다 `wip118BasicResource` → `wip118FindNezPlan` → `wip118SalvoPolicy`를 실제로 평가한다.
   - `hardKillExistingEngagementCounts`의 **살아 있는, 해당 trackId에 배정된** ESSM 수를 권고 salvo에서 빼 `recommendedRounds`를 만든다. 기존 SAM이 아직 살아 있으면 추가 발사가 필요 없다는 판정이 가능하다.
   - recommendation 순서대로 임시 탄수와 SPG 예약을 배분한다. 위협 순서/NEZ/기존 교전 수 변화는 같은 003의 대기 시간에 영향을 줄 수 있다.
2. `updateWip119EngagementAutomation` → `wip119BuildCandidateRows` → `wip119EvaluateRow` (L50299~50328, L50440~50450).
   - 아래 표의 순서대로 관문을 검사하고 첫 `ready=true` 행을 선택한다.
   - 기존 pending salvo가 있으면 먼저 처리한다. 새 salvo는 pending이 없을 때만 시작한다.
3. `wip119StartAutoSalvo` → `wip119ProcessPending` → `wip119FireOne` (L50401~50438).
   - 매 실제 발사 시 network, VLS cycle, assessment, 잔탄, 채널, FCQ를 다시 확인한다.
   - `wip121WithDecisionTrack` 안에서 등록 descriptor의 `fire`, ESSM은 `spawnESSM`을 호출한다.
4. `spawnESSM` → `vlsReleaseB2Request` → `vlsReleaseB2SupportPreflight` → `vlsReleaseEssmB1` (L29859~29913, L39730 이후).
   - 예약/FCQ/식별/장비/EMCON/셀을 다시 검사한 뒤 실제 셀을 소비한다.
   - `VLS_CYCLE` 반환은 pending을 보존하여 `nextStep`까지 기다린다. `wip119ProcessPending`의 다른 실패는 pending을 취소한다.

### 9번째 발사 지연을 구분하는 실제 반환

| 실제 호출 지점 | 관측 가능한 결과 | 현재 자료로 확정 여부 |
|---|---|---|
| `wip119EvaluateRow` 첫 상태 검사 | `LOST_COAST` / `NOT_THREAT` | 미확정. assessment/lostCoast가 저장되지 않음 |
| 같은 함수의 FCQ 검사 | `FCS_QUALITY` | 미확정. confirmed와 sensorAge만으로 FCQ는 판정 불가 |
| `trackEngagementGateA3` 실제 호출 | `IDENTITY_UNKNOWN` / `UNASSESSED` / `AUTHORITY_WITHHELD` 등 → 평가 행의 `A3_AUTHORITY` | 표본에서 WITHHELD는 확인. 실제 호출 반환과 상세 이유는 없음 |
| `recommendedRounds <= 0` | `IN_FLIGHT` / `SALVO_COMPLETE` | 미확정. 발사 기록에는 남아 있는 SAM 수가 없음 |
| `wip118FindNezPlan` / firePlan | `NO_NEZ` / `NO_CHANNEL`, 또는 READY지만 `fireDelayS`가 커 `FUTURE` | 미확정. plan/예약 반환 미수집 |
| `wip119ReengagementBrake` | `REENGAGE_HYST` / `RESALVO_DELAY`, 실제 stable/cooldown/wait | 미확정. `reengageThreatSinceS`와 마지막 assessment 이력이 없음 |
| `wip123EngagementLimit` / 잔탄 검사 | `MAX_ENGAGEMENTS_ABSOLUTE` / `MAX_ENGAGEMENTS_ADAPTIVE` / `RESERVE` | 미확정. nested limit/budget가 기존 간이 로그에 없음 |
| `wip119ProcessPending` / `wip119FireOne` | waiting, VLS_CYCLE 또는 취소 사유 | 미확정. pending과 실패 반환 미수집 |
| `vlsReleaseB2Request` | `lastReject.reason`, support preflight 결과 | 미확정. 성공 발사만 기록됨 |

원래 정책은 재사격 확인 1.5초, 최소 재사격 간격 7.5초, 물리 발사 간격 0.8초다. 003의 마지막 공통 발사가 4.2초이므로 고정 7.5초 조건만 보면 11.7초 이후다. **고정 cooldown 수치 자체가 바뀌어 17→21초가 되었다는 근거는 없다**. 반면 `reengageThreatSinceS`는 실제 THREAT 상태 지속/재진입에 따라 다시 시작하므로 같은 정책 아래서도 지연이 달라질 수 있다. 이것 역시 해당 필드의 기록 전에는 원인 확정이 아니다.

`trackIsFireControlQuality`(L27682~27695)는 displayable, confirmed, `!memActive`, `!reacquiring`, 허용 센서 출처, FCQ 및 공분산 제한을 모두 요구한다. `updateTrackOperationalStateA3`(L26647~26677)는 이 결과 외에도 KILL_ASSESSMENT/HARMLESS/DESTROYED/보호 식별을 검사한다. 따라서 실제 `_a3AuthorityReason`이 `TRACK_NOT_READY`, `KILL_ASSESSMENT`, `NON_THREAT`, 보호 식별 중 무엇인지 분리해야 한다. `SPY1DV_TRACK_REACQUIRE`라는 출처 이름만으로 `reacquiring=true`라고 단정해서는 안 된다.

## 필요한 최소 추가 계측 — 원 호출의 반환만 관찰

추가 시험을 실행한 것이 아니다. 아래는 다음 수집기의 권장 관찰 지점이며, 게임 함수 추가 호출은 금지한다. 실제로 호출되는 함수를 wrapper가 **정확히 한 번** 호출한 뒤 원 반환값을 그대로 돌려주고, 기존 scalar를 복사한다. logger 오류는 게임 경로에 전파하지 않는다.

1. `wip119EvaluateRow` 반환: step/time, row.trackId, `ready/reason/need`, `row.assessment/trackPresent/lostCoast/coastFireControlUsable/liveEngagement/reengageRequired/weapon/salvo/recommendedRounds/salvoPolicy`, `firePlan.status/reason/fireDelayS/nezStartDelayS/nezEndDelayS/channelId`와 예약 시간, 반환에 이미 있는 `a3Gate.reason`, `brake.stableS/cooldownS/waitS`, `limit.totalCount/layerCount/adaptiveCap/absoluteCap`, `reserve.have/reserve`.
2. 실제 `trackIsFireControlQuality` 호출 반환과 `trackEngagementGateA3` 반환: boolean/ok/reason, `trackId`, `confirmed/memActive/reacquiring/sensorDetected/sensorAge/sensorSource/trackQuality/fireControlQuality`, `threatStatus/identity/engagementAuthority/_a3AuthorityReason`, 직접 읽은 `_kfP` 대각·`_lastMeasurementStep`. `trackRefreshDerivedQuality`, `trackCovarianceMetrics`, gate 함수를 logger가 다시 호출하면 안 된다. 이 함수들은 정상 소비 중 파생 상태를 갱신할 수 있다.
3. `wip118FindNezPlan`, `wip118SalvoPolicy`, `hardKillExistingEngagementCounts`의 **원래 호출 결과**: 선택된 계획과 발수·기존 ESSM 수를 직접 연결한다. `wip118BuildEngagementControl`이 반환한 recommendation 순서도 저장한다. 복제 planner를 실행하지 않는다.
4. 실제 `wip119ProcessPending` / `wip119FireOne` 호출 전후의 `pending` scalar와 반환 `ok/reason/waiting/nextStep`; 실제 `wip119CancelPending(reason)` 인자. `wip119UpdateResponseMemory`가 끝난 뒤 기존 response map의 `reengageThreatSinceS/lastAssessment/lastReengageRequired/lastAutoFireS/autoEngagements`를 읽는다.
5. 실제 `vlsReleaseB2SupportPreflight` / `vlsReleaseB2Request` 반환과 기존 release state의 `busy/nextStep/lastReject`. `vlsReleaseB2Snapshot`도 logger가 새로 호출하지 말고 이미 존재하는 객체를 읽는다.
6. 배정된 기존 SAM의 `id/assignedTargetId/dead/life` 전환을 관찰하여 `IN_FLIGHT` 해제 시점과 연결한다. 표적 truth 위치나 물리 ID로 planner 원인을 대신 설명하지 않는다. 기존 사후 피해/Pk 자료는 `AFTER_ACTION_TRUTH_TEST_ONLY`로 계속 분리한다.

우선 구간은 **14~22초**, 주 대상은 003과 004다. 위 `wip119EvaluateRow`/A3 상세 이유만 먼저 수집해도 상태·FCQ·식별·NEZ·발수·재사격·큐 중 어느 관문인지 구분할 수 있다. 모든 무장의 모든 forecast 후보를 무제한 기록할 필요는 없다. 관찰 wrapper를 붙인 실행이 무관찰 실행과 최종 상태/자체 RNG/실제 발사·요격 이력까지 동일한지도 별도로 확인해야 한다.

## 소비 함수의 변경 여부

원본 `compact_source.cjs` AST 추출기를 읽기 전용으로 사용하여 실제 자함 스코프의 다음 17개 선언을 기존 B와 안정화 후보 사이에 비교했다. **17/17 byte 동일**이다. 브라우저와 게임 함수를 실행하지 않았다. 이는 입력 상태가 바뀌지 않았다는 뜻이 아니라, 아래 소비 코드를 수정하여 발사를 늦춘 것은 아니라는 범위 확인이다.

`wip118BuildEngagementControl`, `wip118FindNezPlan`, `wip118SalvoPolicy`, `wip119EvaluateRow`, `updateWip119EngagementAutomation`, `wip119ProcessPending`, `wip119FireOne`, `wip119ReengagementBrake`, `wip119UpdateResponseMemory`, `hardKillExistingEngagementCounts`, `trackIsFireControlQuality`, `trackEngagementGateA3`, `updateTrackOperationalStateA3`, `vlsReleaseB2Request`, `vlsReleaseB2SupportPreflight`, `vlsReleaseEssmB1`, `spawnESSM`.

대표 SHA-256:

| 선언 | 두 제품의 공통 source SHA-256 |
|---|---|
| `wip119EvaluateRow` | `ccf03716553128d7008a7ce5bb773f4e7df3a551edb69c3a73a6ab65e1e627ce` |
| `wip119FireOne` | `d0be28705528e16414bf6cdaca61befc7e3755793740b8f90e4d09bc8bb0d010` |
| `trackIsFireControlQuality` | `be418119048be88b2326b04306c0e8e48f02ff44b10aa89592fd672d22a632e1` |
| `trackEngagementGateA3` | `e2e7c681009518027f4e0ee6caec0b90816578622ab64d3c902bc60f1a303a28` |
| `vlsReleaseB2Request` | `2ef196c16a4f7326803d005e0d67d8d818d4605d1697a0673a964ed904ee88a7` |

기존 `hardKillExistingEngagementCounts` 안에는 PHALANX 집계용 legacy truth 참조가 남아 있다. 이번 분석은 이를 수정하거나 새로 사용하지 않았다. ESSM 기존탄 집계는 자체 발사탄의 `assignedTargetId/isESSM/dead`를 쓰는 별도 분기다. 전체 기존 전투계층을 truth-free로 바꾸었다는 주장은 하지 않는다.

## 판정

- 확인: 실제 연관 반환 변화 → 관측 트랙 갱신 변화 → 기존 방어 소비 경로가 읽을 상태 변화가 존재한다. 003은 후보 17~20초 표본에서 신선하고 확정된 ASM이면서 교전 권한이 보류되어 있다. 9번째 ESSM은 같은 트랙에 4초 늦게 재발사되었다.
- 미확정: 그 4초의 직접 원인이 FCQ/재획득 상태, kinematic assessment, 잔존 SAM/발수, NEZ/채널, 재사격 hysteresis, pending 큐 중 무엇인지. 여러 단계의 연쇄일 수도 있다.
- 승인하지 않음: 자연 포화전의 모듈 손상 악화 및 잔존 위협 1→3. 다른 지표가 좋아졌거나 HOLD 수가 줄었다는 이유로 이 결과를 상쇄하지 않는다. 전체 사격/피해 RNG나 무장 계수는 변경하지 않는다.
