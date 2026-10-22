"""Read-only low-altitude investigation: native telemetry, no controller changes."""
import argparse,collections,csv,gzip,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='ENV_C_LOW'
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('aligned',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
b=json.loads(a.baseline.read_text());n=json.loads(a.aligned.read_text());summary=[]
for tag,j,src in [('baseline',b,a.baseline),('aligned',n,a.aligned)]:
 (a.out/f'low-{tag}.json.gz').write_bytes(gzip.compress(src.read_bytes(),9,mtime=0))
 (a.out/f'low-{tag}-receipt.json').write_bytes(Path(str(src)+'.receipt.json').read_bytes())
 for q in j['cases']:
  ts=q['diagnosticTicks'];d=q['firstDescent']['after']if q['firstDescent']else{};last=ts[-1];sea=next((x for x in ts if x['altitudeM']<40 and x['vzMps']<0),{})
  summary.append({'version':tag,**{k:q[k]for k in ['weapon','rangeKm','altM','targetSpeedMps','crossSpeedMps','reason','success','closestM','flightTimeS']},'terminalSpeedMps':q['terminal']['speedMps'],'descentStartS':d.get('timeS'),'descentStartAltitudeM':d.get('altitudeM'),'descentMode':d.get('mode'),'descentPhase':d.get('phase'),'descentGuidance':d.get('guidance'),'descentCmdOmegaPit':d.get('cmdOmegaPit'),'descentKappaAz':d.get('kappaAz'),'at40mTimeS':sea.get('timeS'),'at40mVzMps':sea.get('vzMps'),'at40mCmdOmegaPit':sea.get('cmdOmegaPit'),'terminalVzMps':last['vzMps'],'terminalGuidance':last['guidance'],'terminalSeaGuard':last['seaGuardActive']})
with(a.out/'low-summary.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
fig,axes=plt.subplots(1,2,figsize=(13,5))
for q in n['cases'][:3]:
 ts=q['diagnosticTicks'];axes[0].plot([x['timeS']for x in ts],[x['altitudeM']for x in ts],label=q['weapon']);last=q['flightTimeS'];tail=[x for x in ts if x['timeS']>=last-2];axes[1].plot([x['timeS']-last for x in tail],[x['altitudeM']for x in tail],label=q['weapon'])
for ax in axes:ax.grid(alpha=.3);ax.legend();ax.set_ylabel('Altitude MSL (m)');ax.axhline(0,c='navy',lw=.8)
axes[0].set_xlabel('Flight time (s)');axes[1].set_xlabel('Time before sea impact (s)');fig.suptitle('ENV_C: 30 m retreat targets — unchanged native guidance / sea-impact handling');fig.tight_layout();fig.savefig(a.out/'low-retreat-descent.png',dpi=140);fig.savefig(a.out/'low-retreat-descent.svg',metadata={'Date':None});plt.close(fig)
lines=['# 저고도 해면 충돌 조사 — 수정 없음','','실제 게임 함수/60Hz 적분을 그대로 사용한 분리 진단이다. 표적은 처음 +X에 두고 이탈은 +X250m/s, 횡단은 +Y250m/s(사격선과90°)로 이동한다. 레이더/데이터링크/조사기는 기존 ENV 이상 조건이다. 전장·센서 truth로 전술 정보를 생성하지 않는다. 진단의 실제 위치·속도는 사후 원인 분석 전용이다.','','## 제시한 이탈3건','','| 기종 | 최초거리 | 변경 전 속도/최근접 | 정렬 후 속도/최근접 | 결과 | 최초 하강: 시각/고도 | 당시 상태/명령 |','|---|---:|---:|---:|---|---|---|']
for i,q in enumerate(n['cases'][:3]):
 old=b['cases'][i];d=q['firstDescent']['after'];lines.append(f"| {q['weapon']} | {q['rangeKm']}km | {old['terminal']['speedMps']:.3f}m/s / {old['closestM']:.3f}m | {q['terminal']['speedMps']:.3f}m/s / {q['closestM']:.3f}m | {q['reason']} | {d['timeS']:.6f}s / {d['altitudeM']:.3f}m | {d['mode']}/{d['phase']}/{d['guidance']} · pitch-rate {d['cmdOmegaPit']:.6f}rad/s · Kappa az {d['kappaAz']:.3f}m/s² |")
lines+=['','![하강 및 충돌 전2초](low-retreat-descent.png)','','최초 하강은 vz가 양수/0에서 음수로 바뀐 첫60Hz 스텝으로 정의했다. 실제 하강 명령은 정점 이전부터 나오므로 하강 시작시각과 명령 시작은 같지 않다. 전체60Hz 명령/속도/자세 로그와 마지막2초는 raw JSON에 있다.','','## 횡단18건','','| 기종 | 표적고도 | 10km | 20km | 40km |','|---|---:|---|---|---|']
for weapon in ['SM2','SM2ER','SM6']:
 for alt in [30,200]:
  vals=[]
  for r in [10,20,40]:
   q=next(q for q in n['cases']if q['weapon']==weapon and q['altM']==alt and q['rangeKm']==r and q['crossSpeedMps']==250);vals.append(f"{q['reason']} · {q['terminal']['speedMps']:.1f}m/s · CPA {q['closestM']:.1f}m")
  lines.append('| '+weapon+' | '+str(alt)+'m | '+' | '.join(vals)+' |')
count=collections.Counter(q['reason']for q in n['cases'][3:]);lines+=['',f'횡단 결과: {dict(count)}. 30m뿐 아니라200m 횡단 표적 일부에서도 충돌한다. 정렬 전후21건의 성공/실패 사유는 모두 같았다. ER/SM-6의 launch 계획 정규화가 달라져 미세한 궤적 차이는 있으며 byte-identical 궤적이라고 주장하지 않는다.','','## 코드 경로와 원인 추정','','1. `_wip79KappaPipState`는 관측 예측점과 terminal velocity 조건을 구성한다. `PIP_LOS` 고각과 표적 수평 속도 반대 방향의 terminal vector를 사용한다. 이탈·횡단에서 이 terminal vector 요구는 큰 자세 변화를 요구할 수 있다. `computeKappaMidcourseAccelV2` → `applyAccelCommandToAutopilotV1` → `updateSamSixDofLiteDynamics`로 하강 명령이 전달된다. 측정된 실제 Kappa az와 cmdOmegaPit는 표/JSON에 있다. 이것만으로 terminal-vector 정책을 단일 원인이라고 확정하지 않는다.','','2. 제시한3건은 `DIRECT`여서 B4 shelf/DIVE 전환으로 생긴 충돌이 아니다. 하강 시작은 KAPPA_MIDCOURSE이며, 충돌 직전에는 ENDGAME/PN 경로로 넘어가 이미 상승 명령을 내고 있다. 속도는 충분하지만 하강 속도를0으로 돌리기 전에 수면을 통과한다. 40m 아래 진입 때도 cmdOmegaPit는 양수다. 힘·모멘트·자세 응답 지연과 이전에 쌓인 하강 운동량을 함께 고려해야 한다.','','3. `_samSeaClearanceRateGuard`의 예측 고도/seaMargin 보호는 `isESSM`인 경우에만 활성이다. SM2MR/ER/SM6는 해당 분기로 들어가지 않는다. 계획의 seaMarginM14 같은 값이 존재해도 이3종에 연속적인 해면 회피 보호를 제공하는 것은 아니다.','','4. `applyAccelCommandToAutopilotV1`의 soft guard는 고도<40m, vz<-5m/s, time-to-sea<0.5s일 때 하강 pitch 명령만 감쇠한다. 이미 상승 명령인 상태에서는 적용되지 않으며, 강제 상승력/위치 보정은 없다. 이3건의 최종 softGuard=false는 이 조건과 일치한다.','','5. `updateMissileBodyB3`의 실제 6DOF 경로는 적분 후 z<0 && !vlsPhase이면 즉시 SEA_IMPACT로 종료한다. 그 다음의 Math.max(0,z)는 사전 고도 하한이나 해면 회피가 아니다. target PIP z>=0 clamp도 미사일의 실제 궤적을0 위에 강제로 고정하지 않는다.','','결론은 추적 정보 소실이나 속도 부족이 아닌, 해당 저고도 기하의 하강/회복과 기존 해면 보호 적용 범위 문제다. 정확한 제어법 보완 여부는 별도 사용자 결정 사항이며 이번에는 유도·고도하한·해면 판정을 변경하지 않았다.','','원문 코드: [native-engine.js](../native-engine.js)에서 위 함수명을 검색하면 현재 게임에서 그대로 복사한 코드가 나온다. 모든 네이티브 함수의 변경0은 RANGE_A 정적 감사로 별도 확인했다.']
(a.out/'LOW_ALT_INVESTIGATION.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'cases':len(n['cases']),'cross':dict(count),'reasonChanges':sum(x['reason']!=y['reason']for x,y in zip(b['cases'],n['cases']))}))
