# B2A 재현 안내

현재 결론은 [REPORT.md](REPORT.md)를 따른다. 최초 입력은 INSTRUCTIONS.md이며 기준 commit c1d17cee, HTML c48c2396…이다. 먼저 derive_matching.py와 report_matching.py로 전체 기폭 탄속 중앙값/중심각을 확정했다.20~80° 조건을 통과한 후 build.py로 세 항목만 적용했다.

Python3.12/Playwright/Chromium, Node+Acorn, matplotlib가 필요하며 공통 하네스를 쓰는 전체 저장소가 필요하다. 임시 파일은 /dev/shm, MPLCONFIGDIR도 충분한 임시 공간으로 설정한다. NODE_PATH에 Acorn을 설치한 node_modules가 필요하다. 브라우저는 기존 browser_tools.launch 계약을 따른다.

실행 순서: build.py → calibrate.py(derive금지,검증만) → measure_range.py와 run_g7.py → verify_surface.py 및 adapted/ 지정 회귀 → reconcile_pairs.py/collect_regression.py → analyze_range.py/analyze_results.py → build.py --embed → static.cjs/audit_scope.cjs → build_reuse_ledger.py/plot_results.py/write_report.py → finalize_docs.py → package.py. build.py --embed는 실제측정 native6함수/공장/spec/산포 지문이 다르면 거절한다. 측정 중 제품을 재빌드하지 않는다.

기존 사이트 어댑터를 test_support/sitecustomize.py로 사용한다. B2_PHASE1_REGRESSION=1, B2_MODE=ON, B2_OUT=새출력폴더, PYTHONPATH=phase1a/test_support로 실행하고 테스트의 AutoAA 조건을 명시한다. 원래 B1/MAP_D 시험 파일과 승인값은 편집하지 않는다. prepare_tests.py가 승인된 단언 교체의 private 실행본과 diff를 생성한다. 전체 실행은 deadline.py의3시간 상한을 지키며, 과거 실행시각을 바꿔 같은 제한을 숨기지 않는다. 새 재현은 새 실행시각/별도 증거 폴더를 명시해야 한다.

REPORT의 실제 실행/재사용/최초 RF-mock 실패/최종2미통과를 구별한다. 표를 맞추는 자동 파라미터 탐색·seed선택·전체 ENV 재측정은 하지 않는다. direct GitHub ZIP은 패키징 commit에 고정하고 원격 영수증은 후속 커밋으로 남긴다.
