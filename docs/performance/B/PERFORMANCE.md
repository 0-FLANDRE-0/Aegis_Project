# PERF_B 성능·검증 조건

최종 원본 15,706,015bytes, SHA `292622e556192d3c954917437709a0f1e4489e1636cd6263a4b7737832013faf`, main `6577a3e216f0bec2ae7aeefb7e79524c33ee52c564de94dfb3763ad3cb24a977`. PERF_A와 PERF_B를 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 각2반복/AB·BA 교대/두 번째 조건 역순이다. 다른 회귀·profile 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 16쌍 모두 저장/관측/무장/방어/EW 상태·entity 수·combatRNG를 exact 비교했다. performance/profiler 및 기존 방어 진단의 `performance.now()` duration인 lastBuildMs/lastAssessmentMs만 명시적으로 제외했다. 실제 시뮬레이션 시각·판단·발사·효과 값은 포함한다. 전체 raw 상태도 state-*.json.gz로 보존한다.

조건별 version order가 두 반복에서 같은 옛 runner 식을 original case index로 고쳤다. 정확한 첫 pass는 유지하고 두 번째는 각 조건에서 반대 순서로 다시 실행했다. 최종 표에는 반대순서 검사를 통과한 두 pass만 쓴다. 처음의 두 번째 pass·전체 report/source는 not-counted-original-order-*에 별도 보존한다. game HTML·fixture setup/measurement/state 함수는 이 보정에서 변경하지 않았다.

| 함정 수 | Kh-32 수 | PERF_A ms/tick 평균 | PERF_B ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
| 1 | 0 | 2.19 | 2.16 | 1.5% |
| 1 | 8 | 4.72 | 4.58 | 3.1% |
| 1 | 32 | 16.30 | 16.64 | -2.0% |
| 1 | 64 | 50.91 | 45.19 | 11.2% |
| 3 | 0 | 6.28 | 5.99 | 4.8% |
| 3 | 8 | 12.16 | 12.07 | 0.8% |
| 3 | 32 | 27.73 | 28.44 | -2.5% |
| 3 | 64 | 71.18 | 64.20 | 9.8% |

해당 호스트/대표 조건의 CPU 관측이며 사용자 휴대폰·하드웨어 GPU FPS 또는 보편적 개선율이 아니다. 64발에서 약10~11% 감소했으며 32발 평균은 약2~2.5% 증가했다. 32발 증가는 후속 SPY 최적화와 재측정에서 추적한다. 작은 차이는 측정 변동일 수 있다. 64발 비용과 SPY/피격/실제 가시 render의 비용이 남아 있다. profiler sensors_tracks_ew phase는 tick당2회이므로 calls로 가중한다. CDP 1ms sampling은 timing과 별도로 수행했다. 원본 샘플과 입력/SHA는 evidence/profile-a-* 및 profile-b-*를 따른다. inclusive 호출 시간은 겹치므로 더해서 전체 비율로 표현하지 않는다.

새 원본 직접 1534/1534PASS,30suites/15captures. 과거 결과 합산0, page/core/runtime/presentation 오류0. 독립 제어 사례96개에서 두 native planner의 계획·예약이 exact이고 새 ctx·current reservation·관측/pose/damage 변화와 기본 forecast 계약을 확인했다. frame의 모든 입력 변화·owner 분리·invalid throw·signed zero·canonical transform exact 및 실제 두 함종 core selftest를 확인했다.

CG/DDG idle/8Kh32AUTO/손상6조건의 EW/network/tactical/maneuver/attack/team 포함 상태/RNG exact, 세 owner1/8/16/64배속 결정성, 실제 VLS/RAM/Phalanx·채프/눌카/Harpoon·late actual-release guards·native RAF/WebGL 피격·UI/camera·저장/reset·기존 AI/공유를 새 원본에 직접 실행했다. 개별 native/natural fixture와 한계는 해당 report를 따른다. PERF_A 도색64모델 source texture1개·pixel/geometry parity와 수명도 유지했다. Actions는 dispatch하지 않았다.
