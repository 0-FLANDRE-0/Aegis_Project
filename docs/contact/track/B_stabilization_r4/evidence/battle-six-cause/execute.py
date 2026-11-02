"""One global browser, fresh Python process per guarded diagnostic page."""
from pathlib import Path
import json,os,subprocess,sys,time
D=Path(__file__).resolve().parent;R=D.parents[5];rows=[]
for label,file,pin in [('R3','Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html','a1e09f0ba815a84152b140ffeafcf139b0cbbf82911713d6c5802ed797fb0561'),('R4','Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html','48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab')]:
 out=D/label;out.mkdir(exist_ok=True);cmd=[sys.executable,'-u',str(D/'run.py'),'--run','--versions','candidate-active','--cases','NATURAL_SATURATION_6','--candidate',str(R/file),'--sha',pin,'--out',str(out)]
 assert not(out/'candidate-active-NATURAL_SATURATION_6.json.gz').exists()
 start=time.perf_counter();before={k:Path('/sys/fs/cgroup/'+k).read_text()for k in ['memory.current','memory.events']}
 with(out/'RUN.log').open('w')as log:result=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy())
 row={'label':label,'exitCode':result.returncode,'wallS':time.perf_counter()-start,'command':cmd,'before':before,'after':{k:Path('/sys/fs/cgroup/'+k).read_text()for k in before},'freshProcessAndBrowser':True,'productChanged':False,'expectedValuesChanged':False};(out/'RECEIPT.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps(row),flush=True)
 if result.returncode:raise SystemExit(result.returncode)
(D/'EXECUTION.json').write_text(json.dumps({'rows':rows,'status':'CAPTURED_GUARDS_PENDING','oneGlobalHeavyBrowser':True},indent=2)+'\n')
