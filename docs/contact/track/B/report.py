"""Read-only evidence reconciliation; writes REPORT.md only, never expectations.

Root-authored VALIDATION.json is authoritative. Missing/current-SHA incomplete
evidence keeps the report PENDING. Historical RC0/foreign-SHA artifacts are not
promoted to final proof. This is a report generator, not an approval mechanism.
"""
from pathlib import Path
import csv,gzip,hashlib,json

P=Path(__file__).resolve().parent;R=P.parents[3]
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(name):
 path=P/name
 return json.loads(path.read_text())if path.exists()else None
def current(name,candidate,shadow=None):
 value=read(name)
 if value is None:return None,'PENDING (파일 없음)'
 recorded=value.get('candidateSha256',value.get('candidateHtmlSha256'))
 if recorded is not None and recorded!=candidate:return None,'HISTORICAL (현재 ACTIVE SHA와 다름)'
 if shadow and value.get('shadowSha256',shadow)!=shadow:return None,'HISTORICAL (현재 SHADOW SHA와 다름)'
 status=value.get('status','PASS'if value.get('pass')is True else'PENDING')
 if name=='VALIDATION.json':status=value.get('trackBStatus','INCOMPLETE')+(' (증거 완료)'if value.get('finalEvidenceComplete')is True else' (증거 미완료)')
 if name=='REGRESSION_RESULTS.json':
  status='FAIL'if value.get('newStrictFailures')else'PASS'if value.get('allRequestedFreshSuitesExecuted')else'INCOMPLETE'
 if name=='evidence/runtime/execution.json'and not value.get('allRequestedTasksExecuted')and status=='PASS':status='INCOMPLETE'
 return value,status
def cell(value):return str(value).replace('|','\\|').replace('\n',' ')
def table(head,rows):
 return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |',*['| '+' | '.join(cell(x)for x in row)+' |'for row in rows]])

def figure_details(candidate,shadow):
 lines=['## 검증 그림',''];allowed={candidate,shadow,'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'};cache={}
 for name,title,tool in [('native-association','관측 차원·연관·모호성 보류의 직접 native 결과','plot_association.py'),('cohort-proof','NPC·Hawklink cohort의 실제 원래 경로와 ACTIVE 비교','plot_cohort.py')]:
  svg=P/'evidence/figures'/f'{name}.svg';csv_path=svg.with_suffix('.csv');valid=svg.exists()and csv_path.exists();rows=[]
  if valid:
   with csv_path.open(newline='')as stream:rows=list(csv.DictReader(stream))
   for row in rows:
    source=P/'evidence'/row['source_json']
    if source not in cache:cache[source]=sha(source.read_bytes())if source.exists()else None
    valid=valid and row['product_sha256']in allowed and cache[source]==row['source_json_sha256']
  if not valid:
   lines += [title+': INCOMPLETE/HISTORICAL — 현재 제품·원본 JSON SHA 확인 전 그림을 최종 증거로 표시하지 않는다.',''];continue
  lines += ['!['+title+'](evidence/figures/'+name+'.svg)','',
   title+'. 직접 익명 관측 fixture이며 자연 RF 발생률·실제 전투 격추율 그림이 아니다. 원래 JSON source pointer와 제품/helper/source SHA는 [CSV](evidence/figures/'+name+'.csv)에 기록되어 있다. '+str(len(rows))+'개 CSV행의 현재 제품/source JSON SHA를 확인했다. 생성 도구: `'+tool+'`.','',
   '- SVG SHA-256: `'+sha(svg.read_bytes())+'`\n- CSV SHA-256: `'+sha(csv_path.read_bytes())+'`','']
 return lines

def d1_progress(candidate):
 receipt=read('evidence/runtime/active/worker-d1-receipt.json');path=P/'evidence/runtime/active/friendly/ciws-d1.jsonl'
 if not path.exists()and Path(str(path)+'.gz').exists():path=Path(str(path)+'.gz')
 if not receipt or receipt.get('productSha256')!=candidate or not path.exists():return[]
 source=P.parent/'A/evidence/candidate/friendly/ciws-d1.jsonl.gz'
 if not source.exists():return[]
 with gzip.open(source,'rt')as stream:reference={r['case']['seed']:r for r in(json.loads(line)for line in stream if line.strip())}
 rows=[]
 with(gzip.open(path,'rt')if path.suffix=='.gz'else path.open())as stream:raw_lines=stream.read().splitlines(keepends=True)
 for line in raw_lines:
  if line.endswith('\n'):rows.append(json.loads(line))
 changed=[]
 for new in rows:
  old=reference.get(new['case']['seed'])
  if not old or old['signatureSha256']==new['signatureSha256']:continue
  a=old['result'];b=new['result'];changed.append([new['case']['seed'],old['signatureSha256'],new['signatureSha256'],f'{a["shipHits"]}→{b["shipHits"]}',f'{a["hpAfter"]}→{b["hpAfter"]}',f'{a["ciwsUsed"]}→{b["ciwsUsed"]}',f'{a["seconds"]:.6g}→{b["seconds"]:.6g}',[t.get('reason')for t in a['targets']],[t.get('reason')for t in b['targets']]])
 comparison=read('evidence/runtime/active/d1-comparison.json')
 completed=bool(receipt.get('completed')and comparison and comparison.get('productSha256')==candidate)
 completion=(f'원래 strict 결과 **{comparison["status"]}**, 동일 signature {sum(r["sameSignature"]for r in comparison["rows"])}/30.'if completed else'전체30개 strict 판정이 끝나기 전이므로 D1 전체 통과·원인 검증을 선언하지 않는다.')
 lines=['### ACTIVE D1의 현재 관측 차이','',f'현재 완성된 JSONL {len(rows)}/30시드, worker 완료={receipt.get("completed")}. '+completion+' 원래 signature가 다른 시드와 원시 사후 결과를 아래에 모두 남긴다. 결과가 같다는 이유로 signature 기대값을 바꾸거나 승인하지 않는다.','']
 if changed:
  lines += [table(['시드','A signature SHA','ACTIVE signature SHA','피격','HP','CIWS 소모','종료 s','A 사후 결과','ACTIVE 사후 결과'],changed),'']
 else:lines += ['완성된 행에서는 아직 다른 signature가 관측되지 않았다. 이는 미실행 나머지 시드의 통과를 뜻하지 않는다.','']
 lines += ['원문: `evidence/runtime/active/friendly/ciws-d1.jsonl(.gz)` · `worker-d1-receipt.json`. 전송 압축 뒤에는 RAW_COMPRESSION.json의 원문/gzip 해시로 연결한다. 내부 CMS/트랙 차이의 관측된 원인 경로는 아래 별도 계측과 연결하며 원래 strict FAIL은 미승인으로 유지한다.','']
 return lines

