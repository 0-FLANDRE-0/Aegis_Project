from pathlib import Path
import os,subprocess,sys,time
P=Path(__file__).resolve().parent
while not(P/'evidence/v2-checks-execution.json').exists():time.sleep(10)
with Path('/tmp/gun-b2-v2-calibration.log').open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/'calibrate.py')],cwd=P.parents[3],env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','B2_CALIBRATION_OUT':str(P/'evidence/dispersion-v2')},stdout=f,stderr=subprocess.STDOUT)
raise SystemExit(r.returncode)
