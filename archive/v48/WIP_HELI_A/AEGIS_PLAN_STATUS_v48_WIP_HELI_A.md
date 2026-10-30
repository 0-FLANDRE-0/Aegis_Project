# AEGIS v48 WIP HELI_A — 헬기 2기 출격·운동 단계 완료

- 실행 파일: `Aegis_SIM_v48_WIP_HELI_A.html`, **16,035,793bytes**. SHA-256 `35dbbb64f3067768494c9c6b08d3dc7f02d53cc223f80f4fc7f4970dcb871477`. packed13 SHA `7d204584e25814797b54e09398e0e222823c14f8e3d7a0bd52b5f90794f02680`. [SHA](SHA256SUMS_v48_WIP_HELI_A.txt).
- 기준: PERF_F 게임 SHA `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5` + helicopter-model-a asset head `f0a12d4fcb7d455f34f4583e8f79cb8849da62a5`. 작업 브랜치 `helicopter-a`.
- 자함 DDG-119의 H1/H2를 AIR에서 선택·지도 목적지 지정·출격 요청·대기열 취소한다. 상태/대기열, 대기속도·대지속도 kt, 고도·침로·거리·근사 ETA·단계 잔여 시간, 지도 심벌·목표·연결선과 헬기/모함 카메라를 제공한다. 콘솔 `window.__HELO__.snapshot()`.
- HANGAR_OPEN10 → TRAVERSE20 → SPREAD30 → START45 → PRE_LAUNCH_CHECK10 → LIFT_HOVER5초, 준비 총120초. 기존 격납고 내부·롤업 문, 접힌 기체 이동, 꼬리/블레이드 전개, 순차 시동·로터 상승, 갑판+5m 부상. LIFT 마지막까지 함 로컬이며 DEPART 때 월드 분리·함 속도 상속. 첫 기체가 실제 로터 여유 포함 갑판 경계를 벗어나면 두 번째 준비를 시작한다.
- MH-60R 제원 제한 질점/상태기계. PUBLIC_SPEC 최대140kt/상승8.4m/s는 이번 사용자 명세에서 제공한 제원. SIM_TUNED 기본120kt/상하3.5m/s/가속1.5·감속2m/s²/뱅크30°/저속15°/s. SI, 기존60Hz, 바람 대기↔대지속도, 제한 선회·정지거리·오버슈트 재접근·연속 재지향·50m MSL 호버. 자세와 3D는 read-only 표시다.
- 재고/대기열/문은 ShipRuntime.aviation, 비행 위치는 world.helicopters. 기존 8.5t AIRCRAFT 질량 proxy를 이동·월드 분리하며 중복 추가하지 않는다. 엄격 preflight 작전 저장/복원·기존 빈 재고 migration·reset 정리. 숫자/Boolean 혼용과 고도/속도/갑판 소유권 오류는 쓰기 전에 거부한다.
- final original **198/198 PASS / 7 suites**, page/core/runtime 오류0. 정적56 + 순수 운동28 + runtime44 + desktop/mobile16 + native19 + 배속5 + PERF_F 비교30. [최종 집계](docs/helicopter/B/evidence/verification-summary.json), [조작·구조·재현·조건](docs/helicopter/B/README.md). F의 과거1817검사를 새 집계에 더하지 않았다. native는 SwiftShader, mobile은 viewport/touch emulation이다. Actions는 실행하지 않았다.
- 압축 자산223,419bytes를 한 번 내장, 두 기 geometry/material 공유와 원거리 LOD. 전체 HTML 증가 **326,494bytes (+2.07835%)**. source SH-60 외형과 CC BY4.0 / SB-129 attribution 유지. 실제 source C5 hardpoint와 시각 축척은 오프라인 등록 SIM_TUNED다.
- 기존 packed0..12·embedded ship/weapon bytes, 전투/센서 권위 경로를 보존했다. PERF_F 원본/상태/SHA/workflow 네 파일은 same bytes/blob archive. stable v48와 asset A/선행 증거 유지.
- §7.1 전체 원본 직접 업로드 후 원격 blob bytes·크기·SHA256·Git blob을 대조한다. [원격 readback](docs/helicopter/B/remote-publication.json)은 확인한 source commit을 명시한다. main/선행 branch merge·새 PR·Actions dispatch는 하지 않는다.
- 이번 완료는 자함 DDG-119 항공 운동/출격 단계다. 센서/IFF/truth→sensor/targetPool/configureOffboardSourceC, 무장, 연료 소모, 로터 공력·지면효과, 고도 UI, 착함/회수는 포함하지 않는다. RECOVERY는 상태 자리만 있다. 다음은 센서/IFF·초수평선 관측 단계다.