def paired_cause_ready(candidate,shadow):
 value=read('evidence/paired-cause/SUMMARY.json');pins={'baseline':'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a','shadow':shadow,'active':candidate}
 return bool(value and len(value.get('runs',[]))==6 and not value.get('errors')and all(r['productSha256']==pins[r['label']]for r in value['runs']))

def causal_details(candidate,shadow):
 lines=['## 미승인 strict 차이 5건의 원인 계측','']
 if paired_cause_ready(candidate,shadow):
  facts=read('evidence/paired-cause/CAUSE_32_FACTS.json');edges=read('evidence/paired-cause-120/CRITICAL_NATIVE_EDGES.json');rows=[]
  for r in facts['runs']:
   d=r['firstDifferences'];hold=r['nativeCriticalDecisions'][0]
   rows.append([r['ship'],f'{hold["tick"]}/{hold["timeS"]:.6f}',f'{d["trackUpdateStream"]["step"]}/{d["trackUpdateStream"]["afterTickTimeS"]:.6f}',f'{d["privateSpyRfRng"]["step"]}/{d["privateSpyRfRng"]["afterTickTimeS"]:.6f}',d['vlsInventory']['step'],d['cachedMass']['step'],r['shadowNativeFieldsExact'],r['diagnosticOnOffNativeFieldsExact']])
  lines += ['### Paired 4건 — 실제 연관 보류에서 적재 이력과 선체 응답으로','',table(['함정','첫 native HOLD tick/s','첫 추정 변화 post-tick/s','private SPY RNG 첫 차이','VLS 차이 tick','mass 차이 tick','A/SHADOW 동일','계측 OFF/ON 동일'],rows),'',
   table(['함정','native 두 matching 합 차이(NIS)','보류 plot','선택 수','거리/radial sanity'],[[r['ship'],r['matchingSums']['absoluteDelta'],r['actualHeldPlots'],r['actualSelectedCount'],r['sanityAllPassed']]for r in edges['rows']]),'',
   'DDG ΔNIS0.04868061886531372, CG0.5153520159868759는 기존 B ambiguity 기준1보다 작아 두 plot이 HOLD됐다. 실제 이미 계산된 native candidate/return을 한 번의 pass-through에서 복사했고 RF/NIS/solver를 추가 실행하지 않았다. 첫8개 edge는 원래 gate64와2500m/180m/s sanity를 모두 통과했다. 첫 원인은 sanity 거부나 component 크기 제한이 아니다.','',
   '관측된 순서는 **모호한 대안 보류 → local 평균/P·갱신/scheduler 이력 변화 → 기존 표적/발사 일정 변화 → 기존 적재 ledger/선체 해석기 응답**이다. 두 함에서 SAM2가 A tick528(8.8초)에서 B tick540(9.0초)으로 늦어졌다. A는528에 기존 SM-2 적재708kg을 먼저 소비하고 B는 유지했으며, 다음529tick에서 기존 mass/CG·GM0·heel/draft가 처음 달라졌다. 그 이전 기록된 물리 스칼라는 같았다.','',
   '32초 최종 mass/CG·GM0·global RNG가 다시 같아도 적분기는 다른 적재 시점의 이력을 보존한다. flood-door world 높이와 갑판에 붙은 cold 헬기 좌표, 자세에서 파생된 effectiveGMM도 따라 달라진다. 최종 effectiveGMM 차이는 GM0 계수 변경이 아니다. 계수·기대값·허용 오차 조정 없이 원인 경로를 확인했지만 paired4 FAIL은 계속 미승인이다.','',
   '원래32초6page는 각1921행(초기+1920tick), A/SHADOW 및 계측 OFF/ON 동등성, 원래 archive와 endpoint5항목·native source SHA를 검증했다. DDG 넓은 ON 기록은10MiB 목표를 넘어선 시험 기록 폭 제한도 공개했다. 후속120초는3.0–3.8초 candidate만 자세히 기록하고1Hz scalar로 줄였으며 과거 실패 시도를 숨기지 않았다. [원인 보고서](PAIRED_CAUSE_RESULTS.md) · [32초 SUMMARY](evidence/paired-cause/SUMMARY.json) · [실제 native edge](evidence/paired-cause-120/CRITICAL_NATIVE_EDGES.json).','']
  extension=read('evidence/paired-cause-120/OUTCOME_REVIEW.json');summary=read('evidence/paired-cause-120/SUMMARY.json')
  if extension and summary and len(summary['runs'])==4 and all(r['productSha256']=={'baseline':'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a','active':candidate}[r['label']]for r in summary['runs']):
   rows=[]
   for r in extension['rows']:
    a,b=r['versions'];rows.append([r['ship'],f'{a["samRamLaunchCount"]}→{b["samRamLaunchCount"]}',f'{a["loadedVlsCells"]}→{b["loadedVlsCells"]}',f'{a["hp"]}→{b["hp"]}',f'{a["waterM3"]}→{b["waterM3"]}',f'{a["nativeInterceptEvents"]}→{b["nativeInterceptEvents"]}',f'8 Kh-32 +{a["laterSpawnCount"]} Kh-35U 모두 alive'])
   lines += ['### 새120초 연장 관측 — 완료된 전투가 아님','',table(['함정','SAM/RAM 발사 A→B','VLS 셀 A→B','HP','침수 m³','native 요격 사건','ASM 상태'],rows),'',
    f'연장4건은 원래 설정에서 horizon만1920→7200tick으로 바꾼 별도 신규 시험이다.32초 checkpoint24/24가 원래 실행과 정확히 같았고 {extension["wallS"]:.3f}초에 완료했다. 두 함 모두 module damage0·NORMAL이지만, 최초8발과 뒤에 스폰한13발이 모두 살아 있고 요격/체계피격/함선피격 사건0이다. **최종 전투가 해결됐거나 요격 성능이 보존됐다고 주장할 수 없다.** 자원 차이는 그대로 보고하고 새120초 검사를 원래420/42 기대값에 합산하지 않는다.','',
    '일부 SAM에 native `_deathReason`가 없어 WEAPON_END를 완전 분류했다고 주장하지 않는다. 누락 사건이나 alive=false만으로 격추를 만들지 않는다. [120초 결과](evidence/paired-cause-120/OUTCOME_REVIEW.json) · [SUMMARY](evidence/paired-cause-120/SUMMARY.json) · [horizon-only diff](evidence/paired-cause-120/horizon-only.diff).','']
 execution=read('evidence/seed419012-cause/EXECUTION.json');analysis=read('evidence/seed419012-cause/ANALYSIS.json')
 if execution and analysis and all(r['productSha256']=={'baseline':'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a','active':candidate}[r['label']]for r in execution['products']):
  lines += ['### D1 seed419012 — 파일 제거가 아닌 기존 CMS cue 순서 변화','',
   '계측한29.0초 첫 프레임부터 A/B에 두 canonical 파일이 모두 있었다. 두 번째는 VISUAL·1hit이고29–30.65초 창에 CREATE가 없다. “B가 두 번째 파일의 생성을 없앴다”는 초기 가설은 자료와 맞지 않는다. 앞선 생성 이력과 두 파일의 실제 물리 표적 동일성은 이 창으로 증명하지 않으며 duplicate 제거라고 쓰지 않는다.','',
   table(['native tick1796 동일 SPY 관측의 후보','AIR4D NIS'],[['track300000001',1.4913444179610076],['track300000002',1.1536789827861333],['대안 차이',analysis['nativeCandidateNisDifference']]]),'',
   '같은 관측·gate64 안에서 A는 작은 NIS의002를 갱신했고, B는 대안 차이0.33766543517487424가 기존 기준1 이하여서 OWN_SPY_GLOBAL/AMBIGUOUS_ASSOCIATION HOLD를 기록했다. post-tick1797부터 평균/P·freshness와 캐시 cue 값이,1800부터 cue 순서와 실제 mount cue가 달라졌다. 이어 focused 재방문과 VISUAL/SPQ 기여 이력도 달라졌다. metadata-only 차이가 아니다.','',
   table(['최종 frame1838 실제 캐시','native1순위','TTI s','native2순위','TTI s'],[['A GUN','002',6.976145618993533,'001',7.0423472604731465],['B GUN','001',7.000081519721263,'002',7.024040628315056],['A RAM','002',6.989602928597308,'001',7.050597368522857],['B RAM','001',7.003378644115532,'002',7.033123797618139]]),'',
   '기존 native C55는 이미 만들어 정렬한 CMS cue의 첫 trackId를 cuedTarget에 넣는다. 실제 사격용 음수 로컬 파일은 GUN -5500001/RAM -5500002로 A/B 같았고, 캡처99프레임의 로컬 추정·보호·무장 상태도 같았다. 최종 after의 차이는 두 mount cue002→001뿐이다. 사후 CMS 거리 replay와 실제 관측된 선택은 ANALYSIS에서 구분했다.','',
   '양쪽 모두 RAM3발/GUN0발, 피격0·HP100·생존,30.633333초에 같은 결과였다. 마지막 RAM PROX_DETONATION_KILL·최근접4.747193334345742m·global RNG3594350424도 같다. 전체30시드 전투 결과/자원은 같지만 signature29/30의 strict FAIL은 미승인이다. 이 결과를 모든 private RF 상태·장래 전투 불변으로 확장하지 않는다.','',
   'A/B 계측은 각 원래 OFF signature와 정확히 일치하고 query/상태·private RNG 무변경, 금지 진실 필드0·fault/overflow0을 확인했다. 원래 diagnostic.js의 두 wrapper는 결과 수집 후 최초 참조만 복원하고 추가tick 없이 awaited ENV match를 확인했다. 복원 전 guard 실패도 보존했다. 모든 원시 차이를 남겼으며 일부 cue만 설명한 것이 원시 diff 삭제는 아니다. [원인 보고서](SEED419012_CAUSE_REPORT.md) · [ANALYSIS](evidence/seed419012-cause/ANALYSIS.json) · [실행 영수증](evidence/seed419012-cause/EXECUTION.json).','']
 return lines

