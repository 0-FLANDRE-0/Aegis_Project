## 최신 개발 기준 — 설계 사거리 정렬 WIP RANGE_A + ENV_C

- ALL4_TERM `9a6838a` 위 `range-a-env-c`. [실행ZIP(HTML1개)](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-a-env-c/Aegis_SIM_v48_WIP_RANGE_A_HTML.zip?download=1) · [리포트ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/range-a-env-c/Aegis_SIM_v48_WIP_RANGE_A_REPORT.zip?download=1).
- [HTML](Aegis_SIM_v48_WIP_RANGE_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md), [SHA](SHA256SUMS_v48_WIP_RANGE_A.txt), [0단계/8값/목표 부족/전체검수](docs/missile/range/A/REPORT.md), [ENV_C전체표·전후 비교·120궤적](docs/envelope/C/REPORT.md).
- ER/SM-6 설계8숫자만360/450km로 정렬했다. 정지 표적 고도1/10/20km 최대는ER136/135/241, SM-6 135/132/286km로 줄었다. 목표에 억지로 맞추지 않고 WIP 결과로 남긴다. 3,884명명 함수/추진/항력/유도/신관/배터리/종료기 보존, MR/ESSM 변경0.
- 0단계/정렬후6조건/전체ENV_C 각각2회 비트 동일. 전체96조합/120궤적, 각 26,714사격. 실제요격점 거리·1km 전역상한 탐색, 계산표 해시 내장. 표를 지도/발사권한/AI에 연결하지 않았다.
- 기존420회귀+UI88+종료기16 통과. 정상240발OFF/ON 각85명중, 기존83명중 보존+2회복, 조기종료0. 자연탐지/전체월드/WebGL8발 통과. 게임/사본 6,806샘플 오차0, 무표적120초truth/RNG hash 동일, 전투는8값복원으로 인과 확인.
- SM-6 100km/5km 접근250m/s seed12002 해면 충돌은OFF3/ON3 모두명중으로 회복. 저고도 이탈3+횡단18조사는수정0이며 횡단11건도해면충돌했다. [조사](docs/envelope/C/results/LOW_ALT_INVESTIGATION.md).
- 원본 18,283,304bytes / SHA `8f504eb45c19c34e473d0d04f08180afde95a9c72b5ec935ec0204bd9d7246b5`. ALL4_TERM8파일 동일 bytes/blob archive, ENV_A/B 및 기존 종료기 자료 변경0. 실행/리포트ZIP 분리·전체 원격readback 영수증은발행후추가한다. Actions/PR/main·이전브랜치 병합 없음.

## 직전 개발 기준 — 누적 Dynamic B4 ALL4 + 관측 기반 종료 WIP ALL4_TERM

- [실행 다운로드 — HTML 1개 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/missile-b4-termination/Aegis_SIM_v48_WIP_ALL4_TERM_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/missile-b4-termination/Aegis_SIM_v48_WIP_ALL4_TERM_REPORT.zip?download=1).
- [HTML](archive/v48/WIP_ALL4_TERM/Aegis_SIM_v48_WIP_ALL4_TERM.html), [상태](archive/v48/WIP_ALL4_TERM/AEGIS_PLAN_STATUS_v48_WIP_ALL4_TERM.md), [SHA](archive/v48/WIP_ALL4_TERM/SHA256SUMS_v48_WIP_ALL4_TERM.txt), [실제 게임·종료 검수](docs/missile/termination/A/REPORT.md), [ENV_B 전후 사거리·궤적](docs/envelope/B/REPORT.md), [재현](docs/missile/termination/A/README.md).
- 최신 PIP_B `294bbb0` 위 `missile-b4-termination`. 4종 B4를 자함/NPC에 적용, 중복 이식 방지. 원안의 SARH/DL 대체 유도 중 조기 종료와 임의 65초 교차 시계를 종료기에서 보완했다. 실제 표적 좌표를 종료 판단에 넣지 않는다. B4 코드·수치 및 기존 신관/추진/항력/시커/Kappa 계산 보존, SM-6 게임 배터리만480초.
- 240발 ON/OFF + 대체 지원36발에서 기존 명중99건/조기 종료0. 실제 RF 소실·재획득·미획득, 배터리8건/정식VLS4건 및 자연 SPY트랙/전체fixed tick/WebGL8발 검사 통과. 기존 관련 회귀420/420 + UI88/88. 세부 조건·초기 실패·한계는 보고서를 따른다.
- ENV_B는 96조합/120궤적, 독립2회 각각11,458사격·46,068,182bytes 동일. 실제 게임/분리 경로5,894샘플 오차0, Chromium 사거리경계151건 일치. ENV_A 구판 자료는 변경하지 않았다. 표는 아직 지도/교전 권한에 연결하지 않는다.
- **알려진 결과 변화:** SM-6 100km/5km/접근250m/s/seed12002는 B4 후 종료기OFF도 비명중 후 SEA_IMPACT (구판명중,3회재현). 요청한 B4 수치를 유지하며 조기 종료와 분리 기록한다. 전면 안정판 승격 없음.
- 원본18,278,162bytes, SHA `c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800`. 이전 전달세트8개 동일 bytes/blob archive. 원본/두 ZIP 직접 업로드·독립 원격 readback, Actions dispatch/PR/main·이전브랜치 병합 없음. 다음은 알려진 B4 결과 검토와 MAP_B다.

# AEGIS 현실형 함정 방위 시뮬레이터

## 이전 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A

- [실행 다운로드 — HTML 1개 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/pip-b-env-a/Aegis_SIM_v48_WIP_PIP_B_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/pip-b-env-a/Aegis_SIM_v48_WIP_PIP_B_REPORT.zip?download=1). 실행 ZIP을 풀어 HTML을 연다. 리포트에는 검증·그림·10Hz CSV·계산표·원시 결과·재현 소스·체크섬을 넣고 실행 HTML은 제외한다.
- [실행 HTML](archive/v48/WIP_PIP_B/Aegis_SIM_v48_WIP_PIP_B.html), [상태](archive/v48/WIP_PIP_B/AEGIS_PLAN_STATUS_v48_WIP_PIP_B.md), [SHA](archive/v48/WIP_PIP_B/SHA256SUMS_v48_WIP_PIP_B.txt), [P1–P5·스크린샷](docs/pip/B/REPORT.md), [ENV_A·그래프·사거리 표](docs/envelope/A/REPORT.md), [재현](docs/pip/B/README.md). PIP_A `662eb14` 위 `pip-b-env-a`.
- 제목줄 아래 전체를 PiP 지도로 사용한다. 기존 중심/전환 버튼 노드와 리스너는 제목 메뉴로 이동하고 빈 바다 메뉴에도 연결했다. 락온 카드 본문은 일반 창으로 옮겨8Hz 갱신, 닫기 억제/다음 락 재개방을 제공한다. 정보/메뉴/후보/제목11px, 일반 버튼28px+36px hit, 위험 조작40px를 유지한다.
- SYS의 2D 센서 빔 표시 기본 OFF. 트랙/ESM/항로점/섬/3D 센서는 보존한다. 자함의 청록 원은 world 단위 항적선 두께가 확대되던 표시 오류였으며 화면1.5px로 수정했다. 실제 원인 분리·확대율별 검사를 보고서에 기록했다.
- ENV_A는 변경하지 않은 게임 비행·유도·로프트·신관241개 함수의 독립 진단이다.4종의96개 최대 거리 조합/120개 궤적·10Hz CSV와 표를 내장한다. 실제 장비 성능 비교는 없으며 시작 시 계산하지 않는다.300km는 검사 상한이다. 표 안쪽에도 실패 구간이 있으므로 지도/발사 판단에 아직 연결하지 않는다.
- 표시·기존 회귀1358/1358건(35 suites), ENV_A25/25건(5 suites) PASS. 120초 상태 해시 동일, 전체 진단2회44,221,270bytes 동일, 최종 브라우저156개 사거리 경계 일치. 실제 게임/독립 경로362샘플 오차0. 세부 후보/런타임 차이와 검증 환경은 보고서에 기록한다.
- 원본18,265,254bytes(+204,315), SHA `ad6ed26d8011fd1bcab80c66eac06a63c748e52b471eb622ef38a2ad26498a55`. 모델/저장/고정tick/센서/권한 보존, PIP_A6개 전달 파일 동일 bytes/blob archive. 검수 합계와 환경 한계는 연결된 최종 보고서·영수증에 기록한다.
- GitHub Actions는 수동 workflow만 준비하며 실행하지 않는다. main/기존 브랜치 병합·새 PR 없음. 다음은 MAP_B 사격 지정/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환이다.3D PiP와 실제 폰 GPU/펜 검증은 후속이다.

## 직전 개발 기준 — 조작 가능한 지도 PiP WIP PIP_A

- [실행 다운로드 — HTML 1개 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/pip-a/Aegis_SIM_v48_WIP_PIP_A_HTML.zip?download=1) · [ZIP 체크섬](archive/v48/WIP_PIP_A/SHA256SUMS_v48_WIP_PIP_A_HTML_ZIP.txt). 압축을 풀고 HTML을 브라우저로 연다. 현재는 실행 파일만 제공하며 다음 기능 완료본부터 리포트 ZIP을 별도로 제공한다.

- [실행 HTML](archive/v48/WIP_PIP_A/Aegis_SIM_v48_WIP_PIP_A.html), [상태](archive/v48/WIP_PIP_A/AEGIS_PLAN_STATUS_v48_WIP_PIP_A.md), [SHA](archive/v48/WIP_PIP_A/SHA256SUMS_v48_WIP_PIP_A.txt), [A–J·스크린샷](docs/pip/A/REPORT.md), [재현](docs/pip/A/README.md), [그리기 감사](docs/pip/A/RENDER_AUDIT.md). MAP_A `c1297b6` 위 `pip-a`.
- 같은 관측 트랙·MAP_A 선택/통제/계획을 쓰는 실제 2D PiP. 별도 거리/중심/추적, 팬/휠/핀치·메뉴·항로점·하푼 계획과 주화면 전환. 기본 40km/4Hz, SYS 2/4/10Hz, 최소 창200×160·반경0.1km, m 표시.
- 후보 [확대]는 전부 보임 우선의 최대 확대. 40px 미만이면 분리 불가/주화면 전환, 목록 유지. ESM 처음40px 판정 제외. 기존 간이 지도는 DEAD_LEGACY로 원문 보존하고 숨겨진 메인2D 페인트는0회다.
- **1271/1271 assertions /32 suites PASS, 페이지 오류0**. MAP_A 런타임994건과 새 핀 기준 정적48건, PiP 입력/순수성/기하/120초/실제3D 검증. PiP ON/OFF 및 기준·수정·pause/resume120초 해시 동일. 물리·센서·판정·발사 권한·게임 저장/모델 보존.
- 원본18,060,939bytes (+13,323), SHA `76c77b5c80835f87654c8aa39cd6a82c1ad66de8bc408ebad675997157024847`. 최소 PiP100m 간격42.84~47.88px. 소프트웨어 WebGL 전후 평균1275.60→1039.96ms(18.47% 감소); 실폰 FPS가 아니며 낮은 전체FPS에서는 PiP도 같은 RAF 상한을 받는다.
- MAP_A 네 파일 동일 bytes/blob archive. 전체 원본 업로드·독립 readback은 docs/pip/A/remote-publication.json. Actions dispatch/main·기존 브랜치 병합/새 PR 없음. 다음은 MAP_B 사격 지정/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환과 임시 커서 연결 제거. 3D PiP·실폰 GPU/펜 하드웨어는 후속.

## 직전 개발 기준 — 지도 조작 WIP MAP_A (당시 기록)

- [실행 HTML](archive/v48/WIP_MAP_A/Aegis_SIM_v48_WIP_MAP_A.html), [상태](archive/v48/WIP_MAP_A/AEGIS_PLAN_STATUS_v48_WIP_MAP_A.md), [SHA](archive/v48/WIP_MAP_A/SHA256SUMS_v48_WIP_MAP_A.txt), [A–P·스크린샷](docs/map/A/REPORT.md), [재현](docs/map/A/README.md), [출처 감사](docs/map/A/OBSERVATION_AUDIT.md). UI_A1 `0452e10` 위 `map-a`.
- 조회/통제/현재 도구/사격 지정 예약 슬롯 분리,20px 객체 탭·겹침 후보·우클릭/550ms/펜 메뉴,정보창·통제/마지막 WP 취소와 연속 방위 테이프. SYS에서 기존 입력으로 전환 가능하며 원본 pointerup은 byte-exact다.
- **1042/1042 assertions /27 suites PASS, 페이지 오류0**. 200회 조회/메뉴 명령 변화0,120초 해시 동일,3개 지도 크기/DPR2.8125·36개 UI 조합·기존 native 회귀420건 확인. 식별 번호 불변/저장 시 트랙·식별 초기화(기존 정책),하푼 계획 Undo 후 발사된 memory/route/INS 변화0,no-arg LOCK/EMCON 회귀 포함.
- 무DL 하푼은 현재 위치 비공개,자함 발사 시각/지정 트랙/고정 계획만 표시한다. 시뮬·센서·물리·판정·발사 권한·게임 저장 스키마·모델을 보존한다. 모바일100% 바 세로42.84px·가로24px 유지.
- 원본18,047,616bytes (+17,772), SHA `68c13d352c3e80ab8bae1e08138ee42284c426f7fb7cce24e9d64941b34362b5`. UI_A1 네 파일 동일 bytes/blob archive. 원본 전체 업로드·독립 원격 readback은 docs/map/A/remote-publication.json. Actions dispatch/main·기존 브랜치 병합/새 PR 없음.
- 다음은 MAP_B 사격 지정 UI/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환과 임시 커서 연결 제거다.3D 미니 CIC 입력·실폰 GPU/FPS/펜 하드웨어는 미검증이다.

