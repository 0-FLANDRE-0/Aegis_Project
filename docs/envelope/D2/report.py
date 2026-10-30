"""Summarize native results without changing any game model or test outcome."""
from pathlib import Path
import collections,csv,gzip,json,os,statistics
os.environ.setdefault('MPLCONFIGDIR','/tmp/aegis-env-d2-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;O=H/'results';P=H/'plots';P.mkdir(exist_ok=True)
load=lambda p:json.loads(p.read_text())
m=load(O/'measurement.json');old=load(H.parent/'D/ENVELOPE_TABLE_D.json');f=json.loads(gzip.decompress((O/'followup.json.gz').read_bytes()));cost=load(H/'COST_ESTIMATE.json');build=load(H/'build.json');proof=load(H/'evidence/path.json');delivery=load(H/'evidence/delivery.json')
def point(q,flag='success'):
 a=[s['interceptPointKm']for s in q['shots']if s[flag]]if q else[]
 return {'meanKm':statistics.fmean(a),'minKm':min(a),'maxKm':max(a)}if a else None
def writecsv(file,fields,rows):
 op=gzip.open(file,'wt',newline='')if file.suffix=='.gz'else file.open('w',newline='')
 with op as out:
  w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
for r in m['rows']:
 r['effectiveInterceptPoint']=point(r['effectiveBoundary'],'lethal')
def shotrow(s,cell,origin):
 d=s.get('descentStart')or{}
 return {**{k:s.get(k)for k in ['weapon','targetLabel','rangeKm','altM','targetSpeedMps','crossSpeedMps','rngSeed','navigationSeed','outcome','reason','success','lethal','closestM','fuzeMissM','flightTimeS','apogeeM','interceptPointKm','targetInterceptPointKm']},'origin':origin,'cellId':cell,'missionKills':';'.join(s['missionKills']),'terminalSpeedMps':s['terminal']['speedMps'],'descentStartS':d.get('timeS'),'descentMode':d.get('mode'),'descentStage':d.get('stage')}
fields=['origin','cellId','weapon','targetLabel','rangeKm','altM','targetSpeedMps','crossSpeedMps','rngSeed','navigationSeed','outcome','reason','success','lethal','closestM','fuzeMissM','flightTimeS','apogeeM','interceptPointKm','targetInterceptPointKm','missionKills','terminalSpeedMps','descentStartS','descentMode','descentStage']
sea=[];outcomes=collections.Counter();spreads=[];count=0
with gzip.open(O/'all-measurement-shots.csv.gz','wt',newline='')as out:
 w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader()
 for p in sorted((O/'cells').glob('*.json.gz')):
  j=json.loads(gzip.decompress(p.read_bytes()))
  for d in j['distances']:
   spreads.append({'cellId':j['cell']['cellId'],'rangeKm':d['rangeKm'],**d['closestRangeM']})
   for s in d['shots']:
    row=shotrow(s,j['cell']['cellId'],'FULL_SWEEP');w.writerow(row);count+=1;outcomes[s['outcome']if s['outcome']!='FAILURE'else s['reason']]+=1
    if s['reason']=='SEA_IMPACT':sea.append(row)
assert count==m['calls'];mainSea=len(sea)
for group,origin in [('boundaries','BOUNDARY_REPEAT'),('trajectories','TRAJECTORY'),('replays','TRAJECTORY_REPEAT')]:
 for q in f[group]:
  shots=q.get('shots')or([q['result']]if q.get('result')else[])
  for s in shots:
   if s['reason']=='SEA_IMPACT':sea.append(shotrow(s,q.get('cellId',q.get('id')),origin))
writecsv(O/'SEA_IMPACT.csv.gz',fields,sea);writecsv(O/'seed-closest-spread.csv',['cellId','rangeKm','min','max'],spreads)
tc=['cellId','weapon','targetLabel','altM','motion','maxRangeKm','effectiveRangeKm','maxPointMeanKm','maxPointMinKm','maxPointMaxKm','effectivePointMeanKm','effectivePointMinKm','effectivePointMaxKm','capReached']
table=[];comparison=[];oldBy={r['cellId']:r for r in old['rows']}
for r in m['rows']:
 t={k:r.get(k)for k in tc}
 for prefix,key in [('max','maxInterceptPoint'),('effective','effectiveInterceptPoint')]:
  for stat in ['mean','min','max']:t[prefix+'Point'+stat.title()+'Km']=(r[key]or{}).get(stat+'Km')
 table.append(t)
 if r['cellId']in oldBy:
  b=oldBy[r['cellId']];comparison.append({'cellId':r['cellId'],'weapon':r['weapon'],'altM':r['altM'],'motion':r['motion'],'historicalMaxKm':b['maxRangeKm'],'currentMaxKm':r['maxRangeKm'],'deltaMaxKm':r['maxRangeKm']-b['maxRangeKm'],'historicalEffectiveKm':b['effectiveRangeKm'],'currentEffectiveKm':r['effectiveRangeKm'],'deltaEffectiveKm':r['effectiveRangeKm']-b['effectiveRangeKm'],'historicalRevision':'KAPPA_PIP_LOS_A','currentRevision':'NEAR_VERTICAL_PATH_FIX_A'})
writecsv(H/'ENV_D_TABLE.csv',tc,table);writecsv(H/'ENV_D_BEFORE_AFTER.csv',list(comparison[0]),comparison)
breaks=[]
for r in m['rows']:
 if r.get('auxiliary')or not r['breakPoint']:continue
 for i,s in enumerate(r['breakPoint']['shots'],1):breaks.append({'cellId':r['cellId'],'rangeKm':r['breakPoint']['rangeKm'],'seedIndex':i,'outcome':s['outcome'],'reason':s['reason'],'closestM':s['closestM'],'fuzeMissM':s['fuzeMissM'],'flightTimeS':s['flightTimeS']})
writecsv(H/'INNER_BREAKS.csv',list(breaks[0]),breaks)
historical=[{'weapon':q['weapon'],'altM':q['altM'],'targetSpeedMps':q['targetSpeedMps'],'historicalMaxRangeKm':q['historicalMaxRangeKm'],'currentMaxRangeKm':next(r['maxRangeKm']for r in m['rows']if not r.get('auxiliary')and r['weapon']==q['weapon']and r['altM']==q['altM']and r['targetSpeedMps']==q['targetSpeedMps']and not r.get('crossSpeedMps')),'historicalTarget':'AIR_POINT','historicalGuidance':'PRE_KAPPA_PIP_LOS','currentTarget':'Kh-35U_ASM','currentGuidance':'NEAR_VERTICAL_PATH_FIX_A'}for q in f['historical']]
for h,q in zip(historical,f['historical']):
 h['firstSeedAtHistoricalBoundary']=json.dumps(q['firstSeedProbes'][0],separators=(',',':'))if q['firstSeedProbes']else'OUTSIDE_MINIMUM_RANGE'
 h['firstSeedAtNextKm']=json.dumps(q['firstSeedProbes'][1],separators=(',',':'))if len(q['firstSeedProbes'])>1 else'CAP_OR_OUTSIDE_MINIMUM_RANGE'
writecsv(H/'ENV_C_HISTORICAL_COMPARISON.csv',list(historical[0]),historical)
tr=[];ph=[]
for t in f['trajectories']:
 if not t['result']:continue
 c=t['condition'];s=t['result'];meta={'id':t['id'],'weapon':c['weapon'],'targetLabel':c['targetLabel'],'initialRangeKm':c['rangeKm'],'targetInitialAltitudeM':c['altM'],'targetSpeedMps':c.get('targetSpeedMps',0),'crossSpeedMps':c.get('crossSpeedMps',0)}
 tr.extend({**meta,**p}for p in s['samples']);ph.extend({'id':t['id'],'weapon':c['weapon'],**p}for p in s['phases'])
writecsv(O/'trajectories-10hz.csv.gz',list(tr[0]),tr);writecsv(O/'phase-intervals.csv',['id','weapon','phase','startS','endS'],ph)
colors={30:'#2aa5aa',5000:'#df9425',15000:'#9061ba'}
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 fig,axes=plt.subplots(1,3,figsize=(15,4),sharey=True)
 for ax,title,mode in zip(axes,['Stationary','Inbound 250 m/s','Crossing 250 m/s'],['static','inbound','cross']):
  for t in f['trajectories']:
   c=t['condition'];s=t['result'];kind='cross'if c.get('crossSpeedMps')else'inbound'if c.get('targetSpeedMps')else'static'
   if c['weapon']!=weapon or kind!=mode or not s:continue
   samples=s['samples'];ax.plot([p['distanceKm']for p in samples],[p['altitudeM']/1000 for p in samples],color=colors[c['altM']],alpha=.7,lw=1,label=f"{c['altM']/1000:g}km / {c['rangeKm']}km")
   ax.plot(s['terminal']['distanceKm'],s['terminal']['altitudeM']/1000,marker='o'if s['success']else'x',color=colors[c['altM']],ms=3)
  ax.set_title(title);ax.set_xlabel('Horizontal distance from launch (km)');ax.grid(alpha=.2)
  if ax.lines:ax.legend(fontsize=5,ncol=2)
  else:ax.text(.5,.5,'Outside measured envelope',transform=ax.transAxes,ha='center')
 axes[0].set_ylabel('Altitude MSL (km)');fig.suptitle(weapon+' — native game engine, SIM_TUNED');fig.tight_layout();fig.savefig(P/(weapon+'-trajectories.svg'));fig.savefig(P/(weapon+'-trajectories.png'),dpi=140);plt.close(fig)
for svg in P.glob('*.svg'):
 svg.write_text('\n'.join(line.rstrip()for line in svg.read_text().splitlines())+'\n')
widths=sorted(q['max']-q['min']for q in spreads)
summary={'measurementShots':count,'measurementElapsedS':m['elapsedS'],'followupShots':f['calls'],'followupElapsedS':f['elapsedS'],'mainSeaImpacts':mainSea,'zeroEffectiveCells':sum(r['effectiveRangeKm']==0 for r in m['rows']if not r.get('auxiliary')),'outcomes':dict(outcomes),'seedSpreadMedianM':statistics.median(widths),'seedSpreadP95M':widths[int(.95*(len(widths)-1))],'seedSpreadMaxM':max(widths),'trajectorySlots':len(f['trajectories']),'executedTrajectories':sum(bool(t['result'])for t in f['trajectories']),'historicalComparedCells':len(comparison),'changedMaxCells':sum(q['deltaMaxKm']!=0 for q in comparison),'changedEffectiveCells':sum(q['deltaEffectiveKm']!=0 for q in comparison)}
(H/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# ENV_D 재측정 A','', '기준: near-vertical-path-fix-a / 38a4f97527b48027fa64f0673cea14a9c83c116d. 모든 수치는 SIM_TUNED 게임 엔진 계산값이다. 제품 게임 함수·계수 변경은 0이며, 최신 HTML의 ENV_D 데이터/상태 API 블록만 교체했다.','',f"실행 전 예상 {cost['expectedShots']:,}발 / {cost['expectedHours']:.2f}시간(4 workers, 25% 여유). 실측 본 측정 {count:,}발 / {m['elapsedS']/3600:.3f}시간, 후속 {f['calls']:,}발 / {f['elapsedS']/3600:.3f}시간. 축소안 미사용. 전체 스윕 1회. 시드 간 비행 재사용 없음.", '', '80발 예비 사격이 전수 검색의 긴 실패 비행 비중을 적게 반영해 실행 시간을 과소 추정했다. 최초 비용 예측은 수정 없이 보존했으며 ACTUAL_COST.json에 실제 비용을 별도 기록했다.', '', 'Kh-35U, 고도 30/1000/5000/10000/15000/20000m, 정지/접근250/접근680/이탈250/횡단250m/s. 고정 5시드는 아래와 같다.','', '|세트|게임 RNG|항법 seed|','|---:|---:|---:|']
for i,s in enumerate(m['seeds'],1):lines.append(f"|{i}|{s['rngSeed']}|{s['navigationSeed']}|")
lines+=['', '각 칸: 바깥/안쪽 km · 요격점 평균(바깥/안쪽) km. 바깥은 5발 중 1발 이상 native 효과, 안쪽은 5km부터 연속 5km grid에서 3발 이상 KILL/STRUCT_FAIL. 0은 첫 연속 구간 없음, 500은 측정 상한. 경계 5발·요격점 최소/최대는 JSON/CSV에 포함.','']
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 lines+=['## '+weapon,'','|고도(m)|정지|접근250|접근680|이탈250|횡단250|','|---:|---:|---:|---:|---:|---:|']
 for alt in [30,1000,5000,10000,15000,20000]:
  vals=[]
  for motion in ['STATIONARY','INBOUND_250','INBOUND_680','OUTBOUND_250','CROSS_250']:
   r=next(r for r in m['rows']if not r.get('auxiliary')and r['weapon']==weapon and r['altM']==alt and r['motion']==motion);fmt=lambda p:f"{p['meanKm']:.1f}"if p else'—';vals.append(f"{r['maxRangeKm']}/{r['effectiveRangeKm']} · {fmt(r['maxInterceptPoint'])}/{fmt(r['effectiveInterceptPoint'])}")
  lines.append('|'+str(alt)+'|'+'|'.join(vals)+'|')
 lines+=['',f'![{weapon}](plots/{weapon}-trajectories.png)','']
lines+=['## 이전 ENV_D 비교','',f"과거 KAPPA_PIP_LOS_A 기준과 바깥 거리 {summary['changedMaxCells']}/120칸, 안쪽 거리 {summary['changedEffectiveCells']}/120칸이 달라졌다. ENV_D_BEFORE_AFTER.csv 전체 비교를 제공한다. 여러 누적 수정이 함께 반영됐으므로 거리 차이를 한 수정의 효과로 단정하지 않는다.",f"안쪽 0인 칸 {summary['zeroEffectiveCells']}개(과거 37개).",'', '|기종|고도|운동|과거 바깥/안쪽|현재 바깥/안쪽|','|---|---:|---|---:|---:|']
for q in comparison:
 if q['deltaMaxKm']or q['deltaEffectiveKm']:lines.append(f"|{q['weapon']}|{q['altM']}|{q['motion']}|{q['historicalMaxKm']}/{q['historicalEffectiveKm']}|{q['currentMaxKm']}/{q['currentEffectiveKm']}|")
lines+=['','## 안쪽 범위가 감소한 조건','', '아래는 연속 구간 기준이 줄어든 칸이다. 중간 실패점 뒤의 먼 거리에서 다시 성공하더라도 안쪽에 연결하지 않았다. 각 실패점의 5발 로그는 INNER_BREAKS.csv와 원시 JSON에 있다. 계수 보정이나 실패 숨김은 하지 않았다.','', '|칸|과거/현재 안쪽 km|끊긴 거리 km|KILL/STRUCT_FAIL|5발 종료 사유|','|---|---:|---:|---:|---|']
for q in comparison:
 if q['deltaEffectiveKm']>=0:continue
 r=next(r for r in m['rows']if r['cellId']==q['cellId']);b=r['breakPoint'];reasons=dict(collections.Counter(s['reason']for s in b['shots']))
 lines.append(f"|{q['cellId']}|{q['historicalEffectiveKm']}/{q['currentEffectiveKm']}|{b['rangeKm']}|{b['lethalCount']}/5|{json.dumps(reasons,separators=(',',':'))}|")
lines+=['','## 보조 ASM·시드 차이','', '|기종|고도|운동|Kh-35U 바깥/안쪽|Kh-32 바깥/안쪽|','|---|---:|---|---:|---:|']
for r in m['rows']:
 if r.get('auxiliary'):
  b=next(q for q in m['rows']if not q.get('auxiliary')and q['weapon']==r['weapon']and q['altM']==r['altM']and q['motion']==r['motion']);lines.append(f"|{r['weapon']}|{r['altM']}|{r['motion']}|{b['maxRangeKm']}/{b['effectiveRangeKm']}|{r['maxRangeKm']}/{r['effectiveRangeKm']}|")
lines+=['',f"5시드 CPA 범위: 중앙값 {summary['seedSpreadMedianM']:.3f}m, P95 {summary['seedSpreadP95M']:.3f}m, 최대 {summary['seedSpreadMaxM']:.3f}m. 항법 시드가 비행 이력에 영향을 주므로 각 발을 독립 실행했다.",'','## 해면 충돌·과거 ENV_C·설계값','',f"본 측정 SEA_IMPACT {mainSea:,}건. results/SEA_IMPACT.csv.gz에 조건·시드·충돌 속도·CPA·하강 시점/단계를 기록했다. ENV_C 비교는 HISTORICAL 항공기 점 표적/구 유도 코드이며 현재 ASM 결과와 직접 동일시하지 않는다.",'','|기종|게임 설계값|바깥 도달 칸|정지 도달 칸|','|---|---:|---:|---:|']
for weapon,goal in [('SM2ER',360),('SM6',450)]:lines.append(f"|{weapon}|{goal}km|{sum(r['maxRangeKm']>=goal for r in m['rows']if not r.get('auxiliary')and r['weapon']==weapon)}/30|{sum(r['maxRangeKm']>=goal for r in m['rows']if not r.get('auxiliary')and r['weapon']==weapon and r['motion']=='STATIONARY')}/6|")
lines+=['','## 검증','',f"실제 브라우저 함수 281개 해시 일치. 실제 함수/독립 진단 6조건(ASM·횡단 포함) 반환값·궤적 오차 0. 진단 전후 live world/RNG/tick 변화 0. 경계 {len(f['boundaries'])}거리×5발, 궤적 고정 무작위30개 반복: {'PASS'if f['pass']else'FAIL'}; 선택 seed {f['selectionSeed']}.",f"궤적은 기존 120 + 횡단 4×3×3=36, 총 {len(f['trajectories'])}슬롯을 유지했다. 실제 실행 {summary['executedTrajectories']}, 나머지는 측정 바깥으로 표시했다. 10Hz CSV·단계 CSV·기종별 PNG/SVG 제공.",f"최종 내장표 120칸. status 일치 DDG/CG: {delivery['checks']['DDG.statusMatch']}/{delivery['checks']['CG.statusMatch']}. 120초 무표적/전투 truth hash 동일: {delivery['checks']['idle120Identical']}/{delivery['checks']['combat120Identical']}. 제품 게임 코드/계수 변경 0. 직전 단계 회귀는 414/420(기존 6 실패), UI88/88, 종료기300발 상태 변화0이며 이번에는 데이터 블록 변경만 검증했다.", '', 'main 병합·release/tag 생성 없음. 지도·AI·발사 판정에 표를 연결하지 않았다.']
(H/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))
