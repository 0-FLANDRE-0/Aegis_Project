"""Original bounded release cases, unmodified; no envelope/range sweep."""
from pathlib import Path
import subprocess,json,time,sys
H=Path(__file__).resolve().parent;R=H.parents[3];start=time.perf_counter();executions=[]
for variant in ['BASE','DZT']:
 out=H/'evidence'/('release-'+variant);out.mkdir(parents=True,exist_ok=True)
 for kind,file in [('normals','normal'),('dual','dual'),('faults','fault'),('battery','battery'),('request','release-request')]:
  cmd=['python','docs/missile/termination/A/verify_live.py','/tmp/aegis-fuze-zem/builds/Aegis_SIM_v48_WIP_FUZE_ZEM_A_'+variant+'.html',str(out/(kind+'.json')),'--cases','docs/missile/termination/A/cases/'+file+'.json','--batch','8'];t=time.perf_counter()
  with(out/(kind+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  q={'variant':variant,'kind':kind,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t};executions.append(q);print(json.dumps(q),flush=True)
  (H/'evidence/release-executions.json').write_text(json.dumps({'rows':executions,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
  if p.returncode:sys.exit(p.returncode)
