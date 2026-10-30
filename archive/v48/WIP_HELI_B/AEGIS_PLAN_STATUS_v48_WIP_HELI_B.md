# AEGIS v48 WIP HELI_B — 로터·격납고·경로 피드백 완료

- 원본 `Aegis_SIM_v48_WIP_HELI_B.html`, **16,037,621bytes**, SHA `e4da7d69b3a4fb70583b336f5659a9f4956b63ed85bcf4fbf9e763ebf30017c3`, packed13 SHA `324c39dd6e78a2976527e66e1e0bc80684b118c182d77b4f62106f7aace46636`. [SHA](SHA256SUMS_v48_WIP_HELI_B.txt), [조작·계약·재현](docs/helicopter/C/README.md), [최종 증거](docs/helicopter/C/evidence/verification-summary.json).
- 기준은 HELI_A SHA `35dbbb64f3067768494c9c6b08d3dc7f02d53cc223f80f4fc7f4970dcb871477`, `helicopter-a` head `15dfc8c1fd60a1e15ddc524e5144724e9381a92b`. 작업은 `helicopter-b`, 새로운 source packed13만 변경했다.
- 메인·꼬리 hub를 source에서 측정하고 회전 그룹을 비균일 축척 밖의 기체 미터 좌표로 분리했다. 실제 중심/법선으로 hub/블레이드만 회전, 꼬리 gearbox12821·지지부는 정지. blur도 같은 축에 맞춘 공유 ring으로 정리했다. source 자산223,419bytes/77geometry/12material 공유 및 LOD를 유지한다.
- 문 뒤에 남은 HULL 외판을 모델 생성 시 두 portal 범위에서 제거했다. 기존 내부·그 밖의 외판은 보존한다. 두 기를 외측0.4m, x=-40.75m로 배치한다. 문 폭 정렬 → 직선 이송 → 꼬리도 벽을 벗어난 x=-56.5m부터 곡선 턴·정렬. 정지 x=-65m는 기존보다3.7m 뒤다. source triangle/양쪽401pose 및 실제21pose에서 간섭이 없고 측면 약0.37m·상부 약0.29m 여유다.
- AIR 왼쪽 조작, 오른쪽 여백 있는 자체 스크롤 목록. 지도 여러 점 순차 추가(최대32)/UNDO/경로 지우기/함선 따라가기. 중간 경로점 통과·급한 코너 감속, 마지막 호버. 목표 변경에도 현재 위치·속도·기수를 유지하고 제한된 감속·선회로 반경을 줄인다.
- 최종 사용자 선택인 **함선 따라가기**를 구현했다. H1좌현/H2우현, 뒤100m·측방400m, 약410m의 움직이는 위치와 함 속도·선회를 따라간다. 궤도비행 모드는 추가하지 않았다. 3D CONTROLS→CAMERA에 H1/H2 추적 버튼을 넣었다.
- 기존 준비120초/50m MSL, SI/고정60Hz, 공개 제원과 운동 한계를 유지한다. 새 상수는 SIM_TUNED. 3D/카메라는 read-only이며 센서/IFF/targetPool/offboard, 무장, 연료, 회수, 고도 UI, 로터 공력은 연결하지 않았다.
- `AEGIS_HELO_SAVE_B1`은 새 경로·추종·localYaw를 preflight/복원한다. 실제 A 비행 저장 migration에서 위치·속도·기수를 보존했다. 잘못된 route/null/index/Boolean·legacy는 쓰기 전에 거부한다.
- 최종 원본 **264/264 PASS / 11 suites**: static56, motion35, runtime44, extensions27, UI30, native17, legacy10, clock5, clearance8, rig-source2, paired baseline30. page/core/runtime 오류0. old A198/F1817을 새 집계에 더하지 않는다. 조건/한계는 증거를 따른다. Actions는 실행하지 않았다.
- HTML은 A보다 **1,828bytes(+0.0114%)**만 증가했다. generic SH-60 source 외형과 SB-129/CC BY4.0 attribution을 유지했다. MH-60R 상세 외장이나 실제 rotor aero를 검증한 의미가 아니다.
- A 원본/상태/SHA/manual workflow는 same bytes/blob으로 `archive/v48/WIP_HELI_A/`에 이동했다. stable v48와 asset/이전 증거는 그대로다. §7.1 전체 원본 직접 upload/원격 blob bytes·크기·SHA·Git blob readback을 수행한다. [원격 확인](docs/helicopter/C/remote-publication.json)은 source commit을 명시한다. main/선행 branch merge, 새 PR, Actions dispatch는 하지 않는다.
