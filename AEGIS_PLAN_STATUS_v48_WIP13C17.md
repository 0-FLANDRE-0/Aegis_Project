# AEGIS v48 WIP13C17 — SPG-62 mechanical servo

- 기준: 사용자 제공 `Aegis_SIM_v48_WIP13C16_C20.html`, 6,642,118 bytes, SHA-256 `d370b57651f5f464642dac98ed38967c2727fff63c11e46ec1c7815bc95449de`.
- 결과: `Aegis_SIM_v48_WIP13C17.html`, 6,646,250 bytes, SHA-256 `efa5fd89978e90341ce317d8c7d76f17ae31796413e1dcc2a4d8f5af3a68e193`.
- 상태: 구현 및 제한된 VM 회귀 통과. 실제 브라우저·WebGL·장시간 실비행 검증 잔여. 정식 완료·병합 판정 아님.
- 원격: `0-FLANDRE-0/Aegis_Project`의 `main` README/작업 지침과 WIP13C6 상태 문서를 확인. 원격의 `main` README는 WIP12D 기준으로 오래되었으므로 현 개발 기준은 제공된 C20 파일이다. 기존 브랜치와 PR은 수정하지 않았다.

## C20 기준 확인

사용자 제공 C20에는 해상 SM-2 SARH와 ESSM ARH의 제한적 대함 경로, 표적함과 RF 반사체, 수상 포격, VLS 뚜껑·uptake, 발사 화염/연막, 외부 3D 모델 보정, 주기관 telegraph 기반 속도/샤프트 상태가 들어 있다. 이번 C17은 이 파일의 압축 패키지에서 메인 시뮬레이션 스크립트만 변경하고 나머지 자산 13개의 해시와 데이터를 유지했다. 과거의 손상된 C17 파일은 사용하지 않았다.

## 구현

1. 각 ShipRuntime의 `combatSystem.fireControl.spg62Servo.mounts`에 3기 안테나의 실제 방위·고각·각속도·명령·트랙·모드·안정화·송신 상태를 두었다. 생성과 수명주기 reset에 동일한 초기화 함수를 적용했다.
2. `simulateFixedTick()`에서만 예약을 확인하고 2축 서보를 적분한다. 정지거리 기반 감속, `2.5 rad/s²` 가속 한계, ±179° 경계 최단각, 방위/고각 및 속도 허용차와 `0.25 s` 안정화를 적용했다. 함포 적분기는 목표 통과 순간 각속도를 0으로 만드는 경로가 있어, 한계 준수를 위해 그 구동 법칙을 별도 SPG 적분기에 적용했다.
3. 최대 방위각속도 `55°/s`, 최대 고각속도 `35°/s`, 방위 ±180°, 고각 −15…85°, 안정화 시간과 허용차는 **SIM_TUNED_PUBLIC_UNKNOWN**이며 실제 SPG-62 공개 성능으로 주장하지 않는다.
4. 예약에 `cueStartT`를 추가하고 기존 `startT`를 바꾸지 않았다. 예약 후보의 기하학 점수에 현재 지향 오차를 섞지 않았다. 예약 창이 열려도 대상 트랙, 실제 지향·각속도·settling·장비 상태가 충족되지 않으면 `sarhAlive`와 live ownership을 만들지 않는다. 저하 섹터 fallback도 활성 예약과 실제 정렬을 요구한다.
5. 물리 SARH 송신빔 gain은 이제 cue 방향 대신 서보의 실제 world boresight를 사용한다. RF는 `emitting`과 live ownership이 둘 다 있는 경우에만 생성한다. 3D 안테나도 전체 mount pose를 읽고, RF 콘은 실제 송신 중인 mount에만 표시한다. 렌더러 안의 회전 보간이나 시뮬레이션 피드백은 추가하지 않았다.
6. BDA/DIRECT_BREAKUP 지원 해제 시 송신과 live ownership을 즉시 끄고, alias 승계 시 서보 targetTrackId를 옮긴다. 해제 이후 마지막 각도에서 모터 가속 한계 안으로 감속한다. 기존 수상 ESSM ARH 발사 gate에는 서보 정렬 요구를 추가하지 않았다.
7. 기존 C5 RF fixture의 완벽히 정렬된 안테나 가정은 **DIAGNOSTIC_ONLY** 준비 함수로만 구성했다. 실제 발사·스케줄러에는 이 함수를 호출하지 않는다. 재사용 진단 API `wip13c17Spg62ServoSnapshot()`과 내장 서보 셀프테스트를 추가했다.

## 실행한 검증

| 검사 | 결과 |
| --- | --- |
| 패키지 14개 record gzip/길이/SHA-256 및 메인 JavaScript 문법 | 통과 |
| 압축 해제 후 전체 스크립트 VM 초기화, seed `1350501` | 13개 실행 스크립트 초기화, `CORE SELFTEST` 실패 0 |
| C17 물리 서보·할당 VM 회귀 | 90° 표적 첫 틱 순간이동 없음, 최초 정렬/조명 `2.3333 s`, 최고 측정 가속도 `2.5000000000000013 rad/s²`(부동소수점 허용 오차), 최고 속도 `0.95993 rad/s` |
| 방위 wrap, 프레임 묶음 1/8/16, 예약 철회 | +179°→−179° 최단 방향, 동일 fixed-tick 결과 exact, 지원 철회 시 RF와 소유권 해제 |
| C5 실제 RF/수상피해 진단, seed `1350501` | 12/12: 수상 반사파·해면 반사·SARH 추적·표적함 물리 충돌/피해 포함 |

재실행:

```text
node AEGIS_WIP13C17_SERVO_REGRESSION.cjs Aegis_SIM_v48_WIP13C17.html
node AEGIS_WIP13C17_VM_REGRESSION.cjs Aegis_SIM_v48_WIP13C17.html
```

## 검증 잔여와 위험

- 실제 브라우저에서 출항·발사 UI, SPG 3D 구동, 2D/3D 왕복, 1×/8×/16× 전투 결과, 콘솔과 WebGL을 아직 확인하지 못했다. 로컬 Chromium 실행 파일은 없었고 브라우저에서 로컬 HTTP 주소가 차단되었다.
- C5 장시간 SM-2 실비행 fixture는 이 VM 환경에서 과도하게 오래 걸려 중단했다. 실제 해상 명중/실패 궤적, 이동 표적 추적, WIP116 다중 예약·손상 cascade, BDA/alias 전체 시나리오의 동적 회귀는 병합 전 수행해야 한다.
- 장래 예약 사이의 slew feasibility는 이 단계에서 scheduler에 넣지 않았다. 멀리 떨어진 표적을 뒤늦게 예약하면 계획 시각보다 RF 개시가 늦어질 수 있으며, 실제 안테나가 정렬되기 전의 허위 조명은 발생하지 않는다.
- C5 RF fixture는 테스트 전용 서보 스냅을 사용한다. 따라서 그 fixture의 통과는 실제 초기 선회가 끝나고 SM-2가 명중한다는 증거가 아니다.

## GitHub 후속 절차

사용자가 결과 HTML을 **기존 WIP13C 작업 브랜치**에 업로드하고 알려주면, 원격 SHA-256을 위 값과 대조한다. 그때 이 상태 문서, 두 검사 파일, 체크섬과 README/작업 지침의 현재 기준을 같은 브랜치에서 함께 갱신한다. 이번 단계에서는 새 브랜치·커밋·PR·병합을 만들지 않았다.

상태 문서 SHA-256과 기타 파일 해시는 동봉된 `SHA256SUMS_v48_WIP13C17.txt`에 기록했다.
