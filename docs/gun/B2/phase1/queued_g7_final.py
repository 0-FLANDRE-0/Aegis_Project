from pathlib import Path
import json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
while not(P/'evidence/g7/execution.json').exists():time.sleep(10)
q=json.loads((P/'evidence/g7/execution.json').read_text());assert len(q)==3 and all(x['exit']==0 for x in q),'G7_INCOMPLETE_NO_SUMMARY'
rows=[]
for name in ['verify_g7_repeat','collect_effects','plot_g7']:
 with Path('/tmp/gun-b2-final-'+name+'.log').open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/(name+'.py'))],cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':'/dev/shm/gun-b2-phase1-mpl'},stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':name,'exit':r.returncode})
 if r.returncode:break
(P/'evidence/g7-final-execution.json').write_text(json.dumps(rows,indent=2)+'\n')
