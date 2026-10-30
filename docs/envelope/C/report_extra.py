"""Full initial/intercept-distance tables, honest capped comparisons and observed loft effects."""
import argparse,collections,csv,gzip,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='ENV_C_EXTRA'
import matplotlib.pyplot as plt
C=Path(__file__).resolve().parent;R=C.parents[2];H=R/'docs/missile/range/A'
def read(p):
 p=Path(p)
 if not p.exists():p=p.with_suffix(p.suffix+'.gz')
 return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
p=argparse.ArgumentParser();p.add_argument('results',type=Path);a=p.parse_args();n=read(a.results);b=read(C.parent/'B/results/results.json');old=read(C.parent/'A/ENVELOPE_TABLE_A.json');proof=read(C/'evidence/verification/results-verification.json');s0=read(C/'stage0/verification.json');s1=read(C/'stage1/verification.json');O=C/'results';assert proof['pass']and s0['pass']and s1['pass']
key=lambda q:(q['weapon'],q['altM'],q['targetSpeedMps']);bm={key(q):q for q in b['table']};nm={key(q):q for q in n['table']};am={key(q):q for q in old['rows']};s0m={(q['weapon'],q['altM']):q for q in s0['rows']}
comparison=[]
for q in n['table']:
 x=bm[key(q)];actual=s0m.get((q['weapon'],q['altM'])) if q['targetSpeedMps']==0 else None
 baseline=actual['maxRangeKm'] if actual else x['maxRangeKm'];baselineCap=False if actual else x['upperCapReached']
 oldPoint=x['lastSuccess']['result']['terminal']['distanceKm'] if x['lastSuccess'] else None
 comparison.append({k:q[k]for k in ['weapon','altM','targetSpeedMps']}|{'envBInitialKm':x['maxRangeKm'],'envBCapped300':x['upperCapReached'],'baseline500InitialKm':actual['maxRangeKm'] if actual else None,'newInitialKm':q['maxRangeKm'],'newCapped500':q['upperCapReached'],'initialDeltaKm':q['maxRangeKm']-baseline if not(baselineCap or q['upperCapReached']) else None,'envBInterceptPointKm':oldPoint,'newInterceptPointKm':q['interceptPointKm'],'firstFailureKm':q['firstFailure']['rangeKm'] if q['firstFailure'] else None,'firstFailureReason':q['firstFailure']['result']['reason'] if q['firstFailure'] else 'MEASUREMENT_CAP_REACHED'})
