# VP_A 검수 결과

**19 suites · 567/567 assertions PASS · 페이지 오류 0.** 기준/최종 파일의 SHA와 개별 raw evidence는 [verification-summary.json](evidence/verification-summary.json)에 기록한다. UI 실측은 별도 fine/coarse 두 번이며 위 assertion 수에 컨트롤 604개를 더하지 않았다.

시험 크기: 1920×1080, 1400×900, 1400×560, 900×900, 600×900, 390×844, 844×390. 고정 seed 1831565813.

## A–I 수치표

| 검수 | 실제 결과 | 판정 |
|---|---|---|
| A: 2D 중심/거리 | 중심 최대 0.000000px, SCALE 40km 전부 동일, 고정 표적 거리/짧은 변 편차 <10⁻¹²% | PASS |
| B: 팬 후 크기 변경 | 원래 중앙 world 점의 중앙 오차 최대 0.000000px | PASS |
| C: 입력 | 7/7 크기에서 자함 커서와 표적 탭→LOCK 성공, 하푼 경유점 최대 0.00002730px | PASS |
| D: 기본 3D | 조준 기준점 중앙 오차 0.164387px, CG 길이/shortSide 0.607594658, DDG 0.538643347; 둘 다 편차 <10⁻¹²%, 모든 선수·함미 포함 | PASS |
| E: 3D 팬 후 변경 | 중앙 기준 위치/shortSide 변화 <10⁻¹²% | PASS |
| F: 크기 연타 | 무작위 30회 / 0.097432s; 정착 후 단일 변경과 투영 좌표 동일, NaN 없음 | PASS |
| G: 회전 지연 | 216.4ms 뒤 dock 높이 241→281px, visible 2D 높이 103px; 중심 재일치. 3D 길이 편차 0.000000%, 선수·함미 포함 | PASS |
| H: 시뮬 불변 | 같은 seed로 native 7200 ticks=120s, resize/repaint 유무 두 상태 해시 완전 동일 | PASS |
| I: 기존 회귀 | 헬기/APS-153/ISAR/하푼/EMCON/저장·침수·기존 DDG/CG 420 assertions | PASS |

H의 해시: `085812f497d54b66feb69e8bd15a53f0fe93e4199c95fdb4cc405b75518b6587`. 각 상태는 1,764,132bytes이며 actual release·헬기 출격·SOV 파랑/물리를 포함한다. 단순 카메라 좌표만 비교한 해시가 아니다.

D의 중심은 기존 기본 카메라의 함 로컬 `(0,11,0)` 조준점이다. yaw 43°/pitch 20°/distance 235m/targetY 11m를 보존했다. 원근 외곽 사각형 중간점으로 초점을 재정의하지 않았다. 선수/함미 포함과 길이는 별도로 검사했다.

## 크기별 실제 2D/3D 값

A/C는 실제 offboard 표적 지정이 가능한 ARM 상태, 반경 40km다. 탭·콘텐츠에 따라 하단 패널 높이가 달라지는 것이 정상이며 계산기는 이를 측정한다.

| CSS 크기 | 보이는 2D 높이 | 2D shortSide | 세로 fov (주 3D) | CG 길이/shortSide |
|---|---:|---:|---:|
| 1920×1080 | 838.1250 | 838.1250 | 52.000000° | 0.607594658 |
| 1400×900 | 630.6875 | 630.6875 | 52.000000° | 0.607594658 |
| 1400×560 | 290.6875 | 290.6875 | 52.000000° | 0.607594658 |
| 900×900 | 564.0000 | 564.0000 | 52.000000° | 0.607594658 |
| 600×900 | 675.5625 | 600.0000 | 72.378321° | 0.607594658 |
| 390×844 | 619.5625 | 390.0000 | 93.093485° | 0.607594658 |
| 844×390 | 143.0000 | 143.0000 | 52.000000° | 0.607594658 |

추가 검수: 실제 visualViewport 1.25배 scale에서 844px 창의 visible width 675.200012px 반영, safe-area 입력(위12/우23/아래18/좌17px)에서 setViewOffset 중앙 정합, DPR2 backing 1200×1800, 실제 전체화면 진입/해제, 터치 핀치와 크기 변경 시 제스처 종료, 가변 카탈로그의 짧은 변 38° 유지. [390px 3D](evidence/viewport/ownship-390.png), [600px 3D](evidence/viewport/ownship-600.png).

## Suite별 수치

| suite | assertions |
|---|---:|
| static | 44 |
| viewport | 70 |
| invariance | 4 |
| extra | 29 |
| regressions/aps153 | 20 |
| regressions/emcon-native | 27 |
| regressions/emcon-ui | 14 |
| regressions/harpoon-clock | 24 |
| regressions/harpoon-f1 | 46 |
| regressions/helicopter-flight | 85 |
| regressions/isar-classes | 8 |
| regressions/isar-clock | 12 |
| regressions/isar-native | 36 |
| regressions/isar-ui | 38 |
| regressions/paired-baseline | 42 |
| regressions/sov-casualty | 13 |
| regressions/sov-deployment | 15 |
| regressions/sov-native | 30 |
| regressions/sov-visual | 10 |

HELI_F2 이전 검사의 수정은 [test migration records](evidence/regressions/)에 남겼다. HELI_F2의 nullable isar:null 필드, SOV_A 네 함급/216행, 옛 창 중앙 입력 공식을 현 좌표 API로 옮긴 부분뿐이다. NODE/Python 실행 경로는 이 작업의 test runner가 원래 각 스크립트 디렉터리를 보존한다. 기존 flight/센서/발사/손상 assertion을 삭제하지 않았다.

별도 상태·제한: 실폰 GPU/FPS·실제 OS 노치/키보드/자동회전 드라이버는 측정하지 않았다. native Chromium fullscreen/VV와 지연 재배치·safe area 입력의 수치 경로를 검증했다. UI의 기존 겹침/작은 글자/패널 잘림은 이번 디자인 변경 범위가 아니다.
