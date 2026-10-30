"""CLEAN_B report: outcome approval and farthest-ending measured run."""
from pathlib import Path
import csv,json
H=Path(__file__).resolve().parent;R=H.parents[2];A=R/'docs/cleanup/A'
read=lambda p:json.loads(p.read_text())
def save(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvout(n,rows):
 with(H/n).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def table(headers,rows):return'\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |'for r in rows])
build=read(H/'build.json');plan=read(H/'PLAN.json');m=read(H/'results/measurement.json');env=read(H/'ENVELOPE_TABLE_D.json');audit=read(H/'evidence/shot-audit.json');iv=read(H/'evidence/interval-verification.json');cg=read(H/'evidence/cg-approval.json');manifest=read(H/'approved-raid-baselines.json');delivery=read(H/'evidence/delivery.json');native=read(H/'evidence/native-equivalence.json');world=read(H/'evidence/world120/world120.json');ui=read(H/'evidence/ui/ui.json');execution=read(H/'evidence/domain/execution.json')
domain=[]
for d in sorted((H/'evidence/domain').iterdir()):
 if not d.is_dir():continue
 if d.name=='paired-baseline':
  j=read(d/'baseline-comparison.json');checks={r['ship']+'.'+r['scenario']+'.'+k:v for r in j['cases']for k,v in r['checks'].items()};domain.append({'suite':d.name,'total':len(checks),'passed':sum(v is True for v in checks.values()),'failed':[k for k,v in checks.items()if v is not True]});continue
 for f in d.glob('*.json'):
  j=read(f);checks=j.get('checks',{})if isinstance(j,dict)else{}
  if checks:domain.append({'suite':d.name,'total':len(checks),'passed':sum(v is True for v in checks.values()),'failed':[k for k,v in checks.items()if v is not True]})
total=sum(x['total']for x in domain);passed=sum(x['passed']for x in domain);assert total==420
assert execution['htmlSha256']==build['sha256']==delivery['htmlSha256'];assert len(ui['checks'])==88
save('evidence/domain-summary.json',{'total':total,'passed':passed,'suites':domain,'htmlSha256':build['sha256'],'elapsedS':execution['elapsedS'],'approvedAssertions':{k:v['assertions']for k,v in manifest['entries'].items()}})
checks={'B1':passed==420 and cg['pass']and execution['pass'],'B2':delivery['pass']and native['pass'],'B3':all(ui['checks'].values()),'B4':iv['pass']and audit['pass']and iv['unmeasured']==0}
save('ACCEPTANCE.json',{'checks':checks,'pass':all(checks.values()),'domain':{'passed':passed,'total':total,'baselineUpdates':6},'UI':{'passed':sum(bool(x)for x in ui['checks'].values()),'total':88},'rows':120,'unmeasured':iv['unmeasured'],'newShots':m['newShotsTotal'],'gameCodeChanged':False,'htmlSha256':build['sha256']})
compact=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
csvout('FINAL_TABLE.csv',[{'cellId':r['cellId'],'weapon':r['weapon'],'altM':r['altM'],'motion':r['motion'],'maxRangeKm':r['maxRangeKm'],'effectiveMinKm':r['effectiveMinKm'],'effectiveMaxKm':r['effectiveMaxKm'],'maxInterceptPoint':compact(r['maxInterceptPoint']),'effectiveMinInterceptPoint':compact(r['effectiveMinInterceptPoint']),'effectiveMaxInterceptPoint':compact(r['effectiveMaxInterceptPoint']),'otherRuns':compact(r['otherRuns']),'deadZones':compact(r['deadZones']),'boundaryFailures':compact(r['boundaryFailures'])}for r in env['rows']])
changed=iv['changed'];csvout('CHANGED_INTERVALS.csv',[{'cellId':r['cellId'],'weapon':r['weapon'],'altM':r['altM'],'motion':r['motion'],'before':compact(r['before']),'after':compact(r['after']),'otherRuns':compact(r['otherRuns']),'deadZones':compact(r['deadZones'])}for r in changed])
import gzip
newRows=[]
for row in m['rows']:
 data=json.loads(gzip.decompress((H/'results/cells'/(row['cellId']+'.json.gz')).read_bytes()))
 for q in data['newDistances']:
  for s in q['shots']:newRows.append({'cellId':row['cellId'],'weapon':row['weapon'],'altM':row['altM'],'motion':row['motion'],'rangeKm':q['rangeKm'],'purpose':q['purpose'],**{k:s.get(k)for k in ['rngSeed','navigationSeed','outcome','reason','lethal','closestM','fuzeMissM','interceptPointKm','flightTimeS']}})