## 직전 개발 기준 — 모바일 UI WIP UI_A1 (당시 기록)

- [실행 HTML](archive/v48/WIP_UI_A1/Aegis_SIM_v48_WIP_UI_A1.html), [상태](archive/v48/WIP_UI_A1/AEGIS_PLAN_STATUS_v48_WIP_UI_A1.md), [SHA](archive/v48/WIP_UI_A1/SHA256SUMS_v48_WIP_UI_A1.txt), [수치·스크린샷](docs/ui/A1/REPORT.md), [재현](docs/ui/A1/README.md). UI_A `30428d6` 위 `ui-a1`.
- 모바일 상태 바는 기본100%에서 세로42.84px·가로24px다. 모든 재고를 유지하고 창 목록/추가를 아이콘으로 압축했다. 창10px 글자·작은 기본 크기, 탭 전면화·제목줄 이동·겹침과 순서 저장을 제공한다. FIRE/LOCK 40px 보호 크기는 유지한다.
- EMCON은 바로 전환한다. 교전 칩은 위쪽에 수동/반자동/자동 팝업을 표시하고 기존 canonical 조작 함수를 호출한다. 시뮬·센서·판정·발사 권한·게임 저장·모델은 유지한다.
- **456/456 assertions /4 suites PASS, 페이지 오류0**. 36 화면/배율/함종 조합, 실제 창 조작·입력 격리·저장, native 탭 조작·위젯 발사 비교,120초 상태·pause/resume 동일. UI_A의1144건은 당시 기록이며 이번 합계에 넣지 않는다.
- 원본18,029,844bytes (+6,522), SHA `fd7079e9154e8778f7f5a340e6102c8843930b9865d4dc1135714c4847cdc3b8`. UI_A 네 파일 동일 bytes/blob archive. 원본 전체 업로드·독립 원격 readback 기록은 docs/ui/A1/remote-publication.json. Actions dispatch/main·기존 브랜치 병합/새 PR 없음.
- 확대UI는 내용에 맞춰 높이가 늘어난다. 배치schema2는 예전 배치를 새 프리셋으로 시작하며 UI 크기 설정은 보존한다. 실폰 GPU/FPS 미측정, HUD/SPY·손상 창 편입/ARM 분리/지도 PIP는 UI_B.

## 직전 개발 기준 — UI WIP UI_A (당시 기록)

- [실행 HTML](archive/v48/WIP_UI_A/Aegis_SIM_v48_WIP_UI_A.html), [상태](archive/v48/WIP_UI_A/AEGIS_PLAN_STATUS_v48_WIP_UI_A.md), [SHA](archive/v48/WIP_UI_A/SHA256SUMS_v48_WIP_UI_A.txt), [검수·스크린샷](docs/ui/A/REPORT.md), [재현](docs/ui/A/README.md). VP_A `3afd0fc` 위 `ui-a`.
- 공용 하단 상태 바·창 6종·공용 교전 위젯·3D 방위 테이프, DOM 전용 UI 85/100/115/130%와 전체화면·가로 고정 설정. 기존 컨트롤은 같은 노드를 이동하며 센서·판정·발사 권한·게임 저장·모델을 보존한다.
- **1144/1144 assertions / 24 suites PASS, 페이지 오류0**. DDG/CG × 9크기 × 3배율 54조합. 원래 127개 노드 연결·중복 id 0, 기존 420건 전체와 120초 상태·pause/resume 동일성 확인.
- 원본18,023,322bytes (+20,368), SHA `a4b6825df6c28eb8f0747f73ec9469c90f277f96eb23e55be67298a6a1cab8e4`. VP_A 네 파일은 동일 bytes/blob archive. 전체 HTML 직접 업로드·원격 전체 readback. Actions dispatch/main·기존 브랜치 병합/새 PR 없음.
- 좁은 화면은 재고 생략·가로 스크롤 없이 표시하므로 상태 바가 2줄을 넘는다. SHIP/손상·침수 창 편입, ARM 분리와 실제 지도 PIP는 UI_B. 실폰 GPU/FPS는 미측정.

## 직전 개발 기준 — 화면 WIP VP_A (당시 기록)

- [실행 HTML](archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html), [상태](archive/v48/WIP_VP_A/AEGIS_PLAN_STATUS_v48_WIP_VP_A.md), [SHA](archive/v48/WIP_VP_A/SHA256SUMS_v48_WIP_VP_A.txt), [전체 보고](docs/viewport/A/README.md), [A–I 검수](docs/viewport/A/VERIFICATION.md). SOV_A `c7d498d` 위 `viewport-a`.
- AEGIS_VIEWPORT로 visible rect/version 통합. 2D 거리 km 유지·공통 입력 변환, 3D 짧은 변52°·viewOffset·정규화 팬, 카탈로그38°. outer CSS와 시뮬/센서/ROE/저장/물리는 보존한다.
- **567/567 assertions /19 suites PASS, 페이지 오류0**. 7크기, 30회/0.097432s 연타, 200ms 이후 panel reflow, 실제 VV/전체화면/터치·DPR, native120초 상태 해시 동일, 기존 헬기/APS/ISAR/하푼/EMCON/손상 회귀 확인.
- 원본18,002,954bytes (+4,506), SHA `432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9`. SOV_A 네 파일을 같은 bytes/blob으로 archive한다. 원본 직접 업로드·원격 전체 bytes 대조. Actions/main·선행 브랜치 병합/새 PR 없음.
- [UI 위치/도크 조사](docs/viewport/A/UI_LAYOUT_REPORT.md), [모바일 coarse](docs/viewport/A/UI_LAYOUT_COARSE_REPORT.md), [604컨트롤+42패널 분류](docs/viewport/A/UI_CLASSIFICATION.tsv), [SOV 자함화](docs/viewport/A/SOV_PLAYER_READINESS.md), [파랑 응답](docs/viewport/A/WAVE_RESPONSE_REPORT.md). 조사 두 기능은 미구현 유지. 기존 좁은 화면 UI 겹침/잘림은 다음 도크 단계, 실폰 GPU/FPS는 미측정.

## 직전 개발 기준 — 소브레멘니 WIP SOV_A (당시 기록)

- [실행 HTML](archive/v48/WIP_SOV_A/Aegis_SIM_v48_WIP_SOV_A.html), [상태](archive/v48/WIP_SOV_A/AEGIS_PLAN_STATUS_v48_WIP_SOV_A.md), [SHA](archive/v48/WIP_SOV_A/SHA256SUMS_v48_WIP_SOV_A.txt), [운용·출처](docs/sovremenny/A/README.md), [검증](docs/sovremenny/A/evidence/verification-summary.json). HELI_F2 `570e5a3` 위 `sovremenny-hull-a`.
- Project 956은 적·중립 NPC 전용이며 FLEET NAV만 가능하다. 센서/무장/전자전/Ka-27/자함 선택은 없다. 원본 수선 Z0·7,940t·32kt와 오프라인 단면/외피/비활성 장착점, 공통 물리·손상·침수·저장·3D·ISAR를 연결했다.
- 157/157 PASS /6 suites, 페이지 오류0. 30km 실제 헬기 LONG/PERI→Hawklink→EMCON 하푼 명중, 통제된 격리 상실→LOST, 손상 중 저장/거부 원자성, 모바일 UI/소프트웨어 WebGL,1/8/16/64× 및 기존 양함종 회귀를 확인했다.
- 원본 17998448bytes / SHA `1e2125e49ae0720d45f2457474753ed948324241aecf69120f5c7694ea733b28`. 실제49k 삼각형·81배치, 실폰 FPS 미측정. 내부·재질·RCS·CG/GM·응답은 SIM_TUNED다.
- HELI_F2 네 파일을 같은 bytes/blob으로 archive하며 기존 소스/자산/stable을 보존한다. 전체 HTML 직접 업로드·독립 원격 readback. Actions dispatch/main·이전 브랜치 병합/새 PR 없음.

## 직전 개발 기준 — 헬기 WIP HELI_F2 (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_F2/Aegis_SIM_v48_WIP_HELI_F2.html), [상태](archive/v48/WIP_HELI_F2/AEGIS_PLAN_STATUS_v48_WIP_HELI_F2.md), [SHA](archive/v48/WIP_HELI_F2/SHA256SUMS_v48_WIP_HELI_F2.txt), [운용](docs/helicopter/L/README.md), [검증](docs/helicopter/L/evidence/verification-summary.json). 별도0번 `1b26a0f` 뒤 `helicopter-isar-f2`.
- AIR ISAR→지도 트랙: 공통 RF 물리→잡음 특징→함급 후보. 고정 방위16초, 탐색/M-of-N 정지, 종료/취소 후 직전 모드·한 주사 전환. 실제 표적 ID/프로파일로 분류하지 않는다.
- ISAR 판독만 버퍼 예외. 수신은 식별/트랙 나이를 바꾸지 않고 운용자 식별 때 근거를 복사한다. 로그 ISAR 후보/신뢰도/경과시간·launchEmcon, 종료 AFTER_ACTION_TRUTH. 기존 F1·무DL·EMCON 통신 독립·함선/헬기 모델 보존.
- 실제 CG LONG40km→ISAR→HOSTILE→무방사 지정→하푼→중립 상선 피격, 실제 DDG/CG RF, 모바일/3D/배율/기존 전투 포함227/227 PASS /8 suites, 오류0. 진단은 SIM_TUNED이며 실제 장비 성능 아님.
- 원본16,099,946bytes,0번 대비18,178bytes 증가.0번 네 파일과 A–K/stable 보존·직접 업로드·독립 readback. Actions dispatch/main·이전 브랜치 병합/새 PR 없음.

## 직전 개발 기준 — 헬기 WIP HELI_F2_0 (0번 단독 당시 기록)

- [0번 단독 실행 HTML](archive/v48/WIP_HELI_F2_0/Aegis_SIM_v48_WIP_HELI_F2_0.html), [상태](archive/v48/WIP_HELI_F2_0/AEGIS_PLAN_STATUS_v48_WIP_HELI_F2_0.md), [SHA](archive/v48/WIP_HELI_F2_0/SHA256SUMS_v48_WIP_HELI_F2_0.txt), [운용](docs/helicopter/K/README.md), [검증](docs/helicopter/K/evidence/verification-summary.json). CG_B `273c36f` 위 `helicopter-emcon-f2-0`.
- EMCON 중 ARM LOCK은 표시 트랙을 지정하고 SPY mode=TWS/pdTracking=false를 유지한다. ON은 PD만 종료·지정 유지, OFF는 기존 SPY 섹터 안이면 PD. MODE/진단/network 전환에서도 같다.
- 하푼 UI를 지정 직후 갱신하고 기존 F1 관문/무DL·Hawklink 독립·VLS/3D AUTO/AUTO TGT/SPG/AUTO 차단을 유지한다. 로그 launchEmcon은 실제 커밋 시점의 함 상태다.
- 실제 CG 헬기→Hawklink→ARM 지정→SPY 물리 방사원/빔 작업0→하푼→launchEmcon=true, 모바일/데스크톱 및 기존 전투 포함124/124 PASS /4 suites, 오류0.
- 원본16,081,768bytes, CG_B 대비1,788bytes 증가. 기존 파일/과거 소스 보존·직접 업로드·독립 readback. **0번 별도 보고 뒤 ISAR1번 이후 진행**이며 이 HTML에는 ISAR가 없다. Actions dispatch/main·이전 브랜치 병합/새 PR 없음.

## 직전 개발 기준 — 헬기 WIP HELI_CG_B (당시 기록)

