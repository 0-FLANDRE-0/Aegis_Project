# AEGIS v48 WIP13C18 — 수상 FCS 표시와 해면/선체 교차 순서

## 기준과 판정

- 기준 HTML: `Aegis_SIM_v48_WIP13C17.html`, SHA-256 `efa5fd89978e90341ce317d8c7d76f17ae31796413e1dcc2a4d8f5af3a68e193`.
- 결과 HTML: `Aegis_SIM_v48_WIP13C18.html`, SHA-256 `0590cb4967a9be2afdf88c550fb0eca70984cd3aff8f975c40b4835133c721b3`.
- 결과 decoded main: SHA-256 `fe65496f8c155ddbe8e16dc8c026b1b1b8543862c67f6d65bbbca5f41713e300`.
- **13C 전체 종료: HOLD.** 이번 범위의 정적·제한적 VM 검사는 통과했으나, 최종 소스의 수상 실비행 17건 및 실제 WebGL/모바일 브라우저 검사는 통과했다고 주장할 수 없다.
- 번호 `WIP14A1`은 C6에서 앞당긴 월드좌표 작업의 과거 오기다. C17 원본을 덮지 않았고 기존 브랜치에 원격 쓰기·병합을 하지 않았다. GitHub `0-FLANDRE-0/Aegis_Project`의 기존 `feat/v48-wip13c17-spg62-servo` 브랜치는 조회 시점에 `main`과 동일한 커밋이었으며, 이번 기준은 사용자가 지정한 로컬 C17 HTML이다.

## 변경

1. 선택된 수상 트랙 카드의 `FCQ`를 함포 전용 `GUN FCQ`로 명시했다. 같은 카드에 익명 트랙을 대상으로 한 SM-2·ESSM 각각의 수상 FCS 품질, 사전검사 차단 사유, 실제 SPG 예약·servo·RF 상태와 ESSM ARH 인계 여유를 읽기 전용으로 표시한다. 화면 계산은 발사·예약·조명을 생성하지 않는다.
2. 수상 SM-2/ESSM의 같은 fixed tick에서 해면과 선체를 모두 가로지르면 실제 선분 매개변수의 선행 사건을 채택한다. 해면 선행 시 RF/피해용 hull contact를 만들지 않고 기존 해면충돌 경로에 해면 교차 위치를 전달한다. 동시 교차는 선체 접촉을 유지한다.
3. SPG 기계식 servo, 미사일 유도·시커, VLS, 함선 추진, 함선 피해 solver 및 13개의 다른 압축 자산 레코드는 그대로 보존했다. 패치 재생성은 `AEGIS_WIP13C18_PACK.py`와 `AEGIS_WIP13C18.patch`를 사용한다.

## 현재 소스에서 확인한 검사

| 검사 | 결과 | 한계 |
| --- | --- | --- |
| 14개 gzip 레코드 복원, 13개 비수정 자산 바이트 일치, main syntax | PASS | 정적 검사 |
| 전체 게임 스크립트 VM 초기화와 `__CORE_SELFTEST_FAILURES__` | PASS, 실패 0 | 브라우저가 아님 |
| C5 수상 SARH RF/피해 진단 | 12/12 PASS | 테스트 전용 servo 정렬 상태 사용; 자연 선회 실비행이 아님 |
| C17 servo 가속·최고속도·wrap·예약 철회·1/8/16 고정틱 | PASS | 제한된 VM fixture |
| 해면 우선·선체 우선·동시 교차·해면 단독·무접촉 | 5/5 PASS | terminal 분기 단위 검사 |
| 수상 카드의 두 FCS·ARH·SPG 표시, 보호 대상 차단, 순수 읽기 | PASS | VM 카드 출력; 실제 화면 픽셀 확인 아님 |

## 실비행/브라우저 경계

보관된 C10의 **1200틱 실제 센서 워밍업 → 익명 수상 트랙 수동 지정 → SM-2/ESSM 실제 발사 → 최대 1800틱 선체 접촉** 하네스를 C18 소스에 이식했다. 첫 SM-2 90° 사례는 워밍업과 발사를 통과했으나, 이 환경의 Node VM에서 발사 후 약 253틱 이후의 갱신에 과도한 시간이 걸려 120초 안에 완주하지 못했다. 계측상 실제 RF 반사체 44개 생성, SARH association 및 EKF 갱신은 반환했고 이후 미사일 유도 갱신이 진행되었다. 시간이 걸리는 정확한 호출과 실제 브라우저에서의 재현 여부는 아직 확인되지 않았다. 별도의 기존 C5 짧은 실비행 진단(`maxTimeS:20`)도 이 VM에서 120초 안에 반환하지 않았다. 따라서 이전 C7~C10의 `17/17`을 C18에 합산하지 않는다.

클라우드 브라우저는 `file:` 로컬 HTML URL을 보안 정책으로 차단했고, 이 실행 환경에는 로컬 Chromium이 없다. 실제 RAF, 3D SPG, 2D/3D 왕복, 모바일 카드 배치, 콘솔·WebGL 및 1/8/16/64 실제 UI 처리량은 미검증이다. 차단된 URL 경로를 다른 브라우저 우회로 재시도하지 않았다.

## 남은 13C 종료 조건

1. 위 실비행 정체의 phase를 분리하고 실제 게임 코드 문제라면 수정한다. 동일 최종 소스로 SM-2/ESSM 8방위와 SPG 손상 ESSM, SPG 다중 예약·지원 철회/BDA·alias, 해면 미스 피해 0을 재실행한다.
2. 실제 브라우저에서 선택 카드·VLS·비행·3D SPG/RF·파괴구/화재/침수, 2D/3D 전환, 시간배율·모바일 표시를 검증한다. 현재 버전에는 접근 가능한 브라우저 경로가 확보되지 않았다.
3. 원래 13C 계획의 surface proximity-first 신관 경로는 직접 선체 접촉과 별도의 RF/기하·피해 분기 설계가 필요하다. 이번 C18의 해면/선체 선행 비교가 근접신관까지 구현했다는 뜻이 아니다.
4. C13 인계가 남긴 Kh-32 늦은 획득 근접 미스, 실제 GPU/발열/장시간 다중 피격 및 실제 64배속 처리량은 별도 검증 대상이다.

재현 명령:

```text
python AEGIS_WIP13C18_PACK.py
node AEGIS_WIP13C17_SERVO_REGRESSION.cjs Aegis_SIM_v48_WIP13C18.html
node AEGIS_WIP13C17_VM_REGRESSION.cjs Aegis_SIM_v48_WIP13C18.html
node AEGIS_WIP13C18_TERMINAL_REGRESSION.cjs Aegis_SIM_v48_WIP13C18.html
AEGIS_CARD_ONLY=1 node AEGIS_WIP13C18_FULL_FLIGHT.cjs Aegis_SIM_v48_WIP13C18.html
timeout 120s node AEGIS_WIP13C18_FULL_FLIGHT.cjs Aegis_SIM_v48_WIP13C18.html '{"weapon":"SM2","bearingDeg":90,"ownSpeedKt":25}'
```

`AEGIS_WIP13C18_DIAGNOSTIC_HOOK.js`는 VM 하네스가 메인 스크립트 안에 주입하는 테스트 전용 코드다. 최종 HTML에는 포함되지 않는다. 상태 문서와 나머지 파일 해시는 `SHA256SUMS_v48_WIP13C18.txt`에 따로 기록한다.
