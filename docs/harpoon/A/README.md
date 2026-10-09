# RGM-84D Harpoon A

벙커힐 K의 검증된 함선·피해·센서 구조에 수동 하푼 발사를 연결한 작업본이다. 최신 HTML은 루트의 `Aegis_SIM_v48_WIP_HARPOON_A.html`이며, 안정 v48 승격이나 원격 병합을 뜻하지 않는다.

## 운용

출항 전 CG-52 USS Bunker Hill 선택 → 출항 → EMCON 해제 → 확인된 수상 트랙 선택 → ARM의 TGT에서 운용자 식별을 적성 또는 훈련 표적으로 지정 → ARM → VLS의 MK 141 / HARPOON에서 A1–A4·B1–B4 선택 → HARPOON FIRE.

UNKNOWN·FRIEND·NEUTRAL, 오래된 관측, 불충분한 INS 예측 범위, 빈 관, 손상 발사대와 위험한 발사 자세는 발사를 차단한다. 버튼을 누른 뒤 0.18초 덮개 열림 기간이 끝나는 실제 발사 순간에도 조건을 재검사한다. 자동 교전은 하푼을 발사하지 않는다. DDG-119에는 Mk 141을 추가하지 않는다.

발사관은 소스 모델의 실제 8개 관에 고정되어 있다. 한 발을 쏘면 해당 관만 비고 번호·선택 위치는 그대로 남는다. 이 단계는 해상 재장전을 제공하지 않는다. 새 세션 전체 RESET은 8발을 복원하며 작전 저장 복원은 저장된 관별 잔탄을 유지한다.

## 코드 계약

- `profile.js`: 불변 RGM-84D 제원·SIM-TUNE, 모델 메타데이터와 실제 관 등록 자료를 읽는다.
- `core.js`: 자함 `ACTIVE_SHIP_RUNTIME.weapons.harpoon`의 관별 재고·발사 대기 상태, world `antiShipOrdnance`·`harpoonBoosters`의 비행·분리를 관리한다. 60 Hz 물리 틱이 권위자이며 기존 120/20 Hz는 유지한다.
- 발사 순간 익명 트랙의 KF 위치·속도·공분산을 깊은 복사 후 동결한다. INS는 이를 전파하며 비행 중 함정 트랙의 갱신·삭제·lock 변경을 따라가지 않는다. 데이터 링크와 SPG-62 조명은 없다.
- 공통 물리 RF 반사 풀·해면 셀·LOS·날씨에서 range/bearing/elevation/Doppler/extent/SNR 익명 관측을 합성한다. ARH는 그 관측의 운동학·범위·Doppler gate와 alpha-beta 상태를 사용한다. 표적 truth ID를 선택하거나 강제 명중하지 않는다.
- 풍축 점질량 비행에 추력·항력·중력·양력과 공유된 공력 한계를 적용한다. 속도를 강제로 고정하지 않는다. 부스터와 미사일의 질량·위치·속도는 물리 틱에서 분리한다. 연료 소진 후에는 무추력 비행을 계속한다.
- 실제 이동 표적함의 swept hull 접촉 후 기존 WIP12A 관통·지연신관과 WIP12F 단일 피해 packet·구획·외피·침수 consumer를 사용한다. 탄두 전체 중량을 TNT로 취급하지 않는다.
- `renderer.js`: 원래 발사관 전방 덮개 272 triangles만 분리한다. 공유 62개 geometry/25개 재질의 표시 인스턴스, 날개·꼬리날개·분리 부스터·화염·기존 연기 backend를 사용한다. 렌더 프레임은 물리를 계산하지 않는다.
- `window.__HARPOON_DIAG_A__`는 읽기 전용 snapshot, 발사 gate, 관 선택, 고정 틱 fixture와 core audit를 제공한다. `focusedTicks`는 환경·표면·하푼만 진행하는 DIAGNOSTIC_ONLY 경로다. 배속 검사는 실제 전체 fixed-tick accumulator를 사용한다.
- 작전 저장은 `MK141_INVENTORY_A1`의 고정 설치 ID와 boolean 잔탄만 복원한다. 비행 중 탄체는 복원하지 않는다. 기존 명시 호환 CG revision은 detached clone에 최초 8발을 migration한다. 현재 revision에서 재고 누락·중복·잘못된 관·자료형은 전체 import를 mutation 없이 거부한다.

## Kh-35U 참고 범위

기존 `ASM_FLIGHT_PROFILES`·`createAsmFlightState`·`updateAsmFlightPhysics`·`updateEnemyMissile` 및 Kh-35U의 sea-skimming/RF/종말 처리 경로를 검토했다. 공통 대기밀도, 시공간 해면, 물리 RF 반사와 관통·폭발·침수 기반을 재사용한다. 하푼은 함상 부스터, 발사 관 구속, 날개 전개와 발사 시점 INS 기억이 필요하므로 별도 점질량 비행 프로필을 둔다. Kh-35U의 기존 6DOF-lite 엔진·피해 보정값을 하푼에 그대로 복사하지 않았다. 기존 Kh-35U/Kh-32 프로필과 위 4개 함수는 byte 동일 검사를 통과했다.

## 재현

Python 3.12+, Node 22+, NumPy 및 `docs/bunkerhill/K/requirements.txt`의 Playwright가 필요하다. WebGL 검사는 Chromium SwiftShader를 사용한다. 브라우저를 자동으로 찾거나 `AEGIS_CHROMIUM_EXECUTABLE`을 지정할 수 있다.

```sh
python docs/harpoon/A/build.py --out /tmp/harpoon-rebuild/candidate.html
python docs/harpoon/A/verify_static.py Aegis_SIM_v48_WIP_HARPOON_A.html archive/v48/WIP_BUNKERHILL_K/Aegis_SIM_v48_WIP_BUNKERHILL_K.html /tmp/harpoon-check/static
python docs/harpoon/A/verify_runtime.py Aegis_SIM_v48_WIP_HARPOON_A.html /tmp/harpoon-check/runtime
python docs/harpoon/A/verify_native.py Aegis_SIM_v48_WIP_HARPOON_A.html /tmp/harpoon-check/native
python docs/harpoon/A/verify_salvo.py Aegis_SIM_v48_WIP_HARPOON_A.html /tmp/harpoon-check/salvo
python docs/bunkerhill/K/verify_cg_runtime.py Aegis_SIM_v48_WIP_HARPOON_A.html /tmp/harpoon-check/cg
python docs/bunkerhill/K/verify_ddg_runtime.py Aegis_SIM_v48_WIP_HARPOON_A.html > /tmp/harpoon-check/ddg.json
```

원본 모델 재저작은 사용자 제공 `RGM-84D_Harpoon_Viewer_v1.html`을 `author_model.py`에 전달한다. 정확한 원본 SHA를 확인하고 균일색 텍스처를 재질 색으로 변환하며 날개·꼬리날개를 분리한다. 배포 HTML에는 필요한 자료가 모두 내장되므로 사용자가 뷰어 파일을 추가로 설치할 필요는 없다. 제공된 모델은 [Civorsky의 Missiles](https://sketchfab.com/3d-models/missiles-37899978144a45d0bd03c3538957b145), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)이며 날개폭·관절·재질 최적화 변경을 명시한다.

검사 원자료는 `evidence/`, 공개 근거·미확정 범위는 [SOURCES.md](SOURCES.md), 최종 집계는 [verification-summary.json](evidence/verification-summary.json)을 따른다. 원자료의 `experimental.html` 표기는 당시 검사 입력명이며 최종 파일과 bytes가 동일하다.
