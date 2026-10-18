# UI_A1 — 모바일 압축과 직접 조작

기준은 UI_A `30428d679ab0ecf724b3e6e007a94ebc3587f386`, HTML SHA-256 `a4b6825df6c28eb8f0747f73ec9469c90f277f96eb23e55be67298a6a1cab8e4`다. 결과는 루트 `Aegis_SIM_v48_WIP_UI_A1.html`이다. [수치·스크린샷](REPORT.md), [검증 색인](evidence/verification-summary.json)을 함께 본다.

사용자의 후속 요청에 따라 UI_A의 모바일 글자/조작 크기와 읽기 전용 상태 칩 정책을 변경한다. 일반 창 10px 글자·26px 버튼, 28px 제목줄, 작은 기본 창과 두 줄/한 줄 상태 바를 사용한다. FIRE/LOCK 등의 40px 보호 크기는 유지한다. 모바일 모드는 레이아웃 너비 ≤700px 또는 너비 ≤1000px이면서 높이 ≤540px일 때다. pointer:coarse에 의존하지 않으며 두 메인 캔버스에는 zoom을 적용하지 않는다.

창은 서로 겹칠 수 있다. 누른 창을 전면화하고 제목줄로 이동한다. 모바일에서는 자동 가장자리 스냅을 끄며 ≡ 메뉴의 명시 고정은 남긴다. 상태 바의 함 정보/재고 버튼은 접힌 NAV/ARM 창을 펼친다. 배치 schema 2는 위치·크기·접힘 복원 높이·겹침 순서를 저장한다. 예전 schema 1 배치는 새 기본 배치로 시작하고 UI 크기 설정은 보존한다. 게임 저장 형식은 바꾸지 않는다.

EMCON 칩은 기존 `emconBtn.click()`을 호출한다. 교전 칩은 바로 위에 수동/반자동/자동 팝업을 표시하며 선택 시 기존 `setEngagementControlMode()`를 한 번 호출한다. 세 모드의 기존 권한·취소·라벨 갱신 절차를 그대로 사용한다. 팝업만 열면 교전 모드는 바뀌지 않는다. 바깥 탭/Escape로 닫는다.

```bash
python docs/ui/A1/build.py archive/v48/WIP_UI_A/Aegis_SIM_v48_WIP_UI_A.html /tmp/UI_A1.html
cmp /tmp/UI_A1.html Aegis_SIM_v48_WIP_UI_A1.html
python docs/ui/A1/run_suite.py archive/v48/WIP_UI_A/Aegis_SIM_v48_WIP_UI_A.html Aegis_SIM_v48_WIP_UI_A1.html /tmp/ui-a1-check
```

Python Playwright·Chromium과 Node 의존성은 이전 UI_A와 같다. `AEGIS_CHROMIUM_EXECUTABLE` 환경 변수로 설치된 Chromium을 지정할 수 있다. 헤드리스 화면 검사는 전체화면만 거부하는 fixture를 사용한다. 시뮬레이션·센서·판정·발사·게임 저장 코드가 UI shell 밖에서 byte-exact인지 정적으로 검사하고, 기존 native 컨트롤의 동일 결과와 120초 상태 해시를 비교한다. 이전 1144건은 UI_A 당시 기록이며 이번에 전부 재실행했다고 합산하지 않는다.

소프트웨어 WebGL/DPR 에뮬레이션이며 실제 휴대전화 GPU/FPS 측정은 아니다. 수동 workflow는 준비만 하고 실행하지 않는다. 이전 UI_A 네 파일은 같은 bytes/blob으로 archive한다.
