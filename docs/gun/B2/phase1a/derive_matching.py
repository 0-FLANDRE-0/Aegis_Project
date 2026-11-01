"""Compute one fixed SIM_TUNED fuze-warhead match, not a hit-rate fit."""
from pathlib import Path
import concurrent.futures,csv,json,math,os,statistics,subprocess,sys,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,sha
from fast_http import load_fast_http
from deadline import check,remaining
OLD=P.parent/'phase1';E=P/'evidence/matching';E.mkdir(parents=True,exist_ok=True)
BASE=Path('/tmp/aegis-gun-b2/b2a-baseline.html')
if not BASE.exists():BASE.write_bytes(subprocess.check_output(['git','show','c1d17cee:Aegis_SIM_v48_WIP_GUN_B2.html'],cwd=R))
assert sha(BASE.read_bytes())=='c48c2396932e07c8051b7a07d2da282951587283d768f2caa384a48936a0ed8b'
def rows():
 return [json.loads(l)for f in sorted((OLD/'evidence/g7').glob('worker*.jsonl'))for l in f.open()if json.loads(l)['on']]
def available(b):return next((f for x in b.get('results',[])if'worldMinRad'in(f:=x.get('gunB2FragmentField',{}))),None)
def clean(x):
 if isinstance(x,dict):return{k:clean(v)for k,v in x.items()if k not in ['refreshMs','elapsedMs']}
 if isinstance(x,list):return[clean(v)for v in x]
 return x
extra=(OLD/'g7_observer.js').read_text()+'''
const b2aOldDetonate=gunB1Detonate;let b2aSpeedLog=[];
gunB1Detonate=function(p,event,dt){b2aSpeedLog.push({id:p.id,ageS:p.ageS,step:simStepCounter,reason:event.reason,velocityMps:{...p.velocityMps},speedMps:Math.hypot(p.velocityMps.x,p.velocityMps.y,p.velocityMps.z)});return b2aOldDetonate(...arguments);};
window.__B2A_MATCH_RUN__=c=>{b2aSpeedLog=[];const result=__B2_G7_RUN__(c);return{result,diagnostic:__B2_G7_LOG__(),speeds:b2aSpeedLog};};
window.__B2A_MATCH_CONSTANTS__=()=>({vf:_wip88GurneyFragmentSpeed(GUN_B1_SPEC.fragments),spec:GUN_B1_SPEC.fragments,source:_wip88GurneyFragmentSpeed.toString()});
'''
def worker(w):
 check();jobs=[r for r in rows()if any(not available(b)for b in r['diagnostic']['bursts'])];jobs=[r for i,r in enumerate(jobs)if i%2==w];raw=build(file=str(BASE),record=False,extra=extra);server,url=serve(raw);errors=[];out=E/f'replay{w}.jsonl';seen={json.loads(l)['caseId']for l in out.read_text().splitlines()}if out.exists()else set();started=time.perf_counter()
 with sync_playwright()as pw,out.open('a')as f:
  b=launch(pw)
  for j,c in enumerate(jobs):
   check()
   if c['caseId']in seen:continue
   p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(min(600000,int(remaining()*1000)));constants=p.evaluate('__B2A_MATCH_CONSTANTS__()');q=p.evaluate('c=>__B2A_MATCH_RUN__(c)',{k:c[k]for k in ['ship','bearing','count','seed','on','caseId']});p.close();p.context.close();exact=clean(q['result'])==clean(c['result'])and clean(q['diagnostic'])==clean(c['diagnostic']);f.write(json.dumps({'caseId':c['caseId'],'exact':exact,'constants':constants,**q},separators=(',',':'))+'\n');f.flush();assert exact,('BASELINE_REPLAY_DIFF',c['caseId']);print(w,j+1,len(jobs),c['caseId'],exact,flush=True)
  b.close()
 server.shutdown();assert not errors;return{'worker':w,'exit':0,'cases':len(jobs),'elapsedS':time.perf_counter()-started}
