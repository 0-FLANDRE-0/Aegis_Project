"""G7: 2 ships x 2 bearings x 4 salvo sizes x 30 seeds x ON/OFF = 960.
Actual observed-track/whole fixed tick game, fresh operational baseline each run.
No asserted hit-rate goal, no tuning feedback.
"""
from pathlib import Path
import sys,json,time,hashlib,os
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
worker=int(sys.argv[1]);workers=int(sys.argv[2]);raw=Path(os.environ.get('GUN_B1_EFFECT_HTML',str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'))).read_bytes();fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js']);out=Path(os.environ.get('GUN_B1_EFFECT_OUT',str(H/'evidence/effects')));out.mkdir(parents=True,exist_ok=True);path=out/f'worker{worker}.jsonl';seen=set()
if path.exists():
 for l in path.read_text().splitlines():
  try:seen.add(json.loads(l)['caseId'])
  except ValueError:pass
jobs=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for bearing in [0,90]:
  for count in range(1,5):
   for i in range(30):
    for on in [False,True]:jobs.append({'ship':ship,'seed':419010+i,'bearing':bearing,'count':count,'on':on})
jobs=[{**q,'caseId':i}for i,q in enumerate(jobs)if i%workers==worker and i not in seen];start=time.perf_counter();errors=[]
with path.open('a')as f,sync_playwright()as pw:
 b=launch(pw);page=None;owner=None
 for n,c in enumerate(jobs):
  if c['ship']!=owner:
   if page:page.close()
   owner=c['ship'];page=load_fleet(b,instrument(raw,fixture),own=owner,errors=errors);page.set_default_timeout(240000)
  result=page.evaluate('c=>__GB_TEST__.scenario(c)',{k:v for k,v in c.items()if k not in ['ship','caseId']});row={**c,'result':result,'htmlSha256':hashlib.sha256(raw).hexdigest()};f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush()
  if n%5==0:print(json.dumps({'worker':worker,'done':n+1,'remaining':len(jobs)-n-1,'caseId':c['caseId'],'elapsedS':time.perf_counter()-start,'shots':result['shots'],'preCiwsKills':result['preCiwsKills'],'gunPreCiwsKills':result['gunPreCiwsKills']}),flush=True)
 if page:page.close()
 b.close()
(out/f'worker{worker}-complete.json').write_text(json.dumps({'cases':len(jobs)+len(seen),'errors':errors,'elapsedS':time.perf_counter()-start,'htmlSha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
