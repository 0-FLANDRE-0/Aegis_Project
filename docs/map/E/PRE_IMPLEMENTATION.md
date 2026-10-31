# MAP_E 구현 전 보고

> 이 문서는 최초 조사 기록이다. 2026-10-31 사용자 결정은 [DECISIONS.md](DECISIONS.md)에 반영했다. 현재 구현·검수 상태는 STATE.md를 따른다.

- 기준: PR #57이 병합된 최신 main `7b9ca6e3e2d2dd26406b93c395d376f7f1b30c06`.
- 기준 HTML: MAP_D SHA-256 `5be55bdc1390d79f7b74bbfa5f128af916ffecdcf28693d0524578646955f40f` 확인.
- 작업 브랜치 `map-e`. 아직 게임 HTML/코드는 수정하지 않았다.
- 실제 출항 DOM을 조사했다. DDG ARM 내부 27개, CG 28개(버튼/선택/링크 포함). 원시 전수 목록: ARM_CONTROLS_BEFORE.tsv, evidence/arm-dom-before.json.

## 1. ARM 컨트롤 전수 표

| 기존 id / 요소 | 기존 기능 | MAP_E 대체 / 처리 | 상태 |
|---|---|---|---|
| armSubTargetBtn | TGT 하위 페이지 이동 | ARM 페이지 폐지, 지도 표적 정보/상황 메뉴 | 지시 범위 |
| armSubVlsBtn | VLS 하위 페이지 이동 | 하단 무장 선택·발사 슬롯 | 지시 범위 |
| armSubGunBtn | GUN 하위 페이지 이동 | 하단 5in 선택·MAP_D 태그 | 지시 범위 |
| armSubEwBtn | EW 하위 페이지 이동 | EMCON/ECM 팝오버·기만체 팝업 | 지시 범위 |
| lockBtn | 비 EMCON 정밀추적 / EMCON 방사 없는 지정 | 비 EMCON은 지도 정밀추적. EMCON 지정은 현재 대체 없음 | 사용자 결정: 새 UI 유보·내부 기능 보존 |
| autoEngBtn | AUTO TGT → autoEngageLock | UI 삭제, 함수 유지 | 명시적 제거 지시 |
| engCtrlBtn | MAN/SEMI/AUTO 전환 | 하단 MAN 칩 메뉴 | 있음 |
| trackIdentityBtn | 선택 트랙 ID 순환 | 지도 ID 변경 메뉴 | 있음 |
| fireBtn | 선택 SAM 발사 | MAP_B 하단 발사 슬롯 | 있음 |
| missileSelectSm2Btn | SM-2MR 선택 | 하단 SM-2MR 칸 | 있음 |
| missileSelectSm2ErBtn | SM-2ER 선택 | 하단 SM-2ER 칸 | 있음 |
| missileSelectSm6Btn | SM-6 선택 | 하단 SM-6 칸 | 있음 |
| missileSelectEssmBtn | ESSM 선택 | 하단 ESSM 칸 | 있음 |
| harpoonFireA | 하푼 발사 | MAP_D RGM-84 선택·발사 슬롯 | 있음 |
| harpoonRouteE | 경로 편집 | MAP_D [경로], AIM 의존 제거 | 있음 |
| harpoonControlsA 내부 출처 링크(id 없음) | Civorsky / CC BY 4.0 출처 | 같은 링크 노드를 DEBUG 출처 영역으로 이동, CREDITS.md 유지 | 이동 |
| cg52GunSelect (CG만) | 함수/함미 포를 수동 선택 | MAP_D는 2문 자동이며 동일 기능이 아님 | 사용자 승인: 개별 UI 폐기·자동 2문 유지 |
| mainGunCueBtn | 선택 포 CUE | 5in 선택 후 수상 트랙 탭 | 있음(자동 마운트 경로) |
| mainGunFireBtn | 선택 포 단발/보류 취소 | MAP_D 발사 슬롯 | 있음(자동 마운트 경로) |
| mainGunContinuousBtn | 선택 포 연속 시작/중지 | MAP_D 연속/중지 | 있음(자동 마운트 경로) |
| mainGunAmmoBtn | 선택 포 HE/SAP | 하단 5in 탄종 메뉴 | 있음(자동 마운트 경로) |
| emconBtn | 레이더 EMCON 토글 | EMCON 팝오버 레이더 ON/OFF | 있음 |
| chaffBtn | deployOwnChaff | 하단 SRBOC 팝업 | 있음 |
| nulka15bBtn | nulkaFire15B(softKillPrimaryThreat()) | 하단 Nulka 팝업 | 있음 |
| softKillAutoBtn | 기존 SK AUTO | ECM 전체 자동 / 끔 | 있음 |
| noiseJamBtn | 잡음 재밍 승인 토글 | 수동 UI 삭제, JAM/FULL에서 기법 승인 | 명시적 정책 변경 |
| deceptJamBtn | 기만 재밍 승인 토글 | 수동 UI 삭제, JAM/FULL에서 기법 승인 | 명시적 정책 변경 |
| armsBtn | 무장 현황 표시 | 같은 버튼을 + 메뉴 항목으로 이동, armsPanel / drawArmsPanel 재사용 | 이동 |

ARM 밖의 `modeAimBtn`은 창 목록 안에 있다. 이 탭 UI도 제거하되 내부 setInputMode/inputMode와 함수는 유지한다.

### 별도 확인을 요청한 버튼

| id | 실제 위치 | 조치 |
|---|---|---|
| scenarioModeBtn | DEBUG | 그대로 유지 |
| newSeaBtn | DEBUG | 그대로 유지 |
| resetBtn | DEBUG | 그대로 유지 |
| debugSpawnKh35Btn | DEBUG | 그대로 유지 |
| debugSpawnKh32Btn | DEBUG | 그대로 유지 |
| debugToggle | DEBUG | 그대로 유지 |
| missileSelect*Btn 4개 | ARM/VLS | UI 제거, 선택 함수 유지, 하단 무장 칸으로 대체 |

