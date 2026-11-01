# GUN_B2 Phase 1 재현 안내

최종 결론과 제한은 [REPORT.md](REPORT.md)를 따른다. PHASE1_START의 승인된 1→5 순서로 구현했다. 원점 복구 기준은 AIR_ORIGIN_A 4c519…이며, 이전 Phase0/재진단 원시 자료와 승인 기대값은 보존한다.

새 게임은 루트의 Aegis_SIM_v48_WIP_GUN_B2.html 하나다. HTML ZIP과 보고서 ZIP을 분리한다. 보고서의 검증은 실제 제품 함수를 실행한다. 별도 근사 탄도/신관/피해 모델은 만들지 않았다. 공유 하네스까지 재현하려면 전체 저장소가 필요하다.

## 도구

Python 3.12, Playwright와 Chromium, matplotlib, Node/Acorn이 필요하다. 브라우저 실행 파일은 기존 browser_tools.launch 계약을 따른다. 이 호스트는 /usr/bin/chromium을 사용했다. 임시 공간이 부족하면 TMPDIR를 충분한 위치로 정한다. `PYTHONDONTWRITEBYTECODE=1`은 선택이다. Acorn은 NODE_PATH 또는 일반 node_modules에서 찾을 수 있게 설치한다.

- build.py: 불변4c519를 누적 패치하고 압축JS/manifest를 함께 생성한다. 확정 산포는 dispersion-constants.json에서 읽는다. 측정표가 있으면 함수/상수 hash guard를 통과해야 내장한다.
- runtime.js: 새5인치 게임 기능. nominal823·기존사통솔버·피해추첨/계수·SAM·RF/EKF는 보존한다.
- static.cjs + compact_source.cjs: 큰 literal data만 같은 UTF16길이 공백으로 파싱한 뒤 원문 오프셋에서 실제 함수문을 꺼낸다. 이 파싱용 문자열은 실행하지 않는다. 보호 지문과 전체4c 원문 역복원을 검사한다.
- calibrate.py: 16,459m native 앵커. `--derive`는 처음 한 번 쓴 역산 단계이며 재측정 명령이 아니다. 보존된 최종 σ를 다른 명중률로 바꾸지 않는다.
- verify_alignment.py / verify_window.py / verify_release_cache.py: 분리 정합, 대칭 AIR 창, 입력 revision 캐시 검사.
- verify_physics.py / verify_broad_phase.py: 신관·파편18건과12,000조건 빠른 거절 동등성.
- measure_range.py → analyze_range.py: 실제 native 발사/업데이트/신관/파편1440시도. 측정 시 함수·상수 hash를 고정한다. 실행 도중 제품을 다시 빌드하지 않는다.
- verify_native_trace.py: 실제 함수 소스 대조, 읽기 전용 계측 전후 native 결과/RNG 동일성6쌍, 누적 신호·최초 탐지·2ms 지연 로그.
- verify_final_pairs.py → analyze_pairs.py: 최종16회 OFF/ON, OFF8의4c 기록 정확비교 및 현재관측/원점/속도 정합.
- run_g7.py → collect_effects.py: 실제 자연 탐지+전체fixed tick 960회. 매 회 새 page/context. 중단 후 같은 HTML SHA에서만 누락 caseId를 이어 실행한다.
- run_regression.py / run_gun_regression.py: 기존 검사를 명시적 후보HTML과OFF/ON으로 실행. 원래 실패도 남긴다.
- reconcile_approvals.py / audit_ew_reuse.py / compare_native_sam.py: 기존 승인5건, 기존 B1의 정확한 inventory 차이 규칙, 실제4c300발 및 자연28조건 대조. 새 기대값이나 허용치는 승인하지 않는다.
- verify_measurement_guards.py: private 파일의 네 종류 불일치를 빌드 출력 전에 거절하는 음성 검사.
- verify_label.py: PC/폰의 메인/PiP 실제 글리프 픽셀로 두 링 라벨의 영역·간격 확인.

## 자료 구별

`evidence/g7`, `evidence/range-intercept`는 최종 측정이다. `density-frame-v1`은 좌표계 혼합을 발견해 폐기한 내부 후보, `cache-input-before`는 입력 revision 보완 전 후보다. 이들의 사격 성과를 최종 행렬에 섞지 않는다. 개발 중 로더/계측/자원 실패도 삭제하지 않는다. 보호 경로의 과거 시험을 재사용하는 경우 실제 SHA와 재사용 조건을 보고서에 적는다.

새 링은 PR 검토용 제안이며 자동9km·발사 권한을 바꾸지 않는다. ≥9km는 바깥 .05 하강 지점을 아직 측정하지 못했다는 뜻이다. 근거리 효과와 사계 제한을 별도로 확인해야 한다. main 병합 및 release/tag 생성은 이 단계에 포함하지 않는다.
