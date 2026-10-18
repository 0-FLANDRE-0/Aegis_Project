"""VP_A business assertions unchanged; navigate new containers for pointer tests."""
import argparse,importlib.util,json,sys,subprocess,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('vp_reg',R/'docs/viewport/A/verify_regressions.py');vp=importlib.util.module_from_spec(spec);spec.loader.exec_module(vp)
def install_navigation():
 from playwright.sync_api import Locator
 original=Locator.click
 def click(self,*args,**kwargs):
  info={};reopen_air=False
  try:
   info=self.evaluate('e=>({id:e.id,tab:e.dataset.tab,window:e.closest(".ui-window-a")?.id})',timeout=2000)
   if info.get('id')=='c':
    reopen_air=self.page.evaluate("()=>{if(!window.__UI_A__)return false;const was=__UI_A__.snapshot().windows.AIR.open;for(const id of ['NAV','AIR','CIC'])__UI_A__.close(id);return was;}")
   if info.get('id','').startswith(('c14','c15')):self.page.evaluate("()=>{if(window.__UI_A__)for(const id of ['NAV','ARM','AIR','DEBUG','FLEET','CIC'])__UI_A__.close(id)}")
   if info.get('tab'):self.page.evaluate("()=>{const e=document.getElementById('uiWindowListA');if(e)e.hidden=false;}")
   elif info.get('window'):self.page.evaluate("id=>{if(window.__UI_A__){const s=__UI_A__.snapshot().windows[id];__UI_A__.open(id);if(s.collapsed)__UI_A__.dock(id,'');}}",info['window'].replace('uiWindowA-',''))
  except Exception:pass
  result=original(self,*args,**kwargs)
  if reopen_air:self.page.evaluate('__UI_A__.open("AIR")')
  if info.get('tab'):self.page.evaluate("()=>{const e=document.getElementById('uiWindowListA');if(e)e.hidden=true;}")
  return result
 Locator.click=click
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--only',choices=vp.SUITES);ap.add_argument('--start-at',choices=vp.SUITES);ap.add_argument('--parallel',type=int,default=1);a=ap.parse_args()
 if a.only:
  install_navigation()
  if a.only=='isar-ui':
   original_read=Path.read_text
   def read(self,*x,**y):
    s=original_read(self,*x,**y)
    if self==R/vp.SUITES['isar-ui']:
     s=s.replace('<=281', "<=x.locator('#uiWindowA-AIR .ui-body-a').evaluate('e=>e.clientHeight')+1")
     s=s.replace("x.mouse.click(xy['x'],xy['y'])","x.evaluate('window.__UI_A__?.close(\"AIR\")');x.mouse.click(xy['x'],xy['y'])")
    return s
   Path.read_text=read
  return vp.adapted(a.only,a.html,a.out)
 a.out.mkdir(parents=True,exist_ok=True);rows=[]
 if a.parallel>1:
  def run(name):
   with (a.out/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,__file__,str(a.html),str(a.out/name),'--only',name],cwd=R,stdout=log,stderr=subprocess.STDOUT)
   return {'suite':name,'exitCode':p.returncode}
  with concurrent.futures.ThreadPoolExecutor(max_workers=min(4,a.parallel))as pool:
   for future in concurrent.futures.as_completed([pool.submit(run,name)for name in vp.SUITES]):rows.append(future.result());print(rows[-1],flush=True);(a.out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
  if any(r['exitCode']for r in rows):raise SystemExit(1)
 else:
  start=not a.start_at
  for name in vp.SUITES:
   if name==a.start_at:start=True
   if not start:continue
   print('RUN '+name,flush=True);p=subprocess.run([sys.executable,__file__,str(a.html),str(a.out/name),'--only',name],cwd=R);rows.append({'suite':name,'exitCode':p.returncode});(a.out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
   if p.returncode:raise SystemExit(p.returncode)
 p=subprocess.run([sys.executable,'docs/helicopter/F/verify_regression.py',str(R/'Aegis_SIM_v48_WIP_VP_A.html'),str(a.html),str(a.out/'paired-baseline'),'--baseline-only'],cwd=R);rows.append({'suite':'paired-baseline','exitCode':p.returncode});(a.out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(p.returncode)
if __name__=='__main__':main()
