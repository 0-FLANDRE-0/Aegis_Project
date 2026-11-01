from pathlib import Path
import json
P=Path(__file__).resolve().parent;B=P.parent;q=json.loads((P/'BUILD_STATUS.json').read_text());old=json.loads((B/'BUILD_STATUS.json').read_text());q['previousB2Status']=old.get('previousB2Status',old);q['currentReport']='docs/gun/B2/phase1a/REPORT.md';q['reviewRequired']=['Harpoon nativeFinish/journal2 assertions remain nonpass: actual native fragmentation MISS','Outer .05 decline not reached by9km; ring is right-censored','Per-seed G7 HP changes remain recorded, not universally attributed to RNG'];(B/'BUILD_STATUS.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
(B/'STATUS.md').write_text('''# GUN_B2 현재 상태

**B2A 세 항목 구현·지정 측정 완료 · PR61 검토용**

고정 탐지 중심45.9437557353°, AIR 기계 정렬 반폭6.25m, 선회σ=고각σ를 적용했다. 앵커400발, 단발1440시도/1400발, 수상90발, 자연G7 120회와 지정5인치 회귀를 완료했다. 원래 CG 단발4개 기대는 그대로 통과했다.

**남은 검토:** 하푼 탐지/파편 도달은 성립했지만 실제 피해MISS로 nativeFinish/종료로그2개 기대는 미통과다. 통과시키기 위한 시드·거리·피해계수 변경은 하지 않았다. ≥9km 링은 검열값이며 전 구간 보증이 아니다.

- [현재 보고서](phase1a/REPORT.md) · [브라우저용 보고](phase1a/INDEX.html)
- [적용 전 계산](phase1a/MATCHING.md) · [시험 단언 교체](phase1a/ASSERTION_MIGRATIONS.json)
- [소스 감사](phase1a/evidence/scope.json) · [재사용 장부](phase1a/TEST_REUSE.json)
- [체크섬](phase1a/CHECKSUMS.sha256) · [원격 영수증](phase1a/REMOTE_READBACK.json)
- [역사 자료: Phase1](phase1/REPORT.md) · [착수 보고](PHASE1_START.md)

원래 Phase1 자료와 승인 파일은 그대로 보존했다. main 병합/release/tag는 하지 않는다.
''')
(B/'README.md').write_text('''# GUN_B2 / B2A

현재 제품은 B2A 누적본이다. [현재 상태](STATUS.md), [B2A 최종 보고](phase1a/REPORT.md), [브라우저용 보고](phase1a/INDEX.html), [재현 안내](phase1a/README.md)를 읽는다.

루트 Aegis_SIM_v48_WIP_GUN_B2.html을 갱신했다. downloads/Aegis_SIM_v48_WIP_GUN_B2A_HTML.zip과 downloads/Aegis_SIM_v48_WIP_GUN_B2A_REPORT.zip으로 게임/보고서를 분리한다. 기존 B2 ZIP과 phase1/ 원시 자료는 역사 자료로 보존한다.

CG 단발4개는 원래 단언을 통과했지만 하푼 native 피해MISS에 따른2개 단언은 미통과로 공개했다. 피해/RF/Pk 계수나 시드·거리로 결과를 맞추지 않았다. PR61을 갱신하고 병합은 사용자에게 맡긴다.
''')
(B/'INDEX.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN_B2A</title><h1>GUN_B2A</h1><p>세 항목 구현·지정 측정 완료. 남은 하푼2개 단언과 검열 링은 보고서에 공개했다.</p><a href="phase1a/INDEX.html">현재 전체 보고서</a> · <a href="phase1a/REPORT.md">Markdown</a> · <a href="STATUS.md">상태</a> · <a href="phase1/INDEX.html">이전 Phase1</a></html>''')
(P/'README.md').write_text('''# B2A 재현 안내

현재 결론은 [REPORT.md](REPORT.md)를 따른다. 최초 입력은 INSTRUCTIONS.md이며 기준 commit c1d17cee, HTML c48c2396…이다. 먼저 derive_matching.py와 report_matching.py로 전체 기폭 탄속 중앙값/중심각을 확정했다.20~80° 조건을 통과한 후 build.py로 세 항목만 적용했다.

Python3.12/Playwright/Chromium, Node+Acorn, matplotlib가 필요하며 공통 하네스를 쓰는 전체 저장소가 필요하다. 임시 파일은 /dev/shm, MPLCONFIGDIR도 충분한 임시 공간으로 설정한다. NODE_PATH에 Acorn을 설치한 node_modules가 필요하다. 브라우저는 기존 browser_tools.launch 계약을 따른다.

실행 순서: build.py → calibrate.py(derive금지,검증만) → measure_range.py와 run_g7.py → verify_surface.py 및 adapted/ 지정 회귀 → reconcile_pairs.py/collect_regression.py → analyze_range.py/analyze_results.py → build.py --embed → static.cjs/audit_scope.cjs → build_reuse_ledger.py/plot_results.py/write_report.py → finalize_docs.py → package.py. build.py --embed는 실제측정 native6함수/공장/spec/산포 지문이 다르면 거절한다. 측정 중 제품을 재빌드하지 않는다.

기존 사이트 어댑터를 test_support/sitecustomize.py로 사용한다. B2_PHASE1_REGRESSION=1, B2_MODE=ON, B2_OUT=새출력폴더, PYTHONPATH=phase1a/test_support로 실행하고 테스트의 AutoAA 조건을 명시한다. 원래 B1/MAP_D 시험 파일과 승인값은 편집하지 않는다. prepare_tests.py가 승인된 단언 교체의 private 실행본과 diff를 생성한다. 전체 실행은 deadline.py의3시간 상한을 지키며, 과거 실행시각을 바꿔 같은 제한을 숨기지 않는다. 새 재현은 새 실행시각/별도 증거 폴더를 명시해야 한다.

REPORT의 실제 실행/재사용/최초 RF-mock 실패/최종2미통과를 구별한다. 표를 맞추는 자동 파라미터 탐색·seed선택·전체 ENV 재측정은 하지 않는다. direct GitHub ZIP은 패키징 commit에 고정하고 원격 영수증은 후속 커밋으로 남긴다.
''')
(P/'PROTOCOL.md').write_text('''# 시험 규약

- 모든 미사일·함포 수치는 게임용 SIM_TUNED다. 실제 무기 성능과 비교하지 않는다.
- 전체 벽시계 상한3시간. TASK_CLOCK.json은 검토 시작을 보수적으로 포함한다. 브라우저 동시 최대2, 자원 실패 재시도0.
- 원점·센서·비행·신관·피해를 별도 근사 모델로 대체하지 않고 실제 선택 HTML의 native함수를 실행한다. 측정 함수.toString SHA와 빌드지문을 확인한다.
- 산포: native16459m 무풍400발, 같은seed/serial400반복, 공칭823·MV/elevσ고정. globalRNG소비0, native착탄동등성0m.
- 단발: DDG/CG×0/90°×1~9km×592001~59204040시드=1440시도. 이상 지속 관측, Kh35U10m/280m/s, native발사/탄도/신호누적/신관/파편/Pk. CG정면1km40건 사계 미발사를 비명중으로 넣지 않는다.
- G7: DDG/CG×0/90°×1·4기×419010~41902415시드, AutoAA ON120회. 새page/context마다 자연RF+전체fixed tick1/60. B2기능은모두ON. 물리ASM 참조의 실제결과/첫3km진입/사망tick만 실적에 쓴다. legacy 혼입카운터는 보존만한다.
- G7 OFF120 및 지정 외회귀는 TEST_REUSE.json의 sourceguard 아래 Phase1 원본을 재사용한다. 새ON120과 같은B2ON120은 동일입력으로비교한다. 전부새실행으로표기하지않는다.
- 수상: DDG/CG×5/10/15km×723001~72301515시드 ON90회. 첫발명중과전체fixture PASS를구분하고 meaningfulMovingFrame 기대를바꾸지않는다.
- 단언: 사용자§5의12/2/5/1/4개범위만교체한다. 4개CG단발은그대로다. fixture의 누락RF메타데이터는 기존native .06을보충하고 productRF계수는유지한다. 실제MISS가나온 하푼2개단언은미통과로남기며다른seed/통과거리를고르지않는다.
- CIWS 이상은참고통계만기록한다. main/release/tag는변경하지않는다.
''')
print('Current status/README updated')
