"""Same native 120-second idle truth and retired-UI census, baseline/candidate."""
import json,re,time,hashlib
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http
start=time.perf_counter();rows=[];errors=[]
state=re.search("STATE='''([\\s\\S]*?)'''",(R/'docs/envelope/D/verify_world120.py').read_text())[1]
extra="window.__FC_DOM__=()=>({liveLock:!!document.getElementById('lockBtn'),retiredLock:!!mapELegacyNodeE('lockBtn'),liveQuickLock:!!document.getElementById('external3DAutoLockBtn')});"
for current in [False,True]:
 raw=build(current,extra=extra);server,url=serve(raw)
 try:
  with sync_playwright()as pw:
   b=launch(pw);p=load_fast_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.evaluate('__GB_TEST__.reset(12002)');dom=p.evaluate('__FC_DOM__()');p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(7200)');s=p.evaluate(state);core=p.evaluate('__CORE_SELFTEST_FAILURES__');b.close()
 finally:server.shutdown()
 tag='after'if current else'before';(P/'evidence'/('idle-'+tag+'120.json')).write_text(s+'\n');rows.append({'tag':tag,'truthSha256':hashlib.sha256(s.encode()).hexdigest(),'dom':dom,'core':core});print(rows[-1],flush=True)
checks={'truthHashSame':rows[0]['truthSha256']==rows[1]['truthSha256'],'retiredUiContractSame':rows[0]['dom']==rows[1]['dom'],'core':all(not r['core']for r in rows)and not errors};(P/'evidence/idle-and-dom.json').write_text(json.dumps({'checks':checks,'rows':rows,'errors':errors,'wallS':time.perf_counter()-start},indent=2)+'\n');raise SystemExit(0 if all(checks.values())else 1)
