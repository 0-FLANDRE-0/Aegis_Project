# TRACK-B stabilization 비용 검증 계획

상태: **실행 대기**. `cost.py --plan`은 파일·해시와 계획만 확인한다. 브라우저는 만들지 않는다. root가 두 browser lane과 광역 CPU 작업을 멈춘 독점 시간창을 명시적으로 지정한 뒤에만 `--run --go-reference ...`를 실행한다.

## 구성과 실행량

| 구성 | 적용 정책 | 진단 |
|---|---|---|
| TRACK-A | 기존 TRACK-A | OFF |
| 기존 B ACTIVE | frozen B ACTIVE | OFF |
| 새 STABLE SHADOW | 기존 B ACTIVE 소비 + 새 solver 계산 | OFF |
| 새 STABLE ACTIVE | 새 stabilization 정책 | OFF |
| 새 STABLE ACTIVE | 새 stabilization 정책 | A·B trace ON |

1회차는 표의 순서, 2회차는 역순이다. 각 표본은 새 브라우저·새 페이지를 사용한다. 원 A의 CG-52 moving-HELO fixture(seed 419010, observe=false)를 그대로 30초 warmup한 뒤 원 A `__TRACK_RUNTIME_A__.bench(2400)`를 호출한다. 10표본 합계는 측정 24,000 fixed ticks와 warmup 18,000 fixed ticks다. 표본당 함 관측자는 기존 fixture와 같은 1개다.

기존 B의 quiescent 최종 CPU 6표본 실측은 합계 약 103.7초, 표본당 약 17.3초였다. 이를 실행시간 추정에만 사용하면 10표본 약 173초이며, 새 test-copy 준비·상태 비교·저장까지 **독점 창 약 3.5~5분**을 예상한다. lock 대기 시간과 광역 작업 재개 시간은 포함하지 않는다. 과거 CPU·heap 원시값을 새 결과로 재사용하지 않는다.

## 재사용·보존 계약

- 원본 `B/measure_cost_final.py`의 browser lease, 프로세스 사전점검, 자원 조회와 원 A benchmark/harness를 그대로 재사용한다. 기존 B/A 파일과 fixture·기대값을 편집하지 않는다.
- 원 A passive state와 기존 B `FULL_STATE_HELPER`를 측정 밖에서 읽는다. body·track 상태·P·owner별 RNG를 포함한 원시 상태를 모두 저장한다. 진단 상태는 비교 대상 game state에 넣지 않는다.
- 10표본의 warmup 상태, 측정 후 상태, benchmark가 반환한 A 상태가 각각 같아야 CPU 비교를 허용한다. owner당 2400회 갱신, 원 core selftest 0, ENV hash 일치와 조회 전후 상태 불변도 확인한다.
- 상태가 다르면 결과를 `NOT_COMPARABLE`로 표시하고 차이를 보존한다. 필드 제외·허용 오차·기대값 갱신으로 비교를 성립시키지 않는다.
- 측정 직후 원 benchmark 반환값을 보조 조회보다 먼저 압축 저장한다. 표본·outlier는 삭제하지 않는다.
- 제품·모듈·manifest·원 도구 해시를 PLAN에 고정한다. 실행 직전에 달라졌으면 중단하며, 기존 실행 자료를 덮어쓰지 않는다.

## 측정치와 한계

CPU는 실제 fixed tick의 mean/median/p95를 표본별로 보고한다. 두 반복의 개별값과 평균을 함께 둔다. 두 번의 짧은 반복만으로 안정적인 성능 향상이나 자동 승인을 주장하지 않는다.

메모리는 CDP `Runtime.getHeapUsage`의 전후 **net live heap delta**만 보고한다. benchmark 결과·상태 문자열도 포함되며 GC 때문에 음수가 될 수 있다. 총 할당량·GC 포함 churn으로 해석하지 않는다. HeapProfiler sampling, allocation kernel wrapper, 강제 GC는 사용하지 않는다.

이 fixture는 일반적인 1트랙 workload다. 별도 Node 128 dense 그래프의 최악 약 42ms 한계는 그대로 남긴다. 이 CPU 표가 해당 포화 조건의 비용이나 60Hz 충족을 대신 증명하지 않는다. 새 포화 입력·추가 할당 시험·제품 계수 변경은 하지 않는다.

## 명령과 산출물

```bash
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_stabilization/cost.py --plan
# root의 독점 실행 GO를 받은 뒤에만:
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_stabilization/cost.py --run --go-reference '<독점 실행 지시 식별문>'
```

`evidence/cost/PLAN.json`, lease/preflight 영수증, 각 표본의 원 benchmark·tick 비용·A 상태·전체 상태·heap 조회값, full-state 차이(있을 때), `SUMMARY.json`을 남긴다. 게임 HTML·센서·비행·발사·피해 코드와 기대값은 변경하지 않는다.
