"""Original frozen cases on an explicitly selected product; no acceptance edits."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument,fixture
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('tag');ap.add_argument('--suite',choices=['release','natural','webgl','ui'],required=True);a=ap.parse_args();out=H/'evidence/c2'/a.tag;out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();rows=[];errors=[];start=time.perf_counter()
if a.suite=='release':
 sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument as original_air_instrument
 with sync_playwright()as pw:
  b=launch(pw);p=load_fleet(b,original_air_instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for kind,name in [('normal','normal'),('dual','dual'),('fault','fault'),('battery','battery'),('request','release-request')]:
   cases=json.loads((R/'docs/missile/termination/A/cases'/(name+'.json')).read_text())
   for i,c in enumerate(cases):
    r=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);rows.append({'id':kind+':'+str(i),'condition':c,'result':r})
    if i%8==0:print(kind,i,r['reason'],flush=True)
   (out/(kind+'.json.gz')).write_bytes(gzip.compress(json.dumps({'rows':[x for x in rows if x['id'].startswith(kind+':')],'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()},separators=(',',':')).encode(),9,mtime=0))
  p.close();b.close()
 assert len(rows)==300
elif a.suite=='natural':
 cases=json.loads((R/'docs/missile/fuze-zem/A/natural-cases.json').read_text())
 with sync_playwright()as pw:
  b=launch(pw);p=load_fleet(b,instrument(raw,fixture()),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for c in cases:
   r=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);rows.append({'id':c['caseId'],'condition':c,'result':r});print(c['caseId'],r['reason'],flush=True)
  p.close();b.close()
 assert len(rows)==28
elif a.suite=='webgl':
 cmd=[sys.executable,str(R/'docs/envelope/D/run_observed_webgl.py'),str(a.html),str(out/'webgl')];result=subprocess.run(cmd,cwd=R);raise SystemExit(result.returncode)
elif a.suite=='ui':
 import runpy
 sys.path.insert(0,str(R/'docs/pip/B'));import browser_backend;browser_backend.install();sys.argv=[str(R/'docs/pip/B/verify_ui.py'),str(a.html),str(out/'ui')];runpy.run_path(str(R/'docs/pip/B/verify_ui.py'),run_name='__main__')
result={'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(out/(a.suite+'.json.gz')).write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),9,mtime=0));print(json.dumps({'suite':a.suite,'shots':len(rows),'success':sum(r['result'].get('success',False)for r in rows),'errors':errors,'elapsedS':result['elapsedS']},default=str));raise SystemExit(1 if errors else 0)
