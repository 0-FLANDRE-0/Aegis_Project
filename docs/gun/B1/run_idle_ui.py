"""Retain resource-contended run, then execute missing/failed wall-clock UI suites unchanged."""
from pathlib import Path
import json,time,os,sys,subprocess,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/idle-ui';E.mkdir(parents=True,exist_ok=True);current=hashlib.sha256((R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes()).hexdigest()
def done():
 try:
  return all((H/f'evidence/effects/worker{i}-complete.json').exists()for i in range(3))and (H/'evidence/regression-driver/execution.json').exists()and (H/'evidence/test-migrations/execution.json').exists()and len(json.loads((H/'evidence/test-migrations/execution.json').read_text()))==2 and json.loads((H/'evidence/ui/results.json').read_text())['htmlSha256']==current and json.loads((H/'evidence/ui-handoff/results.json').read_text())['htmlSha256']==current and json.loads((H/'evidence/effect-equivalence/results.json').read_text())['htmlSha256']['delivery']==current
 except(OSError,ValueError,KeyError):return False
while not done():time.sleep(2)
env={**os.environ,'PYTHONPATH':str(H/'test_support'),'GUN_B1_REGRESSION':'OFF','GUN_B1_EVIDENCE_ROOT':str(H/'evidence/regression-idle'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'};rows=[]
for kind in ['motion_c','rules_c','rings_c','dom_c']:
 t=time.perf_counter()
 with(E/(kind+'.log')).open('w')as f:p=subprocess.run(['flock','/tmp/aegis-gun-b1/gpu.lock',sys.executable,'-u',str(R/'docs/map/E'/('verify_'+kind+'.py'))],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 row={'kind':kind,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t};rows.append(row);print(json.dumps(row),flush=True);(E/'execution.json').write_text(json.dumps(rows,indent=2)+'\n')
