"""Run MAP_A's unchanged runtime assertions against PIP_A. Read-only screenshot
capture bypasses Playwright font/animation settling under software WebGL load.
"""
import argparse,base64,runpy,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--only');a=ap.parse_args()
jobs=[('input','verify_map.py',['--part','input']),('additional','verify_additional.py',[]),('preferences','verify_preferences.py',[]),('legacy','verify_map.py',['--part','legacy','--baseline',str(a.base)]),('invariance','verify_map.py',['--part','invariance']),('bounds','verify_menu_bounds.py',[]),('examples','capture_examples.py',[]),('3d','verify_map.py',['--part','3d']),('routes','capture_routes.py',[]),('ui-a1','verify_ui_a1.py',[]),('ui-a1-events','run_contracts.py',['--part','events']),('ui-a1-hash','run_contracts.py',['--part','hash'])]
if not a.only:
 a.out.mkdir(parents=True,exist_ok=True)
 for name,script,extra in jobs:
  print('MAP regression '+name,flush=True)
  with (a.out/(name+'.log')).open('w')as log:
   code=subprocess.run([sys.executable,__file__,str(a.base),str(a.html),str(a.out),'--only',name],cwd=R,stdout=log,stderr=subprocess.STDOUT).returncode
  print(name,code,flush=True)
  if code:raise SystemExit(code)
else:
 from playwright.sync_api import Page
 def screenshot(self,**kw):
  session=self.context.new_cdp_session(self)
  try:data=base64.b64decode(session.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data'])
  finally:session.detach()
  if kw.get('path'):Path(kw['path']).write_bytes(data)
  return data
 Page.screenshot=screenshot
 name,script,extra=next(q for q in jobs if q[0]==a.only);path=R/'docs/map/A'/script
 sys.path.insert(0,str(path.parent));sys.argv=[str(path),*([str(a.base)]if script=='run_contracts.py'else[]),str(a.html),str(a.out/name),*extra];runpy.run_path(str(path),run_name='__main__')
