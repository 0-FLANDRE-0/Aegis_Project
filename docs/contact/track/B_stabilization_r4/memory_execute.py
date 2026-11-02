"""Memory-only supervisor around the unchanged frozen R4 regression controller.

The original execute function is called once with identical args. No assertion,
result status, expected value, product or environment variable is changed.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time

sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
CONTROLLER=P/'regression.py'
FROZEN='ac73be71cea4924fc1eec577d0da82e84e88207423e1e1f622efd922a2a797fd'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(CONTROLLER.read_bytes())==FROZEN
spec=importlib.util.spec_from_file_location('unchanged_frozen_r4_regressions',CONTROLLER)
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
original=runner.execute

def sample():
 cg=Path('/sys/fs/cgroup');current=int((cg/'memory.current').read_text());limit=(cg/'memory.max').read_text().strip()
 parse=lambda p:{line.split()[0]:int(line.split()[1])for line in p.read_text().splitlines()}
 return {'monotonicS':time.monotonic(),'unixTimeS':time.time(),'pid':os.getpid(),'currentBytes':current,'maxBytes':None if limit=='max'else int(limit),'headroomBytes':None if limit=='max'else int(limit)-current,'events':parse(cg/'memory.events'),'shmemBytes':parse(cg/'memory.stat').get('shmem'),'scope':'Shared cgroup; OOM increments alone do not identify a game process or product cause.'}

def supervised(*args,**kwargs):
 name=args[0];out=runner.E/'memory';out.mkdir(parents=True,exist_ok=True)
 before=sample();receipt={'schema':'AEGIS_R4_ORIGINAL_REGRESSION_MEMORY_1','suite':name,'capturedBeforeWorker':True,'supervisorSha256':sha(Path(__file__).read_bytes()),'frozenControllerSha256':FROZEN,'before':before,'gameQueries':0,'originalExecuteCalls':1,'expectedValuesChanged':False,'statusRewritten':False}
 target=out/(name+'.json');target.write_text(json.dumps(receipt,indent=2)+'\n')
 try:return original(*args,**kwargs)
 finally:
  after=sample();receipt.update(after=after,eventDelta={k:after['events'].get(k,0)-before['events'].get(k,0)for k in set(before['events'])|set(after['events'])});target.write_text(json.dumps(receipt,indent=2)+'\n')

runner.execute=supervised
if __name__=='__main__':runner.main()
