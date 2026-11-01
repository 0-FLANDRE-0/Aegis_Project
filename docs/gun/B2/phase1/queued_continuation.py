from pathlib import Path
import os,subprocess,sys,time,json
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/gun-regression'
while not(E/'ON-verify_label.done.json').exists():time.sleep(10)
rows=[];env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_ALLOW_AUTO':'1','B2_OUT':str(E/'ON'),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
for name in ['continue_native_assertions','continue_adapter_assertions']:
 with(E/(name+'.log')).open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/(name+'.py'))],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':name,'exit':r.returncode})
(E/'continuation-execution.json').write_text(json.dumps(rows,indent=2)+'\n')
