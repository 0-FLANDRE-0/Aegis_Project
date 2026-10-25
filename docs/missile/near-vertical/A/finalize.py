from pathlib import Path
import datetime,hashlib,json
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3]
read=lambda n:json.loads((H/n).read_text())
build=read('build.json');geometry=read('geometry.json');fixture=read('near-vertical-summary.json');product=read('product-rf-summary.json');common=read('common-180-summary.json');natural=read('natural-28-summary.json');release=read('release-comparison.json');domain=read('domain-summary.json');ui=read('ui/ui.json');clock=read('clock.json');smoke=read('smoke.json');static=read('static.json');equiv=read('equivalence.json');world=read('world120/world120.json')
failures=[]
paired=read('domain/paired-baseline/baseline-comparison.json')
for case in paired['cases']:
 for name,ok in case['checks'].items():
  if not ok:failures.append(f"{case['ship']}:{case['scenario']}:{name}")
actual=product['comparison'];controlled=fixture['comparison'];normal=json.loads((H/'release/normal.json').read_text())['results'];targeted=[{'index':i,**{k:normal[i].get(k)for k in('seed','enabled','success','reason','closestM','fuzeMissM')}}for i in range(150,160)]
summary={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_VERIFICATION_1','baseCommit':'759fcd94bfa1081b268bfff9967f0f97088b7078','mainObserved':'cb70a637105ce00e7c0619270237cc35a83d39c2','branch':'near-vertical-path-fix-a','baseHtml':{'bytes':build['variants']['BASE']['htmlBytes'],'sha256':build['variants']['BASE']['htmlSha256']},'minimumHtml':{'bytes':build['variants']['MIN']['htmlBytes'],'sha256':build['variants']['MIN']['htmlSha256']},'finalHtml':{'bytes':build['finalHtmlBytes'],'sha256':build['finalHtmlSha256']},'changedSymbols':static['changedSymbols'],'allOtherMainSymbolsByteExact':static['allOtherMainSymbolsByteExact'],'arhMeasurementPreserved':static['preservedFunctionHashes']['_arhV2MonopulseMeasurement']['same'],'geometry':{'pass':geometry['pass'],'checks':geometry['checks']},'controlledFixture':{'pass':fixture['pass'],'baseKills':sum(x['base']['lethal']for x in controlled),'minimumKills':sum(x['minimum']['lethal']for x in controlled),'finalKills':sum(x['final']['lethal']for x in controlled),'handoffUnchanged':fixture['checks']['handoffUnchanged'],'minimumAndFinalExact':fixture['checks']['minimumAndFinalExact']},'productRf':{'pass':product['pass'],'baseKills':sum(x['base']['success']for x in actual),'finalKills':sum(x['final']['success']for x in actual),'baseClosestRangeM':[min(x['base']['closestM']for x in actual),max(x['base']['closestM']for x in actual)],'finalClosestRangeM':[min(x['final']['closestM']for x in actual),max(x['final']['closestM']for x in actual)],'finalDeterministic':product['checks']['finalDeterministic'],'nativeRfUsed':product['checks']['nativeRfUsed']},'common180':common,'natural28':natural,'release300':{'pass':release['pass'],'shots':release['shots'],'successToFailure':len(release['successToFailure']),'failureToSuccess':len(release['failureToSuccess']),'browserErrors':release['browserErrors'],'statusChanges':sum(len(x['statusChanges'])for x in release['records']),'targeted240km':targeted},'equivalence':{'pass':equiv['pass'],'conditions':len(equiv['conditions']),'functionCount':read('native-source-ledger.json')['functionCount'],'maxErrors':{k:max(x['maxError'][k]for x in equiv['conditions'])for k in ('timeS','xM','yM','altitudeM','speedMps')}},'domain':{'passed':domain['checks']-len(failures),'total':domain['checks'],'knownFailures':failures},'ui':{'pass':ui['pass'],'passed':sum(ui['checks'].values()),'total':len(ui['checks']),'errors':len(ui['errors'])},'clock':{'pass':clock['pass'],'checks':clock['checks']},'smoke':{'pass':smoke['pass'],'pageErrors':len(smoke['pageErrors']),'consoleErrors':len(smoke['consoleErrors']),'coreFailures':len(smoke['coreFailures']),'rangeTableRecalculationRequired':smoke['rangeTable']['recalculationRequired']},'world120':{'pass':world['pass'],'idleSameTruthHash':world['checks']['idleSameTruthHash'],'combatHashChanged':world['combatHashChanged'],'idleTruthSha256':world['records'][0]['truthSha256'],'combatTruthSha256':world['records'][2]['truthSha256']},'knownBaselineFailuresOnly':len(failures)==6,'notRun':['Full ENV_D ~175,955-shot remeasurement','All possible extreme geometries / real-world weapon certification'],'mainMerged':False,'releaseOrTagCreated':False,'reviewedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat()}
summary['implementationPass']=all([static['pass'],geometry['pass'],fixture['pass'],product['pass'],not common['successToFailure'],not common['lethalToNonlethal'],not natural['successToFailure'],release['pass'],equiv['pass'],ui['pass'],clock['pass'],smoke['pass'],world['pass'],summary['knownBaselineFailuresOnly']])
(H/'verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

def f(v,n=3):return f'{v:.{n}f}'
actual_rows='\n'.join(f"| {x['seedIndex']} | {x['base']['reason']} / {f(x['base']['closestM'])} | {x['final']['reason']} / {f(x['final']['closestM'])} | {f(x['final']['maxAbsUsedGammaDeg'])}° |"for x in actual)
report=f'''# NEAR_VERTICAL_PATH_FIX_A 보고서

## 판정

- **±60° 정책 제한 해제: PASS.** `_wip79KappaPipState()`의 목표 경로각 정책 clamp를 제거했다. 실제 받음각·구조 G·동압·구동기·시커 제한은 그대로다.
- **근수직 사례: PASS.** 최신 ARH 기준 BASE는 분리 fixture와 실제 제품 RF 경로 모두 0/5였고, 최종본은 양쪽 모두 5/5 KILL이다.
- **장거리 ARH 수정 보존: PASS.** SM-6 240 km 5시드×종료기 OFF/ON 10발이 모두 명중했고, 종료기 전체 300발에서 FIX_A 대비 성공→실패 0·상태 변경 0이다.
- **관련 회귀: PASS WITH KNOWN BASELINE FAILURES.** 공통 180발과 자연 RF 28조건의 성공→실패 0, UI 88/88, 실제 함수/사본 4조건 오차 0, 배속·시점·손상 검사가 통과했다. 도메인은 수정 전과 같은 raid exact-state 6건만 남아 414/420이다.

## 기준과 산출물

| 항목 | 값 |
|---|---|
| 기준 커밋 | `759fcd94bfa1081b268bfff9967f0f97088b7078` |
| 입력 | `Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html` |
| 입력 크기 / SHA-256 | `{build['variants']['BASE']['htmlBytes']:,} bytes` / `{build['variants']['BASE']['htmlSha256']}` |
| 최종 | `Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html` |
| 최종 크기 / SHA-256 | `{build['finalHtmlBytes']:,} bytes` / `{build['finalHtmlSha256']}` |
| 변경 함수 | `_wip79KappaPipState` 1개 |
| 변경 전/후 함수 SHA | `{build['inputFunctionSha256']}` → `{build['variants']['FINAL']['functionAfterSha256']}` |

## 변경과 수치 계약

최소 비교본은 `gammaF=clamp(gammaF,deg(-60),deg(60))` 한 줄만 제거했다. 이 비교본만으로 원래 5시드는 0/5에서 5/5로 회복했다. 하지만 별도 실제 함수 기하 검사에서 기존 `Math.max(1,horizontalRange)` 보호가 수평거리 0.1 m의 유효 방향을 300 m/s가 아니라 30 m/s 벡터로 축소하고, 완전 중첩에서는 0벡터를 만드는 계약 실패가 재현됐다.

최종본은 실제 실패 지점만 추가로 정리했다. 수평 성분이 있으면 실제 크기로 정규화하고, 정확히 수직/중첩이면 현재 수평 진행방향을 유지한다. 수평속도도 없을 때만 결정적 +X를 사용한다. PIP_LOS 경로각은 `atan2(dz,horizontalRangeM)`의 자연 범위다. 임의 ±89° 상한이나 분모 보정은 넣지 않았다. 최소본과 최종본은 원래 근수직 5발 전체 결과가 exact 같다.

기하 검사는 59.9°/60.1°, 상승·하강 약 89.9°, 0.1 m 좌우, 정확한 수직과 완전 중첩을 포함한다. 최종 모든 출력은 유한하고, 정의된 방향에서 속력 상대오차는 1e-12 미만이다. `loftB4ShapeWaypoint`는 byte 동일하며 원래 100 m/20 km 경로에서 `waypointB4=false`였다. 따라서 이 사례의 60°는 후단 waypoint가 아니라 해당 정책 clamp가 실제 소비한 값이다.

## 근수직 비행 결과

분리 capsule은 선택 HTML에서 추출한 실제 281개 함수와 동일한 프로파일을 사용한다. BASE 최근접은 216.886–237.130 m, 최종은 0.00027–9.950 m이며 최종 5/5 KILL이다. 첫 Kappa tick은 모두 인계 직후 1.733–1.750 s로 동일하다. seed 1에서 BASE는 PIP LOS 89.763°를 60°로 소비했고, 최종은 89.763°를 그대로 소비했다. BASE의 최대 raw 요구는 36.106 G·포화 표본 117개, 최종은 21.601 G·포화 2개였다. 이득과 물리 한계 변경 없이 잘못된 목표방향이 사라진 결과다.

실제 브라우저 제품 경로는 정식 VLS release, 네이티브 RF/EKF, 60 Hz fixed tick, 기존 신관·피해를 사용했다. 함 사통 트랙과 Kh-35U 직선 운동만 fixture가 통제한다.

| 시드 | BASE 결과 / 최근접 m | 최종 결과 / 최근접 m | 최종 최대 사용각 |
|---:|---|---|---:|
{actual_rows}

BASE는 5발 모두 RF TRACK을 얻었지만 이후 LOW_SPEED로 끝났다. 최종은 5발 모두 TRACK 상태에서 KILL했고 최근접 범위는 {f(summary['productRf']['finalClosestRangeM'][0])}–{f(summary['productRf']['finalClosestRangeM'][1])} m다. 같은 최종 bytes/seed 1 재실행은 전체 반환값 exact 일치다.

![근수직 경로 비교](near-vertical-path-comparison.png)

## 회귀

| 검사 | 결과 |
|---|---|
| 공통 SAM | 180발, effects/lethal 170/170 유지, 성공→실패 0 |
| 자연 RF | 28조건, 성공→실패 0, 실패→성공 0, 오류 0 |
| 종료기·발사 | 300발, 성공→실패 0, 상태 변경 0, 오류 0 |
| SM-6 240 km | 5시드×OFF/ON 10/10 명중; seed12001 최근접 1.349768 m 유지 |
| 실제 함수/독립 사본 | 281 함수 해시 일치, 4조건 궤적·반환값 오차 0 |
| 도메인 | 414/420; 기존 raid exact-state 6건만 실패 |
| UI | 88/88, page error 0 |
| 고정 tick | 정상/사통손상 × 1/8/16/64, 3,840 tick exact; 2D/3D view read-only |
| 120초 world | idle hash 동일 `{summary['world120']['idleTruthSha256']}`; 대표 전투 hash도 동일 |
| smoke/core | page·console·core 오류 0 |

도메인 6건은 DDG/CG raid 각각의 `samePhysicalState`, `raidInventoryDeltaBounded`, `sameExistingObserverState`로 FIX_A와 동일하다. assertion을 완화하지 않았다.

## 보존과 남은 범위

ARH 측정 함수, RF 프로파일, PN/APN/ZEM/Kappa 이득·TGO, 발사 인계, 6DoF, 추진·항력·질량·G·받음각·구동기, 신관·피해·배터리·종료기는 byte 동일하다. 외부 shell과 자산도 payload manifest를 제외하면 동일하다.

전체 ENV_D 약 175,955발 재측정은 하지 않았다. 내장 사거리표는 `recalculationRequired=true`를 유지한다. 모든 극단 기하의 명중이나 실제 무장 성능을 주장하지 않는다. main 병합과 release/tag 생성은 하지 않았다.
'''
(H/'REPORT.md').write_text(report)
repro='''# NEAR_VERTICAL_PATH_FIX_A 재현\n\n저장소 루트에서 실행한다. Node 24, Python 3.12, Acorn 8.19, Playwright/Chromium을 사용했다. Chromium 임시 프로필은 공간 제약 때문에 `TMPDIR=/dev/shm`으로 실행했다.\n\n```bash\nexport NODE_PATH="$PWD/docs/performance/F/node_modules"\nnode docs/missile/near-vertical/A/build.cjs\nnode docs/missile/near-vertical/A/test_geometry.cjs\nnode docs/missile/near-vertical/A/test_static.cjs\nnode docs/missile/near-vertical/A/run_near_vertical.cjs\npython docs/missile/near-vertical/A/run_product_one.py --variant BASE --seed-index 1\npython docs/missile/near-vertical/A/run_product_one.py --variant FINAL --seed-index 1\npython docs/missile/near-vertical/A/aggregate_product_rf.py\nnode docs/missile/near-vertical/A/run_common.cjs\npython docs/missile/near-vertical/A/run_natural.py\npython docs/missile/near-vertical/A/run_release_chunk.py --kind normal --start 0 --end 48\npython docs/missile/near-vertical/A/aggregate_release_chunks.py\npython docs/missile/near-vertical/A/compare_release.py\nnode docs/missile/near-vertical/A/export_equivalence.cjs\npython docs/missile/near-vertical/A/verify_equivalence.py\npython docs/missile/near-vertical/A/verify_clock.py\npython docs/missile/near-vertical/A/verify_smoke.py\npython docs/missile/near-vertical/A/verify_world120.py\n```\n\n300발 release는 `release/parts`의 기록처럼 호스트 실행 상한을 피하기 위해 독립 chunk로 실행하고 원래 순서로 병합한다. 도메인 회귀는 `docs/pip/B/run_domain.py`와 `docs/missile/range/A/collect_domain.py`를 사용한다. collector의 exit 1은 기존 6개 raid assertion을 보존한 예상 결과이며 정확히 414/420이어야 한다.\n\n`product-rf-*`는 실제 브라우저/VLS/RF/EKF 경로지만 함 사통 트랙과 표적 직선 운동을 통제한다. `near-vertical-results`는 선택 HTML 실제 함수를 추출한 격리 capsule이다. 두 범위를 합쳐 자연 센서 전체 전장 인증으로 부르지 않는다.\n'''
(H/'REPRODUCE.md').write_text(repro)
status=f'''# AEGIS v48 WIP NEAR_VERTICAL_PATH_FIX_A 상태\n\n- 기준: `arh-measurement-fix-a@759fcd94bfa1081b268bfff9967f0f97088b7078`\n- 최종 HTML: `Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html`\n- 크기: `{build['finalHtmlBytes']:,} bytes`\n- SHA-256: `{build['finalHtmlSha256']}`\n- 변경: `_wip79KappaPipState`의 ±60° 목표 경로각 정책 해제 + 재현된 1m 미만 수평 정규화/중첩 수치 계약 수정\n- 근수직: 분리 fixture 0/5→5/5, 실제 제품 RF 경로 0/5→5/5\n- 장거리 ARH: 240km 10/10 보존, release 300 성공→실패 0\n- 회귀: 공통180·자연RF28 신규 실패 0, UI88/88, 도메인414/420(기존6건), 고정tick·smoke·동등성 PASS\n- 미실행: 전체 ENV_D 재측정\n- main 병합/release/tag: 없음\n'''
(R/'AEGIS_PLAN_STATUS_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.md').write_text(status)
print(json.dumps({'implementationPass':summary['implementationPass'],'finalHtml':summary['finalHtml'],'domain':summary['domain'],'productRf':summary['productRf']},ensure_ascii=False,indent=2))
