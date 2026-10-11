# PERF_A 최종 성능·검증 조건

원본 15,704,207bytes, SHA `13a9de64d918efd053ead648cb312a691688691ccbfa72fe50fefd72054ae6ad`, main `c43d9287e066bd56132d57d3a2cb2b4b37bee05e008f59432a61f82ae41d64e1`. H4A 원본과 PERF_A 원본을 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 각각2반복/AB·BA 교대/두 번째 조건 역순이다. 다른 회귀 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper가 넣는 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 모든16쌍에서 저장/관측/무장/방어/EW 상태, entity 수와 combatRNG를 exact 비교했다. 기존 performance/profiler 및 `performance.now()`가 기록하는 방어 진단의 lastBuildMs/lastAssessmentMs만 비교에서 제외한다. 시뮬레이션 시각·판단·발사·효과 값은 유지한다. 원래 처리시간 필드를 포함한 raw 상태도 모두 보존하고 이 명시적 정규화로 재검증했다. 자세한 각 반복과 압축 상태 원본은 evidence/benchmark.json 및 state-*.json.gz다.

| 함정 수 | Kh-32 수 | H4A ms/tick 평균 | PERF_A ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
| 1 | 0 | 2.12 | 2.15 | -1.0% |
| 1 | 8 | 4.38 | 4.60 | -5.1% |
| 1 | 32 | 16.42 | 15.76 | 4.0% |
| 1 | 64 | 49.43 | 49.81 | -0.8% |
| 3 | 0 | 7.24 | 5.20 | 28.1% |
| 3 | 8 | 17.73 | 13.24 | 25.4% |
| 3 | 32 | 39.29 | 28.11 | 28.4% |
| 3 | 64 | 88.06 | 69.28 | 21.3% |

이 값은 해당 호스트/대표 조건의 CPU 관측이며 사용자 휴대폰 FPS 또는 보편적 개선율이 아니다. 단독 자함의 `getShipSystemDamage`는 기존 경로를 유지하므로 전체 함정 수에 따라 효과가 달라진다. 적은 부하에서 작은 차이는 측정 변동일 수 있다. 64발 조건의 비용이 남아 있어 다음 단계의 planner/SPG·SPY·접촉 geometry 감사를 계속해야 한다. `sensors_tracks_ew` phase는 tick당2회이므로 phase 평균을 단순 합산하지 않고 calls로 가중한다.

실제 native64모델에 고유 Kh-32 도색 texture/canvas1개·2048×2048 RGBA8 source pixel16,777,216bytes를 확인했다. 이전2모델은 동일 픽셀의 texture/canvas2개를 만들었다. 같은 도색64개를 만들 경우의 중복 source pixel budget1,073,741,824bytes(1GiB)가16,777,216bytes(16MiB)로 줄어드는 구조다. 실제 VRAM/heap 측정값이나 FPS가 아니며 mipmap/GPU·renderer별 upload 비용은 별도다. geometry/재질은 개별 소유이며 이 단계에서 draw 수를 줄이지 않는다.

기존 도색 픽셀 SHA와 geometry/재질 SHA가 정확히 같다. 부분 제거 뒤 texture disposal0/실제 WebGL 렌더, 마지막 제거1/반복 제거1, 새 생성·MAIN잔해·닫힌 도감 참조·도감 전환·import/reset epoch를 확인했다. 기존 도감은 닫아도 현재 모델을 보관한다.

새 원본 직접 1483/1483PASS,29suites/15captures. 과거 H4A 결과를 합산하지 않았다. CG/DDG6 ownship 조건은 performance 계측 외 EW/network/tactical/maneuver/attack/team을 포함한 상태와 RNG가 exact다. 세 owner1/8/16/64 배속, 실제 nativeVLS/RAM/Phalanx·채프/눌카/Harpoon·피격 후 nativeRAF/WebGL·UI/camera·저장/reset 및 기존 함대 AI/공유를 직접 재검사했다. 자연 Harpoon과 close-in의 fixture 조건/late guards는 해당 report를 따른다. core/page/runtime/presentation 오류0, Actions 미실행이다.
