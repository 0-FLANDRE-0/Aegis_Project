# R4 fresh 비용 측정 결과

범위 결과: **10/10 PASS · 비용 비교 eligible**. 실제 실행 시간은 **222.48초(3.71분)**다. 기존 R1/R3 결과를 새 측정값으로 쓰지 않고 A/B/R4 SHADOW/R4 ACTIVE OFF·ON을 각각 새 페이지에서2회, 역순으로 실행했다. 각 표본은 원 fixture30초 warmup 뒤 원 native fixed tick2400회다.

| 구성 | 평균 tick ms | 1회 / 2회 평균 ms | 1회 / 2회 p95 ms | 기존 B 대비 관측 평균 |
|---|---:|---:|---:|---:|
| track-a-off | 1.8963 | 1.9398 / 1.8528 | 3.00 / 2.80 | +1.09% |
| old-b-off | 1.8757 | 1.8595 / 1.8920 | 2.90 / 3.00 | +0.00% |
| r4-shadow-off | 1.8601 | 1.8143 / 1.9058 | 2.70 / 2.90 | -0.84% |
| r4-active-off | 1.7962 | 1.7825 / 1.8099 | 2.70 / 2.70 | -4.24% |
| r4-active-on | 2.4536 | 2.8336 / 2.0736 | 5.60 / 3.50 | +30.81% |

ON1회차의2.8336ms/p95 5.6ms와2회차2.0736ms/p95 3.5ms를모두보존했다. 표본·outlier 제거와추가재측정은하지않았다. 두번의짧은반복이므로 OFF의음수비율을안정적인성능향상으로, ON의평균을항상같은부하로단정하지않는다. 이수치는일반1트랙native simulation 비용이며3D FPS·실전다표적포화성능·128dense의별도한계(과거약42ms)를대신증명하지않는다.

| 통제 검사 | 결과 |
|---|---|
| warmup full state / 종료 full state / 원 A passive state | 각각10개표본해시동일 |
| track count 이력·track/P·owner별 private RNG | 동일 |
| observer 수 / owner별 fixed tick 실행 | 1개 / 표본마다2400회 |
| ENV hash·core·sink·조회 전후 상태 | 전부통과 |
| browser error / 종료 후 browser main | 0 / 0 |
| 두 browser lease | 반환후비차단재획득·반환확인 |
| source/proof·historical 입력핀 | 24개시작·종료재검증통과 |
| memory.events low/high/max/oom/oom_kill/group 증가 | 전부0 |

memory.events 누적값은시작과종료모두 max2662/oom50/oom_kill9였다. 과거누적값을이번비용오류로세거나0으로덮지않았다. 사전검사에서는두lease free, browser0, 1초표본의다른CPU활동0을확인했고 root가다른heavy작업을멈춘시간창에서실행했다.

CDP Runtime.getHeapUsage의전후 **net live heap delta**만남겼다. R4 SHADOW OFF1회차−6,878,344bytes, R4 ACTIVE ON2회차−8,717,952bytes도원값그대로다. GC/retention과benchmark 반환값·상태문자열이섞이는proxy이므로총할당량·churn·실제GC횟수로해석하지않는다. HeapProfiler sampling·강제GC·할당kernel wrapper는사용하지않았다.

비용 PASS는같은workload로비교할수있다는뜻이다. 후보의도메인·자연교전실패, 기존D1실패, legacy INCOMPLETE를승인하거나상태를변경하지않는다. 제품48b023c5/SHADOW3c7d2490, 원fixture·계수·기대값·허용오차를수정하지않았고성능·release승인도하지않았다.

- [전체 원시 결과와 모든 표본](evidence/cost-r4/SUMMARY.json)
- [후속 lease·host·state 검사](evidence/cost-r4/POSTCHECKS.json)
- [표 CSV](evidence/cost-r4/RESULT_TABLE.csv)
- [실행 전 독점 검사](evidence/cost-r4/EXCLUSIVE_PREFLIGHT.json)
- [고정된 계획과 출처](evidence/cost-r4/PLAN.json)
