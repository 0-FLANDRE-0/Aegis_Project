import json,time
from playwright.sync_api import sync_playwright
from harness import P,build,serve,launch,load_fast_http
rows=[('ddg-moving',{'kind':'HELO','moving':True,'seconds':90},'DDG_119_LATE_FLIGHT_IIA'),('iff-off',{'kind':'HELO','iff':False,'seconds':60},'CG_52_LATE_TICONDEROGA'),('no-dl',{'kind':'HARPOON','seconds':60,'emconAtS':10},'CG_52_LATE_TICONDEROGA'),('observer-off',{'kind':'HARPOON','seconds':75,'observe':False},'CG_52_LATE_TICONDEROGA')]
out=P/'evidence';start=time.perf_counter();errors=[];raw=build(True,extra=(P/'repro.js').read_text());server,url=serve(raw);checks={}
try:
 with sync_playwright()as pw:
  b=launch(pw)
  for name,c,ship in rows:
   p=load_fast_http(b,url,own=ship,errors=errors);p.set_default_timeout(600000);r=p.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',c);(out/(name+'.json')).write_text(json.dumps(r,separators=(',',':'))+'\n');p.context.close()
   checks[name+'.core']=not r['core']and not any(r['faults'])
   if name=='ddg-moving':checks[name+'.oneFile']=max(len(x['tracks'])for x in r['samples'])==1;checks[name+'.iff']=any(x['identity']=='FRIEND'for x in r['final'])
   if name=='iff-off':checks[name+'.noArtificialFriend']=bool(r['final'])and all(x['identity']=='UNKNOWN'and not x['iff']for x in r['final']);checks[name+'.oneFile']=max(len(x['tracks'])for x in r['samples'])==1
   if name=='no-dl':
    pic=r['picture'];checks[name+'.positionUnavailable']=pic['dataLink']is False and pic['telemetryAvailable']is False and len(pic['launches'])==1 and pic['launches'][0]['source']=='NOT_OBSERVED'and pic['launches'][0]['positionM']is None
    checks[name+'.flightContinues']=r['samples'][-1]['truthDiagnosticOnly']['alive']is True
   if name=='observer-off':
    before=json.loads((out/'after-2.json').read_text());checks[name+'.observerDoesNotAlterState']=all(r[k]==before[k]for k in ['rng','step','final','samples'])
   print(name,{k:v for k,v in checks.items()if k.startswith(name)},round(time.perf_counter()-start,1),flush=True)
  b.close()
finally:server.shutdown()
res={'pass':all(checks.values())and not errors,'checks':checks,'errors':errors,'wallS':time.perf_counter()-start};(out/'variants.json').write_text(json.dumps(res,indent=2)+'\n');raise SystemExit(0 if res['pass']else 1)
