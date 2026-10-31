from pathlib import Path
import hashlib,json
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch
from fast_http import load_fast_http
E=P/'evidence/native-trace';E.mkdir(parents=True,exist_ok=True)
extra=(P/'range_probe.js').read_text()+r'''
window.__B2_NATIVE_SOURCES__=()=>Object.fromEntries([['spawnMainGunProjectileWip13B3',spawnMainGunProjectileWip13B3],['gunB2ShellEvent',gunB2ShellEvent],['gunB2FragmentationPk',gunB2FragmentationPk],['gunB2Pointing',gunB2Pointing],['gunB1SolveAirTrack',gunB1SolveAirTrack]].map(([k,v])=>[k,v.toString()]));
window.__B2_NATIVE_TRACE__=c=>{
 const integral=gunB2FuzeIntegral,detonate=gunB1Detonate,samples=[],events=[];let traced;
 try{
  gunB2FuzeIntegral=function(row,p,prev,next,dt,a,b){const value=integral(...arguments),s=p._gunB2Fuze?.contacts.get(row.object);if(value>0&&samples.length<512)samples.push({id:p.id,ageS:p.ageS,dt,from:a,to:b,integratedSignalS:value,pass:s?.pass,budgetS:s?.budget,exposureBeforeS:s?.exposure,uniform:s?.uniform});return value;};
  gunB1Detonate=function(p,event,dt){events.push({id:p.id,ageS:p.ageS,event:{...event},pending:p._gunB2Fuze?.pending?{...p._gunB2Fuze.pending}:null,passes:p._gunB2Fuze?.passes,velocityMps:{...p.velocityMps},positionM:{...p.positionM}});return detonate(...arguments);};
  traced=__B2_RANGE_PROBE__(c);
 }finally{gunB2FuzeIntegral=integral;gunB1Detonate=detonate;}
 return {traced,samples,events};
};
'''
raw=build(record=False,extra=extra);server,url=serve(raw);errors=[];rows=[];sources=[]
with sync_playwright()as pw:
 browser=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for km in [1,5,9]:
   c={'rangeKm':km,'bearing':0,'seed':592001,'interceptRange':True}
   p=load_fast_http(browser,url,own=ship,errors=errors);p.set_default_timeout(600000)
   source=p.evaluate('__B2_NATIVE_SOURCES__()');sources.append({k:hashlib.sha256(v.encode()).hexdigest()for k,v in source.items()})
   baseline=p.evaluate('c=>__B2_RANGE_PROBE__(c)',c);p.close();p.context.close()
   p=load_fast_http(browser,url,own=ship,errors=errors);p.set_default_timeout(600000)
   q=p.evaluate('c=>__B2_NATIVE_TRACE__(c)',c);p.close();p.context.close()
   q.update(baseline=baseline,exact=baseline==q['traced']);rows.append({'ship':ship,'condition':c,**q});print(ship,km,q['exact'],flush=True)

 browser.close()
server.shutdown();expected=json.loads((P/'evidence/static.json').read_text())['runtimeExpectedHashes'];checks={'actualNativeFunctionSources':all(s==expected for s in sources),'readOnlyTrace':all(r['exact']for r in rows),'processingDelay':all(abs(e['ageS']-e['event']['detectedAgeS']-.002)<1e-9 for r in rows for e in r['events']if e['event']['reason']=='MFF_PROXIMITY'),'oneBudgetPerPass':all(len({s['uniform']for s in r['samples']if s['pass']==1})<=1 for r in rows),'pageErrors0':not errors};q={'pass':all(checks.values()),'checks':checks,'sources':sources,'expected':expected,'rows':rows,'errors':errors};(E/'results.json').write_text(json.dumps(q,indent=2)+'\n');print(checks);raise SystemExit(not q['pass'])
