from pathlib import Path
import json,os,subprocess,sys,time
from deadline import check,remaining
P=Path(__file__).resolve().parent;R=P.parents[3];env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':'/dev/shm/gun-b2a-mpl','NODE_PATH':'/workspace/aegis-performance-f/docs/performance/F/node_modules'}
while not(P/'evidence/g7/execution.json').exists():check();time.sleep(5)
assert json.loads((P/'evidence/g7/execution.json').read_text())['complete'];rows=[]
def run(name,cmd,allow=False):
 check();log=Path('/tmp/gun-b2a-final-'+name+'.log');at=time.perf_counter()
 with log.open('w')as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=remaining())
 rows.append({'step':name,'exit':r.returncode,'elapsedS':time.perf_counter()-at});(P/'evidence/local-finalization.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert r.returncode==0 or allow,(name,log.read_text()[-1200:])
run('g7-analysis',[sys.executable,str(P/'analyze_results.py')]);run('pairs',[sys.executable,str(P/'reconcile_pairs.py')]);run('regression',[sys.executable,str(P/'collect_regression.py')],True)
reg=json.loads((P/'evidence/regression-summary.json').read_text());failed={(r['suite'],k)for r in reg['rows']for k in r.get('failed',[])};assert failed=={('physical-adapter','nativeFinish'),('physical-adapter','nativeAfterActionJournal')},('UNEXPECTED_DIFFERENCE_STOP',failed)
run('embed',[sys.executable,str(P/'build.py'),'--embed']);run('static281',['node','--max-old-space-size=2200',str(P/'static.cjs')]);run('scope',['node','--max-old-space-size=2200',str(P/'audit_scope.cjs')]);run('reuse',[sys.executable,str(P/'build_reuse_ledger.py')]);run('plots',[sys.executable,str(P/'plot_results.py')]);run('report',[sys.executable,str(P/'write_report.py')]);run('docs',[sys.executable,str(P/'finalize_docs.py')]);print('READY_FOR_REPORT_REVIEW_AND_PACKAGING',flush=True)
