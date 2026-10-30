# UI 레이아웃 조사 — pointer:coarse / mobile — 디자인/배치 변경 없음

좌표는 CSS/client px의 `x,y,w,h`. 헤드리스 Chromium에서 직접 측정했다. `0×0`은 해당 조건에서 숨김/빈 컨테이너이며 수치가 없는 것으로 표시하지 않았다. 여러 조건의 UI를 동시에 열었다는 뜻이 아니다. 기본 상태와 조건부 DOM 공개 측정은 JSON에서 구별된다.

- 가장자리 패널은 **controlDeckPanel 하나(2D)**다. 좌우 span ≥90%, 보이는 하단 경계에 닿거나 경계 아래까지 덮는지 검사한다. 기존 4/6px 여백은 붙어 있는 것으로 본다.
- 3D의 전체 변을 덮는 dock는 현재 없다. 미니 CIC, MSL STATUS, 상단 바/퀵 교전/HUD, drawer/flyout은 떠 있는 위젯이다.
- 모달·출항 편성·카탈로그는 독립 작업 화면/조건부 overlay다. 지도의 visible 영역을 영구 축소하는 dock가 아니다.
- canvas로 그리는 SPY scheduler는 DOM id가 없다. 아래에 별도 기록했다.
- 스캔라인/비네트는 장식 레이어이고 영역을 줄이지 않는다. 숨겨진 armsPanel/debugPanel은 legacy 컨테이너다.

## 실제 사각형과 측면 도크 전환 검토

