# AEGIS_PLAN_STATUS v48 WIP HP_A

## 상태

- IMPLEMENTED: 물리 생존, 임무 가능 상태, 표시 HP를 분리한 공통 `shipOutcomeA` 계약과 플레이어/NPC 단일 projection
- TESTED: 커밋 A 기준 감사, B 제한 게이트, C 소비자·저장·UI 폐쇄 게이트, 동결 후보 MAX_THREAT 광역 1회와 누락 장면 하네스 복구
- APPROVED: 사용자가 지시한 survival 권위, 저장 HP 비권위화, MISSION_KILL/LOST 분리와 U4 선행 merge
- UNRESOLVED: `CONFIRMED_ONLY` 성능, 물리 선체 절단/종강도 즉시상실 규칙, 상속 회귀 부채와 외부 편집 save의 cross-field consistency 정책
- RELEASE: 아님. HP_A PR은 생성까지만 진행하며 병합·release·tag는 사용자 결정이다.

## 기준과 제품

- U4 PR #76 검증 head: `88d5bd19a6f4279242a58d66a77aaf248c317c94`
- U4 candidate Actions: `42518438311` PASS
- U4 merge commit / HP_A 기준 main: `82617839e64ea6b70d33ca55b13b3114cca62f3e`
- 기준 제품: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`, 22,195,923 bytes
- 기준 SHA-256: `00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498`
- 결과 제품: `Aegis_SIM_v48_WIP_HP_A.html`, 22,200,135 bytes
- 결과 SHA-256: `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- packed-main SHA-256: `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464`

## 권위 계약

1. `createShipSurvivalV1.snapshot()`의 `state/irreversible/lost`만 물리 상실 권위다.
2. 임무 상태는 기존 `shipEquipmentOfflineV1`과 승조원 `combatUnavailable`에서 파생한다. 새 임계값은 없다.
3. `computeShipStatus().overall`은 exact alias `damageSeverityPct`로 유지한다.
4. 표시 HP는 비가역/상실이면 0, 그 외에는 `clamp(100-damageSeverityPct, 1, 100)`이다.
5. 저장된 `shipHP`는 호환·불일치 감사 필드이고 복원 권위가 아니다. survival 물리 snapshot을 복원한 뒤 outcome을 다시 계산한다.
6. mission kill, irreversible loss, sunk 사건은 서로 분리되고 전이당 한 번만 기록된다.

## 변경하지 않은 것

- 탄두 위력, 관통, 폭압, 파편, 침수 계수, 종강도, 피해 가중치
- 추진·공력·시커·신관·유도·RNG와 전투 판정
- `createShipSurvivalV1`, `damageFloodImpactV1`, 두 `getShipLongitudinalStrengthV48Wip03` 함수 바이트

## 검증 결과

- 기준 감사: shipHP token 38, 잘못된 권위 사용 6건 확인; 최종 감사는 token 30, 잘못된 권위 사용 0건
- 고정 Kh-35 장면(seed 729300): 실제 hit, `FLOODING`, irreversible false, 표시 HP 13.37; 요청된 한 발 false-zero는 U4에서 재현되지 않아 seed search를 하지 않았다.
- 같은 U4의 SOV casualty 기준은 HP 0/FLOODING/reversible false-zero를 재현했고, 후속 SINKING/LOST를 실제 상실 대조로 보존했다.
- B 제한 게이트 11/11, C 제한 게이트 19/19, page/console error 0
- DDG/CG reversible severity 100은 표시 HP 1; 부유 중 승조원 mission kill은 양수 HP; SOV irreversible/LOST만 HP 0
- 손실 callback은 mission kill/irreversible/sunk 각각 중복 0, 1x/8x/16x 물리·RNG·outcome exact
- 저장 왕복 authoritative survival exact, stale stored HP 무시, invalid enum zero-mutation/fail-closed
- 최종 광역 원시 실행 1회: native 364/364, 후보 결정성 42/42, 현재 EMCON 14/14, UI 213/213, WebGL 29/29 PASS
- paired ESM_A raw 36/42: 여섯 `samePhysicalState`만 HP_A survival 저장 계약 차이. 최종 이산 HP/survival/water/module/crew, 전투 RNG, damage/inventory, observer/offboard와 fault-free는 6/6 exact. 기대값·허용오차 변경 0.
- U4 장면 raw 0/0은 상속 스크립트의 U4 byte-count assertion이 브라우저 전에 중단한 하네스 결함. 제품/장면 코드를 바꾸지 않고 pin 두 개만 HP_A로 바꾼 단일 복구 실행은 19/19 PASS. 광역 재실행은 없다.

## 다음

- HP_A PR #77과 candidate Actions를 제출하고 사용자의 병합 결정을 기다린다.
- 병합 뒤 순서는 `통합 기준선 고정 → 교전·방어 OODA`를 유지한다.
- 물리 선체 절단/종강도 즉시 상실은 HP 숫자에 끼워 넣지 않고 별도 근거·결정이 필요한 backlog다.
