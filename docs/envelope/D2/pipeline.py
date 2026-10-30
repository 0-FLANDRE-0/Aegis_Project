"""Wait for the one full sweep, then replay boundaries and build the table."""
from pathlib import Path
import os,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];pid=int(sys.argv[1]);stages=[]
while not (H/'results/measurement.json').exists():
 try:os.kill(pid,0)
 except ProcessLookupError:raise SystemExit('Measurement process stopped before completion; resume suite.cjs before continuing.')
 time.sleep(10)
for name,cmd in [('followup',['node',str(H/'finish_measurement.cjs')]),('build',[sys.executable,str(H/'build.py')]),('delivery',[sys.executable,str(H/'verify_delivery.py')]),('report',[sys.executable,str(H/'report.py')]),('audit',[sys.executable,str(H/'verify_results.py')])]:
 start=time.perf_counter()
 with (H/'evidence'/(name+'.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 stages.append({'stage':name,'returncode':p.returncode,'elapsedS':time.perf_counter()-start});print(stages[-1],flush=True)
 if p.returncode:raise SystemExit(p.returncode)
