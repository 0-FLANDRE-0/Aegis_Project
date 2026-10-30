# MAP_D 지시서: 하푼·Mk45 함포를 지도 교전 흐름에 연결

## 0. 기준과 산출물

- **기준**: `main` (커밋 `9f8e77f9`, PR #56 병합). MAP_C와 CREDITS.md가 포함되어 있다.
- **기준 파일**: `Aegis_SIM_v48_WIP_MAP_C.html` (SHA-256 `84fa5df960772cdb9c9904310ca7af752e3cedae025fd864dc1b27a9de6f8d7b`)
- **작업 브랜치**: `map-d` (main에서 분기). main 병합, release, tag는 만들지 않는다. PR을 열면 사용자가 직접 병합한다.
- **산출물**: `Aegis_SIM_v48_WIP_MAP_D.html`. 보고서·검증 자료는 `docs/map/D/`에 둔다. 구성은 MAP_C와 같다(HTML ZIP과 보고서 ZIP 분리, 원격 readback 체크섬 기록).
- **커밋 작성자 이메일**: GitHub noreply 주소 `110261808+0-FLANDRE-0@users.noreply.github.com`를 쓴다. 레포가 공개 상태다.
- **작업 성격**: UI/입력 연결만 한다. 하푼 비행·시커·INS, 함포 탄도·사격해·사통 품질, 발사 관문·권한, 사거리표, 저장 스키마는 바꾸지 않는다.

## 1. 현재 구조 (구현 전 반드시 확인)

**하푼** (`harpoon*A/C/D/E`)
- 트랙 발사: `harpoonRequestFireA(trackId)` → `harpoonAutoTubeGateD` → `harpoonGateA`
  - 식별 권한, 트랙 나이(≤10 s), 발사거리 4~140 km, INS 예측 σ ≤ 포착 바스켓 4 km를 검사한다.
  - 한 번 호출에 한 발이 나간다. 문 열림 지연(0.18 s)과 `releaseIntervalS` 쿨다운이 있다.
- 좌표 탐색 발사: `harpoonRouteToggleE` / `harpoonRouteAddE` / `harpoonRouteGateE`
  - 경유점 최대 8개, 간격 2 km 이상, 마지막 점에서 8 km 앞이 탐색 중심이다.
  - 발사 시 `routeDraft`는 초기화된다. 같은 경로로 여러 발을 쏘려면 `options.routeProgram`으로 고정 프로그램을 넘긴다(`harpoonRequestFireA(trackId,null,{routeProgram})`).
- AUTO/SEMIAUTO 모드에서는 거부되고 수동 권한만 허용된다(H3 AI 경로는 별도).

**Mk45** (`ACTIVE_SHIP_RUNTIME.weapons.mainGun`)
- `command(trackId, ammoId)`: 사격해 계산(CUE)
- `requestFire(trackId, {mode:'MANUAL', ammoId})`: 단발. 정렬될 때까지 보류(hold)하며, 보류 중 다시 호출하면 취소된다.
- `startContinuousFire` / `stopContinuousFire`: 연속 사격
- `selectAmmo('HE_127_SIM'|'SAP_127_SIM')`: 탄종 선택
- 사통 품질 `solution.fireControlTrackQuality`: `status`가 `FCQ_READY` / `FCQ_DEGRADED`이고 `firePermitted`로 허용 여부를 판단한다.
- 수상 표적, 수동 권한 전용이다.
- 사통 한계(`fireControl.minRangeM` / `maxRangeM`): DDG Mod 4 = 0.8 / 24 km, CG-52 Mod 2 = 0.8 / 22 km
- CG-52는 `weapons.gunMounts`(함수/함미 2문)와 `selectedGunId`를 쓰고, 사계 판정은 `bunkerGunClearance`가 한다.

기존 ARM 패널의 버튼(`harpoonFireA`, `harpoonRouteE`, `mainGunCueBtn` / `FireBtn` / `ContinuousBtn` / `AmmoBtn`, `cg52GunSelect`)은 **삭제하지 않는다.**

## 2. 하단 바 무장 선택 확장

- 재고 바의 `RGM-84`와 `5in` 칸을 MAP_B의 SAM 칸처럼 선택할 수 있게 한다. 그 밖의 칸(Nulka, SRBOC, HELO, CIWS 계열)은 선택 대상이 아니다.
- 선택 규칙은 MAP_B/C와 같다. 재클릭이나 바의 빈 곳을 누르면 해제되고, 다른 무장을 확정하기 전까지 이전 선택이 유지된다. 선택 상태가 바뀌어도 바 요소 위치는 변하지 않아야 한다(MAP_C C4 불변식 유지).
- **RGM-84 메뉴**: 발수 `1 / 2 / 3 / 4`. 장전된 발사관 수 기준으로 비활성화한다.
- **5in 메뉴**: 탄종 `HE / SAP` + 사격 방식 `단발 / 연속`. 탄종을 고르면 기존 `selectAmmo`를 호출한다. 탄종 전환이 거부되면 기존 사유를 표시한다.

## 3. 하푼 흐름

**링** (자함 중심, 사거리표 측정 없음)
- 최소 4 km 실선, 최대 140 km 점선. 값은 `HARPOON_PROFILE_A.sim`에서 읽는다.
- 라벨 스타일은 MAP_C 링 라벨(9px)을 따른다.

**트랙 발사**
- 무장 선택 후 수상 트랙을 탭하면 MAP_C 미니 태그에 판정을 표시한다.
- 판정은 기존 `harpoonAutoTubeGateD(trackId)`의 결과를 **부작용 없이** 미리보기로 실행해 얻는다(MAP_B의 native preview 원칙과 같음. 상태를 쓰는 함수는 호출하지 않는다).
  - 초록: `ok`
  - 빨강: 거부 사유. 기존 reason 코드를 짧은 한글로 표시한다. 예: `NO_TRACK` 트랙 없음, 식별 권한 사유, `SURFACE_TRACK_COAST_EXPIRED` 트랙 노후, 거리 사유, `INS_PREDICTION_BASKET_INSUFFICIENT` INS 예측 범위 초과, `TUBE_EMPTY` 탄 없음, `MK141_LAUNCHER_DAMAGED` 발사기 손상
  - 하푼에는 주황 단계를 새로 만들지 않는다.
- 항공 트랙을 탭하면 빨강 `수상 표적 전용`으로 표시한다.
- **발사**: MAP_B/C의 하단 발사 슬롯(`#mapFireB`)을 쓴다. 클릭하면 운용자 명령 큐에 N발을 넣는다.
  - fixed tick에서 이전 발의 `pending`이 해제되고 쿨다운이 끝날 때마다 `harpoonRequestFireA(trackId)`를 한 번씩 호출한다.
  - 각 발마다 기존 관문을 다시 검사한다. 거부되면 남은 요청을 중지하고 사유를 기록한다(MAP_B 큐 규칙과 같음).
  - 슬롯 표시는 `발사 ×N`, 진행 중이면 `발사 중 k/N`.

**좌표 탐색 발사 (경로 편집)**
- RGM-84를 선택하면 미니 태그(표적 없을 때는 바 근처 작은 칩)에 `[경로]` 버튼을 둔다.
- 누르면 기존 `harpoonRouteToggleE()`로 편집을 시작하고, 지도 상단에 `하푼 경로 편집 중 · n/8` 띠를 표시한다.
  - 편집 중에는 메인·PiP의 **빈 바다 탭**이 함 항로점이 아니라 `harpoonRouteAddE`가 된다. 기존 간격·개수 거부 메시지를 그대로 쓴다.
  - 객체 탭(트랙 선택)은 기존대로 동작한다.
  - 편집 중 함 통제 전환 금지(MAP_C C6)는 유지한다.
- 경로 선과 탐색 중심(마지막 점 + 8 km)을 지도에 표시한다. 기존 경로 그리기가 있으면 재사용한다.
- 경로가 1점 이상이면 발사 슬롯은 경로 모드가 된다(`발사 ×N · 경로`).
  - 클릭 시 `harpoonRouteProgramE`로 **프로그램을 한 번 고정**하고, N발 모두 `harpoonRequestFireA(trackId, null, {routeProgram})`로 같은 경로를 쓴다.
  - 선택된 트랙이 보호 식별이면 기존 관문이 거부한다.
- `[경로]`를 다시 누르면 편집을 종료하고 기존 동작대로 초안을 지운다.
- **후속 작업(SOV_B1) 연결점**: 경로 초안에 좌표 하나를 넣는 내부 함수(예: `mapDHarpoonSetSearchPoint(xM,yM)`)를 두고, 기존 `harpoonRouteAddE` 규칙을 그대로 적용하게 한다. 이번 작업에서는 UI 진입점 없이 함수만 둔다.

## 4. Mk45 함포 흐름

**링**: 최소 0.8 km 실선, 최대 실선/점선. 각 함의 `fireControl.maxRangeM`을 쓴다(DDG 24 km, CG-52 22 km). 값은 수정하지 않는다.

**표적 선택**
- 5in을 선택하고 수상 트랙을 탭하면 기존 `command(trackId, loadedAmmoId)`를 호출해 사격해를 계산한다. 운용자의 명시적 지정이므로 실제 CUE 명령으로 취급한다.
- 미니 태그에는 사통 품질을 색으로 표시한다.
  - `FCQ_READY` + `firePermitted`: 초록
  - `FCQ_DEGRADED` + `firePermitted`: 주황
  - `firePermitted=false` 또는 사격해 실패: 빨강 + 기존 reason
- 2줄째에 TOF와 거리를 표시한다.
- 항공 트랙: 빨강 `수상 표적 전용`

**발사 슬롯**
- 단발: `발사` → `requestFire(trackId, {mode:'MANUAL', ammoId})`
  - 보류 중이면 `정렬 대기 n.n s`를 표시하고, 다시 누르면 기존 동작대로 취소된다.
  - 사이클 중이면 `n.n s`를 표시한다.
- 연속: `연속 사격` → `startContinuousFire`. 진행 중이면 `사격 중지` → `stopContinuousFire('OPERATOR_STOP')`
- 표적 `✕` 해제나 무장 해제 시 연속 사격 중이면 중지한다.

**CG-52 2문 자동**
- 5in 선택 + 표적 지정 시, 각 포(`gunMounts`)에 대해 기존 `command`를 호출한다.
- 사격해가 `ok`이고 사계(`bunkerGunClearance`)가 통과하는 포만 사격 대상이다. 발사 명령은 대상 포 모두에 같은 방식으로 내린다.
- 운용자가 포를 고르는 UI는 만들지 않는다. 태그에는 `2문` / `함수만` / `함미만` / `사계 없음`을 표시한다.
- 기존 `cg52GunSelect`와 `selectedGunId`의 의미는 바꾸지 않는다. 자동 경로는 각 마운트 런타임을 직접 호출한다. 이 방식이 기존 구조상 불가능하면 구현 전 보고에서 대안을 제시한다.
- DDG(1문)는 기존 `mainGun` 하나만 쓴다.

## 5. 보존 조건

- 표적 truth, entity, 적 배열, RF 물리 객체를 새 UI에서 읽지 않는다.
- 하푼·함포 발사는 기존 공개 함수만 호출한다. 렌더 함수에서 발사하거나 상태를 쓰지 않는다. 큐 디스패치는 fixed tick에서만 한다.
- SAM 흐름(MAP_B/C)과 그 검수 결과는 그대로 유지한다.
- `ENVELOPE_TABLE_D` byte 동일. 비행 지문 281개 변경 0. 120초 무표적·전투 truth 해시는 MAP_C와 동일해야 한다.
- 저장 스키마 변경 없음. UI 선택·큐·편집 띠 상태는 저장하지 않는다(기존 `routeDraft`는 기존 저장 규칙을 따른다).
- 기존 하푼 H3 AI(`attackAuthorityH3`)의 수동 경로 우선 규칙을 유지한다.

## 6. 검수

**기존 회귀**: 도메인 420, UI 88, MAP_B 91, 경고 23, 추가 13, MAP_C 신규(UI 135, 추종 73, 규칙 45, 링 33, DOM 13), network-only, 종료기 300발, 자연 관측 WebGL 8발, world120, 하푼 기존 검사(harpoon-f1, harpoon-clock 등), 함포 기존 진단(`wip13b1RunDiagnostics` 등). 위치가 바뀐 요소를 찾던 검사는 준비 경로만 이관하고 검사 항목은 삭제하지 않는다.

**신규** (1400×900, 832×384, 2D 주화면과 3D+PiP, DDG와 CG-52 각각):

| 항목 | 기준 |
|---|---|
| D1 바 | RGM-84·5in 선택/해제/메뉴. 선택·판정 변화 전후로 다른 바 요소 박스 변화 0px. 장전 수에 따른 발수 비활성 |
| D2 하푼 트랙 | 판정이 미리보기와 실제 관문에서 일치(사유 종류별 재현). 미리보기 전후 상태 변화 0. 1~4발 실제 발사, 발사관 자동 선택, 발 간격이 기존 지연·쿨다운 이상. 중간 거부 시 큐 중지 |
| D3 하푼 경로 | 편집 띠 표시. 빈 바다 탭이 경유점으로 들어감(2 km/8점 규칙). 함 항로점 0개 추가. N발이 같은 고정 프로그램 사용(탐색 중심 일치). 편집 종료 시 초안 삭제. `mapDHarpoonSetSearchPoint`가 기존 규칙 통과 |
| D4 함포 | 탭 → CUE. FCQ 색 매핑 3종 재현. 단발 보류/취소, 연속 시작/중지, 탄종 전환. 표적 해제 시 연속 중지. 링 값 DDG 24 km / CG-52 22 km |
| D5 CG-52 자동 | 표적 방위별로 2문/함수만/함미만/사계 없음 재현. 사계 밖 포 발사 0발. 포 선택 UI 없음 |
| D6 레이아웃 | 832×384에서 메뉴·띠·태그 화면 안. 터치 영역 ≥40px(발사)·≥28px(기타) |

스크린샷: 위 조건별 PC/폰 캡처를 남기고, 실제 WebGL 3D+PiP 캡처를 1장 이상 포함한다.

## 7. 범위 밖

- **CG-52 Mk45 Mod 2 제원 보정**(포구속도 823 → 5"/54 공개값 약 760 m/s, 사통 한계 재산정). 별도 작업으로 다룬다.
- 수동 위치 추정·TMA(SOV_B1), 소브레멘니 센서(SOV_B2)
- 사거리표 문제(SM-2MR 490 km, ESSM 구간 선택)
- `aegis-smoke.yml` 갱신. 이 워크플로는 옛 WIP 파일을 고정 대상으로 검사하므로, PR 체크가 실패해도 이번 작업 결과와 무관하다.

## 8. 진행 순서

1. **구현 전 보고**: 하푼 미리보기의 부작용 여부 확인, CG-52 자동 2문 호출 방식, 경로 편집 중 탭 라우팅 지점, 함포 CUE 해제 API 유무.
2. 구현
3. 회귀와 신규 검수 실행
4. `docs/map/D/`에 REPORT.md, STATE.md, 증거, 체크섬을 남긴다. `map-d`에 push한 뒤 원격 readback으로 확인하고, main 대상 PR을 연다(병합은 사용자가 한다).
