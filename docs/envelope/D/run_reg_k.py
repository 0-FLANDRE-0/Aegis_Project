"""REG_K: run original acceptance harnesses unchanged on both pinned builds.

Results are retained even on assertion failures: failures are observations,
never reasons to tune production code or weaken an assertion.
"""
from pathlib import Path
import concurrent.futures, json, os, subprocess, sys, time

H=Path(__file__).resolve().parent
R=H.parents[2]
E=H/'evidence/reg-k'
VERSIONS={
 'current':R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html',
 'recovery':R/'archive/v48/WIP_RANGE_RECOVERY_A/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html',
}
if not VERSIONS['current'].exists():
 VERSIONS['current']=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/VERSIONS['current'].name
def execute(tag, kind, cmd):
 out=E/tag
 out.mkdir(parents=True,exist_ok=True)
 t=time.perf_counter()
 with (out/(kind+'.log')).open('w') as f:
  p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 result={'version':tag,'kind':kind,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t,'command':cmd}
 (out/(kind+'-execution.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
 return result
def domain():
 rows=[]
 for tag,file in VERSIONS.items():
  rows.append(execute(tag,'domain',['python','docs/pip/B/run_domain.py',str(file),str(E/tag/'domain'),'--parallel','2']))
  rows.append(execute(tag,'domain-count',['python','docs/missile/range/A/collect_domain.py',str(E/tag/'domain'),str(E/tag/'domain-acceptance.json')]))
  src="import sys,runpy;sys.path.insert(0,'docs/pip/B');import browser_backend;browser_backend.install();sys.argv=['docs/pip/B/verify_ui.py',"+repr(str(file))+','+repr(str(E/tag/'ui'))+"];runpy.run_path(sys.argv[0],run_name='__main__')"
  rows.append(execute(tag,'ui',['python','-c',src]))
 return rows
def flight():
 rows=[]
 for tag,file in VERSIONS.items():
  for name,case,batch in [('normals-release','normal',8),('dual-release','dual',8),('faults-release','fault',4),('battery-release','battery',4),('release-request-final','release-request',4),('validation-release','validation',8)]:
   folder='docs/missile/range/A/cases/' if case=='validation'else'docs/missile/termination/A/cases/'
   rows.append(execute(tag,name,['python','docs/missile/termination/A/verify_live.py',str(file),str(E/tag/(name+'.json')),'--cases',folder+case+'.json','--batch',str(batch)]))
  rows.append(execute(tag,'live-acceptance',['python','docs/missile/termination/A/verify_live_results.py',str(E/tag)]))
  rows.append(execute(tag,'observed-world',['python','docs/missile/termination/A/verify_observed_world.py',str(file),str(E/tag/'observed-world')]))
 return rows
if __name__=='__main__':
 E.mkdir(parents=True,exist_ok=True)
 start=time.perf_counter()
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:
  rows=sum([f.result() for f in [p.submit(domain),p.submit(flight)]],[])
 (E/'executions.json').write_text(json.dumps({'elapsedS':time.perf_counter()-start,'rows':rows},indent=2)+'\n')
 sys.exit(0 if all(r['exitCode']==0 for r in rows)else 1)