- [수정 실행 HTML](archive/v48/WIP_HELI_CG_B/Aegis_SIM_v48_WIP_HELI_CG_B.html), [상태](archive/v48/WIP_HELI_CG_B/AEGIS_PLAN_STATUS_v48_WIP_HELI_CG_B.md), [SHA](archive/v48/WIP_HELI_CG_B/SHA256SUMS_v48_WIP_HELI_CG_B.txt), [운용](docs/helicopter/J/README.md), [검증](docs/helicopter/J/evidence/verification-summary.json). HELI_CG_A `3ce88eb` 위 `helicopter-cg-b`.
- **A의 후벽 전체 개구·상부 접힘 문은 형상 판단 오류였다.** B는 원본 좌현 문/해치/창1456삼각형을 측방 이동하고 우현 벽·세로 패널·상부 창/플랫폼·관제 구조물을 복원·보존한다. 원본 모델 치수/문 이동량·내부는 SIM_TUNED다.
- 두 기는 나란히 격납하고 좁은 좌현 출구를 공유한다. H2 단독 요청은 H1 통로 이탈까지 대기하며, H1을 무단 출격시키지 않는다. 기존120초/한 패드/DDG 두 문·출격/비행·센서·Hawklink·IFF·OTH 정책은 유지한다.
- CG J1 저장: 유효 I1만 migration, 공중 기체 보존/주문된 지상 기체 재대기. DDG E1 유지. 닫힌 후방75ray 원본 일치/열림 중 우현 보존/202포즈 무간섭/실제 OTH 포함227/227 PASS /8 suites, 오류0.
- 원본16,079,980bytes, A 대비1,644bytes 증가. A 네 파일과 과거 A–I/stable 보존, 전체 원본 직접 업로드·독립 readback. Actions dispatch/main·기존 브랜치 병합/새 PR 없음.

## 직전 개발 기준 — 헬기 WIP HELI_CG_A (형상 교정 전 기록)

- [실행 HTML](archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html), [상태](archive/v48/WIP_HELI_CG_A/AEGIS_PLAN_STATUS_v48_WIP_HELI_CG_A.md), [SHA](archive/v48/WIP_HELI_CG_A/SHA256SUMS_v48_WIP_HELI_CG_A.txt), [운용·재현](docs/helicopter/I/README.md), [검증](docs/helicopter/I/evidence/verification-summary.json). HELI_F1 `bd0e88a` 위 `helicopter-cg-a`.
- CG: **하나의 공용 격납고·단일 출입구·두 주기 위치**. DDG: 기존 좌우 독립 문/출격 경로 보존. 시설 프로파일과 기체 slot/door index를 분리하고120초 준비/하나의 공용 패드를 같은 시스템으로 운용한다. CG 문 기구·내부 치수는 SIM_TUNED다.
- CG 기존 겹친 후벽·개구 부속을 제거하고 절차적 내부/상부 접힘 문을 추가했다. 원본 모델/텍스처는 재사용하며 새 시각 내부를 피해·침수 구획 재저작으로 취급하지 않는다.
- DDG E1 저장 유지/CG I1 단일 문 저장, 이전 CG 빈 재고는 두 격납 기체로만 migration. 기존 SI/fixed60Hz/read-only 렌더/IFF·Hawklink·F1 OTH 권한/무DL 정책 유지.
- 206/206 PASS /8 suites, 오류0. 양쪽 출격 순서/202포즈 무간섭/실제 CG 헬기→APS→Hawklink→순수OFFBOARD 수동 하푼 발사/DDG 및 전투 회귀를 확인했다. 원본16,078,336bytes, F1 대비2,614bytes 증가.
- 전체 원본 직접 업로드·독립 readback, F1 네 파일 동일 bytes/blob archive. stable/과거 A–H 보존. Actions dispatch/main·이전 브랜치 병합/새 PR 없음. 착함/연료/타함 항공 AI/헬기 무장 등은 후속.

## 직전 개발 기준 — 헬기 WIP HELI_F1 (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_F1/Aegis_SIM_v48_WIP_HELI_F1.html), [상태](archive/v48/WIP_HELI_F1/AEGIS_PLAN_STATUS_v48_WIP_HELI_F1.md), [SHA](archive/v48/WIP_HELI_F1/SHA256SUMS_v48_WIP_HELI_F1.txt), [운용·재현](docs/helicopter/H/README.md), [검증](docs/helicopter/H/evidence/verification-summary.json). HELI_E1 `69a5e38` 위 `helicopter-harpoon-f1`.
- 순수 offboard 수동 하푼을 트랙 품질·10초·2σ 바스켓으로 판단한다. active/foreign native·자동 발사관·FLEET wrapper에 일관 적용하며 기존 식별/수동 권한·AI local 조건·사거리·손상·좌표/경로를 보존한다.
- 식별 근거 LOCAL_SENSOR/OPERATOR_ONLY/ISAR 예약과 DEBUG 교전 로그64건. 실제 종료 대상 범주는 AFTER_ACTION_TRUTH 사후 기록만 사용하며 전술·센서·AI는 읽지 않는다. 발사 뒤 DL/업데이트 없음.
- 사용자 결정에 따라 CG-52 헬기는 다음 단계다. 현재 DDG 헬기/CG 하푼 분리는 유지한다. 실제 APS 보고를 CG 수신기에 진단 재생했으며 플레이 전단 공유를 추가한 것은 아니다.
- 원본16,075,722bytes, E1 대비1,500bytes 증가. 209/209 PASS /7 suites, 오류0. 전체 원본 직접 업로드·독립 readback, E1 네 파일 동일 bytes/blob archive. stable/과거 소스·자산 보존, Actions dispatch/main·이전 브랜치 병합/새 PR 없음.

## 직전 개발 기준 — 헬기 WIP HELI_E1 (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_E1/Aegis_SIM_v48_WIP_HELI_E1.html), [상태](archive/v48/WIP_HELI_E1/AEGIS_PLAN_STATUS_v48_WIP_HELI_E1.md), [SHA](archive/v48/WIP_HELI_E1/SHA256SUMS_v48_WIP_HELI_E1.txt), [계산·재현](docs/helicopter/G/README.md), [수정 전후 표](docs/helicopter/G/evidence/final/comparison/performance-comparison.md), [검증](docs/helicopter/G/evidence/verification-summary.json). HELI_E ff3eceb 위 `helicopter-radar-e1`이다.
- 빔 체류 내 PRF×체류시간 펄스 수와 주파수 민첩성의 부분 상관 이득을 클러터에만 적용한다. 신호·열잡음 추가 배율 없이 PERI 앵커를 다시 맞춘다. 주사 간 이진 M-of-N은 그대로다. 모두 SIM_TUNED다.
- SHORT 소형152m·SS3의12.5km, LONG 소형25m·잔잔3km 이하, LONG 중형3000m·Hs3m의50km, PERI35km를 함께 맞췄다. 계기거리 limiter와 전체288조건 전후 표를 제공한다.
- 원본16,074,222bytes, E 대비2,277bytes 증가. 최종152/152 PASS /6 suites. 실제 RF·펄스 이득 무중복·오경보·배속·기존 양함종 전투를 확인했다. 구체적인 수치와 한계는 상태/증거를 따른다.
- 전체 원본 직접 업로드/독립 readback, E 네 파일 동일 bytes/blob archive, stable/이전 소스·자산 보존. Actions dispatch/main·이전 브랜치 병합/새 PR 생성은 하지 않는다.

## 직전 개발 기준 — 헬기 WIP HELI_E (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_E/Aegis_SIM_v48_WIP_HELI_E.html), [상태](archive/v48/WIP_HELI_E/AEGIS_PLAN_STATUS_v48_WIP_HELI_E.md), [SHA](archive/v48/WIP_HELI_E/SHA256SUMS_v48_WIP_HELI_E.txt), [조작·계산·재현](docs/helicopter/F/README.md), [검증](docs/helicopter/F/evidence/verification-summary.json). HELI_D e64f7af 위 `helicopter-radar-e`다.
- 단일 주사 검출 → PERI4-of-9 / LONG·SHORT2-of-3을 적용했다. 모드·빔·해면·CFAR·병합·익명 공분산·200접촉·Hawklink queue 보호와 E1 migration을 사용한다. 수치는 모두 SIM_TUNED이며 analog/reference를 구분한다.
- AIR 모드, 지도 별도 링, 3D AN/APS-153 쐐기·잔상·직하 사각, DEBUG 성능표를 제공한다. 기존 비행·고도·경로·CAMERA·IFF·EMCON 독립·무장 권한을 유지한다.
- 원본16,071,945bytes, D 대비12,992bytes 증가. 최종355/355 PASS /9 suites, 양함종 전투와1/8/16/64× 일치. 앵커와 오경보 결과·시험 범위·한계는 상태와 증거를 따른다.
- 원본 전체 직접 업로드와 독립 GitHub readback, D 네 파일의 동일 bytes/blob archive, stable/과거 소스·자산 보존. Actions dispatch/main·이전 브랜치 병합/새 PR 생성은 하지 않는다. 다음은 OTH 표적지시·공유 정책의 별도 결정이다.

## 직전 개발 기준 — 헬기 WIP HELI_D (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_D/Aegis_SIM_v48_WIP_HELI_D.html), [상태](archive/v48/WIP_HELI_D/AEGIS_PLAN_STATUS_v48_WIP_HELI_D.md), [SHA](archive/v48/WIP_HELI_D/SHA256SUMS_v48_WIP_HELI_D.txt), [조작·계약·재현](docs/helicopter/E/README.md), [최종 검증](docs/helicopter/E/evidence/verification-summary.json). HELI_C final 위 `helicopter-sensors`다.
- 비행 헬기의 실제 RF 반사와 잡음 기반 IFF를 연결했다. IFF ON 기본값, 만료되는 아군 증거와 운용자 식별을 분리하고 실제 AUTO 요격 판단에서 확인한다. 실제 헬기 피격·격추는 후속이다.
- 헬기 수상 탐색 레이더는 기본 OFF다. 공통 RF/SNR·해면·기상과 회전당 탐지 1회, 잡음 측정·SI 공분산을 사용한다. APS-153급 밴드·출력·거리는 전부 SIM_TUNED 가정이다.
- Hawklink H1/H2는 원래 모함에 익명 plot만 지연 전송한다. **레이더 EMCON과 독립**이며 LOS/최대 거리/모함 장비로 연결을 결정한다. 단절 시 대기 보고도 버리고 재전송하지 않는다. 통신 EMCON은 두 링크를 함께 다룰 후속 정책이다.
- AIR의 IFF/레이더·링크 상태, 선택 기체의 지도 수평선, 3D SENSORS의 HELO RADAR 표시를 추가했다. 기존 출격/경로/고도/CAMERA를 유지한다. 원격 관측만으로 무장을 발사하지 않으며 하푼 좌표 검색은 유지한다.
- A→B→C 각 게이트를 별도 커밋으로 고정했다. 최종 동일 HTML의 검사 수·크기·SHA와 조건은 상태/검증을 따른다. 공통 헬기 자산을 재사용하며 이전 C 네 파일은 같은 bytes/blob으로 archive한다. Actions는 실행하지 않는다.

## 직전 개발 기준 — 헬기 WIP HELI_C (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html), [상태](archive/v48/WIP_HELI_C/AEGIS_PLAN_STATUS_v48_WIP_HELI_C.md), [SHA](archive/v48/WIP_HELI_C/SHA256SUMS_v48_WIP_HELI_C.txt), [조작·재현](docs/helicopter/D/README.md), [최종 검증](docs/helicopter/D/evidence/verification-summary.json). HELI_B final 위 `helicopter-c`다.
- 실제 출구 구조물/갑판 경사에 따른 기수 간섭과 겹친 꼬리 바퀴를 수정했다. 공통 모델을 재사용한다.
- AIR 높이를 줄이고 출격/대기 취소를 같은 버튼으로 통합한다. AIR 헬기 보기/모함 보기만 삭제하며 **3D CAMERA H1/H2 추적은 유지**한다.
- 기체별 목표 고도25–3,962.4m를 대표값/직접 입력으로 설정한다. 미 해군의 MH-60R ceiling13,000ft [공개 근거](docs/helicopter/D/altitude-spec.md)를 사용한다. 기본50m/운용 상하3.5m/s, fixed60Hz/read-only와 센서 격리 유지. 경로·호버·함선 따라가기 중에도 고도를 바꾼다.
- **16,041,537bytes**, SHA `65c1f2ec7deb4bc4740a0477754edd210a6c09bacbefad41e93a3ae9675e6ff6`, **248/248 PASS /6 suites**. B 대비3,916bytes 증가. Actions는 dispatch하지 않는다. B 네 파일은 같은 bytes/blob으로 archive하고 stable/자산/이전 source·evidence를 유지한다.