| id 또는 기존 selector | 분류 | 1400×900 | 1400×560 | 600×900 | 844×390 | 측면 도크 전환 / 걸리는 점 |
|---|---|---|---|---|---|---|
| (no id) #DIV>DIV:nth-child(3) | 떠 있는 위젯 | 966.88,666,154.12,9† | 966.88,463.59,154.12,9† | 434.88,666,154.12,9† | 673.98,300.39,154.12,9† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| (no id) #external3DView>DIV:nth-child(10) | 떠 있는 위젯 | 8,82,132.28,41† | 8,82,132.28,41† | 8,82,132.28,41† | 8,82,132.28,41† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| (no id) .external3d-toolbar.c14-topbar | 떠 있는 위젯 | 10,10,1380,45 | 10,10,1380,45 | 6,6,588,61 | 10,10,824,45 | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| (no id) .scanline | 장식 | 0,0,1400,900 | 0,0,1400,560 | 0,0,600,900 | 0,0,844,390 | 이동 대상 아님 |
| (no id) .vignette | 장식 | 0,0,1400,900 | 0,0,1400,560 | 0,0,600,900 | 0,0,844,390 | 이동 대상 아님 |
| airAltitudeDialogC | 독립 모달/overlay | 0,0,0,0 | 0,0,0,0 | 0,0,0,0 | 0,0,0,0 | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| apsPerformanceDialogF | 독립 모달/overlay | 0,0,900,640† | 0,0,900,476† | 0,0,562,640† | 0,0,793.36,331.5† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| armsPanel | 떠 있는 위젯 | 510,205.31,380,489.38† | 510,42,380,476† | 110,205.31,380,489.38† | 232,29.25,380,331.5† | legacy 호환 컨테이너; 실제 현재 컨트롤과 중복 배치 금지 |
| c14ControlsDrawer | 떠 있는 위젯 | 6,60,1388,196† | 6,60,1388,196† | 6,55,588,196† | 6,60,832,196† | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c14ControlsToggle | 떠 있는 위젯 | 10,10,86.02,42 | 10,10,86.02,42 | 6,6,86.02,42 | 10,10,86.02,42 | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c15CameraFlyout | 떠 있는 위젯 | 88,109,302,227† | 88,109,302,227† | 88,104,302,227† | 88,109,302,227† | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c15SensorsFlyout | 떠 있는 위젯 | 88,158,302,178† | 88,158,302,178† | 88,153,302,178† | 88,158,302,178† | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c15SystemFlyout | 떠 있는 위젯 | 88,60,302,129† | 88,60,302,129† | 88,55,302,129† | 88,60,302,129† | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c15WeaponFlyout | 떠 있는 위젯 | 88,207,302,129† | 88,207,302,129† | 88,202,302,129† | 88,207,302,129† | 가능. 메뉴/flyout의 앵커·닫기/포커스·부모 pointer-events·z-index 재설정 필요 |
| c5BuildBadge | 떠 있는 위젯 | 6,880,103.7,15 | 6,540,103.7,15 | 6,880,103.7,15 | 6,370,103.7,15 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| controlDeckPanel | 가장자리(2D) | 6,754,1388,140 | 6,414,1388,140 | 4,664.56,592,231.44 | 6,220,832,164 | 가능. 하단 bar/page 방향·미디어쿼리·장비 페이지 스크롤과 입력 차단 영역을 함께 설계해야 함 |
| damageControlPanelV1 | 떠 있는 위젯 | 914,-30,480,872† | 914,-30,480,532† | 4,12,592,802† | 358,-62,480,362† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| damageFloodPanelV1 | 떠 있는 위젯 | 1014,257,380,585† | 1014,138,380,364† | 4,12,592,802† | 458,46.5,380,253.5† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| debugPanel | 떠 있는 위젯 | 920,90,480,752† | 920,56,480,446† | 300,90,300,720† | 422,39,422,261† | legacy 호환 컨테이너; 실제 현재 컨트롤과 중복 배치 금지 |
| external3DLoading | 떠 있는 위젯 | 0,0,1400,900† | 0,0,1400,560† | 0,0,600,900† | 0,0,844,390† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| external3DMiniCic | 떠 있는 위젯 | 6,744,230,150 | 6,404,230,150 | 6,744,230,150 | 6,234,230,150 | 가능. canvas 고정 반경/클릭 변환·DPR·최소 가독 크기를 함께 유지 |
| external3DMissileStatus | 떠 있는 위젯 | 1144,852.34,250,41.66 | 1144,512.34,250,41.66 | 344,852.34,250,41.66 | 588,342.34,250,41.66 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| external3DQuickState | 떠 있는 위젯 | 1306.98,66.5,78.02,9 | 1306.98,66.5,78.02,9 | 0,0,0,0 | 750.98,66.5,78.02,9 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| external3DReadout | 떠 있는 위젯 | 626,10,156,45 | 626,10,156,45 | 252,6,104,61 | 348,10,156,45 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| external3DTerminalSummary | 떠 있는 위젯 | 1150,91,240,18† | 1150,91,240,18† | 350,118,240,18† | 594,91,240,18† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| external3dBtn | 떠 있는 위젯 | 6,6,76,28 | 6,6,76,28 | 4,4,76,28 | 6,6,76,28 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| harpoonJournalDialogF1 | 독립 모달/overlay | 260,163.5,880,573† | 260,87,880,386† | 24,163.5,552,573† | 33.77,48.75,776.47,292.5† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| hud | 떠 있는 위젯 | 6,40,196.02,61.95 | 6,40,205.62,61.95 | 6,38,205.62,61.95 | 6,40,196.02,61.95 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| isarPerformanceDialogF2 | 독립 모달/overlay | 250,141,900,618† | 250,73,900,414† | 19,141,562,618† | 25.31,39,793.36,312† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| shipDetailPanel | 떠 있는 위젯 | 1034,266,360,300† | 1034,-46,360,300† | 234,223,360,300† | 478,-240,360,300† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| shipSurvivalBannerV1 | 떠 있는 위젯 | 599.3,801,201.39,39† | 599.3,461,201.39,39† | 199.3,769,201.39,39† | 321.3,259,201.39,39† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| toastWrap | 떠 있는 위젯 | 520,836,360,0 | 520,496,360,0 | 120,804,360,0 | 242,294,360,0 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| wip125LoadoutOverlay | 독립 모달/overlay | 0,0,1400,900† | 0,0,1400,560† | 0,0,600,900† | 0,0,844,390† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| wip14a14QuickEngage3D | 떠 있는 위젯 | 1097.94,52,292.06,38 | 1097.94,52,292.06,38 | 415.97,52,178.03,37 | 541.94,52,292.06,38 | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| wip200CatalogCloseX | 독립 모달/overlay | 1091,18,30,30† | 1091,18,30,30† | 559,18,30,30† | 798.11,18,30,30† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| wip200CatalogLoading | 독립 모달/overlay | 149,66,980,615† | 149,66,980,412.59† | 149,66,448,615† | 149,66,687.11,249.39† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| wip200MissileCatalogBtn | 떠 있는 위젯 | 612.88,25,104.12,29† | 612.88,25,104.12,29† | 468.88,25,104.12,29† | 612.88,25,104.12,29† | 가능. 내용 길이·조건부 표시·고정 CSS anchor를 도크의 로컬 좌표로 교체 |
| wip200MissileCatalogOverlay | 독립 모달/overlay | 0,0,1400,900† | 0,0,1400,560† | 0,0,600,900† | 0,0,844,390† | 모달 유지, 진입 버튼만 도크. 포커스/ESC/복사·긴 표·VLS 셀 가독성 고려 |
| (canvas) drawSpySchedulerScreenOverlay | 떠 있는 위젯 | 520,6,360,151 | 520,6,360,151 | 150,6,300,151 | 272,6,300,151 | 가능. canvas overlay를 독립 panel renderer/anchor로 분리하되 scheduler 진단 읽기만 유지 |

