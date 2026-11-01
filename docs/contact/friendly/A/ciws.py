"""Real fixed-tick D1 rerun over the delivered candidate. Prior diagnostic remains immutable."""
from pathlib import Path
import json,time,sys
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http,sha
mode=sys.argv[1]if len(sys.argv)>1 else'd1';extra=(R/'docs/ciws/dmg/A/diagnostic.js').read_text();
if mode=='protection':extra+='\n'+(R/'docs/ciws/dmg/A/protection-trace.js').read_text()
raw=build(True,extra=extra);server,url=serve(raw);out=P/'evidence';errors=[];start=time.perf_counter()
seeds=[419018,419020,419026,419028]if mode=='protection'else list(range(419010,419040))
try:
 with sync_playwright()as pw:
  b=launch(pw)
  with(out/f'ciws-{mode}.jsonl').open('w')as f:
   for s in seeds:
    p=load_fast_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(600000);r=p.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':s});sig=r.pop('equivalenceSignature');f.write(json.dumps({'case':{'seed':s},'signatureSha256':sha(sig.encode()),**r},separators=(',',':'))+'\n');f.flush();p.context.close();print(mode,s,r['result']['shipHits'],round(r['result']['hpAfter'],3),round(time.perf_counter()-start,1),flush=True)
  b.close()
finally:server.shutdown()
(out/f'ciws-{mode}-execution.json').write_text(json.dumps({'errors':errors,'wallS':time.perf_counter()-start},indent=2)+'\n')
