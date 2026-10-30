# 좌표 경로 감사

코드는 `Aegis_SIM_v48_WIP_VP_A.html`의 `c55-game-main` 압축 레코드다. [구현 패치](build.py), [계산기 원문](viewport.js), [관련 위치 전체](display-size-uses.tsv)를 같이 참조한다.

## 지도 좌표계

- 권위 있는 표시 거리 상태: `tacticalViewKm`. `mapZoom`은 `visible.shortSide*.42/(tacticalViewKm*WORLD_UNITS_PER_KM)`로 매 draw/변환 시 계산하는 파생 값이다.
- `worldToScreen` / `screenToWorld`는 **client CSS px**를 사용한다. visualViewport offset, safe area, 하단 패널과 DPR의 영향을 중복 적용하지 않는다. canvas의 backing pixel 좌표는 입력 API에 전달하지 않는다.
- drawRadar의 affine 변환도 `worldToScreen(0,0)`에서 얻는다. map pointer/tap/drag, lock cursor 입력, AIR/ISAR 위치 입력, Harpoon 경로, viewport world bounds/잠금 카드와 지도 스케일이 같은 기준을 사용한다.
- 지도상의 함선·트랙·경로·레이더 원 등은 기존 world 좌표로 그린다. 각 도형마다 화면 중심을 따로 계산하지 않는다. 폰트·심벌·선폭의 world↔px 환산은 파생 mapZoom을 읽는다.
- 지도 자체를 보이는 사각형으로 clip한다. SPY scheduler는 떠 있는 화면 진단이므로 clip 복원 후 layout의 상단 중앙에 그린다.

## 잔존 크기/비율 좌표와 처리

| 위치 (해제 소스 행) | 남은 계산 | 처리/이유 |
|---|---|---|
| 447 / AEGIS_VIEWPORT.measure | visualViewport 또는 innerWidth/innerHeight | **허용된 유일한 창 크기 fallback**. 화면 위치를 각 렌더러에서 다시 계산하는 용도가 아님 |
| 20679–20683 / resize | 2D/altCanvas backing width/height·DPR | 픽셀 버퍼 설정. 2D CSS 크기/offset은 계산기 raw rect 사용 |
| 47162 / drawAltitudeDisplay | 독립 altCanvas 부모 clientWidth/Height·로컬 비율 | 기존 1px 숨김 호환 패널. 폭/높이 20px 미만이면 조기 종료. 주 CIC 좌표계가 아니므로 보존 |
| 49559 / drawSpySchedulerScreenOverlay | 화면 폭의 .30, 상단 중앙 | layout 기준으로 변경. 떠 있는 진단 HUD라 map visible rect를 더 줄이지 않음 |
| 50563 / wip202DrawShipProjection | 오프라인 2D 함선 도면 cache의 W/H | 독립 도면 canvas 내부 좌표. 보존 |
| 50579–50584 / drawShipDetail | `topH=H*.48`, `W/2`, 위/측면도 비율 | **사용자가 지목한 독립 SHIP 피격도 패널**. 지도 좌표에 들어가지 않으므로 보존. 창 전체 중심으로 함선을 배치하는 코드가 아님 |
| 57223–57455 / 미사일 도색 생성 | 1024/2048 텍스처 크기, canvas 폭/높이 비율 | 3D 재질의 픽셀 atlas/스텐실 배치. viewport와 무관하여 보존 |
| 57614 / 효과 텍스처 | 128×128 canvas | 효과 재질 생성. 지도·카메라 위치 계산과 무관 |
| 58737–58749 / drawAuxCic | 미니 CIC 자체의 `w*.5`, `h*.5`, `.46/rangeM`, DPR | 독립 20km 반경 미니 지도. 메인 CIC의 카메라/거리 상태와 별개이며 기존 모함/카메라 중심 정책 유지. 내부 로컬 픽셀 기준을 메인 worldToScreen으로 대체하지 않음 |
| 59259 / 카탈로그 resize | 자체 canvas CSS rect·backing pixel 크기 | 가변 크기이므로 camera projection은 공통 함수로 교체. 카탈로그 내부 패널 디자인은 보존 |
| __VIEWPORT_A__.projectShipPoint | 실제 canvas CSS rect로 NDC를 측정 | **진단 전용** 투영 결과 읽기. 렌더/물리의 위치 소유자가 아님 |
| CSS의 vw/dvh/%/미디어쿼리 | HUD, dock, 모달, drawer 등의 패널 배치 | 원본 CSS bytes 유지. [UI 레이아웃 보고](UI_LAYOUT_REPORT.md)에 요소별 실측과 경계/cascade 기록 |

해제된 main에서 unqualified `innerWidth/innerHeight`는 0건이다. 창 크기 fallback은 계산기 안의 명시적 `window.innerWidth/innerHeight`뿐이다. 렌더러의 own canvas CSS 크기 읽기는 backing buffer와 frustum의 CSS↔NDC 경계에서만 사용한다. 독립 canvas/재질까지 메인 지도의 좌표 함수로 바꾸지 않는다.

## 리사이즈 소유권

window resize/orientationchange, visualViewport resize/scroll, fullscreenchange/webkitfullscreenchange, documentElement/controlDeckPanel/external3DView 및 등록된 카탈로그 canvas의 ResizeObserver를 계산기로 모았다. 다음 rAF에서 읽고 150ms 후 다시 요청한다. 그 뒤 200ms에 추가로 reflow가 생겨도 RO가 새 요청을 만든다. 변한 수치에만 version을 올린다. 새 구독자는 초기 크기가 달라지지 않아도 다음 rAF에 최초 상태를 한 번 받는다.

2D resize와 c52 dock clearance는 구독자다. 3D는 version이 달라지면 resize하며, `_resizeNeeded`는 화질/DPR·context 복구 등 기존 renderer invalidation 용도로도 유지한다. 별도의 window resize listener는 없다. C15 flyout 높이 배치도 layout/구독을 사용한다. fullscreen 버튼 라벨 갱신은 geometry 계산과 별개다.

## 저장

SOV_A의 작전 저장/불러오기 경로에 **mapZoom, camOffset, tacticalZoomIdx, c14CameraPan이 없다**. 따라서 옛 px/world 저장을 km로 옮기는 마이그레이션은 필요 없다. 새 viewport/카메라 상태도 작전 snapshot에 넣지 않았다. 작전 불러오기·함정 변경·epoch·카메라 리셋의 기존 규칙을 유지한다.
