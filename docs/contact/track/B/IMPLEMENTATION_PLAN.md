# TRACK-B 착수·구현 전 결정

기준: `track-a-contract-trace@ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561`, HTML SHA `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`. 작업 브랜치 `track-b-association`. 사용자 TRACK-B 착수 지시로 A 이후 B를 진행한다. 원 지시서 `../A/INSTRUCTIONS.md`의 B 범위와 정보 경계를 유지한다. main·cg-turret-a·friendly-contact-a·track-a-contract-trace는 수정/병합하지 않으며 PR/release/tag도 만들지 않는다.

## 기존 결정과의 관계

충돌하는 새 요구는 없다. 3D AIR 근거 16초, 수상 8m prior, 기존 surface-established-first, per-physical-dwell 일대일, own/non-own C55 분리, 고정 CI .5, MANUAL/HOLD·IFF·ROE·remote-only 권한 제한을 그대로 둔다. C/D의 수명/식별 승계/소비자 통합은 구현하지 않는다. 419025와 기존 paired observer 2건, legacy EMCON UI14는 승인되지 않았다.

## 경로별 첫 적용

|경로|결정|이유/검증|
|---|---|---|
|자함 SPY/수상|기존 Hungarian 비용 graph에 sanity/모호성 보류 연결; focused 및 established-first 우선순위 보존|RC0 native 시험의 누락3건으로 연결 필요 확인; 보류가 새 파일 생성으로 흐르지 않도록 네 호출부 검사|
|NPC observer|기존 계산 NIS graph에 공유 solver 적용, SHADOW/ACTIVE 별도 빌드 비교|sorted-edge greedy가 완전한 일대일 matching을 놓치는 사례를 실제 함수로 재현|
|Hawklink|같은 source·원 측정 epoch의 보고를 pre-update 후보 graph로 처리|서로 다른 접촉의 같은 시각을 중복 fix로 오인/하나에 순차 흡수하지 않음; 다른 시각/센서는 독립 처리|
|SPQ AIR|순차 실행 보존, 이미 계산된 후보와 winner만 shadow trace|행마다 EKF가 바뀌므로 같은 epoch의 최적 행렬이라고 주장하지 않음|
|C55 자함/NPC|live 동작 보존, 실제 측정/사전 file snapshot 기반 shadow 분석|관측 생성·file commit이 섞여 있고 후속 TRACK/SEARCH·local ID 기반 RNG에 영향. 임의 재정렬 금지|
|Link16|현행 연관/NIS/거리·속도 sanity/CI/일대일 보존|C/D의 lineage/순환/수명 변경을 B에 섞지 않음|

## 공유 solver와 새 association 정책

RF·측정 잡음·EKF·Pd/Pk·신관·유도 계수는 변경하지 않는다. 아래는 새 **SIM_TUNED 게임 연관 정책**이며 실물 센서 제원이 아니다.

- 입력은 native가 실제 한 번 계산한 `(plot index, tactical track ID, NIS)`와 측정/필터 추정에서만 얻은 sanity 결과다. 실제 표적 ID/owner/faction/좌표를 넣지 않는다.
- 기존 `bridgeMasterEMinCostAssignmentV35`를 그대로 호출한다. native NIS gate(각 경로의 64/25)와 dummy `gate+.5`는 유지한다. 분리된 connected component별로 풀어 비용을 제한한다.
- 같은 cardinality의 대안 matching이 총 NIS 차이 ≤1이면 바뀌는 행/열을 보류한다. native NIS 비용이 거의 같다는 게임 정책이며, 후보마다 innovation covariance가 다르므로 확률/우도비로 보정됐다고 주장하지 않는다. gate 완화/잡음 변경이 아니다.
- 보류된 관측은 그 호출에서 EKF/hit/신규 생성을 하지 않는다. 기존 트랙은 기존 coast/drop 경로를 따른다. 별도 mutable lifecycle/identity 체계를 만들지 않는다.
- 한 component가 12행 또는 12열을 넘으면 bounded-component hold로 기록한다. 이 제한이 방어 손실을 만들면 실패로 보고하며 결과를 맞추려고 값을 바꾸지 않는다.
- 별도 위치 sanity는 `거리 혁신 ≤2500m`다. 기존 networkAssociationNisG의 hard bound를 재사용한다. 측정 잡음은 native NIS가 처리하고, filter P 또는 측정 P가 커져도 이 절대 상한이 사라지지 않는다. surface는 XY만, AIR는 XYZ를 비교한다.
- 방사속도 관측과 receiver 자기 속도가 실제 있을 때 `|측정 rdot−예측 rdot| ≤180m/s`를 적용한다. 미관측 Doppler/수직 receiver 속도를 0으로 만들어 검사하지 않는다.
- Hawklink는 기존 원 측정 시각·age² P 증가를 유지한다. 새 속도나 실제 좌표로 오래된 보고를 외삽하지 않는다. wire의 표적 고도가 가정일 때 AIR 고도를 끌어내리는 위험은 별도 보류/회귀로 다룬다.
- C55 shadow의 거리 비용은 m 단위이며 NIS가 아니다. 같은 solver를 쓰더라도 `ambiguityDeltaCost=0`으로 정확 동점만 보고하고 degree conflict를 별도로 표시한다. live gate나 보호에는 적용하지 않는다.

