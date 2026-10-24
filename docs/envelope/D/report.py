"""Publish measured tables, all shot summaries, SEA_IMPACT rows and native plots."""
from pathlib import Path
import collections,csv,gzip,json,os,statistics
os.environ.setdefault('MPLCONFIGDIR','/tmp/aegis-env-d/mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;O=H/'results';P=H/'plots';P.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text())
m=load(O/'measurement.json');reg=load(H/'REG_K_RESULTS.json');cost=load(H/'COST_ESTIMATE.json')
f=json.loads(gzip.decompress((O/'followup.json.gz').read_bytes()));build=load(H/'build.json');delivery=load(H/'evidence/delivery-verification.json')
# Inner-point averages use native KILL/STRUCT_FAIL shots; raw cell aggregates
# remain untouched and retain their all-effect point statistics.
for row in m['rows']:
 q=row['effectiveBoundary'];values=[s['interceptPointKm']for s in q['shots']if s['lethal']]if q else[]
 row['effectiveEffectInterceptPoint']=row['effectiveInterceptPoint']
 row['effectiveInterceptPoint']={'meanKm':sum(values)/len(values),'minKm':min(values),'maxKm':max(values),'shotCount':len(values)}if values else None
cols=['origin','cellId','targetLabel','weapon','altM','motion','rangeKm','rngSeed','navigationSeed','outcome','missionKills','reason','success','lethal','closestM','fuzeMissM','interceptPointKm','targetInterceptPointKm','flightTimeS','apogeeM','terminalSpeedMps','descentStartS','descentMode','descentStage']
sea=[];outcomes=collections.Counter();shotCount=0;spread=[]
with gzip.open(O/'all-measurement-shots.csv.gz','wt',newline='')as out:
 w=csv.DictWriter(out,fieldnames=cols);w.writeheader()
 for p in sorted((O/'cells').glob('*.json.gz')):
  j=json.loads(gzip.decompress(p.read_bytes()));cell=j['cell']
  for d in j['distances']:
   spread.append({'cellId':cell['cellId'],'rangeKm':d['rangeKm'],**d['closestRangeM']})
   for s in d['shots']:
    shotCount+=1;outcomes[s['outcome']if s['outcome']!='FAILURE'else s['reason']]+=1
    row={k:s.get(k)for k in cols};row.update({k:cell.get(k)for k in ['cellId','targetLabel','motion']});row['origin']='FULL_SWEEP';row['missionKills']=';'.join(s['missionKills']);row['terminalSpeedMps']=s['terminal']['speedMps']
    descent=s['descentStart']or{};row.update(descentStartS=descent.get('timeS'),descentMode=descent.get('mode'),descentStage=descent.get('stage'));w.writerow(row)
    if s['reason']=='SEA_IMPACT':sea.append(row)
assert shotCount==m['calls']
mainSeaCount=len(sea)
def additionalSea(s,origin,ident):
 if s['reason']!='SEA_IMPACT':return
 row={k:s.get(k)for k in cols};row.update(origin=origin,cellId=ident,
  motion='CROSS_250'if s.get('crossSpeedMps')else'STATIONARY'if not s.get('targetSpeedMps')else'INBOUND_'+str(s['targetSpeedMps'])if s['targetSpeedMps']>0 else'OUTBOUND_'+str(-s['targetSpeedMps']),
  missionKills=';'.join(s['missionKills']),terminalSpeedMps=s['terminal']['speedMps'])
 descent=s['descentStart']or{};row.update(descentStartS=descent.get('timeS'),descentMode=descent.get('mode'),descentStage=descent.get('stage'));sea.append(row)
for q in f['boundaries']:
 for s in q['shots']:additionalSea(s,'BOUNDARY_REPLAY',q['cellId'])
for q in f['trajectories']:
 if q['result']:additionalSea(q['result'],'TRAJECTORY',q['id'])
for q in f['replays']:additionalSea(q['result'],'TRAJECTORY_REPLAY',q['id'])
for q in f['historical']:
 for s in q['firstSeedProbes']:additionalSea(s['result'],'HISTORICAL_BOUNDARY_PROBE',str(q['weapon'])+'_'+str(q['altM']))
pilotPath=H/'evidence/pilot.json'
pilot=load(pilotPath)if pilotPath.exists()else json.loads(gzip.decompress((H/'evidence/pilot.json.gz').read_bytes()))
for i,q in enumerate(pilot['records']):
 for s in q['shots']:additionalSea(s['result'],'COST_PILOT',str(i))
with gzip.open(O/'SEA_IMPACT.csv.gz','wt',newline='')as out:
 w=csv.DictWriter(out,fieldnames=cols);w.writeheader();w.writerows(sea)
with(O/'seed-closest-spread.csv').open('w',newline='')as out:
 w=csv.DictWriter(out,fieldnames=['cellId','rangeKm','min','max']);w.writeheader();w.writerows(spread)
tableCols=['cellId','weapon','targetLabel','altM','motion','maxRangeKm','effectiveRangeKm','maxPointMeanKm','maxPointMinKm','maxPointMaxKm','effectivePointMeanKm','effectivePointMinKm','effectivePointMaxKm','capReached','uniqueDistances','calls']
with(H/'ENV_D_TABLE.csv').open('w',newline='')as out:
 w=csv.DictWriter(out,fieldnames=tableCols);w.writeheader()
 for r in m['rows']:
  q={k:r[k]for k in tableCols if k in r}
  for prefix,field in [('max','maxInterceptPoint'),('effective','effectiveInterceptPoint')]:
   for part in ['mean','min','max']:q[prefix+'Point'+part.title()+'Km']=(r[field]or{}).get(part+'Km')
  w.writerow(q)
with(H/'ENV_C_COMPARISON.csv').open('w',newline='')as out:
 fields=['weapon','altM','motionMps','historicalTarget','historicalGuidance','historicalMaxRangeKm','currentTarget','currentGuidance','currentFiveShotMaxRangeKm','currentEffectiveRangeKm','firstSeedAtHistoricalBoundary','firstSeedNextKm','note'];w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
 for q in f['historical']:
  current=next(r for r in m['rows']if not r.get('auxiliary')and r['weapon']==q['weapon']and r['altM']==q['altM']and r['targetSpeedMps']==q['targetSpeedMps']and not r.get('crossSpeedMps'))
  probes=q['firstSeedProbes'];text=lambda p:json.dumps({'rangeKm':p['rangeKm'],'outcome':p['result']['outcome'],'missionKills':p['result']['missionKills'],'reason':p['result']['reason'],'closestM':p['result']['closestM']},separators=(',',':'))
  w.writerow({'weapon':q['weapon'],'altM':q['altM'],'motionMps':q['targetSpeedMps'],'historicalTarget':q['historicalTarget'],'historicalGuidance':q['historicalGuidance'],'historicalMaxRangeKm':q['historicalMaxRangeKm'],'currentTarget':q['currentTarget'],'currentGuidance':q['currentGuidance'],'currentFiveShotMaxRangeKm':current['maxRangeKm'],'currentEffectiveRangeKm':current['effectiveRangeKm'],'firstSeedAtHistoricalBoundary':text(probes[0])if probes else'OUTSIDE_MINIMUM_RANGE','firstSeedNextKm':text(probes[1])if len(probes)>1 else'CAP_OR_OUTSIDE_MINIMUM_RANGE','note':'Target and guidance both changed; fullLoft C ER360/SM6 450, current240/260; historical values are not current measurements.'})
trajectoryFields=['id','weapon','targetLabel','initialRangeKm','targetInitialAltitudeM','targetSpeedMps','crossSpeedMps','timeS','distanceKm','xM','yM','altitudeM','speedMps','mach','targetXM','targetYM','targetAltitudeM','phase']
with gzip.open(O/'trajectories-10hz.csv.gz','wt',newline='')as out,(O/'phase-intervals.csv').open('w',newline='')as phaseOut:
 w=csv.DictWriter(out,fieldnames=trajectoryFields);w.writeheader();pw=csv.DictWriter(phaseOut,fieldnames=['id','weapon','phase','startS','endS']);pw.writeheader()
 for t in f['trajectories']:
  s=t['result'];c=t['condition']
  if not s:continue
  for p in s['samples']:
   row={k:p.get(k)for k in trajectoryFields};row.update(id=t['id'],weapon=c['weapon'],targetLabel=c['targetLabel'],initialRangeKm=c['rangeKm'],targetInitialAltitudeM=c['altM'],targetSpeedMps=c.get('targetSpeedMps',0),crossSpeedMps=c.get('crossSpeedMps',0));w.writerow(row)
  for phase in s['phases']:pw.writerow({'id':t['id'],'weapon':c['weapon'],**phase})
colors={30:'#2aa5aa',5000:'#df9425',15000:'#9061ba'}
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 fig,axes=plt.subplots(1,3,figsize=(15,4),sharey=True)
 for ax,title,mode in zip(axes,['Stationary target','Inbound 250 m/s','Crossing 250 m/s'],['static','inbound','cross']):
  for t in f['trajectories']:
   c=t['condition'];s=t['result'];motion='cross'if c.get('crossSpeedMps')else'inbound'if c.get('targetSpeedMps')else'static'
   if c['weapon']!=weapon or motion!=mode or not s:continue
   samples=s['samples'];ax.plot([p['distanceKm']for p in samples],[p['altitudeM']/1000 for p in samples],color=colors[c['altM']],alpha=.75,lw=1,label=f"{c['altM']/1000:g} km / launch {c['rangeKm']} km")
   ax.plot(s['terminal']['distanceKm'],s['terminal']['altitudeM']/1000,marker='o'if s['success']else'x',color=colors[c['altM']],ms=3)
  ax.set_title(title);ax.set_xlabel('Horizontal distance from launch (km)');ax.grid(alpha=.2)
  handles,labels=ax.get_legend_handles_labels()
  if handles:ax.legend(handles,labels,fontsize=5,ncol=2,loc='upper left')
  else:
   ax.text(.5,.5,'All requested ranges\noutside measured envelope',transform=ax.transAxes,ha='center',va='center',fontsize=10,color='#555555');ax.set_xlim(0,100 if mode=='cross'else 200)
 axes[0].set_ylabel('Altitude MSL (km)');fig.suptitle(weapon+' — native game ASM-target trajectories (SIM_TUNED)');fig.tight_layout();fig.savefig(P/(weapon+'-trajectories.svg'));fig.savefig(P/(weapon+'-trajectories.png'),dpi=140);plt.close(fig)
spreadWidths=sorted(q['max']-q['min']for q in spread);worstSpread=max(spread,key=lambda q:q['max']-q['min']);worstCell=next(q for q in m['rows']if q['cellId']==worstSpread['cellId'])
summary={'seedClosestSpreadMedianM':statistics.median(spreadWidths),'seedClosestSpreadP95M':spreadWidths[int(.95*(len(spreadWidths)-1))],'seedClosestSpreadWorst':{**worstSpread,'cellMaxRangeKm':worstCell['maxRangeKm']},'measurementShots':shotCount,'mainSeaImpactShots':mainSeaCount,'seaImpactShotsIncludingFollowupAndPilot':len(sea),'outcomes':dict(outcomes),'seedClosestSpreadMaxM':max(q['max']-q['min']for q in spread),'zeroEffectiveCells':sum(r['effectiveRangeKm']==0 for r in m['rows']if not r.get('auxiliary')),'mainCells':120,'auxiliaryCells':6,'trajectorySlots':len(f['trajectories']),'executedTrajectories':sum(bool(t['result'])for t in f['trajectories']),'unreachableTrajectorySlots':sum(not t['result']for t in f['trajectories']),'measurementElapsedS':m['elapsedS'],'followupElapsedS':f['elapsedS']}
(H/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=[f"**REG_K: 성공→실패 {reg['successToFailureCount']}건, 실패→성공 {reg['failureToSuccessCount']}건. 게임 코드·계수 수정 없음.**",'', '# REG_K + ENV_D', '', '기준 KAPPA_PIP_LOS_A / `kappa-pip-los-a`의 `80b6514`. 비교 기준 RANGE_RECOVERY_A. 이 문서의 모든 사거리는 SIM_TUNED 게임 엔진 계산값이며 실제 무기 성능이 아니다.', '', '## 1. 전체 회귀 및 이전 기준과의 차이', '', '|검사|RANGE_RECOVERY_A|KAPPA_PIP_LOS_A|','|---|---:|---:|']
for key,label in [('domain','도메인15묶음'),('ui','UI'),('termination','종료기'),('observed','자연탐지→LOCK→정식VLS→fixed tick→실제WebGL8발')]:
 a,b=reg['acceptance']['recovery'][key],reg['acceptance']['current'][key];lines.append(f"|{label}|{a['count']} / {'PASS'if a['pass']else'FAIL'}|{b['count']} / {'PASS'if b['pass']else'FAIL'}|")
lines+=['','종료기 표의16은 검수 항목 수다. 실제 사격은 정상 ON/OFF240발, 대체 지원36발, RF 소실·재획득·미획득, 배터리8발, 정식 VLS4발을 포함한다. 원래 자연 탐지 검사의8발을 보존하고, ON/OFF 양쪽 모두 실제 WebGL 프레임을 확인하는8발도 별도로 실행했다. 추가 native validation60조건과 전체 사격 조건은 원시 evidence/reg-k에 보존했다.','',f"무표적120초 truth/RNG hash 동일: {reg['idleTruthHashIdentical']}. 사격 비교 {reg['comparedShots']}건 중 결과·최근접·비행시간 등 차이 {len(reg['allOutcomeAndGeometryChanges'])}건. 전체 조건과 전후 값은 [REG_K_ALL_CHANGES.csv](REG_K_ALL_CHANGES.csv), 상세는 [REG_K_RESULTS.json](REG_K_RESULTS.json).",'']
for label,key in [('성공→실패','successToFailure'),('실패→성공','failureToSuccess')]:
 lines.append('### '+label)
 if not reg[key]:lines.append('없음.')
 for r in reg[key]:lines.append('- '+json.dumps({'suite':r['suite'],'condition':r['condition'],'before':r['before'],'after':r['after']},ensure_ascii=False))
lines+=['','전투120초(SM-6 100km/5km/접근250/seed12002)는 hash가 달라졌다. 별도 종료까지 관찰한 결과는 다음과 같다.','', '|버전|120초 시 최근접(m)|최종 종료 사유|발사 후 종료(s)|','|---|---:|---|---:|']
for r in reg['combatFollowup']['records']:
 q=r['final']['afterAction']['missile'];lines.append(f"|{r['version']}|{r['at120']['closestM']:.3f}|{q['reason']}|{q['lifeS']:.6f}|")
lines+=['','최종 targetAlive와 단계 로그는 REG_K_RESULTS에 보존했다. 이 사례의 결과 변화도 교정하지 않았다. 기존 종료기 수집기의 첫 임시 호출은 validation 파일이 아직 준비되지 않아 실패했고, 원래 검사를 변경하지 않고 파일 준비 뒤 재실행했다. 제한 소켓 환경에서의 브라우저 시동 실패는 별도 infra 로그에 구분했으며 게임 실패에 합산하지 않았다.', '', '## 2. 실행 비용', '', '초기 v0 진단은 fixed-tick 외부에서 부착되는 WIP112 계통 손상 observer가 빠져1칸 완료 시점에 중단·무효화했다. 그 결과는 evidence/diagnostic-v0-incomplete-hooks에 보존하고 최종 표에서 제외했다. 이후 native observer + 원문 ASM damage-prefix로 다시 동등성을 검증하고 실행 전 비용도 재측정했다. 정식 전수는 이 보정본1회다.', '',f"실행 전 보고: {cost['expectedShotsTotal']:,}발, {cost['expectedHours']:.2f}시간(4코어, 실측80발 기반,25%여유). 축소안 예상 {cost['reducedExpectedShots']:,}발/{cost['reducedExpectedHours']:.2f}시간. 예상6시간 이내여서 축소안을 사용하지 않았다.",f"실측: 본 측정 {m['calls']:,}발/{m['elapsedS']/3600:.3f}시간, 경계·궤적·과거 경계 확인 {f['calls']:,}발/{f['elapsedS']/3600:.3f}시간. 전체 스윕은1회뿐이다. 모든 시드에서 native 비행을 독립 실행했으며 Pk만 재추첨하는 궤적 재사용은 하지 않았다.", '', '## 3. ASM 기준 사거리표', '', '각 칸: **바깥 / 안쪽 km · 요격점 평균(바깥 / 안쪽) km**. 요격점은 발사 원점에서 native SAM 효과 발생 위치까지의 수평 거리이며, 같은 고정틱의 표적 위치 거리도 별도 기록한다. 바깥 요격점 평균은 효과 발생 발, 안쪽 평균은 KILL/STRUCT_FAIL 발만 사용한다. 경계 JSON에는 두 집계와5발 원본을 함께 기록했다. 바깥은5발 중1발 이상 효과, 안쪽은5km부터 모든5km 지점에서3발 이상KILL/STRUCT_FAIL. 0km는 이 정의를 만족하는 연속 구간이 없다는 뜻이다. 500km는 측정 상한이다. 모든 경계의5발 결과, 요격점 평균·최소·최대는 [ENV_D_TABLE.csv](ENV_D_TABLE.csv)와 [ENVELOPE_TABLE_D.json](ENVELOPE_TABLE_D.json).']
motions=['STATIONARY','INBOUND_250','INBOUND_680','OUTBOUND_250','CROSS_250']
lines+=['',f"안쪽 범위가 0인 기본 표 칸은 {summary['zeroEffectiveCells']}개다. 첫 5km 지점에서 기준을 못 채우면 더 먼 거리에서 성공하더라도 안쪽 범위는 0이다. 500km 상한 도달 칸은 501km를 추정하거나 사격하지 않았고 다음 경계는 없음으로 기록했다."]
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 lines+=['','### '+weapon,'','|고도(m)|정지|접근250|접근680|이탈250|횡단250|','|---:|---:|---:|---:|---:|---:|']
 for alt in [30,1000,5000,10000,15000,20000]:
  values=[]
  for motion in motions:
   q=next(q for q in m['rows']if not q.get('auxiliary')and q['weapon']==weapon and q['altM']==alt and q['motion']==motion)
   def point(v):return f"{v['meanKm']:.1f}"if v else'—'
   values.append(f"{q['maxRangeKm']}/{q['effectiveRangeKm']} · {point(q['maxInterceptPoint'])}/{point(q['effectiveInterceptPoint'])}")
  lines.append('|'+str(alt)+'|'+'|'.join(values)+'|')
 lines+=['',f'![{weapon} native trajectories](plots/{weapon}-trajectories.png)','원 = native 효과 발생, × = 효과 없음. 색은 표적 고도이며 각 곡선의 발사 거리는 범례에 표시했다.']
lines+=['','## 4. 시드와 다른 ASM 라벨', '', '기준 라벨 Kh-35U. ASM_PROFILES의 다른 라벨은 Kh-32 하나이며 요청한6칸을 동일 절차로 측정했다. 시드 첫 값은 global simRandom(Pk/손상), 두 번째 값은 native INS·신관 파생 스트림의 SIM_SEED_BASE와 scenario seed에 준다. SAM 항법은 BATTLESPACE_SEED만 바꿔서는 달라지지 않으므로 두 스트림을 분리해 직접 공급했다.', '', '|세트|게임 RNG|항법 파생 seed|','|---:|---:|---:|']
for i,s in enumerate(m['seeds'],1):lines.append(f"|{i}|{s['rngSeed']}|{s['navigationSeed']}|")
lines+=['',f"5발 CPA 차이의 중앙값은 {summary['seedClosestSpreadMedianM']:.3f}m, 95백분위는 {summary['seedClosestSpreadP95M']:.3f}m, 최대는 {summary['seedClosestSpreadMaxM']:.3f}m이다. 최대 차이 조건은 {worstSpread['cellId']} / {worstSpread['rangeKm']}km이며, 그 칸의 바깥 사거리 {worstCell['maxRangeKm']}km보다 먼 실패 구간이다. 모든 거리별 범위는 results/seed-closest-spread.csv. 예비80발에서도 궤적과 SEA_IMPACT 발생 자체가 달라져 Pk 난수 차이만 있는 조건으로 취급하지 않았다.", '', '|기종|고도|운동|Kh-35U 바깥/안쪽|Kh-32 바깥/안쪽|','|---|---:|---|---:|---:|']
for r in m['rows']:
 if not r.get('auxiliary'):continue
 b=next(q for q in m['rows']if not q.get('auxiliary')and q['weapon']==r['weapon']and q['altM']==r['altM']and q['motion']==r['motion'])
 lines.append(f"|{r['weapon']}|{r['altM']}|{r['motion']}|{b['maxRangeKm']}/{b['effectiveRangeKm']}|{r['maxRangeKm']}/{r['effectiveRangeKm']}|")
lines+=['', '## 5. 해면 충돌 목록', '', f"본 스윕 SEA_IMPACT {mainSeaCount:,}발, 경계·궤적 반복·과거 경계 확인·비용 예비 사격을 포함하면 {len(sea):,}발. origin 열로 출처와 반복을 구분한다. [전체 CSV(gzip)](results/SEA_IMPACT.csv.gz)는 기종·표적 고도·운동·거리·시드·충돌 속도·CPA·하강 시작 시각/모드/단계를 포함한다. 원시 native 결과는 results/cells/*.json.gz. 계수나 판정을 수정하지 않았다.", '', '## 6. ENV_C 과거 결과 및 설계값', '', 'ENV_C는 항공기 점 표적 + 이전 수평 종말 방향 계산(HISTORICAL)이고, ENV_D는 실제 ASM 피해 판정 + KAPPA_PIP_LOS_A이다. 표적과 유도 코드가 둘 다 다르다. ENV_C의 fullLoftKm도 ER360/SM-6 450인 반면 현재는 앞선 RECOVERY_A에서 정한240/260을 유지한다. 또한 이번 seed1 항법 파생 seed는2047861954이며, 옛 ENV_C의 실제 SAM 파생 SIM_SEED_BASE1831565813과 다르다(옛 BATTLESPACE_SEED와 구분). 동일 난수의 인과 A/B가 아니므로 사거리 증감을 한 원인으로 단정하지 않는다. 과거96칸 각각의 마지막 성공/다음1km 위치에서 현 코드의 seed1 단일 발도 확인했다. results/followup.json.gz의 historical에 병렬 기록했다. 횡단24칸은 ENV_C 대응 값이 없다.', '', '발사 시 표적 거리 기준이다. 접근 표적의 큰 초기 거리와 실제 비행/요격점 거리를 구분한다.', '', '|기종|설계값(km)|바깥 링 도달|그중 정지 조건|','|---|---:|---:|---:|']
for weapon,goal in [('SM2ER',360),('SM6',450)]:
 count=sum(r['maxRangeKm']>=goal for r in m['rows']if not r.get('auxiliary')and r['weapon']==weapon);stationary=sum(r['maxRangeKm']>=goal for r in m['rows']if not r.get('auxiliary')and r['weapon']==weapon and r['motion']=='STATIONARY');lines.append(f'|{weapon}|{goal}|{count}/30|{stationary}/6|')
lines+=['','## 7. 결정성·동일 경로·내장 검증', '', f"경계 {len(f['boundaries'])}거리×5발과 궤적30개 재검사: {'PASS'if f['pass']else'FAIL'}. 궤적 추출 RNG seed {f['selectionSeed']}, 선택id는 evidence/determinism.json. 전체 측정2회 실행은 하지 않았다.",f"궤적 조건은 기존120 + 지정 횡단4×3×3=36으로 총{len(f['trajectories'])}칸을 보존했다. 실제 사격 {summary['executedTrajectories']}개, 범위 밖 {summary['unreachableTrajectorySlots']}칸은 도달 불가로 표시했다. 10Hz CSV와 단계 CSV는 results/ 아래에 있다.", '결과는 SAM 종료/표적 퇴역 시점과 같은 fixed tick의 ASM 손상 처리를 기록했다. WIP112 AttachObservers → native SAM → 원문 ASM 손상 prefix 순서를 사용한다. ASM 비행 AI 앞에서만 경계를 끊고, 계통 파편 손상·탄두 상태·동일 틱 구조파괴는 native 경로로 처리한다. 별도 손상 임계값은 만들지 않는다. source prefix와 원 함수 SHA는 diagnostic/native-asm-prefix-proof.json에 있다. 실제 게임/독립 진단6조건(ASM·횡단 포함): 궤적 및 native 피해 결과 오차0. 진단 전후 live world/RNG/tick 변화0. 자세한 조건은 evidence/path.json.', f"최종 ENV_D HTML의 120초 truth hash는 Kappa 기준과 무표적 {delivery['checks']['idle120UnchangedFromKappa']}, 전투 {delivery['checks']['combat120UnchangedFromKappa']}이다. DDG/CG status 일치 {delivery['checks']['statusMatches']}/{delivery['checks']['cgStatusMatches']}; API의 live world/RNG/tick 변화도 0이다.", f"내장 ENVELOPE_TABLE_D 120칸. native source/profile fingerprint `{build['profileHash']}`. 기존 main JS는 새 데이터·읽기 전용 상태 API 블록을 제거하면 byte 동일이며 실제 게임 함수 변경0. 지도·발사·AI와 연결하지 않았다. 기존 ENV_KAPPA_A의 빈 AIR용 표와 ENV_C 과거 데이터는 그대로 보존했다.", '', '수정된 HTML, 별도 실행 ZIP, 별도 리포트 ZIP을 시험 브랜치에 제공한다. 기존 브랜치/main 병합, PR, Actions 실행 없음. 실제 측정 상한을 넘는 성능이나 다른 seed 분포의 보장으로 해석하지 않는다.']
(H/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))