### 아직 동등한 대체가 없는 2건

1. `cg52GunSelect`: 선택한 한 포만 CUE/발사하는 레거시 흐름은 MAP_D의 자동 2문 흐름과 다르다. 자동 2문만 남기려면 수동 선택 UI 폐기를 명시해야 한다. 보존하려면 selector 하나만 옮겨서는 부족하고, 선택 포의 CUE/탄종/단발/연속 조작 묶음까지 DEBUG 등에 남겨야 한다.
2. EMCON 중 수동 지정: `lockByCursor(id)`는 EMCON에서 selectedLockId만 지정하고 PD/방사를 시작하지 않는다. 반면 현재 `mapPrecisionReasonA`는 EMCON이면 정밀추적을 거부한다. 따라서 현재 지도 정밀추적만으로 이 기능을 대신할 수 없다. 정밀추적 금지는 유지한 채 별도 [방사 없는 지정]을 추가하거나, 이 레거시 UI 기능도 폐기한다는 결정이 필요하다.

2026-10-31 결정 수신: CG 개별 조작 UI를 폐기하고 자동 2문을 유지한다. EMCON 방사 없는 지정은 내부 기능을 보존하고 새 UI 배치는 후속 작업으로 남긴다. 결정에 따라 ARM 제거를 진행했다.

## 2. NJ/DJ 승인 플래그의 기존 의미

- 실제 소스에 `OPERATOR TECHNIQUE REQUESTS, not independent full-power transmitters`라고 명시돼 있다.
- `slq32EaTargetForCurrentThreat`와 `updateSlq32EaAllocator`가 기법별 share를 정한다. 기본 autoAim에서 위협 큐가 없으면 STANDBY/자원 0이다.
- JAM/FULL은 두 기법을 승인할 뿐 상시 송신을 강제하지 않는다. 기존 EA 스케줄·기법 선택·위협 평가는 유지한다.
- 새 조작은 기존 own `electronicCommandF`와 setSoftKillAutoDoctrine 경로를 사용하고, OFF는 두 승인 플래그와 SK AUTO를 끈다. 자동 단계를 선택할 때 기존 자동 조준 경로를 사용한다.

## 3. 자동 기만체 경로와 NPC 격리

- 자함 채프: `updateSoftKillDoctrine`의 `softKillDoctrineChaffCandidate` → `deployOwnChaffForThreat(...,{automatic:true})` 부분에 FULL 조건을 추가한다.
- 자함 Nulka: 최상위 `nulkaAuto15B`의 자동 진입 조건에 FULL을 추가한다.
- NPC는 `createElectronicContextF` 안의 별도 lexical soft-kill/Nulka 커널을 사용한다. 이 복사본과 `electronicF` 설정·EA allocator는 변경하지 않는다. 소스 정적 비교와 동일 시드 실행으로 확인한다.
- 수동 `deployOwnChaff` / `nulkaFire15B`에는 ECM 단계 조건을 추가하지 않는다.
- SRBOC는 위협이 없어도 기존 함수가 함 침로로 수동 발사를 허용한다. 새 UI가 임의의 ‘위협 없음’ 차단을 추가하지 않는다. Nulka는 기존 cue 검사를 그대로 따른다.

## 4. 단계 저장과 기존 설정 호환

- 게임 저장 스키마와 항목은 추가하지 않는다. JAM/FULL 구분은 현재 자함의 임시 조작 상태로 둔다.
- reset/load/기존 SK AUTO 명령 뒤에는 기존 플래그에서 OFF/FULL을 추론한다. **JAM 상태를 저장했다가 불러오면 FULL로 추론**한다(지시서의 허용된 fallback).
- 기존 세이브의 수동 NJ/DJ 승인 플래그는 임의로 지우지 않는다. 현재 값은 읽기 전용으로 정확히 표시하고, 새 ECM 단계 선택 시 해당 3단계 요청값으로 바꾼다. 수동 NJ/DJ 선택 UI는 만들지 않는다.
- 전체 방사 OFF/ON용 ‘직전 단계’ 기억도 게임 저장에 넣지 않는다. Hawklink/Link16 통신 정책은 변경하지 않는다.

## 5. UI/입력·권한 변경 범위

- 하푼 지도 미리보기와 큐 호출 인자만 MANUAL로 바꾼다. native harpoonGate/ROE/거리/나이/INS/손상/쿨다운과 H3 본체는 변경하지 않는다.
- 편집 상태의 AIM 탭 조건을 UI 입력 판정에서 분리한다. 새 [경로]는 toggle 함수를 직접 호출하고, MAP_A의 HARPOON_INS가 우선한다. 필요하면 기존 입력 모드에서도 편집 중 경로 탭 우선순위만 일치시킨다.
- 레거시 버튼 참조가 필요한 UI 갱신/시험은 분리된 노드 참조 또는 동일 내부 함수 어댑터로 유지한다. 제거한 DOM을 검사 중 다시 붙이거나 검사 항목을 없애지 않는다.
- 비행 지문 281개/ENV_D/EA·NPC 커널 보존, 변경 예외 함수를 전부 명시하고 기본 120초 해시를 비교한다.

## 6. 검증·제출

기존 전체 회귀와 E1–E7을 최종 HTML에서 검증한다. 과거 ARM 버튼 의존 검사는 준비 경로만 옮기고 목록을 남긴다. HTML ZIP / 보고서 ZIP / 체크섬을 분리해 map-e에 push하고 원격 readback 후 PR만 연다. main 병합·release·tag·CI 변경은 하지 않는다.
