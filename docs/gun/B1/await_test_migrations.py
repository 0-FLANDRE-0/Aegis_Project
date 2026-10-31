"""Sequential follow-up after original MAP_D reports exist; no product mutation."""
from pathlib import Path
import os,time,subprocess,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/test-migrations';E.mkdir(parents=True,exist_ok=True)
while True:
 try:done={x['name']for x in json.loads((H/'evidence/regression-driver/progress.json').read_text())}
 except (OSError,ValueError):done=set()
 if {'verify_d_ui','verify_d_edges'}<=done:break
 time.sleep(2)
env={**os.environ,'PYTHONPATH':str(H/'test_support'),'GUN_B1_REGRESSION':'OFF','GUN_B1_EVIDENCE_ROOT':str(H/'evidence/regression-migrated'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'};rows=[]
for kind in ['ui','edges']:
 t=time.perf_counter()
 with(E/(kind+'.log')).open('w')as f:p=subprocess.run(['flock','/tmp/aegis-gun-b1/gpu.lock',sys.executable,'-u',str(H/'run_test_migrations.py'),kind],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 row={'kind':kind,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t};rows.append(row);print(json.dumps(row),flush=True);(E/'execution.json').write_text(json.dumps(rows,indent=2)+'\n')