## 직전 개발 기준 — 헬기 WIP HELI_B (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_B/Aegis_SIM_v48_WIP_HELI_B.html), **16,037,621bytes**, SHA `e4da7d69b3a4fb70583b336f5659a9f4956b63ed85bcf4fbf9e763ebf30017c3`. A final 위 `helicopter-b`. [상태](archive/v48/WIP_HELI_B/AEGIS_PLAN_STATUS_v48_WIP_HELI_B.md), [SHA](archive/v48/WIP_HELI_B/SHA256SUMS_v48_WIP_HELI_B.txt), [조작·재현](docs/helicopter/C/README.md), [검증](docs/helicopter/C/evidence/verification-summary.json).
- 메인/꼬리 실제 축·회전 주체를 수정하고 고정 gearbox/지지부를 분리했다. 문 뒤 HULL 벽 제거, 양쪽 외측 배치·문 정렬·벽 밖 곡선 턴, 정지 지점3.7m 뒤로 이동.
- AIR는 왼쪽 조작/오른쪽 여백·스크롤 목록. 여러 경로점/UNDO/급한 코너 감속·선회/함선 뒤·측방 약410m 따라가기. 3D CAMERA에 H1/H2 추적을 추가했다. 준비120초와50m MSL, fixed60Hz/read-only 및 센서 격리를 유지한다.
- **264/264 PASS /11 suites**, native 양쪽 portal/rigidity/고정 gearbox, 독립 source401pose 간섭, 실제 A 저장 migration,1/8/16/64배속, 기존 DDG/CG 전투·피격 비교 포함. software GPU/viewport 조건은 보고서를 따른다. Actions는 dispatch하지 않았다.
- 원본 자산 재사용으로 HTML은 A 대비 **1,828bytes(+0.0114%)** 증가. A 네 파일 same bytes/blob archive, stable/asset/과거 증거 유지. 다음 센서/IFF 단계는 이번에 연결하지 않았다.

## 직전 개발 기준 — 헬기 WIP HELI_A (당시 기록)

- [실행 HTML](archive/v48/WIP_HELI_A/Aegis_SIM_v48_WIP_HELI_A.html), **16,035,793bytes**, SHA `35dbbb64f3067768494c9c6b08d3dc7f02d53cc223f80f4fc7f4970dcb871477`. PERF_F + SH-60 asset A 위 `helicopter-a` 작업이다. [상태](archive/v48/WIP_HELI_A/AEGIS_PLAN_STATUS_v48_WIP_HELI_A.md), [SHA](archive/v48/WIP_HELI_A/SHA256SUMS_v48_WIP_HELI_A.txt), [조작·계약·재현](docs/helicopter/B/README.md), [검증](docs/helicopter/B/evidence/verification-summary.json).
- 자함 DDG-119의 두 기를 AIR에서 선택·위치 지정·출격/대기열 취소한다. 문 개방 → 갑판 이동 → 꼬리/로터 전개 → 45초 시동 → 안정화 → 부상까지 120초. 첫 기체가 실제 갑판을 비운 뒤 두 번째가 준비한다. 좌현 이탈 뒤 50m MSL로 비행·목표 호버한다.
- MH-60R 제원 제한 질점 + 상태기계, SI/고정60Hz. 바람·대기속도·선회율·가감속·정지/오버슈트·재지향과 읽기 전용 자세/3D를 적용했다. 레이더/관측 포트·IFF·무장·연료·로터 공력·회수·고도 UI는 이번 단계에서 제외했다.
- 공통 압축 모델 223,419bytes를 한 번 내장, 두 기 geometry/material 공유와 LOD. HTML 증가 **326,494bytes (+2.07835%)**. 원본 SH-60 외형을 MH-60R 상세 외장 검증으로 표현하지 않는다.
- 최종 검증과 실행 조건은 상태/증거를 따른다. 기존 F 전투 회귀와 native 3D를 로컬에서 확인하며 수동 Actions를 dispatch하지 않는다. main/선행 브랜치를 자동 병합하지 않는다.
- PERF_F 네 파일은 같은 bytes/blob으로 [archive](archive/v48/WIP_PERF_F/)에 보존한다. stable v48, asset A와 과거 evidence는 유지한다. 다음은 항공 센서/IFF/초수평선 관측 단계다.

## 헬기 모델 검사 — v01 (당시 asset 기록)

사용자 DDG-118 GLB에서 SH-60의 공통 기체와 격납·전개·비행 정적 부품을 추출했다. [독립 미리보기](docs/helicopter/A/AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html), [lossless GLB](docs/helicopter/A/seahawk-poses-lossless.glb), [상태](docs/helicopter/A/AEGIS_HELICOPTER_MODEL_STATUS_v01.md), [구성·검증·재현](docs/helicopter/A/README.md), [SHA](docs/helicopter/A/SHA256SUMS.txt). 게임용 압축 223,419bytes, 기존 Three 재사용 시 HTML 추가량 301,239bytes (+1.9176%). 구조/native 비교·회수/최종 scene·UI 51검사와 정적 문법 PASS. 당시 별도 helicopter-model-a에서 게임 PERF_F를 보존한 자산 검사 기록이다. 해당 자산을 현재 HELI_A에서 재사용한다.

## 직전 개발 기준 — 최적화 WIP PERF_F (당시 기록)

- 현재 [HTML](archive/v48/WIP_PERF_F/Aegis_SIM_v48_WIP_PERF_F.html), 15,709,299bytes, SHA `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5`, main `e9eb7d600d01e6d271b4dcf99e98b5e65dd09bbfe58f0ef29955affc343b398c`. PERF_E final `bd8962011a16cfeb4158670d3e562a92e0a52ff4` 위 performance-f. 현재 support/workflow/checksum은 F, 이전 문장은 당시 기록이다.
- complete anchor 공개 이후에만 remaining quick work를 최신 피격으로 선점한다. unpublished opening은 보호하고 live/original buffers를 유지한다. 안정된 입력의 최종 형상·현재6ms budget·physics/피해/sensors/AI/RNG/fixed60/120/20Hz/actual release와 이전 캐시/모델/연기 결과는 보존한다. packed13 표시용 scheduler와 texture disposal만 수정한다.
- 최종 원본 1817/1817PASS/38suites, 오류0. [상태](archive/v48/WIP_PERF_F/AEGIS_PLAN_STATUS_v48_WIP_PERF_F.md), [SHA](archive/v48/WIP_PERF_F/SHA256SUMS_v48_WIP_PERF_F.txt), [계약](docs/performance/F/README.md), [성능/한계](docs/performance/F/PERFORMANCE.md), [검증](docs/performance/F/evidence/verification-summary.json).
- 기존 전체 회귀와 연속3회 cut/queue, 양함종 각각120simulated seconds/7200ticks의 세 함정 overload exact state/RNG,8회nativeGPU smoke/Kh32 epoch와pending-cut 외부 함정owner replacement/disposal 검증. 전체 회귀/카메라 종료 후 native second-hit submit4쌍 직렬 AB/BA. 제어된 detached scar/diagnostic tracks이며 자연 다발 피격·실제 수시간 soak·hardware/phone FPS는 미실행이다. 누적CPU는 E 당시기록을 참조하며 새 F측정으로 표현하지 않는다.
- E 네 파일 samebytes/blob archive, stable와 이전 증거 유지. §7.1 full original 직접 upload/독립 remote readback. Actions dispatch/main·선행 branch merge/새 PR 없음.
- 계획한 최종 최적화 검증 범위 완료. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.

## 직전 개발 기준 — 최적화 WIP PERF_E (당시 기록)

- [HTML](archive/v48/WIP_PERF_E/Aegis_SIM_v48_WIP_PERF_E.html), **15,709,083bytes**, SHA `0b59340c2db16d33a6fefe810d8bbf27f96ff189ad8a8166139578b50f2051b5`.
- 완성된 양측 anchor 구멍·변형을 먼저 공개한다. 주변 최종 메쉬와 수명/원본을 보존한다. 일곱 smoke attributes의 exact GPU dirty ranges만 전송하고 split/bound 임시 계산을 줄였다. packed13만 변경, 모델/물리/센서/AI/피해/RNG/고정 주기/발사 gate 유지.
- 최종 원본 **1735/1735PASS/35suites**, 오류0. [상태](archive/v48/WIP_PERF_E/AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md), [SHA](archive/v48/WIP_PERF_E/SHA256SUMS_v48_WIP_PERF_E.txt), [계약](docs/performance/E/README.md), [누적·3D 성능](docs/performance/E/PERFORMANCE.md), [검증](docs/performance/E/evidence/verification-summary.json).
- H4A→E 누적 CPU를 직접 같은 실행에서 측정한다. 단계별 개선율을 더하지 않는다. D→E native 피격·RAF/driver 전송은 별도이며 host/software WebGL 결과를 hardware/phone FPS로 표현하지 않는다.
- performance-e full original upload/readback, Actions dispatch/main·선행 branch 병합/새PR 없음. 다음은 다수 동시 피격·장시간 과부하/자원 회수 최종 점검 → 헬기/초수평선 → RGM-109E Block Va다.

## 직전 개발 기준 — 최적화 WIP PERF_D (당시 기록)

- [HTML](archive/v48/WIP_PERF_D/Aegis_SIM_v48_WIP_PERF_D.html), **15,707,799bytes**, SHA `bd3bc97089cd0085c1990b5460fd4b8d6f5c9bcf794e1f520a42bc9c2aa95c2e`.
- 피격 메쉬의 완성된 구멍·변형을 먼저 표시하고, 기존 frame 작업 예산의 남은 부분을 사용한다. 두 함종의 단면·변형 경계 계산 할당 비용도 줄였다. 최종 메쉬/물리 피해·RNG·주기·release guard는 유지한다.
- 최종 원본 **1660/1660PASS/33suites**, 오류0. [상태](archive/v48/WIP_PERF_D/AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md), [SHA](archive/v48/WIP_PERF_D/SHA256SUMS_v48_WIP_PERF_D.txt), [계약](docs/performance/D/README.md), [조건/성능](docs/performance/D/PERFORMANCE.md), [검증](docs/performance/D/evidence/verification-summary.json).
- performance-d full original upload/readback. Actions dispatch/main·선행 branch 병합/새PR 생성 없음. 다음은 실제3D/효과 부하와 최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

## 직전 개발 기준 — 최적화 WIP PERF_C (당시 기록)

- [HTML](archive/v48/WIP_PERF_C/Aegis_SIM_v48_WIP_PERF_C.html), **15,707,171bytes**, SHA `5f8fb9ed69a960c4eef4c15ab22271c82c9b59a095a9ec8a959689ecba9acffd`.
- SPY NIS 연관의 exact 트랙 상태/공분산/센서 원점 계산 재사용. 측정 innovation·native EKF 갱신·배정/게이트·발사권한·RNG/물리/피해는 유지한다.
- 최종 원본 **1603/1603PASS /31suites**, 오류0. NIS231사례·CG/DDG6조건과 직렬16쌍 상태/RNG exact. [성능·조건](docs/performance/C/PERFORMANCE.md), [상태](archive/v48/WIP_PERF_C/AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md), [SHA](archive/v48/WIP_PERF_C/SHA256SUMS_v48_WIP_PERF_C.txt), [계약](docs/performance/C/README.md), [직접 검증](docs/performance/C/evidence/verification-summary.json).
- PERF_B final 위 `performance-c`, full original 직접 upload·독립 readback. Actions dispatch/main·선행PR 병합·새PR 생성 없음. 다음은 피격 envelope → 실제 render·최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

## 직전 개발 기준 — 최적화 WIP PERF_B (당시 기록)

- [HTML](archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html), **15,706,015bytes**, SHA `292622e556192d3c954917437709a0f1e4489e1636cd6263a4b7737832013faf`.
- 교전 판단 내 관측 예측/SPG 기하 공유와 exact owner 자세의 body frame 재사용. 실제 예약·발사 재검사와 기존 물리/센서/AI/RNG/피해를 유지한다.
- 최종 원본 **1534/1534PASS /30suites**, 오류0. strict CG/DDG6조건과 직렬16쌍 상태/RNG exact. [성능·조건](docs/performance/B/PERFORMANCE.md), [상태](archive/v48/WIP_PERF_B/AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md), [SHA](archive/v48/WIP_PERF_B/SHA256SUMS_v48_WIP_PERF_B.txt), [계약](docs/performance/B/README.md), [직접 검증](docs/performance/B/evidence/verification-summary.json).
- PERF_A final 위 `performance-b`, full original 직접 upload·독립 readback. Actions dispatch/병합/새PR 생성 없음. 다음은 SPY 관측 연관 최적화, 이후 피격/3D·최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

## 직전 개발 기준 — 최적화 WIP PERF_A (당시 기록)