with(O/'comparison-env-b-c.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
name={'SM2':'SM-2MR','SM2ER':'SM-2ER','SM6':'SM-6','ESSM':'ESSM Block 2'}
fmt=lambda q:('≥' if q['upperCapReached'] else '')+str(q['maxRangeKm'])
lines=['# ENV_C — RANGE_A 전체 재측정','',f"프로파일/진단 경계 SHA-256: `{n['profileHash']}`",'','현재 가상 게임 엔진의 SIM_TUNED 모델을 측정했다. 실물 성능과 비교하지 않는다. 정지 해면 발사함·수직 VLS, 오차 없는 지속 유도 정보, private1/60초/RNG 조건이다. 실제 게임 함수 그대로이며 결과는 지도/AI/발사 권한에 연결하지 않았다.','',f"96조합 +120궤적을 독립적으로2회 실행. 각각 {n['calls']:,}사격, 원시 {proof['records'][0]['bytes']:,}bytes가 비트 동일하다.",f"원시 SHA-256 `{proof['records'][0]['sha256']}`.",f"벽시계 {proof['records'][0]['elapsedMs']/1000:.3f}s / {proof['records'][1]['elapsedMs']/1000:.3f}s. 각4workers, CPU4core quota, 브라우저 회귀 우선 일시 중단/재개 및 두 실행 중첩을 포함한다. 전용 CPU 벤치마크가 아니다.",'','## 거리 정의','', '- 최초거리: 발사 시 표적과 발사점의 수평 거리.','- 요격점거리: 그 최대 최초거리 성공 사격에서 실제 신관/파괴 시점 미사일 위치와 발사점 사이 수평 거리. 별개의 최댓값을 다시 탐색한 표가 아니다.','- `≥500`은 측정 상한에서 성공했다는 하한이다. ENV_B `≥300`도 실제 최대라고 해석하지 않는다.','- 비단조 구간을 놓치지 않도록 coarse/이분 탐색 뒤 더 먼 모든 정수km를 검사했다. 표 안쪽 모든 거리의 명중을 보장하지 않는다.','']
lines+=['## 설계 목표 대비 — 측정한 정지 표적6고도 중 최대','','| 기종 | 목표 | 최대 명중 최초거리 | 해당 표적고도 | 부족분 | 최대기록의 목표 도달 |','|---|---:|---:|---:|---:|---|']
goalSummary=[]
for weapon,target in [('SM2ER',360),('SM6',450)]:
 best=max((q for q in n['table']if q['weapon']==weapon and q['targetSpeedMps']==0),key=lambda q:q['maxRangeKm']);met=best['maxRangeKm']>=target;goalSummary.append({'weapon':weapon,'targetKm':target,'measuredMaxKm':best['maxRangeKm'],'altM':best['altM'],'upperCapReached':best['upperCapReached'],'deficitKm':max(0,target-best['maxRangeKm']),'maximumRecordMeetsGoal':met})
 lines.append(f"| {name[weapon]} | {target}km | {fmt(best)}km | {best['altM']/1000:g}km | {max(0,target-best['maxRangeKm'])}km | {'예' if met else '아니오'} |")
lines+=['','명중 구간이 비연속일 수 있으므로 최대기록 도달 여부와 목표거리 자체 사격의 성공 여부는 구분한다. 미측정 고도·사거리는 추정하지 않는다.','']
(O/'design-goal-summary.json').write_text(json.dumps(goalSummary,indent=2))
for field,title in [('maxRangeKm','최대 발사 시 표적 거리'),('interceptPointKm','같은 최대 사격의 실제 요격 지점 거리')]:
 lines+=['## '+title+' — km','']
 for weapon in ['SM2','SM2ER','SM6','ESSM']:
  lines+=['### '+name[weapon],'','| 표적 고도 | 정지 | 접근250m/s | 접근680m/s | 이탈250m/s |','|---|---:|---:|---:|---:|']
  for alt in [30,1000,5000,10000,15000,20000]:
   vals=[]
   for speed in [0,250,680,-250]:
    q=nm[(weapon,alt,speed)];v=fmt(q) if field=='maxRangeKm' else f"{q['interceptPointKm']:.3f}" if q['interceptPointKm'] is not None else '성공 없음: '+q['firstFailure']['result']['reason'];vals.append(v)
   lines.append('| '+f'{alt/1000:g}km'+' | '+' | '.join(vals)+' |')
  lines+=['']
lines+=['요격점 표의 ≥ 기호는 의도적으로 생략했다. 접근 표적의 최초거리 상한 성공이 요격점거리 자체의 상한/최대를 뜻하지 않기 때문이다. 각 사격과의 대응 및 상한 상태는 JSON/CSV에 보존했다.','']
lines+=['ENV_B 원문은300km 측정 범위를 보존했다. 별도 stage0의6조건만 기준판도500km로 다시 측정했다. 아래 차이는 각 보고서에서 확인한 최대값 간 차이며, 나머지90조건의 기준판을500km까지 새로 계산했다고 주장하지 않는다. 비연속 구간이 있으므로 측정 밖 영역을 추정으로 채우지 않았다.','']
for speed,title in [(0,'정지 표적'),(-250,'이탈250m/s 표적')]:
 lines+=['## ENV_B 대비 — '+title,'','| 기종 | 고도 | ENV_B(300km 상한) | 같은 기준판500km 추가 측정 | ENV_C(500km 상한) | 기록값 차이 |','|---|---:|---:|---:|---:|---:|']
 for q in comparison:
  if q['targetSpeedMps']!=speed:continue
  lines.append(f"| {name[q['weapon']]} | {q['altM']/1000:g}km | {'≥' if q['envBCapped300'] else ''}{q['envBInitialKm']} | {q['baseline500InitialKm'] if q['baseline500InitialKm'] is not None else '—'} | {'≥' if q['newCapped500'] else ''}{q['newInitialKm']} | {q['initialDeltaKm'] if q['initialDeltaKm'] is not None else '상한 때문에 미확정'} |")
 lines+=['']
fig,axes=plt.subplots(2,2,figsize=(13,9));alts=[30,1000,5000,10000,15000,20000]
for ax,weapon in zip(axes.flat,['SM2','SM2ER','SM6','ESSM']):
 for speed,label,color in [(0,'stationary','#2166ac'),(-250,'retreat250','#b35806')]:
  ax.plot([h/1000 for h in alts],[bm[(weapon,h,speed)]['maxRangeKm']for h in alts],'--o',color=color,alpha=.6,label='ENV_B '+label)
  ax.plot([h/1000 for h in alts],[nm[(weapon,h,speed)]['maxRangeKm']for h in alts],'-s',color=color,label='ENV_C '+label)
  for data in [bm,nm]:
   capped=[h for h in alts if data[(weapon,h,speed)]['upperCapReached']]
   if capped:ax.scatter([h/1000 for h in capped],[data[(weapon,h,speed)]['maxRangeKm']for h in capped],marker='^',s=65,facecolors='none',edgecolors=color)
 ax.set(title=name[weapon],xlabel='Target altitude MSL (km)',ylabel='Initial target distance (km)');ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.suptitle('Game-engine envelopes: ENV_B capped300 / ENV_C capped500; triangle markers denote capped lower bounds');fig.tight_layout();fig.savefig(O/'envelope-b-c-comparison.png',dpi=140);fig.savefig(O/'envelope-b-c-comparison.svg',metadata={'Date':None});plt.close(fig);lines+=['![전후 비교](results/envelope-b-c-comparison.png)','','## 지정한 퇴행2건','', '| 조건 | ENV_A | ENV_B | ENV_C | ENV_C 다음1km 실패 |','|---|---:|---:|---:|---|']
for weapon in ['SM2ER','SM6']:
 k=(weapon,15000,-250);q=nm[k];lines.append(f"| {name[weapon]} · 고도15km · 이탈250m/s | {am[k]['maxRangeKm']} | {bm[k]['maxRangeKm']} | {fmt(q)} | {q['firstFailure']['result']['reason'] if q['firstFailure'] else '상한 도달'} |")
iso=read(H/'evidence/loft-isolate-aligned.json');ison=read(H/'evidence/loft-isolate-on.json');oldiso=read(R/'docs/missile/termination/A/evidence/loft-isolate-current.json');lines+=['',f"SM-6 100km/5km/접근250m/s/seed12002: ALL4 기준 {oldiso['results'][0]['reason']} {oldiso['results'][0]['flightTimeS']:.6f}s → 정렬 후 종료기OFF3회/ON3회 모두 명중 {iso['results'][0]['flightTimeS']:.6f}s. 원래 RF/시커/INS 경로의 게임 시험이며, ENV 이상조건의 기본 seed와 구분한다.",'','## 설계 거리 자체 사격','', '| 기종 | 표적고도 | 목표거리 | 변경 전 | 정렬 후 | 정렬 후 최근접 / 종말속도 |','|---|---:|---:|---|---|---|']
goal=read(O/'goal-shots.json');gm={(q['version'],q['weapon'],q['altM']):q for q in goal['cases']}
for weapon in ['SM2ER','SM6']:
 for alt in [1000,10000,20000]:
  q=gm[('aligned',weapon,alt)];x=gm[('baseline',weapon,alt)];lines.append(f"| {name[weapon]} | {alt/1000:g}km | {q['rangeKm']}km | {x['reason']} | {q['reason']} | {q['closestM']:.1f}m / {q['terminal']['speedMps']:.1f}m/s |")
lines+=['','## 관찰한 로프트 변화 — 수정하지 않음','']
selected=[]
for version,data in [('ENV_B',b),('ENV_C',n)]:
 q=next(q for q in data['trajectories']if q['weapon']=='SM2ER'and q['rangeKm']==150 and q['altM']==5000 and q['targetSpeedMps']==0);s=next(s for s in q['samples']if s['shelfM']is not None);selected.append({'version':version,'firstShelfM':s['shelfM'],'apogeeM':q['apogeeM'],'reason':q['reason'],'flightTimeS':q['flightTimeS'],'terminalSpeedMps':q['terminal']['speedMps'],'closestM':q['closestM']})
lines+=['| ER150km/5km/정지 | 첫 B4선반 | 최고고도 | 결과 | 비행시간 | 종말속도 |','|---|---:|---:|---|---:|---:|']
for q in selected:lines.append(f"| {q['version']} | {q['firstShelfM']:.3f}m | {q['apogeeM']:.3f}m | {q['reason']} | {q['flightTimeS']:.3f}s | {q['terminalSpeedMps']:.3f}m/s |")
lines+=['','같은 사격에서 fullLoft 분모와 Rmax 기준이 커지면 정규화된 로프트 요구가 작아진다. 위처럼 선반·초기 궤적이 낮아지고 기존 항력에서 에너지를 더 잃는 결과가 관찰됐다. 수치만 목표 거리로 올렸다고 실제 최대가 늘어나지 않았다. 추진 자체의 부족으로 단정하지 않는다. 함수/추진/항력/배터리/시커/신관은 바꾸지 않았다.','',f"120궤적 결과: {dict(collections.Counter(q['reason']for q in n['trajectories']))}.",f"비단조 coarse 행: {proof['nonMonotonicCoarseRows']}개. 전체 명중 구간은 연속 사거리 원으로 해석하지 않는다.",'','`LOW_SPEED`는 기존 Mach0.5 종료, `SEA_IMPACT`는 실제 해면 관통 후 종료, `BATTERY_EXHAUSTED`는 기존 비행 전원 수명 종료다. `PROX_DETONATION_AIRCRAFT`인데 성공=false인 경우 신관은 기폭했지만 기존 항공기 격추 판정을 만족하지 못했다. 신규 성공 기준을 추가하지 않았다.','','[전체120궤적·10Hz·단계 구간](results/REPORT_ENV_C.md) · [96행 전후 CSV](results/comparison-env-b-c.csv) · [요약 JSON](ENVELOPE_TABLE_C.json) · [저고도 이탈/횡단 조사](results/LOW_ALT_INVESTIGATION.md) · [원본 ENV_B](../B/REPORT.md)']
(C/'REPORT.md').write_text('\n'.join(lines)+'\n');(O/'loft-range-normalization-example.json').write_text(json.dumps(selected,indent=2));print('ENV_C full report:',len(n['table']),len(n['trajectories']))
