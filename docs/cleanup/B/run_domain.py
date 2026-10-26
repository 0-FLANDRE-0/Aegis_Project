"""Rerun all 420 assertions, with only the explicitly approved six references."""
from pathlib import Path
import concurrent.futures,json,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/viewport/A'))
from verify_regressions import SUITES
html=R/'Aegis_SIM_v48_WIP_CLEAN_B.html';out=H/'evidence/domain';out.mkdir(parents=True,exist_ok=True);rows=[];start=time.perf_counter()
def run(name):
 with(out/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(R/'docs/pip/B/run_domain.py'),str(html),str(out/name),'--only',name],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 return{'suite':name,'exitCode':p.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for row in pool.map(run,SUITES):rows.append(row);(out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
with(out/'paired-baseline.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html'),str(html),str(out/'paired-baseline'),'--baseline-only','--approved-raid-baseline',str(H/'approved-raid-baselines.json')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
rows.append({'suite':'paired-baseline','exitCode':p.returncode});(out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');result={'rows':rows,'elapsedS':time.perf_counter()-start,'pass':all(r['exitCode']==0 for r in rows),'htmlSha256':__import__('hashlib').sha256(html.read_bytes()).hexdigest()};(out/'execution.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['pass']else 1)