- [HTML](archive/v48/WIP_PERF_A/Aegis_SIM_v48_WIP_PERF_A.html), **15,704,207 bytes**, SHA `13a9de64d918efd053ead648cb312a691688691ccbfa72fe50fefd72054ae6ad`.
- 불변 부품 색인·EW 지원 대역 조기 검사·Kh-32 동일 도색 공유. **64모델에 canvas/texture1개**, 원래 도색 픽셀과 geometry를 보존하고 부분/최종 제거·도감·import/reset 수명을 검증했다.
- 기존 fixed60/120/20Hz·센서·AI·무장·피해·Harpoon DL0를 유지한다. strict6 ownship조건과 직렬CPU16쌍에서 상태/RNG exact. [성능 조건/관측](docs/performance/A/PERFORMANCE.md).
- 최종 원본 **1483/1483PASS /29suites**, 오류0. [상태](archive/v48/WIP_PERF_A/AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md), [SHA](archive/v48/WIP_PERF_A/SHA256SUMS_v48_WIP_PERF_A.txt), [운용](docs/performance/A/README.md), [직접 검증](docs/performance/A/evidence/verification-summary.json).
- H4A final 위 `performance-a`, 원본 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. 다음은 교전 planner/SPG 중복 계산 최적화이며 헬기/초수평선 → RGM-109E Block Va는 최적화 뒤다. main/선행PR 병합·새PR 생성은 실행하지 않는다.

## 직전 개발 기준 — Multi Ship WIP H4A (당시 기록)

- [HTML](archive/v48/WIP_MULTI_SHIP_H4A/Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html), **15,702,263 bytes**, SHA `3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a`.
- CMS 미획득에도 **CIWS 자체 RF의 확인된 접근 위협**으로 독립 자위 대응한다. 실제 발사에서 owner-local capability·freshness·아군/중립/효과 보호·HOLD/EMCON/손상을 재검사한다. CMS 적성/원거리 SAM 권한을 만들지 않는다.
- 유일하게 연관된 **local RF 거리·접근 + passive 시커 방위**를 기존 채프 timing에 전달한다. ESM 방위만으로 거리를 추측하지 않는다. 기본 fresh CG 하푼 공격에서 채프4/Phalanx95발·실제 분해를 확인했다.
- 최종 원본 **1484/1484 PASS /27 suites**, 오류0. [상태](archive/v48/WIP_MULTI_SHIP_H4A/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4A.md), [SHA](archive/v48/WIP_MULTI_SHIP_H4A/SHA256SUMS_v48_WIP_MULTI_SHIP_H4A.txt), [운용](docs/multiship/H4A/README.md), [직접 검증](docs/multiship/H4A/evidence/verification-summary.json), [조건](docs/multiship/H4A/PERFORMANCE.md).
- H4 final 위 `multiship-defense-h4a`, PR base H4. 원본/support 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. 새 main/선행 PR 병합은 실행하지 않는다. 다음은 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va다.

## 직전 개발 기준 — Multi Ship WIP H4 (당시 기록)

- [HTML](archive/v48/WIP_MULTI_SHIP_H4/Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html), **15,697,218 bytes**, SHA `602371dfd5be5147c2e04dd4078e3216ca4f47e8ce4e7b0092bd861c3d9a5132`.
- FLEET의 **함대 전술·호위/수상전 임무·종렬/좌우 전형·1/2/4km 간격**을 owner별로 설정한다. 기본OFF이며 아군은 받은 선도함 항법과 기존 H2 타/기관 명령으로 기동한다. 수동/대공 방어가 우선하고 단절/OFF에 항법을 반환한다.
- fresh 현지 적성 수상 관측과 **각 함정의 별도 H3 동의** 아래 한 primary에 native Harpoon2발을 분담한다. 받은 접수는 동의/lease 만료 뒤에도 기억해 추가 AI 살보를 보류한다. 공유OFF는 항법만, 링크 없는 상황의 보편적 중복 방지는 아니다.
- **수상 자위 판단**은 반복된 현지 incoming ASM와 유일한 near-origin 수상 관측의 근거를 사용한다. operator 식별을 덮어쓰지 않고 아군/중립 보호가 우선한다. 발사원 근거 없는 미식별 첫 공격은 보류한다. Harpoon DL0/INS→ARH, 기존 물리·무장·EW·해상효과/3D를 유지한다.
- strict 설정 저장·H3 이하 팀OFF migration·transient reset, 최종 원본 **1403/1403 PASS /24 suites**, 오류0. [상태](archive/v48/WIP_MULTI_SHIP_H4/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4.md), [SHA](archive/v48/WIP_MULTI_SHIP_H4/SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt), [운용](docs/multiship/H4/README.md), [직접 검증](docs/multiship/H4/evidence/verification-summary.json), [조건](docs/multiship/H4/PERFORMANCE.md), [남은2단계](docs/multiship/H4/DEPENDENCIES.md).
- H3 `af1eade2d418b215720a68a5b902aae0d9387203` 위 `multiship-tactical-h4`, PR base H3. 원본/support 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. main/선행 PR 병합은 실행하지 않는다. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.

## 직전 개발 기준 — Multi Ship WIP H3 (당시 기록)

- [HTML](archive/v48/WIP_MULTI_SHIP_H3/Aegis_SIM_v48_WIP_MULTI_SHIP_H3.html), **15,683,482 bytes**, SHA `0a9626535c209d8ad4e5a9b5262bd826d8ede8df928562534ba6c44b5673d178`.
- owner별 **대수상 공격 AI**: fresh 현지 HOSTILE 수상 관측·별도1/2발 공격 동의(120초)·발사대/사거리/예측 오차·chart/아군 보호를 거쳐 기존 native 하푼을 발사한다. 자함/아군함 기본OFF이며 전술 AI ON + AUTO와 동의가 필요하다. FLEET에서 공격량/동의/철회를 조작한다.
- 개방 중 OFF/철회/관제 인계·식별/alias/관측 소실/손상/보호 변경은 actual release를 막는다. 수동 하푼/waypoint 우선, 예비2발, native 자동 고정 튜브 선택/INS→ARH/DL0와 기존 H1/H2/G 물리·방어·기동·3D/해상효과를 유지한다.
- 적함도 자기 현지 HOSTILE 파일에만 mission 살보를 실행한다. IFF 무응답을 적성으로 간주하지 않아 UNKNOWN 첫 공격은 보류한다. 공유/ESM-only는 공격 권한이나 현지 FCS가 아니다. AI는 비행 위치/명중 truth를 알지 못한다.
- strict settings-only 저장, H2/H1/G/F/B/no-fleet 명시 OFF migration, 동의/계획/capability reset. 최종 원본 직접 **1198/1198 PASS**, page/core/runtime/presentation 오류0. [상태](archive/v48/WIP_MULTI_SHIP_H3/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H3.md), [SHA](archive/v48/WIP_MULTI_SHIP_H3/SHA256SUMS_v48_WIP_MULTI_SHIP_H3.txt), [운용](docs/multiship/H3/README.md), [직접 검증](docs/multiship/H3/evidence/verification-summary.json), [조건](docs/multiship/H3/PERFORMANCE.md), [남은3단계](docs/multiship/H3/DEPENDENCIES.md).
- H2 `59fad37cc170c760c1659b916febc168021a31b4` 위 `multiship-tactical-h3`, PR base H2. 원본 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. main/선행 PR 병합은 실행하지 않는다.

## 직전 개발 기준 — Multi Ship WIP H2

- [HTML](archive/v48/WIP_MULTI_SHIP_H2/Aegis_SIM_v48_WIP_MULTI_SHIP_H2.html), **15,675,514 bytes**, SHA `522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1`.
- 관측 기반 **기동 utility AI**가 승인된 현지 위협·조종/장비 상태·기존 SPG-62/CIWS 사각으로 유지/선회/속력 후보를 비교한다. native 타/기관 명령만 쓰며 실제 선회·가감속·피해/침수 물리를 유지한다. chart 해안과 관측된 수상 교통으로 위험 후보를 제외한다.
- FLEET **기동 AI ON/OFF / 기동 AI 재개**, 자함 기본OFF·아군/적함 기본ON. 전술 AI ON + AUTO에서 실행하며 NAV/FLEET 수동 항법·지도 항로 조작이 우선한다. ON/OFF는 수동 우선권을 지우지 않는다. 기동 재개는 레이더/EW 수동 hold를 유지한다.
- 요청 항법 baseline과 strict 설정만 저장하며 판단/목표/명령 소유권은 reset/import 때 비운다. H1/G/F/B/no-fleet 저장을 명시 migration한다. 공유/ESM만으로 기동·현지 FCS·적성 식별을 생성하지 않는다. 기존 방어 gate·물리/비행·CG RAM0·고정 셀·Harpoon DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_H2/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H2.md), [SHA](archive/v48/WIP_MULTI_SHIP_H2/SHA256SUMS_v48_WIP_MULTI_SHIP_H2.txt), [운용/계약](docs/multiship/H2/README.md), [직접 검증](docs/multiship/H2/evidence/verification-summary.json), [측정 조건](docs/multiship/H2/PERFORMANCE.md), [후속 H3](docs/multiship/H2/DEPENDENCIES.md), [직접 업로드](docs/multiship/H2/GITHUB_HANDOFF.md).
- 최종 원본 직접 **883/883 PASS**, page/core/runtime/presentation 오류0. 실제 기동·수동 항법/저장·사각/해안/수상 접촉, 자연 센서→AI→요격, 세 척1/8/16/64 결정성, H1 물리/RNG, 실제 WebGL/RAF 피격·복원을 확인했다. 조건과 한계는 위 집계를 따른다.
- `multiship-tactical-h2`는 H1 head `43021f9693dc0500b5f2def531ec5d0d9e17bf0b` 위다. 원본 직접 업로드·독립 readback을 수행한다. Actions 사용 불가 조건에 따라 수동 workflow만 준비하고 로컬 검증으로 마감한다. 다음은 **H3 대수상 공격 AI**다.

## 직전 개발 기준 — Multi Ship WIP H1

- [HTML](archive/v48/WIP_MULTI_SHIP_H1/Aegis_SIM_v48_WIP_MULTI_SHIP_H1.html), **15,669,638 bytes**, SHA `e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058`.
- 함정별 **유틸리티 방어 AI**가 현지 관측의 접근 긴급도·미대응 수·가용탄·사통 채널·장비 손상을 비교한다. 기존 AUTO 실행기에 표적 우선순위와 부족한 탄약의 살보 배분을 연결하고 레이더·전자전 준비를 조절한다. 발사 권한·사각·NEZ·예비탄·BDA·G 아군 보호/담당 분담은 기존 gate를 유지한다.
- FLEET의 **전술 AI ON/OFF / AI 운용 재개**로 조작한다. 자함 기본 OFF, 아군/적함 기본 ON이며 해당 owner AUTO에서 실행한다. 수동 레이더·전자전과 공동 EMCON이 우선한다. 공유·ESM 경보는 준비에만 쓰며 현지 FCS 없이 발사하지 않는다.
- 설정만 strict detached preflight로 저장하고 판단·우선 파일·임시 radar/EW 소유권은 reset/import 때 비운다. G/F/B 저장은 명시 migration한다. 기존 owner 항법·3D·물리/비행·CG RAM0·고정 셀·Harpoon DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_H1/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H1.md), [SHA](archive/v48/WIP_MULTI_SHIP_H1/SHA256SUMS_v48_WIP_MULTI_SHIP_H1.txt), [운용/계약](docs/multiship/H1/README.md), [직접 검증](docs/multiship/H1/evidence/verification-summary.json), [측정 조건](docs/multiship/H1/PERFORMANCE.md), [후속 H2/H3](docs/multiship/H1/DEPENDENCIES.md), [직접 업로드](docs/multiship/H1/GITHUB_HANDOFF.md).
- 최종 원본 직접 **625/625 PASS**, page/core/runtime/presentation 오류0. H1-on 실제 발사, 초기 트랙 없는 자연 센서→AUTO, 수동/그룹 우선권과 손상, 세 척1/8/16/64 결정성, 기존 G 물리/RNG, 실제 WebGL/RAF 피격·복원을 확인했다. 조건과 한계는 위 집계를 따른다.
- `multiship-tactical-h1`은 G head `d902d24486918c23d43e3067be16ab03fbaedde2` 위다. 원본 직접 업로드·독립 readback을 수행한다. Actions 사용 불가 조건에 따라 수동 workflow를 준비하고 로컬 검증으로 마감한다. 다음은 **H2 기동 utility**, 이어 H3 대수상 공격이다.

## 직전 개발 기준 — Multi Ship WIP G