def final_cost_details(candidate):
 value=read('evidence/cost-final/SUMMARY.json')
 if not value or value.get('completionStatus')!='COMPLETE' or len(value.get('records',[]))!=9:
  return ['## 최종 단독 성능 관측','', '**INCOMPLETE:** 기존 동시 호스트 측정은 raw 자료로 보존하지만 비용 판정의 주 자료로 사용하지 않는다. 두 browser lease를 모두 잡는9개 순차 측정이 닫힐 때까지 최종 표를 출력하지 않는다.','']
 pins={'A':'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a','B':candidate}
 if any(r['productSha256']!=pins.get(r['product'])for r in value['records']):return ['최종 비용 자료는 현재 제품 SHA와 달라 HISTORICAL로 제외한다.','']
 cpu=[r for r in value['records']if r['kind']=='cpu'];alloc=[r for r in value['records']if r['kind']=='allocation']
 lines=['## 최종 단독 성능 관측','',
  f'동시 브라우저가 없는 preflight를 확인하고 두 lease를 전체 측정 동안 독점한 순차9구성이다. CPU는30초 warmup+2400tick, allocation은 두 owner120tick warmup+600tick이다. 반복 순서를 뒤집었고 원시 샘플을 제외하지 않았다. 총 {value["wallS"]:.3f}초, 측정 검수 {value["status"]}. 기존 concurrent-host cost/raw sampling 자료는 지우지 않고 NOT_FINAL_FOR_COST_ASSESSMENT로 구분한다.','',
  table(['제품','반복','진단','평균 ms/tick','median','p95','live heap 변화 B'],[[r['product'],r['repetition'],'ON'if r['trace']else'OFF',f'{r["meanTickMs"]:.5g}',f'{r["medianTickMs"]:.5g}',f'{r["p95TickMs"]:.5g}',r['liveHeapDeltaBytes']]for r in cpu]),'',
  table(['제품','진단','두 owner 각tick','GC 포함 sampling 추정 B','sample 수'],[[r['product'],'ON'if r['trace']else'OFF',r['fixedTicks'],r['sampledAllocation']['sampledBytesEstimate'],r['sampledAllocation']['sampleRecords']]for r in alloc]),'',
  table(['검수','값'],[[k,v]for k,v in value['checks'].items()]),'',
  'CPU 주 측정은 원래 함수를 감싸는 kernel timer 없이 실제 fixed tick을 실행했다. 별도 allocation sample은 GC로 수거된 객체도 포함하도록 major/minor 옵션을 켰다. 이는 통계적 총할당 추정이며 정확한 byte/count가 아니다. live heap delta는 GC 때문에 음수가 될 수 있는 순수 live 변화로 총 churn이 아니다. 원시 profile·tick samples·preflight·source hashes를 모두 남겼다.','',
  'allocation에서 부모 surfacePosition21회가 각각 중첩 surface를1회 호출했다. 이 inclusive 호출/시간은 겹치므로42개의 고유 candidate나 총CPU로 합산하지 않는다. AIR/cartesian은0회여서 해당 kernel이나 dense raid 스트레스를 포괄 검증했다고 쓰지 않는다. A/B 및 진단 OFF/ON의 body·track/P·private RNG 동등성은 위 검수 범위다. 성능 수치를 자동 승인하거나 신뢰할 수 있는 속도 향상으로 단정하지 않는다. [최종 SUMMARY](evidence/cost-final/SUMMARY.json) · [ASSESSMENT](evidence/cost-final/ASSESSMENT.json) · [COST_FINAL](COST_FINAL.md) · [PROVENANCE](evidence/cost-final/PROVENANCE.json) · [독점 lease](evidence/cost-final/LEASE.json).','']
 assessment=read('evidence/cost-final/ASSESSMENT.json')
 if assessment and assessment.get('candidateSha256')==candidate:
  lines += [table(['CPU 반복','B OFF vs A OFF 평균 %','B ON vs B OFF 평균 %'],[[r['repetition'],f'{r["BoffVersusAoffMeanPercent"]:+.4f}',f'{r["BonVersusBoffMeanPercent"]:+.4f}']for r in assessment['cpuPairedComparisons']]),'',
   '두 반복에서 B OFF는 -2.4868%/+0.0182%, 진단 ON 추가분은 +4.0247%/+4.3732%였다. 관측한 두 반복의 값이며 통계적 유의성이나 일반적인 속도 향상을 주장하지 않는다. 원시 샘플 제외0, 최종 측정 구간 resource event 변화 없음. 이전 동시 호스트/retained-only sampling 자료는 [runtime 비용 해석](evidence/runtime/COST_CONTEXT_NOT_FINAL.json)에 따로 보존한다.','']
 return lines

