# PERF_C 성능·검증 조건

최종 원본 15,707,171bytes, SHA `5f8fb9ed69a960c4eef4c15ab22271c82c9b59a095a9ec8a959689ecba9acffd`, decoded main `015c4cf9f83c9f6bd595ce61583e214bbd12c8248fad15bacdc87fa10f0c7358`. PERF_B와 PERF_C를 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 2반복이며 각 조건의 두 pass가 AB/BA 반대 순서다. 두 번째에는 조건 순서도 뒤집는다. 다른 회귀·profile 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 16쌍 모두 관측/저장/무장/방어/EW 상태·entity 수·combatRNG를 exact 비교한다. performance/profiler 및 기존 performance.now() duration인 lastBuildMs/lastAssessmentMs만 명시 제외하고 full raw state도 보존한다. 실제 시뮬레이션 시각·연관·판단·발사·효과는 포함한다.

| 함정 수 | Kh-32 수 | PERF_B ms/tick 평균 | PERF_C ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
| 1 | 0 | 2.16 | 2.04 | 5.5% |
| 1 | 8 | 4.75 | 4.65 | 2.1% |
| 1 | 32 | 16.46 | 12.88 | 21.7% |
| 1 | 64 | 47.11 | 32.69 | 30.6% |
| 3 | 0 | 5.76 | 5.54 | 3.8% |
| 3 | 8 | 12.14 | 11.92 | 1.8% |
| 3 | 32 | 27.68 | 25.63 | 7.4% |
| 3 | 64 | 64.15 | 50.44 | 21.4% |

해당 호스트/대표 조건의 CPU 관측이며 휴대폰/하드웨어 GPU FPS 또는 보편적 개선율이 아니다. 이번8조건 평균은 모두 감소했다. 0~8발 조건의 작은 차이는 실행 변동일 수 있다. PERF_B의 32발 약2~2.5% 증가는 당시 A/B 비교값이고 이번 표는 새 B/C 비교다. 서로 다른 실행의 절대 시간을 누적 성능율로 합산하지 않는다. profiler sensors_tracks_ew phase는 tick당2회이므로 calls로 가중한다. 별도 CDP 1ms profile은 inclusive 호출이 겹쳐 전체 비율로 합산하지 않는다.

최종 원본 직접 1603/1603PASS,31suites/15captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0. native NIS231사례에서 number exact·filter state exact를 확인했다. 상태6개/공분산36개 제자리 변경, 센서 위치·속도6개, 측정 오차4개, signed zero·invalid/fallback·canonical 갱신/거부 후 재연관, 36/64/96/180 게이트 양측과 실제 두 함종 core를 확인했다. 이 VM 의존성 제어는 자연 탐지나 요격률 인증이 아니다. 반복32관측의 native matrix multiply64→2는 동일 입력 제어 사례의 작업 감소이며 전체 게임 개선율이 아니다.

CG/DDG idle/8Kh32AUTO/손상6조건의 EW/network/tactical/maneuver/attack/team 포함 상태/RNG exact, 세 owner1/8/16/64배속, 실제 VLS/RAM/Phalanx·채프/눌카/Harpoon·actual release guards·native RAF/WebGL 피격·UI/camera·저장/reset·AI/공유를 새 원본에 직접 실행했다. 기존 PERF_A texture/canvas/lifecycle와 PERF_B planner/frame 계약도 재검사했다. 각 native/natural fixture의 조건·한계는 해당 raw report를 따른다. Actions dispatch는 없다.
