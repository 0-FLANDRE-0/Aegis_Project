# AEGIS 이전 작업본

루트에는 현재 최신 안정판과 최신 개발 WIP 세트를 두며, 아래 파일은 내용 변경 없이 버전별 폴더에 보존한다. `archive/` 내부 파일은 최신 소스 자동 선택 및 GitHub Actions 실행 대상이 아니다.

PERF_C의 직전 PERF_B HTML/status/SHA/workflow는 `v48/WIP_PERF_B/`에 원래 bytes/blob으로 보존한다. PERF_B support/evidence는 `docs/performance/B/`에 유지하고 현재 검증/workflow는 `docs/performance/C/`다.

당시 PERF_B의 직전 PERF_A HTML/status/SHA/workflow는 `v48/WIP_PERF_A/`에 원래 bytes/blob으로 보존한다. PERF_A support/evidence는 `docs/performance/A/`에 유지하고 당시 검증/workflow는 `docs/performance/B/`였다.

당시 PERF_A의 직전 H4A HTML/status/SHA/workflow는 `v48/WIP_MULTI_SHIP_H4A/`에 원래 bytes/blob으로 보존한다. H4A support와 당시 evidence는 `docs/multiship/H4A/`에 유지하며, 당시 검증·workflow 기준은 `docs/performance/A/`였다.

| 버전 | 주요 변경 | 최종 상태 | 후속 버전 |
| --- | --- | --- | --- |
| v37.1 WIP01 | SPQ-9B·SPS-73 독립 3D 스윕 시각화 | 기능 구현 및 비-WebGL 검사 완료 | WIP02 |
| v37.1 WIP02 | CIWS B1 익명 관측·로컬 RF 경계 분리 | 안전 결함 확인 | WIP03 |
| v37.1 WIP03 | A3 AUTO 권한·로컬 탐지 필수화 | 브라우저 fixture 결함 확인 | WIP04 |
| v37.1 WIP04 | 명시적 B1 진단 API·획득 후 권한 재검증 | 회귀 fixture 보강 필요 | WIP05 |
| v37.1 WIP05 | 후보 audit·사각·재획득 fixture 보강 | AUTO 전달·3D 격리 문제 확인 | WIP06 |
| v37.1 WIP06 | AUTO fixture·정지 상태 3D 격리 수정 | 후속 기하 fixture 문제 확인 | WIP07 |
| v37.1 WIP07 | Phalanx 자기검사 접근 기하 수정 | A3 재접근 축 불일치 확인 | WIP08 |
| v37.1 WIP08 | A3 재접근 fixture 수정·CIWS B1 종결 | Actions B1 통과 | WIP09 |
| v37.1 WIP09 | CIWS B2 가속도·기동 예측 | 생산 RF noise guard 부족 | WIP10 |
| v37.1 WIP10 | 가속도 feed-forward 분리·live RF fixture | 속도 안정화 부족 | WIP11 |
| v37.1 WIP11 | 로컬 RF 속도 평활·B2 종결 | Actions B1/B2 통과 | WIP12 |
| v37.1 WIP12 | CIWS B3 연속 손상 성능 | Actions B1/B2/B3 통과 | WIP13 |
| v37.1 WIP13 | Phalanx/SeaRAM Block 1B 공통 센서 15/10 km | Actions 6개 job 통과·정식 승격 기준 | v37.1 |

## 보관 경로

각 작업본은 `v37.1/WIPNN/` 아래에 다음 두 파일로 보존한다.

- `Aegis_SIM_v37.1_WIPNN.html`
- `AEGIS_PLAN_STATUS_v37.1_WIPNN.md`

## WIP PERF_C 보존

직전 verified PERF_C HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_C에 samebytes/blob으로 이동했다. 해당 historical scripts/records는 당시 경로와 조건을 보존하며 현재 root/support/workflow는 PERF_D다.

## WIP PERF_D 보존

직전 D HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_D에 samebytes/blob으로 이동했다. 이전 scripts/records는 당시 경로와 조건을 유지하며 현재 root/support/workflow는 PERF_E다.

## WIP PERF_E 보존

직전 E HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_E에 samebytes/blob 보존. 현재root/support/workflow는 PERF_F다.
