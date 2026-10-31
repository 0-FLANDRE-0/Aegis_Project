"""Update current status while keeping the pre-implementation reports immutable."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;B=P.parent
j=lambda f:json.loads((P/f).read_text())
assert j('evidence/effects-summary.json')['complete'] and j('evidence/g7-repeat.json')['pass'] and j('evidence/product-invariants.json')['pass']
old=json.loads((B/'BUILD_STATUS.json').read_text());previous=old.get('previousPostOriginStatus',old)
build=j('build.json');effects=j('evidence/effects-summary.json')
status={'schema':'AEGIS_GUN_B2_PHASE1_STATUS_1','phase':'IMPLEMENTED_MEASURED_DRAFT_REVIEW','baselineCommit':'cce180255e0f76b804a2ae6a3b6078aec2f9dea8','baselineHtmlSha256':build['baselineSha256'],'productHtmlSha256':build['htmlSha256'],'measurementHtmlSha256':j('measurement-build.json')['htmlSha256'],'gameCodeChanged':True,'phase1Implemented':True,'newGameHtmlProduced':True,'g7Trials':960,'rangeAttempts':1440,'rangeActualShots':1400,'anchorFinalShots':400,'rangeSigmaM':j('evidence/dispersion-final/validation.json')['rangeSigmaM'],'matched60HpWorseCases':len(effects['worseMatchedHpCases']),'newExpectationsApproved':0,'newOnBehavioralDifferences':24,'domainChecksPerMode':420,'domainExistingApprovalsOnly':True,'canonicalUiChecksPerMode':88,'mainMergeByThisTask':False,'releaseOrTagCreated':False,'currentReport':'docs/gun/B2/phase1/REPORT.md','reviewItems':['New ON behavioral expectations not approved','Near-range MFF detection/delay/fragment geometry has low effect','Outer .05 decline not reached by 9km; ring right-censored proposal, not a certified effective interval','29 of matched 60 trials have lower ship HP; not attributed wholesale to RNG'],'previousPostOriginStatus':previous}
(B/'BUILD_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
(B/'STATUS.md').write_text('''# GUN_B2 상태

**Phase 1 구현·측정 완료 · gun-b2 PR 검토용**

현재 관측 기반 발사 정합, 독립 산포, AIR 대칭 포인팅, 5인치 전용 신호 누적 신관·파편 띠를 승인 순서 1→5로 구현했다. OFF 기준은 AIR_ORIGIN_A(4c519…)다.

필수 자연 탐지 행렬 960회, 단발 거리 측정 1440시도/1400발, 16,459m 최종 앵커 400발을 완료했다. 상세 검수·원시 실패·재사용 범위는 [최종 보고](phase1/REPORT.md)에 있다. 기존 승인 5건 외 기대값·허용치 갱신은 없다.

**검토 사항:** 기존 같은 60회 대비 HP 악화 29회, 새 ON 동작 차이 24항목, 근거리 MFF 효과가 낮은 구간, 외측 .05 하강점을 찾지 못한 ≥9km 검열 링 제안이다. 전체 전투 결과 개선이나 모든 원시 검사의 통과를 주장하지 않는다. 피해 RNG/Pk 계수를 맞추지 않았다. main 병합/release/tag는 하지 않는다.

- [보고서](phase1/REPORT.md) · [변경 결과 분류](phase1/DIFFERENCES.md)
- [수치·계산 방식](phase1/PARAMETERS.md) · [시험 규약](phase1/PROTOCOL.md)
- [체크섬](phase1/CHECKSUMS.sha256) · [패키지 영수증](phase1/PACKAGE_RECEIPT.json)
- [기존 원점 복구 후 재진단/착수 보고](PHASE1_START.md) — 당시 상태를 그대로 보존
- [과거 Phase0](PHASE0.md) — 현재 제품 상태가 아님

원격 readback 영수증은 산출물 push 후 후속 커밋의 phase1/REMOTE_READBACK.json에 남긴다.
''')
(B/'README.md').write_text('''# GUN_B2

현재 산출물은 **Phase 1 구현·측정본**이다. [상태](STATUS.md), [최종 보고](phase1/REPORT.md), [브라우저용 보고서](phase1/INDEX.html), [재현 안내](phase1/README.md)를 먼저 읽는다.

게임 HTML은 저장소 루트 Aegis_SIM_v48_WIP_GUN_B2.html이다. downloads/Aegis_SIM_v48_WIP_GUN_B2_HTML.zip과 downloads/Aegis_SIM_v48_WIP_GUN_B2_PHASE1_REPORT.zip으로 게임/리포트를 분리한다. 보고서 ZIP에는 원시 수치·CSV·로그·도구·그림·대표 화면을 넣고, 중복 회귀 PNG 전체는 저장소 원본과 phase1/MEDIA_INDEX.tsv에 보존한다.

기존 PHASE0.md, PHASE1_START.md, post-origin/, evidence/와 승인 기록은 그 단계의 역사 자료다. 현재 제품에 새 기능이 없다는 과거 문장은 당시 상태이며 수정하지 않았다. 새 기대값은 승인하지 않았고 main 병합/release/tag는 하지 않는다.
''')
(B/'INDEX.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN_B2 current report</title><style>body{font:14px/1.7 system-ui;max-width:1000px;margin:30px auto;padding:16px}a{display:block;margin:10px 0}</style><h1>GUN_B2 — Phase 1</h1><p>구현·측정 완료, PR 검토용. 새 ON 동작 차이·HP 악화·근거리 효과와 검열 링은 최종 보고서에 공개했다.</p><a href="phase1/INDEX.html">현재 전체 보고서·그림</a><a href="phase1/REPORT.md">현재 보고서 Markdown</a><a href="phase1/DIFFERENCES.md">검사 차이 분류</a><a href="STATUS.md">상태</a><a href="PHASE1_START.md">역사 자료: 원점 복구 후 착수 보고</a><a href="PHASE0.md">역사 자료: Phase 0</a></html>''')
notes=P/'development/notes';notes.mkdir(parents=True,exist_ok=True)
for name in ['WORKING_STATE.md','CHECKPOINT_CURRENT.md']:
 f=P/name
 if f.exists():f.rename(notes/name)
print(json.dumps(status,ensure_ascii=False))
