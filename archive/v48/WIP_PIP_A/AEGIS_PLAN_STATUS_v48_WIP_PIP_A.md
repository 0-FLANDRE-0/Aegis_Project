# AEGIS 계획·상태 — v48 WIP PIP_A

기준: MAP_A `c1297b6b0c6d7ceb600517aea3d5a4d0aa62594f`. 작업 브랜치: `pip-a`.

## 완료

- [실행 HTML](Aegis_SIM_v48_WIP_PIP_A.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_PIP_A.md), [SHA](SHA256SUMS_v48_WIP_PIP_A.txt), [A–J·스크린샷](docs/pip/A/REPORT.md), [재현](docs/pip/A/README.md), [그리기 감사](docs/pip/A/RENDER_AUDIT.md). MAP_A `c1297b6` 위 `pip-a`.
- 같은 관측 트랙·MAP_A 선택/통제/계획을 쓰는 실제 2D PiP. 별도 거리/중심/추적, 팬/휠/핀치·메뉴·항로점·하푼 계획과 주화면 전환. 기본 40km/4Hz, SYS 2/4/10Hz, 최소 창200×160·반경0.1km, m 표시.
- 후보 [확대]는 전부 보임 우선의 최대 확대. 40px 미만이면 분리 불가/주화면 전환, 목록 유지. ESM 처음40px 판정 제외. 기존 간이 지도는 DEAD_LEGACY로 원문 보존하고 숨겨진 메인2D 페인트는0회다.
- **1271/1271 assertions /32 suites PASS, 페이지 오류0**. MAP_A 런타임994건과 새 핀 기준 정적48건, PiP 입력/순수성/기하/120초/실제3D 검증. PiP ON/OFF 및 기준·수정·pause/resume120초 해시 동일. 물리·센서·판정·발사 권한·게임 저장/모델 보존.
- 원본18,060,939bytes (+13,323), SHA `76c77b5c80835f87654c8aa39cd6a82c1ad66de8bc408ebad675997157024847`. 최소 PiP100m 간격42.84~47.88px. 소프트웨어 WebGL 전후 평균1275.60→1039.96ms(18.47% 감소); 실폰 FPS가 아니며 낮은 전체FPS에서는 PiP도 같은 RAF 상한을 받는다.
- MAP_A 네 파일 동일 bytes/blob archive. 전체 원본 업로드·독립 readback은 docs/pip/A/remote-publication.json. Actions dispatch/main·기존 브랜치 병합/새 PR 없음. 다음은 MAP_B 사격 지정/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환과 임시 커서 연결 제거. 3D PiP·실폰 GPU/펜 하드웨어는 후속.

## 검증·경계

- [32 suites /1271 assertions](docs/pip/A/evidence/verification-summary.json), [보고서](docs/pip/A/REPORT.md), [감사](docs/pip/A/RENDER_AUDIT.md), [보존 증거](docs/pip/A/archive-proof.json).
- 공통 준비와 읽기 전용 그림 분리. PiP는 적 truth/별도 트랙을 소유하지 않는다. 기존 빔 라벨 truth domain과 적 대응체 실제 좌표 fallback 표시를 관측 결과로 정리했다.
- 2D·PiP 거리/중심은 독립, 네 MAP_A 슬롯은 공용. 무DL 하푼 actual 위치 비공개와 발사 후 고정 INS 경로를 보존한다.
- 게임 저장 정책은 그대로이며 UI 설정은 브라우저 전용 schema1. 잘못된/차단된 저장은 기본값으로 시작한다.
- E의4Hz/입력 지연은 CPU 기하 fixture의 스케줄 검증이다. 실제 SwiftShader는 약1초/프레임으로, PiP도 이 RAF 상한을 받는다. 성능 결과는 실폰 측정이 아니다.
- 기능/센서/무장·ROE 변경 없음. MAP_B, 3D 직접 선택/3D PiP, 실제 단말·펜 검증은 후속이다.

## 발행

수동 workflow만 준비하며 Actions는 실행하지 않는다. 전체 HTML 원본과 support를 직접 업로드하고 원격 전체 blob을 다시 읽는다. [발행 영수증](docs/pip/A/remote-publication.json). main 및 기존 브랜치의 head를 보존한다.

## 다운로드 전달 보완 — 2026-10-20

- [실행용 ZIP](Aegis_SIM_v48_WIP_PIP_A_HTML.zip), [ZIP SHA-256](SHA256SUMS_v48_WIP_PIP_A_HTML_ZIP.txt), [포장 검증](docs/pip/A/evidence/html-delivery.json).
- 검증된 HTML 하나만 수록한다. 원본18,060,939bytes/SHA-256과 시뮬레이션 코드는 그대로다. 기존1271건 결과를 보존하며 이번 작업에서 시뮬레이션 검사를 새로 실행한 것은 아니다.
- ZIP CRC·수록 목록·압축 해제 bytes·재현 생성·원격 전체 bytes를 확인한다. 현재 리포트 ZIP은 생략하고 다음 기능 완료본부터 실행/리포트 ZIP을 별도로 제공한다.