csvout('ADDITIONAL_SHOTS.csv',newRows);refinedShots=sum(r['purpose']=='REFINE_MIN'for r in newRows);gridShots=len(newRows)-refinedShots
assert gridShots==plan['baseGridShots'];assert refinedShots<=plan['refinementMaximumShots']
save('ACTUAL_COST.json',{'plannedGridShots':plan['baseGridShots'],'plannedRefinementMaximumShots':plan['refinementMaximumShots'],'plannedMaximumShots':plan['maximumExpectedShots'],'plannedMinutes':plan['expectedSeconds']/60,'actualGridShots':gridShots,'actualRefinementShots':refinedShots,'actualShots':m['newShotsTotal'],'actualMinutes':m['elapsedS']/60,'reusedGridShots':audit['reusedGridShots'],'workers':m['workers'],'threeHourLimitRespected':m['elapsedS']<10800})
interval=lambda r:f"{r['startKm']}~{r['endKm']}"
dead=lambda r:interval(r)+'('+r['representativeFailureReason']+')'
out=['# CLEAN_B — CG 기준 승인 및 유효 요격 구간 재정의','',f'**도메인 {passed}/420, UI88 및 검수 B1–B4 '+('전체 PASS.'if all(checks.values())else'미통과 항목 있음.')+f' 유효구간 120/120 확정, 값 변경 {len(changed)}칸.**','',
 f'기준 `clean-a@{build["baseCommit"]}`, 입력 SHA `{build["baseHtmlSha256"]}`. 산출물 `{build["output"]}` ({build["bytes"]:,} bytes), SHA-256 `{build["sha256"]}`. 별도 `clean-b` 브랜치. main/기준 브랜치 병합 및 release/tag 생성 없음. 게임용 SIM_TUNED 모델 산출값이며 실물 성능과 비교하지 않는다.','',
 '## 1. CG 회귀 3건 기준값 승인','',
 '사용자의 새 기준을 적용했다. 격추 수·표적별 최종 결과·자함 HP·침수·모듈 손상·생존이 같거나 좋으면 (a)이며, 자원 소모 차이는 수치만 보존한다. CG 3건을 (a)로 승인하고 DDG와 동일한 exact-state 기준 적용 경로에 추가했다.','',
 table(['180초 비교 항목','KAPPA 기준','현재','판정'],[['SAM 발사',21,22,'자원 차이 기록'],['native SAM 격추',2,2,'동일'],['자함 HP',100,100,'동일'],['침수 m³',0,0,'동일'],['모듈 손상','0','0','동일'],['생존','생존','생존','동일'],['VLS 잔여 셀',104,103,'자원 차이 기록'],['20mm 잔탄 합계',3100,3039,'61발 추가 소모 기록']]),'',
 '원래 8발과 native 추가 스폰 47발의 개별 최종 상태도 동일하다. 비교는 앞선 CLEAN_A의 동일한 180초 고정 진단 지평이며, 추가 스폰 전부의 전투 종료를 의미하지 않는다. 이번에 180초 raid를 다시 쏘았다고 세지 않았다. 이 근거는 `evidence/cg-approval.json`, 원래 개별 결과는 CLEAN_A `RAID_OUTCOMES.csv`에 있다.','',
 '`approved-raid-baselines.json`에 CG의 이전/새 물리·관측·재고 전체 값, 각각 SHA-256 및 사유 **"사용자 승인: 결과 동일, 자원 소모 차이만 존재"**를 기록했다. DDG의 승인 항목3개는 그대로 보존했다. 승인된 게임 코어 해시에서만 적용하며 허용 오차를 늘리거나 비교 필드를 제외하지 않았다. 원래 판정값은 검수 로그 `originalChecks`에 유지한다.','',
 table(['함정','대상 검사','이전 상태 해시','새 상태 해시','사유'],[[k,', '.join(v['assertions']),v['oldHash'],v['newHash'],v['reason']]for k,v in manifest['entries'].items()]),'',
 f'최종 CLEAN_B HTML을 대상으로 전체 15 suites **{passed}/420**을 다시 실행했다. 미통과 검사: '+(', '.join(k for s in domain for k in s['failed'])or'없음')+f'. 소요 {execution["elapsedS"]:.2f}초. `python docs/cleanup/B/run_domain.py`는 승인 manifest를 명시적으로 사용한다. 승인 옵션 없는 과거 비교기의 결과를 소급 변경하지 않는다.','',
 '## 2. 추가 사격 대상과 비용','',
 f'실행 전에 `PLAN.md`/`PLAN.json`과 채팅에 대상/비용을 보고했다. 기본 격자 부족 **{plan["baseGridShots"]:,}발**, 경계 세분화 최대 **{plan["refinementMaximumShots"]}발**, 합계 최대 **{plan["maximumExpectedShots"]:,}발**, 예상 **{plan["expectedSeconds"]/60:.2f}분**이었다. 3시간 제한 이내이므로 실행했다.','',
 f'실제 기본 격자 {gridShots:,}발 + 경계 세분화 {refinedShots}발 = **{m["newShotsTotal"]:,}발**, **{m["elapsedS"]/60:.2f}분**, {m["workers"]} workers. 기존 격자 **{audit["reusedGridShots"]:,}발**을 재사용했다. 서로 다른 시드의 비행을 하나로 재사용하지 않았다. 사전 추정은 같은 칸의 인접 기존 비행 tick 수×과거 비용,1.5 여유와 준비60초를 사용했다.','',
 '새 1km 격자 보강은120칸 모두 필요했다. 그중 CLEAN_A의 끊김 뒤 미측정이 남은 칸은21개다. 전체 부족 거리 목록은 PLAN.json에 있으며, 그21개는 아래와 같다.','',
 table(['기종','고도 m','운동','이전 구간 km','끊김 뒤 미측정 점 수'],[[r['weapon'],r['altM'],r['motion'],f"{r['previousEffectiveMinKm']}~{r['previousEffectiveMaxKm']}",len(r['missingAfterPriorBreakKm'])]for r in plan['rows']if r['missingAfterPriorBreakKm']]),'',
 '5개 고정 시드 세트(game RNG / navigation): '+', '.join(f"({s['rngSeed']}, {s['navigationSeed']})"for s in m['seeds'])+'. 같은 빌드·기종·고도·표적 운동·거리·시드의 기록만 재사용했다. D2 원시 데이터 logical SHA-256, CLEAN_A의 Git blob, 각5발 결과 SHA-256을 검증했다. 승인 전/다른 유도 버전의 기록은 섞지 않았다.','',
 '## 3. 바뀐 유효구간과 나머지 구간','',
 '격자는1~min(30, 바깥 최대거리)km의1km 간격, 이후35km부터 바깥 최대거리 이하5km 간격이다. 통과는5발 중3발 이상 native KILL/STRUCT_FAIL다. 격자의 연속 통과 묶음 중 **끝 거리가 가장 먼 묶음**을 선택했다. 폭이 가장 넓은 묶음 선택과 다르다. 그 시작이30km를 넘으면 앞 실패점과의 사이를1km 간격으로 모두 보강하고 연결성을 다시 계산했다. 숨은 중간 실패를 건너뛰어 첫 성공과 이어 붙이지 않는다.','',
 '다른 통과 묶음은 `otherRuns`, 묶음 사이 실패 지점들은 `deadZones`에 시작·끝과 대표 native 실패 사유를 남겼다. 첫 묶음 전/마지막 묶음 뒤 실패는 `boundaryFailures`로 별도 기록했다. 이 범위는 측정 격자의 결과이며, 사이의 모든 연속 실수 거리를 시험했다는 뜻이 아니다. 바깥 최대거리가5의 배수가 아니면 해당 끝값을 별도 격자점으로 추가하지 않았다. 바깥 링 값 자체는 변경하지 않았다.','',
 table(['기종','고도 m','운동','이전→새 km','otherRuns','deadZones'],[[r['weapon'],r['altM'],r['motion'],f"{r['before'][0]}~{r['before'][1]} → {r['after'][0]}~{r['after'][1]}",'; '.join(interval(x)for x in r['otherRuns'])or'없음','; '.join(dead(x)for x in r['deadZones'])or'없음']for r in changed]),'',
 f'값 변경 {len(changed)}칸, 동일 {120-len(changed)}칸. 범위가 같은 칸의 otherRuns/deadZones도 전체 JSON 및 FINAL_TABLE.csv에 보존했다. 근거리의 짧은 성공 구간을 삭제하거나 통과 기준을 완화하지 않았다.','',
 '## 4. 기종별 최종 표','',
 '각 칸은 **바깥 / 최소~최대 유효 km**. SM2=SM-2MR, SM2ER=SM-2ER, SM6=SM-6, ESSM=ESSM Block 2. 운동 속도 단위m/s. 500km는 측정 상한이며 상한 바깥 최대치를 추정하지 않았다.','']
