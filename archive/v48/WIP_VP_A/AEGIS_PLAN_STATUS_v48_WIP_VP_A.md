# AEGIS v48 WIP VP_A 상태

기준 SOV_A `c7d498d063010385b1aa2172049c4dd248f96ec1` / 브랜치 `viewport-a`.

**VP_A 구현·런타임·브라우저 검증 완료: 567/567 assertions, 19 suites, 페이지 오류0.**

- 실행 파일 `Aegis_SIM_v48_WIP_VP_A.html` / **18,002,954bytes**, SOV_A 대비 **4,506bytes 증가**.
- SHA-256 `432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9`.
- [전체 보고/재현](docs/viewport/A/README.md), [원시 검증 요약](docs/viewport/A/evidence/verification-summary.json).

## 1. 변경 요약

AEGIS_VIEWPORT로 visualViewport/안전영역/가장자리 패널의 CSS 사각형과 version을 계산한다. resize·VV resize/scroll·orientation·fullscreen·RO를 한 곳에서 rAF/150ms 재측정으로 합쳤다. 개별 resize/setTimeout 초기화를 제거했다. 2D는 보이는 짧은 변 반경 km를 상태로 유지하고 worldToScreen/screenToWorld를 그리기/입력에 공유한다. 3D는 보이는 짧은 변52°와 setViewOffset, 정규화 팬을 사용한다. 가변 카탈로그는 같은 규칙에38°를 보존한다.

상수/동작 기준 차이, 자함 커서와 표적 LOCK의 구분은 [구현 전 보고](docs/viewport/A/CONFLICTS.md)에 기록했다. 거리 한계는 기존7개 시험 크기의 px/world 범위 합집합 **7.184210526–1492.105263158km**이며 기존15/40/120/300km 단계 유지. mapZoom/카메라 팬은 원래 작전 저장에 없으므로 저장 migration은 없다.

## 2. A–I 결과 수치

| 항목 | 결과 |
|---|---|
| A: 2D 중심/거리 | 중앙 오차0px, 40km 라벨 동일, 고정 표적 거리/shortSide 편차 <10⁻¹²% |
| B: 2D 팬 | 같은 world 중앙점의 최대 오차0px |
| C: 입력 | 7/7 크기에서 자함 커서·표적 탭→LOCK, 경유점 최대오차0.00002730px |
| D: 3D | 최대 중앙 오차0.164388px, CG/DDG 길이/shortSide 각각0.607594658/0.538643347, 편차 <10⁻¹²%, 모든 선수·함미 포함 |
| E: 3D 팬 | 중앙 기준 정규화 위치 변화 <10⁻¹²% |
| F: 크기 연타 | 30회/0.097432초, 단일 변경 정착 좌표와 동일, NaN 없음 |
| G: 회전 지연 | 216.4ms 뒤 panel 241→281px, visible 높이103px로 반영. 2D/3D 중심·거리·포함 통과 |
| H: 120초 불변 | 7200 native fixed ticks, 상태1,764,132bytes의 SHA 두 실행 동일 |
| I: 기존 기능 | 헬기/APS-153/ISAR/하푼/EMCON/저장·손상/기존 함정420 assertions 통과 |

H SHA: `085812f497d54b66feb69e8bd15a53f0fe93e4199c95fdb4cc405b75518b6587`. 실제 하푼 발사/헬기 출격/SOV를 포함한다. D/E는 기존 자함 카메라 조준점 local `(0,11,0)` 기준이며 외곽 중간점으로 바꾸지 않았다. [7개 크기별 값/전체 suite 표](docs/viewport/A/VERIFICATION.md).

추가: 실제 VV1.25배 scale, 제어된 safe area, DPR2, 전체화면 진입/해제, 터치 핀치/크기 변경 중 제스처 취소, 카탈로그 검증. 물리 pose를 먼저 적용하고 viewport의 실제 rAF 갱신을 기다린 뒤 투영을 측정했다.

## 3. 가장자리/떠 있는 위젯

2D `controlDeckPanel`만 full-span 하단 edge로 분류한다. 3D에는 현재 edge dock가 없다. 미니 CIC, MSL STATUS, topbar/HUD, quick engagement, drawer/flyout, 조건부 SHIP/손상 창은 떠 있는 위젯이다. 모달/출항 편성/카탈로그는 독립 overlay다. [38요소·4크기·기본/조건부 위치와 측면 도크 검토](docs/viewport/A/UI_LAYOUT_REPORT.md), [coarse/mobile](docs/viewport/A/UI_LAYOUT_COARSE_REPORT.md).

## 4. 비율 기반 좌표 잔존

주 지도는 공통 변환을 사용한다. SHIP 도면의 `topH=H*.48`, 숨김 altCanvas, 독립20km 미니 CIC, 도색/효과 텍스처 내부 비율은 보존한다. 직접 창 크기 fallback은 계산기에만 있고 픽셀 버퍼 설정과 로컬 panel 좌표는 별개다. [행 위치/사유](docs/viewport/A/COORDINATE_AUDIT.md).

## 5. 다음 UI 레이아웃 조사

디자인·배치와 outer CSS bytes는 바꾸지 않았다. fine/coarse 각각4크기×8상태, CSSOM15개 미디어쿼리를 기록했다. 640/980/1000/700px, 높이520px, pointer:coarse와 reduced-motion의 효과는 위 위치 보고에 포함한다. [604컨트롤+42패널의 분류/코드 위치](docs/viewport/A/UI_CLASSIFICATION.tsv).

## 6. SOV 자함화/공용 파랑 조사

[자함화 차단 지점/교체 범위](docs/viewport/A/SOV_PLAYER_READINESS.md). npcOnly/startup/session guard뿐 아니라 자함 SENSOR_MODEL 직접 레지스트리, VLS 편성/무장 codec, 자함 geometry/interior/dynamics 경로를 공용화해야 한다. 목표는 공용 지도+함정별 전투 panel/provider다. 새 SOV 기능은 열지 않았다.

[파랑 일관성](docs/viewport/A/WAVE_RESPONSE_REPORT.md). DDG/CG는 자함·아군·적함 모두 공통 동역학은 쓰지만 파랑 외력 opt-in이 없다. SOV만 외력을 받는다. .55/.18/.18은 실제 RAO 자료가 아닌 SIM_TUNED다. APS mast 높이는 현재 정적 프로파일 값이라 공용 동요 확장 시 동적 높이/안정화/피격/갑판 이탈 경계를 함께 검토해야 한다. 이번에는 변경하지 않았다.

## 7. 남은 범위/반영

기존 짧은 가로 화면의 SHIP/보수반 등 잘림·위젯 겹침은 다음 측면 도크 작업으로 남긴다. 실제 휴대폰 GPU/FPS와 OS 노치/키보드/회전 드라이버는 미측정이다. 극단 세로 비율(h/w 약2.443 초과)은 세로 FOV100° 상한과 짧은 변52° 유지가 양립하지 않는다. 시험7크기에서는 상한에 걸리지 않는다.

SOV_A 네 파일을 동일 bytes/blob으로 archive했다. 전체 HTML·소스·증거·문서·체크섬을 브랜치에 직접 올리고 원격 bytes/크기/SHA/Git blob을 대조한다. 수동 workflow만 준비하며 Actions dispatch/main·이전 브랜치 병합/새 PR은 하지 않는다. 원격 결과는 `docs/viewport/A/remote-publication.json`에 남긴다.