- [HTML](archive/v48/WIP_MULTI_SHIP_G/Aegis_SIM_v48_WIP_MULTI_SHIP_G.html), **15,664,301 bytes**, SHA `7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7`.
- 새 **FLEET** 탭에서 함정 변경으로 자함/아군함을 선택하고 속력·타각, 수동/자율 방어, 현지 표적 식별과 SAM·함포·Harpoon 발사, EMCON·링크/공유/방어 분담을 조작한다. 공동 탐색 레이더 정책은 함대에 적용한다. 각 함정의 항법·현지 track ID·탄약·센서/무장·피해 runtime은 유지한다. NAV·ARM·CIC·기존3D 교전 버튼은 원래 자함 기준이다.
- 3D 아군함 보기의 실제 pointer/touch 입력을 고쳤다. 카메라 focus/reset/retire 레이블과 FLEET의 선택 함정 3D 보기도 연결했다.
- 아군의 측정 위치·속도·공분산·관측 시각을 2Hz/.3s 지연으로 공유한다. 보수적 covariance intersection의 CIC 정정, 연결 손실 시 개별 EMCON 복귀, 현지 FCS 승인에 한정한 SAM 분담을 적용한다. 공유만으로 사통을 생성하거나 원격 발사하지 않는다.
- 하푼의 빔각·선회·짧은 재획득 때 이전 레이더 관측과 발사 기록으로 연관을 이어가고 애매하면 자동 요격을 보류한다. 위치 미관측 때 지도에 없고 **Harpoon DL=0**이다. 비행/물리 커널·CG RAM0·고정 셀·함정별 해상효과를 보존한다.
- [상태](archive/v48/WIP_MULTI_SHIP_G/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_G.md), [SHA](archive/v48/WIP_MULTI_SHIP_G/SHA256SUMS_v48_WIP_MULTI_SHIP_G.txt), [구조/운용/한계](docs/multiship/G/README.md), [검증 집계](docs/multiship/G/evidence/verification-summary.json), [측정 조건](docs/multiship/G/PERFORMANCE.md), [후속 H 전술 AI](docs/multiship/G/DEPENDENCIES.md), [직접 업로드](docs/multiship/G/GITHUB_HANDOFF.md).
- 최종 원본 직접 **897/897 PASS**, page/core/runtime/presentation 오류0. mouse/touch와 실제 RAF camera, owner별 실제 발사/보호, 세 척1/8/16/64 결정성, native3D 피격/복원과 F 물리/RNG 회귀를 확인했다. 각 tested SHA와 조건은 위 집계를 따른다.
- `multiship-network-g`는 F head `e4a1ceb6700f1d891e1c11aee0f9519b8ccde9c5` 위다. 원본 직접 업로드와 원격 readback을 수행하며 Actions 사용 불가 조건에 따라 로컬 검증으로 마감한다. 수동 workflow는 dispatch하지 않는다. main/선행 branch를 임의 병합하지 않는다.

## 직전 개발 기준 — Multi Ship WIP F

- [HTML](archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html), **15,638,513 bytes**, SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`.
- 출항 전 아군/적군을 각각 없음/DDG-119/CG-52로 선택한다. 아군은 자함 근처, 적군은10~30km 임의 해상에 배치한다. 초기 레이더 EMCON·시험 표적함·항공기 ON/OFF도 선택한다. normal3D `아군함 보기`로 적 truth 위치를 드러내지 않는다.
- 함정별 ESM·noise/replay·눌카/SRBOC를 기존 owner 무장/방어 AUTO에 연결했다. 실제 방사·대역·기하·손상·수신빔과 자기 측정으로 대응한다. CIC는 자함의 방위/오차·신호세기 및 거리 미확정만 표시한다. 초기 EMCON은 레이더 침묵이며 방어 ECM 정책과 분리한다.
- 아군·적군에도 자함과 같은 함수파·선미 포말·항적을 표시한다. 실제 속도/위치·침로와 함종 수선면을 따르며 표시용 history/mesh는 owner별로 분리·폐기한다.
- 인증 IFF 측정을 기존 수상 트랙에 연관해 FRIEND 보호한다. 아군 네트워크/정정/공동 EMCON·합동교전·기동/공격 AI는 다음 단계다. CG RAM0, 원본 물리·고정 셀·Harpoon INS→ARH/DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_F/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_F.md), [SHA](archive/v48/WIP_MULTI_SHIP_F/SHA256SUMS_v48_WIP_MULTI_SHIP_F.txt), [구조/검사/한계](docs/multiship/F/README.md), [다음 단계](docs/multiship/F/DEPENDENCIES.md), [최종 검증](docs/multiship/F/evidence/verification-summary.json), [측정 조건](docs/multiship/F/PERFORMANCE.md), [직접 원격 반영](docs/multiship/F/GITHUB_HANDOFF.md).
- 최종 원본 직접 **593/593 PASS**. 실제 Kh-35U RF/자연 관측 AUTO·시커 재밍, 세 척1/8/16/64 결정성, 실제3D 피격/복원을 확인했다. ESM RNG 분리로 E 대비 일부 raid 발사 순서/잔탄은 바뀐다. DDG EW 안테나는 별도 등록이 없어 legacy RF 기준점으로 유지한다. SIM-TUNE/SwiftShader와 상세 한계는 위 문서를 따른다.
- `multiship-ew-f`는 E head `bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6` 위다. 원본 HTML을 직접 업로드·readback한다. Actions 사용 불가라는 사용자 조건에 따라 로컬 검증으로 마감하며 새 workflow는 수동 실행용이다. main/선행 branch를 임의 병합하지 않는다.

## 직전 개발 기준 — Multi Ship WIP E

- [E HTML](archive/v48/WIP_MULTI_SHIP_E/Aegis_SIM_v48_WIP_MULTI_SHIP_E.html), 15,609,329 bytes, SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`. [E 상태](archive/v48/WIP_MULTI_SHIP_E/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md), [PR #49](https://github.com/0-FLANDRE-0/Aegis_Project/pull/49).
- 원래 AUTO/BDA·alias/지원 이관과 항공기 ON/OFF를 owner-local로 실행했다. 당시 E660건은 역사 기록이며 F 직접 수에 합산하지 않는다. E 원본 세트/workflow는 same bytes/blob으로 archive에 보존한다.

## 직전 개발 기준 — Multi Ship WIP D

- [D HTML](archive/v48/WIP_MULTI_SHIP_D/Aegis_SIM_v48_WIP_MULTI_SHIP_D.html), SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`, 15,575,097 bytes. [D 상태](archive/v48/WIP_MULTI_SHIP_D/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_D.md), [PR #48](https://github.com/0-FLANDRE-0/Aegis_Project/pull/48).
- 5A/5B의 owner 무장·양방향 실물 접촉/구획 피해·3D와 advisory shadow를 구현했다. E에서 방어 AUTO/BDA를 추가했으며 D 기록과 증거는 역사 기준으로 보존한다.

## 직전 개발 기준 — Multi Ship WIP C

- [HTML](archive/v48/WIP_MULTI_SHIP_C/Aegis_SIM_v48_WIP_MULTI_SHIP_C.html), **15,344,725 bytes**, SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`.
- 4단계: 실제 배치 함정의 SPY/해면탐색/항법 레이더와 익명 관측·추정 트랙을 함정별로 실행한다. 자함 CIC는 자함 관측만 읽으며 상대 위치·정체를 바로 주입하지 않는다. CG/DDG의 면 배치·센서 profile, 지평선·지형 차폐와 EMCON/손상·coast를 적용한다.
- 이후 헬기를 받을 오차·시각·지연·링크 단절이 있는 외부 관측 포트를 준비했다. **헬기 자체와 양방향 무장/EW/AI는 후속 단계**다. Harpoon 발사 후 DL=0, 기본 적함 없음/자함 EMCON ON, 60/120/20 Hz를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_C/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_C.md), [SHA](archive/v48/WIP_MULTI_SHIP_C/SHA256SUMS_v48_WIP_MULTI_SHIP_C.txt), [구조/포트](docs/multiship/C/README.md), [다음 단계](docs/multiship/C/DEPENDENCIES.md), [검증 집계](docs/multiship/C/evidence/verification-summary.json), [측정 조건](docs/multiship/C/PERFORMANCE.md), [GitHub 인계](docs/multiship/C/GITHUB_HANDOFF.md).
- `multiship-sensors-c`는 B head `ae94326caea7cd0329233f381933cdc240bedb47` 위에서 이어간다. B 원본 세트/workflow는 동일 bytes로 archive에 보존한다. stable v48은 그대로다. 새 PR은 B branch를 base로 하며 A/B/C는 미병합 상태로 유지한다.

- 최종 파일 직접 검증 **417/417 PASS**. [PR #47](https://github.com/0-FLANDRE-0/Aegis_Project/pull/47), [독립 원격104파일 readback](docs/multiship/C/evidence/remote-publication.json). CI 실제 상태는 해당 최신 head checks를 따른다.

## 직전 개발 기준 — Multi Ship WIP B

- [HTML](archive/v48/WIP_MULTI_SHIP_B/Aegis_SIM_v48_WIP_MULTI_SHIP_B.html), **15,328,273 bytes**, SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`.
- 3단계: 출항 전 선택한 DDG-119/CG-52를 실제 세계에 배치한다. 각 함정의 항해·피해·침수·구획/승조원·질량/동역학·침몰/구명뗏목과 원본 3D 모델을 독립 실행한다. `3D VIEW → 배치 함정 보기`로 카메라를 바꾼다.
- 함정별 센서와 양방향 요격/공격·EW·AI는 4~7단계 잔여다. 상대 truth 위치를 CIC/교전 판단에 주입하지 않는다. 기본 적함 없음과 기존 자함 운용, shared world 1회 및 60/120/20 Hz 주기를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_B/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_B.md), [SHA](archive/v48/WIP_MULTI_SHIP_B/SHA256SUMS_v48_WIP_MULTI_SHIP_B.txt), [범위/저장/진단](docs/multiship/B/README.md), [다음 단계](docs/multiship/B/DEPENDENCIES.md), [검증 집계](docs/multiship/B/evidence/verification-summary.json), [측정 조건](docs/multiship/B/PERFORMANCE.md).
- `multiship-physics-b`는 A head `3fab03782abb313cd3ece1bbfe254cdb77981231`을 기준으로 한다. A PR #45가 미병합이므로 B PR은 A 위에 연결한다. A HTML/status/SHA/workflow는 같은 bytes/blob으로 archive에 보존하고 stable v48은 변경하지 않는다. 원본 HTML 직접 업로드·원격 readback과 CI는 [GitHub 인계](docs/multiship/B/GITHUB_HANDOFF.md)를 따른다.

- 최종 직접 검증 **466/466 PASS**. [PR #46](https://github.com/0-FLANDRE-0/Aegis_Project/pull/46), [원격 56파일 readback](docs/multiship/B/evidence/remote-publication.json). CI 실제 상태는 해당 PR의 head checks를 따른다.

## 직전 개발 기준 — Multi Ship WIP A

- [HTML](archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html), **15,314,629 bytes**, SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`.
- 1~2단계: 기존 동작·성능 기준 기록과 독립 함정 상태/컨텍스트. 출항 전 표적함 `있음/없음`, 적함 준비 `없음/DDG-119/CG-52`를 선택하고 저장·reset에도 적용한다.
- 적함은 **STATE_BOUND_INACTIVE** 준비 상태다. 실제 해상 모델 배치·항해·탐지·요격·공격·EW/AI는 3단계 이후다. 자함의 기존 UI·물리·전투 루프와 세계 업데이트 1회를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_A/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_A.md), [SHA](archive/v48/WIP_MULTI_SHIP_A/SHA256SUMS_v48_WIP_MULTI_SHIP_A.txt), [상세/한계](docs/multiship/A/README.md), [다음 단계](docs/multiship/A/DEPENDENCIES.md), [검증 집계](docs/multiship/A/evidence/verification-summary.json), [업로드 인계](docs/multiship/A/GITHUB_HANDOFF.md).
- 브랜치 `multiship-runtime-a`, 기준 main `cb70a637105ce00e7c0619270237cc35a83d39c2`. 사용자 업로드 `28dfc4fcefb22e8c0989617b2212e37d096c05d6`의 HTML을 검증본과 byte 단위로 대조했다. [업로드 검증 기록](docs/multiship/A/evidence/remote-upload-check.json). 이 revision은 지원 파일·E archive 이동·직접 업로드 규칙을 포함한다. PR/Actions 결과는 GitHub 기록을 따른다. stable v48은 같은 bytes로 보존한다.
- [GitHub 규칙 7.1](AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인): 사용자 승인에 따라 앞으로 Codex가 원본 HTML과 지원 파일을 직접 업로드하고 원격 bytes를 확인한다. 사용자 수동 HTML 업로드는 필수가 아니다.

## 직전 병합 기준 — Harpoon WIP E