motions=list(dict.fromkeys(r['motion']for r in env['rows']))
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 out+=['### '+weapon,'',table(['고도 m',*motions],[[alt,*[(lambda r:f"{r['maxRangeKm']} / {r['effectiveMinKm']}~{r['effectiveMaxKm']}")(next(r for r in env['rows']if r['weapon']==weapon and r['altM']==alt and r['motion']==motion))for motion in motions]]for alt in [30,1000,5000,10000,15000,20000]]),'']
out+=['## 5. 검수 B1–B4','',table(['검수','결과','증거'],[['B1','PASS'if checks['B1']else'FAIL',f'{passed}/420; DDG3+CG3 승인 exact 기준, 사유/해시 기록'],['B2','PASS'if checks['B2']else'FAIL','ENV_D 블록 외 게임 코드·UI·자산 byte 동일, 실제 함수283개 일치,120초 무표적/전투 truth 동일'],['B3','PASS'if checks['B3']else'FAIL','최종 HTML에서 UI88/88 새 실행'],['B4','PASS'if checks['B4']else'FAIL','120칸 최소/최대 확정, 미측정0, otherRuns/deadZones 기록 및 독립 Python 재구성']]),'',
 table(['120초 상태','양쪽 동일 SHA-256'],[['무표적',world['records'][0]['truthSha256']],['전투',world['records'][2]['truthSha256']]]),'',
 f'내장 표 `{env["schema"]}`, profileHash `{env["profileHash"]}`. DDG/CG status().match=true와complete=true를 확인했다. 각 행 previous는 CLEAN_A 원문 값이며 그 안의 이전 D2 기록도 보존했다. 지도·발사 판정에 연결하지 않았다. 게임 코드·PN/Kappa·추진·항력·질량·G·배터리·시커·신관·Pk 계수 변경0.','',
 'byte 동일 검사는 압축 실행 main을 해제한 뒤 ENV_D 블록을 제외해 비교했다. 재포장에 필요한 C55 asset13의 gzip payload와 rawBytes/gzipBytes/SHA-256 메타데이터만 갱신했다. 나머지 HTML shell·UI 및 자산0–12는 동일하다.','',
 '감사 도구의 초기 오류1건도 보존했다. 즉시 기폭 결과 samResult=MISS라도 이미 표적 탄두 유폭으로 native 최종 outcome=KILL인6발이 있었다. 초기 감사는 samResult만 검사해 이를 불일치로 표시했다. 기존 D2의 최종 outcome 및 lethal 정의를 확인해 감사 도구의 참조 필드를 바로잡았다. 게임·사격 결과·lethal 값·구간·통과 기준은 바꾸지 않았다. 원본 오류 로그와6발 내역은 evidence/audit-diagnostic-correction.json 및 shot-audit-initial-samresult-error.log에 있다.','',
 '재현 도구: plan.cjs → measure.cjs → build.py → audit.cjs → verify_intervals.py → verify_native.cjs → run_domain.py / run_ui.py / verify_delivery.py → report.py. 브라우저는 기존 Playwright/Chromium, Node AST 도구는 기존 acorn 의존성을 쓴다. 원시 새 사격은 results/cells, 소스/재사용 해시는 evidence, 별도 CSV는 ADDITIONAL_SHOTS.csv 및 CHANGED_INTERVALS.csv에 있다.','']
