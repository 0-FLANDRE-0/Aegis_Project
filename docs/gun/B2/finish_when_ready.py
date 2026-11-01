"""Finish local evidence only after the complete matrix. Never commit/publish."""
from pathlib import Path
import datetime,json,os,subprocess,sys,time
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/dev/shm','NODE_PATH':'/workspace/aegis-performance-f/docs/performance/F/node_modules','MPLCONFIGDIR':'/tmp/aegis-gun-b2/matplotlib'}
while True:
 corrected=(E/'a-stop-start.json').exists()
 q=json.loads(subprocess.check_output([sys.executable,str(B/('progress_a_stop.py'if corrected else'progress.py'))],cwd=R,env=env));print(json.dumps(q),flush=True)
 if q['invalidCompleteLines']or q['inactiveWorkers']:raise SystemExit('INSPECTION_REQUIRED')
 if q['cases']==q['expected'] and q['completeWorkers']==4:break
 time.sleep(45)
commands=([[sys.executable,str(B/'audit_a_stop.py')]]if corrected else[])+[['node',str(B/'static_audit.cjs')],*[ [sys.executable,str(B/n)]for n in ['validate_approved.py','analyze.py','verify_phase0.py','plot.py','make_report.py']]];executions=[]
for cmd in commands:
 at=time.perf_counter();subprocess.run(cmd,cwd=R,env=env,check=True);executions.append({'script':Path(cmd[1]).name,'elapsedS':time.perf_counter()-at})
(E/'local-finalization.json').write_text(json.dumps({'complete':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executions':executions,'published':False,'phase':'PHASE0_ONLY'},indent=2)+'\n');print('LOCAL_EVIDENCE_COMPLETE_REVIEW_BEFORE_PUBLICATION',flush=True)
