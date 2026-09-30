# WIP14 Reference Material Notes

## 첨부 원본

- 파일: `Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`
- 저장 위치: `references/wip14/`
- 크기: `1,217,184 bytes`
- SHA-256: `29c30894f3bbcf301ca1df282c8598adbad19e284498efded375505c89e8d10e`
- 성격: 사용자가 제공한 별도 공대공 시뮬레이터 참고본

## 검토된 구조

| 관심 영역 | 원본 표식/함수 | WIP14에서의 사용 |
| --- | --- | --- |
| own-state 분리 | `AIR-NAV-1`, `airNav1Init`, `airNav1UpdateSolution`, `airNav1OwnState` | B1 truth boundary 교차검토 |
| 공통 packet transport | `AIR-DL-1/2`, `weaponLink*` | B2 transport/queue/sequence/age 설계 참고 |
| 제한적 two-way link | `registerTwoWayWeaponLinkSupport`, return packet 처리 | 범용 B2b return-link capability 참고. 특정 미사일 전용으로 구현하지 않고 현재 첫 활성 profile만 SM-6 |
| bounded assistance | `weaponLinkBuildGuidanceAssistance` | 직접 조종명령이 아닌 제한 advisory 참고 |
| 지원 종료 불변식 | `RETURN_LINK_NEVER_EXTENDS_LAUNCH_TIME_SUPPORT_DEADLINE` | B2 필수 회귀로 채택 |
| stateful loft | `computeAim174bStatefulCorridor` | B4 공통 상태기계 개념 참고 |

## 사용 제한

- 이 파일은 실행 기준본이나 AEGIS 자동 테스트 입력이 아니다.
- 공대공 좌표계, radar/FCS, 수치 상수, weapon performance를 그대로 복사하지 않는다.
- reference AIM-174B는 함정 VLS, 가용 미사일 탭, 자동/반자동 교전 목록에 추가하지 않는다.
- 실제 구현은 AEGIS의 current `main`, WIP14 B1 truth boundary, fixed-step/RNG/track authority 규칙을 우선한다.
