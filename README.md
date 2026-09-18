# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP12A.html`](Aegis_SIM_v48_WIP12A.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP12A.md`](AEGIS_PLAN_STATUS_v48_WIP12A.md)
- 설계 계약: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- HTML SHA-256: `60705246ef0b659dadf67e23ca9b84bf7dc2cb477857d9714223291c564c3729`
- 상태: WIP12A 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP12A 핵심 범위

- `TerminalProjectileSpec`, 가변 projectile state, ordered `ImpactTrace`, `BoundaryImpactResult`와 채널별 `DamagePacket` 공통 계약
- 전체 질량과 실제 coherent penetrator 질량 분리; 운동에너지·운동량·yaw는 상태에서 파생
- normalized `direction`과 `bodyAxis`를 별도 보존해 속도 방향과 탄체 종축의 3D 불일치 표현
- `BOUNDARY`, 저항 없는 `EMPTY`, 실제 물질의 `DAMAGE_VOLUME`, 저항 없는 `CREW_EXPOSURE` 분리
- 방향·속도·무결성 변화 뒤 현재 ray로 BVH/AABB를 다시 질의하는 event-driven traversal
- 다음 접촉, volume exit, projectile stop, fuze expiry 중 가장 빠른 사건을 결정적으로 처리하는 시간 기반 신관
- 무기 이름이 아닌 충돌 regime으로 solver 선택; thin ductile plate, light structure, volume crush 경로 활성화
- homogeneous/face-hardened armor는 검증되지 않은 임시식을 넣지 않고 명시적 `UNSUPPORTED_SOLVER` 결과 반환
- `RICOCHET/STOPPED/PARTIAL/PERFORATED`와 `INTACT/DEFORMED/FRACTURED/SHATTERED`를 독립 축으로 기록
- 질량·에너지·운동량 closure를 검사하는 `ImpactBudget`
- 직접 관통, plug/spall, 탄두 파편, 폭압, 열·소이, 파괴구·침수, 구조 충격, 승조원 노출 채널 분리
- `impactEventId` 기반 중복 적용 방지와 기존 침수·구조·승조원·VLS/장비 consumer 연결
- 아라미드는 직접 관통 저항이 아니라 rear-spall/fragment 채널만 감쇠
- `TEST_12P7_AP`부터 `TEST_127_SAP`까지 `DIAGNOSTIC_SIM_TUNED` 탄체 6종과 각 탄체의 도탄·정지·부분·관통·shatter 경계 fixture
- Kh-35U/Kh-32 live impact는 공통 API의 `LEGACY_ASM_PENETRATION_COMPAT`를 거치되 기존 WIP11C 계산·결과·전투 RNG를 exact 보존
- damage patch는 surface/local 좌표·구멍·균열·잔존두께 계약과 진단 fixture만 정의하고 persistent ledger는 비활성

## 검증

- 기존 정적 계약 6종, WIP11C `32/32`, WIP12A `29/29` 정적 계약 통과
- WIP12A Playwright `2/2 PASS`
- Playwright 전체 `30/30 PASS` (로컬 Three.js 경로 사용)
- 6종 진단탄 정상 traversal과 각 탄의 도탄·정지·부분·완전 관통·shatter 경계 통과
- EMPTY 상태 불변·신관 시간 진행, 방향 변화 뒤 geometry 재질의, volume 내 감속 기반 신관 만료, DUD와 tie ordering 확인
- `PERFORATED + SHATTERED` 독립 결과 축과 질량·에너지·운동량 ledger closure 확인
- 아라미드 적용 전후 직접 관통 work 불변, spall/fragment 감소 확인
- 동일 packet 1회 적용 시 침수 opening, 구조 충격, 승조원 피해와 VLS/장비 피해가 발생하고 재적용은 `DUPLICATE_IMPACT_EVENT`로 거부됨을 확인
- 기존 Kh-35U/Kh-32 관통 결과와 전투 RNG exact parity 확인
- 동일 fixture의 `1×/8×/16×` 결과 exact 일치 및 `64×` 4,096건 과부하 계측 완료
- 기존 Kh-32/ESSM 유령 트랙, CIWS, 침수, 구조, 승조원, 재질, 운영 snapshot zero-mutation, 3D 회귀 통과
- Workflow YAML parse 통과, WIP12A 전용 2개 job을 포함한 총 `22`개 job 구성

## 다음 단계

- WIP13: 해상사격 FCS
- WIP14: 간단한 표적함과 복수 함선 프로파일
- 실제 포탄/함포 운용을 연결할 때는 WIP12A 커널에 생산 탄약 데이터를 별도 검증하여 추가한다.
- homogeneous/KC 장갑 solver와 persistent damage patch ledger는 검증·snapshot migration을 동반하는 별도 단계로 유지한다.
- 기존 ASM의 신규 solver 이전은 compatibility parity와 별도로 승인하기 전까지 수행하지 않는다.

## 범위 밖

WIP12A는 실제 함포 발사, 포탑·탄창 운용, 외탄도, 공기저항·바람·분산, 해상사격 FCS, 새 표적함, 실전 중장갑 solver 또는 persistent damage patch를 활성화하지 않는다.

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며, WIP10·WIP11·WIP11A·WIP11B·WIP11C는 각각의 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