- [HTML](archive/v48/WIP_HARPOON_E/Aegis_SIM_v48_WIP_HARPOON_E.html), **15,285,590 bytes**, SHA `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`.
- ARM → VLS 하푼 아래 웨이포인트 지정/해제. 최대8점 CIC 탭·초안 점선, 해제 시 AIM 커서 복귀. 발사 시 관/경로 pin, 성공 뒤 초안 삭제/다음 탄의 독립 경로. 마지막 점 전 ARH OFF, INS 평면 통과 뒤 전방 SEARCH. 마지막 점은 탐색 시작점이다.
- 고정 좌표 검색 계획 +8km search/+2km turn reserve ≤140km SIM-TUNE, fuel0.225kg/s. 익명 height/Doppler filter 조정·DL0·보호 수상 track/수동 발사·자동 관/고정재고·DDG 미설치를 유지한다. CG E_1/C·B·A·G·D 명시 legacy; route/flight는 transient다.
- 동일 bytes **178/178 PASS**, 120/124/130km×정지/15kt6건 물리 접촉·empty-sea 강제명중0, 1/8/16/64×3072 full ticks exact, native640×480 실제 경로2/발사2·덮개/부스터/RAF/reset·오류0. 단일 seed·terrain bypass/focused60Hz range와 SwiftShader 범위를 명시하고 실제140km 전조건 인증/일반 명중률을 주장하지 않는다.
- [상태](archive/v48/WIP_HARPOON_E/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_E.md), [SHA](archive/v48/WIP_HARPOON_E/SHA256SUMS_v48_WIP_HARPOON_E.txt), [E 상세](docs/harpoon/E/README.md), [집계](docs/harpoon/E/evidence/verification-summary.json), [인계](docs/harpoon/E/GITHUB_HANDOFF.md).
- 사용자 업로드 `a96053ba1dc56389822c17c92a632f21fcc446b2`의 E HTML을 전달본과 byte 단위로 대조했고 원격 무결성 검사도 통과했다. 이 revision은 작은 지원 파일·상태/SHA·E 전체 workflow와 K 기존 blob의 archive 이동을 포함한다. 전체 Actions와 병합 결과는 [PR #44](https://github.com/0-FLANDRE-0/Aegis_Project/pull/44)를 따른다. [업로드 검증 기록](docs/harpoon/E/evidence/remote-publication.json).

## 직전 로컬 비교 — Harpoon WIP D

D HTML/status/SHA는 `archive/v48/WIP_HARPOON_D/`에 같은 bytes 보존했다. 당시 SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`, 15,283,086 bytes. 자동 관 선택 직접67/67과 이후 별도 장거리 보고(60km gate 통과/100·120·124km prediction basket 거부, gate-only 우회124km15kt miss)는 [D 당시 상태](archive/v48/WIP_HARPOON_D/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_D.md)와 [D 장거리 보고](docs/harpoon/long-range/D/REPORT.md)를 따른다. E는 좌표 route mode로 장거리를 별도 검사하며 track-only prediction basket은 유지한다. K+작은 A/B/C/D 모듈로 D exact 재생성 가능하고 큰 D archive는 신규 remote 업로드 대상이 아니다.

## 직전 로컬 비교 — Harpoon WIP C

C HTML/status/SHA는 `archive/v48/WIP_HARPOON_C/`에 같은 bytes 보존했다. 당시 HTML SHA `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`, 15,281,856 bytes, 직접155/155 기록은 [당시 상태](archive/v48/WIP_HARPOON_C/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_C.md)와 [C 근거](docs/harpoon/C/README.md)를 따른다. A/B/C 큰 archive HTML은 remote 업로드 대상이 아니며 K+작은 모듈로 exact 재생성한다. C workflow/manifest는 역사 보존하고 현재 검사는 E manifest/workflow다.

## 직전 로컬 비교 — Harpoon WIP B

B HTML/status/SHA는 `archive/v48/WIP_HARPOON_B/`에 같은 bytes 보존했다. 당시 HTML SHA `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`, 15,274,780 bytes, 직접133/133 기록은 [당시 상태](archive/v48/WIP_HARPOON_B/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_B.md)와 [B 근거](docs/harpoon/B/README.md)를 따른다. A/B 대형 archive HTML은 remote에 없고 upload 대상이 아니다. K+작은 A/B 모듈로 비교본을 exact 재생성하며 역사 manifest/workflow는 현재 검사로 사용하지 않는다.

## 직전 로컬 비교 — Harpoon WIP A

- A HTML/상태/SHA는 로컬 `archive/v48/WIP_HARPOON_A/`에 같은 bytes로 보존했다. HTML은 14,962,500 bytes, SHA `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`이다. [당시 상태](archive/v48/WIP_HARPOON_A/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_A.md), [A 소형 모듈·검사](docs/harpoon/A/README.md), [공개 자료](docs/harpoon/A/SOURCES.md), [당시 155/155 집계](docs/harpoon/A/evidence/verification-summary.json).
- A는 remote에 업로드되지 않았다. 원격 비교는 이미 존재하는 K blob과 작은 A 모듈에서 exact 재생성한다. 로컬 A archive HTML을 새 remote binary로 전송하지 않는다. A 당시 업로드 인계/workflow/support manifest는 역사 근거이며 현재 E의 분담과 manifest가 우선한다.
- A의 K 284건·기존 CG30/DDG14 이력은 B 검사에 재실행 수로 합산하지 않는다. 정식 v48은 별도 안정 기준이다.

## 직전 병합 기준 — 벙커힐 WIP K

- 파일: [Aegis_SIM_v48_WIP_BUNKERHILL_K.html](archive/v48/WIP_BUNKERHILL_K/Aegis_SIM_v48_WIP_BUNKERHILL_K.html), **14,458,866 bytes**, SHA-256 `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`.
- 사용자 업로드 commit `5c883a5aeb80e0878f0f256f2a7a64d90224920e`의 HTML을 검증본과 byte 단위로 대조했다. [원격 업로드 근거](docs/bunkerhill/K/evidence/remote-upload-check.json).
- 출항 전에 DDG-119 또는 퇴역 전 구성의 CG-52 USS Bunker Hill을 선택한다. 벙커힐은 원본 모델, 고정 61+61 VLS, 전후 함포, 양현 20mm Phalanx, 독립 장착 좌표·사각·탄약을 사용한다. SPG-62 접시 전체 회전, 레이더 회전 부품, 거친 해면 클러터와 피격 후 3D 지속을 검사했다.
- CIC에는 벙커힐의 전·후·양현 SPY 배열 방향을 표시하고 DDG의 기존 대각선 도식은 유지한다. 선택 함선의 피격 인디케이터와 선수 좌측 측면도를 사용한다. CG 내부는 SIM-TUNE 12갑판·277구획·330명 배치다.
- **SHIP → 보수반 → 승조원·함 포기**에서 실제 경로로 도착한 생존자부터 25인승 구명뗏목에 순차 탑승한다. CIC·3D 바다에서 표류하며 저장·복원된다. 정상 전원 퇴함에서 CG 330명/14척/마지막 5명과 DDG 310명/13척/마지막 10명을 확인했다.
- 구명뗏목 정원은 USN Mark 7 공개 자료를 따른다. 실제 CG 비치 수량·진수 위치는 미확정이며 충분한 provision·진수점·형상·표류·접촉은 SIM-TUNE이다. 레이더의 공개 확인 범위와 SPQ-9 두 면의 SIM-TUNE도 명시했다. [구명뗏목 근거](docs/bunkerhill/K/RESCUE_SOURCES.md), [레이더 근거](docs/bunkerhill/K/RADAR_SOURCES.md).
- 로컬 K **284/284** 검사 통과. [상태](archive/v48/WIP_BUNKERHILL_K/AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_K.md), [체크섬](archive/v48/WIP_BUNKERHILL_K/SHA256SUMS_v48_WIP_BUNKERHILL_K.txt), [suite와 한계](docs/bunkerhill/K/evidence/verification-summary.json), [GitHub 반영·검증 안내](docs/bunkerhill/K/GITHUB_VALIDATION.md).
- [Bunker Hill workflow](.github/workflows/bunkerhill-late-profile.yml)가 업로드된 동일 HTML로 exact 재빌드, CIC, 퇴함·저장·배속·native 3D, CG/DDG, 셀·구획·클러터·SPG·실제 다수 Kh-32 AUTO를 검사한다. 원격 결과는 PR의 Actions checks와 artifact를 따른다. 일반 smoke에는 역사 payload 검사도 포함된다.
- 대형 비교 HTML을 추가 업로드하지 않고, 최신 K 내장 asset과 작은 기준 모듈로 D/F/H/I/J를 고정 SHA에 맞춰 재구성한다. 이전 Bunker Hill HTML archive는 전달한 로컬 ZIP에 보존되어 있다. GitHub의 선행 STARTUP_A는 당시 HTML·상태·전체 체크섬 대상 32개 파일을 `archive/v48/WIP_STARTUP_A/`에 exact 보존했고, 기존 root baseline은 역사 검사 호환을 위해 유지한다.
- K는 [PR #43](https://github.com/0-FLANDRE-0/Aegis_Project/pull/43)으로 main에 병합했다. K 뒤의 최신 하푼 구현·검사는 위 E를 따른다. 정식 v48은 별도 안정 기준으로 유지한다.

## 현재 안정 기준 — v48

- 정식 파일: [`Aegis_SIM_v48.html`](Aegis_SIM_v48.html)
- 크기: `7,354,511 bytes`
- SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- **WIP15C를 코드 변경 없이 byte-identical로 승격한 안정판**이다.
- 상태: [`AEGIS_PLAN_STATUS_v48.md`](AEGIS_PLAN_STATUS_v48.md), [체크섬](SHA256SUMS_v48.txt)
- WIP15에서 SRBOC 6기/36튜브 실제 발사 원점, 예비탄·빈 발사기 단위 재장전, Nulka active decoy, ASM seeker acquisition 안정화, SM-2ER/SM-6 수동 대수상 교전, WIP13A 침수 self-test fixture 수리를 마쳤다.
- WIP15C 최종 검사에서 core self-test failure `0`, final runtime page error `0`.
- 상세 WIP15C 감사·검증 기록은 [`docs/wip15/C/`](docs/wip15/C/)에 보존한다.

## 선행 검증 — 출항 전 함선 선택·초기화

- 파일: [`Aegis_SIM_v48_WIP_STARTUP_A.html`](Aegis_SIM_v48_WIP_STARTUP_A.html), `7,361,673 bytes`, SHA-256 `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`.
- 준비 branch: [`ship-startup-ddg-regression`](../../tree/ship-startup-ddg-regression), parent `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`. WIP 번호 미확정이며 `WIP_STARTUP_A`는 기능명 토큰이다.
- 선택 전에 runtime 생성을 대기하고 불변 profile을 확정한 뒤 공통 세션 생성 → 기존 subsystem 결속 → 장비 편성 → 출항을 수행한다. 이 단계에 등록된 운용 함선은 DDG-119였다.
- [상태](AEGIS_PLAN_STATUS_v48_WIP_STARTUP_A.md), [체크섬](SHA256SUMS_v48_WIP_STARTUP_A.txt), [구현·검사·인계](docs/ship-startup/A/README.md).
- 로컬: package 34/34, startup 15/15, DDG runtime 14/14, 실제 3D 복구 13/13 PASS. 기존 B와 전투 aggregate·발사·명중·교전 결과가 같다. 상세 float의 최대 차이 약 `3.9e-13`을 기록했다.
- 사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 크기·Git blob·parent를 확인했으며 검증본과 exact 일치한다. tested head `61a8931f0cc5e933fb901e270e0f5f28e046519b`에서 [출항 준비 CI](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412380) **1/1**, [원본 B 회귀](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412362) **1/1**, [일반 smoke](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412322) **32/32 job PASS**. 일반 3D의 실제 입력은 이번 HTML이며 다른 일반 job에는 역사 payload가 포함된다.
- [PR #42](https://github.com/0-FLANDRE-0/Aegis_Project/pull/42)는 `WIP16` 위의 후속 draft PR이다. 단계 구현·업로드·원격 회귀는 완료했다. 마감 문서·증거·체크섬 반영은 tested source를 변경하지 않는다. 기존 PR #41/main/안정 v48은 변경하지 않았다. 다음 구현은 벙커힐 profile·model·builder 연결이다.

## 직전 검토 후보 — v48 WIP16B

- 작업 branch: [`WIP16`](../../tree/WIP16), PR [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41).
- 이전 사용자 업로드 파일: [`Aegis_SIM_v48_WIP16B.html`](archive/v48/WIP16B/Aegis_SIM_v48_WIP16B.html), **7,357,036 bytes**. `7562bb0925e2b85521d37fefd2c81898ed6de18a`에서 원격 크기·Git blob이 로컬 검증본과 exact 일치한다. B HTML/상태/체크섬은 동일 Git blob으로 archive에 보존했다.
- SHA-256: `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`, Git blob `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf`.
- 상태: [WIP16B 계획/검증](archive/v48/WIP16B/AEGIS_PLAN_STATUS_v48_WIP16B.md), [당시 체크섬](archive/v48/WIP16B/SHA256SUMS_v48_WIP16B.txt), [수정 계약](docs/wip16/B/README.md).
- Codex에서 이어갈 문서: [WIP16B 개발 인계서](docs/wip16/B/AEGIS_CODEX_HANDOFF_WIP16B.md). 최신 판정·검증 명령·미병합 상태·벙커힐 참고 파일과 다음 작업 경계를 포함한다.
- 필수 피격 구멍 생성 중에는 직전 canvas를 유지하고 geometry commit 뒤 GPU 제출을 재개한다. C5의 실제 센서·함포·VLS 부품과 profile binding을 검사한다.
- C55 records 0–12와 3D 렌더러 앞의 전투·피해·nav/DL/loft source는 동일하다.
- WIP16A 사용자 업로드와 [당시 마감 기록](docs/wip16/A/CLOSEOUT.md)은 보존한다.
- 검증: 로컬 package **34/34**, B Chromium renderer/recovery **13/13**, 기존 13조건과 seed 반복 검사 **14/14**, 최종 일반 smoke **32/32 PASS**. 최종 support의 WIP16A 원본 보존 workflow도 **4/4 job PASS**. 기술적 통합 판정은 PASS이며 main 병합은 명시 승인 대기다.
- main/v48.1 승격·release/tag는 아직 실행하지 않았다.

WIP16B HTML 사용자 업로드·원격 exact 확인을 마쳤다. 당시 CI와 파일 대조 guard의 최종 결과는 [마감 증거](docs/wip16/B/evidence/upload_closeout.json)를 따른다. 이후 함선 선택·초기화 결과와 잔여 반영은 위 최신 항목을 따른다. 하푼·토마호크와 다함 동시 운용은 후속 범위로 둔다.

## 이전 통합 기준 — v48 WIP14B4

- **WIP14 FEATURE SCOPE CLOSED.** 최종 작업본은 [`Aegis_SIM_v48_WIP14B4.html`](archive/v48/WIP14B4/Aegis_SIM_v48_WIP14B4.html)이다.
- 크기 `7,319,028 bytes`, SHA-256 `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`. 사용자 업로드 원격 파일은 로컬 최종본과 Git blob exact 일치 확인.
- B1~B4에서 onboard navigation/truth boundary, ASM/RAM own-nav, VLS release scheduler, generic one/two-way weapon-link, SM-6 GPS/양방향 DL, 미사일별 stateful loft를 구현했다.
- B4 게임 검토 범위는 SM-2MR 160 km, SM-2ER/SM-6 260 km이며 실제 무장 최대사거리 인증이나 전 조건 명중 보장값이 아니다.
- 최종 상태: [`AEGIS_PLAN_STATUS_v48_WIP14B4.md`](archive/v48/WIP14B4/AEGIS_PLAN_STATUS_v48_WIP14B4.md), [branch closeout](AEGIS_WIP14_BRANCH_STATUS.md), [checksums](archive/v48/WIP14B4/SHA256SUMS_v48_WIP14B4.txt).
- 상세 B4 report/validation evidence는 [`docs/wip14/B4/`](docs/wip14/B4/)에 보존한다.
- Known deferred: 기존 침수 core self-test 1건, 환경상 WebGL 실렌더링 미검증, 장거리/저고도 포락선 추가 검증. WIP14 유도·DL·loft feature scope 종료를 막는 항목으로 두지 않는다.
- 다음 기능 단계 WIP15는 **3D에 이미 존재하는 양현 3기씩 SRBOC와 runtime 4기/24발을 6기/36발 canonical layout으로 정합하고 실제 launcher/tube 위치에서 발사되게 하는 작업**부터 시작한다. Nulka는 그 뒤 연결한다.

## 이전 개발 기준 — v48 WIP13C22

- 작업본: [`Aegis_SIM_v48_WIP13C22.html`](Aegis_SIM_v48_WIP13C22.html)
- 상태와 남은 검증: [`AEGIS_PLAN_STATUS_v48_WIP13C22.md`](AEGIS_PLAN_STATUS_v48_WIP13C22.md)
- SHA-256: `9b697fcb2edfef69b01d39add5600d1f61638fa42bf6b2d07222d25d491e75fa` (전체 파일: [체크섬](SHA256SUMS_v48_WIP13C22.txt))
- C22는 C19 외형·SPG 서보와 C18 해면/선체 판정을 보존하며, 기존 SM-2/ESSM 신관 프로파일로 대수상 충격·근접기폭을 판정한다. 충돌 예정이면 충격신관을 우선하고, 예상 선체 미스에 한해 신관 조건을 통과한 근접기폭을 허용한다.
- 판정: **C22 코드·결정적 런타임 검사 완료 / 13C 전체 종료 HOLD**. 정식 v48 릴리스가 아니다. 실제 브라우저/WebGL 및 전체 방위 실비행 검증은 남아 있다.
- 검사: [C22 전용 회귀](.github/workflows/wip13c22-regression.yml)에서 패키지·체크섬·고정 틱 신관 fixture·SPG 회귀와 3가지 실비행 시나리오를 실행한다.
- 이전 기준: [C19 상태](AEGIS_PLAN_STATUS_v48_WIP13C19.md), [C19 외형](AEGIS_WIP13C19_STATUS.md), [13C 수상교전 계획](WIP13C_SURFACE_MISSILE_ENGAGEMENT_PLAN.md). C20/C21은 철회된 중간 산출물이므로 병합하지 않는다. 실수로 생성된 C6/C17 브랜치에서도 병합하지 않는다.


## 과거 통합 기록 — WIP12D

- 시뮬레이터: [`Aegis_SIM_v48_WIP12D.html`](Aegis_SIM_v48_WIP12D.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP12D.md`](AEGIS_PLAN_STATUS_v48_WIP12D.md)
- WIP12D Kh-32 잔존체 계약: [`docs/WIP12D_KH32_RESIDUAL_OVERPENETRATION.md`](docs/WIP12D_KH32_RESIDUAL_OVERPENETRATION.md)
- WIP12E 구획 폭압 착수 인계서: [`docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`](docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md)
- WIP12C 내부 종말효과 계약: [`docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md`](docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md)
- WIP12B live ordnance 계약: [`docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md`](docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md)
- 공통 커널 설계: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- HTML SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 상태: WIP12D 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP12D 핵심 범위

