# Multi Ship A 성능 기준 기록

최종 HTML SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`를 고정된 E와 같은 seed·같은 full fixed tick 조건으로 순차 실행한 기록이다. 대기 240ticks/1배속, 8 Kh-32 AUTO 1920ticks/8배속, 초기 침수 25m³ 480ticks/16배속을 각 함종에 적용했다. terrain/GPU를 우회한 headless Chromium CPU fixture다. 적함 준비를 해상 실행한 성능 시험은 아니다.

tick.total은 최대 512개 최근 표본의 평균/p95/최대(ms)다. heap은 GC를 강제하지 않은 종료 시 CDP Runtime.getHeapUsage.usedSize(MiB) 관측이며 전체 GPU/프로세스 메모리가 아니다. 단일 측정의 차이를 속도 향상·메모리 누수 판단에 쓰지 않는다.

| 함종 | 조건 | 버전 | 표본 | avg ms | p95 ms | max ms | V8 used MiB |
|---|---|---|---:|---:|---:|---:|---:|
| DDG-119 | idle | E | 240 | 2.300 | 4.300 | 41.800 | 132.76 |
| DDG-119 | idle | A | 240 | 2.546 | 5.000 | 45.800 | 138.41 |
| DDG-119 | raid | E | 512 | 5.514 | 8.500 | 17.400 | 175.65 |
| DDG-119 | raid | A | 512 | 5.183 | 7.900 | 12.900 | 272.09 |
| DDG-119 | damaged | E | 480 | 1.424 | 3.100 | 52.400 | 127.48 |
| DDG-119 | damaged | A | 480 | 1.539 | 3.700 | 38.500 | 100.53 |
| CG-52 | idle | E | 240 | 2.150 | 3.700 | 73.200 | 115.28 |
| CG-52 | idle | A | 240 | 2.724 | 5.500 | 76.600 | 122.46 |
| CG-52 | raid | E | 512 | 5.497 | 8.200 | 15.300 | 156.44 |
| CG-52 | raid | A | 512 | 4.973 | 6.900 | 10.300 | 167.12 |
| CG-52 | damaged | E | 480 | 2.391 | 3.600 | 68.400 | 124.24 |
| CG-52 | damaged | A | 480 | 2.410 | 3.200 | 64.500 | 105.87 |

전체 subsystem·개체 수·난수·물리 snapshot은 `evidence/baseline-comparison.json.gz`에 보존했다. 모든 6쌍의 physical state와 RNG가 exact이며 오류가 없다. 종료 시 E/A 개체 수가 같았다. 대기는 hostile 0/track 0, raid는 hostile 8과 DDG track 28/CG track 24, 침수는 hostile 0/track 0이다. profiler의 sensors_tracks_ew 호출 수는 기존 한 tick의 두 측정 구간을 합치므로 world update를 두 번 한 뜻이 아니다.

## 실제 native 표시 기록

393×852 실제 선택 UI와 WebGL RAF를 SwiftShader 소프트웨어 렌더러로 실행했다. 제어된 관통 피해 뒤 native geometry가 실제 외판 구멍을 commit했고 후속 frame과 tick이 진행했다. 소프트웨어 draw 지연이 큰 환경으로 실제 모바일/하드웨어 FPS를 대신하지 않는다.

| 함종 | 완료 draw | 완료 tick | frame 표본 | avg ms | p95 ms | max ms |
|---|---:|---:|---:|---:|---:|---:|
| DDG-119 | 79 | 67 | 78 | 982.3 | 1256.3 | 2647.6 |
| CG-52 | 110 | 67 | 109 | 1284.9 | 1567.9 | 3676.5 |

원본 `evidence/native.json.gz`와 startup/damage screenshot을 보존했다. 페이지·console·simulation·presentation 오류는 0이다.

후속 최적화는 실함 2척을 활성화한 뒤 같은 cadence를 지키면서 후보 공간 색인/LOS cache·geometry/draw batching·particle 상한·표시 cache를 비교한다. AI/센서 권위값이나 물리 cadence를 낮추는 방식으로 이 기준을 우회하지 않는다.