† 진단에서 조건부 UI를 공개하여 얻은 위치. 기본 상태에서 떠 있다는 뜻은 아니다. `controlDeckPanel`은 탭별 높이가 다르므로 아래 표도 참조한다. 메시지/종말 결과/프로파일러 내용이 길어지면 위젯 높이가 달라질 수 있다. 이 표는 고정된 콘텐츠를 사용한 측정값이다.

## 하단 패널 탭별 크기

| 크기 | NAV | ARM | FLEET | AIR | DEBUG |
|---|---|---|---|---|---|
| 1400×900 | 6,754,1388,140 | 6,624.69,1388,269.31 | 6,487,1388,407 | 6,578,1388,316 | 6,564,1388,330 |
| 1400×560 | 6,414,1388,140 | 6,284.69,1388,269.31 | 6,166,1388,388 | 6,266.81,1388,287.19 | 6,224,1388,330 |
| 600×900 | 4,664.56,592,231.44 | 4,675.56,592,220.44 | 4,446,592,450 | 4,537,592,359 | 4,354.25,592,541.75 |
| 844×390 | 6,220,832,164 | 6,113,832,271 | 6,79.81,832,304.19 | 6,152.41,832,231.59 | 6,72,832,312 |

## 미디어쿼리 경계

| 조건 | 바꾸는 내용 |
|---|---|
| 641–980px | ARM 3열, EW 2칸·미사일 선택 3열 배치 |
| 641px 이상 & 높이 ≤520px | 하단 패널 최대 높이 확장, ARM 5열, 카드 padding/gap 축소, note 숨김 |
| ≤640px | dock 양옆/하단 4px, bar 2행/78px, NAV/DEBUG 재배치, ARM TGT/VLS/GUN/EW 하위 탭, HUD·3D 입력·damage·drawer·quick engage 크기 변경. AIR/FLEET의 동적 CSS도 포함 |
| 641–1000px | dock bar를 2행으로, utility를 다음 행 중앙으로. 980과 별개의 경계 |
| ≤700px | 손상/침수 패널의 폭·높이·safe area·터치 버튼 |
| pointer: coarse 또는 ≤640px | 3D 큰 터치 버튼/도구 모음, 미니 CIC 150px 높이와 내부 canvas 126px, MSL STATUS 46vw, help 숨김. 뒤쪽 C14/C15 규칙의 cascade도 작용 |
| prefers-reduced-motion | drawer/flyout 전환 애니메이션 제한; viewport/시뮬 시간 변경 없음 |

CSSOM의 조건과 실제 선언 전체를 아래에 남긴다. 원본 outer CSS bytes는 SOV_A와 동일하다.