- Kh-32의 실제 기폭 위치에서 legacy 잔존 유효에너지 비율을 읽어 폭발 직전 물리 속도와 운동에너지를 복원
- 최대 4개의 결정적 대형 잔존체에 부모의 병진운동과 제한된 화학에너지를 배분하고 질량·에너지 ledger를 닫음
- `PERFORATED`와 `SHATTERED`를 독립 결과로 유지해, 깨진 잔존체도 임계 질량·coherent mass·속도·에너지가 남으면 후속 내부 구조와 반대편 외판을 계속 관통
- 방향 변화마다 상세 구획·장비 volume·국부 외판을 다시 질의하고, 막힌 잔존체와 실제 함외 과관통을 모두 기록
- 함외 비행 뒤 다른 선체·상부구조와 다시 만나는지 제한적으로 재질의하고, 재진입 시 실제 재질·내부 구조·반대편 외피를 다시 계산하여 막힘·도탄·재이탈을 허용
- 모든 완전 관통 외피 접촉은 독립된 파괴구를 남기며, 물리 선체 구멍은 기존 침수 모델에 연결되어 위치·수심·파랑에 따라 실제 유입과 후속 피해를 발생
- 반대편 이탈 위치·파괴구·잔존 질량·속도·에너지를 보존하고, 최종 해수면 위 이탈은 제한된 탄도 표시선, 수선 아래 이탈은 즉시 수중 진입으로 표시
- 기존 폭발원은 속도와 기폭 후 진행거리에 따라 보존적인 head/peak/tail 연쇄원으로 분포하며, 3D도 같은 source를 연결한 물방울형 envelope를 표시
- 관통선·큰 잔존체·출구·바다 진입은 명시적 `내부 구조` 보기에서만 표시하며 렌더링은 물리·피해·난수에 피드백하지 않음
- `피격 중심` 모드는 국부 clipping과 object-AABB culling을 사용하고, `전체 내부`로 모든 세부 구획을 복원; hazard는 최대 3개 batch로 표시
- Kh-32/Kh-35U의 primary legacy 피해 권위와 전투 RNG는 유지하고, blast를 다시 적용하지 않는 별도 event-ID 보충 경로가 잔존체의 제한된 기계적 피해와 실제 외피 구멍만 한 번 적용
- 비폭발성 불활성 파편과 구조 충격은 자체 발화하지 않으며, 기존 WIP12C의 실제 취약 장비 volume 희박 발화 정책만 유지
- DUD는 대형 잔존체 cascade를 만들지 않음
- 누적 형상 보정으로 전방 연돌은 `x=3.50…17.10 m`, 후방 연돌은 `x=-18.15…-4.55 m`; 3D 메시·피격 AABB·RCS·내부 배기 트렁크·2D 상/측면 인디케이터가 같은 값을 소비
- 후방 상단 SPG-62와 받침대를 `x=-20.0 m`로 0.30 m 후퇴시켜 보수적 평면 투영 간격 `0.40 m`, 실제 높이 테이퍼 간격 `1.499 m`를 확보; 계산된 접선각 `48.18°`를 올림한 차단 반각 `49°` 적용

## 검증

- WIP12D 정적 계약 `36/36 PASS`; WIP12A `32/32`, WIP11C `32/32`, WIP11B runtime safety `16/16` 하위 호환 정적 계약 통과
- 정적 계약 파일 `11/11 PASS`, 전체 Playwright `36/36 PASS` (최신 WIP12D `32/32` + 보존 WIP12B·WIP12C `4/4`)
- WIP12D Playwright `2/2 PASS`; core selftest failure `0`, 콘솔/page error `0`
- 실제 Kh-32 seed `481232`: 확장된 전방 연돌을 먼저 맞아 primary damage budget `191`, 물방울형 3-source power 합 `1.0`, damaged parts `17`, 상위 피해 `제1보일러실 47 / 제1발전실 43`
- legacy ASM 공식과 전투 RNG 권위는 그대로이며, 위 seed 차이는 요청에 따라 넓어진 실제 연돌 피격 envelope가 첫 접촉 surface를 바꾼 의도된 형상 결과
- 폭발 직전 복원 속도 `900.1217 m/s`, 대형 잔존체 `4`, shatter continuation `10`, 내부 정지 `2`, 반대편 외판 이탈 `2`
- 실제 잔존체 외피 구멍 `2`, 제한된 기계적 보충 피해 `9.34313`; `0.045 m²` 수중 구멍 진단은 `0.5 s`에 `0.06548 m³` 유입
- 실제 함정 재진입 fixture는 전방 연돌 이탈 후 `12.35 m` 외부 비행과 후방 연돌 재진입·재이탈을 `EXIT → REENTRY → EXIT`로 검증
- 함외 잔존체는 각각 `10.723 kg @ 1178.123 m/s`, `13.137 kg @ 1135.289 m/s`; 해수면 진입 `1`, 즉시 수중 진입 `1`
- 같은 seed 결과 exact, DUD 잔존체/출구 `0/0`, combat RNG 불변, 질량 closure error `0 kg`
- traversal 256회 `0.2684 ms/impact`, render-frame geometry query `0`
- 3D draw call `2342 → 298`(`87.28%` 감소), 피격 중심/전체 내부 복원과 내부 전용 표시 확인
- Workflow YAML은 WIP12D 전용 2개 job을 더한 총 `28`개 job으로 구성

## WIP12D 당시 다음 단계

- WIP12E: legacy scalar blast 재분배를 bounded compartment/portal pressure·impulse solver로 교체하고, 반사압·폭풍·동적 breach·외부 vent를 구조/장비/승조원 consumer와 내부 전용 시각화에 연결
- WIP12E 권위 전환 뒤 기존 Kh-32 `191` scalar budget과 부품별 피해 exact parity는 강제하지 않고 calibration 비교값으로 유지하되, 관통·기폭 위치·잔존체·구멍·침수·전투 RNG 회귀는 보존
- WIP13: WIP12E 완료 뒤 공통 종말효과 계약을 소비하는 제한적 표면교전 표적 승인·발사/FCS 경로
- WIP14: 간단한 표적함과 복수 함선 프로파일
- Kh-32/Kh-35U primary 피해 권위의 공통 packet 완전 이전은 현재의 제한된 breach/mechanical 보충과 별도로 승인·검증
- 실제 함포 발사·포탑·탄창·외탄도·해상사격 해법은 범위를 별도로 고정한 뒤 연결
- homogeneous/KC 장갑 solver, 수중 충격 피해, persistent damage patch와 operational snapshot migration은 별도 단계로 유지

## 안정판과 아카이브

현재 안정판은 [`v48`](../../releases/tag/v48)이다. 이전 WIP 아카이브는 `archive/v48/`에 보존한다. 루트의 과거 작업본 일괄 정리는 WIP16 코드 검토와 별도 범위다.
