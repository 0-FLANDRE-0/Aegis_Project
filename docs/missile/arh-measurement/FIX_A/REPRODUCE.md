# ARH Measurement FIX_A 재현

저장소 루트에서 실행한다. Chromium은 관리형 환경에서 네트워크 권한이 있는 샌드박스 프로필이 필요할 수 있다.

```bash
node docs/missile/arh-measurement/FIX_A/build_variants.cjs
python docs/missile/arh-measurement/FIX_A/verify_contracts.py
python docs/missile/arh-measurement/FIX_A/run_flight_compare.py
python docs/missile/arh-measurement/FIX_A/analyze_flights.py
python docs/missile/arh-measurement/FIX_A/run_targeted_regression.py
node docs/missile/arh-measurement/FIX_A/run_common_final.cjs
python docs/missile/arh-measurement/FIX_A/run_natural_final.py
```

종료기 전체 회귀:

```bash
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/release/normal.json --cases docs/missile/termination/A/cases/normal.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/release/dual.json --cases docs/missile/termination/A/cases/dual.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/release/fault.json --cases docs/missile/termination/A/cases/fault.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/release/battery.json --cases docs/missile/termination/A/cases/battery.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/release/request.json --cases docs/missile/termination/A/cases/release-request.json --batch 8
```

프로젝트 회귀:

```bash
python docs/pip/B/run_domain.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/domain --parallel 2
python docs/missile/range/A/collect_domain.py docs/missile/arh-measurement/FIX_A/domain docs/missile/arh-measurement/FIX_A/domain-summary.json || true
python docs/pip/B/verify_ui.py Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html docs/missile/arh-measurement/FIX_A/ui
python docs/missile/arh-measurement/FIX_A/verify_clock.py
node docs/missile/arh-measurement/FIX_A/verify_static.cjs
python docs/missile/arh-measurement/FIX_A/verify_smoke.py
```

그래프와 요약:

```bash
MPLCONFIGDIR=/tmp/matplotlib-arh-fix-a python docs/missile/arh-measurement/FIX_A/plot_flights.py
node docs/missile/arh-measurement/FIX_A/finalize_evidence.cjs
```

도메인 collector는 기존 6개 실패를 그대로 보고하므로 exit 1이 정상 기준이다. 결과는 정확히 `414/420`이어야 한다.
