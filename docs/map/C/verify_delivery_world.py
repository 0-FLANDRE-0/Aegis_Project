from pathlib import Path
import sys,re,json,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet
sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument
s=(R/'docs/envelope/D/verify_world120.py').read_text();STATE=re.search("STATE='''([\\s\\S]*?)'''",s)[1];raw=(R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes();errors=[];records=[];start=time.perf_counter()
expected={'idle':'fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc','combat':'b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1'}
with sync_playwright()as pw:
 b=launch(pw)
 for mode in ['idle','combat']:
  p=load_fleet(b,instrument(raw)if mode=='combat'else raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);ticks=0
  if mode=='combat':
   c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True};p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');ticks=900;q=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
   while not q.get('launched')and ticks<3600:p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');ticks+=300;q=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
   assert q.get('launched')
  p.evaluate('n=>__NAVAL_SIM_DIAG__.stepTicks(n)',7200-ticks);state=p.evaluate(STATE);sig=hashlib.sha256(state.encode()).hexdigest();q={'mode':mode,'ticks':7200,'truthSha256':sig,'expected':expected[mode],'same':sig==expected[mode],'core':p.evaluate('__CORE_SELFTEST_FAILURES__')};records.append(q);print(q,flush=True);p.close()
 b.close()
out={'pass':all(r['same']and not r['core']for r in records)and not errors,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(H/'evidence/delivery-world120.json').write_text(json.dumps(out,indent=2)+'\n');assert out['pass']
