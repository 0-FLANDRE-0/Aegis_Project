"""Start independent B1 regression after final physical checks; keep main regression intact."""
from pathlib import Path
import os,subprocess,sys,time
P=Path(__file__).resolve().parent
while not(P/'evidence/v2-checks-execution.json').exists():time.sleep(10)
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
with Path('/tmp/gun-b2-gun-regression.log').open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/'run_gun_regression.py')],env=env,cwd=P.parents[3],stdout=f,stderr=subprocess.STDOUT)
raise SystemExit(r.returncode)