(H/'REPORT.md').write_text('\n'.join(out));save('STATUS.json',{'state':'COMPLETE'if all(checks.values())else'CHECK_FAILED','branch':'clean-b','gameCodeChanged':False,'domainPass':passed,'domainTotal':420,'approvedAssertions':6,'newShots':m['newShotsTotal'],'effectiveRows':120,'unmeasured':iv['unmeasured'],'changedCells':len(changed),'checks':checks,'build':build})
(H/'STATUS.md').write_text(f'# CLEAN_B 인계 상태\n\n- 도메인 {passed}/420, UI88, B1–B4 '+('PASS'if all(checks.values())else'미통과 항목 있음')+f'.\n- DDG3+CG3 승인 exact 기준 및 게임 코어 해시 보호. 결과 중심 분류, 자원 차이 기록.\n- 게임 비행·센서·교전 코드와 계수 변경0.\n- 유효구간120/120 확정, 변경{len(changed)}칸/동일{120-len(changed)}칸, 미측정0.\n- 가장 먼 끝값의 연속 통과 구간 선택. otherRuns/deadZones/previous 보존.\n- 새 사격{m["newShotsTotal"]:,}발, {m["elapsedS"]/60:.2f}분.\n- schema3 및 DDG/CG status match,120초 무표적·전투 truth hash 동일.\n- 지도·발사 판정 연결 없음. main 병합 및 release/tag 생성 없음.\n')
print(json.dumps({'checks':checks,'newShots':m['newShotsTotal'],'changedCells':len(changed)}));assert all(checks.values())
