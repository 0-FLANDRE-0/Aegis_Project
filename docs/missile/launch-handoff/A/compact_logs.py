"""Small scalar CSV for the report. Full raw control vectors stay in JSON.gz."""
from pathlib import Path
import json,csv,gzip
H=Path(__file__).resolve().parent;O=H/'analysis'
d=json.load(gzip.open(H/'final-results/pipeline.json.gz'));rows=[]
def pref(out,prefix,d):
 if isinstance(d,dict):
  for k,v in d.items():
   if not isinstance(v,(dict,list)):out[prefix+k]=v
for r in d['records']:
 c=r['condition'];tag=f"{r['variant']}_{c['weapon']}_{c['rangeKm']}km"
 for p in r['pipeline']:
  s=p['post'];ch=s.get('chain')or{};out={'case':tag,'timeS':p['timeS'],'owner':s['owner'],'guidance':s['guidance'],'pitchover':s['pitchover'],'pitchoverTimerS':s['pitchoverTimerS'],'handoffAtS':s['handoffAtS'],'launchAuthority':s['launchAuthority'],'overlap':s['overlap'],'blend':s['blend'],'feedbackActive':s['feedbackActive'],'actuatorSaturated':s['actuatorSaturated']}
  for k in ['desiredPitchRad','desiredBearingRad','bodyPitchRad','bodyHeadingRad','velocityPitchRad','velocityHeadingRad','speed3DMps','horizontalMps','rawDemandG','limitedCommandG','availableG','actualNormalG','deliveredG','source','sourceAgeS','rfAgeS','trackValid','rawAoaDeg','physicalAoaLimitRad']:out[k]=s.get(k)
  for name in ['pn','apn','zem']:
   call=p['calls'][name];out[name+'.calledThisTick']=call['calledThisTick'];out[name+'.lastCalledAtS']=call['lastCalledAtS'];value=call['value']or{}
   for k in ['ax','ay','az']:out[name+'.'+k]=value.get(k)
  for prefix,v in [('position.',s.get('positionM')),('velocity.',s.get('velMps')),('normalAcceleration.',s.get('normalAccWorld')),('controlVector.',s.get('controlVector')),('kappa.',p['kappa']),('finalInput.',p['finalInput']),('bridgeInput.',(ch.get('bridge')or{}).get('input')),('bridgeOutput.',(ch.get('bridge')or{}).get('output')),('autopilotOutput.',(ch.get('autopilot')or{}).get('output'))]:pref(out,prefix,v)
  gate=s.get('newGate');pref(out,'gate.',gate if gate and gate['atS']==p['timeS']else{})
  command=(ch.get('autopilot')or{}).get('command')or{}
  for k in ['ax','ay','az','tgo','gammaFDeg']:out['consumedCommand.'+k]=command.get(k)
  pref(out,'preGate.',{k:v for k,v in(p['preGate']or{}).items()if k in ['lifeS','pitchover','handoffAtS','launchAuthority','overlap','bodyPitchRad','velocityPitchRad','speed3DMps','horizontalMps','owner']})
  rows.append(out)
columns=list(dict.fromkeys(k for r in rows for k in r))
with gzip.open(O/'pipeline-compact.csv.gz','wt',newline='')as f:
 w=csv.DictWriter(f,columns,lineterminator='\n');w.writeheader();w.writerows(rows)
clock=json.loads((H/'final-evidence/clock-view-damage.json').read_text());lines=['# 배속 / 표시 회귀 비용','', '서버 Chromium, 동일3840 fixed ticks. 실폰 FPS 또는64배 실시간 달성 보장이 아니다.','', '| SPG 상태 | 배속 | frame 수 | wall초 |','|---|---:|---:|---:|']
for r in clock['records']:lines.append(f"| {'손상'if r['damage']else'정상'} | {r['timeScale']} | {sum(b['frames']for b in r['batches'])} | {sum(b['wallS']for b in r['batches']):.3f} |")
lines+=['','원래 물리/RNG/제어 동등 판정은 `final-evidence/clock-view-damage.json`을 따른다.']
(H/'PERFORMANCE.md').write_text('\n'.join(lines)+'\n')
print('compact rows',len(rows),'bytes',(O/'pipeline-compact.csv.gz').stat().st_size)