def evidence_details(candidate,shadow,build,scope,broad,runtime):
 """Current-SHA details only; no approval or new simulation computation."""
 lines=['## 신규 B 검증과 보호 범위 상세','']
 unit=read('evidence/solver-unit.json');module_sha=next((m.get('sourceSha256')for m in build.get('modules',[])if m['path']=='association.js'),None)
 native,native_status=current('evidence/native-integration/SUMMARY.json',candidate,shadow)
 supplement,supplement_status=current('evidence/cohort-supplement/SUMMARY.json',candidate,shadow)
 protected=scope.get('protectedSymbols',[])if scope else[];nested=scope.get('nestedProtectedSymbols',[])if scope else[]
 unit_current=bool(unit and module_sha and unit.get('moduleSha256')==module_sha)
 lines += [table(['검사','결과','구분'],[
  ['보호 심볼',f'{sum(r["equal"]for r in protected)}/{len(protected)} byte 동일','SCOPE.json'],
  ['중첩 보호 커널',f'{sum(r["equal"]for r in nested)}/{len(nested)} byte 동일','nested 합산 성능 지표 아님'],
  ['solver unit',f'{unit["passed"]}/{unit["count"]} {unit["status"]}'if unit_current else'INCOMPLETE/HISTORICAL','현재 association 모듈 SHA 일치 필요'],
  ['native 익명 관측 통합',native_status,'23 group, 자연 RF·전투 증거 아님'],
  ['NPC/Hawklink cohort 보충',supplement_status,'별도 직접 native fixture']]),'',
  '신규 unit/native/cohort 단언을 기존 domain420에 더하지 않는다. 직접 native fixture는 실제 기존 연관·필터·소비 함수를 호출하지만 자연 RF 발생률이나 실제 전투 성공을 대신하지 않는다. ACTIVE 모듈 SHA: `'+str(module_sha)+'`.','']
 if native:
  rows=[]
  for mode in ['off','on']:
   raw=read('evidence/native-integration/active-'+mode+'.json')
   if raw and raw['productSha256']==candidate:
    checks=raw['nativeResult']['checks'];rows.append([mode.upper(),sum(bool(v)for v in checks.values()),len(checks),raw['queryGameStateUnchanged'],raw['envMatch']])
  lines += [table(['ACTIVE 진단','통과','검사','query 상태 무변경','ENV match'],rows),'',
   table(['제품 OFF/ON','fixture 수','각 fixture 상태/private RNG 동일','최종 상태 동일'],[[r['label'],r['fixtureCount'],r['perFixtureGameAndPrivateRngSha256Exact'],r['postAllFixturesStateExact']]for r in native.get('traceOnOff',[])]),'',
   f'SHADOW 원래 native 기록 동일: {native["shadowOriginalNativeRecordsExact"]}. C55의 진단 ON 전용8항목은 원시 SHADOW ON 열로 보고했다. 이 보고 열 수정은 raw 점수·상태·소스·기대값을 변경하지 않았다. 근거: [native SUMMARY](evidence/native-integration/SUMMARY.json).','']
 if supplement:
  rows=[]
  for product in ['baseline','shadow','active']:
   raw=read('evidence/cohort-supplement/'+product+'-native-result.json')
   if not raw or raw['productSha256']!={'baseline':'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a','shadow':shadow,'active':candidate}[product]:continue
   records=raw['nativeResult']['records'];npc=records['npcActualGreedyTrap'];hawk=records['hawklinkActualSequentialFalseReplay']
   rows.append([product,npc['associatedDelta'],npc['birthDelta'],npc['fileCount'],hawk['acceptedDelta'],hawk['rejectedDelta'],hawk['fileCount']])
  lines += ['### NPC·Hawklink 실제 소비 경로 보충','',table(['제품','NPC 연관','NPC 신규','NPC 파일','Hawk 접수','Hawk 거부','Hawk 파일'],rows),'',
   f'ACTIVE 신규 검사 {supplement["activeChecks"]["passed"]}/{supplement["activeChecks"]["count"]} PASS. 실제 기준 경로에서 NPC greedy trap과 Hawklink sequential false-replay가 재현됐다. ACTIVE는 원래 두 파일을 각각 한 번 갱신하고 원 측정 시각·owner 독립성·identity/authority 무승격을 유지했다. SHADOW의 원래 native 결과/private game RNG는 A와 같았다. 이 결과는 자연 RF·실제 전투 시험이 아니다.','',
   '새 B 계약의 대조 검사에서 A/SHADOW는 각각 5/14였고 ACTIVE는 14/14다. 이는 기존 회귀 기대값을 바꾼 점수가 아니라 새 계약을 같은 실제 native 경로에 적용한 결과다.','',
   '최초4030m midpoint 시험은 부동소수 변환 때문에 결함을 재현하지 못해 attempts에 보존했다. 최종 보충 fixture는 보고 위치만1m 옮긴4029m로 원래 sequential 선택을 명확히 만들었다. 제품 comparator·계수·Pd/Pk는 바꾸지 않았다. 접근자 오류 시도와 재현 실패도 숨기지 않았으며 원래 native 통합 helper를 고쳐 통과시킨 것이 아니다. [보충 SUMMARY](evidence/cohort-supplement/SUMMARY.json) · [PROVENANCE](evidence/cohort-supplement/PROVENANCE.json).','']
 lines += figure_details(candidate,shadow)
 if broad:
  rows={r['suite']:r for r in broad['rows']};pair=rows.get('paired-track-a',{});failed=sum(len(r.get('failedAssertions',[]))for r in broad['rows']if r['status']=='FAIL')
  lines += ['## 원래 회귀 총계와 신규 strict 실패','',
   f'원래 domain420: **{broad["currentVsTrackADomain"]["passed"]} PASS / {failed} strict FAIL / 14 INCOMPLETE** = native364 +paired38/42 +retired UI14. 기존 기준값·허용 오차 갱신0. fresh16개 suite는 모두 실행됐고 pending은 {broad.get("pendingFreshSuites")}다. 실행 시간 {broad["wallS"]:.1f}초 ({broad["wallS"]/60:.2f}분). aggregate exit1은 paired4 strict FAIL 보존 때문이다.','',
   table(['별도 lane','결과','상태'],[['UI',f'{rows.get("ui213",{}).get("passedAssertions")}/213',rows.get('ui213',{}).get('status')],['자연 탐지→LOCK→정식 VLS→fixed tick→실제 WebGL',f'8발/{rows.get("webgl8",{}).get("passedAssertions")}/29 단언',rows.get('webgl8',{}).get('status')]]),'',
   'WebGL29 PASS는8발 모두 격추라는 뜻이 아니다. 이 숫자를 domain420에 중복 더하지 않는다. 최초 CG→friendly404/observer2 미승인/legacy14 이력도 이번402/4/14와 별도로 남는다.','',
   table(['원래 실패 단언','상태'],[[name,'FAIL ·기대값 불변·승인 없음']for name in pair.get('failedAssertions',[])]),'']
 review,review_status=current('PAIRED_DELTA_REVIEW.json',candidate)
 if review:
  lines += [table(['함정','HP A→B','VLS A→B','global RNG A→B','observer 변경 leaf'],[[r['ship'],f'{r["before"]["shipHP"]}→{r["after"]["shipHP"]}',r['loadedVlsBeforeAfter'],f'{r["before"]["globalRng"]}→{r["after"]["globalRng"]}',r['observerChangedLeaves']]for r in review['rows']]),'',
   table(['함정','heel rad A→B','effective GM m A→B','최종 mass/CG 동일','water kg A→B'],[[r['ship'],f'{r["before"]["heelRad"]:.10g}→{r["after"]["heelRad"]:.10g}',f'{r["before"]["effectiveGMM"]:.10g}→{r["after"]["effectiveGMM"]:.10g}',r['selectedFinalMassAndCgExact'],f'{r["before"]["waterMassKg"]}→{r["after"]["waterMassKg"]}']for r in review['rows']]),'',
   ('아래 별도 계측으로 관측된 원인 경로는 확인했으며 strict FAIL은 미승인으로 유지한다. 'if paired_cause_ready(candidate,shadow)else'현재 원인 미검증·미승인이다. ')+ 'full inventory·module damage·최종 mass/CG·global RNG는 같지만 실제 heel/흘수/부력/GM과 observer 값은 다르다. 모든2259 leaf 차이를 보존했으며 물리 차이를 metadata로 제외하지 않는다. 원래 기대값·허용 오차는 바꾸지 않는다. 초기 PAIRED_DELTA_REVIEW의 원인 대기 표기는 최초 endpoint 기록이고, 후속 원인 증거는 아래 자료로 별도 연결한다.','',
   '**32초 endpoint 한계:** 두 함 모두 이때 HP100·물0이고,8발 Kh-32가 모두 alive이며 intercept 기록은 비어 있다. 이는 전체 습격의 최종 격추·생존 동일을 입증하지 않는다.8발 요격 성공으로 표현하지 않는다. AFTER_ACTION truth는 사후 비교에만 쓰고 실시간 소비자에 연결하지 않는다. [전후 검토](PAIRED_DELTA_REVIEW.json) · [모든 leaf diff](evidence/regression/paired-state-deltas.json.gz).','']
  attempts=[]
  for index in [1,2]:
   attempt=read(f'evidence/paired-cause/ATTEMPT_{index}_FAILURE.json')
   if attempt:attempts.append([index,attempt['status'],attempt['stage'],attempt['error'],attempt.get('causeConfirmed'),attempt['productCodeChanged']])
  if attempts:
   lines += ['### 별도 원인 계측의 실패 시도','',table(['시도','상태','구간','실패 내용','해당 원인 확정','제품 코드 변경'],attempts),'',
    '첫 시도는 원래 raid 실행 후 큰 cache/timeline을 가져오던 중 browser target이 죽어 INCOMPLETE다. 같은 A 실행 구간의 host OOM counter 증가1은 별도 환경 관측이며 제품 결함 원인으로 확정하거나 승인하지 않는다. bounded scalar/chunk 읽기로 계측 도구를 재시도한다. 두 번째 시도는 기존 최종 pipeline wrapper와 base 함수의 서로 다른 SHA를 비교한 도구 검사 오류로, 실제 base reference와 기존 outer wrapper를 각각 비교하도록 고쳤다. 두 시도 모두 원래 fixture 명령·제품 코드는 바꾸지 않았으며 최종 원인 증거나 PASS로 세지 않는다. [시도1](evidence/paired-cause/ATTEMPT_1_FAILURE.json) · [시도2](evidence/paired-cause/ATTEMPT_2_FAILURE.json).','']
 lines += ['## Runtime 도구 수정 이력과 진행 한계','',
  '초기 도구 a151ee2a…b7f75는 async `__ENV_D__.status()`의 Promise를 기다리기 전에 `.match`를 읽어 변경 없는 TRACK-A 자연3에서도 ENV check만 거짓 실패했다. 원래 결과·query·상태는 일치했다. root 승인으로 원래 A처럼 전체 Promise 결과를 기다린 뒤 **같은 match===true 조건**을 검사하도록 고쳤다. 현재 도구 SHA는 `a173e069a62db844baa4d0dfd298e43209749c93dab5580deaecc30b76905523`이다. 전체 resolved ENV status와 worker별 실제 loaded-controller/source receipt를 저장한다. 제품·ENV hash 기준·기대값을 완화하지 않았다.','',
  '잘못된 async guard의 REPRO/TRACE 시도·초기 source/provenance·로그는 `evidence/runtime/attempts/async-env-guard-a151/`와 재시도 snapshot에 남겼다. D1 PASS의 초기 script는 da73163에서 복구 가능하고 `original_script()` 함수는 수정 전/후 byte 동일(SHA `a54b4bb5f08c8502f385973ba1f82a342b84a75d51a8e8b769681295f46557c4`)이다. 과거 거짓 실패를 제품 수정 성과나 승인된 결과로 세지 않는다.','']
 lines += d1_progress(candidate)
 lines += causal_details(candidate,shadow)
 required={(p,t)for p in ['baseline','shadow','active']for t in ['d1','repro','trace','auto-iff','idle','clocks','performance','allocation']};records=runtime.get('rows',[])if runtime else[]
 closed=bool(runtime and runtime.get('allRequestedTasksExecuted')is True and required<={(r['product'],r['task'])for r in records})
 if not closed:
  lines += ['**INCOMPLETE:** runtime24개가 아직 모두 닫히지 않아 전후 성능 비교는 출력하지 않는다. 일부 완료 샘플을 골라 결론 내리지 않는다. root VALIDATION도 아직 최종 완료 근거로 사용하지 않는다.',''];return lines
 lines += final_cost_details(candidate)
 return lines
