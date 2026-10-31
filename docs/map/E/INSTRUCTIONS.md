# MAP_E 지시서: 레거시 ARM 패널 제거, EMCON/ECM 팝오버, 기만체 발사, 하푼 수동 권한 보정

## 0. 기준과 산출물

- **기준**: `map-d` (커밋 `04348a14`, PR #57). PR #57이 main에 병합됐으면 main 최신 커밋을 기준으로 하고 보고서에 SHA를 기록한다.
- **기준 파일**: `Aegis_SIM_v48_WIP_MAP_D.html` (SHA-256 `5be55bdc1390d79f7b74bbfa5f128af916ffecdcf28693d0524578646955f40f`)
- **작업 브랜치**: `map-e`. main 병합, release, tag 금지. PR만 열고 병합은 사용자가 한다.
- **커밋 작성자 이메일**: `110261808+0-FLANDRE-0@users.noreply.github.com`
- **산출물**: `Aegis_SIM_v48_WIP_MAP_E.html`, `docs/map/E/`. 구성은 MAP_D와 같다(HTML ZIP / 보고서 ZIP 분리, 원격 readback).
- **성격**: UI 정리가 중심이다. 시뮬 로직 변경은 **§3의 ECM 자동 단계 조건 1개**와 **§5의 하푼 지도 경로 권한 인자**만 허용한다. 그 외 비행·유도·센서·탄도·발사 관문·사거리표·저장 스키마는 바꾸지 않는다.

## 1. 레거시 ARM 패널 제거

- 제어 데크의 **ARM 탭(`modeAimBtn`)과 ARM 페이지(TGT/VLS/GUN/EW 하위 탭 포함)를 UI에서 제거**한다.
- 버튼이 호출하던 **함수는 삭제하지 않는다**: `autoEngageLock`, `cycleTrackOperatorIdentityA3`, `wip13cSelectVlsWeapon`, `harpoonRequestFireA`, `mainGun.*`, `deployOwnChaff`, `nulkaFire15B`, `setSoftKillAutoDoctrine` 등.
- **대체 경로** (이미 있음, 동작 유지):

| ARM 기능 | 대체 경로 |
|---|---|
| LOCK | 지도 표적 메뉴 `정밀추적` |
| ID 지정 | 지도 표적 메뉴 `ID 변경` |
| CTRL MAN | 하단 `MAN` 칩 |
| VLS 무장 선택·FIRE | MAP_B |
| 하푼·웨이포인트, MK45 | MAP_D |
| EMCON | §2 팝오버 |
| SRBOC·Nulka | §4 |
| SK AUTO·NJ·DJ | §2·§3 |

- **AUTO TGT는 UI에서 제거**한다. `autoEngageLock` 함수는 남긴다.
- **ARMS STATUS**(`armsBtn` / `armsPanel`)는 맨 오른쪽 `+` 창 추가 메뉴의 항목으로 옮긴다. 기존 패널 그리기 함수를 재사용한다.
- **하푼 경로 편집이 AIM 탭에 의존하지 않게** 바꾼다. MAP_D는 기존 AIM 버튼 경로로 편집을 켜서 ARM 창이 함께 열렸다. 이번에는 `[경로]` 버튼이 `harpoonRouteToggleE()`를 직접 호출하고, 탭 라우팅은 MAP_A의 `HARPOON_INS` 우선 규칙으로 동작하게 한다. 편집 중 ARM 창이나 다른 창이 자동으로 열리면 안 된다.
- `setInputMode('AIM')`, `inputMode`, `lockCursor` 등 내부 상태와 함수는 남긴다. UI 진입점만 없앤다.
- **구현 전 보고 필수**: ARM 페이지 DOM에 들어 있는 모든 컨트롤을 전수 목록화하고, 각각이 위 대체 경로로 커버되는지 표로 보고한다.
  - 특히 `scenarioModeBtn`, `newSeaBtn`, `resetBtn`, `debugSpawnKh35Btn`, `debugSpawnKh32Btn`, `debugToggle`, `missileSelect*Btn`이 ARM 페이지 안에 있는지 확인한다.
  - 시나리오·리셋·디버그 생성 버튼이 ARM 안에 있으면 삭제하지 말고 DEBUG 탭으로 옮긴다.
  - 대체 경로가 없는 기능이 나오면 구현하지 말고 보고한다.

## 2. EMCON 팝오버

하단 바 `EMCON` 칩(`#uiEmconChipA`)을 누르면 칩 바로 위에 작은 팝오버가 뜬다. 스타일과 배치는 기존 `MAN` 칩 메뉴(`#uiModeMenuA`)를 따른다.

```
[ 전체 방사 ON / OFF ]
[ 레이더 ON / OFF ]
ECM:  [ 끔 ] [ 재밍 자동 ] [ 전체 자동 ]
```

- **레이더 ON/OFF**: 기존 `toggleEmcon`(`emconActive`)을 그대로 쓴다. 지금 EMCON은 레이더 방사만 끄며, 재머는 별개다.
- **ECM 3단계**(§3):
  - `끔`: 재밍·기만체 자동 모두 끔
  - `재밍 자동`: 잡음/기만 재밍을 자동 교리가 운용
  - `전체 자동`: 재밍 자동 + Mk 36 채프·Nulka 자동 발사. 기존 SK AUTO와 같은 동작
- **전체 방사 OFF**: 레이더 OFF + ECM `끔`으로 전환한다. 직전 ECM 단계는 기억해 둔다.
- **전체 방사 ON**: 레이더 ON + 기억한 ECM 단계로 복원한다. 기억한 단계가 없으면 `끔`으로 둔다.
- **수동 잡음/기만 재밍 선택 UI는 만들지 않는다.** 재밍은 자동으로만 운용한다.
- **칩 표시**: 레이더와 ECM 상태를 짧게 보여준다(예: `EMCON OFF · ECM 자동`). MAP_C의 고정 폭 규칙을 지켜서, 상태가 바뀌어도 바 요소 위치가 변하면 안 된다.
- 팝오버 바깥을 탭하거나 다시 칩을 누르면 닫힌다. 팝오버 버튼 터치 영역은 28px 이상으로 한다.

## 3. ECM 자동 단계 (시뮬 로직 변경 허용 범위)

- 기존 `softKillAutoDoctrine`는 켜지면 EA 시분할(이미 승인된 SLQ-32 기법), Mk 36 채프, Nulka 자동을 함께 운용한다. 이 동작은 `전체 자동`과 같다.
- `재밍 자동`을 위해 자함 전용 단계 값(예: `ownEcmAutoLevelE ∈ {OFF, JAM, FULL}`)을 추가하고, **기존 채프 자동 발사 경로와 `nulkaAuto15B`에 "단계가 FULL일 때만 발사" 조건 하나만** 추가한다. EA 스케줄링, 위협 평가, 기법 선택 로직은 바꾸지 않는다.
- 단계별 상태 매핑:
  - `OFF`: `softKillAutoDoctrine=false`, `noiseJamActive=false`, `deceptJamActive=false`
  - `JAM`: `softKillAutoDoctrine=true`, 잡음·기만 기법 둘 다 승인(`noiseJamActive=true`, `deceptJamActive=true`), 기만체 자동 발사 억제
  - `FULL`: `JAM`과 같고 기만체 자동 발사 허용
- 자동 교리가 어떤 기법을 언제 쓸지는 기존 로직이 판단한다. 승인 플래그는 "사용 가능"의 의미이며, 항상 송신한다는 뜻이 아니다. 구현 전 보고에 기존 의미를 확인해서 적는다.
- **다른 함정(multiship AI·NPC)의 `electronicF` 설정과 동작은 바꾸지 않는다.** 새 단계 값은 자함에만 적용한다.
- 저장: 기존 저장 항목(`softKillAutoDoctrine` 등)은 그대로 둔다. 새 단계 값을 저장할지는 기존 스키마를 바꾸지 않는 방법으로 정하고 보고한다. 바꾸지 않을 수 없다면 저장하지 않고, 불러온 뒤 기존 플래그에서 단계를 추론한다(SK AUTO 켜짐 → FULL).

## 4. SRBOC·Nulka 하단 바 발사

- 하단 재고 바의 `SRBOC`, `Nulka` 칸을 누르면 칸 바로 위에 작은 `발사` 버튼이 뜬다. MAP_B 발수 메뉴와 같은 위치·스타일이다.
- `발사`를 누르면 바로 쏜다. 재확인은 없다.
  - SRBOC: 기존 `deployOwnChaff()`
  - Nulka: 기존 `nulkaFire15B(softKillPrimaryThreat())`
  - 기존 함수가 거부하면(탄 없음, 재장전, 위협 없음 등) 기존 사유를 표시하고 버튼을 비활성 처리한다.
- 이 팝업은 **일시적**이다. 현재 선택된 무장(SAM/RGM-84/5in)과 표적 선택을 바꾸지 않는다. 팝업 바깥을 탭하면 닫힌다.
- ECM 단계와 무관하게 수동 발사는 항상 가능하다(기존 동작과 같음).
- 발사 명령은 기존 함수가 처리하는 방식을 따른다. 렌더/그리기에서 호출하지 않는다.

## 5. 하푼 지도 경로 수동 권한 보정

- MAP_D의 지도 하푼 경로는 `harpoonRequestFireA(..., {mode: engagementControlMode, ...})`로 현재 대공 교전 모드를 넘긴다. 그래서 AUTO/SEMIAUTO일 때 `MANUAL_SURFACE_AUTHORITY_REQUIRED`로 거부된다.
- 대함 발사는 대공 교리 모드와 무관한 **운용자 수동 발사**이므로, 지도 경로(미리보기와 실제 큐 모두)는 `mode: 'MANUAL'`로 호출한다. 함포 경로가 이미 이렇게 하고 있다.
- 식별 권한, 트랙 나이, 거리, INS 바스켓, 손상, 쿨다운 등 다른 관문은 그대로다.
- H3 AI 경로(`attackAuthorityH3`)와 수동 경로 우선 규칙은 바꾸지 않는다.

## 6. 보존 조건

- 표적 truth, entity, 적 배열, RF 물리 객체를 새 UI에서 읽지 않는다.
- 비행 지문 281개, 기존 최상위 함수·상수(이번 변경 예외 목록 제외), `ENVELOPE_TABLE_D` 120행 byte 동일.
- 120초 무표적·전투 truth 해시는 MAP_D와 동일해야 한다. 기본 ECM 단계가 기존 기본값(SK AUTO 꺼짐)과 같아야 한다.
- MAP_B/C/D의 교전 흐름, 태그, 발사 슬롯, 탭 선택 규칙은 그대로 유지한다.

## 7. 검수

**기존 회귀**: 도메인 420, UI 88, MAP_B 91, 경고 23, 추가 13, MAP_C 전체, MAP_D(native 84 / UI 213 / 경계 145), EMCON UI, network-only, 종료기 300발, 자연 WebGL 8발, world120, 하푼·함포 기존 진단, 소프트킬·Nulka·SRBOC 기존 도메인 검사.

ARM 버튼을 누르던 기존 검사는 **같은 내부 함수를 호출하는 test-only 어댑터나 새 UI 경로로 준비만 이관**한다. 검사 항목은 삭제하지 않으며, 이관 목록은 보고서에 남긴다.

**신규** (1400×900, 832×384, 2D 주화면과 3D+PiP, DDG와 CG 각각):

| 항목 | 기준 |
|---|---|
| E1 ARM 제거 | ARM 탭·페이지·AUTO TGT DOM 없음. 전수 목록의 모든 기능에 대체 경로가 있음. DEBUG·시나리오 기능 접근 가능. ARMS STATUS가 `+` 메뉴에서 열림 |
| E2 팝오버 | 전체 방사 OFF/ON 시 레이더와 ECM 단계 저장·복원. 레이더 단독 토글. 칩 폭 고정으로 바 박스 변화 0px. 바깥 탭 시 닫힘 |
| E3 ECM 단계 | OFF/JAM/FULL 각각에서 다중 위협 시나리오 실행. JAM에서 채프·Nulka 자동 발사 0발 + EA 동작. FULL에서 기존 SK AUTO와 같은 결과(같은 시드에서 발사 기록 일치). OFF에서 자동 EA·기만체 0. 타 함정 설정 불변 |
| E4 기만체 수동 | SRBOC·Nulka 팝업 발사가 기존 함수 결과와 일치. 거부 사유 표시. 현재 무장·표적 선택 불변 |
| E5 하푼 권한 | AUTO/SEMIAUTO/MANUAL 각 모드에서 지도 하푼 발사 가능(다른 관문 동일). 보호 식별 거부 유지. H3 AI 경로 결과 불변 |
| E6 경로 편집 | 편집 시작·종료 중 창 자동 열림 0. 빈 바다 탭은 경유점이 되고 함 항로점 증분 0 |
| E7 레이아웃 | 832×384에서 팝오버·팝업이 화면 안. 터치 영역 기준 충족 |

## 8. 범위 밖

- 3D 기본 화면 전환, 2D 주화면일 때의 3D PiP
- CG-52 Mk45 Mod 2 제원 보정
- SOV_B1(TMA)·SOV_B2(소브레멘니 센서)
- 사거리표 문제, `aegis-smoke.yml` 갱신

## 9. 진행 순서

1. **구현 전 보고**: ARM 컨트롤 전수 표, NJ/DJ 승인 플래그의 기존 의미, 채프·Nulka 자동 발사 경로 위치, ECM 단계 저장 방식
2. 구현
3. 회귀·신규 검수
4. `docs/map/E/` 산출 → `map-e` push → 원격 readback → PR 생성(병합은 사용자)
