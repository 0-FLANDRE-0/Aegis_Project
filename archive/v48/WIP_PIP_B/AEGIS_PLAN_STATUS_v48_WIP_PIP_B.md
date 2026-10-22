# AEGIS 계획·상태 — v48 WIP PIP_B + ENV_A

기준: PIP_A `662eb14e0344b5202631ab95ec1f8cd354d4a41a`. 작업 브랜치: `pip-b-env-a`.

## 최신 개발 기준 — PiP·정보 정리 WIP PIP_B + ENV_A

- [실행 다운로드 — HTML 1개 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/pip-b-env-a/Aegis_SIM_v48_WIP_PIP_B_HTML.zip?download=1) · [리포트 ZIP](https://github.com/0-FLANDRE-0/Aegis_Project/raw/refs/heads/pip-b-env-a/Aegis_SIM_v48_WIP_PIP_B_REPORT.zip?download=1). 실행 ZIP을 풀어 HTML을 연다. 리포트에는 검증·그림·10Hz CSV·계산표·원시 결과·재현 소스·체크섬을 넣고 실행 HTML은 제외한다.
- [실행 HTML](Aegis_SIM_v48_WIP_PIP_B.html), [상태](AEGIS_PLAN_STATUS_v48_WIP_PIP_B.md), [SHA](SHA256SUMS_v48_WIP_PIP_B.txt), [P1–P5·스크린샷](docs/pip/B/REPORT.md), [ENV_A·그래프·사거리 표](docs/envelope/A/REPORT.md), [재현](docs/pip/B/README.md). PIP_A `662eb14` 위 `pip-b-env-a`.
- 제목줄 아래 전체를 PiP 지도로 사용한다. 기존 중심/전환 버튼 노드와 리스너는 제목 메뉴로 이동하고 빈 바다 메뉴에도 연결했다. 락온 카드 본문은 일반 창으로 옮겨8Hz 갱신, 닫기 억제/다음 락 재개방을 제공한다. 정보/메뉴/후보/제목11px, 일반 버튼28px+36px hit, 위험 조작40px를 유지한다.
- SYS의 2D 센서 빔 표시 기본 OFF. 트랙/ESM/항로점/섬/3D 센서는 보존한다. 자함의 청록 원은 world 단위 항적선 두께가 확대되던 표시 오류였으며 화면1.5px로 수정했다. 실제 원인 분리·확대율별 검사를 보고서에 기록했다.
- ENV_A는 변경하지 않은 게임 비행·유도·로프트·신관241개 함수의 독립 진단이다.4종의96개 최대 거리 조합/120개 궤적·10Hz CSV와 표를 내장한다. 실제 장비 성능 비교는 없으며 시작 시 계산하지 않는다.300km는 검사 상한이다. 표 안쪽에도 실패 구간이 있으므로 지도/발사 판단에 아직 연결하지 않는다.
- 표시·기존 회귀1358/1358건(35 suites), ENV_A25/25건(5 suites) PASS. 120초 상태 해시 동일, 전체 진단2회44,221,270bytes 동일, 최종 브라우저156개 사거리 경계 일치. 실제 게임/독립 경로362샘플 오차0. 세부 후보/런타임 차이와 검증 환경은 보고서에 기록한다.
- 원본18,265,254bytes(+204,315), SHA `ad6ed26d8011fd1bcab80c66eac06a63c748e52b471eb622ef38a2ad26498a55`. 모델/저장/고정tick/센서/권한 보존, PIP_A6개 전달 파일 동일 bytes/blob archive. 검수 합계와 환경 한계는 연결된 최종 보고서·영수증에 기록한다.
- GitHub Actions는 수동 workflow만 준비하며 실행하지 않는다. main/기존 브랜치 병합·새 PR 없음. 다음은 MAP_B 사격 지정/무장 플라이아웃/작은 발사 버튼/하푼 모드 전환이다.3D PiP와 실제 폰 GPU/펜 검증은 후속이다.


## 검증과 경계

- [P1–P5](docs/pip/B/REPORT.md), [동작 검증 합계](docs/pip/B/evidence/verification-summary.json), [ENV_A E1–E4·실행 비용](docs/envelope/A/REPORT.md), [정확한 원문 의존성](docs/envelope/A/dependencies.json), [격리 경계](docs/envelope/A/boundaries.json).
- 게임 비행 모델/프로파일은 바꾸지 않는다. ENV_A는 이상적인 유도 입력을 가진 별도의 게임 모델이며 실제 무기 성능 자료로 사용할 수 없다. 사거리 표는 최외곽 성공 정수km이고, 안쪽 거리의 전부 성공을 보장하지 않는다.
- 원본 카드의 행만 DOM 창으로 옮긴다. 선택/락/발사 정책과 무DL 하푼 위치 비공개 정책은 그대로다. 원인 불명의 원은 자함 항적의 world 단위 펜 문제로 확정해 시각 계산 한 줄만 고쳤다.
- [PIP_A archive 증거](docs/pip/B/archive-proof.json), [포장 검증](docs/pip/B/evidence/delivery.json), [원격 전체 readback](docs/pip/B/remote-publication.json). 실행 HTML과 별도 리포트 ZIP을 제공한다.
- Actions dispatch/main·기존 브랜치 병합/새 PR 없음. 실제 폰 GPU/FPS·펜 하드웨어는 측정하지 않았다. 다음은 MAP_B/UI_B다.
