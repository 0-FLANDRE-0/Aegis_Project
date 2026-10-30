"""Durable read-only headless checks; launched detached from expiring tool sessions."""
from pathlib import Path
import json,sys,subprocess,time,os
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence';kind=sys.argv[1];start=time.perf_counter();rows=[];env=os.environ.copy();env.pop('MAP_D_CONTEXT_FILTER',None)
if kind=='gpu':
 jobs=[('sov-visual',[str(H/'run_legacy_domain.py'),str(R/'Aegis_SIM_v48_WIP_MAP_E.html'),str(E/'domain-final/sov-visual'),'--only','sov-visual']),('Dui213',[str(H/'verify_d_ui.py')]),('Dedges145',[str(H/'verify_d_edges.py')]),('extras',[str(H/'verify_extra.py')]),('new-ui',[str(H/'verify_ui_c.py')]),('motion',[str(H/'verify_motion_c.py')]),('rules',[str(H/'verify_rules_c.py')]),('rings',[str(H/'verify_rings_c.py')]),('dom',[str(H/'verify_dom_c.py')])]
else:
 jobs=[('network',[str(H/'verify_network.py')]),('warnings',[str(H/'verify_warnings.py')]),('paired-baseline',[str(R/'docs/helicopter/F/verify_regression.py'),str(R/'archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html'),str(R/'Aegis_SIM_v48_WIP_MAP_E.html'),str(E/'domain-final/paired-baseline'),'--baseline-only','--approved-raid-baseline',str(H/'approved-raid-baselines.json')])]
for name,args in jobs:
 cmd=[sys.executable,'-u',*args]
 if kind=='gpu':cmd=['flock','/tmp/aegis-map-e/gpu.lock',*cmd]
 log=E/(name+'-remaining.log')
 with log.open('w')as f:q=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 row={'name':name,'exitCode':q.returncode,'log':log.name,'elapsedS':time.perf_counter()-start};rows.append(row);(E/('remaining-'+kind+'.json')).write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'pass':all(q['exitCode']==0 for q in rows)},indent=2)+'\n');print(row,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
