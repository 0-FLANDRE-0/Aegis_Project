from pathlib import Path
import os,subprocess,sys,time
P=Path(__file__).resolve().parent
while not(P/'evidence/final-pairs/results.json').exists():time.sleep(10)
while not(P/'evidence/native-trace/results.json').exists()or not __import__('json').loads((P/'evidence/native-trace/results.json').read_text())['pass']:time.sleep(10)
with Path('/tmp/gun-b2-label-preview.log').open('w')as f:
 r=subprocess.run([sys.executable,'-u',str(P/'verify_label.py')],cwd=P.parents[3],env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT)
raise SystemExit(r.returncode)
