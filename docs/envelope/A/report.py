"""Render engine-computed results as exportable plots/CSV/readable tables."""
import argparse,collections,csv,hashlib,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='ENV_A'
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);r=json.loads(a.results.read_text());(a.out/'results.json').write_bytes(a.results.read_bytes())
keys=['weapon','rangeKm','altM','targetSpeedMps','timeS','distanceKm','xM','yM','altitudeM','speedMps','mach','targetXM','phase','loftDemand','cruiseAltM','shelfM','highTargetShelfAltM']
with(a.out/'trajectories-10hz.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
 for q in r['trajectories']:
  for i,s in enumerate(q['samples']):
   if i and s['timeS']==q['samples'][i-1]['timeS']:continue
   w.writerow({**{k:q[k]for k in keys[:4]},**{k:s.get(k)for k in keys[4:]}})
summary=['weapon','rangeKm','altM','targetSpeedMps','label','success','reason','apogeeM','flightTimeS','closestM','fuzeMissM','burnoutStatus','burnoutTimeS','burnoutDistanceKm','burnoutAltitudeM','burnoutSpeedMps','terminalSpeedMps','terminalMach']
with(a.out/'trajectory-summary.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=summary);w.writeheader()
 for q in r['trajectories']:
  b=q['burnout']or{};w.writerow({**{k:q.get(k)for k in summary[:11]},'burnoutStatus':'RECORDED'if b else'NOT_REACHED_BEFORE_TERMINATION','burnoutTimeS':b.get('timeS'),'burnoutDistanceKm':b.get('distanceKm'),'burnoutAltitudeM':b.get('altitudeM'),'burnoutSpeedMps':b.get('speedMps'),'terminalSpeedMps':q['terminal']['speedMps'],'terminalMach':q['terminal']['mach']})
with(a.out/'loft-phase-intervals.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(['weapon','rangeKm','altM','targetSpeedMps','phase','startS','endS','resolutionS'])
 for q in r['trajectories']:
  for s in q['phases']:w.writerow([q[k]for k in ['weapon','rangeKm','altM','targetSpeedMps']]+[s[k]for k in ['phase','startS','endS']]+[.1])
colors={30:'#1976b5',5000:'#178749',15000:'#c96816'};styles={30:'-',60:'--',100:'-.',150:':',200:(0,(5,2,1,2))}
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 fig,axes=plt.subplots(1,2,figsize=(15,5),sharey=True);rows=[q for q in r['trajectories']if q['weapon']==weapon];ymax=max(q['apogeeM']/1000 for q in rows)*1.08
 for ax,speed in zip(axes,[0,250]):
  for q in rows:
   if q['targetSpeedMps']!=speed:continue
   s=q['samples'];ax.plot([p['distanceKm']for p in s],[p['altitudeM']/1000 for p in s],color=colors[q['altM']],linestyle=styles[q['rangeKm']],linewidth=1,alpha=.4 if q['beyondComputedEnvelope']else.9)
   ax.plot(q['terminal']['distanceKm'],q['terminal']['altitudeM']/1000,'o'if q['success']else'x',color=colors[q['altM']],markersize=3)
  ax.set(title='Stationary target'if speed==0 else'Head-on target: 250 m/s',xlabel='Missile horizontal travel from launch (km)',xlim=(0,310),ylim=(0,max(5,ymax)));ax.grid(alpha=.25)
 axes[0].set_ylabel('Altitude MSL (km)');fig.suptitle(f'{weapon} — unchanged game-engine trajectories (not real-weapon performance)')
 from matplotlib.lines import Line2D
 legend=[Line2D([0],[0],color=c,label=f'Target {h/1000:g} km')for h,c in colors.items()]+[Line2D([0],[0],color='#555',linestyle=s,label=f'Initial {d} km')for d,s in styles.items()]
 fig.legend(handles=legend,ncol=8,loc='lower center',fontsize=8);fig.tight_layout(rect=(0,.07,1,.95));fig.savefig(a.out/(weapon+'-trajectories.svg'),metadata={'Date':None});fig.savefig(a.out/(weapon+'-trajectories.png'),dpi=130);plt.close(fig)
# Compact embedded data: no trajectories or native model references.
table={'schema':'AEGIS_ENVELOPE_TABLE_A_1','provenance':'GAME_ENGINE_COMPUTED','profileHash':r['profileHash'],'rangeCapKm':300,'resolutionKm':1,'targetKind':r['targetKind'],'idealSupport':True,'rows':[]}
for q in r['table']:
 short={k:q[k]for k in ['weapon','profileId','altM','targetSpeedMps','maxRangeKm','upperCapReached','resolutionKm','nonMonotonicCoarse','searchPolicy']}
 for key in ['lastSuccess','firstFailure']:
  x=q[key];short[key]=None if x is None else{'rangeKm':x['rangeKm'],'reason':x['result']['reason'],'success':x['result']['success'],'closestM':x['result']['closestM'],'terminalSpeedMps':x['result']['terminal']['speedMps']}
 table['rows'].append(short)
(H/'ENVELOPE_TABLE_A.json').write_text(json.dumps(table,ensure_ascii=False,indent=2))
(a.out/'envelope-table.json').write_text(json.dumps(table,ensure_ascii=False,indent=2))
lines=['# ENV_A 게임 엔진 진단 결과','',f"프로파일 SHA-256: `{r['profileHash']}`",'','정지·해면 발사 / 오차 없는 지속 표적 정보 / 기존 비행·유도·로프트·신관 코드. 실제 장비 성능과 비교하지 않는다. `≥300`은 검사 상한이며 실제 최대 거리 확정을 뜻하지 않는다.','',f"최대 거리 96조합, 궤적 120사격. 각 궤적은 10Hz이며 마지막 종료 샘플을 추가했다. 단계 구간은 이 10Hz 관측에 기반하므로 경계 시각의 분해능은 0.1초다.",'','이분 탐색 후 더 먼 모든 정수 km를 검사해 비단조 성공 구간을 누락하지 않았다. 범위 내부의 모든 거리에서 성공한다는 뜻은 아니다.','']
for weapon in ['SM2','SM2ER','SM6','ESSM']:
 lines+=['## '+weapon,'',f'![{weapon} 궤적]({weapon}-trajectories.png)','','단위: 최초 사격 거리 km. 표적 고도는 MSL.','','| 고도 | 정지 | 접근 250m/s | 접근 680m/s | 이탈 250m/s |','|---|---:|---:|---:|---:|']
 for alt in [30,1000,5000,10000,15000,20000]:
  cells=[]
  for v in [0,250,680,-250]:
   q=next(q for q in r['table']if q['weapon']==weapon and q['altM']==alt and q['targetSpeedMps']==v);cells.append(('≥'if q['upperCapReached']else'')+str(q['maxRangeKm']))
  lines.append('| '+str(alt)+'m | '+' | '.join(cells)+' |')
 lines+=['']
fail=collections.Counter(q['reason']for q in r['trajectories']if not q['success']);lines+=['## 실패 사유','',str(dict(fail)),'','`LOW_SPEED`: 기존 Mach 0.5 종료 조건, `SEA_IMPACT`: 해면 충돌, `MAX_LIFE`: 기존 수명 제한. `PROX_DETONATION_AIRCRAFT`인데 성공이 아니면 근접신관은 작동했으나 기존 항공기 파괴 거리 조건을 만족하지 않은 것이다.','', '마지막 성공/첫 실패의 실제 거리·사유·최근접 거리·종말 속도는 [envelope-table.json](envelope-table.json)에, 연소 종료·최고 고도·종말 속도는 [trajectory-summary.csv](trajectory-summary.csv)에 기록했다.']
(a.out/'REPORT_ENV_A.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'rows':len(table['rows']),'trajectories':len(r['trajectories']),'failures':dict(fail),'profileHash':r['profileHash']}))
