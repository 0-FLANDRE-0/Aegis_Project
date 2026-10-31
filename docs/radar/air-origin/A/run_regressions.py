"""Fresh main/candidate regressions. No reference/threshold updates; retain failures."""
from pathlib import Path
import concurrent.futures,datetime,json,os,subprocess,sys,time
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence';E.mkdir(exist_ok=True)
if (B/'approved-expectations.json').exists():E=E/'approval/full-regression';E.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'docs/viewport/A'));from verify_regressions import SUITES
jobs=[]
for tag,html in [('MAIN','Aegis_SIM_v48_WIP_GUN_B1.html'),('AIR_ORIGIN_A','Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html')]:
 out=E/'regression'/tag
 approval=B/'approved-expectations.json';approved_args=['--approved-air-origin-baselines',str(approval)]if tag=='AIR_ORIGIN_A'and approval.exists()else[]
 env={**os.environ,'AIR_ORIGIN_REGRESSION':'1','AIR_ORIGIN_HTML':html,'AIR_ORIGIN_OUT':str(out),'PYTHONPATH':str(B/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
 for name in SUITES:
  cmd=[sys.executable,str(R/'docs/map/E/verify_emcon_ui.py'),str(R/html),str(out/'domain'/name)]if name=='emcon-ui'else[sys.executable,str(R/'docs/map/E/run_legacy_domain.py'),str(R/html),str(out/'domain'/name),'--only',name]
  jobs.append((tag+'-domain-'+name,cmd,env))
 jobs.extend([(tag+'-paired42',[sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(R/html),str(out/'paired42'),'--baseline-only']+approved_args,env),
 (tag+'-natural28',[sys.executable,str(R/'docs/map/E/c2_browser.py'),html,tag,'--suite','natural'],env),
 (tag+'-webgl8',[sys.executable,str(R/'docs/envelope/D/run_observed_webgl.py'),html,str(out/'webgl8')],env),
 (tag+'-world120',[sys.executable,str(R/'docs/map/E/verify_delivery_world.py')]+approved_args,env),
 (tag+'-ciws',[sys.executable,str(B/'verify_combat.py'),html,str(out/'combat')],env)])
start=time.perf_counter();rows=[]
def run(j):
 name,cmd,env=j;at=time.perf_counter()
 with(E/(name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 return {'name':name,'exitCode':p.returncode,'elapsedS':time.perf_counter()-at}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for f in concurrent.futures.as_completed([pool.submit(run,j)for j in jobs]):
  row=f.result();rows.append(row);print(json.dumps(row),flush=True);(E/'regression-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
(E/'regression-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'expectedValuesUpdated':False,'jobCount':len(jobs)},indent=2)+'\n')
