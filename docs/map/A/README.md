# MAP_A — 지도 조회·통제·명령 분리

기준은 UI_A1 commit `0452e1066a5abddd144788c4cba80e38cec97afd`, HTML SHA-256 `fd7079e9154e8778f7f5a340e6102c8843930b9865d4dc1135714c4847cdc3b8`다. 결과는 루트 [Aegis_SIM_v48_WIP_MAP_A.html](../../../Aegis_SIM_v48_WIP_MAP_A.html)이다. [전체 보고서](REPORT.md), [수치 색인](evidence/verification-summary.json), [정보 출처 감사](OBSERVATION_AUDIT.md)를 함께 본다.

지도 객체를 탭하면 정보창을 연다. 항해 명령은 정보창/상황 메뉴에서 명시적으로 통제를 얻은 뒤 빈 바다를 탭한다. 시작은 통제 없음이다. 조회와 통제, 실제 LOCK은 독립적이다. 겹친 심볼은 후보 목록을 먼저 연다. 우클릭·550ms 롱프레스·펜 보조 버튼은 같은 상황 메뉴를 연다. 임의 점 삭제는 비활성이고 마지막 점만 취소할 수 있다. AIR·ARM 등 기존 조작 창은 그대로 있다.

SYS의 ‘지도 입력’을 ‘기존’으로 바꾸면 원본 UI_A1 canvas pointerup 분기를 그대로 실행한다. 선택 상태는 UI 메모리뿐이며 게임 저장에 추가하지 않는다. 신규/기존 설정과 정보창 배치는 localStorage의 기존 UI 경로를 사용한다. 저장 시 트랙·식별 초기화(기존 정책)를 유지한다. 하푼의 데이터링크 없는 현재 위치는 공개하지 않는다. 자함 정보창의 발사 기록에서 발사 시각·지정 트랙·고정 계획만 조회할 수 있다.

소스는 `observations.js`(화이트리스트 경계/기존 명령 어댑터), `map.js`(UI 상태·입력·표시), `map.css`다. `build.py`가 고정된 UI_A1에서 정확히 재빌드한다. 기존 함수의 변경 7개와 원본 14개 패킹 블록의 무결성을 정적 검사한다. 원본 canvas pointerup/게임 저장 코드는 byte-exact다. 새로운 UI 컨트롤을 추가하며 기존 컨트롤을 복제하거나 이벤트 핸들러를 교체하지 않는다.

```bash
python docs/map/A/build.py archive/v48/WIP_UI_A1/Aegis_SIM_v48_WIP_UI_A1.html /tmp/MAP_A.html
cmp /tmp/MAP_A.html Aegis_SIM_v48_WIP_MAP_A.html
python docs/map/A/run_suite.py archive/v48/WIP_UI_A1/Aegis_SIM_v48_WIP_UI_A1.html Aegis_SIM_v48_WIP_MAP_A.html /tmp/map-a-check
```

Python Playwright/Chromium과 Node 의존성은 UI_A1과 동일하다. `AEGIS_CHROMIUM_EXECUTABLE`로 Chromium 경로를 지정할 수 있다. 헤드리스에서는 UI가 자동 전체화면에 들어가는 것만 거부하는 기하 fixture를 사용한다. `verify_ui_a1.py`는 변경된 함 정보 버튼 기대값과 명시적 기존 입력 모드만 이관하며, 기존 테스트 소스는 수정하지 않는다. `verify_regressions.py`도 기존 창을 전면화하고 기존 입력 모드를 선택하는 테스트 어댑터다. 모든 기능 판정은 원래 native 경로를 사용한다. 이전 버전의 assertion 수를 이번에 실행한 것처럼 합산하지 않는다.

함급·시뮬레이션·물리·센서·ROE·발사 권한·저장 스키마·모델은 변경하지 않는다. 3D 미니 CIC 입력은 이번 범위가 아니다. 전체 검수는 소프트웨어 WebGL이며 실제 S24 GPU/FPS나 실제 펜 하드웨어 검증은 아니다. 펜 down과 chorded move는 DOM PointerEvent로 확인한다. 구상서 파일은 제공된 작업 트리/첨부에서 찾지 못했으며 상세 MAP_A 지시서를 구현 기준으로 삼았다.
