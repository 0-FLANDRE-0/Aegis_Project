"""Finish local verification/delivery after the one running sweep completes.

Never starts a full sweep, never uploads, and stops on any failed check.
"""
from pathlib import Path
import base64,gzip,json,os,re,subprocess,time
H=Path(__file__).resolve().parent;R=H.parents[2];LOG=H/'evidence/post-measurement.json'
env=os.environ.copy();env['NODE_PATH']='/workspace/aegis-performance-f/docs/performance/F/node_modules'
started=time.perf_counter();events=[]
def event(stage,**data):
 events.append({'stage':stage,'elapsedS':time.perf_counter()-started,**data})
 LOG.write_text(json.dumps({'events':events},indent=2)+'\n');print(json.dumps(events[-1]),flush=True)
def run(stage,cmd):
 event(stage,status='RUNNING',command=cmd)
 with(H/'evidence'/(stage+'.log')).open('w')as out:
  p=subprocess.run(cmd,cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT)
 event(stage,status='PASS'if p.returncode==0 else'FAIL',exitCode=p.returncode)
 if p.returncode:raise RuntimeError(stage+' failed; inspect evidence/'+stage+'.log')
def main():
 event('WAITING_FOR_EXISTING_SWEEP')
 while not(H/'results/measurement.json').exists():
  try:
   stat=Path('/proc/21187/stat').read_text().split()
   alive=stat[2]!='Z'
  except FileNotFoundError:alive=False
  if not alive:raise RuntimeError('Measurement process ended without a complete result; do not repeat completed cells')
  time.sleep(10)
 # File creation is synchronous, but let its final write settle before parsing.
 for _ in range(10):
  try:m=json.loads((H/'results/measurement.json').read_text());break
  except json.JSONDecodeError:time.sleep(1)
 else:raise RuntimeError('Incomplete measurement JSON')
 assert len(m['rows'])==126
 event('FULL_SWEEP_COMPLETE',calls=m['calls'],measurementElapsedS=m['elapsedS'])
 run('followup',['taskset','-c','0-3','node',str(H/'finish_measurement.cjs')])
 run('build',['python',str(H/'build.py')])
 base=R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
 if not base.exists():base=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/base.name
 paths=[]
 for tag,p in [('base',base),('candidate',R/'Aegis_SIM_v48_WIP_ENV_D.html')]:
  raw=p.read_bytes();source=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)</script>',raw)[1]));dest=Path('/tmp/aegis-env-d')/(tag+'-delivery-main.js');dest.write_bytes(source);paths.append(dest)
  run(tag+'-syntax',['node','--check',str(dest)])
 run('scope',['node',str(R/'docs/performance/F/verify_scope.cjs'),*[str(p)for p in paths]])
 run('delivery-verification',['taskset','-c','0-3','python',str(H/'verify_delivery.py')])
 run('report',['python',str(H/'report.py')])
 run('verification',['python',str(H/'verify_results.py')])
 run('archive',['python',str(H/'archive_delivery.py')])
 run('package',['python',str(H/'package.py')])
 event('LOCAL_DELIVERY_READY',uploadStarted=False)
try:main()
except Exception as error:
 event('STOPPED',error=str(error));raise
