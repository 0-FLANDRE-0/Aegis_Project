# TRACK-B stabilization 비용 측정 결과

결과: **PASS · 비교 가능한 동일 workload**. 5구성×2회 역순, 각30초 warmup+2400 native fixed ticks를 실행했다. 실제 독점 실행 시간은 **223.49초(3.72분)**다. 표본·outlier를 제거하지 않았다.

| 구성 | 평균 tick ms | 1회 / 2회 평균 ms | 1회 / 2회 p95 ms | 기존 B 대비 평균 |
|---|---:|---:|---:|---:|
| track-a-off | 1.9041 | 1.9080 / 1.9002 | 3.00 / 2.90 | -5.62% |
| old-b-off | 2.0174 | 2.1522 / 1.8825 | 3.80 / 2.90 | +0.00% |
| stable-shadow-off | 1.9489 | 1.9035 / 1.9943 | 3.10 / 3.20 | -3.40% |
| stable-active-off | 2.1065 | 1.9595 / 2.2534 | 3.00 / 3.90 | +4.42% |
| stable-active-on | 2.1398 | 2.2659 / 2.0137 | 3.90 / 3.30 | +6.07% |

두 번의 짧은 표본에서 반복별 변동이 크다. 위 평균은 이번 실행의 관측값이며 안정적인 성능 향상·퇴행이나 성능 승인으로 확장하지 않는다. 일반1트랙 fixture이므로 별도 Node128 dense 최악 약42ms 한계도 해결한 것으로 보지 않는다.

| 검증 | 결과 |
|---|---|
| warmup 전체 state / 측정 후 전체 state / 원 A passive state | 각각10표본 해시 동일 |
| track count 이력 / 트랙·P·owner별 private RNG | 동일 |
| observer 수 / owner별 fixed tick 실행 | 1개 / 표본당2400회 |
| ENV hash / core selftest / 진단 sink / 조회 불변 | 모두 통과 |
| browser 오류 / 종료 후 browser main | 0 / 0 |
| 두 browser lease | 반환 후 비차단 재획득·반환 확인 |
| memory.events 증가 | low/high/max/oom/oom_kill/oom_group_kill 모두0 |

memory.events의 기존 누적값은 max2191, oom48, oom_kill8이며 이번 전후에 동일했다. 과거 누적값을 이번 측정의 오류로 처리하거나0으로 감추지 않았다.

메모리는 CDP **net live JS heap delta**만 보존했다. `stable-active-off` 2회차에는−14,597,164 bytes가 기록되었다. benchmark 반환값·상태 문자열과 GC/retention 영향이 섞일 수 있으므로 총 할당량 또는 churn으로 해석할 수 없다. 실제 GC 횟수는 계측하지 않았으며 HeapProfiler sampling·강제GC·할당 kernel wrapper를 사용하지 않았다.

제품·module·manifest·원 fixture·기대값은 바꾸지 않았다. 비용 PLAN의 source/proof22핀과 제품4핀을 종료 시점에 다시 확인했다. `COST_PLAN.md`와 `cost.py`는 실행 당시 입력으로 고정 보존한다.

- [원시 결과와 판정](evidence/cost/SUMMARY.json)
- [lease 반환·메모리·추가 검사](evidence/cost/POSTCHECKS.json)
- [표 CSV](evidence/cost/RESULT_TABLE.csv)
- [실행 계획과 출처 핀](evidence/cost/PLAN.json)

성능 승인 및 release 승인은 하지 않았다.
