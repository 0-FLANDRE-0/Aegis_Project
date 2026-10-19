# v48 WIP MAP_A — 상태 / 인계

- 개발 기준: UI_A1 `0452e1066a5abddd144788c4cba80e38cec97afd` / SHA `fd7079e9154e8778f7f5a340e6102c8843930b9865d4dc1135714c4847cdc3b8`.
- 결과: `Aegis_SIM_v48_WIP_MAP_A.html` / 18,047,616bytes / SHA `68c13d352c3e80ab8bae1e08138ee42284c426f7fb7cce24e9d64941b34362b5`. WIP 유지.
- 작업 브랜치: `map-a`. [A–P 전체 보고](docs/map/A/REPORT.md), [검수 색인](docs/map/A/evidence/verification-summary.json), [재현](docs/map/A/README.md), [정보 출처 감사](docs/map/A/OBSERVATION_AUDIT.md).

## 완료

- [실행 HTML](Aegis_SIM_v48_WIP_MAP_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_MAP_A.md), [SHA](SHA256SUMS_v48_WIP_MAP_A.txt), [A–P·스크린샷](docs/map/A/REPORT.md), [재현](docs/map/A/README.md), [출처 감사](docs/map/A/OBSERVATION_AUDIT.md). UI_A1 `0452e10` 위 `map-a`.
- 조회/통제/현재 도구/사격 지정 예약 슬롯 분리,20px 객체 탭·겹침 후보·우클릭/550ms/펜 메뉴,정보창·통제/마지막 WP 취소와 연속 방위 테이프. SYS에서 기존 입력으로 전환 가능하며 원본 pointerup은 byte-exact다.
- **1042/1042 assertions /27 suites PASS, 페이지 오류0**. 200회 조회/메뉴 명령 변화0,120초 해시 동일,3개 지도 크기/DPR2.8125·36개 UI 조합·기존 native 회귀420건 확인. 식별 번호 불변/저장 시 트랙·식별 초기화(기존 정책),하푼 계획 Undo 후 발사된 memory/route/INS 변화0,no-arg LOCK/EMCON 회귀 포함.
- 무DL 하푼은 현재 위치 비공개,자함 발사 시각/지정 트랙/고정 계획만 표시한다. 시뮬·센서·물리·판정·발사 권한·게임 저장 스키마·모델을 보존한다. 모바일100% 바 세로42.84px·가로24px 유지.
- 원본18,047,616bytes (+17,772), SHA `68c13d352c3e80ab8bae1e08138ee42284c426f7fb7cce24e9d64941b34362b5`. UI_A1 네 파일 동일 bytes/blob archive. 원본 전체 업로드·독립 원격 readback은 docs/map/A/remote-publication.json. Actions dispatch/main·기존 브랜치 병합/새 PR 없음.
- 다음은 MAP_B 사격 지정 UI/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환과 임시 커서 연결 제거다.3D 미니 CIC 입력·실폰 GPU/FPS/펜 하드웨어는 미검증이다.

## 검수·시뮬 경계

- 1042/1042 assertions, 27 suites, 오류0. seed1831565813.200회 지도 조회/후보/메뉴와 무입력 실행 모두7,200ticks/120초 상태 SHA `9c594b8b9a83eb0506a9ac20b19328b1880e17e3f25583093e6983db5847c136`.
- UI_A1 native 컨트롤/교전 위젯, pause/resume, 헬기·APS·ISAR·EMCON·하푼·SOV 손상/침수/저장·DDG/CG baseline 회귀.14개 packed 블록 검증, 기존13개 블록/모델 동일,기존 게임 저장/legacy pointerup 동일.
- 선택·통제는 UI transient, 게임 저장에 추가 안 함. 기존 작전 불러오기는 트랙/식별 초기화 정책 그대로. 기존 snapshot/센서·판정은 변경하지 않음.
- 정보창은 관측/수신/자함 보유 데이터만 사용. 적 truth/private association getter 읽기0.무DL 하푼 실시간 위치/INS/시커 공개 없음.
- 최종 소스의7개 기존 함수만 명시 변경: lockByCursor,drawRadar,UI shell update/restore/windowSize/focusWindow/focusOpen. UI/입력과 정확한ID의 기존 명령 어댑터.

## 남은 범위

MAP_B의 사격 지정·무장 플라이아웃·사거리/단발/살보·작은 발사 버튼·하푼 모드 전환은 미구현이다. 중앙 planningReason에 새 계획 상태를 추가하고 MAP_A_LEGACY_CURSOR_BRIDGE를 제거할 것.3D PIP 입력/ROE 단계/별칭과 HUD·손상 창 정리는 후속 범위다.실폰 GPU/FPS/실제 펜은 미측정이다.구상서 파일이 없으므로 상세 사용자 지시서를 기준으로 삼았다.

## 보존·게시

UI_A1 HTML/상태/SHA/workflow는 `archive/v48/WIP_UI_A1/`에 같은 bytes/blob으로 보존한다.원본 전체 GitHub 업로드와 전체 blob readback,보호 브랜치 불변을 기록한다.Actions 사용 불가 상황을 반영하여 workflow는 manual-only이고 실행하지 않는다.main/기존 브랜치 병합/새 PR은 하지 않는다.
