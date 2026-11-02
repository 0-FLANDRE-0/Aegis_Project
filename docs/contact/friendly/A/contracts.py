import json,time
from playwright.sync_api import sync_playwright
from harness import P,build,serve,launch,load_fast_http
errors=[];start=time.perf_counter();raw=build(True,extra=(P/'contracts.js').read_text());server,url=serve(raw)
try:
 with sync_playwright()as pw:
  b=launch(pw);p=load_fast_http(b,url,own='CG_52_LATE_TICONDEROGA',errors=errors);r=p.evaluate('__FC_CONTRACTS__()');b.close()
finally:server.shutdown()
r.update(errors=errors,wallS=time.perf_counter()-start);(P/'evidence/contracts.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(0 if r['pass']and not errors else 1)