## 실행·완료 판정

1. pure solver + actual native Hungarian 단위 검증, 익명 native ingress A/SHADOW/ACTIVE 비교.
2. 자연 헬기 60/120초·Harpoon75초, C5530시드·419025·두 문맥 보호, observer ownership/clock/query invariance.
3. 기존 도메인364+paired42, 현 UI213, 실제 WebGL8발/29단언. 기대값은 바꾸지 않고 모든 차이를 원문으로 보존한다.
4. 바뀐 전투 결과·상태는 별도 분석한다. 결과 악화를 보정하거나 통과로 간주하지 않는다. fixture 성공과 자연 RF/실제 무장을 구분한다.
5. 독립 HTML·소스 diff·검증/미완료 보고서를 별도 GitHub 브랜치에 제출한다. HTML ZIP과 보고서 ZIP을 나누고 원격 해시를 확인한다. 상속 문제가 남으면 releaseApproved=false/final CLOSED 금지를 유지한다.

## 게임 시험 전 독립 검토의 수정

초기 max(2500m,5σ)/max(180m/s,5σ) 안은 큰 측정 P에서 무한 확장되는 설계 결함이 발견돼 폐기했다. 게임 결과를 보기 전에 기존 network hard caps 2500m/180m/s로 고정했다. 초기 unit 결과는 해당 proposal의 시험일 뿐 최종 정책 합격으로 세지 않는다. 새 단위 검증은 큰 filter P뿐 아니라 큰 measurement P도 상한을 넘기지 않는지 검사한다. native Hungarian의 gate+.5 dummy 정책은 유지하므로 최대 cardinality 보장이 아니라 최소 비용 할당이며, 파일 수를 최대화하는 목적이 아니다.

## 첫 실제 함수 시험 RC0

ACTIVE `79a098a8…` / SHADOW `ac96bc13…`에서 신규 계약69검사 중 ACTIVE66통과·3실패. 세 실패는 자함 spyGlobalAssignmentsV36에 공통 검사가 아직 연결되지 않은 결함(동점 단일/복수 plot의 임의 할당, huge P의 먼 후보 수용)이다. 기대값/계수 변경 없이 own global·surface staged graph와 실제 null→create 호출부를 수정한다. RC0 자료는 historical/not-final로 보존한다. SHADOW의 실제 기존 상태는 A와 동일했다. focused·SPQ AIR·C55 live는 기존 우선순위/인터리브 정책을 유지하며 전체 개선 완료를 주장하지 않는다.

## RC1 빌드 전 경계 검토

자함 RF의 discrete echo 수에는 256개 상한 보장이 없어 `plotCount>256` 예외는 정상 대량 관측에서도 게임을 중단시킬 수 있었다. 게임 시험 전에 전역 plotCount 상한을 제거했다. plotCount는 인덱스 검증에만 쓰고 sparse connected component의 12행/열 제한은 유지한다. C55의 256개는 진단 capture만의 독립 상한으로, 초과 시 LIMIT 기록 후 진단 분석을 생략하며 native 관측/파일은 제한하지 않는다.
