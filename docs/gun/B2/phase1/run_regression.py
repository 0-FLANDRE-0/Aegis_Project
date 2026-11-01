"""Unchanged legacy assertions; approval reconciliation is a separate exact audit."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression';E.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'docs/viewport/A'));from verify_regressions import SUITES
jobs=[]
for mode in ['OFF','ON']:
 out=E/mode;env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':mode,'B2_OUT':str(out),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
 for name in SUITES:
  cmd=[sys.executable,str(R/'docs/map/E/verify_emcon_ui.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(out/'domain'/name)]if name=='emcon-ui'else[sys.executable,str(R/'docs/map/E/run_legacy_domain.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(out/'domain'/name),'--only',name]
  jobs.append((mode+'-domain-'+name,cmd,env))
 jobs.extend([(mode+'-paired42',[sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(out/'paired42'),'--baseline-only'],env),(mode+'-world120',[sys.executable,str(R/'docs/map/E/verify_delivery_world.py')],env)])
 for suite in ['release','natural','ui']:jobs.append((mode+'-'+suite,[sys.executable,str(R/'docs/map/E/c2_browser.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),'GUN_B2_'+mode,'--suite',suite],env))
 jobs.append((mode+'-webgl8',[sys.executable,str(R/'docs/envelope/D/run_observed_webgl.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(out/'webgl8')],env))
 for name in ['verify_d_native','verify_d_ui','verify_d_edges','verify_ew_h3','verify_e','verify_e_policy','run_final_ui']:
  jobs.append((mode+'-'+name,[sys.executable,str(R/'docs/map/E'/(name+'.py'))],env))
start=time.perf_counter();rows=[]
def run(job):
 name,cmd,env=job;t=time.perf_counter();log=E/(name+'.log');stamp=E/(name+'.done.json')
 if stamp.exists():return json.loads(stamp.read_text())
 with log.open('w')as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 row={'name':name,'exit':r.returncode,'elapsedS':time.perf_counter()-t};print(json.dumps(row),flush=True);stamp.write_text(json.dumps(row)+'\n');return row
with concurrent.futures.ThreadPoolExecutor(max_workers=1)as pool:
 for row in pool.map(run,jobs):rows.append(row);(E/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'assertionsChanged':0},indent=2)+'\n')
