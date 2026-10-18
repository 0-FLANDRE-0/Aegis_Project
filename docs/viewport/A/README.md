# VP_A — viewport/거리/카메라 표시 통합

기준 SOV_A `c7d498d063010385b1aa2172049c4dd248f96ec1`. 결과 `Aegis_SIM_v48_WIP_VP_A.html`은 **18,002,954bytes**, 기준 대비 **4,506bytes 증가**다. SHA-256:

`432de9b88566d6198da0a21856ab85d1febda8106fcd28f6d8f13fd8801e67b9`

**567/567 assertions /19 suites PASS, 페이지 오류0.** [A–I 검수](VERIFICATION.md), [원시 요약](evidence/verification-summary.json).

1. **변경 요약**: [구현 전 기준](CONFLICTS.md), [계산기](viewport.js), [결정적 패치/패킹](build.py). 공통 AEGIS_VIEWPORT의 version을 2D/3D/dock clearance가 구독한다. 거리 상태는 km, 팬은 기존 world 단위(2D)/정규화 short-side span(3D). 주 3D 기준 52°, 카탈로그 38°.
2. **A–I 수치표**: [VERIFICATION.md](VERIFICATION.md). 실제 함체 pose를 먼저 적용해 D/G를 검증했다. H의120초 상태 해시는 동일하며 실제 Harpoon release/헬기/선박을 포함한다.
3. **가장자리/위젯 분류**: 가장자리 축소는 2D controlDeckPanel만. 3D 작은 위젯/상단 HUD/미니 CIC/MSL STATUS/drawer는 떠 있는 것으로 유지. [요소별 측정](UI_LAYOUT_REPORT.md).
4. **화면 비율 좌표 잔존**: [COORDINATE_AUDIT.md](COORDINATE_AUDIT.md), [검색표](display-size-uses.tsv). SHIP 도면의 H*.48, altCanvas, 미니 CIC, 재질 atlas 등의 독립 로컬 좌표는 보존했다. mapZoom이 작전 저장에 없으므로 저장 migration 없음.
5. **차기 UI 레이아웃 조사**: [fine/desktop](UI_LAYOUT_REPORT.md), [coarse/mobile](UI_LAYOUT_COARSE_REPORT.md). 각38개 floating DOM 요소/4크기/32상태, CSSOM15미디어쿼리. [604컨트롤+42패널의 공용/전용/혼합 분류](UI_CLASSIFICATION.tsv), 코드 위치 포함.
6. **SOV 자함화 조사**: [차단 지점/규모](SOV_PLAYER_READINESS.md), [401개 가정 검색 결과](profile-assumptions.tsv), [본문/행 위치](source-audit.json). [파랑 조사](WAVE_RESPONSE_REPORT.md). 두 기능은 구현하지 않았다.
7. **남은 문제/판단**: 기존 짧은 가로 화면에서 SHIP/보수반·HUD 일부 겹침/잘림은 디자인 변경 범위 밖이다. 다음 측면 도크 단계에서 다룬다. 실폰 GPU/FPS, 실제 OS 노치/키보드/회전 드라이버는 미측정이다. D/E 기준점은 기존 카메라의 함 로컬 `(0,11,0)` 조준점이며 원근 외곽 사각형 중심으로 재정의하지 않았다. 높이/폭이 약2.443을 넘는 극단 세로 화면에서는 요청된 세로FOV100° 상한 때문에 짧은 변52°를 동시에 유지할 수 없다. 이번 7개 시험 크기는 상한에 걸리지 않는다.

## 구현 경계

ShipRuntime/프로파일, 60Hz fixed step, 센서/측정/식별/ROE/발사/전자전/손상/침수/파랑 모델과 save schema는 변경하지 않는다. main에서 기존3191개 명명 함수의 본문을 대조해 변경된15개 이름이 모두 표시/좌표 경로임을 확인했고, 명명 함수 외 camera/input 메서드 변경은 패치에 명시했다. 나머지13개 packed record와 SOV 등록/모델/텍스처 자산, outer CSS는 byte-identical이다.

view rect는 client CSS px다. visualViewport 크기·offset에서 safe area를 뺀 layout을 만들고, 명시적으로 등록된 full-span edge panel만 뺀다. 키보드/visual viewport 때문에 panel 하단이 visible 영역 밖에 있어도 그 영역의 하단을 덮으면 제외한다. rAF +150ms 재측정과 RO가 더 늦은 reflow를 처리한다. 최초 구독도 다음 rAF에 한 번 받는다. 버퍼 크기 설정과 독립 panel 내부 좌표를 지도 투영과 혼합하지 않는다.

새 진단 `window.AEGIS_VIEWPORT.snapshot()`과 `window.__VIEWPORT_A__.snapshot()`은 detached 데이터를 반환한다. `__VIEWPORT_A__`의 거리/팬 setter는 표시 상태만 바꾸며 시뮬레이션 제어 기능은 없다.

## 재현

```bash
python docs/viewport/A/build.py archive/v48/WIP_SOV_A/Aegis_SIM_v48_WIP_SOV_A.html /tmp/VP_A.html
cmp /tmp/VP_A.html Aegis_SIM_v48_WIP_VP_A.html
python docs/viewport/A/run_suite.py archive/v48/WIP_SOV_A/Aegis_SIM_v48_WIP_SOV_A.html Aegis_SIM_v48_WIP_VP_A.html artifacts/viewport-a
```

Python Playwright/Chromium과 `docs/performance/F`의 npm 의존성이 필요하다. `NODE_PATH`와 `AEGIS_CHROMIUM_EXECUTABLE`을 표준 방식으로 지정할 수 있다. CI용 workflow는 workflow_dispatch만 준비하며 **이번에는 Actions를 실행하지 않았다**. 로컬 브라우저는 SwiftShader다. 테스트의 source/metadata migration만 [runner](verify_regressions.py)에 기록하며 앱의 assertion 대상 정책을 완화하지 않는다.

SOV_A HTML/상태/SHA/workflow 네 파일을 [동일 bytes/blob으로 보존](evidence/archive-preservation.json)한다. 전체 HTML을 작업 브랜치에 직접 업로드한 뒤 원격 전체 blob bytes를 다시 대조한다. main/선행 브랜치 병합이나 새 PR 생성은 이번 작업에 포함하지 않는다. 원격 대조 기록은 `remote-publication.json`에 별도 남긴다.
