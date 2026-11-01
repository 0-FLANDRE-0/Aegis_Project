# TRACK-B 개발·실행 환경

이 문서는 실행 환경과 증거 수집 절차를 기록한다. 결과 승인·계수 튜닝 문서가 아니다. 원래 A/friendly test·fixture·assertion·허용 오차는 보존한다.

## 기준과 별도 산출물

- TRACK-A 기준: `ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561`, HTML SHA `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`.
- RC1 source commit: `da73163a808aa6e480f1c26f42bdc1ae13ddb985`.
- ACTIVE: `Aegis_SIM_v48_WIP_TRACK_B.html`, SHA `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`.
- SHADOW: `Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html`, SHA `e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d`.
- 현재 파일과 실행 증거가 다른 SHA를 가리키면 과거 결과로 구분한다. `BUILD*.json`, `SCOPE*.json`과 실제 HTML byte를 함께 검사한다.

## 측정 호스트

준비 시 확인한 환경: Linux 6.18.57 x86_64 / glibc2.41, 보이는 CPU5개, Python3.12.14, Node24.19.0, Playwright1.62.0, NumPy2.3.5, psutil7.2.2. 실행 작업 디렉터리는 `/dev/shm/aegis-ciws-dmg-a`다. 디스크 여유가 작아 `TMPDIR=/dev/shm`, `PYTHONDONTWRITEBYTECODE=1`로 임시 파일을 RAM-backed filesystem에 둔다. 모듈/브라우저 실제 경로와 test adapter는 기존 A의 것을 그대로 재사용하며 그 source SHA를 결과에 기록한다.

호스트는 다른 시험과 공유한다. controller는 `/dev/shm/aegis-track-b-browser-0.lock`과 `-1.lock` 두 flock lease로 협력 브라우저 상한2를 지킨다. 각 controller 기본 병렬도1, root가 lane을 배분한다. 이 제한에 참여하지 않는 외부 프로세스까지 자동 제어한다는 뜻은 아니다. shared-host CPU·heap 수치를 제품 자체의 순수 비용이나 확정적 개선율로 단정하지 않는다.

## 실제 게임 함수와 시험 경로

광역 native13·paired42·UI213·WebGL8발/29단언은 기존 원래 runner 명령과 환경을 사용한다. `regression_runner.py`는 원래 test/helper23파일을 기준 commit의 git blob과 비교하며, 기존 결과의 false를 자동 통과로 바꾸지 않는다. domain406+retiredUI14의 관계와 최초404/paired2/legacy14 이력은 별도 유지한다.

runtime은 `verify_runtime.py`가 원본 friendly/A script를 runpy로 그대로 실행한다. HTML 읽기와 friendly evidence 쓰기 경로만 후보별로 바꾸며 이벤트·명령·측정·연관 함수를 재작성하지 않는다. 자연 재현과 성능 캡처는 원래 A `PASSIVE_HELPER`, 실제 `__FRIENDLY_REPRO_A__.run`, `simulateFixedTick`, 기존 원래 NIS kernel을 호출한다. private 상태 읽기는 AFTER_ACTION_TEST_ONLY로 분리하고 게임에 되먹이지 않는다. 보호 계수·물리·EKF·IFF·권한·피해 RNG를 바꾸지 않는다.

상태 비교는 원래 native signature/strict assert와 추가 모든 JSON leaf 차이를 함께 남긴다. 공분산·관측 나이·분류·RNG·owner 상태 차이를 누락하거나 단순 metadata로 분류하지 않는다. SHADOW의 원래 소비자 상태는 A와 동일해야 한다. ACTIVE에서 외국/NPC 연관 결과가 바뀐 경우 전체 raw 차이와 전투 결과를 보고하고 원인 검토 전 승인하지 않는다.

## 결과와 이력 보존

실행 명령·SHA·source checksum·exit code·wall time·lease·원시 결과·실패 단언은 evidence에 남긴다. 기존 결과가 있는 다른 SHA로 이어 실행하지 않는다. 변경 시 이전 시도는 `evidence/attempts/`로 보존한 뒤 새 후보에서 재실행한다. RC0 broad는 NOT_EXECUTED였으며 이전 native FAIL 자료를 RC1 결과로 세지 않는다.

`REPORT.md`는 `report.py`로 생성할 수 있지만 root의 최종 `VALIDATION.json`과 현재 SHA의 모든 자료가 닫히기 전에는 PENDING이다. 보고서 생성은 test 결과·기대값·제품을 수정하지 않는다. GitHub 산출물 전달과 원격 readback은 root가 수행한다. main/기준 브랜치 병합, release/tag 생성은 금지 상태를 유지한다.
