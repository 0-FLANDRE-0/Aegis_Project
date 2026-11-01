from pathlib import Path
import json,sys,time,os
from playwright.sync_api import sync_playwright
from deadline import check,remaining
check()
from harness import P,R,build,serve,load_http,launch,sha
E=Path(os.environ.get('B2_RANGE_OUT',str(P/'evidence/range-intercept')));E.mkdir(parents=True,exist_ok=True);product_sha=sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes())
if any(E.glob('*.jsonl')) and (E/'execution.json').exists():assert json.loads((E/'execution.json').read_text())['htmlSha256']==product_sha,'RANGE_CACHE_REQUIRES_IDENTICAL_HTML_USE_B2_RANGE_OUT_FOR_FRESH_RUN'
build_info=json.loads((P/'build.json').read_text());assert build_info['htmlSha256']==product_sha
model=build_info['modelFingerprints'];observed=[]
source_hook='window.__B2_MEASURED_FUNCTIONS__=()=>Object.fromEntries(['+','.join('[\"'+n+'\",'+n+']' for n in model['nativeSourceHashes'])+'].map(([n,f])=>[n,f.toString()]));'
raw=build(record=False,extra=(P/'range_probe.js').read_text()+source_hook);server,url=serve(raw);start=time.perf_counter();errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for bearing in [0,90]:
   path=E/f'{ship}-{bearing}.jsonl';seen={(r['rangeKm'],r['seed'])for r in [json.loads(l)for l in path.read_text().splitlines()]}if path.exists()else set()
   p=load_http(b,url,own=ship,errors=errors);p.set_default_timeout(600000)
   actual={n:sha(v.encode())for n,v in p.evaluate('__B2_MEASURED_FUNCTIONS__()').items()};assert actual==model['nativeSourceHashes'],'ACTUAL_NATIVE_SOURCE_MISMATCH';observed.append(actual)
   with path.open('a')as f:
    for km in range(1,10):
     for s in range(40):
      check()
      c={'rangeKm':km,'bearing':bearing,'seed':592001+s,'interceptRange':True}
      if(km,c['seed'])in seen:continue
      row=p.evaluate('c=>__B2_RANGE_PROBE__(c)',c);f.write(json.dumps({'ship':ship,**row},separators=(',',':'))+'\n');f.flush()
     print(ship,bearing,km,round(time.perf_counter()-start,1),flush=True)
   p.close();p.context.close()
 b.close()
server.shutdown();(E/'execution.json').write_text(json.dumps({'errors':errors,'elapsedS':time.perf_counter()-start,'htmlSha256':product_sha,'modelFingerprints':model,'actualSourceChecks':observed,'conditions':'IDEAL_OBSERVATION_CONSTANT_VELOCITY_PHYSICAL_ASM','samplesPerBin':40},indent=2)+'\n')
