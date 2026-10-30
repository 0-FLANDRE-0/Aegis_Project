"""Read CPA at 120s and continue the changed combat case to a native outcome.

Only a readout is added to the disposable test page. Native sensors, target AI,
termination and VLS are preserved. This does not replace the 120s hash evidence.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/reg-k'
sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument
from browser import launch,load_fleet
helper="""window.__REG_K_COMBAT_READ__=()=>{const m=TERM_LIVE_LAST_MISSILE_A;return {afterAction:__TERM_LIVE_TEST__.afterAction(),closestM:m?._everClosest!=null?m._everClosest*1000:null,fuzeMissM:m?._fuzeBurstMissM??null,loft:m?._loftB4??null,target:targetPool[0]?{alive:!!targetPool[0].alive,x:targetPool[0].x,y:targetPool[0].y,z:targetPool[0].z,vx:targetPool[0].vx,vy:targetPool[0].vy,vz:targetPool[0].vz}:null};};"""
def add(raw):
 h=instrument(raw).decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);s=gzip.decompress(base64.b64decode(m[1])).decode();s=s.replace('\n  completeShipStartup();','\n'+helper+'\n  completeShipStartup();',1);z=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);j=json.loads(m[1]);j[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());return(h[:m.start(1)]+json.dumps(j,separators=(',',':'))+h[m.end(1):]).encode()
errors=[];rows=[]
with sync_playwright()as pw:
 b=launch(pw)
 for tag,file in [('recovery',R/'archive/v48/WIP_RANGE_RECOVERY_A/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'),('current',R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html')]:
  if not file.exists():file=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/file.name
  p=load_fleet(b,add(file.read_bytes()),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
  c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True}
  p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');launchResult=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
  if not launchResult.get('launched'):raise RuntimeError(launchResult)
  p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(6300)');at120=p.evaluate('__REG_K_COMBAT_READ__()');t=120
  while not p.evaluate('__TERM_LIVE_TEST__.observe().dead')and t<520:
   p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(600)');t+=10
  final=p.evaluate('__REG_K_COMBAT_READ__()');rows.append({'version':tag,'at120':at120,'finalAfterS':t,'final':final,'core':p.evaluate('__CORE_SELFTEST_FAILURES__')});print(tag,at120['closestM'],final['afterAction'],flush=True);p.close()
 b.close()
out={'pass':not errors and all(not r['core']for r in rows),'records':rows,'errors':errors,'method':__doc__};(E/'combat-followup.json').write_text(json.dumps(out,indent=2)+'\n')
