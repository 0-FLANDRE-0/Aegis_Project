# 소브레멘니 자함화 준비 조사 — 구현 없음

코드 위치는 `Aegis_SIM_v48_WIP_VP_A.html`의 압축 레코드 **c55-game-main**을 해제한 소스 행이다. `build.py`의 `decoded()`로 동일 소스를 복원할 수 있다. [핵심 위치/본문](source-audit.json), [프로파일·슬롯 가정 검색 목록](profile-assumptions.tsv), [전체 UI 분류](UI_CLASSIFICATION.tsv)를 함께 본다. 검색 목록은 401건이며 중복 호출·진단도 포함한다. 401개 결함이나 401개 필수 수정이라는 뜻은 아니다.

## 실제 차단 지점

| 영역 | 현재 동작과 코드 위치 | 비 VLS·비 SPY 자함 수용 여부 |
|---|---|---|
| 레지스트리 | `SHIP_PROFILE_REGISTRY`(2094): 세 프로파일 등록 | 등록 자체는 가능. SOV는 이미 등록됨 |
| 함 선택 | `SHIP_STARTUP_CATALOG`(3072), `selectStartupShip`(3080): `npcOnly` 제외·거부 | 현재 명시 차단. 이번에도 유지 |
| runtime 생성 | `createShipRuntime`(3751)의 역할 guard + `createPlayerShipSession`(3770)의 SOV 무조건 거부 | 전투 가능 자함으로 바꾸는 일반 권한 계약부터 필요 |
| 자함 소유권 | `createPlayerShipSession`, `ACTIVE_SHIP_SESSION/RUNTIME`(3771–3779) | canonical runtime은 공용이다. 다만 현재 자함 전용 전역/호환 별칭은 초기 선택에 한 번 결속됨. NPC runtime을 포커스만 바꾸어 자함으로 삼을 수 없음 |
| 자함 센서 초기화 | `SENSOR_MODEL=SHIP_SENSOR_MODEL_REGISTRY...`(25411) | **직접 차단**. 레지스트리에 SOV_NO_SENSORS_A가 없어 undefined. NPC용 `resolveSensorSuite`의 비설치 호환 템플릿 경로와 다름 |
| 센서 슬롯 | `createPreparedShipRuntimeA`(13885–13910), `prepareObserverC`, `createShipRadarStateA` | `spyScheduler`, `spq9b`, `bridgeMasterE`, `hardpoints.spg62` 형태를 전제. NPC는 0/빈 슬롯과 실행 guard로 수용 중. 이는 비 SPY 전투체계 일반화가 아님 |
| 형상 초기화 | `IS_BUNKER`(3103), 이후 `SELECTED_SHIP_GEOMETRY/REGISTRATION` 분기 | CG 이외는 Burke 기본 경로로 이어지는 자함 전역이 남음. NPC의 `geometryForShipProfileA` SOV 분기와 자함 출발점이 다름 |
| VLS 편성 | `SHIP_STARTUP_CATALOG`(3074), `wip125RenderLoadoutUi`, `createProfileVlsInventory`(20452) | 재고 0은 표현 가능. 그러나 출항 UI는 fwd/aft VLS 셀과 SM2/SM2ER/SM6/ESSM4/EMPTY 편성을 전제. 비 VLS 함은 전용 편성 모듈/편성 없는 출항 분기가 필요 |
| 무장 슬롯 | `createPreparedShipRuntimeA`(13895–13902), `profileWeaponMassNodesA`, `prepareWeaponsD` | `vls/closeIn/mainGun/srboc/nulka/harpoon` 및 Mk41/Mk36/Nulka 매거진 이름이 고정됨. SOV의 빈 재고·dummy gun은 **비무장 NPC 호환용**이며 러시아 무장 인터페이스가 아님 |
| 사통 | SPG62 등록/할당, SPY 정밀추적, VLS release 경로 | 추적 지정과 센서별 사통 지원을 인터페이스로 분리해야 함. F2의 EMCON 수동 지정은 공용 지정의 출발점으로 재사용 가능 |
| 저장/불러오기 | `exportOperationalState`, `operationalValidationContextV48Wip11B`, `validateOperationalWeaponsV48Wip11B` | 외부 envelope와 shipId/profile/revision 검증은 공용. 현재 무장 codec은 VLS·US close-in·soft-kill·Harpoon 형식. 비 VLS 함도 빈 슬롯 envelope는 유지 가능하지만 새 무장은 모듈 codec과 migration 필요. 강제로 profileId만 바꾸는 저장은 거부되는 것이 정상 |
| 헬기 | `HELO_FACILITY_PROFILES_I`, `heloFacilityA`(102 부근) | DDG/CG 시설만 있고 SOV 시설/Ka-27 없음. AIR shell은 재사용 가능하나 갑판·격납·출격 경로/기체 데이터가 새로 필요 |
| 데미지·침수 | `preparePhysicalShipB`(13666), `createPreparedShipRuntimeA`(13896), SOV 손상/침수 codec | 공통 계산기는 이미 SOV NPC에서 작동함. 다만 자함의 builder registry는 별도 진입점. `SHIP_INTERIOR_BUILDER_REGISTRY`(32040)는 DDG/CG뿐이라 SOV 자함은 등록/결속을 추가해야 함. 자함 dynamics getter(32591)는 Burke 단면 전역을 인자로 넘기는 경로도 정리 필요 |
| 렌더·피격도 | NPC renderer는 SOV 지원. 자함/SHIP 2D 도면은 `IS_BUNKER`와 Burke 기본 경로 | renderer provider를 자함/NPC 공통 선택자로 통일하고 SOV 2D 도면 자료를 등록해야 함 |
| FLEET 변경 | SOV NAV-only guard, network/team/attack 명령 거부 | 현재 적·중립 SOV를 자함으로 변경하는 기능은 없음. 기존 동맹 변경 버튼을 임의로 개방하면 안 됨 |