if len(sys.argv)>1:worker(int(sys.argv[1]));raise SystemExit()
check();start=time.perf_counter()
def run(w):
 with(E/f'replay{w}.log').open('w')as f:r=subprocess.run([sys.executable,'-u',__file__,str(w)],cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT,timeout=remaining())
 return {'worker':w,'exit':r.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:execution=list(pool.map(run,[0,1]))
(E/'execution.json').write_text(json.dumps(execution,indent=2)+'\n');assert all(r['exit']==0 for r in execution)
replayed={r['caseId']:r for f in E.glob('replay*.jsonl')for l in f.open()if(r:=json.loads(l))};assert len(replayed)==25 and all(r['exact']for r in replayed.values());const=next(iter(replayed.values()))['constants'];vf=const['vf'];speeds=[];crossMax=0
for r in rows():
 replay={p['id']:p for p in replayed.get(r['caseId'],{}).get('speeds',[])}
 for b in r['diagnostic']['bursts']:
  field=available(b)
  if field:
   speed=vf*math.sin(math.radians(70))/math.tan(field['worldMinRad'])-vf*math.cos(math.radians(70));other=vf*math.sin(math.radians(110))/math.tan(field['worldMaxRad'])-vf*math.cos(math.radians(110));assert abs(speed-other)<1e-8
   method='EXACT_INVERSE_OF_STORED_NATIVE_FRAGMENT_WORLD_ANGLE'
   if b['projectileId']in replay:crossMax=max(crossMax,abs(speed-replay[b['projectileId']]['speedMps']))
  else:speed=replay[b['projectileId']]['speedMps'];method='NATIVE_READ_ONLY_REPLAY_MISSING_SPEED'
  speeds.append({'caseId':r['caseId'],'ship':r['ship'],'bearing':r['bearing'],'count':r['count'],'seed':r['seed'],'projectileId':b['projectileId'],'reason':b['outcome'],'ageS':b['ageS'],'speedMps':speed,'method':method})
assert len(speeds)==1417 and crossMax<1e-8;vm=statistics.median(r['speedMps']for r in speeds);vt=280.;b=12.5;delay=.002;w=-(vm+vt)
def roots(a,bb,c):
 disc=bb*bb-4*a*c
 return[(-bb-math.sqrt(disc))/(2*a),(-bb+math.sqrt(disc))/(2*a)]
def arrival(thetaDeg,speed=vm,miss=b):
 # In translating projectile axes, r at first design detection; target is approaching.
 x=miss/math.tan(math.radians(thetaDeg));r=(x-(speed+vt)*delay,miss);ww=-(speed+vt);ts=[t for t in roots(ww*ww-vf*vf,2*r[0]*ww,r[0]*r[0]+r[1]*r[1])if t>0];t=min(ts);dx=r[0]+ww*t;return {'angleDeg':math.degrees(math.atan2(miss,dx)),'flightTimeS':t,'detectionX':x,'afterDelayX':r[0],'arrivalX':dx,'arrivalY':miss}
lo,hi=.001,89.999
for _ in range(100):
 m=(lo+hi)/2
 if arrival(m)['angleDeg']>90:hi=m
 else:lo=m
center=(lo+hi)/2;matched=arrival(center);formula=math.degrees(math.atan2(b,(vm+vt)*(delay+b/vf)));assert abs(center-formula)<1e-10;allowed=20<=center<=80
with(E/'burst-speeds.csv').open('w',newline='')as f:
 wri=csv.DictWriter(f,fieldnames=list(speeds[0]),lineterminator='\n');wri.writeheader();wri.writerows(speeds)
q={'provenance':'SIM_TUNED_GAME_ONLY_FUZE_WARHEAD_MATCH','baselineCommit':'c1d17cee','baselineHtmlSha256':sha(BASE.read_bytes()),'g7SourceHtmlSha256':'925178b5b06bcd81304f6b98da4436fda4fd85eaf7ea8de3813a981981f0da71','g7OnCases':480,'burstCount':1417,'storedGeometrySpeedCount':1392,'missingSpeedNativeReplayCount':25,'readOnlyReplayCases':25,'nativeReplayExact':True,'inverseVsNativeMaxErrorMps':crossMax,'speedMedianMps':vm,'speedMinMps':min(r['speedMps']for r in speeds),'speedMaxMps':max(r['speedMps']for r in speeds),'targetSpeedMps':vt,'passDistanceM':b,'processingDelayS':delay,'gurney':const,'formula':'theta=atan2(b,(vm+vt)*(processingDelayS+b/vf)); r_after_delay+w*t, t=b/vf at body90deg','fixedPolarCenterDeg':center,'matched':matched,'within20to80':allowed,'applied':False,'elapsedS':time.perf_counter()-start}
(P/'matching.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if not allowed:raise SystemExit('STOP_DESIGN_CENTER_OUTSIDE_20_80_NO_PRODUCT_CHANGE')
