from pathlib import Path
from datetime import datetime,timezone,timedelta
import html,json,hashlib
P=Path(__file__).resolve().parent;B=P.parent;R=P.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest();build=json.loads((P/'build.json').read_text());reg=json.loads((P/'evidence/regression-summary.json').read_text());g=json.loads((P/'evidence/g7-summary.json').read_text());scope=json.loads((P/'evidence/scope.json').read_text());task=json.loads((P/'TASK_CLOCK.json').read_text());now=datetime.now(timezone.utc);deadline=datetime.fromisoformat(task['deadlineUtc']);status={'schema':'AEGIS_GUN_B2B_STATUS_1','implemented':True,'finishedUtc':now.isoformat(),'finishedKst':now.astimezone(timezone(timedelta(hours=9))).isoformat(),'within3Hours':now<=deadline,'baselineCommit':'fa0fdde96dfcc7c0655f8ba8bc3e7a903b4591f4','baselineHtmlSha256':'9515e70cb88f7caac8dd9c0b618a104a878882a5a1c06f0967059150e2b7d516','htmlSha256':build['htmlSha256'],'rangeAttempts':1440,'rangeActualReleases':1400,'g7FreshTrials':g['freshOnTrials'],'g7HpWorse':g['hpWorse'],'g7HpBetter':g['hpBetter'],'g7HpSame':g['hpSame'],'regressionPass':reg['pass'],'scopePass':scope['pass'],'mainMerged':False,'releaseOrTagCreated':False,'reviewRequired':['25kg equivalent casing and geometry remain SIM_TUNED','Existing target V50 reference mass was undocumented; 1.1g FSP mapping remains SIM_TUNED','Both measured rings are right-censored at >=9km']};assert status['within3Hours']and status['regressionPass']and status['scopePass'];(P/'BUILD_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');(B/'BUILD_STATUS.json').write_text(json.dumps({'current':status,'currentReport':'docs/gun/B2/phase1b/REPORT.md','previousB2A':json.loads((B/'phase1a/BUILD_STATUS.json').read_text())},ensure_ascii=False,indent=2)+'\n')
(P/'README.md').write_text('''# GUN_B2B 재현 안내

현재 결론은 [REPORT.md](REPORT.md), 입력은 [INSTRUCTIONS.md](INSTRUCTIONS.md), 출처와 남은 가정은 [SOURCES.md](SOURCES.md)를 따른다. 기준은 gun-b2 `fa0fdde9`와 B2A HTML `9515e70c…`이다.

재현 순서는 `derive_model.py` → `build.py` → `freeze_fingerprints.cjs` → `unit_runtime.py` → `measure_range.py`와 `run_g7.py`(동시 최대2브라우저) → `prepare_tests.py`/`run_regressions.py` → `analyze_range.py`/`analyze_results.py` → `build.py --embed` → `audit_scope.cjs` → `build_reuse_ledger.py` → plot/report/docs/package다. 임시파일은 `/dev/shm`을 쓰고 `deadline.py`의 3시간 상한을 지킨다.

측정 빌드와 최종 빌드는 표시용 range table만 다르다. `measurement-build.json`의 native source SHA로 실제 제품 함수를 확인한다. 기존 B1/MAP_D 원본 테스트는 수정하지 않으며 `prepare_tests.py`가 private 실행본과 diff를 만든다. physical-adapter의 두 승인 단언 외 기대값·허용오차는 바꾸지 않는다.

모든 미사일·함포 수치는 게임용 `SIM_TUNED`다. 실제 무기 성능과 비교하지 않는다. 결과에 맞춘 파라미터 탐색이나 seed 선택은 금지한다.
''')
(P/'PROTOCOL.md').write_text('''# GUN_B2B 시험 규약

- 5인치 전용 탄체/Gurney/Mott/질량별 관통/Pk와 고정 신관 중심만 변경한다.
- 몸체90°±20° 판정, 도달시간, 발사정합, 산포, AIR 창, 신호누적, 피해 RNG는 유지한다.
- 단발: DDG/CG × 0/90° × 1–9km × 40시드 = 1,440시도. CG정면1km 사계 보류는 비명중으로 넣지 않는다.
- G7: DDG/CG × 0/90° × 1·4기 × 15시드 = 120회, AutoAA ON, 자연 RF와 전체 fixed tick. B2A 동일120회와 비교한다.
- 수상 첫 발, SAM/common UI/EW/H3/domain/world120은 소스 가드 아래 재사용하며 새 실행으로 표기하지 않는다.
- physical-adapter 두 단언만 native 피해 경로 실행과 KILL/MISS/DAMAGED 결과 기록으로 교체한다. seed·거리·계수는 유지한다.
- 벽시계3시간, 브라우저 동시 최대2, 결과 적합을 위한 재조정0, main/release/tag0.
''')
report=(P/'REPORT.md').read_text();page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN_B2B report</title><style>body{font:14px/1.7 system-ui;max-width:1500px;margin:25px auto;padding:0 16px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 monospace}img{max-width:100%;height:auto}.note{background:#eef6ff;padding:12px}</style><h1>GUN_B2B</h1><p class="note">5인치 Mott 게임 모델과 지정 측정 완료. 실물 성능 주장이 아니며 남은 SIM_TUNED 가정은 보고서에 공개했다.</p><p><a href="REPORT.md">보고서</a> · <a href="SOURCES.md">출처</a> · <a href="MATCHING.md">중심각 계산</a> · <a href="GUN_B2B.diff">게임 diff</a></p>'''
for name,title in [('mott-bins','Mott 구간 수·질량'),('unit-pk','단위 Pk'),('single-shot-pk','단발 Pk B2A/B2B'),('g7-comparison','G7 B2A/B2B')]:page+=f'<h2>{title}</h2><a href="plots/{name}.svg"><img src="plots/{name}.png" alt="{title}"></a>'
page+='<pre>'+html.escape(report)+'</pre></html>';(P/'INDEX.html').write_text(page)
(B/'STATUS.md').write_text(f'''# GUN_B2 현재 상태

**B2B 5인치 Mott 게임 모델·지정 측정 완료 · PR61 검토용**

25kg 등가 탄체, Comp B Gurney/Mott 공개 상수, 10개 질량 구간과 질량별 관통을 5인치 전용 경로에 적용했다. 신관 중심은 B2A 실제 기폭 속도 중앙값으로 {json.loads((P/'model-parameters.json').read_text())['fuzeMatching']['fixedPolarCenterDeg']:.6f}°로 재계산했다.

단발1,440시도/1,400발, 자연G7 120회, 지정5인치 회귀를 완료했다. SAM 보호함수281/281과 수상HE 경로는 바이트 동일하다. 양 함정 링은 ≥9km 우측 검열값이다.

- [현재 보고서](phase1b/REPORT.md) · [브라우저용 보고](phase1b/INDEX.html)
- [출처와 가정](phase1b/SOURCES.md) · [적용 전 계산](phase1b/MATCHING.md)
- [소스 감사](phase1b/evidence/scope.json) · [재사용 장부](phase1b/TEST_REUSE.json)
- [이전 B2A](phase1a/REPORT.md)

main 병합/release/tag는 하지 않는다.
''')
(B/'README.md').write_text('''# GUN_B2 / B2B

현재 제품은 B2B 누적본이다. [현재 상태](STATUS.md), [최종 보고](phase1b/REPORT.md), [브라우저용 보고](phase1b/INDEX.html), [재현 안내](phase1b/README.md)를 읽는다.

루트 `Aegis_SIM_v48_WIP_GUN_B2.html`을 갱신했다. 게임 ZIP과 원시 검증·보고서 ZIP을 `downloads/`에 따로 둔다. B2A/Phase1 자료는 역사 자료로 보존한다.

공개값과 `SIM_TUNED` 값을 분리했고 결과에 맞춰 수치를 다시 고르지 않았다. PR61만 갱신하며 병합은 사용자에게 맡긴다.
''')
print('docs finalized',status['finishedKst'])
