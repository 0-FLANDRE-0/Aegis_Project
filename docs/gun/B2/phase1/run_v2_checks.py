from pathlib import Path
import os,subprocess,sys,json,time
P=Path(__file__).resolve().parent;rows=[];start=time.perf_counter()
for name in ['verify_physics','verify_broad_phase','measure_range','verify_native_trace','verify_final_pairs']:
 with Path('/tmp/gun-b2-v2-'+name+'.log').open('w')as f:q=subprocess.run([sys.executable,'-u',str(P/(name+'.py'))],cwd=P.parents[3],env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT)
 row={'test':name,'exit':q.returncode};rows.append(row);print(row,flush=True)
 if q.returncode:break
(P/'evidence/v2-checks-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
