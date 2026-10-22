"""Validate Node-computed table boundaries in the final browser's native capsule."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'docs/pip/B'));import browser_backend;browser_backend.install()
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];raw=a.html.read_bytes();table=json.loads((Path(__file__).parent/'ENVELOPE_TABLE_C.json').read_text());rows=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,errors=errors);p.evaluate('window.__ENV_BOUNDARY_TEST__=__ENV_A__.create()')
 for i,r in enumerate(table['rows']):
  for kind in ['lastSuccess','firstFailure']:
   expected=r[kind]
   if expected is None:continue
   c={'weapon':r['weapon'],'rangeKm':expected['rangeKm'],'altM':r['altM'],'targetSpeedMps':r['targetSpeedMps'],'samples':False};q=p.evaluate('c=>__ENV_BOUNDARY_TEST__.runCase(c)',c);rows.append({'case':c,'kind':kind,'expected':expected,'actual':{'success':q['success'],'reason':q['reason'],'closestM':q['closestM'],'terminalSpeedMps':q['terminal']['speedMps']},'sameOutcome':q['success']==expected['success']and q['reason']==expected['reason'],'closestDeltaM':abs(q['closestM']-expected['closestM'])if q['closestM']is not None and expected['closestM']is not None else None,'speedDeltaMps':abs(q['terminal']['speedMps']-expected['terminalSpeedMps'])})
  if (i+1)%24==0:print('boundaries',i+1,flush=True)
 b.close()
checks={'all96RowBoundsMatchBrowser':all(r['sameOutcome']for r in rows),'allRequiredBoundsPresent':len(rows)==sum(r[k]is not None for r in table['rows']for k in ['lastSuccess','firstFailure']),'pageErrors':not errors};q={'pass':all(checks.values()),'checks':checks,'records':rows,'maxClosestDeltaM':max(r['closestDeltaM']or 0 for r in rows),'maxSpeedDeltaMps':max(r['speedDeltaMps']for r in rows),'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'boundaries.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps({'pass':q['pass'],'checks':checks,'maxClosestDeltaM':q['maxClosestDeltaM'],'maxSpeedDeltaMps':q['maxSpeedDeltaMps'],'failed':[r['case']for r in rows if not r['sameOutcome']]}));raise SystemExit(0 if q['pass']else 1)