def main():
 build=read('BUILD.json')or{};shadow_build=read('BUILD_SHADOW.json')or{};candidate=build.get('htmlSha256');shadow=shadow_build.get('htmlSha256');validation,validation_status=current('VALIDATION.json',candidate,shadow)
 product=R/build.get('output','Aegis_SIM_v48_WIP_TRACK_B.html');shadow_product=R/shadow_build.get('output','Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html')
 bytes_match=bool(candidate and shadow and product.exists()and shadow_product.exists()and sha(product.read_bytes())==candidate and sha(shadow_product.read_bytes())==shadow)
 native,native_status=current('evidence/native-integration/SUMMARY.json',candidate,shadow);broad,broad_status=current('REGRESSION_RESULTS.json',candidate);runtime,runtime_status=current('evidence/runtime/execution.json',candidate,shadow);scope,scope_status=current('SCOPE.json',candidate)
 # Finished evidence may contain FAILs. Do not relabel completed failing work
 # as unexecuted, and do not conflate evidence closure with a stage approval.
 authoritative_complete=bool(validation and validation.get('finalEvidenceComplete')is True and bytes_match)
 stage=validation.get('trackBStatus','PENDING')if validation else'PENDING';closure=validation.get('finalClosure','INCOMPLETE')if validation else'INCOMPLETE'
 lines=['# TRACK-B 보고서','',f'현재 단계: **{stage}** · 증거 정리: **{"완료"if authoritative_complete else"PENDING"}** · 전체 종료: **{closure}** · releaseApproved: **false**.','',
 '선언한 live 구현 계약은 PASS지만, 원래 paired4건과 D1 signature1건은 원인 계측 후에도 사용자 미승인 strict FAIL이다. 증거 수집 완료와 단계 승인·전체 TRACK-B closure를 구별한다. C55/SPQ AIR 등 SHADOW-only 범위와 기존 미해결 항목도 남아 있다.','',
 'TRACK-A 위의 연관 변경과 진단 범위만 다룬다. 원래 기대값·허용 오차를 갱신하지 않으며, OODA·새 전술 AI·TRACK-C/D를 구현하지 않는다. 기존 419025 피격 FAIL, CG→friendly observer 2건 미승인 KNOWN_DELTA, 구형 EMCON UI14 INCOMPLETE를 승인하거나 해결했다고 표시하지 않는다.','',
 '## 빌드와 증거의 연결','',table(['항목','값'],[['기준','ee960db / TRACK-A e2c1976a…96d67a'],['ACTIVE SHA-256',candidate],['SHADOW SHA-256',shadow],['실제 HTML byte와 BUILD 일치',bytes_match],['authoritative VALIDATION',validation_status],['main/기준 브랜치 병합·release/tag','수행하지 않음']]),'',
 'SHADOW/ACTIVE는 build-time 정책이다. 진단 ON/OFF는 알고리즘 mode·RF·EKF·IFF·교전 권한을 바꾸지 않는다. 실제 적용 경로, SHADOW로 남긴 경로, 보호 심볼의 세부 사항은 IMPLEMENTATION_PLAN/OWN_NPC_AUDIT/C55_AUDIT/NETWORK_AUDIT와 scope 증거를 함께 읽어야 한다.','',
 '## 검증 현황','']
 rows=[['제품 checksum', 'PASS'if bytes_match else'PENDING','ACTIVE/SHADOW 실제 bytes와 BUILD'],['보호 범위',scope_status,'SCOPE.json'],['직접 native 익명 관측 통합',native_status,'자연 RF·실제 전투로 세지 않음'],['원래 광역 회귀',broad_status,'364 native +42 paired; legacy14 별도 INCOMPLETE'],['runtime A/SHADOW/ACTIVE',runtime_status,'원본 D1/자연3/진단/시계/IFF/idle/owner·비용']]
 lines += [table(['검증','상태','범위'],rows),'']
 if broad:
  lines += [table(['원래 lane','실행/통과/기대','미승인 또는 미완료'],[['native13',f'{broad["native13"]["executedAssertions"]}/{broad["native13"]["passedAssertions"]}/364','기존 assertion 그대로'],['paired',f'{broad["currentVsTrackADomain"]["pairedPassed"]}/42','모든 원시 state leaf 차이 보존'],['신규 strict FAIL',', '.join(broad.get('newStrictFailures',[]))or'없음','자동 승인 없음'],['미실행 fresh suite',', '.join(broad.get('pendingFreshSuites',[]))or'없음','빈칸을 PASS로 처리하지 않음'],['구형 EMCON UI','14 INCOMPLETE','retired #lockBtn 기대값 불변']]),'']
 if runtime:
  lines += [table(['variant','task','상태','exit'],[[r['product'],r['task'],r['status'],r['exitCode']]for r in runtime.get('rows',[])]),'']
 lines += evidence_details(candidate,shadow,build,scope,broad,runtime)
 lines += ['## 차이와 비용의 해석','',
 '원래 strict 검사 실패는 FAIL로 보존한다. 변경된 observer·상태·공분산·분류·identity·freshness·private RNG를 제거해 동일하다고 만들지 않는다. 자연 재현의 원시 결과와 AFTER_ACTION_TEST_ONLY 전체 관련 track/observer 사본은 비교 전에 저장한다. 같은 제품의 trace OFF/ON 및 snapshot 조회 순수성과, ACTIVE의 외국/NPC 연관에서 생긴 A 대비 변화는 서로 다른 검사다. 변화의 원인 검증 전 자동 KNOWN_DELTA/PASS 승격은 하지 않는다.','',
 'CPU 평균·median·p95는 shared host의 raw proxy다. 모든 반복과 outlier를 유지하고 신뢰할 수 있는 속도 향상으로 단정하지 않는다. nested kernel timing/counter는 겹치므로 합산하지 않는다. live heap delta는 총 할당량이 아니며 heap sampling은 통계적 추정이다.','',
 '## 이력과 남은 항목','',
 'RC0(79a098a8…)는 실제 native contract에서 own-SPY 연결 누락3건이 발견된 실패 후보다. 해당 기록은 attempts 아래 historical로 보존한다. 이 agent의 RC0 broad lane은 브라우저를 시작하기 전에 중단되어 NOT_EXECUTED이며, RC0 파일을 새 후보의 회귀 PASS로 재사용하지 않는다. 초기 5σ proposal과 최종 2500m/180m/s hard cap도 구분한다.','',
 '미해결 원래 전투 손실과 observer 차이는 TRACK-B 검수 통과만으로 승인되지 않는다. paired4+D1 signature1의 관측된 원인 경로는 후속 계측으로 확인했지만 기대값을 갱신하지 않았고 사용자 승인 전까지 FAIL을 유지한다. C55/SPQ AIR의 interleaved 경로처럼 SHADOW에 남은 범위는 live batch 완료라고 표현하지 않는다. TRACK-C/D 설계는 후속 단계이며 이번 완료 판단에 포함하지 않는다.','',
 '실행 명령과 재현 조건은 README.md / REGRESSION_PLAN.md / TEST_PLAN.md를 따른다. 이 생성기는 test result·원래 기준·제품·checksum을 수정하지 않고 REPORT.md만 쓴다.']
 (P/'REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'report':'docs/contact/track/B/REPORT.md','stage':stage,'finalEvidenceComplete':authoritative_complete,'validation':validation_status,'releaseApproved':False}))
if __name__=='__main__':main()
