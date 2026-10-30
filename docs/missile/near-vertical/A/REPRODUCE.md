# NEAR_VERTICAL_PATH_FIX_A 재현

저장소 루트에서 실행한다. Node 24, Python 3.12, Acorn 8.19, Playwright/Chromium을 사용했다. Chromium 임시 프로필은 공간 제약 때문에 `TMPDIR=/dev/shm`으로 실행했다.

```bash
export NODE_PATH="$PWD/docs/performance/F/node_modules"
node docs/missile/near-vertical/A/build.cjs
node docs/missile/near-vertical/A/test_geometry.cjs
node docs/missile/near-vertical/A/test_static.cjs
node docs/missile/near-vertical/A/run_near_vertical.cjs
python docs/missile/near-vertical/A/run_product_one.py --variant BASE --seed-index 1
python docs/missile/near-vertical/A/run_product_one.py --variant FINAL --seed-index 1
python docs/missile/near-vertical/A/aggregate_product_rf.py
node docs/missile/near-vertical/A/run_common.cjs
python docs/missile/near-vertical/A/run_natural.py
python docs/missile/near-vertical/A/run_release_chunk.py --kind normal --start 0 --end 48
python docs/missile/near-vertical/A/aggregate_release_chunks.py
python docs/missile/near-vertical/A/compare_release.py
node docs/missile/near-vertical/A/export_equivalence.cjs
python docs/missile/near-vertical/A/verify_equivalence.py
python docs/missile/near-vertical/A/verify_clock.py
python docs/missile/near-vertical/A/verify_smoke.py
python docs/missile/near-vertical/A/verify_world120.py
```

300발 release는 `release/parts`의 기록처럼 호스트 실행 상한을 피하기 위해 독립 chunk로 실행하고 원래 순서로 병합한다. 도메인 회귀는 `docs/pip/B/run_domain.py`와 `docs/missile/range/A/collect_domain.py`를 사용한다. collector의 exit 1은 기존 6개 raid assertion을 보존한 예상 결과이며 정확히 414/420이어야 한다.

`product-rf-*`는 실제 브라우저/VLS/RF/EKF 경로지만 함 사통 트랙과 표적 직선 운동을 통제한다. `near-vertical-results`는 선택 HTML 실제 함수를 추출한 격리 capsule이다. 두 범위를 합쳐 자연 센서 전체 전장 인증으로 부르지 않는다.
