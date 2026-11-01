"""Reduced approved G7 matrix:120 fresh full-native fixed-tick scenarios, one lane."""
from pathlib import Path
import json,os,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,sha
from fast_http import load_fast_http
from deadline import check,remaining
check();q=json.loads((P.parent/'phase1a/evidence/dispersion/validation.json').read_text());assert q['pass'],'B2A_ANCHOR_SOURCE_GUARD_STOP';E=P/'evidence/g7';E.mkdir(parents=True,exist_ok=True)
alljobs=[{'ship':ship,'bearing':bearing,'count':count,'seed':419010+s,'on':on}for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for bearing in[0,90]for count in range(1,5)for s in range(30)for on in[False,True]];jobs=[{**c,'caseId':i}for i,c in enumerate(alljobs)if c['on']and c['count']in[1,4]and c['seed']<419025];assert len(jobs)==120;jobs.sort(key=lambda c:(c['seed'],c['count'],c['bearing'],c['ship']))
shaProduct=sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes());model=json.loads((P/'measurement-build.json').read_text())['modelFingerprints']
extra=(P.parent/'phase1/g7_observer.js').read_text()+'''
const b2aG7Detonate=gunB1Detonate;let b2aG7Speeds=[];
gunB1Detonate=function(p,event,dt){b2aG7Speeds.push({id:p.id,step:simStepCounter,speedMps:Math.hypot(p.velocityMps.x,p.velocityMps.y,p.velocityMps.z),velocityMps:{...p.velocityMps}});return b2aG7Detonate(...arguments);};
window.__B2A_G7__=c=>{b2aG7Speeds=[];const result=__B2_G7_RUN__(c);return{result,diagnostic:__B2_G7_LOG__(),burstVelocities:b2aG7Speeds};};
'''
extra+='window.__B2A_NATIVE_SOURCES__=()=>Object.fromEntries(['+','.join('["'+n+'",'+n+']'for n in model['nativeSourceHashes'])+'].map(([n,f])=>[n,f.toString()]));'
raw=build(record=False,extra=extra);server,url=serve(raw);errors=[];started=time.perf_counter();path=E/'trials.jsonl';old=[json.loads(l)for l in path.read_text().splitlines()]if path.exists()else[];assert all(r['htmlSha256']==shaProduct for r in old),'STALE_RETRY_FORBIDDEN';seen={r['caseId']for r in old};observed=[];completed=False
try:
 with path.open('a')as f,sync_playwright()as pw:
  b=launch(pw)
  for i,c in enumerate(jobs):
   check()
   if c['caseId']in seen:continue
   p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(min(600000,int(remaining()*1000)))
   if len(observed)<1:
    actual={n:sha(s.encode())for n,s in p.evaluate('__B2A_NATIVE_SOURCES__()').items()};assert actual==model['nativeSourceHashes'];observed.append(actual)
   at=time.perf_counter();r=p.evaluate('c=>__B2A_G7__(c)',c);p.close();p.context.close();f.write(json.dumps({**c,**r,'htmlSha256':shaProduct,'wallS':time.perf_counter()-at},separators=(',',':'))+'\n');f.flush()
   if i%3==0:print(i+1,120,round(time.perf_counter()-started,1),flush=True)
  b.close()
 completed=True
finally:
 server.shutdown();(E/'execution.json').write_text(json.dumps({'complete':completed,'cases':sum(1 for _ in path.open())if path.exists()else 0,'errors':errors,'elapsedS':time.perf_counter()-started,'htmlSha256':shaProduct,'actualSources':observed,'workers':1,'resourceRetries':0},indent=2)+'\n')
assert not errors
