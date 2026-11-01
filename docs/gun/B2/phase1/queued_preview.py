from pathlib import Path
import subprocess,sys,time,os,json
P=Path(__file__).resolve().parent;R=P.parents[3]
while not(P/'evidence/v2-checks-execution.json').exists():time.sleep(10)
q=json.loads((P/'evidence/v2-checks-execution.json').read_text());assert all(r['exit']==0 for r in q['rows'])
for name,args,extra in [('analyze_range',[],{}),('build',['--stage','all','--ui-preview'],{}),('verify_measurement_guards',[],{}),('calibrate',[],{'B2_CALIBRATION_OUT':str(P/'evidence/dispersion-final')}),('verify_label',[],{'B2_LABEL_HTML':'/tmp/aegis-gun-b2/phase1-ui.html'})]:
 with Path('/tmp/gun-b2-final-'+name+'.log').open('w')as log:r=subprocess.run([sys.executable,'-u',str(P/(name+'.py')),*args],cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1',**extra},stdout=log,stderr=subprocess.STDOUT)
 if r.returncode:raise SystemExit(name+' FAILED')
