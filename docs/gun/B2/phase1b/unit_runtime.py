from pathlib import Path
import json, math, time
from playwright.sync_api import sync_playwright
from harness import P, build, serve, load_http, launch

expected=json.loads((P/'model-parameters.json').read_text())
extra='''
window.__B2B_UNIT__=()=>({
 spec:GUN_B1_SPEC.fragments,
 rows:['Kh-35U','Kh-32'].flatMap(target=>[5,10,15,20,25].map(distanceM=>({target,distanceM,detail:gunB1FragmentationPk(distanceM,'GUN',target,{missileSpeedMps:662.8512070445188,relativeSpeedMps:280,targetSpeedMps:280,encounterAngleRad:0})}))),
 samSource:_wip88FragmentationPk.toString(),fieldSource:gunB2FragmentField.toString()
});
'''
raw=build(record=False,extra=extra);server,url=serve(raw);errors=[];started=time.perf_counter()
try:
 with sync_playwright() as pw:
  browser=launch(pw);page=load_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(120000)
  got=page.evaluate('__B2B_UNIT__()');page.close();page.context.close();browser.close()
finally: server.shutdown()
checks=[]
for row,ref in zip(got['rows'],expected['unitRows']):
 detail=row['detail'];checks.append({
  'target':row['target'],'distanceM':row['distanceM'],
  'countError':detail['mottCountCheck']-expected['mott']['n0'],
  'massErrorKg':detail['mottMassCheckKg']-expected['input']['caseMassKg'],
  'pkError':detail['pk']-ref['pk'],
  'binCount':len(detail['massBins']),
 })
result={'pass':not errors and all(abs(x['countError'])<1e-9 and abs(x['massErrorKg'])<1e-10 and abs(x['pkError'])<1e-12 and x['binCount']==10 for x in checks),'errors':errors,'elapsedS':time.perf_counter()-started,'checks':checks,'spec':got['spec']}
(P/'evidence').mkdir(exist_ok=True);(P/'evidence/unit-runtime.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass'] else 1)
