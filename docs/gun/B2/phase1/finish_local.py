"""Serial finalization after all physical measurements and repeat guards finish."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':'/dev/shm/gun-b2-phase1-mpl','NODE_PATH':'/workspace/aegis-performance-f/docs/performance/F/node_modules'}
while not(P/'evidence/g7-final-execution.json').exists():time.sleep(10)
a=json.loads((P/'evidence/g7-final-execution.json').read_text());assert len(a)==3 and all(x['exit']==0 for x in a),a
rows=[]
def run(name,cmd,extra=None):
 log=Path('/tmp/gun-b2-local-'+name+'.log')
 with log.open('w')as f:r=subprocess.run(cmd,cwd=R,env={**env,**(extra or{})},stdout=f,stderr=subprocess.STDOUT)
 rows.append({'step':name,'exit':r.returncode,'log':str(log)})
 (P/'evidence/local-finalization.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert r.returncode==0,(name,log.read_text()[-2400:])
run('build',[sys.executable,str(P/'build.py'),'--stage','all'])
sha=hashlib.sha256((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes()).hexdigest();assert sha=='c48c2396932e07c8051b7a07d2da282951587283d768f2caa384a48936a0ed8b',sha
run('static',['node','--max-old-space-size=2200',str(P/'static.cjs')])
run('audit',[sys.executable,str(P/'audit_product.py')])
run('label',[sys.executable,str(P/'verify_label.py')],{'B2_LABEL_HTML':str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),'B2_LABEL_OUT':str(P/'evidence/label-final'),'B2_LABEL_DPR':'2.8125'})
run('docs',[sys.executable,str(P/'finalize_docs.py')])
run('report',[sys.executable,str(P/'generate_report.py')])
# Check the allowed parent status changes before packaging their final bytes.
run('audit-after-docs',[sys.executable,str(P/'audit_product.py')])
# Packaging must not include its own in-progress runner receipt, which changes on exit.
# Local completion receipt remains a repository-side execution record outside archive hashes.
print('LOCAL_READY_FOR_PACKAGING',flush=True)