## UI 분류와 교체 경계

아래는 구조 판단이며 개별 버튼·입력·탭의 id/근거 위치는 [UI_CLASSIFICATION.tsv](UI_CLASSIFICATION.tsv)에 기록한다. 기능을 새로 구현하거나 기존 식별·발사권한을 바꾸지 않았다.

| 분류 | 항목 | 근거/걸리는 점 |
|---|---|---|
| 공용 | 2D 지도, 팬/줌/중앙, 전체화면, 시간 배율, NAV 속력·타각·항로·UNDO, 기본 3D/CAMERA/GFX, 함대 NAV | `drawRadar`, `setControlDeckTabWip13C`, `physicalShipCommandB`, 카메라 adapter. 센서 트랙의 화면 표시와 진실 상태는 분리 유지 |
| 공용 | 손상/침수/승조원/퇴함의 표시 구조 | 데이터가 runtime/토폴로지에서 옴. 장비 이름·부서 명칭과 일부 도면은 아래 혼합 항목 |
| 이지스/미국 장비 전용 | SPY mode/PD, SPG-62 조사, VLS 셀/SM2·SM2ER·SM6·ESSM, Mk45, Phalanx/RAM, Mk36/Nulka, Mk141 하푼 | 실제 release·센서·inventory 구현이 장비 종류를 전제. SOV 전투 패널에서 이 버튼들을 이름만 바꾸어 재사용하면 안 됨 |
| 혼합 | ARM/TGT·LOCK·AUTO UI | 패널/운용자 선택은 공용이나 정상 LOCK이 SPY PD와 결속, AUTO 선택·weapon preference도 현재 US 장비 내용. 공용 지정/ROE와 센서별 지원을 분리해야 함 |
| 혼합 | FLEET 관측 공유·전자전·합동 제어 | 공용 runtime/전단 shell이 있으나 현재 링크/교전 지원 내용과 장비 권한이 기존 함정에 맞춰짐. UI의 네트워크 추상화를 실제 CEC 성능으로 취급하지 않음 |
| 혼합 | AIR | 목록/대기열/경로/고도/링크 UI 구조는 재사용 가능. 내용은 MH-60R·APS-153·Hawklink이며 SOV용 항공 전투체계가 아님 |
| 혼합 | SENSORS 3D | 시각화 컨테이너는 공용. SPY/SPQ/Nav/SPG/APS 버튼과 빔 자료는 장비 provider로 교체해야 함 |
| 혼합 | DEBUG, HUD, MSL STATUS, SHIP 도면·장비 목록 | 표/로그/진입 구조는 공용. 테스트 미사일·사통 용어·셀/도면 데이터는 함정/장비별 공급 필요 |
| 혼합 | EMCON/EW shell | 레이더 방사 통제 정책은 공용. SLQ-32·Nulka·SRBOC 등 실제 장비 호출은 함정별 내용. 통신 EMCON은 여전히 별도 후속 항목 |

## 목표 구조와 규모

목표는 **공용 전술 지도 + 함정별 전투 패널 교체**다. 지도/viewport/선택·운용자 식별/항해/함대 shell은 유지하고, 프로파일 capability가 `sensorProviders`, `weaponProviders`, `combatPanelProvider`, `loadoutProvider`, `aviationFacility`, `saveCodecs`를 선택하게 한다. renderer와 물리 registration도 각자 provider를 선택하며 렌더 메시를 물리에 되먹이지 않는다.

예상 작업 단위(설계 추정이며 일정 약속 아님):

1. 비설치 장비 계약과 자함/NPC 결속 통일: 약 8–12개 초기화/registry 진입점. 0/없음은 실제 실행 안 함을 보장.
2. 출항 편성과 전투 UI provider 분리: 약 15–25개 주요 mount/update/bind 함수, 수백 개 기존 컨트롤의 소속 정리. 지도 전체 재작성은 불필요.
3. SOV 자함 geometry/interior/dynamics/renderer/2D 도면의 공용 registry 등록과 저장 codec 검증. 비무장 자함으로 우선 회귀 가능하게 설계.
4. 그 다음 러시아 센서·사통·무장 모듈을 독립 단계로 추가. 장비 물리·AI·권한·무장별 저장 migration은 위 shell 작업보다 큰 별도 범위.

1–3번은 대략 수십 개 진입 함수와 수천 행 규모의 재배치/adapter/검증이 예상된다. 정확한 변경 행수는 구현 설계 후 산정해야 한다. 현재 SOV의 npcOnly나 NO_EQUIPMENT guard를 풀어 기능이 생겼다고 취급하는 방식은 사용하지 않는다.
