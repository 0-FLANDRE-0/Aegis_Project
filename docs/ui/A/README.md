# UI_A — 공용 상태 바와 창 시스템

최신 산출물은 루트 `Aegis_SIM_v48_WIP_UI_A.html`이다. [검수 보고서](REPORT.md), [검증 색인](evidence/verification-summary.json), [기존 컨트롤 이동 목록](MOVED_CONTROLS.tsv)을 함께 본다.

기준은 사용자 지정 VP_A SHA-256 `432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9`다. 시뮬레이터·센서·무장 권한·게임 저장과 모델은 바꾸지 않는다.

```bash
python docs/ui/A/build.py archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html /tmp/UI_A.html
cmp /tmp/UI_A.html Aegis_SIM_v48_WIP_UI_A.html
python docs/ui/A/verify_static.py archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html Aegis_SIM_v48_WIP_UI_A.html /tmp/ui-a-check/static
python docs/ui/A/verify_regressions.py Aegis_SIM_v48_WIP_UI_A.html /tmp/ui-a-check/regressions --parallel 1
python docs/ui/A/verify_ui.py Aegis_SIM_v48_WIP_UI_A.html /tmp/ui-a-check/ui
```

`windows.js`, `fullscreen.js`, `ui.css`가 새 표시 계층이다. `build.py`는 hash-pinned 원본의 main record와 화면 CSS에만 patch를 적용한다. `window.__UI_A__.snapshot()`은 배치·연결된 기존 노드·재고·시간 버튼의 상태를 확인하는 진단 포트다.

기존 회귀의 UI 탐색은 새 컨테이너를 실제로 열고, 가려진 지도를 노출한 뒤 같은 native 컨트롤을 누르도록 이관했다. 기존 fixed tick·센서·유도·피해·저장 검사 조건은 보존한다. AIR의 예전 고정 높이 검사는 크기 조절 창의 내부 scroll 영역 검사로 대체한다.

기존 567건에는 420건이 포함된다. 중복 합산하지 않는다. 헤드리스 emulation을 실제 휴대전화 FPS로 보고하지 않는다. CI는 사용자 환경 사정에 따라 수동 실행 workflow만 준비한다.

## 검증 환경과 fixture 이관

사업 로직 420개 assertion은 원래 suite를 호출한다. UI 자동화만 새 창의 실제 열기/전면화/스크롤 경로를 따라간다. 지도 클릭 전에는 겹친 창을 닫고 VP_A 좌표 변환을 사용한다. AIR의 진행률과 결과는 고정 300ms 대신 해당 표시가 갱신될 때까지 기다린다. 소프트웨어 WebGL의 모델 준비는 기존 native 큐를 그대로 기다린다.

UI 배치 검사에서는 자동 전체화면을 거부하도록 브라우저 fixture를 둔다. 전체화면 검사는 별도 storage suite와 VP_A 실제 진입/해제 검사로 수행한다. 일반 회귀에서는 첫 제스처의 실제 전체화면을 해제한 뒤 시작하여 Linux headless의 비활성 창 프레임 제한을 피한다. 스크린샷은 native 화면 갱신 뒤 CDP capture로 얻는다. 이 절차는 제품의 truth·센서·클록을 바꾸지 않는다.

여러 전체 suite를 같은 evidence 폴더에 동시에 실행하지 않는다. UI/3D suite와 다수 SwiftShader 인스턴스를 병렬 실행하면 브라우저의 RAF/클릭 안정화가 타임아웃될 수 있다. 최종 기록은 `evidence/release/`에만 둔다.

APS/ISAR/교전 로그의 기존 dialog 3개는 숨긴 옛 shell 밖의 body로 이동했다. 고도 설정 dialog는 AIR 페이지 subtree와 함께 이동하며 native modal을 유지한다.
