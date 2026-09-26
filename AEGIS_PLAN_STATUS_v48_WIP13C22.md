# AEGIS v48 WIP13C22 — 대수상 신관 프로파일 통합

기준: `Aegis_SIM_v48_WIP13C19.html` (SHA-256 `152237dbb4517d7b6af5dc7ac0e5dc77c70bc00c6ec02aa17b2e1af57778bd77`).  
결과: `Aegis_SIM_v48_WIP13C22.html` (SHA-256 `9b697fcb2edfef69b01d39add5600d1f61638fa42bf6b2d07222d25d491e75fa`). 상태 문서 해시는 `SHA256SUMS_v48_WIP13C22.txt` 참고.

**C20과 C21은 업로드하지 말 것.** C20은 무조건 조기 근접기폭, C21은 접촉 우선 방침을 복구했지만 신관 범위를 별도 9m/7m로 중복 선언했다. C22는 C19를 기준으로 다시 패키징했으며 이전 C21 산출물을 수정·덮어쓰지 않았다.

## 구현

- 기존 SM-2 Mk45 TDD 및 ESSM Block 2 TDD 프로파일이 신관 탐지 반경(각각 80m, 60m), 무장 거리(2.2km, 1.6km), 빔, RF 탐지 확률 및 처리 지연(4ms, 3ms)을 제공한다. 이 값들은 게임 내 `SIM_TUNED_PUBLIC_UNKNOWN`이며 실물 제원으로 주장하지 않는다.
- 기존 `SAM_MISSILE_PROFILES`의 `lethalRadiusM`(SM-2 35m, ESSM 25m)을 근접기폭 허용 상한으로 사용한다. 별도 9m/7m 신관 상수는 제거했다. 표적함의 실제 IJ 대역 RCS를 공통 신관 탐지 함수의 선택적 입력으로 전달한다. 공중 요격 호출에는 변화가 없다.
- 미사일이 이번 고정 틱에 실제 선체와 충돌하면 기존 WIP12B/WIP12F 충격신관 경로를 사용한다. 충돌하지 않았고 현 상대속도 직선 연장 경로도 선체를 통과하지 않는 경우에만 근접기폭을 검토한다. 감지, 무장 거리, 빔·탐지 확률 및 처리 지연을 모두 통과해야 RF 근접신관이 작동한다.
- 수상 신관 감지 상태는 해당 미사일 내부에 보관하고 공중 요격의 `proxArmed`는 건드리지 않는다. 센서·FCS에서는 익명 트랙을 유지하며 물리 표적 객체는 신관 감지와 충돌·피해 판정에서만 사용한다.
- 해면이 먼저 교차하면 기존 `SEA_IMPACT`로 종료한다. SPG-62, 발사 계약, SM-2/ESSM 유도, 함선 외형 및 렌더러는 변경하지 않았다. C19와 비교해 C55 압축 레코드 13만 달라졌다.

## 검증 결과

| 검사 | 결과 |
| --- | --- |
| 압축 레코드·SHA·문법·수정 영역 truth 검색 | 14/14 무결성, main JS 문법 통과, 형상 레코드 보존, 새 FCS truth 접근 없음 |
| DOM VM 부팅·core selftest | 통과, 실패 0 |
| 신관 fixture | **10/10**: SM-2/ESSM 선체 접촉 2, 근접 미스 2, 유효 범위에 들어왔으나 이후 선체 접촉 예상되어 기폭 금지 2, 해면 선행 1, 원거리 미스 1, 탐지 반경 1m 변경 시 근접 미스에서 무기폭 2. 중복 피해 없음 |
| 지원 상태 fixture | 별칭 이전, DIRECT_BREAKUP BDA, SPG 지원 해제 통과 |
| 해면·선체 교차 | 5/5 통과 |
| C17 서보·C5 SARH | fixed tick 서보 1×/8×/16×/64× 정확 일치, 최초 RF 2.3333s, C5 VM 12/12 통과 |
| 실비행 SM-2 | seed 1350501, 8km, 방위 90°, `SURFACE_TARGET_CONTACT`, 충격신관, 폭약 34.5kg, 피해 1건 |
| 실비행 ESSM | seed 1350501, 8km, 방위 90°, SPG 전체 비활성, `SURFACE_TARGET_CONTACT`, 충격신관, 폭약 15.5kg, 피해 1건 |
| 실비행 해면 선행 | seed 1350501, 방위 0°, `SEA_IMPACT`, 표적 피해 0건 |

근접 미스에서는 기존 선체·상부구조 메쉬까지의 최근접 거리를 사용한다. 이 작업은 미래 유도 선회를 예측하지 않으며, 현재 고정 틱의 상대 운동을 직선 연장해 충돌 가능성을 판정한다. 공중 표적용 신관 모델의 해상 클러터 오기폭률을 수상함 선체의 RF 모델로 억지 연결하지 않았다. 전체 방위의 실제 브라우저 실비행, 3D/WebGL 피격 장면은 이번에 실행하지 않았다. 따라서 13C 전체 완료로 표시하지 않는다.

기준 C19로 재생성: `python AEGIS_WIP13C22_PACK.py`. 검증: `python AEGIS_WIP13C22_PACKAGE_CHECK.py`, `node tests/AEGIS_WIP13C22_TERMINAL_LIVE_TEST.cjs Aegis_SIM_v48_WIP13C22.html`, `node tests/AEGIS_WIP13C22_SEA_HULL_REGRESSION.cjs Aegis_SIM_v48_WIP13C22.html`, `node tests/AEGIS_WIP13C22_SERVO_CADENCE.cjs Aegis_SIM_v48_WIP13C22.html`, `node tests/AEGIS_WIP13C22_FULL_FLIGHT.cjs Aegis_SIM_v48_WIP13C22.html '{"weapon":"SM2","bearingDeg":90,"ownSpeedKt":25}'`.

원격 `feat/v48-wip13c-control-deck-ui-foundation` 브랜치에 C22 HTML 업로드를 Git blob 일치로 확인했다. 문서·검증 소스도 같은 브랜치에 기록한다. 브라우저/WebGL 및 전체 방위 실비행은 후속 검증 조건으로 유지한다.
