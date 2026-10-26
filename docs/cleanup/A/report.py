"""Produce the requested CLEAN_A evidence tables without promoting failed checks."""
from pathlib import Path
import collections,csv,gzip,hashlib,json,time
H=Path(__file__).resolve().parent;R=H.parents[2]
def read(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvout(n,rows):
 with (H/n).open('w',newline='')as f:
  fields=list(dict.fromkeys(k for row in rows for k in row))
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |'for r in rows])
p1=read(H/'evidence/part1.json');build=read(H/'build.json');m=read(H/'results/intervals.json');env=read(H/'ENVELOPE_TABLE_D.json');old=read(R/'docs/envelope/D2/ENVELOPE_TABLE_D.json');oldby={r['cellId']:r for r in old['rows']}
pair=read(H/'evidence/paired-clean/baseline-comparison.json');domain=[]
for d in sorted((H/'evidence/domain-original').iterdir()):
 if not d.is_dir()or d.name=='paired-baseline':continue
 for f in d.glob('*.json'):
  j=read(f);checks=j.get('checks',{})if isinstance(j,dict)else{}
  if checks:domain.append({'suite':d.name,'total':len(checks),'pass':sum(v is True for v in checks.values()),'fail':[k for k,v in checks.items()if v is not True]})
checks={c['ship']+'.'+c['scenario']+'.'+k:v for c in pair['cases']for k,v in c['checks'].items()}
domain.append({'suite':'paired-baseline (DDG a approved)','total':len(checks),'pass':sum(v is True for v in checks.values()),'fail':[k for k,v in checks.items()if v is not True]})
assert sum(x['total']for x in domain)==420
domain_pass=sum(x['pass']for x in domain);assert domain_pass==417
save('evidence/domain-summary.json',{'total':420,'pass':domain_pass,'unapprovedOriginalPass':414,'approvedReferenceUpdates':3,'failed':3,'suites':domain,'scope':'14 original native suites on byte-identical latest game core; exact paired comparison freshly run on delivered CLEAN_A HTML'})
air=read(H/'results/part2-air.json.gz');near=read(H/'results/part2-near.json.gz');p2=[]
for i,name in [(0,'SM6_240KM_AIR_TERMINATION_OFF'),(1,'SM6_240KM_AIR_TERMINATION_ON')]:
 rows=[r for r in air['rows']if r['condition']['enabled']==bool(i)]
 p2.append({'caseId':name,'condition':rows[0]['condition'],'stages':{r['variant']:{k:r['result'].get(k)for k in ['success','reason','closestM','fuzeMissM','flightTimeS']}for r in rows}})
p2.append({'caseId':'SM6_0P1KM_20KM_STATIONARY_ASM_SEED1','condition':near['rows'][0]['condition'],'stages':{r['variant']:{k:r['result'].get(k)for k in ['success','lethal','outcome','reason','closestM','fuzeMissM','flightTimeS']}for r in near['rows']}})
assert all(x['stages']['LATEST']['success']for x in p2)
save('evidence/part2.json',{'cases':p2,'recovered':3,'newGameFixes':0,'errors':air['errors']})
csvout('PART2_SHOTS.csv',[{'caseId':c['caseId'],'stage':v,**s}for c in p2 for v,s in c['stages'].items()])
prior_zero=[r for r in m['rows']if r['previousEffectiveRangeKm']==0];assert len(prior_zero)==13
intervalChecks={'rows120':len(m['rows'])==120,'schema2':env['schema']=='AEGIS_ENVELOPE_TABLE_D_2','oldRowsPreserved':all(r['previous']==oldby[r['cellId']]for r in env['rows']),'outerRangesPreserved':all(r['maxRangeKm']==oldby[r['cellId']]['maxRangeKm']for r in env['rows']),'all120MinimaMeasured':all(r['effectiveMinKm']is not None for r in m['rows']),'all13FormerZerosHaveMinima':all(r['effectiveMinKm']is not None for r in prior_zero),'noExtraGridWithoutApproval':m['additionalGridAuthorized']or all(q['purpose']=='MINIMUM'for r in m['rows']for q in r['newDistances'])}
for r in m['rows']:
 original=read(R/'docs/envelope/D2/results/cells'/(r['cellId']+'.json.gz'));cache={q['rangeKm']:q for q in original['distances']};cache.update({q['rangeKm']:q for q in r['newDistances']})
 lethal=lambda k:sum(bool(x['lethal'])for x in cache[k]['shots'])
 minimum=r['effectiveMinKm'];assert all(lethal(k)<3 for k in range(1,minimum));assert lethal(minimum)>=3
 assert all(q['lethalCount']>=3 for q in r['gridChecks']if r['breakPoint']is None or q['rangeKm']!=r['breakPoint']['rangeKm'])
 if r['breakPoint']:assert r['breakPoint']['lethalCount']<3
 if r['status']=='MEASURED':assert r['effectiveMaxKm']>=minimum
intervalChecks['minimumEarliestPassAll120']=True;intervalChecks['knownGridContinuity']=True
save('evidence/interval-verification.json',{'checks':intervalChecks,'integrityPass':all(intervalChecks.values()),'complete':m['complete'],'pendingCells':[r['cellId']for r in m['rows']if r['status']=='PENDING_REQUIRED_GRID'],'freshShots':m['newShotsTotal'],'formerZeroCount':len(prior_zero)})
def stats(s):return json.dumps(s,ensure_ascii=False,separators=(',',':'))if s is not None else'NOT_MEASURED'
csvout('EFFECTIVE_INTERVALS.csv',[{'cellId':r['cellId'],'weapon':r['weapon'],'altM':r['altM'],'motion':r['motion'],'maxRangeKm':r['maxRangeKm'],'effectiveMinKm':r['effectiveMinKm'],'effectiveMaxKm':r['effectiveMaxKm']if r['effectiveMaxKm']is not None else'NOT_MEASURED','status':r['intervalStatus'],'previousEffectiveRangeKm':r['previous']['effectiveRangeKm'],'maxInterceptPoint':stats(r['maxInterceptPoint']),'effectiveMinInterceptPoint':stats(r['effectiveMinInterceptPoint']),'effectiveMaxInterceptPoint':stats(r['effectiveMaxInterceptPoint']),'breakPointFiveShots':stats(r['intervalBreakBoundary'])}for r in env['rows']])
csvout('RAID_OUTCOMES.csv',[{'ship':c['ship'],'version':v,'targetId':k,'outcome':o}for c in p1['comparisons']for v,s in [*c['before'].items(),('LATEST',c['current'])]for k,o in s['allNativeTargetOutcomes'].items()])
c2=read(H/'evidence/c2-comparison.json');delivery=read(H/'evidence/delivery.json');world=read(H/'evidence/world120/world120.json');native=read(H/'evidence/native-equivalence.json')
ui=read(H/'evidence/c2/CLEAN/ui/ui.json');uiChecks=ui['checks'];assert len(uiChecks)==88 and all(uiChecks.values())
web=[read(H/'evidence/c2'/t/'webgl/observed-world.json')for t in ['LATEST','CLEAN']]
webrows=[]
for a,b in zip(web[0]['records'],web[1]['records']):
 assert a['weapon']==b['weapon']and a['enabled']==b['enabled']
 assert a['launch']==b['launch']and a['final']==b['final']and a['samples']==b['samples']
 webrows.append({'weapon':a['weapon'],'terminationEnabled':a['enabled'],'oldTargetAlive':a['final']['targetAlive'],'newTargetAlive':b['final']['targetAlive'],'reason':b['final']['missile']['reason'],'physicalReturnsExact':True,'actualWebglFramesIncreased':b['framesAfterFlight'][1]>b['framesAfterFlight'][0]})
assert len(webrows)==8 and all(x['actualWebglFramesIncreased']for x in webrows)
save('evidence/webgl-comparison.json',{'shots':8,'successToFailure':0,'rows':webrows,'both29AssertionsPass':all(x['pass']for x in web)})
acceptance={'C1':{'pass':domain_pass==420,'passed':domain_pass,'total':420,'approvedUpdates':3,'unresolvedCG':3},'C2':{'pass':all(not x['successToFailure']and not x['exactResultChanges']for x in c2.values())and all(uiChecks.values())and all(x['pass']for x in web),'ui':88,'release':300,'common':180,'naturalRF':28,'webgl':8,'successToFailure':0},'C3':{'pass':delivery['pass'],'idle':world['records'][0]['truthSha256'],'combat':world['records'][2]['truthSha256']},'C4':{'pass':m['complete']and all(intervalChecks.values()),'rows':120,'minimumKnown':120,'completeIntervals':sum(r['status']!='PENDING_REQUIRED_GRID'for r in m['rows']),'pending':build['pendingCells'],'formerZeroMinima':13}}
save('ACCEPTANCE.json',acceptance)
stageNames={'KAPPA':'KAPPA','DZT':'DZT','HANDOFF':'HANDOFF','ARH':'ARH','VERTICAL':'NEAR_VERTICAL','LATEST':'최신'}
out=['# CLEAN_A 검증 보고서','',f'**전체 합격 보류: 도메인 회귀 {domain_pass}/420, CG 실제 자원 퇴행 3건 유지. 유효구간 최대값 {build["pendingCells"]}칸은 추가 시험 범위 확인 대기.**','',
 '게임 비행·센서·교전 코드는 변경하지 않았다. DDG의 검증된 (a) 기준값 3건만 선택적으로 갱신했다. 결과를 맞추는 계수 조정·검사 완화·실패 제외는 없다. 원본 브랜치/main 병합 및 tag/release 생성 없음.','',
 f'기준 `env-d-remeasure-a@{build["baseCommit"]}`. 입력 SHA-256 `b846bd92a01f405fda82bafa08a5758925106d9827615d9dd06553134648c8db`. 출력 `{build["output"]}`, {build["bytes"]:,} bytes, SHA-256 `{build["sha256"]}`. 모든 값은 게임 SIM_TUNED 모델 산출값이며 실물과 비교하지 않는다.','',
 '## 1. 도메인 회귀 6건','',
 table(['함정 / 검사','KAPPA','DZT','HANDOFF','ARH','NEAR_VERTICAL','최신','분류 / 조치'],[[('DDG'if r['ship'].startswith('DDG')else'CG')+' / '+r['assertion'],*['PASS'if r['buildStatus'][v]else'FAIL'for v in ['KAPPA','DZT','HANDOFF','ARH','VERTICAL','LATEST']],r['classification']+' / '+r['action']]for r in p1['six']]),'',
 '6건 모두 처음 실패한 빌드는 LAUNCH_HANDOFF_A다. DZT→HANDOFF에서 변경된 기존 함수는 `updateMissileBodyB3` 하나이고, 새 보조 함수는 `samLaunchHandoffGateA`다. HANDOFF의 해당 함수만 DZT로 되돌린 **진단 전용 대조군**은 6건 모두 통과했다. 대조군의 복원은 제품에 적용하지 않았다. 자세·속도·3D 경로 정렬 기반 발사 제어권 인계 시점이 바뀌어 궤적, 추적기 관측, 재교전 스케줄과 재고가 달라진 인과관계를 확인했다.','',
 '32초 원래 fixture 비교를 보존하고 같은 원래 8발 Kh-32/AUTO 조건을 180초까지 연장했다. 팀·기동 유틸리티는 원래대로 OFF, 아군함은 없다. 고유 native 추가 스폰을 끄지 않았다. 총 55개 ASM 중 원래 8발만 모두 종료됐고 추가 47발은 아직 비행 중이다. 따라서 종료 시각/사유는 **32초 원래 검수 종료 및 180초 고정 진단 지평**이며, 전 세계 적 미사일 전멸·전투 종료를 의미하지 않는다. 원래 8발과 추가 47발의 개별 결과는 `RAID_OUTCOMES.csv`에 전부 수록했다.','']
metrics=[]
for c in p1['comparisons']:
 for v,s in [*c['before'].items(),('LATEST',c['current'])]:metrics.append(['DDG'if c['ship'].startswith('DDG')else'CG',v,s['samLaunches'],s['samNativeKills'],f"{s['shipHP']:.6f}",s['loadedVlsCells'],' / '.join(str(x)for x in s['closeInAmmo'].values()),f"{s['waterM3']:.6f}",'생존'if s['shipAlive']else'상실'])
out += [table(['함정','빌드','SAM 발사','native SAM KILL','자함 HP','VLS 잔여 셀','CIWS 잔탄','침수 m³','생존'],metrics),'',
 'DDG는 KAPPA와 DZT 모두 대비 SAM 발사 23→21, SAM KILL 0→3, HP/침수/모듈 손상/생존/탄약이 나빠지지 않았다. 원래 8발 결과도 사후 관측에서 개선됐다. (a)로 분류한 3건만 exact-state 새 값으로 갱신했다. `approved-raid-baselines.json`에 예전/새 물리·관측 상태와 재고, 양쪽 해시 및 갱신 사유를 보존하고, 검증된 게임 코어 해시에서만 사용할 수 있게 했다. 일반 회귀 실행의 기본 동작은 그대로다. 32초 VLS 비교는 DDG 91→90이며, 이 조기 한 시점의 소모 차이를 180초 결과로 검토한 것이다.','',
 'CG는 SAM 발사 21→22, VLS 잔여 104→103, 20mm 탄약 최신 61발 추가 소모, SAM KILL 2→2, HP100/침수0/생존 유지다. 이 경우 (a)로 처리하지 않았다. 같은 비행 함수 복원 대조군이 원래 상태로 돌아오므로 최초 원인은 인계 수정으로 특정되지만, 검증된 인계를 되돌리거나 발사 정책을 바꾸지 않고 고칠 수 있는 단일 최소 결함은 확정하지 못했다. CG 3건은 실제 자원 퇴행 (b)으로 남기며 기준값을 갱신하지 않는다. 이전 보고서의 “기존 실패” 표기를 바로잡는다. HANDOFF 시점에는 CIWS 추가 76발, 최신은 추가 61발이다.','',
 '대조 계측은 고유 fixed tick 뒤 읽기만 수행했다. 독립 비계측 원래 fixture 대비 32초의 state/dynamics/RNG/observer/offboard 40개 일치 검사를 통과했다. 모듈 손상은 모든 키 합집합으로 비교했다. native `NORMAL_HIT`은 대상 자체의 종료 원인 라벨이며 자함 명중 수와 동의어로 해석하지 않는다. 원래 표적별 내역은 다음과 같다.','',
 table(['함정','원래 표적','KAPPA','DZT','HANDOFF','최신'],[[('DDG'if c['ship'].startswith('DDG')else'CG'),k,*[c['before'][v]['initialTargets'][k]for v in ['KAPPA','DZT','HANDOFF']],c['current']['initialTargets'][k]]for c in p1['comparisons']for k in c['current']['initialTargets']]),'',
 '## 2. HANDOFF 신규 실패 3발 재확인','',
 table(['원래 조건','KAPPA','HANDOFF','최신','회복 단계'],[[c['caseId'],*[(('성공'if c['stages'][v]['success']else'실패')+f" / CPA {c['stages'][v]['closestM']:.6f}m")for v in ['KAPPA','HANDOFF','LATEST']],'ARH'if i<2 else'NEAR_VERTICAL']for i,c in enumerate(p2)]),'',
 '240km 2발: 원래 normal.json 인덱스 152/153, SM-6, 고도5km, 접근250m/s, seed12001, 종료기 OFF/ON. 두 발 모두 HANDOFF에서 native 기폭 뒤 AIR miss였고 최신에서는 native AIR 명중이다. ARH_MEASUREMENT_FIX_A부터 회복했다.','',
 '극단 고각 1발: 수평0.1km / 고도20km / 정지 Kh-35U / `(rngSeed,navigationSeed)=(1831565813,2047861954)`. HANDOFF/ARH에서 TRACKED_DIVERGENCE, NEAR_VERTICAL부터 native KILL이다. 원래 AIR 시험과 ASM 피해 판정 경로를 섞지 않았다. 별도 신관·유도·종료기 조정은 없다. 세 발 전체 중간 단계 및 기폭 miss/시간은 `PART2_SHOTS.csv`, 원시 궤적은 `results/part2-*.json.gz`에 있다.','',
 '## 3. 게임 코드 변경 여부','',
 '변경 없음. 압축 실행 main의 ENV_D 진단 데이터/accessor 블록 외에는 byte 동일하고, 외부 HTML shell과 자산0–12도 동일하다. 새 함수/물리 계수/발사 정책을 적용하지 않았다. 수정한 별도 파일은 선택적 DDG 회귀 기준값 적용 도구와 CLEAN_A 측정·보고 도구다.','',
 f'내장 표는 `AEGIS_ENVELOPE_TABLE_D_2`, prior 각 행은 `previous`에 그대로 보존. frozen 진단 엔진과 실제 새 HTML에서 추출한 **{native["functions"]}개 native 함수 해시 및 native 엔진 전체 bytes 일치**. profile `status().match=true`는 함수/프로파일 일치를 뜻한다. {build["pendingCells"]}칸이 남은 현재 `effectiveIntervalsComplete=false`, `additionalMeasurementsRequired=true`를 별도로 공개한다. 지도·발사 판정 연결은 없다.','',
 '## 4. 유효 요격 구간','',
 '각 칸 표기: **바깥 / 최소~최대 유효 km**. 운동은 정지 / 접근250 / 접근680 / 이탈250 / 횡단250m/s. 최소는 1~30km 정수 지점 최초 3/5 KILL 또는 STRUCT_FAIL, 그 다음은 최소보다 엄격히 큰 5의 배수부터 연속 5km 간격이다. 최소가 정확히 5의 배수일 때 그 점을 중복 검사하지 않는다.','',
 f'추가 {m["newShotsTotal"]:,}발은 최소거리 탐색에만 사용했다. 기존 같은 빌드·조건·5개 시드 사격은 논리 SHA-256을 확인해 재사용했다. 최대구간의 미측정 점은 실행하지 않았다. 이는 사용자의 “새로 필요한 것은 1~30km 최소거리 사격뿐” 제한과 실제 부족 캐시 사이의 범위 충돌이다. 별도 질문의 답을 기다리며 값을 추정하지 않았다.','']
motions=['STATIONARY','INBOUND_250','INBOUND_680','OUTBOUND_250','CROSSING_250']
actualMotions=list(dict.fromkeys(r['motion']for r in env['rows']));assert len(actualMotions)==5;motions=actualMotions
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 out += ['### '+weapon,'',table(['고도 m',*motions],[[alt,*[(lambda r:f"{r['maxRangeKm']} / {r['effectiveMinKm']}~"+(str(r['effectiveMaxKm'])if r['effectiveMaxKm']is not None else'미확정'))(next(r for r in env['rows']if r['weapon']==weapon and r['altM']==alt and r['motion']==motion))for motion in motions]]for alt in [30,1000,5000,10000,15000,20000]]),'']
out += ['### 이전 0km 13칸','',table(['기종','고도 m','운동','새 최소 km','새 최대 km','끊김/대기 지점 km'],[[r['weapon'],r['altM'],r['motion'],r['effectiveMinKm'],r['effectiveMaxKm']if r['effectiveMaxKm']is not None else'미확정',r['breakPoint']['rangeKm']if r['breakPoint']else r['firstMissingGridKm']]for r in prior_zero]),'',
 '13칸을 전부 “5km보다 먼 최소 사거리 문제”로 해석할 수 없다. 8칸은 1km에서 3/5 이상이지만 5km에서 실패한다. 지정한 첫 구간 정의로는 **1~1km**다. 15km 이후의 다른 성공 구간을 임의로 골라 최대 유효거리를 늘리지 않았다. 이 결과는 거리별 성공이 단조가 아니라는 게임 모델의 관측이며, 사용자 판단 없이 정의/임계값을 바꾸지 않았다.','',
 '대기 5칸은 ESSM 고도5km 접근680(최소7km), 10km 접근680(14km), 15km 접근680(19km), 20km 접근250(10km), 20km 접근680(24km). 기존 최대구간은 5km 실패에서 끊겨 후속 grid가 부족하다. 첫 실패까지 필요한 미측정 5km grid는 최악 38점×5발=190발이며, 기존 결과 재사용과 조기 중단 원칙은 동일하다. 추가 허용 시 실행 스크립트는 준비되어 있다.','',
 '전체 120칸의 요격 지점 평균/최소/최대, 5발 내역, 끊김점, 이전값은 `EFFECTIVE_INTERVALS.csv` 및 `ENVELOPE_TABLE_D.json`에 있다. `NOT_MEASURED`는 빈칸/실패 제외가 아니라 명시적 미측정 상태다. 따라서 C4 전체 완료 판정은 보류한다.','',
 '## 5. 검수 C1–C4와 실행 시간','',
 table(['검수','결과','수치 / 제한'],[['C1','미통과',f'{domain_pass}/420; 원래 기준 414/420. DDG (a) 3개 exact 기준만 갱신, CG (b) 3개 유지'],['C2','PASS','UI88/88, 종료기300, 공통180, 자연RF28, 실제WebGL8; 최신 대비 성공→실패0'],['C3','PASS','무표적/전투 각각120초 truth 해시 동일, 게임 코어 byte 동일'],['C4','보류',f'120개 최소 확정 / {120-build["pendingCells"]}개 전체 구간 확정 / {build["pendingCells"]}개 최대구간 미측정; 이전0km 13개 최소 모두 기록']]),'',
 table(['시험','최신 성공','CLEAN 성공','완전 반환값 차이','실행 초 (최신 / CLEAN)'],[[k,str(v['oldSuccess'])+'/'+str(v['shots']),str(v['newSuccess'])+'/'+str(v['shots']),v['exactResultChanges'],f"{v['elapsedS']['LATEST']:.2f} / {v['elapsedS']['CLEAN']:.2f}"]for k,v in c2.items()]),'',
 '실제 WebGL8발은 양쪽 모두 원래29/29 검사를 통과하고 발사/관측 샘플/최종 물리 반환값이 모두 동일하다. 기존 MR/ER 명중4발 유지, SM-6/ESSM 기존 비명중4발도 그대로다. “8발 검증”을 “8발 명중”으로 세지 않았다. 종료기300은240normal+36dual+12fault+8battery+4정식VLS이고 중복 합산하지 않았다. 자연RF28은 별도 제어된 ASM 경로다.','',
 table(['상태','양쪽 동일 SHA-256'],[['무표적120초',acceptance['C3']['idle']],['전투120초',acceptance['C3']['combat']]]),'',
 '전투 hash 시나리오(SM-6 100km/5km/접근250m/s/seed12002)의 기존 비명중/POST_CROSS 종료도 양쪽 그대로다. 이를 회복 명중으로 올려 세지 않는다.','',
 f'최소거리 추가 사격 벽시계 {m["elapsedS"]:.2f}초(2 workers). 역사 raid 7개 변형, 장기 raid 8쌍, part2 18발, 전체 도메인 15 suites, 두 HTML의 C2/C3를 별도 실행했다. 각 작업 실제 소요는 원시 결과의 `elapsedS`에 보존했다. 동시 실행 시간이 겹치므로 이를 직렬 총시간/실기 FPS로 해석하지 않는다.','',
 '### 재현','',
 '```sh\nexport NODE_PATH=/workspace/aegis-performance-f/docs/performance/F/node_modules\nnode docs/cleanup/A/prepare.cjs\npython docs/cleanup/A/run_history.py\npython docs/cleanup/A/run_raid_studies.py\npython docs/cleanup/A/analyze_part1.py\nnode docs/cleanup/A/intervals.cjs\npython docs/cleanup/A/build.py\nnode docs/cleanup/A/verify_native.cjs\npython docs/cleanup/A/verify_delivery.py\npython docs/cleanup/A/report.py\n```','',
 '브라우저 도구는 Chromium/Playwright 및 기존 저장소 테스트 의존성을 사용한다. 최소거리 cache는 기존 D2 engine/functions/seed와 동일한 것만 재사용한다. 추가 grid는 명시적 scope 승인 파일 없이는 실행할 수 없다. 상세 원시 증거와 스크립트는 REPORT ZIP에 포함한다.','']
(H/'REPORT.md').write_text('\n'.join(out))
save('STATUS.json',{'schema':'AEGIS_CLEAN_A_STATUS_1','state':'PARTIAL_REVIEW_REQUIRED','gameCodeChanged':False,'newLaunchRegressionsRecovered':3,'domainPass':domain_pass,'domainTotal':420,'approvedDDGBaselines':3,'unresolvedCGRegressions':3,'tableRows':120,'effectiveMinKnown':120,'pendingEffectiveMax':build['pendingCells'],'maximumAdditionalGridShots':190,'build':build,'acceptance':acceptance})
print(json.dumps({'domainPass':domain_pass,'C2':acceptance['C2']['pass'],'C3':acceptance['C3']['pass'],'C4':acceptance['C4']['pass']}))
