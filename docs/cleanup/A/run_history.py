from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];start=time.perf_counter();rows=[]
def run(variant):
 out=H/'evidence/history'/variant;out.mkdir(parents=True,exist_ok=True)
 with (out/'execution.log').open('w')as log:p=subprocess.run([sys.executable,str(H/'history_pair.py'),variant],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 row={'variant':variant,'exitCode':p.returncode};return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for row in pool.map(run,['KAPPA','DZT','HANDOFF','ARH','VERTICAL','LATEST','REVERT_LAUNCH_ONLY']):
  rows.append(row);(H/'evidence/history-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
(H/'evidence/history-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
