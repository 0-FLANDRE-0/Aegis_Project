from pathlib import Path
import os,subprocess,sys,time
P=Path(__file__).resolve().parent
while not(P/'evidence/surface/execution.json').exists():time.sleep(10)
for name in ['verify_native_trace','verify_final_pairs']:
 with Path('/tmp/gun-b2-'+name+'.log').open('w')as f:
  q=subprocess.run([sys.executable,'-u',str(P/(name+'.py'))],cwd=P.parents[3],env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT)
 print(name,q.returncode,flush=True)
