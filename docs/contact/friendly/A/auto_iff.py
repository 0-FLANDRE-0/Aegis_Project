import json,time
from playwright.sync_api import sync_playwright
from harness import P,build,serve,launch,load_fast_http
start=time.perf_counter();errors=[];raw=build(True,extra=(P/'repro.js').read_text());server,url=serve(raw)
try:
 with sync_playwright()as pw:
  b=launch(pw);p=load_fast_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);r=p.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',{'kind':'HELO','moving':True,'seconds':90,'auto':True});b.close()
finally:server.shutdown()
checks={'inventoryUnchangedInAuto':r['inventoryUnchanged'],'friendlyThroughIff':bool(r['final'])and all(x['identity']=='FRIEND'and x['iff']['authenticatedFriendly']for x in r['final']),'oneFile':max(len(x['tracks'])for x in r['samples'])==1,'core':not r['core']and not any(r['faults'])and not errors};(P/'evidence/auto-iff.json').write_text(json.dumps({'checks':checks,'result':r,'errors':errors,'wallS':time.perf_counter()-start},separators=(',',':'))+'\n');print(checks);raise SystemExit(0 if all(checks.values())else 1)