```css
@media (min-width: 641px) and (max-width: 980px) {
  #controlDeckArmPage.active { grid-template-columns: repeat(3, minmax(0px, 1fr)); }
  #controlDeckArmPage.active > .arm-section[data-arm-group="EW"] { grid-column: 1 / span 2; }
  #controlDeckArmPage.active > .missile-selector { grid-column: 3; }
}
@media (min-width: 641px) and (max-height: 520px) {
  .control-deck { max-height: calc(100dvh - 12px); }
  #controlDeckArmPage.active { grid-template-columns: minmax(0px, 1.15fr) minmax(0px, 0.72fr) minmax(0px, 1.15fr) minmax(0px, 1.05fr) minmax(0px, 1fr); }
  #controlDeckArmPage.active > .arm-section[data-arm-group="EW"], #controlDeckArmPage.active > .missile-selector { grid-column: auto; }
  .control-deck-section { padding: 3px; gap: 2px; }
  .control-deck-note { display: none; }
}
@media (max-width: 640px) {
  :root { --control-dock-bar-h: 78px; }
  .control-deck { left: 4px; right: 4px; bottom: 4px; max-height: calc(100dvh - 46px); }
  .control-deck-bar { grid-template-columns: 1fr auto; grid-template-areas: "tabs damage" "utility utility"; gap: 4px 6px; padding: 4px; }
  .control-deck-tabs { grid-template-columns: repeat(3, minmax(48px, 1fr)); }
  .control-deck-tab { height: 32px; }
  .control-deck-utility { justify-content: center; overflow: visible; }
  .control-deck-damage { gap: 3px; }
  #controlDeckNavPage.active { grid-template-columns: repeat(2, minmax(0px, 1fr)); }
  #controlDeckNavPage.active > :first-child { grid-column: 1 / -1; }
  #controlDeckArmPage.active { grid-template-columns: repeat(2, minmax(0px, 1fr)); }
  #controlDeckArmPage.active > .control-deck-subtabs { display: grid; grid-template-columns: repeat(4, minmax(0px, 1fr)); grid-column: 1 / -1; }
  #controlDeckArmPage.active > .arm-section { display: none; grid-column: 1 / -1; }
  #controlDeckArmPage[data-arm-subtab="TARGET"].active > .arm-section[data-arm-group="TARGET"], #controlDeckArmPage[data-arm-subtab="GUN"].active > .arm-section[data-arm-group="GUN"], #controlDeckArmPage[data-arm-subtab="EW"].active > .arm-section[data-arm-group="EW"] { display: flex; }
  #controlDeckArmPage[data-arm-subtab="VLS"].active > .arm-section[data-arm-group="VLS"] { display: flex; grid-column: auto; }
  #controlDeckDebugPage.active { grid-template-columns: repeat(2, minmax(0px, 1fr)); }
  #controlDeckDebugPage.active > :last-child { grid-column: 1 / -1; }
  .control-deck-page { gap: 4px; padding: 4px; }
  .control-deck-section { max-height: none; padding: 4px; gap: 3px; }
  .external-3d-entry { left: 4px; top: 4px; }
  .hud-status { top: 38px; max-width: 72vw; }
  .control-deck .compass-hud { display: none; }
  #controlDeckArmPage .missile-panel { max-height: 44px; }
}
@media (pointer: coarse), (max-width: 640px) {
  .external3d-btn { min-height: 44px; padding: 8px 12px; font-size: 10px; }
  .external3d-toolbar { left: 6px; right: 6px; top: 6px; gap: 5px; align-items: flex-start; }
  .external3d-toolbar-group { gap: 4px; }
  .external3d-toolbar-group:first-child { max-width: calc(-92px + 100vw); }
  .external3d-readout { font-size: 8px; max-width: 86px; }
  .external3d-msl-status { inset: auto 6px 6px auto; font-size: 8px; min-width: 0px; width: min(46vw, 250px); max-width: 46vw; }
  .external3d-mini-cic { left: 6px; bottom: 6px; width: min(46vw, 230px); height: 150px; }
  .external3d-mini-cic canvas { height: 126px; }
  .external3d-help { display: none; }
}
@media (pointer: coarse), (max-width: 640px) {
  .external3d-msl-status { inset: auto 6px 6px auto; font-size: 8px; min-width: 0px; width: min(46vw, 250px); max-width: 46vw; }
  .external3d-mini-cic { left: 6px; bottom: 6px; width: min(46vw, 230px); height: 150px; }
  .external3d-mini-cic canvas { height: 126px; }
  .external3d-help { display: none; }
}
@media (max-width: 700px) {
  #damageControlPanelV1 { right: 8px; bottom: calc(8px + env(safe-area-inset-bottom,0px)); width: calc(-16px + 100vw); max-height: calc(100dvh - 20px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px)); }
  #damageControlPanelV1 .dc-header { padding: 10px 12px; }
  #damageControlPanelV1 .dc-scroll { padding: 10px 12px 16px; }
  #damageControlPanelV1 .dc-team-grid { gap: 6px; }
  #damageFloodPanelV1 { bottom: calc(8px + env(safe-area-inset-bottom,0px)); box-sizing: border-box; left: 8px !important; top: auto !important; width: calc(-16px + 100vw) !important; max-width: none !important; max-height: calc(100dvh - 24px) !important; z-index: 5600 !important; }
  #damageFloodPanelV1 button { min-height: 44px; font-size: 14px; touch-action: manipulation; }
}
@media (max-width: 640px) {
  #controlDeckDamageActions #damageControlToggleV1, #controlDeckDamageActions #damageFloodToggleV1 { min-width: 64px !important; min-height: 32px !important; padding: 3px 5px !important; font-size: 8px !important; }
  #damageControlPanelV1, #damageFloodPanelV1 { right: 4px !important; bottom: calc(var(--control-dock-bar-h) + 8px) !important; width: calc(-8px + 100vw) !important; max-width: none !important; max-height: calc(100dvh - var(--control-dock-bar-h) - 20px) !important; }
}
@media (min-width: 641px) and (max-width: 1000px) {
  :root { --control-dock-bar-h: 78px; }
  .control-deck-bar { grid-template-columns: 1fr auto; grid-template-areas: "tabs damage" "utility utility"; row-gap: 4px; }
  .control-deck-tabs { justify-self: start; }
  .control-deck-utility { justify-content: center; }
}
@media (max-width: 640px) {
  #external3DView .c14-topbar { left: 6px; right: 6px; top: 6px; }
  #external3DReadout { max-width: 104px; font-size: 8px; }
}
@media (prefers-reduced-motion: reduce) {
  #c14ControlsDrawer, #c14ControlsDrawer.open { transition: none; }
}
@media (max-width: 640px) {
  #c14ControlsDrawer { top: 55px; }
  .c15-flyout { max-height: 340px; }
}
@media (prefers-reduced-motion: reduce) {
  #c14ControlsDrawer .c15-flyout { animation: auto ease 0s 1 normal none running none; }
}
@media (max-width: 640px) {
  #wip14a14QuickEngage3D { right: 6px; top: 52px; gap: 3px; max-width: calc(-100px + 100vw); flex-wrap: wrap; justify-content: flex-end; }
  #wip14a14QuickEngage3D .external3d-btn { min-height: 27px !important; padding: 3px 5px !important; font-size: 7px !important; }
  #external3DQuickState { display: none; }
  #external3DTerminalSummary { top: 118px; }
}
@media (max-width: 640px) {
  .control-deck-tabs { grid-template-columns: repeat(4, minmax(42px, 1fr)); }
  #controlDeckFleetPage.active { grid-template-columns: 1fr; max-height: calc(100dvh - 135px); }
  #controlDeckFleetPage input, #controlDeckFleetPage select { min-height: 44px; }
}
@media (max-width: 640px) {
  .control-deck-tabs { grid-template-columns: repeat(5, minmax(38px, 1fr)); }
  #controlDeckAirPage.active { max-height: min(44dvh, 280px); }
  #airControlsB { max-height: min(42dvh, 265px); }
  #airControlsB button { min-height: 38px; font-size: 10px; }
  #airAircraftA { height: 210px; max-height: 38dvh; }
  .air-aircraft-a { font-size: 10px; padding: 5px; }
  #airControlsB .control-deck-note { font-size: 9px; }
  #airAltitudeDialogC button { min-height: 44px; }
}
```

## UI 교체 분류

`UI_CLASSIFICATION.tsv`는 현재 페이지에서 생성된 버튼·탭·입력 컨트롤 각각의 id(없으면 dataset), 분류, 이유, 코드 위치를 기록한다. `이지스 전용`은 이 프로젝트의 현 US/AEGIS 장비 provider 소속이라는 뜻이며 하푼/팰렁스가 이지스함에서만 쓰인다는 주장과 다르다. 데이터로 반복 생성되는 행/셀은 provider와 dataset으로 찾아간다. 현재 존재하지 않는 SOV 전투 버튼을 만들어 분류하지 않았다.

이동 시 주요 제약: 짧은 가로 화면에서 HUD/메뉴/상태가 지도와 겹칠 수 있다. 이번에는 이를 숨기거나 측면 도크로 옮기지 않았다. 3D 작은 위젯을 모두 edge panel로 취급하면 기준점이 메뉴 개폐마다 흔들리므로 명시적으로 제외했다.
