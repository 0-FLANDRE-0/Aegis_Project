# 파랑 응답 일관성 조사 — 물리 변경 없음

대상은 VP_A에 그대로 포함된 SOV_A 물리다. 좌표·운동·센서·피격 코드 변경은 없다. 위치는 [source-audit.json](source-audit.json)의 `c55-game-main` 해제 소스를 기준으로 한다.

## 함정·역할별 현재 상태

| 프로파일 | 자함 | 아군 NPC | 적 NPC | 근거 |
|---|---|---|---|---|
| DDG-119 | 파랑 상하동/횡동요/종동요 외력 없음 | 없음 | 없음 | `createShipDynamicsV15`의 `waveForce=sovHullA(shipProfile)?...:null` |
| CG-52 | 없음 | 없음 | 없음 | 동일 조건. 역할이나 팀이 아니라 프로파일로 제한 |
| SOVREMENNY_956 | 현재 금지 | 현재 금지 | 있음 | `sovWaveForcingA`; 중립 NPC도 동일하게 있음 |

DDG/CG가 물리 자체를 생략하는 것은 아니다. 동일한 부력·중량·GM/GZ·관성·감쇠·타각/선회·피격 충격·침수 계산을 한다. 따라서 손상, 선회 또는 외부 충격이 있으면 자세와 흘수가 변한다. **무피해·정상 직진에서 해상상태만 바꾸어도 주기적인 강체 동요를 일으키는 외력**이 연결되지 않은 것이다. 정수 부력과 중량이 평형이면 그 비율/흘수/횡경사가 거의 고정되는 현상은 이 구조와 일치한다.

이는 DDG/CG가 실제로 파랑에 반응하지 않는다는 함급 제원이 아니다. SOV_A의 신규 함정 외력만 opt-in으로 추가하고 기존 DDG/CG의 물리 회귀를 보존한 구현 범위의 차이다. 기존 함정에 공용 응답을 넣는 별도 작업이 남아 있다.

공통 파랑 환경이 전혀 없는 것도 아니다. 공통 바다 높이, 기상·클러터, 파공의 해수 유입, wake/foam 등의 경로는 별개다. `applyShipBodyFrame`(57836)은 물리의 `sceneMatrixRows`를 그대로 읽는다. `syncFloodAttitudePreview`는 표시용 점검 레이어이며 DDG/CG에 별도의 가짜 파랑 운동을 더하지 않는다.

## SOV 계수의 근거와 한계

`profile.js` / `makeSovProfileA`의 `waveResponse:{source:'SIM_TUNED',heave:.55,roll:.18,pitch:.18}`다. 공개 956형 RAO, 모형 시험 또는 실선 계측으로 맞춘 값이 아니다.

`sovWaveForcingA`는 중심 파고 1점, 좌우 `±0.4·beam`, 전후 `±0.25·length`에서 공통 sea-level 함수를 샘플한다. 중심 높이에 .55를 곱하고, 두 점 간 파고 차로 구한 기울기에 roll/pitch 각각 .18을 곱한다. 기존 shared force integrator에 부력/수선면적/GM과 결합한 외력·모멘트로 들어가므로 렌더 애니메이션이 아니다.

의도는 156m 선체가 한 점의 파고·해면 기울기를 그대로 따라 과도하게 움직이는 것을 완화하는 SOV_A의 경험적 설정이다. 선체 평균 파압, 주파수·파향별 응답, 속력에 따른 조우 주파수, 공진, slamming을 구현한 값은 아니다. SOV_A의 잔잔/0.9m/3m 검사도 수치가 유한하고 동요가 발생하는 동작 확인이며 실제 함급 응답의 정량 보정 근거가 아니다. 이 계수를 DDG/CG에 그대로 복사하는 것을 물리 검증으로 볼 수 없다.

## 공용화 지점과 영향

| 지점 | 필요한 후속 작업 | 확인해야 할 영향 |
|---|---|---|
| 파랑 외력 provider | `sovWaveForcingA`를 profile/pose/environment 입력의 공용 provider로 분리. 프로파일별 계수·샘플링/평균화·감쇠 근거 명시 | 현재 SOV 보존 회귀와 DDG/CG의 새 동요 회귀를 구분. 같은 fixed tick/seed 결정성 유지 |
| shared dynamics | SOV 조건을 capability 기반으로 바꾸고 각 hull의 수선면적·GM·질량·관성에 맞춰 적용 | 120Hz 힘 적분, 20Hz 정수압 quadrature를 유지한 채 비용 측정. 침수 안정성·전복·갑판 침수·충격 응답 재확인 |
| 센서 높이/수평선 | 함체 frame의 동적 안테나 좌표를 각 RF/LOS/horizon 계산에 일관되게 공급 | **현재 APS의 `apsPhysicalHeightF`(4080)는 함 프로파일의 정적 `referenceHeightM`를 읽음.** SOV_A에서 30m fallback을 대체했지만 매 파랑 자세의 mast-tip 세계 Z를 계산하는 경로는 아님. 외피/함체 frame의 반사체와 정적 수평선 높이 사이 일관성은 후속 검토 필요 |
| 함포/사통 | 기존 함체→월드 좌표/안정화·짐벌·속도 제한의 경계 재검사 | 롤/피치·각속도 증가 시 포신 조준 오차, SPG/센서 beam 안정화, 발사점 운동/탄체 속도 상속을 확인 |
| 피격 판정 | `createShipBodyFrameV1`과 `shipFrameForInputsPerfB`에 이미 heel/trim/draft가 포함됨 | 동적 pose로 ray/sweep·외피·구획 경로를 동일하게 갱신. 새 동요로 충돌 누락/이중 접촉 또는 오래된 frame cache 사용이 없어야 함 |
| 헬기 갑판 단계 | 로컬 hardpoint/DEPART 분리와 갑판 물리 frame 연결 확인 | 상하동·회전 중 기체 위치, 문/선체 간섭, 이탈 순간의 수직·회전 점속도 상속 여부 검토. 현재 회수/착함은 미구현이므로 착함이 준비됐다고 취급하지 않음 |
| 표시/선체 기준 | 3D는 물리 frame 읽기만 유지. 해면 shader와 실제 물리 sea-level 파형/시각 정합 확인 | 카메라 흔들림을 운동 판정과 혼동하지 않기. 갑판 로컬 카메라와 월드 카메라 정책도 별도로 정의 |

권장 순서는 공용 외력 입력/프로파일 계약 → DDG/CG의 정량 응답 보정 → 동적 센서 높이 일관성 → 사통·발사·피격·헬기 경계 회귀다. 이번 VP_A에서는 위 항목을 구현하지 않았다.
