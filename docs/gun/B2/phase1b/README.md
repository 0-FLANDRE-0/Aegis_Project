# GUN_B2B 재현 안내

현재 결론은 [REPORT.md](REPORT.md), 입력은 [INSTRUCTIONS.md](INSTRUCTIONS.md), 출처와 남은 가정은 [SOURCES.md](SOURCES.md)를 따른다. 기준은 gun-b2 `fa0fdde9`와 B2A HTML `9515e70c…`이다.

재현 순서는 `derive_model.py` → `build.py` → `freeze_fingerprints.cjs` → `unit_runtime.py` → `measure_range.py`와 `run_g7.py`(동시 최대2브라우저) → `prepare_tests.py`/`run_regressions.py` → `analyze_range.py`/`analyze_results.py` → `build.py --embed` → `audit_scope.cjs` → `build_reuse_ledger.py` → plot/report/docs/package다. 임시파일은 `/dev/shm`을 쓰고 `deadline.py`의 3시간 상한을 지킨다.

측정 빌드와 최종 빌드는 표시용 range table만 다르다. `measurement-build.json`의 native source SHA로 실제 제품 함수를 확인한다. 기존 B1/MAP_D 원본 테스트는 수정하지 않으며 `prepare_tests.py`가 private 실행본과 diff를 만든다. physical-adapter의 두 승인 단언 외 기대값·허용오차는 바꾸지 않는다.

모든 미사일·함포 수치는 게임용 `SIM_TUNED`다. 실제 무기 성능과 비교하지 않는다. 결과에 맞춘 파라미터 탐색이나 seed 선택은 금지한다.
