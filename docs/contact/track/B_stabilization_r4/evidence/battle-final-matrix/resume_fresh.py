"""Resume only previously unexecuted pages in one fresh process/browser each.

No helper, product, initial condition, or result criterion is changed.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
D=Path(__file__).resolve().parent
R=D.parents[5]
jobs=[('candidate-shadow','CG_MULTIPLE_3'),('candidate-shadow','DDG_BEARING_CROSSING_2'),
      ('candidate-active','NATURAL_SATURATION_6'),('candidate-active','DDG_CONVERGING_2'),
      ('candidate-active','CG_MULTIPLE_3'),('candidate-active','DDG_BEARING_CROSSING_2')]
common=['--run','--shadow',str(R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D_SHADOW.html'),
        '--shadow-sha','3c7d2490e7e0d6fe94452e43d8f22132fbdd8add83986208bf7173068c478444',
        '--candidate',str(R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html'),
        '--sha','48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab',
        '--out',str(D)]
attempts=D/'attempts';attempts.mkdir(exist_ok=True)
allrows=[]
for version,case in jobs:
    tag=version+'-'+case
    assert not (D/(tag+'-SUMMARY.json')).exists(),('Do not overwrite passed pages',tag)
    command=[sys.executable,'-u',str(D/'run.py'),'--versions',version,'--cases',case]+common
    before={n:Path('/sys/fs/cgroup/'+n).read_text() for n in ['memory.events','memory.current']}
    started=time.perf_counter()
    with (attempts/(tag+'.log')).open('w') as log:
        result=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy())
    row={'version':version,'case':case,'command':command,'exitCode':result.returncode,
         'wallS':time.perf_counter()-started,'freshPythonProcessAndBrowser':True,
         'before':before,'after':{n:Path('/sys/fs/cgroup/'+n).read_text()for n in before},
         'productChanged':False,'expectedValuesChanged':False,'releaseApproved':False}
    for name in ['PLAN.json','SAMPLER_SOURCE.json','SUMMARY.json']:
        p=D/name
        if p.exists():(attempts/(tag+'-'+name)).write_bytes(p.read_bytes())
    (attempts/(tag+'-RECEIPT.json')).write_text(json.dumps(row,indent=2)+'\n')
    allrows.append(row)
    (attempts/'RESUME.json').write_text(json.dumps({'rows':allrows,'status':'RUNNING'if result.returncode==0 else'TOOLING_OR_FIXTURE_INCOMPLETE','gameFailureInferredFromToolExit':False},indent=2)+'\n')
    print(json.dumps(row),flush=True)
    if result.returncode!=0:raise SystemExit(result.returncode)
(attempts/'RESUME.json').write_text(json.dumps({'rows':allrows,'status':'CAPTURE_COMPLETE','gameFailureInferredFromToolExit':False},indent=2)+'\n')
